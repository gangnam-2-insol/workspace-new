import asyncio
import logging
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, quote

logger = logging.getLogger(__name__)

class TrendCrawler:
    """채용 트렌드 크롤링 서비스"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    async def get_job_trends(self, job_keyword: str = "") -> List[str]:
        """직무별 채용 트렌드 수집"""
        try:
            trends = []

            # 여러 소스에서 트렌드 수집
            if job_keyword:
                # 직무별 특화 트렌드
                job_trends = await self._get_job_specific_trends(job_keyword)
                trends.extend(job_trends)

            # 일반적인 채용 트렌드
            general_trends = await self._get_general_trends()
            trends.extend(general_trends)

            # 중복 제거 및 정리
            unique_trends = list(set(trends))
            return unique_trends[:10]  # 상위 10개만 반환

        except Exception as e:
            logger.error(f"트렌드 수집 실패: {str(e)}")
            return self._get_fallback_trends(job_keyword)

    async def _get_job_specific_trends(self, job_keyword: str) -> List[str]:
        """직무별 특화 트렌드 수집"""
        trends = []

        # 직무별 기본 트렌드 매핑
        job_trends_mapping = {
            "개발자": [
                "클린 코드", "테스트 주도 개발", "마이크로서비스", "클라우드 네이티브",
                "DevOps", "CI/CD", "코드 리뷰", "페어 프로그래밍", "애자일 방법론"
            ],
            "디자이너": [
                "사용자 경험(UX)", "사용자 인터페이스(UI)", "디자인 시스템", "프로토타이핑",
                "사용자 리서치", "접근성", "반응형 디자인", "마이크로 인터랙션"
            ],
            "기획자": [
                "데이터 기반 의사결정", "A/B 테스트", "사용자 스토리", "프로덕트 로드맵",
                "KPI 설정", "스프린트 기획", "스테이크홀더 관리", "리스크 관리"
            ],
            "마케터": [
                "디지털 마케팅", "콘텐츠 마케팅", "SEO/SEM", "소셜 미디어 마케팅",
                "인플루언서 마케팅", "퍼포먼스 마케팅", "브랜드 마케팅", "고객 여정 관리"
            ],
            "영업": [
                "고객 관계 관리(CRM)", "영업 파이프라인", "제안서 작성", "협상 기술",
                "고객 니즈 분석", "영업 전략", "파트너십 관리", "매출 예측"
            ]
        }

        # 키워드 매칭
        for job, job_trends in job_trends_mapping.items():
            if job in job_keyword or job_keyword in job:
                trends.extend(job_trends)
                break

        return trends

    async def _get_general_trends(self) -> List[str]:
        """일반적인 채용 트렌드 수집"""
        try:
            # 실제 크롤링 대신 시뮬레이션 (실제 구현 시에는 실제 사이트 크롤링)
            general_trends = [
                "원격 근무", "하이브리드 워크", "워라밸", "성장 기회",
                "학습 문화", "다양성과 포용성", "지속가능성", "혁신 문화",
                "데이터 기반 의사결정", "고객 중심 사고", "협업 문화", "책임감"
            ]

            return general_trends

        except Exception as e:
            logger.error(f"일반 트렌드 수집 실패: {str(e)}")
            return []

    def _get_fallback_trends(self, job_keyword: str) -> List[str]:
        """크롤링 실패 시 기본 트렌드 반환"""
        base_trends = [
            "협업 능력", "문제 해결 능력", "학습 의지", "책임감",
            "고객 중심 사고", "혁신적 사고", "적응력", "성장 마인드셋"
        ]

        if job_keyword:
            if "개발" in job_keyword:
                base_trends.extend(["기술적 전문성", "코드 품질", "테스트 주도 개발"])
            elif "디자인" in job_keyword:
                base_trends.extend(["사용자 경험", "창의적 표현", "디자인 시스템"])
            elif "기획" in job_keyword:
                base_trends.extend(["전략적 사고", "데이터 분석", "프로젝트 관리"])
            elif "마케팅" in job_keyword:
                base_trends.extend(["시장 감각", "콘텐츠 제작", "데이터 기반 마케팅"])

        return base_trends

    async def crawl_job_sites(self, job_keyword: str) -> List[Dict[str, Any]]:
        """실제 채용 사이트 크롤링 (향후 구현)"""
        # 실제 구현 시에는 다음과 같은 사이트들을 크롤링
        # - 잡코리아, 원티드, 사람인, 로켓펀치 등
        # - 각 사이트의 채용 공고에서 키워드 추출

        # 현재는 시뮬레이션 데이터 반환
        return [
            {
                "title": f"{job_keyword} 관련 채용공고",
                "keywords": ["협업", "문제해결", "학습능력"],
                "source": "시뮬레이션"
            }
        ]

    def extract_keywords_from_text(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 로직
        keywords = []

        # 일반적인 채용 키워드 패턴
        common_keywords = [
            "협업", "문제해결", "책임감", "학습", "혁신", "고객", "성장",
            "전문성", "창의성", "적응력", "소통", "리더십", "팀워크"
        ]

        for keyword in common_keywords:
            if keyword in text:
                keywords.append(keyword)

        return keywords
