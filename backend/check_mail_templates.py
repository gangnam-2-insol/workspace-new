#!/usr/bin/env python3
"""
기존 메일 템플릿 구조를 확인하는 스크립트
"""

from pymongo import MongoClient

def check_mail_templates():
    """메일 템플릿 구조를 확인합니다."""

    try:
        # MongoDB 연결
        client = MongoClient('mongodb://localhost:27017/')
        db = client['hireme']

        print("📧 메일 설정 확인:")
        mail_settings = db.mail_settings.find_one({"_id": "default"})
        if mail_settings:
            print(f"  발신자: {mail_settings.get('senderName', 'N/A')}")
            print(f"  이메일: {mail_settings.get('senderEmail', 'N/A')}")
            print(f"  SMTP 서버: {mail_settings.get('smtpServer', 'N/A')}:{mail_settings.get('smtpPort', 'N/A')}")

        print("\n📧 메일 템플릿 확인:")
        mail_templates = db.mail_templates.find_one({"_id": "default"})
        if mail_templates:
            print("  전체 템플릿 데이터:")
            import json
            print(json.dumps(mail_templates, indent=2, ensure_ascii=False, default=str))

            print("\n  템플릿 키 목록:")
            for key in mail_templates.keys():
                if key != "_id":
                    print(f"    - {key}")

            print("\n  rejected 템플릿 상세:")
            rejected = mail_templates.get("rejected", {})
            if isinstance(rejected, dict):
                print(f"    제목: {rejected.get('subject', 'N/A')}")
                print(f"    내용: {rejected.get('content', 'N/A')}")
            else:
                print(f"    타입: {type(rejected)}")
                print(f"    값: {rejected}")

        else:
            print("❌ 메일 템플릿이 존재하지 않습니다.")

        client.close()

    except Exception as e:
        print(f"❌ 확인 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    check_mail_templates()

