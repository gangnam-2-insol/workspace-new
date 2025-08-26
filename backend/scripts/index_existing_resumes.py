#!/usr/bin/env python3
"""
기존 이력서들을 Elasticsearch에 일괄 인덱싱하는 독립 스크립트

사용법:
    python index_existing_resumes.py

이 스크립트는 MongoDB에 있는 모든 이력서를 Elasticsearch에 인덱싱합니다.
유사인재 추천 기능에서 키워드 검색이 제대로 작동하도록 하기 위해 필요합니다.
"""

import os
import sys
import asyncio
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# 프로젝트 루트를 Python path에 추가
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

# 서비스들 import
from modules.core.services.similarity_service import SimilarityService
from modules.core.services.embedding_service import EmbeddingService
from modules.core.services.vector_service import VectorService
from modules.core.services.llm_service import LLMService

class ResumeIndexer:
    def __init__(self):
        """인덱서 초기화"""
        print("🚀 이력서 인덱서 초기화 중...")
        
        # MongoDB 연결
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        self.client = AsyncIOMotorClient(self.mongodb_uri)
        self.db = self.client.hireme
        
        # 서비스 초기화
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService(
            api_key=os.getenv("PINECONE_API_KEY", "dummy-key"),
            index_name=os.getenv("PINECONE_INDEX_NAME", "resume-vectors")
        )
        self.llm_service = LLMService()
        self.similarity_service = SimilarityService(
            self.embedding_service, 
            self.vector_service, 
            self.llm_service
        )
        
        print("✅ 서비스 초기화 완료")

    async def index_all_resumes(self):
        """모든 이력서를 ES에 인덱싱"""
        try:
            print("\n📋 기존 이력서 ES 인덱싱 시작...")
            start_time = datetime.now()
            
            # DB에서 모든 이력서 조회 (resumes 컬렉션에서)
            print("🔍 MongoDB resumes 컬렉션에서 이력서 조회 중...")
            all_resumes = await self.db.resumes.find().to_list(None)
            total_count = len(all_resumes)
            
            if total_count == 0:
                print("❌ 인덱싱할 이력서가 없습니다.")
                return {
                    "total_resumes": 0,
                    "indexed_count": 0,
                    "failed_count": 0,
                    "errors": []
                }
            
            print(f"📊 총 {total_count}개 이력서 발견")
            print("=" * 50)
            
            indexed_count = 0
            failed_count = 0
            errors = []
            
            for i, resume in enumerate(all_resumes, 1):
                try:
                    resume_id = str(resume["_id"])
                    name = resume.get("name", "Unknown")
                    
                    # 진행률 표시
                    progress = (i / total_count) * 100
                    print(f"[{i:3d}/{total_count}] ({progress:5.1f}%) 처리 중: {name}")
                    
                    # Elasticsearch에 이력서 인덱싱
                    es_result = await self.similarity_service.keyword_search_service.index_document(resume)
                    
                    if es_result["success"]:
                        indexed_count += 1
                        print(f"    ✅ 성공: {name}")
                    else:
                        failed_count += 1
                        error_msg = f"이력서 {name}({resume_id}) 인덱싱 실패: {es_result.get('message', 'Unknown error')}"
                        errors.append(error_msg)
                        print(f"    ❌ 실패: {error_msg}")
                        
                except Exception as resume_error:
                    failed_count += 1
                    error_msg = f"이력서 {resume.get('name', 'Unknown')}({str(resume.get('_id', ''))}) 처리 중 오류: {str(resume_error)}"
                    errors.append(error_msg)
                    print(f"    ⚠️  오류: {error_msg}")
            
            # 완료 보고서
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("=" * 50)
            print("📈 인덱싱 완료 보고서")
            print("=" * 50)
            print(f"🕐 소요 시간: {duration:.1f}초")
            print(f"📊 전체 이력서: {total_count:,}개")
            print(f"✅ 성공: {indexed_count:,}개")
            print(f"❌ 실패: {failed_count:,}개")
            
            if total_count > 0:
                success_rate = (indexed_count / total_count) * 100
                print(f"🎯 성공률: {success_rate:.1f}%")
            
            if errors and len(errors) > 0:
                print(f"\n⚠️  오류 목록 (최대 10개):")
                for error in errors[:10]:
                    print(f"   • {error}")
                if len(errors) > 10:
                    print(f"   ... 및 {len(errors) - 10}개 추가 오류")
            
            print("=" * 50)
            
            if indexed_count > 0:
                print("🎉 인덱싱이 완료되었습니다!")
                print("💡 이제 유사인재 추천에서 키워드 검색이 정상적으로 작동할 것입니다.")
            else:
                print("😞 인덱싱된 이력서가 없습니다. 오류를 확인해 주세요.")
            
            return {
                "total_resumes": total_count,
                "indexed_count": indexed_count,
                "failed_count": failed_count,
                "success_rate": round((indexed_count / total_count * 100) if total_count > 0 else 0, 2),
                "duration_seconds": duration,
                "errors": errors
            }
            
        except Exception as e:
            print(f"💥 인덱싱 중 치명적 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
        finally:
            # MongoDB 연결 종료
            self.client.close()
            print("\n🔌 MongoDB 연결 종료됨")

    async def check_elasticsearch_status(self):
        """Elasticsearch 연결 상태 확인"""
        try:
            print("🔍 Elasticsearch 연결 상태 확인 중...")
            stats = await self.similarity_service.keyword_search_service.get_index_stats()
            
            if stats.get("index_exists", False):
                doc_count = stats.get("document_count", 0)
                print(f"✅ ES 연결 성공 - 현재 인덱싱된 문서: {doc_count:,}개")
                return True
            else:
                print("⚠️  ES 인덱스가 존재하지 않음 - 새로 생성됩니다")
                return True
                
        except Exception as e:
            print(f"❌ Elasticsearch 연결 실패: {str(e)}")
            print("💡 ES가 실행 중인지 확인하고 설정을 점검해 주세요.")
            return False

async def main():
    """메인 함수"""
    print("🏁 이력서 ES 인덱싱 스크립트 시작")
    print("=" * 60)
    
    try:
        # 인덱서 생성
        indexer = ResumeIndexer()
        
        # ES 상태 확인
        es_ok = await indexer.check_elasticsearch_status()
        if not es_ok:
            print("\n❌ Elasticsearch 연결에 실패했습니다. 스크립트를 종료합니다.")
            return
        
        # 인덱싱 실행
        result = await indexer.index_all_resumes()
        
        # 최종 결과
        print(f"\n🏆 최종 결과: {result['indexed_count']:,}개 성공, {result['failed_count']:,}개 실패")
        
        if result['indexed_count'] > 0:
            print("🎯 인덱싱이 성공적으로 완료되었습니다!")
            sys.exit(0)
        else:
            print("⚠️  인덱싱된 문서가 없습니다.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류가 발생했습니다: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("📚 기존 이력서 Elasticsearch 인덱싱 도구")
    print("   유사인재 추천 키워드 검색 활성화를 위해 실행합니다")
    print("=" * 60)
    
    # Python 버전 확인
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 이상이 필요합니다.")
        sys.exit(1)
    
    # 환경변수 확인
    required_env_vars = ["MONGODB_URI"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  필요한 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("💡 .env 파일이나 시스템 환경변수를 확인해 주세요.")
    
    # 비동기 실행
    asyncio.run(main())