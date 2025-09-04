import sys
import os
from datetime import datetime
from bson import ObjectId

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.services.mongo_service import MongoService

def create_chunks_for_analysis():
    """생성된 지원자 데이터에 대한 청크 데이터 생성"""
    
    mongo_service = MongoService()
    
    try:
        print("🔍 청크 데이터 생성을 위한 지원자 데이터 조회 중...")
        
        # 모든 지원자 조회
        applicants = list(mongo_service.sync_db.applicants.find())
        print(f"📋 총 {len(applicants)}명의 지원자를 발견했습니다.")
        
        if not applicants:
            print("❌ 청크 데이터를 생성할 지원자가 없습니다.")
            return
        
        # 실제로 이력서와 자기소개서가 있는 지원자만 필터링
        valid_applicants = []
        for applicant in applicants:
            resume_id = applicant.get("resume_id")
            cover_letter_id = applicant.get("cover_letter_id")
            
            if resume_id or cover_letter_id:
                valid_applicants.append(applicant)
        
        print(f"📋 이력서 또는 자기소개서가 있는 지원자: {len(valid_applicants)}명")
        
        if not valid_applicants:
            print("❌ 청크 데이터를 생성할 수 있는 지원자가 없습니다.")
            return
        
        total_chunks_created = 0
        
        for applicant in valid_applicants:
            applicant_id = str(applicant["_id"])
            applicant_name = applicant.get("name", "Unknown")
            
            print(f"\n👤 {applicant_name} ({applicant_id}) - 청크 데이터 생성 중...")
            
            # 1. 이력서 청크 생성
            resume_id = applicant.get("resume_id")
            if resume_id:
                try:
                    resume = mongo_service.sync_db.resumes.find_one({"_id": ObjectId(resume_id)})
                    if resume and resume.get("extracted_text"):
                        chunks_created = create_resume_chunks(resume, applicant_id, applicant_name)
                        total_chunks_created += chunks_created
                        print(f"   ✅ 이력서 청크 {chunks_created}개 생성 완료")
                    else:
                        print(f"   ⚠️ 이력서 데이터가 없거나 내용이 비어있음")
                except Exception as e:
                    print(f"   ❌ 이력서 청크 생성 실패: {str(e)}")
            
            # 2. 자기소개서 청크 생성
            cover_letter_id = applicant.get("cover_letter_id")
            if cover_letter_id:
                try:
                    cover_letter = mongo_service.sync_db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
                    if cover_letter and cover_letter.get("extracted_text"):
                        chunks_created = create_cover_letter_chunks(cover_letter, applicant_id, applicant_name)
                        total_chunks_created += chunks_created
                        print(f"   ✅ 자기소개서 청크 {chunks_created}개 생성 완료")
                    else:
                        print(f"   ⚠️ 자기소개서 데이터가 없거나 내용이 비어있음")
                except Exception as e:
                    print(f"   ❌ 자기소개서 청크 생성 실패: {str(e)}")
        
        print(f"\n🎉 청크 데이터 생성 완료!")
        print(f"📊 총 생성된 청크 수: {total_chunks_created}개")
        
        return total_chunks_created
        
    except Exception as e:
        print(f"❌ 청크 데이터 생성 중 오류 발생: {str(e)}")
        return None

def create_resume_chunks(resume, applicant_id, applicant_name):
    """이력서 청크 생성"""
    mongo_service = MongoService()
    
    text = resume.get("extracted_text", "")
    if not text:
        return 0
    
    # 청크 설정
    chunk_size = 500
    chunk_overlap = 50
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        
        # 청크 문서 생성
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
                "total_chunks": len(text) // chunk_size + 1,
                "split_type": "fixed_size",
                "source": "resume_extraction"
            },
            "created_at": datetime.now()
        }
        
        # MongoDB에 청크 저장
        result = mongo_service.sync_db.resume_chunks.insert_one(chunk_doc)
        chunks.append(chunk_doc)
        chunk_index += 1
        
        start = end - chunk_overlap if chunk_overlap > 0 else end
        
        if start >= len(text):
            break
    
    return len(chunks)

def create_cover_letter_chunks(cover_letter, applicant_id, applicant_name):
    """자기소개서 청크 생성"""
    mongo_service = MongoService()
    
    text = cover_letter.get("extracted_text", "")
    if not text:
        return 0
    
    # 청크 설정
    chunk_size = 400
    chunk_overlap = 50
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        
        # 청크 문서 생성
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
                "total_chunks": len(text) // chunk_size + 1,
                "split_type": "fixed_size",
                "source": "cover_letter_extraction"
            },
            "created_at": datetime.now()
        }
        
        # MongoDB에 청크 저장
        result = mongo_service.sync_db.cover_letter_chunks.insert_one(chunk_doc)
        chunks.append(chunk_doc)
        chunk_index += 1
        
        start = end - chunk_overlap if chunk_overlap > 0 else end
        
        if start >= len(text):
            break
    
    return len(chunks)

if __name__ == "__main__":
    create_chunks_for_analysis()
