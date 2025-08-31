"""
채용공고 템플릿 시스템
LLM이 참조할 수 있는 다양한 채용공고 템플릿
"""

from typing import Dict, List, Any
from enum import Enum

class JobLevel(str, Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"

class JobType(str, Enum):
    FULLTIME = "fulltime"
    PARTTIME = "parttime"
    CONTRACT = "contract"
    INTERNSHIP = "internship"

class JobTemplate:
    """채용공고 템플릿 클래스"""

    def __init__(self, level: JobLevel, job_type: JobType):
        self.level = level
        self.job_type = job_type
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        """템플릿 로드"""
        return {
            JobLevel.INTERN: {
                "title_patterns": [
                    "{company} {position} 인턴 채용",
                    "{position} 인턴십 모집",
                    "{company} {position} 인턴 개발자 채용"
                ],
                "description_patterns": [
                    "열정적인 {position} 인턴을 모집합니다.",
                    "성장하고 싶은 {position} 인턴을 찾습니다.",
                    "함께 성장할 {position} 인턴을 모집합니다."
                ],
                "requirements": [
                    "관련 전공자 또는 관련 분야에 관심이 있는 분",
                    "기본적인 프로그래밍 지식 보유",
                    "팀워크와 소통 능력",
                    "새로운 기술에 대한 학습 의지"
                ],
                "preferred": [
                    "관련 프로젝트 경험",
                    "Git 사용 경험",
                    "기술 블로그 운영 경험",
                    "오픈소스 기여 경험"
                ]
            },
            JobLevel.JUNIOR: {
                "title_patterns": [
                    "{company} {position} 신입/경력 채용",
                    "{position} 개발자 모집",
                    "{company} {position} 신입 개발자 채용"
                ],
                "description_patterns": [
                    "함께 성장할 {position} 개발자를 모집합니다.",
                    "열정적인 {position} 개발자를 찾습니다.",
                    "새로운 도전을 원하는 {position} 개발자를 모집합니다."
                ],
                "requirements": [
                    "관련 전공자 또는 관련 분야 경험",
                    "기본적인 프로그래밍 언어 숙련도",
                    "문제 해결 능력과 학습 의지",
                    "팀워크와 소통 능력"
                ],
                "preferred": [
                    "관련 프로젝트 경험",
                    "Git 사용 경험",
                    "기술 블로그 운영 경험",
                    "오픈소스 기여 경험"
                ]
            },
            JobLevel.MIDDLE: {
                "title_patterns": [
                    "{company} {position} 경력 개발자 채용",
                    "{position} 개발자 모집",
                    "{company} {position} 중급 개발자 채용"
                ],
                "description_patterns": [
                    "경험을 바탕으로 성장할 {position} 개발자를 모집합니다.",
                    "독립적으로 업무를 수행할 수 있는 {position} 개발자를 찾습니다.",
                    "기술적 역량을 발휘할 {position} 개발자를 모집합니다."
                ],
                "requirements": [
                    "관련 분야 3년 이상 경력",
                    "독립적인 프로젝트 수행 능력",
                    "기술적 문제 해결 능력",
                    "팀 협업 및 소통 능력"
                ],
                "preferred": [
                    "대규모 프로젝트 경험",
                    "아키텍처 설계 경험",
                    "멘토링 경험",
                    "기술 발표 경험"
                ]
            },
            JobLevel.SENIOR: {
                "title_patterns": [
                    "{company} {position} 시니어 개발자 채용",
                    "{position} 시니어 개발자 모집",
                    "{company} {position} 고급 개발자 채용"
                ],
                "description_patterns": [
                    "기술 리더십을 발휘할 {position} 시니어 개발자를 모집합니다.",
                    "아키텍처 설계와 기술 의사결정을 담당할 {position} 개발자를 찾습니다.",
                    "팀의 기술적 성장을 이끌 {position} 시니어 개발자를 모집합니다."
                ],
                "requirements": [
                    "관련 분야 5년 이상 경력",
                    "대규모 시스템 설계 및 개발 경험",
                    "기술 리더십 및 멘토링 경험",
                    "아키텍처 설계 및 기술 의사결정 경험"
                ],
                "preferred": [
                    "팀 리드 경험",
                    "기술 컨퍼런스 발표 경험",
                    "오픈소스 프로젝트 리드 경험",
                    "기술 블로그 운영 및 기술 문서 작성 경험"
                ]
            },
            JobLevel.LEAD: {
                "title_patterns": [
                    "{company} {position} 팀 리드 채용",
                    "{position} 팀 리드 모집",
                    "{company} {position} 기술 리드 채용"
                ],
                "description_patterns": [
                    "팀을 이끌고 기술적 비전을 제시할 {position} 팀 리드를 모집합니다.",
                    "기술 전략과 팀 관리 능력을 겸비한 {position} 리드를 찾습니다.",
                    "조직의 기술적 성장을 주도할 {position} 팀 리드를 모집합니다."
                ],
                "requirements": [
                    "관련 분야 7년 이상 경험",
                    "팀 리드 또는 매니저 경험",
                    "기술 전략 수립 및 실행 경험",
                    "조직 관리 및 리더십 경험"
                ],
                "preferred": [
                    "대규모 조직 관리 경험",
                    "기술 컨퍼런스 키노트 발표 경험",
                    "기술 커뮤니티 리더 경험",
                    "기술 전략 수립 및 실행 경험"
                ]
            }
        }

    def get_template(self) -> Dict[str, Any]:
        """현재 레벨의 템플릿 반환"""
        return self.templates.get(self.level, {})

    def generate_title(self, company: str, position: str) -> str:
        """제목 생성"""
        patterns = self.get_template().get("title_patterns", [])
        if patterns:
            import random
            pattern = random.choice(patterns)
            return pattern.format(company=company, position=position)
        return f"{company} {position} 채용"

    def generate_description(self, position: str) -> str:
        """설명 생성"""
        patterns = self.get_template().get("description_patterns", [])
        if patterns:
            import random
            pattern = random.choice(patterns)
            return pattern.format(position=position)
        return f"{position} 개발자를 모집합니다."

    def get_requirements(self) -> List[str]:
        """자격 요건 반환"""
        return self.get_template().get("requirements", [])

    def get_preferred(self) -> List[str]:
        """우대 사항 반환"""
        return self.get_template().get("preferred", [])

class JobTemplateManager:
    """채용공고 템플릿 관리자"""

    def __init__(self):
        self.templates = {}
        self._init_templates()

    def _init_templates(self):
        """템플릿 초기화"""
        for level in JobLevel:
            for job_type in JobType:
                key = f"{level.value}_{job_type.value}"
                self.templates[key] = JobTemplate(level, job_type)

    def get_template(self, level: JobLevel, job_type: JobType) -> JobTemplate:
        """템플릿 조회"""
        key = f"{level.value}_{job_type.value}"
        return self.templates.get(key)

    def get_all_templates(self) -> Dict[str, JobTemplate]:
        """모든 템플릿 반환"""
        return self.templates

    def suggest_template(self, keywords: List[str], requirements: Dict[str, Any]) -> JobTemplate:
        """키워드와 요구사항을 바탕으로 적합한 템플릿 추천"""
        # 키워드 분석
        level_keywords = {
            JobLevel.INTERN: ["인턴", "인턴십", "신입", "학생"],
            JobLevel.JUNIOR: ["신입", "주니어", "1년", "2년"],
            JobLevel.MIDDLE: ["경력", "중급", "3년", "4년", "5년"],
            JobLevel.SENIOR: ["시니어", "고급", "5년", "6년", "7년"],
            JobLevel.LEAD: ["리드", "팀장", "매니저", "7년", "8년", "9년"]
        }

        # 레벨 추정
        suggested_level = JobLevel.JUNIOR  # 기본값
        for level, level_words in level_keywords.items():
            if any(word in " ".join(keywords) for word in level_words):
                suggested_level = level
                break

        # 직무 타입 추정
        suggested_type = JobType.FULLTIME  # 기본값
        if "계약" in " ".join(keywords) or "contract" in " ".join(keywords):
            suggested_type = JobType.CONTRACT
        elif "인턴" in " ".join(keywords) or "intern" in " ".join(keywords):
            suggested_type = JobType.INTERNSHIP
        elif "파트타임" in " ".join(keywords) or "parttime" in " ".join(keywords):
            suggested_type = JobType.PARTTIME

        return self.get_template(suggested_level, suggested_type)

# 전역 템플릿 매니저 인스턴스
template_manager = JobTemplateManager()
