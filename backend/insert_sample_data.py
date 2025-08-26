import json
import requests
import time

def insert_sample_data_batch():
    """이미 생성된 샘플 데이터를 배치로 나누어 삽입"""
    
    # JSON 파일에서 데이터 로드
    try:
        with open('backend/sample_applicants.json', 'r', encoding='utf-8') as f:
            applicants = json.load(f)
        print(f"JSON 파일에서 {len(applicants)}개 지원자 데이터를 로드했습니다.")
    except FileNotFoundError:
        print("sample_applicants.json 파일을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"JSON 파일 로드 오류: {e}")
        return
    
    print("=== 지원자 데이터 DB 삽입 시작 ===")
    
    success_count = 0
    fail_count = 0
    batch_size = 10  # 작은 배치 크기로 설정
    
    for i in range(0, len(applicants), batch_size):
        batch = applicants[i:i + batch_size]
        print(f"\n배치 {i//batch_size + 1} 처리 중... ({i+1}-{min(i+batch_size, len(applicants))})")
        
        for j, applicant in enumerate(batch):
            try:
                response = requests.post(
                    'http://localhost:8000/api/applicants',
                    json=applicant,
                    timeout=10
                )
                
                if response.status_code == 201:
                    success_count += 1
                    print(f"  ✅ {i+j+1}: {applicant['name']} - 성공")
                else:
                    fail_count += 1
                    print(f"  ❌ {i+j+1}: {applicant['name']} - 실패 ({response.status_code})")
                    
            except Exception as e:
                fail_count += 1
                print(f"  ❌ {i+j+1}: {applicant['name']} - 오류 ({str(e)})")
            
            # 요청 간 간격 추가
            time.sleep(0.1)
        
        # 배치 간 간격 추가
        time.sleep(1)
        print(f"배치 완료: 성공 {success_count}, 실패 {fail_count}")
    
    print(f"\n=== 완료 ===")
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print(f"총 처리: {len(applicants)}개")
    
    # 최종 확인
    try:
        response = requests.get('http://localhost:8000/api/applicants?skip=0&limit=1000')
        if response.status_code == 200:
            data = response.json()
            actual_count = len(data.get('applicants', []))
            print(f"DB에 실제 저장된 지원자 수: {actual_count}개")
        else:
            print("DB 확인 실패")
    except Exception as e:
        print(f"DB 확인 오류: {e}")

if __name__ == "__main__":
    insert_sample_data_batch()
