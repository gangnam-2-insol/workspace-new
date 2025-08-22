from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import re
import hashlib
import os

from models.applicant import ApplicantCreate
from models.document import ResumeCreate, CoverLetterCreate, PortfolioCreate, PortfolioItem, PortfolioItemType, Artifact, ArtifactKind
from services.mongo_service import MongoService

class MongoSaver:
    def __init__(self, mongo_uri: str = None):
        self.mongo_service = MongoService(mongo_uri)
    
    def _serialize_datetime(self, obj):
        """datetime 객체와 ObjectId를 JSON 직렬화 가능한 형태로 변환합니다."""
        try:
            from bson import ObjectId
            if isinstance(obj, ObjectId):
                return str(obj)
        except ImportError:
            pass
        
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._serialize_datetime(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        else:
            return obj
    
    def _dict_with_serialized_datetime(self, model_obj):
        """모델 객체의 dict를 datetime 직렬화하여 반환합니다."""
        if hasattr(model_obj, 'dict'):
            data = model_obj.dict()
        else:
            data = model_obj
        return self._serialize_datetime(data)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """파일의 SHA-256 해시를 계산합니다."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _create_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """파일 메타데이터를 생성합니다."""
        stat = file_path.stat()
        return {
            "filename": file_path.name,
            "size": stat.st_size,
            "mime": "application/pdf",  # PDF 파일 가정
            "hash": self._calculate_file_hash(file_path),
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    def _extract_basic_info_from_ocr(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """OCR 결과에서 기본 정보를 추출합니다."""
        basic_info = {}
        
        if "basic_info" in ocr_result:
            basic_info = ocr_result["basic_info"]
        
        # 기본 정보가 없으면 텍스트에서 추출 시도
        if not basic_info:
            text = ocr_result.get("extracted_text", "")
            basic_info = {
                "emails": [],
                "phones": [],
                "names": [],
                "urls": []
            }
            
            # 간단한 정규식으로 정보 추출 (실제로는 더 정교한 로직 필요)
            import re
            
            # 이메일 추출
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            basic_info["emails"] = list(set(emails))
            
            # 전화번호 추출
            phones = re.findall(r'\b\d{2,3}-\d{3,4}-\d{4}\b', text)
            basic_info["phones"] = list(set(phones))
        
        return basic_info
    
    def save_resume_with_ocr(self, 
                           ocr_result: Dict[str, Any], 
                           applicant_data: ApplicantCreate,
                           job_posting_id: str,
                           file_path: Optional[Path] = None,
                           existing_applicant_id: Optional[str] = None,
                           replace_existing: bool = False) -> Dict[str, Any]:
        """이력서 OCR 결과를 저장합니다."""
        try:
            # 1. 지원자 생성/조회 (기존 지원자 ID가 있으면 사용)
            if existing_applicant_id:
                # 기존 지원자 조회
                from bson import ObjectId
                existing_applicant = self.mongo_service.applicants.find_one({"_id": ObjectId(existing_applicant_id)})
                if existing_applicant:
                    # 기존 지원자 정보로 Applicant 객체 생성
                    from models.applicant import Applicant
                    applicant = Applicant(
                        id=existing_applicant_id,
                        name=existing_applicant.get("name", ""),
                        email=existing_applicant.get("email", ""),
                        phone=existing_applicant.get("phone", ""),
                        position=existing_applicant.get("position", ""),
                        department=existing_applicant.get("department", ""),
                        experience=existing_applicant.get("experience", ""),
                        skills=existing_applicant.get("skills", ""),
                        growthBackground=existing_applicant.get("growthBackground", ""),
                        motivation=existing_applicant.get("motivation", ""),
                        careerHistory=existing_applicant.get("careerHistory", ""),
                        analysisScore=existing_applicant.get("analysisScore", 65),
                        analysisResult=existing_applicant.get("analysisResult", ""),
                        status=existing_applicant.get("status", "pending"),
                        job_posting_id=existing_applicant.get("job_posting_id"),
                        created_at=existing_applicant.get("created_at"),
                        updated_at=datetime.utcnow()
                    )
                    print(f"🔄 기존 지원자 사용: {applicant.name} ({applicant.email})")
                    
                    # 기존 이력서가 있고 교체 옵션이 활성화된 경우
                    if existing_applicant.get("resume_id") and replace_existing:
                        print(f"🔄 기존 이력서 교체 모드")
                        # 기존 이력서 교체
                        resume_data = ResumeCreate(
                            applicant_id=applicant.id,
                            extracted_text=ocr_result.get("extracted_text", ""),
                            summary=ocr_result.get("summary", ""),
                            keywords=ocr_result.get("keywords", []),
                            document_type="resume",
                            basic_info=self._extract_basic_info_from_ocr(ocr_result),
                            file_metadata=self._create_file_metadata(file_path) if file_path else {}
                        )
                        
                        resume = self.mongo_service.replace_resume(applicant.id, resume_data)
                        print(f"✅ 이력서 교체 완료: {resume.id}")
                        
                        return {
                            "applicant": self._dict_with_serialized_datetime(applicant),
                            "resume": self._dict_with_serialized_datetime(resume),
                            "message": "이력서 교체 완료"
                        }
                else:
                    # 기존 지원자를 찾을 수 없는 경우 새로 생성
                    applicant = self.mongo_service.create_or_get_applicant(applicant_data)
            else:
                # 새 지원자 생성
                applicant = self.mongo_service.create_or_get_applicant(applicant_data)
            
            # 2. 파일 메타데이터 생성
            file_metadata = {}
            if file_path:
                file_metadata = self._create_file_metadata(file_path)
            
            # 3. 기본 정보 추출
            basic_info = self._extract_basic_info_from_ocr(ocr_result)
            
            # 4. 이력서 데이터 생성 (application_id 제거)
            resume_data = ResumeCreate(
                applicant_id=applicant.id,
                extracted_text=ocr_result.get("extracted_text", ""),
                summary=ocr_result.get("summary", ""),
                keywords=ocr_result.get("keywords", []),
                document_type="resume",
                basic_info=basic_info,
                file_metadata=file_metadata
            )
            
            # 5. 이력서 저장
            resume = self.mongo_service.create_resume(resume_data)
            
            # 6. 지원자 데이터에 resume_id 업데이트
            try:
                from bson import ObjectId
                self.mongo_service.applicants.update_one(
                    {"_id": ObjectId(applicant.id)},
                    {"$set": {"resume_id": str(resume.id)}}
                )
                print(f"✅ 지원자 데이터에 resume_id 업데이트: {str(resume.id)}")
            except Exception as e:
                print(f"⚠️ resume_id 업데이트 실패: {e}")
            
            return {
                "applicant": self._dict_with_serialized_datetime(applicant),
                "resume": self._dict_with_serialized_datetime(resume),
                "message": "이력서 저장 완료"
            }
            
        except Exception as e:
            raise Exception(f"이력서 저장 실패: {str(e)}")
    
    def save_cover_letter_with_ocr(self, 
                                 ocr_result: Dict[str, Any], 
                                 applicant_data: ApplicantCreate,
                                 job_posting_id: str,
                                 file_path: Optional[Path] = None,
                                 existing_applicant_id: Optional[str] = None,
                                 replace_existing: bool = False) -> Dict[str, Any]:
        """자기소개서 OCR 결과를 저장합니다."""
        try:
            # 1. 지원자 생성/조회 (기존 지원자 ID가 있으면 사용)
            if existing_applicant_id:
                # 기존 지원자 조회
                from bson import ObjectId
                existing_applicant = self.mongo_service.applicants.find_one({"_id": ObjectId(existing_applicant_id)})
                if existing_applicant:
                    # 기존 지원자 정보로 Applicant 객체 생성
                    from models.applicant import Applicant
                    applicant = Applicant(
                        id=existing_applicant_id,
                        name=existing_applicant.get("name", ""),
                        email=existing_applicant.get("email", ""),
                        phone=existing_applicant.get("phone", ""),
                        position=existing_applicant.get("position", ""),
                        department=existing_applicant.get("department", ""),
                        experience=existing_applicant.get("experience", ""),
                        skills=existing_applicant.get("skills", ""),
                        growthBackground=existing_applicant.get("growthBackground", ""),
                        motivation=existing_applicant.get("motivation", ""),
                        careerHistory=existing_applicant.get("careerHistory", ""),
                        analysisScore=existing_applicant.get("analysisScore", 65),
                        analysisResult=existing_applicant.get("analysisResult", ""),
                        status=existing_applicant.get("status", "pending"),
                        job_posting_id=existing_applicant.get("job_posting_id"),
                        created_at=existing_applicant.get("created_at"),
                        updated_at=datetime.utcnow()
                    )
                    print(f"🔄 기존 지원자 사용 (자기소개서): {applicant.name} ({applicant.email})")
                    
                    # 기존 자기소개서가 있고 교체 옵션이 활성화된 경우
                    if existing_applicant.get("cover_letter_id") and replace_existing:
                        print(f"🔄 기존 자기소개서 교체 모드")
                        # 기존 자기소개서 교체
                        cover_letter_data = CoverLetterCreate(
                            applicant_id=applicant.id,
                            extracted_text=ocr_result.get("extracted_text", ""),
                            summary=ocr_result.get("summary", ""),
                            keywords=ocr_result.get("keywords", []),
                            document_type="cover_letter",
                            basic_info=self._extract_basic_info_from_ocr(ocr_result),
                            file_metadata=self._create_file_metadata(file_path) if file_path else {}
                        )
                        
                        cover_letter = self.mongo_service.replace_cover_letter(applicant.id, cover_letter_data)
                        print(f"✅ 자기소개서 교체 완료: {cover_letter.id}")
                        
                        return {
                            "applicant": self._dict_with_serialized_datetime(applicant),
                            "cover_letter": self._dict_with_serialized_datetime(cover_letter),
                            "message": "자기소개서 교체 완료"
                        }
                else:
                    # 기존 지원자를 찾을 수 없는 경우 새로 생성
                    applicant = self.mongo_service.create_or_get_applicant(applicant_data)
            else:
                # 새 지원자 생성
                applicant = self.mongo_service.create_or_get_applicant(applicant_data)
            
            # 2. 파일 메타데이터 생성
            file_metadata = {}
            if file_path:
                file_metadata = self._create_file_metadata(file_path)
            
            # 3. 기본 정보 추출
            basic_info = self._extract_basic_info_from_ocr(ocr_result)
            
            # 4. 자기소개서 데이터 생성 (application_id 제거)
            cover_letter_data = CoverLetterCreate(
                applicant_id=applicant.id,
                extracted_text=ocr_result.get("extracted_text", ""),
                summary=ocr_result.get("summary", ""),
                keywords=ocr_result.get("keywords", []),
                document_type="cover_letter",
                basic_info=basic_info,
                file_metadata=file_metadata
            )
            
            # 5. 자기소개서 저장
            cover_letter = self.mongo_service.create_cover_letter(cover_letter_data)
            
            # 6. 지원자 데이터에 cover_letter_id 업데이트
            try:
                from bson import ObjectId
                self.mongo_service.applicants.update_one(
                    {"_id": ObjectId(applicant.id)},
                    {"$set": {"cover_letter_id": str(cover_letter.id)}}
                )
                print(f"✅ 지원자 데이터에 cover_letter_id 업데이트: {str(cover_letter.id)}")
            except Exception as e:
                print(f"⚠️ cover_letter_id 업데이트 실패: {e}")
            
            return {
                "applicant": self._dict_with_serialized_datetime(applicant),
                "cover_letter": self._dict_with_serialized_datetime(cover_letter),
                "message": "자기소개서 저장 완료"
            }
            
        except Exception as e:
            raise Exception(f"자기소개서 저장 실패: {str(e)}")
    
    def save_portfolio_with_ocr(self, 
                             ocr_result: Dict[str, Any], 
                             applicant_data: ApplicantCreate,
                             job_posting_id: str,
                             file_path: Optional[Path] = None,
                             existing_applicant_id: Optional[str] = None,
                             replace_existing: bool = False) -> Dict[str, Any]:
        """포트폴리오 OCR 결과를 저장합니다."""
        # 1. 지원자 생성/조회 (기존 지원자 ID가 있으면 사용)
        if existing_applicant_id:
            # 기존 지원자 조회
            from bson import ObjectId
            existing_applicant = self.mongo_service.applicants.find_one({"_id": ObjectId(existing_applicant_id)})
            if existing_applicant:
                # 기존 지원자 정보로 Applicant 객체 생성
                from models.applicant import Applicant
                applicant = Applicant(
                    id=existing_applicant_id,
                    name=existing_applicant.get("name", ""),
                    email=existing_applicant.get("email", ""),
                    phone=existing_applicant.get("phone", ""),
                    position=existing_applicant.get("position", ""),
                    department=existing_applicant.get("department", ""),
                    experience=existing_applicant.get("experience", ""),
                    skills=existing_applicant.get("skills", ""),
                    growthBackground=existing_applicant.get("growthBackground", ""),
                    motivation=existing_applicant.get("motivation", ""),
                    careerHistory=existing_applicant.get("careerHistory", ""),
                    analysisScore=existing_applicant.get("analysisScore", 65),
                    analysisResult=existing_applicant.get("analysisResult", ""),
                    status=existing_applicant.get("status", "pending"),
                    job_posting_id=existing_applicant.get("job_posting_id"),
                    created_at=existing_applicant.get("created_at"),
                    updated_at=datetime.utcnow()
                )
                print(f"🔄 기존 지원자 사용 (포트폴리오): {applicant.name} ({applicant.email})")
                
                # 기존 포트폴리오가 있고 교체 옵션이 활성화된 경우
                if existing_applicant.get("portfolio_id") and replace_existing:
                    print(f"🔄 기존 포트폴리오 교체 모드")
                    # 기존 포트폴리오 교체
                    portfolio_item = PortfolioItem(
                        item_id=f"item_{int(datetime.utcnow().timestamp())}",
                        title="포트폴리오 문서",
                        type=PortfolioItemType.DOC,
                        artifacts=[]
                    )
                    
                    portfolio_data = PortfolioCreate(
                        applicant_id=applicant.id,
                        extracted_text=ocr_result.get("extracted_text", ""),
                        summary=ocr_result.get("summary", ""),
                        keywords=ocr_result.get("keywords", []),
                        document_type="portfolio",
                        basic_info=self._extract_basic_info_from_ocr(ocr_result),
                        file_metadata=self._create_file_metadata(file_path) if file_path else {},
                        items=[portfolio_item],
                        analysis_score=0.0,
                        status="active"
                    )
                    
                    portfolio = self.mongo_service.replace_portfolio(applicant.id, portfolio_data)
                    print(f"✅ 포트폴리오 교체 완료: {portfolio.id}")
                    
                    return {
                        "applicant": self._dict_with_serialized_datetime(applicant),
                        "portfolio": self._dict_with_serialized_datetime(portfolio),
                        "message": "포트폴리오 교체 완료"
                    }
            else:
                # 기존 지원자를 찾을 수 없는 경우 새로 생성
                applicant = self.mongo_service.create_or_get_applicant(applicant_data)
        else:
            # 새 지원자 생성
            applicant = self.mongo_service.create_or_get_applicant(applicant_data)
        
        # 2. 파일 메타데이터 생성
        file_metadata = {}
        if file_path:
            file_metadata = self._create_file_metadata(file_path)
        
        # 3. 기본 정보 추출
        basic_info = self._extract_basic_info_from_ocr(ocr_result)
        
        # 4. 포트폴리오 아이템 생성
        portfolio_item = PortfolioItem(
            item_id=f"item_{int(datetime.utcnow().timestamp())}",
            title="포트폴리오 문서",
            type=PortfolioItemType.DOC,
            artifacts=[]
        )
        
        # 5. 포트폴리오 데이터 생성 (application_id 제거)
        portfolio_data = PortfolioCreate(
            applicant_id=applicant.id,
            extracted_text=ocr_result.get("extracted_text", ""),
            summary=ocr_result.get("summary", ""),
            keywords=ocr_result.get("keywords", []),
            document_type="portfolio",
            basic_info=basic_info,
            file_metadata=file_metadata,
            items=[portfolio_item],
            analysis_score=0.0,  # 기본값 설정
            status="active"
        )
        
        # 6. 포트폴리오 저장
        portfolio = self.mongo_service.create_portfolio(portfolio_data)
        
        # 7. 지원자 데이터에 portfolio_id 업데이트
        try:
            from bson import ObjectId
            self.mongo_service.applicants.update_one(
                {"_id": ObjectId(applicant.id)},
                {"$set": {"portfolio_id": str(portfolio.id)}}
            )
            print(f"✅ 지원자 데이터에 portfolio_id 업데이트: {str(portfolio.id)}")
        except Exception as e:
            print(f"⚠️ portfolio_id 업데이트 실패: {e}")
        
        return {
            "applicant": self._dict_with_serialized_datetime(applicant),
            "portfolio": self._dict_with_serialized_datetime(portfolio),
            "message": "포트폴리오 저장 완료"
        }
    
    def close(self):
        """MongoDB 연결을 종료합니다."""
        self.mongo_service.close()
