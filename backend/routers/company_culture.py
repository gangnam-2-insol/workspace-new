import os
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

from models.company_culture import (
    CompanyCultureCreate, CompanyCultureUpdate, CompanyCultureResponse,
    ApplicantCultureScore
)
from modules.company_culture.services import CompanyCultureService, get_database
from services.llm_service import LLMService
from services.trend_crawler import TrendCrawler

router = APIRouter(prefix="/api/company-culture", tags=["회사 인재상"])

@router.post("/", response_model=CompanyCultureResponse)
async def create_company_culture(
    culture_data: CompanyCultureCreate,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """회사 인재상 생성"""
    service = CompanyCultureService(db)
    result = await service.create_culture(culture_data)
    return result

@router.get("/", response_model=List[CompanyCultureResponse])
async def get_company_cultures(
    category: str = Query(None, description="카테고리별 필터링"),
    db: AsyncIOMotorClient = Depends(get_database)
):
    """회사 인재상 목록 조회"""
    service = CompanyCultureService(db)

    if category:
        return await service.get_cultures_by_category(category)
    else:
        return await service.get_all_cultures()

@router.get("/default", response_model=CompanyCultureResponse)
async def get_default_culture(
    db: AsyncIOMotorClient = Depends(get_database)
):
    """기본 인재상 조회"""
    service = CompanyCultureService(db)
    default_culture = await service.get_default_culture()

    if not default_culture:
        # 기본 인재상이 없으면 404 대신 빈 응답 반환
        raise HTTPException(
            status_code=404,
            detail="기본 인재상이 설정되지 않았습니다. 인재상 관리에서 기본 인재상을 설정해주세요."
        )

    return default_culture

@router.post("/{culture_id}/set-default", response_model=CompanyCultureResponse)
async def set_default_culture(
    culture_id: str,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """기본 인재상 설정"""
    service = CompanyCultureService(db)
    return await service.set_default_culture(culture_id)

@router.get("/{culture_id}", response_model=CompanyCultureResponse)
async def get_company_culture(
    culture_id: str,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """특정 회사 인재상 조회"""
    service = CompanyCultureService(db)
    return await service.get_culture_by_id(culture_id)

@router.put("/{culture_id}", response_model=CompanyCultureResponse)
async def update_company_culture(
    culture_id: str,
    update_data: CompanyCultureUpdate,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """회사 인재상 수정"""
    service = CompanyCultureService(db)
    return await service.update_culture(culture_id, update_data)

@router.delete("/{culture_id}")
async def delete_company_culture(
    culture_id: str,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """회사 인재상 삭제 (비활성화)"""
    service = CompanyCultureService(db)
    await service.delete_culture(culture_id)
    return {"message": "인재상이 성공적으로 삭제되었습니다."}

@router.post("/evaluate/{applicant_id}/{culture_id}", response_model=ApplicantCultureScore)
async def evaluate_applicant_culture(
    applicant_id: str,
    culture_id: str,
    resume_text: str,
    cover_letter_text: str = "",
    db: AsyncIOMotorClient = Depends(get_database)
):
    """지원자 인재상 평가"""
    service = CompanyCultureService(db)
    return await service.evaluate_applicant_culture(
        applicant_id, culture_id, resume_text, cover_letter_text
    )

@router.get("/categories/list")
async def get_culture_categories(db: AsyncIOMotorClient = Depends(get_database)):
    """인재상 카테고리 목록 조회 (더 이상 사용되지 않음)"""
    return {
        "categories": []
    }

@router.get("/stats/overview")
async def get_culture_statistics(db: AsyncIOMotorClient = Depends(get_database)):
    """인재상 통계 조회"""
    try:
        # 전체 인재상 수
        total_count = await db.company_cultures.count_documents({})
        active_count = await db.company_cultures.count_documents({"is_active": True})

        return {
            "total_cultures": total_count,
            "active_cultures": active_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="통계 조회에 실패했습니다.")

@router.post("/ai-generate")
async def generate_ai_cultures(
    request_data: dict,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """AI를 사용한 인재상 자동 생성 (키워드 기반)"""
    try:
        print(f"🔍 [AI 인재상 추천] 요청 데이터: {request_data}")

        keywords = request_data.get("keywords", [])
        job = request_data.get("job", "")
        department = request_data.get("department", "")
        use_trends = request_data.get("use_trends", False)

        print(f"🔍 [AI 인재상 추천] 파싱된 데이터:")
        print(f"   - 키워드: {keywords}")
        print(f"   - 직무: {job}")
        print(f"   - 부서: {department}")
        print(f"   - 트렌드 사용: {use_trends}")

        # 키워드 기반 맞춤형 인재상 생성
        recommended_cultures = await generate_custom_cultures(keywords, job, department, use_trends)

        print(f"🔍 [AI 인재상 추천] 생성된 인재상 수: {len(recommended_cultures)}")
        for i, culture in enumerate(recommended_cultures):
            print(f"   {i+1}. {culture.get('name', 'N/A')}")

        return recommended_cultures
    except Exception as e:
        print(f"❌ [AI 인재상 추천] 오류 발생: {str(e)}")
        import traceback
        print(f"❌ [AI 인재상 추천] 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="AI 인재상 생성에 실패했습니다.")

async def generate_custom_cultures(keywords: list, job: str, department: str, use_trends: bool) -> list:
    """키워드 기반 맞춤형 인재상 생성 (LLM + 크롤링 통합)"""

    print(f"🔍 [generate_custom_cultures] 시작")
    print(f"   - 키워드: {keywords}")
    print(f"   - 직무: {job}")
    print(f"   - 부서: {department}")
    print(f"   - 트렌드 사용: {use_trends}")

    try:
        # LLM 서비스 초기화
        print(f"🔍 [generate_custom_cultures] LLM 서비스 초기화 시작")
        llm_service = LLMService()
        print(f"🔍 [generate_custom_cultures] LLM 서비스 초기화 완료")

        trend_crawler = TrendCrawler()
        print(f"🔍 [generate_custom_cultures] 트렌드 크롤러 초기화 완료")

        # 트렌드 수집 (use_trends가 True인 경우)
        trends = []
        if use_trends:
            print(f"🔍 [generate_custom_cultures] 트렌드 수집 시작")
            trends = await trend_crawler.get_job_trends(job)
            print(f"🔍 [generate_custom_cultures] 수집된 트렌드: {trends}")

        # LLM을 사용한 인재상 생성
        print(f"🔍 [generate_custom_cultures] LLM 인재상 생성 시작")
        llm_cultures = await llm_service.generate_culture_recommendations(
            keywords=keywords,
            job=job,
            department=department,
            trends=trends
        )
        print(f"🔍 [generate_custom_cultures] LLM 인재상 생성 완료: {len(llm_cultures) if llm_cultures else 0}개")

        # LLM 결과가 있으면 반환, 없으면 기본 규칙 기반으로 폴백
        if llm_cultures and len(llm_cultures) > 0:
            print(f"🔍 [generate_custom_cultures] LLM 결과 사용 (최대 7개)")
            return llm_cultures[:7]  # 최대 7개 반환

        # 폴백: 기본 규칙 기반 추천
        print(f"🔍 [generate_custom_cultures] LLM 결과 없음, 폴백 사용")
        return await _fallback_recommendations(keywords, job, department)

    except Exception as e:
        print(f"❌ [generate_custom_cultures] LLM 기반 추천 실패: {str(e)}")
        import traceback
        print(f"❌ [generate_custom_cultures] 스택 트레이스: {traceback.format_exc()}")
        logger.error(f"LLM 기반 추천 실패: {str(e)}")
        # 완전한 폴백: 기본 규칙 기반 추천
        print(f"🔍 [generate_custom_cultures] 폴백으로 전환")
        return await _fallback_recommendations(keywords, job, department)

async def _fallback_recommendations(keywords: list, job: str, department: str) -> list:
    """기본 규칙 기반 인재상 추천 (폴백)"""

    print(f"🔍 [_fallback_recommendations] 폴백 추천 시작")
    print(f"   - 키워드: {keywords}")
    print(f"   - 직무: {job}")
    print(f"   - 부서: {department}")

    # 키워드 기반 맞춤 인재상 생성
    custom_cultures = []

    # 입력된 키워드를 기반으로 인재상 생성
    for keyword in keywords:
        if keyword.lower() in ["책임감", "책임", "성실"]:
            custom_cultures.append({
                "name": "책임감과 성실성",
                "description": "자신의 역할과 의무를 성실히 수행하고 결과에 대한 책임을 지는 자세"
            })
        elif keyword.lower() in ["협업", "팀워크", "협력"]:
            custom_cultures.append({
                "name": "효과적 협업",
                "description": "다양한 배경의 사람들과 협력하여 공통 목표를 달성하는 능력"
            })
        elif keyword.lower() in ["문제해결", "문제", "해결"]:
            custom_cultures.append({
                "name": "문제 해결 능력",
                "description": "복잡한 문제를 체계적으로 분석하고 창의적으로 해결하는 능력"
            })
        elif keyword.lower() in ["혁신", "창의", "창의적"]:
            custom_cultures.append({
                "name": "혁신적 사고",
                "description": "새로운 아이디어를 창출하고 문제를 창의적으로 해결하는 능력"
            })
        elif keyword.lower() in ["고객", "고객중심", "고객지향"]:
            custom_cultures.append({
                "name": "고객 중심 사고",
                "description": "고객의 니즈를 이해하고 이를 만족시키기 위해 노력하는 자세"
            })
        elif keyword.lower() in ["학습", "성장", "개발"]:
            custom_cultures.append({
                "name": "지속적 성장",
                "description": "새로운 기술과 지식을 습득하여 개인과 조직의 성장을 추구하는 자세"
            })
        else:
            # 일반적인 키워드에 대한 기본 인재상
            custom_cultures.append({
                "name": f"{keyword} 중심",
                "description": f"{keyword}을(를) 중요하게 생각하고 실천하는 자세"
            })

    # 직무별 특화 인재상 추가
    job_specific = {
        "개발자": [
            {"name": "기술적 전문성", "description": "최신 기술 트렌드를 파악하고 실무에 적용하는 능력"},
            {"name": "코드 품질", "description": "깔끔하고 유지보수가 용이한 코드를 작성하는 능력"},
            {"name": "문제 해결 능력", "description": "복잡한 기술적 문제를 체계적으로 분석하고 해결하는 능력"}
        ],
        "디자이너": [
            {"name": "창의적 표현", "description": "사용자 경험을 고려한 창의적이고 직관적인 디자인 능력"},
            {"name": "사용자 중심 사고", "description": "사용자의 니즈와 행동 패턴을 이해하고 반영하는 능력"}
        ],
        "기획자": [
            {"name": "전략적 사고", "description": "비즈니스 목표를 달성하기 위한 전략적 계획 수립 능력"},
            {"name": "데이터 기반 의사결정", "description": "데이터를 분석하여 객관적이고 효과적인 의사결정을 하는 능력"}
        ],
        "마케터": [
            {"name": "시장 감각", "description": "시장 트렌드와 고객 니즈를 빠르게 파악하는 능력"},
            {"name": "창의적 마케팅", "description": "새롭고 효과적인 마케팅 전략을 기획하고 실행하는 능력"}
        ]
    }

    if job and job in job_specific:
        custom_cultures.extend(job_specific[job])

    # 중복 제거
    seen_names = set()
    unique_cultures = []
    for culture in custom_cultures:
        if culture["name"] not in seen_names:
            seen_names.add(culture["name"])
            unique_cultures.append(culture)

    print(f"🔍 [_fallback_recommendations] 생성된 인재상:")
    for i, culture in enumerate(unique_cultures):
        print(f"   {i+1}. {culture['name']}")

    # 최대 7개까지만 반환
    result = unique_cultures[:7]
    print(f"🔍 [_fallback_recommendations] 최종 반환: {len(result)}개")
    return result
