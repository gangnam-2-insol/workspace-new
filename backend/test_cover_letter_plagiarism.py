import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def test_cover_letter_plagiarism():
    """자소서 표절체크 테스트"""
    try:
        # MongoDB 연결
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme
        
        print("✅ MongoDB 연결 성공")
        
        # 지원자 조회
        applicants = await db.applicants.find({}).to_list(10)
        print(f"📋 지원자 수: {len(applicants)}")
        
        # 자소서가 있는 지원자 찾기
        applicants_with_cover_letters = []
        for applicant in applicants:
            if applicant.get("cover_letter_id"):
                applicants_with_cover_letters.append(applicant)
                print(f"  - {applicant.get('name', 'Unknown')}: {applicant.get('cover_letter_id')}")
        
        if not applicants_with_cover_letters:
            print("❌ 자소서가 있는 지원자가 없습니다.")
            return
        
        # 첫 번째 지원자의 자소서 표절체크 테스트
        test_applicant = applicants_with_cover_letters[0]
        applicant_id = str(test_applicant["_id"])
        cover_letter_id = test_applicant["cover_letter_id"]
        
        print(f"\n🧪 테스트 대상: {test_applicant.get('name', 'Unknown')} (ID: {applicant_id})")
        print(f"📝 자소서 ID: {cover_letter_id}")
        
        # 자소서 내용 확인
        cover_letter = await db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
        if cover_letter:
            content = cover_letter.get("content", "")
            extracted_text = cover_letter.get("extracted_text", "")
            print(f"📄 자소서 내용 길이: {len(content)}자")
            print(f"📄 추출된 텍스트 길이: {len(extracted_text)}자")
            print(f"📄 내용 미리보기: {content[:100]}...")
        else:
            print("❌ 자소서를 찾을 수 없습니다.")
            return
        
        # 자소서 표절체크 API 호출 시뮬레이션
        print(f"\n🔍 자소서 표절체크 시작...")
        
        # SimilarityService 초기화
        from modules.core.services.embedding_service import EmbeddingService
        from modules.core.services.vector_service import VectorService
        from modules.core.services.similarity_service import SimilarityService
        
        embedding_service = EmbeddingService()
        vector_service = VectorService(
            api_key=os.getenv("PINECONE_API_KEY", "dummy-key"),
            index_name=os.getenv("PINECONE_INDEX_NAME", "resume-vectors")
        )
        similarity_service = SimilarityService(embedding_service, vector_service)
        
        # 청킹 테스트
        from modules.core.services.chunking_service import ChunkingService
        chunking_service = ChunkingService()
        
        # 자소서 데이터에 extracted_text 필드가 없으면 content를 사용
        if not cover_letter.get("extracted_text"):
            cover_letter["extracted_text"] = content
        
        # 자소서 청킹
        chunks = chunking_service.chunk_cover_letter(cover_letter)
        print(f"📦 생성된 청크 수: {len(chunks)}")
        
        for i, chunk in enumerate(chunks[:3]):  # 처음 3개만 출력
            print(f"  청크 {i+1}: {chunk['chunk_type']} - {len(chunk['text'])}자")
            print(f"    내용: {chunk['text'][:50]}...")
        
        if chunks:
            print("✅ 자소서 청킹 성공!")
        else:
            print("❌ 자소서 청킹 실패 - 청크가 생성되지 않았습니다.")
        
        client.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cover_letter_plagiarism())
