import requests
import json

def test_frontend_recruitment():
    url = "http://localhost:8000/api/langgraph/agent"
    
    payload = {
        "message": "프론트엔드 개발자 모집 공고입니다. React와 Typescript를 활용한 웹 애플리케이션 개발 경험이 2년 이상인 분을 우대하며, 사용자 경험(UX) 개선에 관심이 많고 세심한 UI 구현 능력을 갖춘 분을 찾고 있습니다. 애자일(Agile) 개발 환경에 적응력이 좋고, 팀 내 협업 및 코드 리뷰에 적극적으로 참여할 수 있는 분이면 더욱 좋습니다. 자바스크립트 라이브러리 및 최신 트렌드에 대한 이해도가 높은 지원자를 환영합니다.",
        "conversation_history": [],
        "session_id": "test-session"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🌐 프론트엔드 개발자 채용공고 테스트 시작...")
        print(f"📤 요청 URL: {url}")
        print(f"📤 요청 데이터: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"📥 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 성공! 응답 데이터:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 추출된 필드 확인
            if 'extracted_fields' in result:
                print(f"🔍 추출된 필드: {result['extracted_fields']}")
                print(f"🔍 필드 개수: {len(result['extracted_fields'])}개")
                
                # 각 필드별 상세 확인
                for key, value in result['extracted_fields'].items():
                    print(f"  - {key}: {value}")
            else:
                print("⚠️ 추출된 필드가 없습니다.")
                
        else:
            print(f"❌ 오류! 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"💥 예외 발생: {e}")

if __name__ == "__main__":
    test_frontend_recruitment()
