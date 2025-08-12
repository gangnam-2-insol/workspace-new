from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime
import time

# 라우터 임포트
from chatbot_router import router as chatbot_router
from routers.applicants import router as applicants_router
from routers.users import router as users_router
from routers.upload import router as upload_router
from routers.pdf_router import router as pdf_router

# 데이터베이스 및 모델 임포트
from database import get_database, close_database, check_database_connection

# FastAPI 앱 생성
app = FastAPI(
    title="HireMe API",
    description="HireMe 프로젝트 백엔드 API",
    version="1.0.0"
)

# 미들웨어 추가
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 추가
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["chatbot"])
app.include_router(applicants_router)
app.include_router(users_router)
app.include_router(upload_router)
app.include_router(pdf_router, prefix="/api")

# 기본 API 라우트들
@app.get("/")
async def root():
    return {"message": "HireMe API 서버가 실행 중입니다!"}

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    db_status = await check_database_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "timestamp": datetime.now(),
        "database": "connected" if db_status else "disconnected"
    }

# 에러 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "내부 서버 오류가 발생했습니다."}
    )

# 데이터베이스 연결 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    await close_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        workers=1,  # 단일 워커로 시작
        log_level="info"
    ) 