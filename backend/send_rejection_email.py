#!/usr/bin/env python3
"""
kyunghol87@naver.com에게 불합격 통지 메일을 보내는 스크립트
"""
import asyncio
import aiohttp
import json

async def send_rejection_email():
    url = "http://localhost:8000/api/send-individual-mail"
    email_data = {
        "recipient": "kyunghol87@naver.com",
        "template": "불합격 통지",
        "input_text": "kyunghol87@naver.com에게 불합격 메일 보내줘"
    }

    print(f"📧 불합격 통지 메일 발송 시작")
    print(f"📧 수신자: {email_data['recipient']}")
    print(f"📧 템플릿: {email_data['template']}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=email_data) as response:
                print(f"📧 응답 상태 코드: {response.status}")

                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 메일 발송 성공!")
                    print(f"📧 응답 내용: {json.dumps(result, ensure_ascii=False, indent=2)}")
                else:
                    error_text = await response.text()
                    print(f"❌ 메일 발송 실패: {error_text}")

    except Exception as e:
        print(f"❌ 메일 발송 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🚀 불합격 통지 메일 발송을 시작합니다...")
    asyncio.run(send_rejection_email())

