import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
from typing import List, Optional, Dict, Any
import locale
import codecs
from datetime import datetime
from datetime import timedelta
import csv
from chatbot import chatbot_router, langgraph_router
from github import router as github_router
from routers.upload import router as upload_router
from routers.pick_chatbot import router as pick_chatbot_router
from routers.integrated_ocr import router as integrated_ocr_router

from routers.pdf_ocr import router as pdf_ocr_router


from similarity_service import SimilarityService
from embedding_service import EmbeddingService
from vector_service import VectorService
from services.mongo_service import MongoService

# Python 환경 인코딩 설정
# 시스템 기본 인코딩을 UTF-8로 설정
if sys.platform.startswith('win'):
    # Windows 환경에서 UTF-8 강제 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # 콘솔 출력 인코딩 설정
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# FastAPI 앱 생성
app = FastAPI(title="AI 채용 관리 시스템 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 한글 인코딩을 위한 미들웨어
@app.middleware("http")
async def add_charset_header(request, call_next):
    response = await call_next(request)
    
    # 모든 JSON 응답에 UTF-8 인코딩 명시
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["content-type"] = "application/json; charset=utf-8"
    
    # 텍스트 응답에도 UTF-8 인코딩 명시
    elif response.headers.get("content-type", "").startswith("text/"):
        if "charset" not in response.headers.get("content-type", ""):
            current_content_type = response.headers.get("content-type", "")
            response.headers["content-type"] = f"{current_content_type}; charset=utf-8"
    
    return response

# 라우터 등록
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["chatbot"])
app.include_router(langgraph_router, prefix="/api/langgraph", tags=["langgraph"])
# 프론트엔드 호환을 위해 /api/langgraph-agent 프리픽스도 동일 라우터로 마운트
app.include_router(langgraph_router, prefix="/api/langgraph-agent", tags=["langgraph-agent"])
app.include_router(github_router, prefix="/api", tags=["github"])
app.include_router(upload_router, tags=["upload"])
app.include_router(pick_chatbot_router, prefix="/api", tags=["pick-chatbot"])
app.include_router(integrated_ocr_router, prefix="/api/integrated-ocr", tags=["integrated-ocr"])
# 프론트엔드 호환을 위해 /upload 경로에도 등록
app.include_router(integrated_ocr_router, prefix="/upload", tags=["upload-compat"])

app.include_router(pdf_ocr_router, prefix="/api/pdf-ocr", tags=["pdf_ocr"])


# MongoDB 연결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
client = AsyncIOMotorClient(MONGODB_URI)
db = client.hireme

# 환경 변수에서 API 키 로드
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") 
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "resume-vectors")

# 서비스 초기화
embedding_service = EmbeddingService()
vector_service = VectorService(
    api_key=PINECONE_API_KEY or "dummy-key",  # API 키가 없어도 서버 시작은 가능
    index_name=PINECONE_INDEX_NAME
)
similarity_service = SimilarityService(embedding_service, vector_service)

# Pydantic 모델들
class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    role: str = "user"
    created_at: Optional[datetime] = None

class Resume(BaseModel):
    id: Optional[str] = None
    resume_id: Optional[str] = None
    name: str
    position: str
    department: Optional[str] = ""
    experience: int
    skills: List[str]
    growthBackground: Optional[str] = ""
    motivation: Optional[str] = ""
    careerHistory: Optional[str] = ""
    analysisScore: int = 0
    analysisResult: str = ""
    status: str = "pending"
    created_at: Optional[datetime] = None

class ResumeChunk(BaseModel):
    id: Optional[str] = None
    resume_id: str
    chunk_id: str
    text: str
    start_pos: int
    end_pos: int
    chunk_index: int
    field_name: Optional[str] = None  # growthBackground, motivation, careerHistory
    metadata: Optional[Dict[str, Any]] = None
    vector_id: Optional[str] = None  # Pinecone 벡터 ID
    created_at: Optional[datetime] = None

class Interview(BaseModel):
    id: Optional[str] = None
    user_id: str
    company: str
    position: str
    date: datetime
    status: str = "scheduled"
    created_at: Optional[datetime] = None

