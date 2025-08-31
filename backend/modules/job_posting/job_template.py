"""
기본 채용공고 템플릿 관리자
동적 템플릿 시스템과 호환되는 기본 템플릿 관리자
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime

class JobLevel(str, Enum):
    """채용 레벨"""
    JUNIOR = "junior"      # 신입
    MIDDLE = "middle"      # 중급
    SENIOR = "senior"      # 고급
    LEAD = "lead"          # 리드
    MANAGER = "manager"    # 매니저

class JobType(str, Enum):
    """채용 유형"""
    FULLTIME = "fulltime"  # 정규직
    CONTRACT = "contract"  # 계약직
    INTERN = "intern"      # 인턴
    PARTTIME = "parttime"  # 파트타임

class JobTemplate:
    """기본 채용공고 템플릿"""

    def __init__(self, template_id: str, name: str, level: JobLevel, job_type: JobType):
        self.template_id = template_id
        self.name = name
        self.level = level
        self.job_type = job_type
        self.content = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class JobTemplateManager:
    """기본 템플릿 관리자"""

    def __init__(self):
        self.templates = {}
        self._initialize_default_templates()

    def _initialize_default_templates(self):
        """기본 템플릿 초기화"""
        # 신입 개발자 템플릿
        junior_template = JobTemplate("junior_dev", "신입 개발자", JobLevel.JUNIOR, JobType.FULLTIME)
        junior_template.content = {
            "title_patterns": ["{company} 신입 개발자 채용", "{company} 신입 {position} 개발자 모집"],
            "description_patterns": [
                "열정적인 신입 개발자를 모집합니다.",
                "함께 성장할 신입 개발자를 찾습니다."
            ],
            "requirements": [
                "컴퓨터공학 또는 관련 전공자",
                "프로그래밍 언어에 대한 기본 지식",
                "새로운 기술에 대한 학습 의지"
            ],
            "preferred": [
                "프로젝트 경험",
                "오픈소스 기여 경험",
                "기술 블로그 운영"
            ]
        }
        self.templates["junior_dev"] = junior_template

        # 중급 개발자 템플릿
        middle_template = JobTemplate("middle_dev", "중급 개발자", JobLevel.MIDDLE, JobType.FULLTIME)
        middle_template.content = {
            "title_patterns": ["{company} {position} 개발자 채용", "{company} 중급 {position} 개발자 모집"],
            "description_patterns": [
                "경험 있는 개발자를 모집합니다.",
                "함께 성장할 중급 개발자를 찾습니다."
            ],
            "requirements": [
                "관련 분야 3년 이상 경험",
                "프로젝트 경험",
                "문제 해결 능력"
            ],
            "preferred": [
                "팀 프로젝트 경험",
                "기술 리더십 경험",
                "성과 지향적 사고"
            ]
        }
        self.templates["middle_dev"] = middle_template

        # 고급 개발자 템플릿
        senior_template = JobTemplate("senior_dev", "고급 개발자", JobLevel.SENIOR, JobType.FULLTIME)
        senior_template.content = {
            "title_patterns": ["{company} 시니어 {position} 개발자 채용", "{company} 고급 {position} 개발자 모집"],
            "description_patterns": [
                "시니어 개발자를 모집합니다.",
                "기술 리더십을 발휘할 고급 개발자를 찾습니다."
            ],
            "requirements": [
                "관련 분야 5년 이상 경험",
                "대규모 프로젝트 경험",
                "기술 아키텍처 설계 경험"
            ],
            "preferred": [
                "팀 리더십 경험",
                "기술 멘토링 경험",
                "비즈니스 이해도"
            ]
        }
        self.templates["senior_dev"] = senior_template

    def get_template_by_id(self, template_id: str) -> Optional[JobTemplate]:
        """ID로 템플릿 조회"""
        return self.templates.get(template_id)

    def get_templates_by_criteria(self, level: JobLevel = None, job_type: JobType = None) -> List[JobTemplate]:
        """조건에 맞는 템플릿 조회"""
        result = []
        for template in self.templates.values():
            if level and template.level != level:
                continue
            if job_type and template.job_type != job_type:
                continue
            result.append(template)
        return result

    def create_template(self, name: str, level: JobLevel, job_type: JobType, content: Dict[str, Any]) -> JobTemplate:
        """새 템플릿 생성"""
        template_id = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        template = JobTemplate(template_id, name, level, job_type)
        template.content = content
        self.templates[template_id] = template
        return template
