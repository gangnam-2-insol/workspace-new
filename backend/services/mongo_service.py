from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
import hashlib
import os

from models.applicant import Applicant, ApplicantCreate, ApplicantUpdate, ApplicantStatus
from models.document import ResumeDocument, ResumeCreate, CoverLetterDocument, CoverLetterCreate, PortfolioDocument, PortfolioCreate

class MongoService:
    def __init__(self, mongo_uri: str = None):
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.hireme
        
        # 컬렉션 초기화
        self.applicants = self.db.applicants
        self.resumes = self.db.resumes
        self.cover_letters = self.db.cover_letters
        self.portfolios = self.db.portfolios
        
        # 인덱스 생성
        self._create_indexes()
    
    def _create_indexes(self):
        """필요한 인덱스들을 생성합니다."""
        try:
            # applicants 컬렉션 인덱스
            self.applicants.create_index([("email", ASCENDING)], unique=True)
            self.applicants.create_index([("created_at", DESCENDING)])
            
            # resumes 컬렉션 인덱스
            self.resumes.create_index([("applicant_id", ASCENDING), ("created_at", DESCENDING)])
            
            # cover_letters 컬렉션 인덱스
            self.cover_letters.create_index([("applicant_id", ASCENDING), ("created_at", DESCENDING)])
            
            # portfolios 컬렉션 인덱스
            self.portfolios.create_index([("applicant_id", ASCENDING), ("version", DESCENDING)], unique=True)
            self.portfolios.create_index([("applicant_id", ASCENDING), ("created_at", DESCENDING)])
            
            print("✅ MongoDB 인덱스 생성 완료")
        except Exception as e:
            print(f"⚠️ 인덱스 생성 중 오류: {e}")
    
    # Applicant 관련 메서드
    def find_applicant_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """이름으로 지원자를 검색합니다."""
        try:
            # 정확한 이름 매칭
            applicant = self.applicants.find_one({"name": name})
            if applicant:
                applicant["_id"] = str(applicant["_id"])
                return applicant
            
            # 부분 이름 매칭 (한글 이름의 경우)
            if any(ord(char) > 127 for char in name):  # 한글이 포함된 경우
                applicant = self.applicants.find_one({"name": {"$regex": name, "$options": "i"}})
                if applicant:
                    applicant["_id"] = str(applicant["_id"])
                    return applicant
            
            return None
        except Exception as e:
            print(f"이름으로 지원자 검색 중 오류: {e}")
            return None
    
    def find_applicant_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """이메일로 지원자를 검색합니다."""
        try:
            applicant = self.applicants.find_one({"email": email})
            if applicant:
                applicant["_id"] = str(applicant["_id"])
            return applicant
        except Exception as e:
            print(f"이메일로 지원자 검색 중 오류: {e}")
            return None
    
    def find_applicant_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """전화번호로 지원자를 검색합니다."""
        try:
            # 전화번호 정규화 (하이픈, 공백 제거)
            normalized_phone = ''.join(filter(str.isdigit, phone))
            
            # 정확한 매칭
            applicant = self.applicants.find_one({"phone": phone})
            if applicant:
                applicant["_id"] = str(applicant["_id"])
                return applicant
            
            # 정규화된 전화번호로 검색
            applicant = self.applicants.find_one({"phone": normalized_phone})
            if applicant:
                applicant["_id"] = str(applicant["_id"])
                return applicant
            
            # 부분 매칭 (뒤 4자리)
            if len(normalized_phone) >= 4:
                last_four = normalized_phone[-4:]
                applicant = self.applicants.find_one({"phone": {"$regex": last_four + "$"}})
                if applicant:
                    applicant["_id"] = str(applicant["_id"])
                    return applicant
            
            return None
        except Exception as e:
            print(f"전화번호로 지원자 검색 중 오류: {e}")
            return None

    def create_or_get_applicant(self, applicant_data: ApplicantCreate) -> Applicant:
        """지원자를 생성하거나 기존 지원자를 조회합니다."""
        try:
            # 이메일로 기존 지원자 조회
            existing = self.applicants.find_one({"email": applicant_data.email})
            if existing:
                # ObjectId를 문자열로 변환
                existing["_id"] = str(existing["_id"])
                return Applicant(**existing)
            
            # 새 지원자 생성
            applicant_dict = applicant_data.dict()
            applicant_dict["created_at"] = datetime.utcnow()
            result = self.applicants.insert_one(applicant_dict)
            
            applicant_dict["_id"] = str(result.inserted_id)
            return Applicant(**applicant_dict)
            
        except DuplicateKeyError:
            # 동시 생성 시도 시 기존 지원자 반환
            existing = self.applicants.find_one({"email": applicant_data.email})
            if existing:
                # ObjectId를 문자열로 변환
                existing["_id"] = str(existing["_id"])
                return Applicant(**existing)
    
    def get_applicant(self, applicant_id: str) -> Optional[Applicant]:
        """지원자를 조회합니다."""
        try:
            if not ObjectId.is_valid(applicant_id):
                return None
            
            applicant = self.applicants.find_one({"_id": ObjectId(applicant_id)})
            if applicant:
                # ObjectId를 문자열로 변환
                applicant["_id"] = str(applicant["_id"])
                return Applicant(**applicant)
            return None
        except Exception as e:
            print(f"지원자 조회 오류: {e}")
            return None
    
    def get_applicant_by_id(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 ID로 지원자를 조회합니다."""
        try:
            if not ObjectId.is_valid(applicant_id):
                return None
            
            applicant = self.applicants.find_one({"_id": ObjectId(applicant_id)})
            if applicant:
                # ObjectId를 문자열로 변환
                applicant["_id"] = str(applicant["_id"])
                return applicant
            return None
        except Exception as e:
            print(f"지원자 조회 오류: {e}")
            return None
    
    # Document 관련 메서드들
    def create_resume(self, resume_data: ResumeCreate) -> ResumeDocument:
        """이력서를 생성합니다."""
        resume_dict = resume_data.dict()
        resume_dict["created_at"] = datetime.utcnow()
        
        result = self.resumes.insert_one(resume_dict)
        resume_dict["_id"] = str(result.inserted_id)
        
        return ResumeDocument(**resume_dict)
    
    def create_cover_letter(self, cover_letter_data: CoverLetterCreate) -> CoverLetterDocument:
        """자기소개서를 생성합니다."""
        cover_letter_dict = cover_letter_data.dict()
        cover_letter_dict["created_at"] = datetime.utcnow()
        
        result = self.cover_letters.insert_one(cover_letter_dict)
        cover_letter_dict["_id"] = str(result.inserted_id)
        
        return CoverLetterDocument(**cover_letter_dict)
    
    def create_portfolio(self, portfolio_data: PortfolioCreate) -> PortfolioDocument:
        """포트폴리오를 생성합니다."""
        # 기존 포트폴리오가 있는지 확인하고 버전 결정
        latest = self.portfolios.find_one(
            {"applicant_id": portfolio_data.applicant_id},
            sort=[("version", DESCENDING)]
        )
        
        new_version = (latest["version"] + 1) if latest else 1
        
        portfolio_dict = portfolio_data.dict()
        portfolio_dict["created_at"] = datetime.utcnow()
        portfolio_dict["updated_at"] = datetime.utcnow()
        portfolio_dict["version"] = new_version
        
        result = self.portfolios.insert_one(portfolio_dict)
        portfolio_dict["_id"] = str(result.inserted_id)
        
        return PortfolioDocument(**portfolio_dict)
    
    def update_portfolio(self, applicant_id: str, portfolio_data: PortfolioCreate) -> PortfolioDocument:
        """포트폴리오를 업데이트합니다 (버전 증가)."""
        # 최신 버전 조회
        latest = self.portfolios.find_one(
            {"applicant_id": applicant_id},
            sort=[("version", DESCENDING)]
        )
        
        new_version = (latest["version"] + 1) if latest else 1
        
        portfolio_dict = portfolio_data.dict()
        portfolio_dict["created_at"] = datetime.utcnow()
        portfolio_dict["updated_at"] = datetime.utcnow()
        portfolio_dict["version"] = new_version
        
        result = self.portfolios.insert_one(portfolio_dict)
        portfolio_dict["_id"] = str(result.inserted_id)
        
        return PortfolioDocument(**portfolio_dict)
    
    def get_portfolio_by_applicant_id(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 ID로 포트폴리오를 조회합니다 (최신 버전)."""
        try:
            portfolio = self.portfolios.find_one(
                {"applicant_id": applicant_id},
                sort=[("version", DESCENDING)]
            )
            
            if portfolio:
                # ObjectId를 문자열로 변환
                portfolio["_id"] = str(portfolio["_id"])
                return portfolio
            
            return None
            
        except Exception as e:
            print(f"포트폴리오 조회 오류: {e}")
            return None
    
    # Bundle 관련 메서드
    def get_applicant_bundle(self, applicant_id: str) -> Dict[str, Any]:
        """지원자 번들을 조회합니다 (이력서, 자기소개서, 포트폴리오)."""
        try:
            # 지원자 정보
            applicant = self.get_applicant(applicant_id)
            if not applicant:
                return None
            
            # 이력서 (최신)
            resume = self.resumes.find_one(
                {"applicant_id": applicant_id},
                sort=[("created_at", DESCENDING)]
            )
            
            # 자기소개서 (최신)
            cover_letter = self.cover_letters.find_one(
                {"applicant_id": applicant_id},
                sort=[("created_at", DESCENDING)]
            )
            
            # 포트폴리오 (최신 버전)
            portfolio = self.portfolios.find_one(
                {"applicant_id": applicant_id},
                sort=[("version", DESCENDING)]
            )
            
            return {
                "applicant": applicant.dict() if applicant else None,
                "resume": resume,
                "cover_letter": cover_letter,
                "portfolio": portfolio
            }
            
        except Exception as e:
            print(f"번들 조회 오류: {e}")
            return None
    
    def attach_documents_to_applicant(self, applicant_id: str, documents: Dict[str, Any]) -> Dict[str, Any]:
        """지원자에 문서들을 첨부합니다."""
        results = {}
        
        try:
            # 이력서 첨부
            if "resume" in documents:
                resume_data = ResumeCreate(**documents["resume"])
                results["resume"] = self.create_resume(resume_data)
            
            # 자기소개서 첨부
            if "cover_letter" in documents:
                cover_letter_data = CoverLetterCreate(**documents["cover_letter"])
                results["cover_letter"] = self.create_cover_letter(cover_letter_data)
            
            # 포트폴리오 첨부
            if "portfolio" in documents:
                portfolio_data = PortfolioCreate(**documents["portfolio"])
                results["portfolio"] = self.create_portfolio(portfolio_data)
            
            return results
            
        except Exception as e:
            print(f"문서 첨부 오류: {e}")
            raise
    
    def replace_resume(self, applicant_id: str, new_resume_data: ResumeCreate) -> ResumeDocument:
        """기존 이력서를 새 이력서로 교체합니다."""
        try:
            print(f"🔄 이력서 교체 시작: 지원자 {applicant_id}")
            
            # 기존 이력서 삭제
            delete_result = self.resumes.delete_many({"applicant_id": applicant_id})
            print(f"🗑️ 기존 이력서 삭제: {delete_result.deleted_count}개")
            
            # 새 이력서 생성
            new_resume = self.create_resume(new_resume_data)
            print(f"✅ 새 이력서 생성: {new_resume.id}")
            
            # 지원자 데이터에 resume_id 업데이트
            self.applicants.update_one(
                {"_id": ObjectId(applicant_id)},
                {"$set": {"resume_id": str(new_resume.id)}}
            )
            print(f"🔄 지원자 데이터 업데이트 완료")
            
            return new_resume
        except Exception as e:
            print(f"❌ 이력서 교체 중 오류: {e}")
            raise
    
    def replace_cover_letter(self, applicant_id: str, new_cover_letter_data: CoverLetterCreate) -> CoverLetterDocument:
        """기존 자기소개서를 새 자기소개서로 교체합니다."""
        try:
            print(f"🔄 자기소개서 교체 시작: 지원자 {applicant_id}")
            
            # 기존 자기소개서 삭제
            delete_result = self.cover_letters.delete_many({"applicant_id": applicant_id})
            print(f"🗑️ 기존 자기소개서 삭제: {delete_result.deleted_count}개")
            
            # 새 자기소개서 생성
            new_cover_letter = self.create_cover_letter(new_cover_letter_data)
            print(f"✅ 새 자기소개서 생성: {new_cover_letter.id}")
            
            # 지원자 데이터에 cover_letter_id 업데이트
            self.applicants.update_one(
                {"_id": ObjectId(applicant_id)},
                {"$set": {"cover_letter_id": str(new_cover_letter.id)}}
            )
            print(f"🔄 지원자 데이터 업데이트 완료")
            
            return new_cover_letter
        except Exception as e:
            print(f"❌ 자기소개서 교체 중 오류: {e}")
            raise
    
    def replace_portfolio(self, applicant_id: str, new_portfolio_data: PortfolioCreate) -> PortfolioDocument:
        """기존 포트폴리오를 새 포트폴리오로 교체합니다."""
        try:
            print(f"🔄 포트폴리오 교체 시작: 지원자 {applicant_id}")
            
            # 기존 포트폴리오 삭제
            delete_result = self.portfolios.delete_many({"applicant_id": applicant_id})
            print(f"🗑️ 기존 포트폴리오 삭제: {delete_result.deleted_count}개")
            
            # 새 포트폴리오 생성
            new_portfolio = self.create_portfolio(new_portfolio_data)
            print(f"✅ 새 포트폴리오 생성: {new_portfolio.id}")
            
            # 지원자 데이터에 portfolio_id 업데이트
            self.applicants.update_one(
                {"_id": ObjectId(applicant_id)},
                {"$set": {"portfolio_id": str(new_portfolio.id)}}
            )
            print(f"🔄 지원자 데이터 업데이트 완료")
            
            return new_portfolio
        except Exception as e:
            print(f"❌ 포트폴리오 교체 중 오류: {e}")
            raise
    
    def check_document_exists(self, applicant_id: str, document_type: str) -> bool:
        """지원자가 특정 종류의 문서를 보유하고 있는지 확인합니다."""
        try:
            if document_type == "resume":
                return self.resumes.find_one({"applicant_id": applicant_id}) is not None
            elif document_type == "cover_letter":
                return self.cover_letters.find_one({"applicant_id": applicant_id}) is not None
            elif document_type == "portfolio":
                return self.portfolios.find_one({"applicant_id": applicant_id}) is not None
            else:
                return False
        except Exception as e:
            print(f"문서 존재 여부 확인 중 오류: {e}")
            return False

    def check_content_duplicate(self, content: str, document_type: str, exclude_applicant_id: str = None) -> Dict[str, Any]:
        """문서 내용의 중복 여부를 확인합니다."""
        try:
            from difflib import SequenceMatcher
            
            # 해당 문서 타입의 컬렉션 선택
            if document_type == "resume":
                collection = self.resumes
            elif document_type == "cover_letter":
                collection = self.cover_letters
            elif document_type == "portfolio":
                collection = self.portfolios
            else:
                return {"is_duplicate": False, "has_similar_content": False, "exact_matches": [], "similar_matches": []}
            
            # 모든 문서 조회 (제외할 지원자 ID가 있으면 제외)
            query = {}
            if exclude_applicant_id:
                query["applicant_id"] = {"$ne": exclude_applicant_id}
            
            documents = list(collection.find(query))
            
            exact_matches = []
            similar_matches = []
            
            for doc in documents:
                doc_content = doc.get("extracted_text", "")
                if not doc_content:
                    continue
                
                # 유사도 계산
                similarity = SequenceMatcher(None, content, doc_content).ratio()
                
                if similarity == 1.0:  # 100% 일치
                    exact_matches.append({
                        "document": doc,
                        "similarity": similarity,
                        "changes": {"similarity": similarity}
                    })
                elif similarity >= 0.9:  # 90% 이상 유사
                    similar_matches.append({
                        "document": doc,
                        "similarity": similarity,
                        "changes": {"similarity": similarity}
                    })
            
            return {
                "is_duplicate": len(exact_matches) > 0,
                "has_similar_content": len(similar_matches) > 0,
                "exact_matches": exact_matches,
                "similar_matches": similar_matches
            }
            
        except Exception as e:
            print(f"내용 중복 검사 중 오류: {e}")
            return {"is_duplicate": False, "has_similar_content": False, "exact_matches": [], "similar_matches": []}

    def get_resume_by_applicant_id(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 ID로 이력서를 조회합니다."""
        try:
            resume = self.resumes.find_one({"applicant_id": applicant_id})
            if resume:
                resume["_id"] = str(resume["_id"])
            return resume
        except Exception as e:
            print(f"이력서 조회 중 오류: {e}")
            return None

    def get_cover_letter_by_applicant_id(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 ID로 자기소개서를 조회합니다."""
        try:
            cover_letter = self.cover_letters.find_one({"applicant_id": applicant_id})
            if cover_letter:
                cover_letter["_id"] = str(cover_letter["_id"])
            return cover_letter
        except Exception as e:
            print(f"자기소개서 조회 중 오류: {e}")
            return None

    def get_portfolio_by_applicant_id(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 ID로 포트폴리오를 조회합니다."""
        try:
            portfolio = self.portfolios.find_one({"applicant_id": applicant_id})
            if portfolio:
                portfolio["_id"] = str(portfolio["_id"])
            return portfolio
        except Exception as e:
            print(f"포트폴리오 조회 중 오류: {e}")
            return None

    # 지원자 목록 조회 및 관리 메서드들
    def get_applicants(self, skip: int = 0, limit: int = 50, status: Optional[ApplicantStatus] = None, 
                       position: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """지원자 목록을 조회합니다. 페이지네이션과 필터링을 지원합니다."""
        try:
            # 쿼리 조건 구성
            query = {}
            
            # 상태별 필터
            if status:
                query["status"] = status.value if hasattr(status, 'value') else status
            
            # 직무별 필터
            if position:
                query["position"] = {"$regex": position, "$options": "i"}
            
            # 검색어 필터 (이름 또는 이메일)
            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}}
                ]
            
            # 지원자 목록 조회 (생성일시 역순)
            cursor = self.applicants.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
            
            applicants = []
            for applicant in cursor:
                applicant["_id"] = str(applicant["_id"])
                applicants.append(applicant)
            
            return applicants
            
        except Exception as e:
            print(f"지원자 목록 조회 중 오류: {e}")
            return []

    def get_applicant(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 ID로 지원자를 조회합니다."""
        try:
            if not ObjectId.is_valid(applicant_id):
                return None
                
            applicant = self.applicants.find_one({"_id": ObjectId(applicant_id)})
            if applicant:
                applicant["_id"] = str(applicant["_id"])
            return applicant
            
        except Exception as e:
            print(f"지원자 조회 중 오류: {e}")
            return None

    def update_applicant(self, applicant_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """지원자 정보를 업데이트합니다."""
        try:
            if not ObjectId.is_valid(applicant_id):
                return None
            
            # updated_at 필드 자동 설정
            update_data["updated_at"] = datetime.utcnow()
            
            result = self.applicants.update_one(
                {"_id": ObjectId(applicant_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # 업데이트된 지원자 정보 반환
                return self.get_applicant(applicant_id)
            return None
            
        except Exception as e:
            print(f"지원자 업데이트 중 오류: {e}")
            return None

    def update_applicant_status(self, applicant_id: str, status_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """지원자 상태를 업데이트합니다."""
        try:
            if not ObjectId.is_valid(applicant_id):
                return None
            
            # 이전 상태 조회
            current_applicant = self.get_applicant(applicant_id)
            if not current_applicant:
                return None
            
            previous_status = current_applicant.get("status", "unknown")
            
            # 상태 변경 이력 추가
            status_history = current_applicant.get("status_history", [])
            status_history.append({
                "previous_status": previous_status,
                "new_status": status_data["status"],
                "changed_at": datetime.utcnow(),
                "reason": status_data.get("status_reason"),
                "updated_by": status_data.get("status_updated_by")
            })
            
            # 업데이트 데이터에 이력 포함
            update_data = {
                **status_data,
                "status_history": status_history,
                "previous_status": previous_status
            }
            
            # 상태 업데이트
            result = self.applicants.update_one(
                {"_id": ObjectId(applicant_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ 지원자 {applicant_id} 상태 변경: {previous_status} → {status_data['status']}")
                return self.get_applicant(applicant_id)
            return None
            
        except Exception as e:
            print(f"지원자 상태 업데이트 중 오류: {e}")
            return None

    def get_applicant_stats(self) -> Dict[str, Any]:
        """지원자 통계를 조회합니다."""
        try:
            # 전체 지원자 수
            total = self.applicants.count_documents({})
            
            # 상태별 지원자 수
            stats = {
                "total": total,
                "pending": 0,
                "document_pass": 0,
                "document_fail": 0,
                "interview_pass": 0,
                "interview_fail": 0,
                "final_pass": 0,
                "final_fail": 0,
                "hold": 0,
                "withdrawn": 0
            }
            
            # 각 상태별 카운트
            pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            
            status_counts = list(self.applicants.aggregate(pipeline))
            
            for status_count in status_counts:
                status = status_count["_id"]
                count = status_count["count"]
                if status in stats:
                    stats[status] = count
            
            # 직무별 통계
            position_pipeline = [
                {"$group": {"_id": "$position", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            position_stats = list(self.applicants.aggregate(position_pipeline))
            stats["by_position"] = position_stats
            
            # 월별 지원자 수 (최근 12개월)
            monthly_pipeline = [
                {"$match": {"created_at": {"$gte": datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)}}},
                {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}}, "count": {"$sum": 1}}},
                {"$sort": {"_id": -1}},
                {"$limit": 12}
            ]
            
            monthly_stats = list(self.applicants.aggregate(monthly_pipeline))
            stats["by_month"] = monthly_stats
            
            return stats
            
        except Exception as e:
            print(f"지원자 통계 조회 중 오류: {e}")
            return {"total": 0}

    def delete_applicant(self, applicant_id: str) -> bool:
        """지원자를 삭제합니다."""
        try:
            if not ObjectId.is_valid(applicant_id):
                return False
            
            # 지원자 삭제
            result = self.applicants.delete_one({"_id": ObjectId(applicant_id)})
            
            # 관련 문서들도 삭제 (선택사항)
            # self.resumes.delete_many({"applicant_id": applicant_id})
            # self.cover_letters.delete_many({"applicant_id": applicant_id})
            # self.portfolios.delete_many({"applicant_id": applicant_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"지원자 삭제 중 오류: {e}")
            return False

    def close(self):
        """MongoDB 연결을 종료합니다."""
        self.client.close()
