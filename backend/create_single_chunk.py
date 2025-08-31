from modules.core.services.mongo_service import MongoService
from bson import ObjectId
import datetime

def create_single_chunk():
    mongo = MongoService()

    # 김개발 지원자 데이터 조회
    applicant = mongo.sync_db.applicants.find_one({'_id': ObjectId('68ad8560eca9366a442c7b52')})
    print(f'지원자: {applicant["name"]}')

    # 자기소개서 조회
    cover_letter = mongo.sync_db.cover_letters.find_one({'_id': ObjectId(applicant['cover_letter_id'])})
    text = cover_letter['extracted_text']
    print(f'자기소개서 길이: {len(text)}자')

    # 청크 생성 (첫 500자만)
    chunk_text = text[:500]
    chunk_doc = {
        'applicant_id': str(applicant['_id']),
        'document_id': str(cover_letter['_id']),
        'document_type': 'cover_letter',
        'chunk_index': 0,
        'content': chunk_text,
        'metadata': {
            'applicant_name': applicant['name'],
            'document_title': f"{applicant['name']}의 자기소개서"
        },
        'created_at': datetime.datetime.now()
    }

    # 청크 저장
    result = mongo.sync_db.cover_letter_chunks.insert_one(chunk_doc)
    print(f'청크 생성 완료: {result.inserted_id}')

    # 확인
    chunks = list(mongo.sync_db.cover_letter_chunks.find())
    print(f'총 청크 수: {len(chunks)}개')

if __name__ == "__main__":
    create_single_chunk()
