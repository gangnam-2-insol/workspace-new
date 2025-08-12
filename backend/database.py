from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB 연결 설정
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
# 기본 DB명을 'hireme'로 고정하여 프론트/샘플 데이터와 일치시킵니다.
DATABASE_NAME = os.getenv("DATABASE_NAME", "hireme")

# 연결 풀 설정
MONGODB_CONFIG = {
    "maxPoolSize": 50,
    "minPoolSize": 10,
    "maxIdleTimeMS": 30000,
    "serverSelectionTimeoutMS": 5000,
    "connectTimeoutMS": 10000,
    "socketTimeoutMS": 10000,
}

# 비동기 클라이언트 (FastAPI용)
async_client = AsyncIOMotorClient(MONGODB_URI, **MONGODB_CONFIG)
async_db = async_client[DATABASE_NAME]

# 동기 클라이언트 (일반 작업용)
sync_client = MongoClient(MONGODB_URI, **MONGODB_CONFIG)
sync_db = sync_client[DATABASE_NAME]

# 컬렉션 참조
applicants_collection = async_db.applicant
users_collection = async_db.users
interviews_collection = async_db.interviews
jobs_collection = async_db.jobs
# 샘플 스키마용 이력서 컬렉션 (CSV 사양)
resumes_collection = async_db.resumes

# 동기 컬렉션 참조
sync_applicants_collection = sync_db.applicant
sync_users_collection = sync_db.users
sync_interviews_collection = sync_db.interviews
sync_jobs_collection = sync_db.jobs
sync_resumes_collection = sync_db.resumes

def get_database():
    """데이터베이스 인스턴스 반환"""
    return async_db

def get_sync_database():
    """동기 데이터베이스 인스턴스 반환"""
    return sync_db

async def close_database():
    """데이터베이스 연결 종료"""
    async_client.close()
    sync_client.close()

# 연결 상태 확인
async def check_database_connection():
    """데이터베이스 연결 상태 확인"""
    try:
        await async_client.admin.command('ping')
        return True
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return False

