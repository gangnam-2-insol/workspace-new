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

from routers.pdf_ocr import router as pdf_ocr_router


from similarity_service import SimilarityService
from embedding_service import EmbeddingService
from vector_service import VectorService

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
    department: str
    experience: str
    skills: str
    growthBackground: str
    motivation: str
    careerHistory: str
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
                    "experience",
                    "skills",
                    "growthBackground",
                    "motivation",
                    "careerHistory",
                    "analysisResult",
                    "status",
                ]
                for field_name in string_fields:
                    value = row.get(field_name, "")
                    document[field_name] = "" if value is None else str(value)

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
            await db.applicants.insert_many(documents_to_insert)
            new_count = await db.applicants.count_documents({})
            print(f"📥 CSV에서 {len(documents_to_insert)}건 임포트 완료 → 현재 총 문서 수: {new_count}")
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
                    "experience",
                    "skills",
                    "growthBackground",
                    "motivation",
                    "careerHistory",
                    "analysisResult",
                    "status",
                ]:
                    value = row.get(field_name, "")
                    item[field_name] = "" if value is None else str(value)

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

# 이력서 유사도 체크 API
@app.post("/api/resume/similarity-check/{resume_id}")
async def check_resume_similarity(resume_id: str):
    """특정 이력서의 유사도 체크 (다른 모든 이력서와 비교)"""
    try:
        print(f"[INFO] 유사도 체크 요청 - resume_id: {resume_id}")
        
        # SimilarityService를 통한 청킹 기반 유사도 분석
        result = await similarity_service.find_similar_resumes_by_chunks(resume_id, db.applicants, limit=50)
        
        # 현재 이력서 정보 조회
        current_resume = await db.applicants.find_one({"_id": object_id})
        print(f"[INFO] 데이터베이스 조회 결과: {current_resume is not None}")
        
        # 청킹 기반 API 응답 형식에 맞게 변환
        similarity_results = []
        for similar in result["data"]["similar_resumes"]:
            # 청킹 상세 정보에서 필드별 유사도 추출
            chunk_details = similar.get("chunk_details", {})
            field_similarities = {
                "growthBackground": 0.0,
                "motivation": 0.0,
                "careerHistory": 0.0
            }
            
            # 청크 매칭에서 필드별 최고 점수 추출
            for chunk_key, chunk_info in chunk_details.items():
                if "growth_background" in chunk_key:
                    field_similarities["growthBackground"] = max(field_similarities["growthBackground"], chunk_info["score"])
                elif "motivation" in chunk_key:
                    field_similarities["motivation"] = max(field_similarities["motivation"], chunk_info["score"])
                elif "career_history" in chunk_key:
                    field_similarities["careerHistory"] = max(field_similarities["careerHistory"], chunk_info["score"])
            
            similarity_result = {
                "resume_id": similar["resume"]["_id"],
                "applicant_name": similar["resume"].get("name", "알 수 없음"),
                "position": similar["resume"].get("position", ""),
                "department": similar["resume"].get("department", ""),
                "overall_similarity": round(similar["similarity_score"], 4),
                "field_similarities": {
                    "growthBackground": round(field_similarities["growthBackground"], 4),
                    "motivation": round(field_similarities["motivation"], 4),
                    "careerHistory": round(field_similarities["careerHistory"], 4)
                },
                "chunk_matches": similar.get("chunk_matches", 0),
                "chunk_details": chunk_details,
                "is_high_similarity": similar["similarity_score"] > 0.7,
                "is_moderate_similarity": 0.4 <= similar["similarity_score"] <= 0.7,
                "is_low_similarity": similar["similarity_score"] < 0.4,
                "llm_analysis": similar.get("llm_analysis")
            }
            similarity_results.append(similarity_result)
        
        # 다른 모든 이력서 조회 (현재 이력서 제외)
        other_resumes = await db.applicants.find({"_id": {"$ne": ObjectId(resume_id)}}).to_list(1000)
        
        # 현재 이력서의 비교 텍스트 (유사도 계산 필드)
        current_fields = {
            "growthBackground": current_resume.get("growthBackground", ""),
            "motivation": current_resume.get("motivation", ""),
            "careerHistory": current_resume.get("careerHistory", "")
        }
        
        # 전체 텍스트 조합
        current_text = " ".join([text for text in current_fields.values() if text])
        
        similarity_results = []
        
        for other_resume in other_resumes:
            other_id = str(other_resume["_id"])
            
            # 다른 이력서의 비교 텍스트
            other_fields = {
                "growthBackground": other_resume.get("growthBackground", ""),
                "motivation": other_resume.get("motivation", ""), 
                "careerHistory": other_resume.get("careerHistory", "")
            }
            other_text = " ".join([text for text in other_fields.values() if text])
            
            # 실제 유사도 계산 사용
            try:
                print(f"💫 이력서 간 유사도 계산 시작: {resume_id} vs {other_id}")
                
                # SimilarityService의 텍스트 유사도 계산 메서드 직접 호출
                text_similarity = similarity_service._calculate_text_similarity(current_resume, other_resume)
                overall_similarity = text_similarity if text_similarity is not None else 0.0
                
                print(f"📊 텍스트 유사도 결과: {overall_similarity:.3f}")
                
                # 필드별 유사도 계산
                field_similarities = {}
                for field_name in current_fields.keys():
                    if current_fields[field_name] and other_fields[field_name]:
                        # 필드별 개별 텍스트 유사도 계산
                        field_sim = similarity_service._calculate_text_similarity(
                            {field_name: current_fields[field_name]},
                            {field_name: other_fields[field_name]}
                        )
                        field_similarities[field_name] = field_sim if field_sim is not None else 0.0
                        print(f"📋 {field_name} 유사도: {field_similarities[field_name]:.3f}")
                    else:
                        field_similarities[field_name] = 0.0
                        
            except Exception as e:
                print(f"[ERROR] 유사도 계산 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                
                # 오류 시 기본값 사용
                import random
                overall_similarity = random.uniform(0.1, 0.9)
                field_similarities = {}
                for field_name in current_fields.keys():
                    if current_fields[field_name] and other_fields[field_name]:
                        field_similarities[field_name] = random.uniform(0.0, 1.0)
                    else:
                        field_similarities[field_name] = 0.0
            
            # LLM 분석 추가 (유사도가 일정 수준 이상일 때만)
            llm_analysis = None
            
            if overall_similarity >= 0.3:  # 30% 이상 유사할 때만 LLM 분석
                try:
                    print(f"[API] LLM 분석 시작 - 유사도: {overall_similarity:.3f}")
                    llm_analysis = await similarity_service.llm_service.analyze_similarity_reasoning(
                        original_resume=current_resume,
                        similar_resume=other_resume,
                        similarity_score=overall_similarity
                    )
                    print(f"[API] LLM 분석 완료")
                except Exception as llm_error:
                    print(f"[API] LLM 분석 중 오류: {llm_error}")
                    llm_analysis = {
                        "success": False,
                        "error": str(llm_error),
                        "analysis": "LLM 분석에 실패했습니다."
                    }
            
            similarity_result = {
                "resume_id": other_id,
                "applicant_name": other_resume.get("name", "알 수 없음"),
                "position": other_resume.get("position", ""),
                "department": other_resume.get("department", ""),
                "overall_similarity": round(overall_similarity, 4),
                "field_similarities": {
                    "growthBackground": round(field_similarities["growthBackground"], 4),
                    "motivation": round(field_similarities["motivation"], 4),
                    "careerHistory": round(field_similarities["careerHistory"], 4)
                },
                "is_high_similarity": overall_similarity > 0.7,
                "is_moderate_similarity": 0.4 <= overall_similarity <= 0.7,
                "is_low_similarity": overall_similarity < 0.4,
                "llm_analysis": llm_analysis
            }
            
            similarity_results.append(similarity_result)
        
        # 유사도 높은 순으로 정렬
        similarity_results.sort(key=lambda x: x["overall_similarity"], reverse=True)
        
        # 전체 표절 위험도 분석 추가
        plagiarism_analysis = None
        high_similarity_results = [r for r in similarity_results if r["overall_similarity"] >= 0.3]
        
        if high_similarity_results:
            try:
                print(f"[API] 표절 위험도 분석 시작")
                plagiarism_analysis = await similarity_service.llm_service.analyze_plagiarism_risk(
                    original_resume=current_resume,
                    similar_resumes=high_similarity_results
                )
                print(f"[API] 표절 위험도 분석 완료")
            except Exception as plag_error:
                print(f"[API] 표절 위험도 분석 중 오류: {plag_error}")
                plagiarism_analysis = {
                    "success": False,
                    "error": str(plag_error),
                    "risk_level": "UNKNOWN",
                    "analysis": "표절 위험도 분석에 실패했습니다."
                }
        
        # 통계 정보
        high_similarity_count = len([r for r in similarity_results if r["is_high_similarity"]])
        moderate_similarity_count = len([r for r in similarity_results if r["is_moderate_similarity"]])
        low_similarity_count = len([r for r in similarity_results if r["is_low_similarity"]])
        
        return {
            "current_resume": {
                "id": resume_id,
                "name": current_resume.get("name", ""),
                "position": current_resume.get("position", ""),
                "department": current_resume.get("department", "")
            },
            "similarity_results": similarity_results,
            "statistics": {
                "total_compared": len(similarity_results),
                "high_similarity_count": high_similarity_count,
                "moderate_similarity_count": moderate_similarity_count,
                "low_similarity_count": low_similarity_count,
                "average_similarity": round(sum([r["overall_similarity"] for r in similarity_results]) / len(similarity_results) if similarity_results else 0, 4)
            },
            "top_similar": similarity_results[:5] if similarity_results else [],
            "plagiarism_analysis": plagiarism_analysis,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사도 체크 실패: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)