#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_create_single_applicant():
    url = "http://localhost:8000/api/sample/create-single-applicant"
    data = {
        "name": "테스트 지원자",
        "email": "test@example.com"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API 호출 성공!")
        else:
            print("❌ API 호출 실패!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_create_single_applicant()
