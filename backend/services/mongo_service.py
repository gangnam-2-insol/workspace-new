from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
import hashlib
import os

from models.applicant import Applicant, ApplicantCreate
from models.document import ResumeDocument, ResumeCreate, CoverLetterDocument, CoverLetterCreate, PortfolioDocument, PortfolioCreate

class MongoService:
    def __init__(self, mongo_uri: str = None):
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.hireme
        
        # 컬렉션 초기화 (applications 제거)
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
            
            # resumes 컬렉션 인덱스 (application_id 제거)
            self.resumes.create_index([("applicant_id", ASCENDING), ("created_at", DESCENDING)])
            
            # cover_letters 컬렉션 인덱스 (application_id 제거)
            self.cover_letters.create_index([("applicant_id", ASCENDING), ("created_at", DESCENDING)])
            
            # portfolios 컬렉션 인덱스 (application_id 제거)
            self.portfolios.create_index([("applicant_id", ASCENDING), ("version", DESCENDING)], unique=True)
            self.portfolios.create_index([("applicant_id", ASCENDING), ("created_at", DESCENDING)])
            
            # 포트폴리오 스키마 검증 설정
            self._setup_portfolio_schema_validation()
            
            print("✅ MongoDB 인덱스 생성 완료")
        except Exception as e:
            print(f"⚠️ 인덱스 생성 중 오류: {e}")
    
    def _setup_portfolio_schema_validation(self):
        """포트폴리오 컬렉션에 JSON Schema 검증을 설정합니다."""
        try:
            import json
            from pathlib import Path
            
            # 스키마 파일 로드
            schema_path = Path(__file__).parent.parent / "schemas" / "portfolio_schema.json"
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                
                # 기존 검증 규칙 제거 후 새로 설정
                self.db.command({
                    "collMod": "portfolios",
                    "validator": schema,
                    "validationLevel": "moderate",
                    "validationAction": "error"
                })
                print("✅ 포트폴리오 스키마 검증 설정 완료")
            else:
                print("⚠️ 포트폴리오 스키마 파일을 찾을 수 없습니다")
        except Exception as e:
            print(f"⚠️ 포트폴리오 스키마 검증 설정 중 오류: {e}")
    
    # Applicant 관련 메서드
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
        except Exception:
            return None
    
    # Document 관련 메서드들 (application_id 제거)
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
    
    # Bundle 관련 메서드 (applicant_id 기반으로 변경)
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
    
    def close(self):
        """MongoDB 연결을 종료합니다."""
        self.client.close()
