from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from datetime import datetime
import uuid

# .env 파일 로드
load_dotenv()

router = APIRouter(tags=["applicants"])

# MongoDB 연결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
client = AsyncIOMotorClient(MONGODB_URI)
db = client.hireme

# 지원자 모델
class Applicant(BaseModel):
    id: str
    name: str
    position: str
    department: str
    experience: int
    skills: List[str]
    ai_score: float
    ai_analysis: str
    status: str = "신규"
    created_at: datetime
    updated_at: datetime

class ApplicantCreate(BaseModel):
    name: str
    position: str
    department: str
    experience: int
    skills: List[str]
    ai_score: float
    ai_analysis: str

class ApplicantUpdate(BaseModel):
    status: str

@router.get("/")
async def get_all_applicants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    position: Optional[str] = Query(None)
):
    """모든 지원자 조회 (페이지네이션 지원)"""
    try:
        print(f"🔍 지원자 조회 요청: skip={skip}, limit={limit}, status={status}, position={position}")
        
        # 필터 조건 구성
        filter_query = {}
        if status:
            filter_query["status"] = status
        if position:
            filter_query["position"] = {"$regex": position, "$options": "i"}
        
        print(f"🔍 필터 쿼리: {filter_query}")
        
        # 지원자 데이터 조회
        cursor = db.resumes.find(filter_query).skip(skip).limit(limit)
        applicants = await cursor.to_list(length=limit)
        
        print(f"🔍 조회된 원본 데이터 수: {len(applicants)}")
        
        # 총 문서 수 조회
        total_count = await db.resumes.count_documents(filter_query)
        print(f"🔍 총 문서 수: {total_count}")
        
        # 응답 데이터 구성
        applicants_data = []
        for applicant in applicants:
            print(f"🔍 처리 중인 지원자: {applicant.get('name', 'N/A')}")
            
            # MongoDB ObjectId를 문자열로 변환
            applicant["id"] = str(applicant["_id"])
            del applicant["_id"]
            
            # 기본값 설정
            if "status" not in applicant:
                applicant["status"] = "신규"
            if "created_at" not in applicant:
                applicant["created_at"] = datetime.now()
            if "updated_at" not in applicant:
                applicant["updated_at"] = datetime.now()
            
            applicants_data.append(applicant)
        
        print(f"🔍 최종 응답 데이터 수: {len(applicants_data)}")
        
        return {
            "applicants": applicants_data,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"지원자 데이터 조회 실패: {str(e)}")

@router.post("/")
async def create_applicant(applicant: ApplicantCreate):
    """새 지원자 생성"""
    try:
        # 고유 ID 생성
        applicant_id = str(uuid.uuid4())
        
        # 현재 시간
        now = datetime.now()
        
        # 지원자 데이터 구성
        applicant_data = {
            "id": applicant_id,
            "name": applicant.name,
            "position": applicant.position,
            "department": applicant.department,
            "experience": applicant.experience,
            "skills": applicant.skills,
            "ai_score": applicant.ai_score,
            "ai_analysis": applicant.ai_analysis,
            "status": "신규",
            "created_at": now,
            "updated_at": now
        }
        
        # MongoDB에 저장
        result = await db.resumes.insert_one(applicant_data)
        
        # 저장된 데이터 반환
        applicant_data["_id"] = result.inserted_id
        
        return {
            "message": "지원자가 성공적으로 생성되었습니다.",
            "applicant": applicant_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 생성 실패: {str(e)}")

@router.put("/{applicant_id}/status")
async def update_applicant_status(applicant_id: str, update_data: ApplicantUpdate):
    """지원자 상태 업데이트"""
    try:
        # 지원자 존재 확인
        existing_applicant = await db.resumes.find_one({"id": applicant_id})
        if not existing_applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")
        
        # 상태 업데이트
        result = await db.resumes.update_one(
            {"id": applicant_id},
            {
                "$set": {
                    "status": update_data.status,
                    "updated_at": datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="상태 업데이트에 실패했습니다.")
        
        return {"message": "지원자 상태가 성공적으로 업데이트되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 업데이트 실패: {str(e)}")

@router.get("/stats/overview")
async def get_applicant_stats():
    """지원자 통계 조회"""
    try:
        # 전체 지원자 수
        total_applicants = await db.resumes.count_documents({})
        
        # 상태별 지원자 수
        status_stats = await db.resumes.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        # 직무별 지원자 수
        position_stats = await db.resumes.aggregate([
            {"$group": {"_id": "$position", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        # 평균 AI 점수
        avg_score_result = await db.resumes.aggregate([
            {"$group": {"_id": None, "avg_score": {"$avg": "$ai_score"}}}
        ]).to_list(length=1)
        
        avg_score = avg_score_result[0]["avg_score"] if avg_score_result and avg_score_result[0]["avg_score"] is not None else 0
        
        return {
            "total_applicants": total_applicants,
            "status_distribution": {stat["_id"]: stat["count"] for stat in status_stats},
            "position_distribution": {stat["_id"]: stat["count"] for stat in position_stats},
            "average_ai_score": round(avg_score, 1) if avg_score is not None else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.get("/health")
async def applicants_health_check():
    """지원자 서비스 헬스 체크"""
    return {
        "status": "healthy",
        "mongodb_connected": bool(client),
        "database": "Hireme",
        "collection": "resumes"
    }
