#!/usr/bin/env python3
"""
중복된 document_rejected 템플릿을 제거하는 스크립트
"""
from pymongo import MongoClient
import json

def cleanup_duplicate_templates():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['hireme']

        print("🧹 중복 템플릿 정리 시작...")

        # 현재 메일 템플릿 확인
        mail_templates = db.mail_templates.find_one({"_id": "default"})
        if not mail_templates:
            print("❌ 메일 템플릿을 찾을 수 없습니다.")
            return

        print("📧 현재 템플릿 구조:")
        for key in mail_templates.keys():
            if key not in ['_id', 'created_at', 'updated_at']:
                print(f"  - {key}")

        # document_rejected 제거
        if 'document_rejected' in mail_templates:
            result = db.mail_templates.update_one(
                {"_id": "default"},
                {"$unset": {"document_rejected": ""}}
            )
            print(f"✅ document_rejected 템플릿 제거 완료: {result.modified_count}개 수정")
        else:
            print("ℹ️ document_rejected 템플릿이 이미 존재하지 않습니다.")

        # 정리 후 템플릿 구조 확인
        updated_templates = db.mail_templates.find_one({"_id": "default"})
        print("\n📧 정리 후 템플릿 구조:")
        for key in updated_templates.keys():
            if key not in ['_id', 'created_at', 'updated_at']:
                print(f"  - {key}")

        client.close()
        print("\n✅ 중복 템플릿 정리가 완료되었습니다.")

    except Exception as e:
        print(f"❌ 정리 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    cleanup_duplicate_templates()

