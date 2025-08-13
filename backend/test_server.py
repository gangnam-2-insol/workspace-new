"""
간단한 테스트 서버 - API 엔드포인트 테스트용
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = FastAPI(title="테스트 서버", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB 연결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/Hireme")
client = AsyncIOMotorClient(MONGODB_URI)
db = client.Hireme

@app.get("/")
async def root():
    return {"message": "테스트 서버가 실행 중입니다!"}

@app.get("/api/applicants/")
async def get_applicants():
    """지원자 목록 조회"""
    try:
        # MongoDB에서 데이터 조회
        cursor = db.resumes.find({})
        applicants = await cursor.to_list(length=100)
        
        # 응답 데이터 구성
        applicants_data = []
        for applicant in applicants:
            applicant_data = {
                "id": str(applicant["_id"]),
                "position": applicant.get("position", "N/A"),
                "department": applicant.get("department", "N/A"),
                "experience": applicant.get("experience", "N/A"),
                "created_at": applicant.get("created_at", datetime.now())
            }
            applicants_data.append(applicant_data)
        
        return {
            "applicants": applicants_data,
            "total": len(applicants_data),
            "message": "지원자 데이터 조회 성공"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 데이터 조회 실패: {str(e)}")

@app.get("/api/upload/health")
async def upload_health():
    """업로드 서비스 헬스 체크"""
    return {"status": "healthy", "message": "업로드 서비스가 정상 작동 중입니다"}

@app.post("/api/upload/validate-uploaded-file")
async def validate_file_test():
    """파일 검증 테스트 (간단한 버전)"""
    return {
        "filename": "test.txt",
        "validation_result": {
            "is_valid": True,
            "reason": "테스트용 응답",
            "suggested_type": "자기소개서"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 테스트 서버를 시작합니다...")
    print("📊 MongoDB 연결 확인 중...")
    print(f"🔗 MongoDB URI: {MONGODB_URI}")
    uvicorn.run(app, host="0.0.0.0", port=8003)
