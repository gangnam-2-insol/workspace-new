import asyncio
import json
import sys
from pathlib import Path

# 백엔드 경로 추가
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

async def test_talent_recommendation():
    """유사인재 추천 기능 테스트"""
    try:
        print("=== 유사인재 추천 기능 테스트 시작 ===")
        
        # 1. 유사도 서비스 임포트 테스트
        try:
            from backend.modules.core.services.embedding_service import EmbeddingService
            from backend.modules.core.services.vector_service import VectorService
            from backend.modules.core.services.llm_service import LLMService
            from backend.modules.core.services.similarity_service import SimilarityService
            print("[OK] 서비스 모듈 임포트 성공")
        except ImportError as e:
            print(f"[FAIL] 서비스 모듈 임포트 실패: {e}")
            return False
        
        # 2. 서비스 초기화 테스트
        try:
            embedding_service = EmbeddingService()
            vector_service = VectorService()
            llm_service = LLMService()
            similarity_service = SimilarityService(
                embedding_service=embedding_service,
                vector_service=vector_service,
                llm_service=llm_service
            )
            print("[OK] 서비스 초기화 성공")
        except Exception as e:
            print(f"[FAIL] 서비스 초기화 실패: {e}")
            return False
        
        # 3. API 라우터 테스트
        try:
            from backend.modules.api.routers.similarity_router import router
            print("[OK] API 라우터 로드 성공")
            
            # 엔드포인트 확인
            routes = [route.path for route in router.routes]
            expected_routes = ['/similarity/search-similar', '/similarity/check-plagiarism/{document_id}']
            
            for route in expected_routes:
                if any(route in r for r in routes):
                    print(f"[OK] 엔드포인트 확인: {route}")
                else:
                    print(f"[WARN] 엔드포인트 누락: {route}")
                    
        except Exception as e:
            print(f"[FAIL] API 라우터 테스트 실패: {e}")
            return False
        
        # 4. 프론트엔드 UI 파일 존재 확인
        frontend_files = [
            "frontend/src/pages/TalentRecommendation/TalentRecommendation.js",
            "frontend/src/pages/CoverLetterValidation/CoverLetterValidation.js"
        ]
        
        for file_path in frontend_files:
            full_path = Path(__file__).parent / file_path
            if full_path.exists():
                print(f"[OK] 프론트엔드 파일 존재: {file_path}")
            else:
                print(f"[WARN] 프론트엔드 파일 누락: {file_path}")
        
        # 5. 테스트 파일 존재 확인
        test_file = Path(__file__).parent / "backend/modules/tests/test_similarity_service.py"
        if test_file.exists():
            print("[OK] 유닛 테스트 파일 존재")
        else:
            print("[WARN] 유닛 테스트 파일 누락")
        
        print("=== 유사인재 추천 기능 테스트 완료 ===")
        return True
        
    except Exception as e:
        print(f"[ERROR] 테스트 실행 중 오류: {e}")
        return False

async def test_plagiarism_detection():
    """표절 의심도 기능 테스트"""
    try:
        print("=== 자소서 표절의심도 기능 테스트 시작 ===")
        
        # 1. LLM 서비스 표절 분석 메서드 확인
        try:
            from backend.modules.core.services.llm_service import LLMService
            llm_service = LLMService()
            
            # 메서드 존재 확인
            if hasattr(llm_service, 'analyze_plagiarism_suspicion'):
                print("[OK] 표절 분석 메서드 존재")
            else:
                print("[FAIL] 표절 분석 메서드 누락")
                return False
                
        except Exception as e:
            print(f"[FAIL] LLM 서비스 로드 실패: {e}")
            return False
        
        # 2. 표절 검사 API 엔드포인트 확인
        try:
            from backend.modules.api.routers.similarity_router import router
            routes = [route.path for route in router.routes]
            
            if any('/similarity/check-plagiarism/' in route for route in routes):
                print("[OK] 표절 검사 API 엔드포인트 존재")
            else:
                print("[FAIL] 표절 검사 API 엔드포인트 누락")
                return False
                
        except Exception as e:
            print(f"[FAIL] API 엔드포인트 확인 실패: {e}")
            return False
        
        # 3. 프론트엔드 표절 검증 UI 확인
        ui_file = Path(__file__).parent / "frontend/src/pages/CoverLetterValidation/CoverLetterValidation.js"
        if ui_file.exists():
            # 파일 내용에서 표절 관련 기능 확인
            content = ui_file.read_text(encoding='utf-8')
            if 'plagiarism' in content.lower() or '표절' in content:
                print("[OK] 프론트엔드 표절 검증 UI 존재")
            else:
                print("[WARN] 프론트엔드에 표절 관련 UI 부분적으로만 구현")
        else:
            print("[FAIL] 프론트엔드 표절 검증 UI 파일 누락")
            return False
        
        # 4. 모델 정의 확인
        try:
            from backend.modules.core.models.similarity_models import PlagiarismAnalysis
            print("[OK] 표절 분석 모델 정의 존재")
        except ImportError:
            print("[FAIL] 표절 분석 모델 정의 누락")
            return False
        
        print("=== 자소서 표절의심도 기능 테스트 완료 ===")
        return True
        
    except Exception as e:
        print(f"[ERROR] 표절 검사 테스트 실행 중 오류: {e}")
        return False

async def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("유사인재 추천 및 자소서 표절의심도 기능 통합 테스트")
    print("=" * 60)
    
    # 1. 유사인재 추천 테스트
    talent_result = await test_talent_recommendation()
    
    print("\n" + "-" * 60 + "\n")
    
    # 2. 표절 의심도 테스트  
    plagiarism_result = await test_plagiarism_detection()
    
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print(f"유사인재 추천 기능: {'통과' if talent_result else '실패'}")
    print(f"자소서 표절의심도 기능: {'통과' if plagiarism_result else '실패'}")
    
    overall_success = talent_result and plagiarism_result
    print(f"전체 테스트: {'성공' if overall_success else '부분 성공'}")
    
    return {
        'talent_recommendation': talent_result,
        'plagiarism_detection': plagiarism_result,
        'overall': overall_success
    }

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n최종 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")