# 초기 데이터 로딩 유틸리티: DB가 비어있으면 루트 CSV에서 임포트
async def seed_applicants_from_csv_if_empty() -> None:
    try:
        total_documents = await db.applicants.count_documents({})
        if total_documents > 0:
            return

        project_root_csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "hireme.applicants.csv")
        )
        if not os.path.exists(project_root_csv_path):
            return

        documents_to_insert = []
        with open(project_root_csv_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                document: Dict[str, Any] = {}

                # _id 처리: 가능하면 ObjectId로 저장
                raw_id = row.get("_id")
                if raw_id and isinstance(raw_id, str) and len(raw_id) == 24:
                    try:
                        document["_id"] = ObjectId(raw_id)
                    except Exception:
                        document["_id"] = raw_id

                # resume_id 처리
                raw_resume_id = row.get("resume_id")
                if raw_resume_id and isinstance(raw_resume_id, str) and len(raw_resume_id) == 24:
                    try:
                        document["resume_id"] = ObjectId(raw_resume_id)
                    except Exception:
                        document["resume_id"] = raw_resume_id
                elif raw_resume_id:
                    document["resume_id"] = raw_resume_id

                # 문자열 필드들: 항상 문자열로 캐스팅
                string_fields = [
                    "name",
                    "position",
                    "department",
                    "growthBackground",
                    "motivation",
                    "careerHistory",
                    "analysisResult",
                    "status",
                ]
                for field_name in string_fields:
                    value = row.get(field_name, "")
                    document[field_name] = "" if value is None else str(value)
                
                # experience 필드: 정수로 처리
                try:
                    experience_value = row.get("experience", "0")
                    document["experience"] = int(experience_value) if experience_value else 0
                except (ValueError, TypeError):
                    document["experience"] = 0
                
                # skills 필드: 리스트로 처리
                skills_value = row.get("skills", "")
                if skills_value:
                    # 쉼표로 구분된 문자열을 리스트로 변환
                    skills_list = [skill.strip() for skill in str(skills_value).split(",") if skill.strip()]
                    document["skills"] = skills_list
                else:
                    document["skills"] = []

                # 숫자 필드
                try:
                    document["analysisScore"] = int(row.get("analysisScore", "0") or 0)
                except Exception:
                    document["analysisScore"] = 0

                # created_at 처리
                created_at_raw = row.get("created_at")
                if created_at_raw:
                    try:
                        iso_candidate = created_at_raw.replace("Z", "+00:00")
                        document["created_at"] = datetime.fromisoformat(iso_candidate)
                    except Exception:
                        document["created_at"] = datetime.now()

                documents_to_insert.append(document)

        if documents_to_insert:
            print(f"🔎 시드 대상 문서 수: {len(documents_to_insert)}")
            
            # 중복 체크 및 업데이트
            inserted_count = 0
            updated_count = 0
            
            for document in documents_to_insert:
                try:
                    # 기존 문서가 있는지 확인
                    existing = await db.applicants.find_one({"name": document.get("name"), "position": document.get("position")})
                    if existing:
                        # 기존 문서 업데이트
                        await db.applicants.update_one(
                            {"_id": existing["_id"]},
                            {"$set": document}
                        )
                        updated_count += 1
                    else:
                        # 새 문서 삽입
                        await db.applicants.insert_one(document)
                        inserted_count += 1
                except Exception as e:
                    print(f"문서 처리 실패: {e}")
                    continue
            
            new_count = await db.applicants.count_documents({})
            print(f"📥 CSV 처리 완료 → 삽입: {inserted_count}건, 업데이트: {updated_count}건, 총 문서 수: {new_count}")
    except Exception as seed_error:
                    print(f"[ERROR] CSV 임포트 실패: {seed_error}")


def load_applicants_from_csv() -> List[Dict[str, Any]]:
    """DB 미가동/비어있을 때 CSV를 직접 읽어 반환"""
    try:
        project_root_csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "hireme.applicants.csv")
        )
        if not os.path.exists(project_root_csv_path):
            return []

        applicants: List[Dict[str, Any]] = []
        with open(project_root_csv_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                item: Dict[str, Any] = {}
                # id/_id
                raw_id = row.get("_id") or row.get("id")
                if raw_id:
                    item["id"] = str(raw_id)

                # 기본 문자열 필드
                for field_name in [
                    "name",
                    "position",
                    "department",
                    "growthBackground",
                    "motivation",
                    "careerHistory",
                    "analysisResult",
                    "status",
                ]:
                    value = row.get(field_name, "")
                    item[field_name] = "" if value is None else str(value)
                
                # experience 필드: 정수로 처리
                try:
                    experience_value = row.get("experience", "0")
                    item["experience"] = int(experience_value) if experience_value else 0
                except (ValueError, TypeError):
                    item["experience"] = 0
                
                # skills 필드: 리스트로 처리
                skills_value = row.get("skills", "")
                if skills_value:
                    # 쉼표로 구분된 문자열을 리스트로 변환
                    skills_list = [skill.strip() for skill in str(skills_value).split(",") if skill.strip()]
                    item["skills"] = skills_list
                else:
                    item["skills"] = []

                # score
                try:
                    item["analysisScore"] = int(row.get("analysisScore", "0") or 0)
                except Exception:
                    item["analysisScore"] = 0

                # created_at
                created_at_raw = row.get("created_at")
                if created_at_raw:
                    try:
                        iso_candidate = created_at_raw.replace("Z", "+00:00")
                        item["created_at"] = datetime.fromisoformat(iso_candidate)
                    except Exception:
                        item["created_at"] = datetime.now()

                applicants.append(item)
        return applicants
    except Exception:
        return []

# API 라우트들
@app.get("/")
async def root():
    return {"message": "AI 채용 관리 시스템 API가 실행 중입니다."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "서버가 정상적으로 작동 중입니다."}

# 사용자 관련 API
@app.get("/api/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(1000)
    # MongoDB의 _id를 id로 변환
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return [User(**user) for user in users]

@app.post("/api/users", response_model=User)
async def create_user(user: User):
    user_dict = user.dict()
    user_dict["created_at"] = datetime.now()
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return User(**user_dict)

# 이력서 관련 API
@app.get("/api/resumes", response_model=List[Resume])
async def get_resumes():
    resumes = await db.resumes.find().to_list(1000)
    # MongoDB의 _id를 id로 변환
    for resume in resumes:
        resume["id"] = str(resume["_id"])
        del resume["_id"]
    return [Resume(**resume) for resume in resumes]

@app.post("/api/resumes", response_model=Resume)
async def create_resume(resume: Resume):
    resume_dict = resume.dict()
    resume_dict["created_at"] = datetime.now()
    result = await db.resumes.insert_one(resume_dict)
    resume_dict["id"] = str(result.inserted_id)
    return Resume(**resume_dict)

# 면접 관련 API
@app.get("/api/interviews", response_model=List[Interview])
async def get_interviews():
    interviews = await db.interviews.find().to_list(1000)
    # MongoDB의 _id를 id로 변환
    for interview in interviews:
        interview["id"] = str(interview["_id"])
        del interview["_id"]
    return [Interview(**interview) for interview in interviews]

@app.post("/api/interviews", response_model=Interview)
async def create_interview(interview: Interview):
    interview_dict = interview.dict()
    interview_dict["created_at"] = datetime.now()
    result = await db.interviews.insert_one(interview_dict)
    interview_dict["id"] = str(result.inserted_id)
    return Interview(**interview_dict)

# 지원자 관련 API
@app.get("/api/applicants")
async def get_applicants(skip: int = 0, limit: int = 20):
    try:
        # DB가 비어있으면 CSV에서 자동 임포트
        await seed_applicants_from_csv_if_empty()
        # 총 문서 수
        total_count = await db.applicants.count_documents({})

        if total_count == 0:
            # DB가 완전 비어있을 때 CSV를 가상 DB처럼 반환
            csv_applicants = load_applicants_from_csv()
            items = csv_applicants[skip:skip+limit]
            return {
                "applicants": [Resume(**a) for a in items],
                "total_count": len(csv_applicants),
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < len(csv_applicants)
            }

        # 페이징으로 이력서(지원자) 목록 조회
        applicants = await db.applicants.find().skip(skip).limit(limit).to_list(limit)

        # MongoDB의 _id를 id로 변환 및 ObjectId 필드들을 문자열로 변환
        for applicant in applicants:
            applicant["id"] = str(applicant["_id"])
            del applicant["_id"]
            if "resume_id" in applicant and applicant["resume_id"]:
                applicant["resume_id"] = str(applicant["resume_id"])

        return {
            "applicants": [Resume(**applicant) for applicant in applicants],
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 목록 조회 실패: {str(e)}")

# 개별 지원자 조회 API
@app.get("/api/applicants/{applicant_id}")
async def get_applicant(applicant_id: str):
    try:
        # MongoDB ObjectId로 조회 시도
        try:
            applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
        except:
            # ObjectId 변환 실패시 문자열로 조회
            applicant = await db.applicants.find_one({"_id": applicant_id})
        
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")
        
        # MongoDB의 _id를 id로 변환
        applicant["id"] = str(applicant["_id"])
        del applicant["_id"]
        if "resume_id" in applicant and applicant["resume_id"]:
            applicant["resume_id"] = str(applicant["resume_id"])
        
        return Resume(**applicant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 조회 실패: {str(e)}")

# 지원자 통계 API
@app.get("/api/applicants/stats/overview")
async def get_applicant_stats():
    try:
        # DB가 비어있으면 CSV에서 자동 임포트
        await seed_applicants_from_csv_if_empty()
        # 총 지원자 수 (resumes 컬렉션 기준)
        total_applicants = await db.resumes.count_documents({})

        if total_applicants == 0:
            # CSV 기반 가상 통계
            csv_applicants = load_applicants_from_csv()
            total = len(csv_applicants)
            status_counts = {"pending": 0, "approved": 0, "rejected": 0}
            for a in csv_applicants:
                s = (a.get("status") or "").lower()
                if s in status_counts:
                    status_counts[s] += 1
            return {
                "total_applicants": total,
                "status_breakdown": status_counts,
                "recent_applicants_30_days": total,
                "success_rate": round((status_counts.get("approved", 0) / total * 100) if total > 0 else 0, 2)
            }

        # 상태별 지원자 수
        pending_count = await db.resumes.count_documents({"status": "pending"})
        approved_count = await db.resumes.count_documents({"status": "approved"})
        rejected_count = await db.resumes.count_documents({"status": "rejected"})
        
        # 최근 30일간 지원자 수 (월 경계/윤달 이슈 없이 안전하게 계산)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_applicants = await db.resumes.count_documents({"created_at": {"$gte": thirty_days_ago}})
        
        return {
            "total_applicants": total_applicants,
            "status_breakdown": {
                "pending": pending_count,
                "approved": approved_count,
                "rejected": rejected_count
            },
            "recent_applicants_30_days": recent_applicants,
            "success_rate": round((approved_count / total_applicants * 100) if total_applicants > 0 else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 통계 조회 실패: {str(e)}")

# Vector Service API
@app.post("/api/vector/create")
async def create_vector(data: Dict[str, Any]):
    """텍스트를 벡터로 변환하여 저장"""
    try:
        text = data.get("text", "")
        document_id = data.get("document_id")
        metadata = data.get("metadata", {})
        
        # 여기서 실제 벡터화 로직 구현
        # 예: embedding_model을 사용하여 텍스트를 벡터로 변환
        
        # 임시로 성공 응답 반환
        return {
            "message": "Vector created successfully",
            "document_id": document_id,
            "vector_dimension": 384,  # 예시 차원
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"벡터 생성 실패: {str(e)}")

@app.post("/api/vector/search")
async def search_vectors(data: Dict[str, Any]):
    """벡터 유사도 검색"""
    try:
        query_text = data.get("query", "")
        top_k = data.get("top_k", 5)
        threshold = data.get("threshold", 0.7)
        
        # 여기서 실제 벡터 검색 로직 구현
        
        # 임시로 검색 결과 반환
        return {
            "results": [
                {
                    "document_id": "doc_001",
                    "score": 0.95,
                    "text": "검색된 텍스트 샘플 1",
                    "metadata": {"type": "resume", "applicant_id": "app_001"}
                },
                {
                    "document_id": "doc_002", 
                    "score": 0.87,
                    "text": "검색된 텍스트 샘플 2",
                    "metadata": {"type": "cover_letter", "applicant_id": "app_002"}
                }
            ],
            "total_found": 2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"벡터 검색 실패: {str(e)}")

# Chunking Service API
@app.post("/api/chunking/split")
async def split_text(data: Dict[str, Any]):
    """텍스트를 청크로 분할하고 DB에 저장"""
    try:
        text = data.get("text", "")
        resume_id = data.get("resume_id")
        field_name = data.get("field_name", "")  # growthBackground, motivation, careerHistory
        chunk_size = data.get("chunk_size", 1000)
        chunk_overlap = data.get("chunk_overlap", 200)
        split_type = data.get("split_type", "recursive")
        
        if not resume_id:
            raise HTTPException(status_code=400, detail="resume_id가 필요합니다.")
        
        # 텍스트 분할 로직
        chunks = []
        text_length = len(text)
        start = 0
        chunk_index = 0
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk_text = text[start:end]
            
            if chunk_text.strip():  # 빈 청크는 제외
                chunk_id = f"chunk_{chunk_index:03d}"
                vector_id = f"resume_{resume_id}_{chunk_id}"
                
                chunk_doc = {
                    "resume_id": resume_id,
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "start_pos": start,
                    "end_pos": end,
                    "chunk_index": chunk_index,
                    "field_name": field_name,
                    "vector_id": vector_id,
                    "metadata": {
                        "length": len(chunk_text),
                        "split_type": split_type,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap
                    },
                    "created_at": datetime.now()
                }
                
                # MongoDB에 청크 저장
                result = await db.resume_chunks.insert_one(chunk_doc)
                chunk_doc["id"] = str(result.inserted_id)
                
                chunks.append(chunk_doc)
                chunk_index += 1
            
            start = end - chunk_overlap if chunk_overlap > 0 else end
            
            if start >= text_length:
                break
        
        return {
            "chunks": chunks,
            "total_chunks": len(chunks),
            "original_length": text_length,
            "resume_id": resume_id,
            "field_name": field_name,
            "split_config": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "split_type": split_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 분할 실패: {str(e)}")

@app.get("/api/chunking/resume/{resume_id}")
async def get_resume_chunks(resume_id: str):
    """특정 이력서의 모든 청크 조회"""
    try:
        chunks = await db.resume_chunks.find({"resume_id": resume_id}).to_list(1000)
        
        # MongoDB의 _id를 id로 변환
        for chunk in chunks:
            chunk["id"] = str(chunk["_id"])
            del chunk["_id"]
        
        return {
            "resume_id": resume_id,
            "chunks": [ResumeChunk(**chunk) for chunk in chunks],
            "total_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"청크 조회 실패: {str(e)}")

@app.post("/api/chunking/process-resume")
async def process_resume_with_chunking(data: Dict[str, Any]):
    """이력서 전체를 필드별로 청킹 처리"""
    try:
        resume_id = data.get("resume_id")
        if not resume_id:
            raise HTTPException(status_code=400, detail="resume_id가 필요합니다.")
        
        # 이력서 정보 조회
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")
        
        chunk_size = data.get("chunk_size", 800)
        chunk_overlap = data.get("chunk_overlap", 150)
        
        # 청킹할 필드들
        fields_to_chunk = ["growthBackground", "motivation", "careerHistory"]
        all_chunks = []
        
        for field_name in fields_to_chunk:
            field_text = resume.get(field_name, "")
            if field_text and field_text.strip():
                # 필드별 청킹 처리
                field_chunks = []
                text_length = len(field_text)
                start = 0
                chunk_index = 0
                
                while start < text_length:
                    end = min(start + chunk_size, text_length)
                    chunk_text = field_text[start:end]
                    
                    if chunk_text.strip():
                        chunk_id = f"{field_name}_chunk_{chunk_index:03d}"
                        vector_id = f"resume_{resume_id}_{chunk_id}"
                        
                        chunk_doc = {
                            "resume_id": resume_id,
                            "chunk_id": chunk_id,
                            "text": chunk_text,
                            "start_pos": start,
                            "end_pos": end,
                            "chunk_index": chunk_index,
                            "field_name": field_name,
                            "vector_id": vector_id,
                            "metadata": {
                                "applicant_name": resume.get("name", ""),
                                "position": resume.get("position", ""),
                                "department": resume.get("department", ""),
                                "length": len(chunk_text)
                            },
                            "created_at": datetime.now()
                        }
                        
                        result = await db.resume_chunks.insert_one(chunk_doc)
                        chunk_doc["id"] = str(result.inserted_id)
                        field_chunks.append(chunk_doc)
                        chunk_index += 1
                    
                    start = end - chunk_overlap if chunk_overlap > 0 else end
                    if start >= text_length:
                        break
                
                all_chunks.extend(field_chunks)
        
        return {
            "resume_id": resume_id,
            "applicant_name": resume.get("name", ""),
            "processed_fields": fields_to_chunk,
            "total_chunks": len(all_chunks),
            "chunks_by_field": {
                field: len([c for c in all_chunks if c["field_name"] == field])
                for field in fields_to_chunk
            },
            "chunks": all_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력서 청킹 처리 실패: {str(e)}")

@app.post("/api/chunking/merge")
async def merge_chunks(data: Dict[str, Any]):
    """청크들을 병합"""
    try:
        chunks = data.get("chunks", [])
        separator = data.get("separator", "\n\n")
        
        # 청크 병합
        merged_text = separator.join([chunk.get("text", "") for chunk in chunks])
        
        return {
            "merged_text": merged_text,
            "total_length": len(merged_text),
            "chunks_merged": len(chunks),
            "separator_used": separator
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"청크 병합 실패: {str(e)}")

# Similarity Service API
@app.post("/api/similarity/compare")
async def compare_similarity(data: Dict[str, Any]):
    """두 텍스트 간의 유사도 계산"""
    try:
        text1 = data.get("text1", "")
        text2 = data.get("text2", "")
        method = data.get("method", "cosine")  # cosine, jaccard, levenshtein
        
        # 여기서 실제 유사도 계산 로직 구현
        # 예: sentence-transformers의 cosine similarity
        
        # 임시로 유사도 점수 반환
        import random
        similarity_score = random.uniform(0.3, 0.95)  # 임시 점수
        
        return {
            "similarity_score": round(similarity_score, 4),
            "method": method,
            "text1_length": len(text1),
            "text2_length": len(text2),
            "comparison_result": {
                "highly_similar": similarity_score > 0.8,
                "moderately_similar": 0.5 < similarity_score <= 0.8,
                "low_similar": similarity_score <= 0.5
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사도 계산 실패: {str(e)}")

@app.post("/api/similarity/batch")
async def batch_similarity(data: Dict[str, Any]):
    """여러 텍스트들 간의 일괄 유사도 계산"""
    try:
        texts = data.get("texts", [])
        reference_text = data.get("reference_text", "")
        method = data.get("method", "cosine")
        threshold = data.get("threshold", 0.7)
        
        # 배치 유사도 계산
        results = []
        import random
        
        for i, text in enumerate(texts):
            similarity_score = random.uniform(0.2, 0.95)  # 임시 점수
            results.append({
                "index": i,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "similarity_score": round(similarity_score, 4),
                "above_threshold": similarity_score >= threshold
            })
        
        # 임계값 이상인 결과들 필터링
        filtered_results = [r for r in results if r["above_threshold"]]
        
        return {
            "results": results,
            "filtered_results": filtered_results,
            "total_compared": len(texts),
            "above_threshold_count": len(filtered_results),
            "method": method,
            "threshold": threshold,
            "reference_text_length": len(reference_text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 유사도 계산 실패: {str(e)}")

@app.get("/api/similarity/metrics")
async def get_similarity_metrics():
    """유사도 서비스 메트릭 조회"""
    try:
        # 임시 메트릭 데이터
        return {
            "total_comparisons": 1250,
            "average_similarity": 0.67,
            "supported_methods": ["cosine", "jaccard", "levenshtein", "semantic"],
            "performance_stats": {
                "average_processing_time_ms": 45,
                "comparisons_per_second": 220,
                "cache_hit_rate": 0.78
            },
            "usage_by_method": {
                "cosine": 850,
                "semantic": 300,
                "jaccard": 70,
                "levenshtein": 30
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메트릭 조회 실패: {str(e)}")

# 다중 하이브리드 검색 API 🆕
@app.post("/api/resume/search/multi-hybrid")
async def search_resumes_multi_hybrid(data: Dict[str, Any]):
    """다중 하이브리드 검색: 벡터 + 텍스트 + 키워드 검색을 결합"""
    try:
        query = data.get("query", "")
        search_type = data.get("type", "resume")
        limit = data.get("limit", 10)
        
        print(f"[API] 다중 하이브리드 검색 요청 - 쿼리: '{query}', 제한: {limit}")
        
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="검색어를 입력해주세요.")
        
        # SimilarityService의 다중 하이브리드 검색 실행
        result = await similarity_service.search_resumes_multi_hybrid(
            query=query,
            collection=db.applicants,
            search_type=search_type,
            limit=limit
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="다중 하이브리드 검색에 실패했습니다.")
        
        return {
            "success": True,
            "message": f"다중 하이브리드 검색 완료: '{query}'",
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] 다중 하이브리드 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"다중 하이브리드 검색 실패: {str(e)}")

# 키워드 검색 API
@app.post("/api/resume/search/keyword")
async def search_resumes_keyword(data: Dict[str, Any]):
    """키워드 기반 이력서 검색 (BM25)"""
    try:
        query = data.get("query", "")
        limit = data.get("limit", 10)
        
        print(f"[API] 키워드 검색 요청 - 쿼리: '{query}', 제한: {limit}")
        
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="검색어를 입력해주세요.")
        
        # KeywordSearchService를 통한 BM25 검색
        result = await similarity_service.keyword_search_service.search_by_keywords(
            query=query,
            collection=db.applicants,
            limit=limit
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "키워드 검색에 실패했습니다."))
        
        return {
            "success": True,
            "message": result["message"],
            "data": {
                "query": result["query"],
                "results": result["results"],
                "total": result["total"],
                "search_method": "keyword_bm25",
                "query_tokens": result.get("query_tokens", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] 키워드 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"키워드 검색 실패: {str(e)}")

# 키워드 검색 인덱스 관리 API
@app.post("/api/resume/search/keyword/rebuild-index")
async def rebuild_keyword_index():
    """키워드 검색 인덱스 재구축"""
    try:
        print(f"[API] 키워드 인덱스 재구축 요청")
        
        # KeywordSearchService를 통한 인덱스 재구축
        result = await similarity_service.keyword_search_service.build_index(db.applicants)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "인덱스 재구축에 실패했습니다."))
        
        return {
            "success": True,
            "message": result["message"],
            "data": {
                "total_documents": result["total_documents"],
                "index_created_at": result["index_created_at"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] 키워드 인덱스 재구축 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"키워드 인덱스 재구축 실패: {str(e)}")

@app.get("/api/resume/search/keyword/stats")
async def get_keyword_search_stats():
    """키워드 검색 인덱스 통계 조회"""
    try:
        stats = await similarity_service.keyword_search_service.get_index_stats()
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        print(f"[API] 키워드 검색 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"키워드 검색 통계 조회 실패: {str(e)}")

# 유사 인재 추천 API
@app.post("/api/applicants/similar-recommendation/{applicant_id}")
async def recommend_similar_applicants(applicant_id: str):
    """지원자 기반 유사 인재 추천 (하이브리드 검색: 벡터 + 키워드)"""
    try:
        print(f"\n=== [SIMILAR_APPLICANTS] 유사 인재 추천 시작 ===")
        print(f"[SIMILAR_APPLICANTS] 요청 applicant_id: {applicant_id}")
        print(f"[SIMILAR_APPLICANTS] 요청 시간: {datetime.now().isoformat()}")
        
        # MongoDB 서비스 초기화
        mongo_service = MongoService()
        print(f"[SIMILAR_APPLICANTS] MongoDB 서비스 초기화 완료")
        
        # 1. 지원자 정보 조회
        print(f"[SIMILAR_APPLICANTS] 지원자 정보 조회 중...")
        applicant = await mongo_service.get_applicant_by_id(applicant_id)
        if not applicant:
            print(f"[SIMILAR_APPLICANTS] ❌ 지원자를 찾을 수 없음 - ID: {applicant_id}")
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "APPLICANT_NOT_FOUND",
                    "message": "지원자를 찾을 수 없습니다."
                }
            )
        
        print(f"[SIMILAR_APPLICANTS] ✅ 지원자 찾음:")
        print(f"[SIMILAR_APPLICANTS]   - 이름: {applicant.get('name', 'N/A')}")
        print(f"[SIMILAR_APPLICANTS]   - 이메일: {applicant.get('email', 'N/A')}")
        print(f"[SIMILAR_APPLICANTS]   - 지원직무: {applicant.get('position', 'N/A')}")
        print(f"[SIMILAR_APPLICANTS]   - resume_id: {applicant.get('resume_id', 'N/A')}")
        
        # 2. 지원자 기반 유사 인재 추천 수행
        print(f"[SIMILAR_APPLICANTS] 지원자 기반 하이브리드 검색 시작...")
        applicants_collection = mongo_service.db.applicants
        
        # 지원자 기반 유사 인재 추천 수행
        result = await similarity_service.search_similar_applicants_hybrid(
            target_applicant=applicant,
            applicants_collection=applicants_collection,
            limit=10
        )
        
        print(f"[SIMILAR_APPLICANTS] ✅ 하이브리드 유사도 분석 완료")
        print(f"[SIMILAR_APPLICANTS] 결과 요약:")
        if result.get("success"):
            results = result.get("data", {}).get("results", [])
            similar_count = len(results)
            vector_count = result.get("data", {}).get("vector_count", 0)
            keyword_count = result.get("data", {}).get("keyword_count", 0)
            
            print(f"[SIMILAR_APPLICANTS]   - 유사한 지원자 수: {similar_count}")
            print(f"[SIMILAR_APPLICANTS]   - 벡터 검색 결과: {vector_count}개")
            print(f"[SIMILAR_APPLICANTS]   - 키워드 검색 결과: {keyword_count}개")
            
            if similar_count > 0:
                for i, sim_applicant in enumerate(results[:3]):
                    final_score = sim_applicant.get("final_score", 0)
                    vector_score = sim_applicant.get("vector_score", 0)
                    keyword_score = sim_applicant.get("keyword_score", 0)
                    name = sim_applicant.get("applicant", {}).get("name", "N/A")
                    position = sim_applicant.get("applicant", {}).get("position", "N/A")
                    methods = sim_applicant.get("search_methods", [])
                    print(f"[SIMILAR_APPLICANTS]   - #{i+1}: {name} ({position}) (최종:{final_score:.3f}, V:{vector_score:.3f}, K:{keyword_score:.3f}, 방법:{methods})")
        else:
            print(f"[SIMILAR_APPLICANTS]   - 분석 실패: {result}")
        
        print(f"=== [SIMILAR_APPLICANTS] 유사 인재 추천 완료 ===\n")
        
        # 결과 반환
        if result.get("success"):
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "유사 인재 추천 완료",
                    "data": result.get("data", {})
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "SIMILARITY_SEARCH_FAILED",
                    "message": result.get("message", "유사 인재 추천 중 오류가 발생했습니다.")
                }
            )
        
    except ValueError as ve:
        print(f"[ERROR] 이력서 유사도 체크 - 값 오류: {str(ve)}")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "NOT_FOUND",
                "message": str(ve)
            }
        )
    except Exception as e:
        print(f"[SIMILAR_APPLICANTS] ❌ 시스템 오류: {str(e)}")
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[SIMILAR_APPLICANTS] 상세 오류 정보:")
        print(error_traceback)
        
        # 지원자가 삭제되어 관련 데이터를 찾을 수 없는 경우 404 반환
        error_message = str(e).lower()
        if "not found" in error_message or "찾을 수 없" in error_message or "deleted" in error_message:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "APPLICANT_OR_DATA_NOT_FOUND",
                    "message": "지원자 또는 관련 데이터를 찾을 수 없습니다."
                }
            )
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": f"유사 인재 추천 중 오류가 발생했습니다: {str(e)}"
            }
        )

# 자소서 표절체크 엔드포인트
@app.post("/api/coverletter/similarity-check/{applicant_id}")
async def check_coverletter_plagiarism(applicant_id: str):
    """자소서 표절체크 전용 엔드포인트 (applicant_id 기반)"""
    try:
        print(f"[INFO] 자소서 표절체크 요청 - applicant_id: {applicant_id}")
        
        # MongoDB 서비스 초기화
        mongo_service = MongoService()
        
        # 1. 지원자 정보 조회
        applicant = await mongo_service.get_applicant_by_id(applicant_id)
        print(f"[DEBUG] 지원자 조회 결과: {applicant is not None}")
        if applicant:
            print(f"[DEBUG] 지원자 필드: {list(applicant.keys())}")
            print(f"[DEBUG] cover_letter_id: {applicant.get('cover_letter_id', 'NONE')}")
        
        if not applicant:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "APPLICANT_NOT_FOUND",
                    "message": "지원자를 찾을 수 없습니다."
                }
            )
        
        # 2. 자소서 ID 추출
        cover_letter_id = applicant.get("cover_letter_id")
        print(f"[DEBUG] cover_letter_id 값: {cover_letter_id}")
        print(f"[DEBUG] cover_letter_id 타입: {type(cover_letter_id)}")
        
        if not cover_letter_id:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "COVER_LETTER_NOT_FOUND",
                    "message": f"해당 지원자({applicant_id})의 자소서가 없습니다. cover_letter_id 필드가 비어있거나 null입니다.",
                    "debug_info": {
                        "applicant_id": applicant_id,
                        "has_applicant": True,
                        "cover_letter_id": cover_letter_id,
                        "applicant_fields": list(applicant.keys())
                    }
                }
            )
        
        print(f"[INFO] 자소서 ID 추출 완료: {cover_letter_id}")
        
        # 3. 자소서 컬렉션에서 검색
        cover_letters_collection = mongo_service.db.cover_letters
        
        # 4. 자소서 표절체크 수행
        result = await similarity_service.find_similar_documents(
            document_id=cover_letter_id,
            collection=cover_letters_collection,
            document_type="cover_letter",
            limit=5
        )
        
        # 결과 반환
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "자소서 표절체크 완료",
                "data": result
            }
        )
        
    except ValueError as ve:
        print(f"[ERROR] 자소서 표절체크 - 값 오류: {str(ve)}")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "NOT_FOUND",
                "message": str(ve)
            }
        )
    except Exception as e:
        print(f"[ERROR] 자소서 표절체크 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": f"자소서 표절체크 중 오류가 발생했습니다: {str(e)}"
            }
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)