"""
LangGraph Agent 시스템 테스트
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# 상위 디렉토리를 파이썬 패스에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_agent_system import LangGraphAgentSystem

class TestCase:
    def __init__(self, input: str, expected_intent: str, category: str):
        self.input = input
        self.expected_intent = expected_intent
        self.category = category
        
    def __str__(self):
        return f"Input: {self.input}, Expected: {self.expected_intent}, Category: {self.category}"

def generate_test_cases() -> List[TestCase]:
    """테스트 케이스 생성"""
    test_cases = []
    
    # 1. 정보 요청 테스트 (25개)
    info_requests = [
        "채용 트렌드가 어떻게 되나요?",
        "개발자 연봉 수준이 어떻게 되나요?",
        "신입 개발자 면접 준비는 어떻게 하나요?",
        "프론트엔드 개발자의 주요 업무가 뭔가요?",
        "백엔드 개발자에게 필요한 기술스택을 알려줘",
        "데브옵스 엔지니어의 하는 일이 뭐예요?",
        "인공지능 개발자 전망이 어떤가요?",
        "클라우드 엔지니어가 되려면 어떻게 해야 하나요?",
        "IT 업계 채용 시장 상황이 어떤가요?",
        "개발자 이력서는 어떻게 작성하는게 좋을까요?",
        "포트폴리오는 어떻게 준비해야 하나요?",
        "기술 면접은 보통 어떻게 진행되나요?",
        "개발자 영어 면접은 어떻게 준비하나요?",
        "신입 개발자 채용 공고 작성 팁 좀 알려주세요",
        "개발자 채용 시 가장 중요한 점이 뭔가요?",
        "코딩 테스트는 어떻게 준비해야 하나요?",
        "개발자 연봉 협상은 어떻게 하는게 좋을까요?",
        "재택근무 회사 찾는 방법 알려주세요",
        "스타트업 개발자로 일하는 것의 장단점이 뭔가요?",
        "대기업 IT 직군 채용 프로세스가 어떻게 되나요?",
        "프리랜서 개발자는 어떻게 시작하나요?",
        "개발자 전직 시 고려사항이 뭐가 있을까요?",
        "개발자 성장 로드맵 좀 설명해주세요",
        "주니어 개발자가 피해야 할 실수가 뭐가 있나요?",
        "개발자 커리어 패스에 대해 설명해주세요"
    ]
    
    for req in info_requests:
        test_cases.append(TestCase(req, "info_request", "정보 요청"))
    
    # 2. UI 액션 테스트 (25개)
    ui_actions = [
        "채용 페이지 열어줘",
        "이력서 관리 화면으로 이동해줘",
        "면접 관리 페이지 보여줘",
        "대시보드로 돌아가줘",
        "설정 페이지 열어줘",
        "채용 공고 등록 페이지로 이동",
        "지원자 목록 화면 보여줘",
        "포트폴리오 분석 페이지 열어줘",
        "인재 추천 페이지로 이동해줘",
        "면접 일정 관리 화면 보여줘",
        "사용자 관리 페이지 열어줘",
        "통계 대시보드로 이동해줘",
        "이력서 상세 보기 화면 열어줘",
        "채용 공고 미리보기 화면으로 이동",
        "지원자 평가 페이지 보여줘",
        "면접관 배정 화면 열어줘",
        "합격자 관리 페이지로 이동",
        "채용 프로세스 설정 화면 보여줘",
        "이메일 템플릿 관리 페이지 열어줘",
        "평가 기준 설정 화면으로 이동",
        "공고 마감 관리 페이지 보여줘",
        "지원자 필터링 화면 열어줘",
        "면접 피드백 페이지로 이동",
        "채용 통계 화면 보여줘",
        "시스템 로그 페이지 열어줘"
    ]
    
    for action in ui_actions:
        test_cases.append(TestCase(action, "ui_action", "UI 액션"))
    
    # 3. 혼합 시나리오 테스트 (25개)
    mixed_cases = [
        ("개발자 채용 트렌드 알려주고 채용 페이지 열어줘", "ui_action", "혼합"),
        ("이력서 작성 팁 알려주고 이력서 등록 페이지로 이동해줘", "ui_action", "혼합"),
        ("면접 준비 방법 설명해주고 면접 일정 페이지 열어줘", "ui_action", "혼합"),
        ("포트폴리오 분석해주고 결과 페이지 보여줘", "ui_action", "혼합"),
        ("채용 공고 작성 방법 알려주고 등록 페이지로 이동", "ui_action", "혼합"),
        ("개발자 연봉 정보 알려주고 통계 페이지 열어줘", "ui_action", "혼합"),
        ("기술 면접 팁 알려주고 면접 관리 페이지로 이동", "ui_action", "혼합"),
        ("채용 시장 분석해주고 대시보드 보여줘", "ui_action", "혼합"),
        ("코딩 테스트 준비 방법 알려주고 시험 페이지 열어줘", "ui_action", "혼합"),
        ("이력서 피드백 해주고 수정 페이지로 이동", "ui_action", "혼합"),
        ("개발자 커리어 패스 설명해주고 로드맵 페이지 보여줘", "ui_action", "혼합"),
        ("면접 질문 예시 알려주고 질문 관리 페이지 열어줘", "ui_action", "혼합"),
        ("포트폴리오 작성법 알려주고 등록 화면으로 이동", "ui_action", "혼합"),
        ("채용 성공 사례 알려주고 사례 페이지 보여줘", "ui_action", "혼합"),
        ("개발자 역량 평가 방법 설명하고 평가 페이지 열어줘", "ui_action", "혼합"),
        ("채용 프로세스 설명해주고 설정 페이지로 이동", "ui_action", "혼합"),
        ("이력서 분석 결과 설명하고 상세 페이지 보여줘", "ui_action", "혼합"),
        ("면접 피드백 방법 알려주고 피드백 페이지 열어줘", "ui_action", "혼합"),
        ("채용 성과 분석해주고 리포트 페이지로 이동", "ui_action", "혼합"),
        ("개발자 교육 과정 설명하고 교육 페이지 보여줘", "ui_action", "혼합"),
        ("채용 예산 관리 방법 알려주고 예산 페이지 열어줘", "ui_action", "혼합"),
        ("인재 추천 기준 설명하고 추천 페이지로 이동", "ui_action", "혼합"),
        ("면접 스케줄링 방법 알려주고 캘린더 보여줘", "ui_action", "혼합"),
        ("채용 공고 최적화 방법 설명하고 수정 페이지 열어줘", "ui_action", "혼합"),
        ("개발자 평가 기준 설명하고 평가표 페이지로 이동", "ui_action", "혼합")
    ]
    
    for input_text, expected, category in mixed_cases:
        test_cases.append(TestCase(input_text, expected, category))
    
    # 4. 엣지 케이스 테스트 (25개)
    edge_cases = [
        ("", "chat", "엣지 케이스"),
        ("?", "info_request", "엣지 케이스"),
        ("!@#$%", "chat", "엣지 케이스"),
        ("123456", "chat", "엣지 케이스"),
        ("ㅋㅋㅋㅋ", "chat", "엣지 케이스"),
        ("페이지", "chat", "엣지 케이스"),
        ("알려줘", "info_request", "엣지 케이스"),
        ("열어줘", "ui_action", "엣지 케이스"),
        ("이동해줘", "ui_action", "엣지 케이스"),
        ("보여줘", "ui_action", "엣지 케이스"),
        ("설명해", "info_request", "엣지 케이스"),
        ("어떻게", "info_request", "엣지 케이스"),
        ("왜", "info_request", "엣지 케이스"),
        ("뭐야", "info_request", "엣지 케이스"),
        ("언제", "info_request", "엣지 케이스"),
        ("어디로", "info_request", "엣지 케이스"),
        ("누구", "info_request", "엣지 케이스"),
        ("그래", "chat", "엣지 케이스"),
        ("응", "chat", "엣지 케이스"),
        ("아니", "chat", "엣지 케이스"),
        ("네", "chat", "엣지 케이스"),
        ("ㅇㅇ", "chat", "엣지 케이스"),
        ("ㄴㄴ", "chat", "엣지 케이스"),
        ("페이지 열어줘 알려줘", "ui_action", "엣지 케이스"),
        ("설명해주고 이동해줘", "ui_action", "엣지 케이스")
    ]
    
    for input_text, expected, category in edge_cases:
        test_cases.append(TestCase(input_text, expected, category))
    
    return test_cases

async def run_tests():
    """테스트 실행"""
    agent = LangGraphAgentSystem()
    test_cases = generate_test_cases()
    results = []
    
    print(f"\n총 {len(test_cases)}개의 테스트 케이스 실행\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n테스트 케이스 {i}/{len(test_cases)}")
        print(f"입력: {test_case.input}")
        print(f"예상 의도: {test_case.expected_intent}")
        print(f"카테고리: {test_case.category}")
        
        try:
            response = await agent.process_request(test_case.input)
            actual_intent = response.get("intent", "unknown")
            success = actual_intent == test_case.expected_intent
            
            result = {
                "test_case": str(test_case),
                "actual_intent": actual_intent,
                "success": success,
                "response": response
            }
            
            results.append(result)
            
            print(f"실제 의도: {actual_intent}")
            print(f"결과: {'성공' if success else '실패'}")
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            results.append({
                "test_case": str(test_case),
                "error": str(e),
                "success": False
            })
    
    return results

def analyze_results(results: List[Dict[str, Any]]):
    """테스트 결과 분석"""
    total = len(results)
    successful = sum(1 for r in results if r.get("success", False))
    failed = total - successful
    
    categories = {}
    for result in results:
        test_case = result["test_case"]
        category = test_case.split(", Category: ")[1]
        
        if category not in categories:
            categories[category] = {"total": 0, "success": 0, "failed": 0}
        
        categories[category]["total"] += 1
        if result.get("success", False):
            categories[category]["success"] += 1
        else:
            categories[category]["failed"] += 1
    
    print("\n=== 테스트 결과 분석 ===")
    print(f"\n전체 테스트: {total}개")
    print(f"성공: {successful}개 ({successful/total*100:.1f}%)")
    print(f"실패: {failed}개 ({failed/total*100:.1f}%)")
    
    print("\n카테고리별 결과:")
    for category, stats in categories.items():
        success_rate = stats["success"] / stats["total"] * 100
        print(f"\n{category}:")
        print(f"  총 테스트: {stats['total']}개")
        print(f"  성공: {stats['success']}개 ({success_rate:.1f}%)")
        print(f"  실패: {stats['failed']}개 ({100-success_rate:.1f}%)")

if __name__ == "__main__":
    results = asyncio.run(run_tests())
    analyze_results(results)
