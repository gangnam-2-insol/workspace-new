import sys
import os
from datetime import datetime
from bson import ObjectId

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.services.mongo_service import MongoService

def create_chunks_quick():
    """이미 생성된 5명의 지원자 데이터에 대해서만 빠르게 청크 생성"""
    
    mongo_service = MongoService()
    
    # 생성된 5명의 지원자 ID (이전에 생성된 데이터)
    target_applicant_ids = [
        "68ad8560eca9366a442c7b52",  # 김개발
        "68ad8560eca9366a442c7b56",  # 이백엔드
        "68ad8560eca9366a442c7b5a",  # 박풀스택
        "68ad8560eca9366a442c7b5e",  # 최데이터
        "68ad8560eca9366a442c7b62"   # 정AI
    ]
    
    try:
        print("🚀 빠른 청크 데이터 생성 시작...")
        
        total_chunks_created = 0
        
        for applicant_id in target_applicant_ids:
            try:
                # 지원자 정보 조회
                applicant = mongo_service.sync_db.applicants.find_one({"_id": ObjectId(applicant_id)})
                if not applicant:
                    print(f"⚠️ 지원자를 찾을 수 없음: {applicant_id}")
                    continue
                
                applicant_name = applicant.get("name", "Unknown")
                print(f"\n👤 {applicant_name} - 청크 생성 중...")
                
                # 이력서 청크 생성
                resume_id = applicant.get("resume_id")
                if resume_id:
                    resume = mongo_service.sync_db.resumes.find_one({"_id": ObjectId(resume_id)})
                    if resume and resume.get("extracted_text"):
                        chunks = create_resume_chunks_fast(resume, applicant_id, applicant_name)
                        total_chunks_created += chunks
                        print(f"   ✅ 이력서 청크 {chunks}개 생성")
                
                # 자기소개서 청크 생성
                cover_letter_id = applicant.get("cover_letter_id")
                if cover_letter_id:
                    cover_letter = mongo_service.sync_db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
                    if cover_letter and cover_letter.get("extracted_text"):
                        chunks = create_cover_letter_chunks_fast(cover_letter, applicant_id, applicant_name)
                        total_chunks_created += chunks
                        print(f"   ✅ 자기소개서 청크 {chunks}개 생성")
                
            except Exception as e:
                print(f"❌ {applicant_id} 처리 중 오류: {str(e)}")
        
        print(f"\n🎉 빠른 청크 생성 완료!")
        print(f"📊 총 생성된 청크 수: {total_chunks_created}개")
        
        return total_chunks_created
        
    except Exception as e:
        print(f"❌ 청크 생성 중 오류: {str(e)}")
        return None

def create_resume_chunks_fast(resume, applicant_id, applicant_name):
    """이력서 청크 빠른 생성"""
    text = resume.get("extracted_text", "")
    if not text:
        return 0
    
    # 간단한 청크 설정
    chunk_size = 500
    chunk_overlap = 50
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        
        chunk_doc = {
            "applicant_id": applicant_id,
            "document_id": str(resume["_id"]),
            "document_type": "resume",
            "chunk_index": chunk_index,
            "content": chunk_text,
            "metadata": {
                "applicant_name": applicant_name,
                "document_title": f"{applicant_name}의 이력서",
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "split_type": "fixed_size",
                "source": "resume_extraction"
            },
            "created_at": datetime.now()
        }
        
        # MongoDB에 저장
        mongo_service = MongoService()
        mongo_service.sync_db.resume_chunks.insert_one(chunk_doc)
        chunks.append(chunk_doc)
        chunk_index += 1
        
        start = end - chunk_overlap if chunk_overlap > 0 else end
        if start >= len(text):
            break
    
    return len(chunks)

def create_cover_letter_chunks_fast(cover_letter, applicant_id, applicant_name):
    """자기소개서 청크 빠른 생성"""
    text = cover_letter.get("extracted_text", "")
    if not text:
        return 0
    
    # 간단한 청크 설정
    chunk_size = 400
    chunk_overlap = 50
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        
        chunk_doc = {
            "applicant_id": applicant_id,
            "document_id": str(cover_letter["_id"]),
            "document_type": "cover_letter",
            "chunk_index": chunk_index,
            "content": chunk_text,
            "metadata": {
                "applicant_name": applicant_name,
                "document_title": f"{applicant_name}의 자기소개서",
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "split_type": "fixed_size",
                "source": "cover_letter_extraction"
            },
            "created_at": datetime.now()
        }
        
        # MongoDB에 저장
        mongo_service = MongoService()
        mongo_service.sync_db.cover_letter_chunks.insert_one(chunk_doc)
        chunks.append(chunk_doc)
        chunk_index += 1
        
        start = end - chunk_overlap if chunk_overlap > 0 else end
        if start >= len(text):
            break
    
    return len(chunks)

if __name__ == "__main__":
    create_chunks_quick()
