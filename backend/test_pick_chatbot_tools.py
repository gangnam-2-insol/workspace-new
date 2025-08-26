#!/usr/bin/env python3
"""
픽톡(Pick Chatbot) 새로 추가된 툴들 테스트 스크립트
"""

import asyncio
import json
from datetime import datetime

from routers.pick_chatbot import AgentSystem, ToolExecutor


async def test_job_posting_tool():
    """채용공고 툴 테스트"""
    print("=" * 50)
    print("📝 채용공고 툴 테스트")
    print("=" * 50)

    tool_executor = ToolExecutor()

    # 1. 채용공고 생성 테스트
    print("\n1. 채용공고 생성 테스트")
    job_data = {
        "title": "테스트 채용공고",
        "position": "백엔드 개발자",
        "company": "테스트 회사",
        "description": "테스트용 채용공고입니다.",
        "requirements": ["Python", "FastAPI", "MongoDB"],
        "salary": "3000-5000만원"
    }

    result = await tool_executor.job_posting_tool("create", job_data=job_data)
    print(f"생성 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

    if "job_id" in result:
        job_id = result["job_id"]

        # 2. 채용공고 조회 테스트
        print("\n2. 채용공고 조회 테스트")
        result = await tool_executor.job_posting_tool("read", job_id=job_id)
        print(f"조회 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 3. 채용공고 수정 테스트
        print("\n3. 채용공고 수정 테스트")
        update_data = {
            "title": "수정된 테스트 채용공고",
            "salary": "3500-5500만원"
        }
        result = await tool_executor.job_posting_tool("update", job_id=job_id, update_data=update_data)
        print(f"수정 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 4. 채용공고 발행 테스트
        print("\n4. 채용공고 발행 테스트")
        result = await tool_executor.job_posting_tool("publish", job_id=job_id)
        print(f"발행 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 5. 채용공고 삭제 테스트
        print("\n5. 채용공고 삭제 테스트")
        result = await tool_executor.job_posting_tool("delete", job_id=job_id)
        print(f"삭제 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

    # 6. 전체 목록 조회 테스트
    print("\n6. 전체 목록 조회 테스트")
    result = await tool_executor.job_posting_tool("read")
    print(f"목록 조회 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

async def test_applicant_tool():
    """지원자 툴 테스트"""
    print("\n" + "=" * 50)
    print("👥 지원자 툴 테스트")
    print("=" * 50)

    tool_executor = ToolExecutor()

    # 1. 지원자 생성 테스트
    print("\n1. 지원자 생성 테스트")
    applicant_data = {
        "name": "테스트 지원자",
        "email": "test@example.com",
        "phone": "010-1234-5678",
        "position": "백엔드 개발자",
        "resume_url": "https://example.com/resume.pdf",
        "cover_letter": "테스트 자기소개서입니다.",
        "job_posting_title": "테스트 채용공고"
    }

    result = await tool_executor.applicant_tool("create", applicant_data=applicant_data)
    print(f"생성 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

    if "applicant_id" in result:
        applicant_id = result["applicant_id"]

        # 2. 지원자 조회 테스트
        print("\n2. 지원자 조회 테스트")
        result = await tool_executor.applicant_tool("read", applicant_id=applicant_id)
        print(f"조회 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 3. 지원자 수정 테스트
        print("\n3. 지원자 수정 테스트")
        update_data = {
            "name": "수정된 테스트 지원자",
            "phone": "010-9876-5432"
        }
        result = await tool_executor.applicant_tool("update", applicant_id=applicant_id, update_data=update_data)
        print(f"수정 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 4. 지원자 상태 변경 테스트
        print("\n4. 지원자 상태 변경 테스트")
        result = await tool_executor.applicant_tool("update_status", applicant_id=applicant_id, status="interview")
        print(f"상태 변경 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 5. 지원자 삭제 테스트
        print("\n5. 지원자 삭제 테스트")
        result = await tool_executor.applicant_tool("delete", applicant_id=applicant_id)
        print(f"삭제 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

    # 6. 지원자 통계 테스트
    print("\n6. 지원자 통계 테스트")
    result = await tool_executor.applicant_tool("get_stats")
    print(f"통계 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

async def test_mail_tool():
    """메일 툴 테스트"""
    print("\n" + "=" * 50)
    print("📧 메일 툴 테스트")
    print("=" * 50)

    tool_executor = ToolExecutor()

    # 1. 메일 템플릿 조회 테스트
    print("\n1. 메일 템플릿 조회 테스트")
    result = await tool_executor.mail_tool("get_templates")
    print(f"템플릿 조회 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

    # 2. 메일 템플릿 생성 테스트
    print("\n2. 메일 템플릿 생성 테스트")
    template_data = {
        "type": "interview",
        "subject": "면접 안내",
        "content": "안녕하세요 {applicant_name}님,\n\n{company_name}의 {position} 포지션 면접 안내드립니다.\n\n면접 일시: {interview_date}\n면접 장소: {interview_location}\n\n감사합니다."
    }
    result = await tool_executor.mail_tool("create_template", template_data=template_data)
    print(f"템플릿 생성 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

async def test_intent_classification():
    """의도 분류 테스트"""
    print("\n" + "=" * 50)
    print("🎯 의도 분류 테스트")
    print("=" * 50)

    agent_system = AgentSystem()

    test_inputs = [
        "채용공고 목록을 보여주세요",
        "새로운 지원자를 등록해주세요",
        "지원자 통계를 보여주세요",
        "메일 템플릿을 만들어주세요",
        "채용공고를 수정해주세요",
        "지원자 상태를 변경해주세요"
    ]

    for user_input in test_inputs:
        print(f"\n입력: {user_input}")
        intent = agent_system.classify_intent(user_input)
        print(f"의도 분류 결과: {json.dumps(intent, ensure_ascii=False, indent=2)}")

async def main():
    """메인 테스트 함수"""
    print("🚀 픽톡(Pick Chatbot) 새로 추가된 툴들 테스트 시작")
    print(f"테스트 시작 시간: {datetime.now()}")

    try:
        # 의도 분류 테스트
        await test_intent_classification()

        # 채용공고 툴 테스트
        await test_job_posting_tool()

        # 지원자 툴 테스트
        await test_applicant_tool()

        # 메일 툴 테스트
        await test_mail_tool()

        print("\n" + "=" * 50)
        print("✅ 모든 테스트 완료!")
        print(f"테스트 종료 시간: {datetime.now()}")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
