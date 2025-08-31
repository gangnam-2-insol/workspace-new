from modules.core.services.mongo_service import MongoService
from bson import ObjectId
import datetime

def create_similar_chunk():
    mongo = MongoService()

    # 김개발 지원자 데이터 조회
    applicant = mongo.sync_db.applicants.find_one({'_id': ObjectId('68ad8560eca9366a442c7b52')})
    print(f'원본 지원자: {applicant["name"]}')

    # 원본 자기소개서 조회
    cover_letter = mongo.sync_db.cover_letters.find_one({'_id': ObjectId(applicant['cover_letter_id'])})
    original_text = cover_letter['extracted_text']
    print(f'원본 자기소개서 길이: {len(original_text)}자')

    # 유사한 내용의 새로운 자기소개서 생성 (일부 내용을 수정)
    similar_text = """
지원동기
안녕하세요. 프론트엔드 개발자 김개발입니다. 귀사의 혁신적인 웹 서비스와 사용자 중심의 개발 문화에 매료되어 지원하게 되었습니다.

성장배경
컴퓨터공학을 전공하며 웹 개발에 대한 깊은 관심을 키워왔습니다. 대학 시절부터 다양한 프로젝트를 통해 실무 경험을 쌓았고, 특히 사용자 경험을 중시하는 프론트엔드 개발에 매료되어 이분야로 진로를 정했습니다.

경력사항
2022년부터 ABC 스타트업에서 프론트엔드 개발자로 근무하며 React 기반의 웹 애플리케이션을 개발했습니다. 사용자 인터페이스 개선과 성능 최적화에 중점을 두어 작업했으며, 팀 내 기술 공유 세션을 주도했습니다.

기술역량
React, TypeScript, Next.js, Tailwind CSS 등 모던 웹 기술에 대한 깊은 이해를 바탕으로 사용자 친화적인 웹 애플리케이션을 개발할 수 있습니다. 특히 성능 최적화와 접근성 개선에 대한 경험이 풍부합니다.

입사 후 포부
귀사에서 모던 웹 기술을 활용한 혁신적인 프로젝트에 참여하고 싶습니다. 사용자 경험을 최우선으로 하는 개발 문화에서 더욱 성장하여, 사용자들에게 가치 있는 서비스를 제공하는 개발자가 되고 싶습니다.
    """

    # 새로운 자기소개서 문서 생성
    new_cover_letter_doc = {
        'applicant_id': str(applicant['_id']),
        'extracted_text': similar_text,
        'summary': '프론트엔드 개발에 대한 열정과 경험을 바탕으로 사용자 중심의 웹 서비스 개발에 기여하고 싶어 지원했습니다.',
        'keywords': ['프론트엔드', 'React', '사용자경험', '웹개발'],
        'document_type': 'cover_letter',
        'growthBackground': '컴퓨터공학을 전공하며 웹 개발에 대한 깊은 관심을 키워왔습니다.',
        'motivation': '귀사의 혁신적인 웹 서비스와 사용자 중심의 개발 문화에 매료되어 지원했습니다.',
        'careerHistory': '2022년부터 ABC 스타트업에서 프론트엔드 개발자로 근무했습니다.',
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now()
    }

    # 새로운 자기소개서 저장
    new_cover_letter_result = mongo.sync_db.cover_letters.insert_one(new_cover_letter_doc)
    new_cover_letter_id = str(new_cover_letter_result.inserted_id)
    print(f'유사한 자기소개서 생성 완료: {new_cover_letter_id}')

    # 유사한 청크 생성
    chunk_text = similar_text[:500]
    similar_chunk_doc = {
        'applicant_id': str(applicant['_id']),
        'document_id': new_cover_letter_id,
        'document_type': 'cover_letter',
        'chunk_index': 0,
        'content': chunk_text,
        'metadata': {
            'applicant_name': applicant['name'],
            'document_title': f"{applicant['name']}의 유사한 자기소개서"
        },
        'created_at': datetime.datetime.now()
    }

    # 유사한 청크 저장
    similar_chunk_result = mongo.sync_db.cover_letter_chunks.insert_one(similar_chunk_doc)
    print(f'유사한 청크 생성 완료: {similar_chunk_result.inserted_id}')

    # 확인
    chunks = list(mongo.sync_db.cover_letter_chunks.find())
    print(f'총 청크 수: {len(chunks)}개')

    return new_cover_letter_id

if __name__ == "__main__":
    create_similar_chunk()
