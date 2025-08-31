"""
PICK-TALK 전용 직접 채용공고 등록 API
AI 제목 추천 단계를 건너뛰고 바로 등록하는 API
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from modules.core.services.mongo_service import MongoService
from modules.job_posting.models import JobStatus
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# MongoDB 서비스 의존성
def get_mongo_service():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    return MongoService(mongo_uri)

router = APIRouter(prefix="/pick-chatbot", tags=["PICK-TALK Direct Registration"])

from typing import Any

# 완전히 유연한 모델 - 모든 필드를 Any로 받음
from pydantic import BaseModel, Field


class FlexibleJobPostingRequest(BaseModel):
    """완전히 유연한 채용공고 요청 모델"""
    class Config:
        extra = "allow"

class DirectJobPostingResponse(BaseModel):
    """직접 등록 응답"""
    success: bool
    message: str
    job_posting_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

@router.post("/direct-register")
async def direct_register_job_posting(
    request: Dict[str, Any],  # 완전히 유연한 데이터 구조
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """
    PICK-TALK 전용 직접 채용공고 등록
    AI 제목 추천 단계를 건너뛰고 바로 등록
    """
    try:
        # 요청 데이터 추출
        request_data = request

        print("\n🚀 [PICK-TALK 직접 등록] API 호출 시작")
        print(f"📝 제목: {request_data.get('title', 'N/A')}")
        print(f"🏢 회사: {request_data.get('company_name') or request_data.get('company', 'N/A')}")
        print(f"💼 직무: {request_data.get('position', 'N/A')}")
        print(f"📍 위치: {request_data.get('location', 'N/A')}")

        # 🔍 디버깅: 전체 요청 데이터 출력
        print(f"🔍 [디버깅] 전체 요청 데이터:")
        for key, value in request_data.items():
            print(f"    {key}: {value}")

        # 채용공고 데이터 준비 및 변환
        job_data = request_data.copy()

        print(f"🔍 [디버깅] 변환 전 데이터:")
        for key, value in job_data.items():
            print(f"    {key}: {value}")

        # PICK-TALK 데이터를 기존 DB 스키마에 맞게 변환
        if job_data.get('company_name') and not job_data.get('company'):
            job_data['company'] = job_data['company_name']

        if job_data.get('description') and not job_data.get('main_duties'):
            job_data['main_duties'] = job_data['description']

        if job_data.get('application_deadline') and not job_data.get('deadline'):
            job_data['deadline'] = job_data['application_deadline']

        if job_data.get('employment_type') and not job_data.get('work_type'):
            job_data['work_type'] = job_data['employment_type']

        # contact_info에서 이메일과 전화번호 추출
        if job_data.get('contact_info'):
            contact_info = job_data['contact_info']
            if not job_data.get('contact_email') and contact_info.get('email'):
                job_data['contact_email'] = contact_info['email']
            if not job_data.get('contact_phone') and contact_info.get('phone'):
                job_data['contact_phone'] = contact_info['phone']

        # 기본값 설정
        if not job_data.get('company'):
            job_data['company'] = job_data.get('company_name', '성장기업')
        if not job_data.get('main_duties'):
            job_data['main_duties'] = job_data.get('description', '개발 업무')
        if not job_data.get('work_type'):
            job_data['work_type'] = job_data.get('employment_type', 'fulltime')

        # 메타데이터 추가
        now = datetime.now()
        job_data.update({
            "created_at": now,
            "updated_at": now,
            "status": JobStatus.PUBLISHED,  # PICK-TALK에서는 바로 published 상태로 등록
            "applicants": 0,
            "views": 0,
            "bookmarks": 0,
            "shares": 0,
            "source": "pick_talk",  # 등록 소스 표시
            "ai_generated": True    # AI 생성 여부 표시
        })

        print("📊 [데이터 준비] 완료")
        print(f"    📝 상태: {job_data['status']}")
        print(f"    🕐 생성일: {job_data['created_at']}")
        print(f"    🤖 AI 생성: {job_data['ai_generated']}")

        # MongoDB에 저장
        db = mongo_service.db
        result = await db.job_postings.insert_one(job_data)

        if result.inserted_id:
            job_id = str(result.inserted_id)
            print(f"✅ [등록 완료] 채용공고 ID: {job_id}")

            return {
                "success": True,
                "message": "채용공고가 성공적으로 등록되었습니다!",
                "job_posting_id": job_id,
                "data": {
                    "title": job_data.get('title', 'N/A'),
                    "company": job_data.get('company', job_data.get('company_name', 'N/A')),
                    "position": job_data.get('position', 'N/A'),
                    "location": job_data.get('location', 'N/A'),
                    "status": JobStatus.PUBLISHED,
                    "created_at": now.isoformat()
                }
            }
        else:
            print("❌ [등록 실패] DB 삽입 결과 없음")
            return {
                "success": False,
                "message": "채용공고 등록에 실패했습니다."
            }

    except Exception as e:
        logger.error("PICK-TALK 직접 등록 실패: %s", str(e))
        print(f"💥 [등록 실패] 예외 발생: {str(e)}")
        print(f"🔍 [예외 타입]: {type(e).__name__}")
        import traceback
        print(f"🔍 [스택 트레이스]: {traceback.format_exc()}")

        return {
            "success": False,
            "message": f"채용공고 등록 중 오류가 발생했습니다: {str(e)}"
        }

@router.post("/debug")
async def debug_request(request: Dict[str, Any]):
    """디버깅용 API - 전달되는 데이터 확인"""
    print(f"🔍 [DEBUG API] 요청 받음")
    print(f"    데이터 타입: {type(request)}")
    print(f"    데이터 내용: {request}")

    return {
        "status": "debug_success",
        "received_data": request,
        "data_type": str(type(request)),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """PICK-TALK 직접 등록 API 상태 확인"""
    return {
        "status": "healthy",
        "service": "PICK-TALK Direct Registration",
        "timestamp": datetime.now().isoformat()
    }
