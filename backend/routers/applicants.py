import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from models.applicant import Applicant, ApplicantCreate
from modules.core.services.embedding_service import EmbeddingService
from modules.core.services.similarity_service import SimilarityService
from modules.core.services.vector_service import VectorService
from modules.core.services.mongo_service import MongoService

router = APIRouter(prefix="/api/applicants", tags=["applicants"])

# MongoDB 서비스 의존성
def get_mongo_service():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    return MongoService(mongo_uri)

# SimilarityService 의존성
def get_similarity_service():
    # 환경 변수에서 API 키 로드
    pinecone_api_key = os.getenv("PINECONE_API_KEY", "dummy-key")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "resume-vectors")

    embedding_service = EmbeddingService()
    vector_service = VectorService(
        api_key=pinecone_api_key,
        index_name=pinecone_index_name
    )
    return SimilarityService(embedding_service, vector_service)

@router.post("/", response_model=Applicant)
async def create_or_get_applicant(
    applicant_data: ApplicantCreate,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자를 생성하거나 기존 지원자를 조회합니다."""
    try:
        result = await mongo_service.create_or_get_applicant(applicant_data)
        # 응답 구조에서 applicant 부분만 반환
        return result["applicant"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 생성/조회 실패: {str(e)}")

@router.get("/{applicant_id}", response_model=Applicant)
async def get_applicant(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자를 조회합니다."""
    applicant = await mongo_service.get_applicant_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
    return applicant

@router.get("/")
async def get_all_applicants(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(50, ge=1, le=1000, description="가져올 개수"),
    status: Optional[str] = Query(None, description="상태 필터"),
    position: Optional[str] = Query(None, description="직무 필터"),
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """모든 지원자 목록을 조회합니다."""
    try:
        print(f"🔍 API 라우터 호출 - MongoDB URI: {mongo_service.mongo_uri}")
        print(f"🔍 API 라우터 호출 - skip: {skip}, limit: {limit}, status: {status}, position: {position}")

        result = await mongo_service.get_applicants(skip=skip, limit=limit, status=status, position=position)

        # 디버깅: 응답 데이터 확인
        if result.get('applicants') and len(result['applicants']) > 0:
            first_applicant = result['applicants'][0]
            print(f"🔍 API 응답 - 첫 번째 지원자 필드들: {list(first_applicant.keys())}")
            print(f"🔍 API 응답 - email 존재: {'email' in first_applicant}")
            print(f"🔍 API 응답 - phone 존재: {'phone' in first_applicant}")
            if 'email' in first_applicant:
                print(f"🔍 API 응답 - email 값: {first_applicant['email']}")
            if 'phone' in first_applicant:
                print(f"🔍 API 응답 - phone 값: {first_applicant['phone']}")

        # 응답 데이터 확인 (디버깅용)
        if result.get('applicants') and len(result['applicants']) > 0:
            first_applicant = result['applicants'][0]
            print(f"🔍 API 응답 - 첫 번째 지원자 필드들: {list(first_applicant.keys())}")
            print(f"🔍 API 응답 - email 존재: {'email' in first_applicant}, 값: {first_applicant.get('email', 'None')}")
            print(f"🔍 API 응답 - phone 존재: {'phone' in first_applicant}, 값: {first_applicant.get('phone', 'None')}")

        return result
    except Exception as e:
        print(f"❌ API 라우터 오류: {e}")
        raise HTTPException(status_code=500, detail=f"지원자 목록 조회 실패: {str(e)}")

@router.put("/{applicant_id}/status")
async def update_applicant_status(
    applicant_id: str,
    status_data: dict,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 상태를 업데이트합니다."""
    try:
        new_status = status_data.get("status")
        if not new_status:
            raise HTTPException(status_code=400, detail="상태 값이 필요합니다")

        result = await mongo_service.update_applicant_status(applicant_id, new_status)
        if not result:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")

        return {"message": "상태가 성공적으로 업데이트되었습니다", "status": new_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 업데이트 실패: {str(e)}")

@router.get("/stats/overview")
async def get_applicant_stats(
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 통계를 조회합니다."""
    try:
        stats = await mongo_service.get_applicant_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.post("/similar")
async def search_similar_applicants(
    search_criteria: Dict[str, Any],
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """유사한 지원자를 검색합니다."""
    try:
        print(f"[INFO] 유사 지원자 검색 요청 - 기준: {search_criteria}")

        # 검색 기준 추출
        position = search_criteria.get("position", "")
        skills = search_criteria.get("skills", "")
        experience = search_criteria.get("experience", "")
        department = search_criteria.get("department", "")

        # 유사도 서비스 초기화
        similarity_service = get_similarity_service()

        # 유사 지원자 검색 수행
        similar_applicants = await similarity_service.find_similar_applicants(
            position=position,
            skills=skills,
            experience=experience,
            department=department,
            limit=10
        )

        return {
            "status": "success",
            "applicants": similar_applicants,
            "search_criteria": search_criteria,
            "message": f"{len(similar_applicants)}명의 유사한 지원자를 발견했습니다."
        }

    except Exception as e:
        print(f"[ERROR] 유사 지원자 검색 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"유사 지원자 검색 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{applicant_id}/cover-letter")
async def get_applicant_cover_letter(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자의 자소서를 조회합니다."""
    try:
        print(f"[INFO] 자소서 조회 요청 - applicant_id: {applicant_id}")

        # 1. 지원자 존재 확인
        applicant = await mongo_service.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")

        # 2. 자소서 ID 확인
        cover_letter_id = applicant.get("cover_letter_id")
        if not cover_letter_id:
            # 자소서가 없는 경우 빈 응답 반환 (404 대신)
            return {
                "status": "success",
                "applicant_id": applicant_id,
                "cover_letter": None,
                "message": "자소서가 없습니다",
                "has_cover_letter": False
            }

        # 3. 자소서 조회
        from bson import ObjectId
        from motor.motor_asyncio import AsyncIOMotorClient

        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme

        # cover_letter_id 대신 applicant_id로 조회
        cover_letter = await db.cover_letters.find_one({"applicant_id": ObjectId(applicant_id)})
        client.close()

        if not cover_letter:
            # 자소서 ID는 있지만 실제 자소서가 없는 경우
            return {
                "status": "success",
                "applicant_id": applicant_id,
                "cover_letter": None,
                "message": "자소서를 찾을 수 없습니다",
                "has_cover_letter": False
            }

        # ObjectId를 문자열로 변환하여 JSON 직렬화 문제 해결
        def convert_objectids_to_strings(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, ObjectId):
                        obj[key] = str(value)
                    elif isinstance(value, dict):
                        convert_objectids_to_strings(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                convert_objectids_to_strings(item)
            return obj

        cover_letter = convert_objectids_to_strings(cover_letter)

        return {
            "status": "success",
            "applicant_id": applicant_id,
            "cover_letter": cover_letter,
            "message": "자소서 조회 완료",
            "has_cover_letter": True
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 자소서 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"자소서 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/{applicant_id}/recommendations")
async def get_talent_recommendations(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 기반 유사 인재 추천"""
    try:
        print(f"🚀 [유사인재 추천 API] === 요청 시작 ===")
        print(f"📋 [유사인재 추천 API] 요청 정보:")
        print(f"  - 지원자 ID: {applicant_id}")
        print(f"  - 요청 시간: {datetime.now().isoformat()}")
        print(f"  - MongoDB 서비스: {type(mongo_service).__name__}")

        # 1. 지원자 존재 확인
        print(f"🔍 [유사인재 추천 API] 1단계: 지원자 존재 확인")
        from bson import ObjectId
        applicant_collection = mongo_service.db.applicants
        print(f"  - 지원자 컬렉션: {applicant_collection.name}")
        
        target_applicant = await applicant_collection.find_one({"_id": ObjectId(applicant_id)})
        
        if not target_applicant:
            print(f"❌ [유사인재 추천 API] 지원자를 찾을 수 없음: {applicant_id}")
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")

        print(f"✅ [유사인재 추천 API] 지원자 확인 완료")
        print(f"  - 지원자 이름: {target_applicant.get('name', 'N/A')}")
        print(f"  - 지원자 직무: {target_applicant.get('position', 'N/A')}")
        print(f"  - 지원자 경력: {target_applicant.get('experience', 'N/A')}")
        print(f"  - 지원자 기술스택: {target_applicant.get('skills', 'N/A')}")
        print(f"  - 이력서 ID: {target_applicant.get('resume_id', 'N/A')}")
        print(f"  - 지원자 필드 목록: {list(target_applicant.keys())}")

        # 2. 유사도 서비스 초기화
        print(f"🔧 [유사인재 추천 API] 2단계: 유사도 서비스 초기화")
        similarity_service = get_similarity_service()
        print(f"  - 유사도 서비스 타입: {type(similarity_service).__name__}")
        print(f"  - 임베딩 서비스: {type(similarity_service.embedding_service).__name__}")
        print(f"  - 벡터 서비스: {type(similarity_service.vector_service).__name__}")
        print(f"  - LLM 서비스: {type(similarity_service.llm_service).__name__}")

        # 3. 유사 인재 추천 수행
        print(f"🔍 [유사인재 추천 API] 3단계: 유사 인재 추천 수행")
        print(f"  - 검색 제한: 5명")
        print(f"  - 검색 시작 시간: {datetime.now().isoformat()}")
        
        start_time = datetime.now()
        result = await similarity_service.search_similar_applicants_hybrid(
            target_applicant=target_applicant,
            applicants_collection=applicant_collection,
            limit=5
        )
        end_time = datetime.now()
        
        search_duration = (end_time - start_time).total_seconds()
        print(f"  - 검색 완료 시간: {end_time.isoformat()}")
        print(f"  - 검색 소요 시간: {search_duration:.2f}초")

        print(f"📊 [유사인재 추천 API] 검색 결과 분석")
        print(f"  - 결과 성공 여부: {result.get('success', False)}")
        print(f"  - 결과 메시지: {result.get('message', 'N/A')}")
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"  - 검색 방법: {data.get('search_method', 'N/A')}")
            ensemble_weights = data.get('ensemble_weights', {})
            if ensemble_weights:
                print(f"  - 가중치 설정: vector: {ensemble_weights.get('vector', 0.5)}, keyword: {ensemble_weights.get('keyword', 0.5)}")
            else:
                print(f"  - 가중치 설정: N/A")
            print(f"  - 총 결과 수: {data.get('total', 0)}")
            print(f"  - 벡터 검색 결과 수: {data.get('vector_count', 0)}")
            print(f"  - 키워드 검색 결과 수: {data.get('keyword_count', 0)}")
            
            results = data.get('results', [])
            print(f"  - 상세 결과 수: {len(results)}")
            
            for i, res in enumerate(results[:3]):  # 상위 3개만 로깅
                applicant = res.get('applicant', {})
                print(f"    #{i+1}: {applicant.get('name', 'N/A')} "
                      f"(최종:{res.get('final_score', 0):.3f}, "
                      f"V:{res.get('vector_score', 0):.3f}, "
                      f"K:{res.get('keyword_score', 0):.3f})")
        else:
            print(f"  - 오류 정보: {result.get('error', 'N/A')}")
            print(f"  - 디버그 정보: {result.get('debug_info', 'N/A')}")

        # 4. 응답 구성
        print(f"📤 [유사인재 추천 API] 4단계: 응답 구성")
        response_data = {
            "status": "success",
            "applicant_id": applicant_id,
            "recommendations": result,
            "message": "유사 인재 추천 완료",
            "debug_info": {
                "search_duration_seconds": search_duration,
                "target_applicant_name": target_applicant.get('name', 'N/A'),
                "target_applicant_position": target_applicant.get('position', 'N/A'),
                "request_timestamp": start_time.isoformat(),
                "response_timestamp": end_time.isoformat()
            }
        }
        
        print(f"✅ [유사인재 추천 API] === 요청 완료 ===")
        print(f"  - 응답 상태: success")
        print(f"  - 총 소요 시간: {search_duration:.2f}초")
        
        return response_data

    except HTTPException:
        print(f"❌ [유사인재 추천 API] HTTP 예외 발생 - 재발생")
        raise
    except Exception as e:
        print(f"❌ [유사인재 추천 API] 예상치 못한 오류 발생")
        print(f"  - 오류 타입: {type(e).__name__}")
        print(f"  - 오류 메시지: {str(e)}")
        print(f"  - 오류 스택: {e.__traceback__}")
        
        import traceback
        print(f"  - 상세 스택 트레이스:")
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"유사 인재 추천 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/{applicant_id}/cover-letter")
async def check_cover_letter_plagiarism(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """자소서 표절체크 (호환성을 위한 별명 엔드포인트)"""
    try:
        print(f"[INFO] 자소서 표절체크 요청 - applicant_id: {applicant_id}")

        # 1. 지원자 존재 확인
        applicant = await mongo_service.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")

        # 2. 자소서 존재 확인
        cover_letter_id = applicant.get("cover_letter_id")
        if not cover_letter_id:
            raise HTTPException(status_code=404, detail="자소서가 없습니다")

        # 3. 자소서 내용 가져오기
        from bson import ObjectId
        from motor.motor_asyncio import AsyncIOMotorClient

        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme

        cover_letter = await db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
        client.close()

        if not cover_letter:
            raise HTTPException(status_code=404, detail="자소서를 찾을 수 없습니다")

        cover_letter_text = cover_letter.get("content", "")

        # 4. 유사도 서비스 초기화
        similarity_service = get_similarity_service()

        # 5. 자소서 표절체크 수행 (청킹 기반 유사도 검색 사용)
        result = await similarity_service.find_similar_documents_by_chunks(
            document_id=applicant_id,
            collection=mongo_service.db.applicants,
            document_type="cover_letter",
            limit=10
        )

        return {
            "status": "success",
            "applicant_id": applicant_id,
            "plagiarism_result": result,
            "message": "자소서 표절체크 완료"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 자소서 표절체크 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"자소서 표절체크 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{applicant_id}/cover-letter-analysis")
async def get_cover_letter_analysis(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자의 자소서 분석 결과를 가져옵니다."""
    try:
        print(f"[INFO] 자소서 분석 결과 조회 요청 - applicant_id: {applicant_id}")

        # 1. 지원자 존재 확인
        applicant = await mongo_service.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")

        # 2. 자소서 ID 확인
        cover_letter_id = applicant.get("cover_letter_id")
        if not cover_letter_id:
            raise HTTPException(status_code=404, detail="자소서가 없습니다")

        # 3. 자소서 분석 결과 가져오기
        from bson import ObjectId
        from motor.motor_asyncio import AsyncIOMotorClient

        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme

        try:
            # cover_letter_id 대신 applicant_id로 조회
            cover_letter = await db.cover_letters.find_one({"applicant_id": ObjectId(applicant_id)})
            
            if not cover_letter:
                raise HTTPException(status_code=404, detail="자소서를 찾을 수 없습니다")

            # analysis_results 배열에서 가장 최근 분석 결과 가져오기
            analysis_results = cover_letter.get("analysis_results", [])
            
            if not analysis_results:
                # 분석 결과가 없는 경우 기본 구조 반환
                return {
                    "success": True,
                    "data": {
                        "technical_suitability": { "score": 75, "feedback": "분석이 필요합니다." },
                        "job_understanding": { "score": 80, "feedback": "분석이 필요합니다." },
                        "growth_potential": { "score": 85, "feedback": "분석이 필요합니다." },
                        "teamwork_communication": { "score": 70, "feedback": "분석이 필요합니다." },
                        "motivation_company_fit": { "score": 90, "feedback": "분석이 필요합니다." },
                        "summary": "자소서 분석이 필요합니다.",
                        "recommendations": ["분석을 진행해주세요."],
                        "overall_score": 80
                    },
                    "message": "분석 결과가 없습니다. 분석을 진행해주세요."
                }

            # 가장 최근 분석 결과 반환
            latest_analysis = analysis_results[-1]
            
            return {
                "success": True,
                "data": latest_analysis,
                "message": "자소서 분석 결과를 성공적으로 가져왔습니다."
            }

        finally:
            client.close()

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 자소서 분석 결과 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"자소서 분석 결과 조회 중 오류가 발생했습니다: {str(e)}"
        )
