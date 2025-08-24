"""
페이지 매칭 시스템
사용자의 요청을 분석하여 적절한 페이지로 이동할 수 있도록 도와주는 시스템
픽톡의 완전자율에이전트 모토를 유지하면서 페이지 매칭 기능을 제공
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PageMatch:
    """페이지 매칭 결과를 나타내는 데이터 클래스"""
    page_path: str
    page_name: str
    confidence: float
    reason: str
    action_type: str = "navigate"  # navigate, modal, function
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}

class PageMatcher:
    """페이지 매칭을 담당하는 클래스"""
    
    def __init__(self):
        # 페이지 매핑 정의
        self.page_mappings = {
            # 대시보드 관련
            "dashboard": {
                "keywords": ["대시보드", "홈", "메인", "시작", "처음"],
                "path": "/",
                "name": "대시보드",
                "description": "시스템 전체 현황을 확인할 수 있는 메인 페이지"
            },
            
            # 채용공고 관련
            "job-posting": {
                "keywords": ["채용공고", "구인", "모집", "채용", "공고", "등록", "작성", "올리기"],
                "path": "/job-posting",
                "name": "채용공고 등록",
                "description": "새로운 채용공고를 등록하는 페이지"
            },
            
            # AI 채용공고 등록
            "ai-job-registration": {
                "keywords": ["AI", "인공지능", "자동", "스마트", "도우미", "어시스턴트"],
                "path": "/ai-job-registration",
                "name": "AI 채용공고 등록",
                "description": "AI 도우미를 활용한 채용공고 등록"
            },
            
            # 이력서 관리
            "resume": {
                "keywords": ["이력서", "CV", "경력", "스킬", "기술", "경험"],
                "path": "/resume",
                "name": "이력서 관리",
                "description": "지원자들의 이력서를 관리하는 페이지"
            },
            
            # 지원자 관리
            "applicants": {
                "keywords": ["지원자", "후보자", "지원", "신청자", "후보", "명단"],
                "path": "/applicants",
                "name": "지원자 관리",
                "description": "지원자들의 정보를 관리하는 페이지"
            },
            
            # 면접 관리
            "interview": {
                "keywords": ["면접", "인터뷰", "일정", "스케줄", "캘린더", "미팅"],
                "path": "/interview",
                "name": "면접 관리",
                "description": "면접 일정과 정보를 관리하는 페이지"
            },
            
            # 면접 캘린더
            "interview-calendar": {
                "keywords": ["캘린더", "달력", "일정표", "스케줄러"],
                "path": "/interview-calendar",
                "name": "면접 캘린더",
                "description": "면접 일정을 캘린더 형태로 확인하는 페이지"
            },
            
            # 포트폴리오 분석
            "portfolio": {
                "keywords": ["포트폴리오", "프로젝트", "작품", "깃허브", "코드"],
                "path": "/github-test",
                "name": "포트폴리오 분석",
                "description": "지원자들의 포트폴리오를 분석하는 페이지"
            },
            
            # 자기소개서 검증
            "cover-letter": {
                "keywords": ["자기소개서", "자소서", "소개서", "동기", "이유"],
                "path": "/cover-letter",
                "name": "자기소개서 검증",
                "description": "지원자들의 자기소개서를 검증하는 페이지"
            },
            
            # 인재 추천
            "talent": {
                "keywords": ["인재", "추천", "매칭", "적합", "추천인"],
                "path": "/talent",
                "name": "인재 추천",
                "description": "적합한 인재를 추천받는 페이지"
            },
            
            # 사용자 관리
            "users": {
                "keywords": ["사용자", "계정", "관리자", "권한", "멤버"],
                "path": "/users",
                "name": "사용자 관리",
                "description": "시스템 사용자들을 관리하는 페이지"
            },
            
            # 설정
            "settings": {
                "keywords": ["설정", "환경설정", "옵션", "프로필", "계정설정"],
                "path": "/settings",
                "name": "설정",
                "description": "시스템 설정을 관리하는 페이지"
            },
            
            # PDF OCR
            "pdf-ocr": {
                "keywords": ["PDF", "OCR", "문서", "스캔", "추출", "텍스트"],
                "path": "/pdf-ocr",
                "name": "PDF OCR",
                "description": "PDF 문서를 OCR로 처리하는 페이지"
            },
            
            # 깃허브 테스트
            "github-test": {
                "keywords": ["깃허브", "GitHub", "테스트", "실험"],
                "path": "/github-test",
                "name": "깃허브 테스트",
                "description": "깃허브 관련 기능을 테스트하는 페이지"
            }
        }
        
        # 액션 키워드 정의
        self.action_keywords = {
            "navigate": ["이동", "가기", "보기", "확인", "열기", "접속"],
            "create": ["생성", "만들기", "작성", "등록", "추가"],
            "edit": ["수정", "편집", "변경", "업데이트"],
            "delete": ["삭제", "제거", "지우기"],
            "search": ["검색", "찾기", "조회", "필터"]
        }
        
        # 특정 기능 키워드
        self.feature_keywords = {
            "modal": ["모달", "팝업", "창", "다이얼로그"],
            "form": ["폼", "양식", "입력", "작성"],
            "list": ["목록", "리스트", "테이블", "그리드"],
            "detail": ["상세", "자세히", "정보", "내용"]
        }

    def match_page(self, user_input: str) -> Optional[PageMatch]:
        """
        사용자 입력을 분석하여 적절한 페이지를 매칭
        
        Args:
            user_input: 사용자 입력 텍스트
            
        Returns:
            PageMatch 객체 또는 None
        """
        print(f"\n🎯 [페이지 매칭 시작] 사용자 입력: {user_input}")
        
        # 입력 전처리
        text = user_input.lower().strip()
        
        # 페이지 매칭 시도
        best_match = None
        best_score = 0.0
        
        for page_id, page_info in self.page_mappings.items():
            score = self._calculate_page_score(text, page_info)
            
            print(f"🎯 [페이지 매칭] {page_info['name']}: {score:.2f}")
            
            if score > best_score:
                best_score = score
                best_match = page_id
        
        # 임계값 확인 (0.3 이상)
        if best_score >= 0.3:
            page_info = self.page_mappings[best_match]
            
            # 액션 타입 결정
            action_type = self._determine_action_type(text)
            
            # 추가 데이터 추출
            additional_data = self._extract_additional_data(text, best_match)
            
            match_result = PageMatch(
                page_path=page_info["path"],
                page_name=page_info["name"],
                confidence=best_score,
                reason=f"'{page_info['name']}' 페이지와 {best_score:.1%} 일치",
                action_type=action_type,
                additional_data=additional_data
            )
            
            print(f"🎯 [페이지 매칭 완료] {match_result.page_name} ({match_result.confidence:.1%})")
            return match_result
        
        print(f"🎯 [페이지 매칭 실패] 적절한 페이지를 찾을 수 없음 (최고 점수: {best_score:.2f})")
        return None

    def _calculate_page_score(self, text: str, page_info: Dict[str, Any]) -> float:
        """페이지 매칭 점수 계산"""
        score = 0.0
        
        # 키워드 매칭
        for keyword in page_info["keywords"]:
            if keyword in text:
                score += 0.2
                
                # 정확한 매칭에 가중치
                if keyword == text or text.startswith(keyword) or text.endswith(keyword):
                    score += 0.1
        
        # 설명 매칭
        description = page_info["description"]
        for word in text.split():
            if word in description:
                score += 0.05
        
        # 액션 키워드와의 조합
        for action_type, action_keywords in self.action_keywords.items():
            for action_keyword in action_keywords:
                if action_keyword in text:
                    score += 0.1
                    break
        
        # 특별한 패턴 보너스
        # 사용자명 + 포트폴리오/깃허브 패턴
        if re.search(r'\b[a-zA-Z][a-zA-Z0-9_]{2,}\b', text):  # 사용자명 패턴
            if page_info.get("name") == "포트폴리오 분석" and any(keyword in text for keyword in ["포트폴리오", "깃허브", "프로젝트", "분석", "결과"]):
                score += 0.3  # 포트폴리오 분석 페이지에 보너스
            elif page_info.get("name") == "깃허브 테스트" and any(keyword in text for keyword in ["깃허브", "github"]):
                score += 0.3  # 깃허브 테스트 페이지에 보너스
        
        return min(score, 1.0)  # 최대 1.0

    def _determine_action_type(self, text: str) -> str:
        """액션 타입 결정"""
        text_lower = text.lower()
        
        # 모달 관련 키워드
        if any(keyword in text_lower for keyword in self.feature_keywords["modal"]):
            return "modal"
        
        # 폼 관련 키워드
        if any(keyword in text_lower for keyword in self.feature_keywords["form"]):
            return "form"
        
        # 기본적으로 네비게이션
        return "navigate"

    def _extract_additional_data(self, text: str, page_id: str) -> Dict[str, Any]:
        """추가 데이터 추출"""
        additional_data = {}
        
        # 사용자명 추출 (영어/숫자 조합 - GitHub 사용자명 등)
        username_match = re.search(r'\b([a-zA-Z][a-zA-Z0-9_]{2,})\b', text)
        if username_match:
            potential_username = username_match.group(1)
            # 일반적인 단어가 아닌 경우만 사용자명으로 인식
            if not potential_username.lower() in ['portfolio', 'github', 'project', 'analysis', 'result']:
                additional_data["username"] = potential_username
        
        # 지원자 이름 추출 (한글)
        name_match = re.search(r'([가-힣]{2,4})\s*(지원자|님|의|을|를|에게)?', text)
        if name_match:
            additional_data["applicant_name"] = name_match.group(1)
        
        # 문서 타입 추출
        doc_types = {
            "이력서": "resume",
            "자기소개서": "cover_letter", 
            "포트폴리오": "portfolio"
        }
        
        for korean_name, doc_type in doc_types.items():
            if korean_name in text:
                additional_data["document_type"] = doc_type
                break
        
        return additional_data

    def get_available_pages(self) -> List[Dict[str, str]]:
        """사용 가능한 페이지 목록 반환"""
        return [
            {
                "id": page_id,
                "name": info["name"],
                "path": info["path"],
                "description": info["description"]
            }
            for page_id, info in self.page_mappings.items()
        ]

    def suggest_pages(self, user_input: str) -> List[PageMatch]:
        """사용자 입력에 대한 페이지 제안"""
        suggestions = []
        
        for page_id, page_info in self.page_mappings.items():
            score = self._calculate_page_score(user_input, page_info)
            if score >= 0.1:  # 낮은 임계값으로 제안
                suggestions.append(PageMatch(
                    page_path=page_info["path"],
                    page_name=page_info["name"],
                    confidence=score,
                    reason=f"'{page_info['name']}' 페이지와 관련이 있을 수 있습니다",
                    action_type="navigate"
                ))
        
        # 점수 순으로 정렬
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:3]  # 상위 3개만 반환

# 전역 인스턴스
page_matcher = PageMatcher()
