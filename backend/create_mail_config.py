#!/usr/bin/env python3
"""
메일 설정과 템플릿을 MongoDB에 생성하는 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import db

async def create_mail_config():
    """메일 설정과 템플릿을 생성합니다."""

    print("📧 메일 설정과 템플릿을 생성합니다...")

    # 메일 설정 생성
    mail_settings = {
        "_id": "default",
        "senderName": "AI 채용 관리 시스템",
        "senderEmail": "your-email@gmail.com",  # 실제 Gmail 주소로 변경 필요
        "senderPassword": "your-app-password",  # Gmail 앱 비밀번호로 변경 필요
        "smtpServer": "smtp.gmail.com",
        "smtpPort": 587,
        "useTLS": True
    }

    # 메일 템플릿 생성
    mail_templates = {
        "_id": "default",
        "rejected": {
            "subject": "[AI 채용 관리 시스템] 지원 결과 안내",
            "content": """안녕하세요, {applicant_name}님

{company_name}의 {job_posting_title} {position} 지원에 대해 안내드립니다.

안타깝게도 이번 지원에서는 합격하지 못했습니다.
더 나은 기회가 있을 때 다시 지원해 주시기 바랍니다.

감사합니다.

{company_name} 인사팀"""
        },
        "passed": {
            "subject": "[AI 채용 관리 시스템] 합격 안내",
            "content": """안녕하세요, {applicant_name}님

{company_name}의 {job_posting_title} {position} 지원에 대해 안내드립니다.

축하합니다! 이번 지원에서 합격하셨습니다.
추가 안내사항은 별도로 연락드리겠습니다.

감사합니다.

{company_name} 인사팀"""
        },
        "interview": {
            "subject": "[AI 채용 관리 시스템] 면접 안내",
            "content": """안녕하세요, {applicant_name}님

{company_name}의 {job_posting_title} {position} 지원에 대해 안내드립니다.

1차 서류 전형을 통과하셨습니다.
면접 일정은 별도로 안내드리겠습니다.

감사합니다.

{company_name} 인사팀"""
        }
    }

    try:
        # 기존 설정 삭제 (있다면)
        await db.mail_settings.delete_one({"_id": "default"})
        await db.mail_templates.delete_one({"_id": "default"})

        # 새 설정 삽입
        await db.mail_settings.insert_one(mail_settings)
        await db.mail_templates.insert_one(mail_templates)

        print("✅ 메일 설정과 템플릿이 성공적으로 생성되었습니다.")
        print("\n📧 메일 설정:")
        print(f"  발신자: {mail_settings['senderName']}")
        print(f"  이메일: {mail_settings['senderEmail']}")
        print(f"  SMTP 서버: {mail_settings['smtpServer']}:{mail_settings['smtpPort']}")

        print("\n📧 메일 템플릿:")
        for template_name, template_data in mail_templates.items():
            if template_name != "_id":
                print(f"  {template_name}: {template_data['subject']}")

        print("\n⚠️  주의사항:")
        print("  - Gmail을 사용하려면 '앱 비밀번호'를 생성해야 합니다.")
        print("  - 2단계 인증을 활성화하고 앱 비밀번호를 생성하세요.")
        print("  - create_mail_config.py 파일에서 senderEmail과 senderPassword를 실제 값으로 변경하세요.")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

    return True

async def check_mail_config():
    """현재 메일 설정과 템플릿을 확인합니다."""

    print("📧 현재 메일 설정과 템플릿을 확인합니다...")

    try:
        # 메일 설정 확인
        mail_settings = await db.mail_settings.find_one({"_id": "default"})
        if mail_settings:
            print("✅ 메일 설정이 존재합니다:")
            print(f"  발신자: {mail_settings.get('senderName', 'N/A')}")
            print(f"  이메일: {mail_settings.get('senderEmail', 'N/A')}")
            print(f"  SMTP 서버: {mail_settings.get('smtpServer', 'N/A')}:{mail_settings.get('smtpPort', 'N/A')}")
        else:
            print("❌ 메일 설정이 존재하지 않습니다.")

        # 메일 템플릿 확인
        mail_templates = await db.mail_templates.find_one({"_id": "default"})
        if mail_templates:
            print("✅ 메일 템플릿이 존재합니다:")
            for template_name, template_data in mail_templates.items():
                if template_name != "_id":
                    print(f"  {template_name}: {template_data.get('subject', 'N/A')}")
        else:
            print("❌ 메일 템플릿이 존재하지 않습니다.")

    except Exception as e:
        print(f"❌ 확인 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🚀 메일 설정 생성 스크립트를 시작합니다...")

    # 현재 설정 확인
    asyncio.run(check_mail_config())

    print("\n" + "="*50)

    # 새 설정 생성 여부 확인
    response = input("새로운 메일 설정과 템플릿을 생성하시겠습니까? (y/N): ").strip().lower()

    if response in ['y', 'yes']:
        success = asyncio.run(create_mail_config())
        if success:
            print("\n✅ 설정이 완료되었습니다. 이제 메일 발송을 테스트할 수 있습니다.")
        else:
            print("\n❌ 설정 생성에 실패했습니다.")
    else:
        print("설정 생성을 취소했습니다.")

