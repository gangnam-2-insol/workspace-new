import requests
import json

def check_job_postings():
    """현재 채용공고 목록 확인"""
    try:
        response = requests.get('http://localhost:8000/api/job-postings')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            job_postings = response.json()
            print(f"총 채용공고 수: {len(job_postings)}")
            
            if job_postings:
                print("\n=== 채용공고 목록 ===")
                for i, job in enumerate(job_postings, 1):
                    print(f"\n{i}. 채용공고:")
                    print(f"   ID: {job.get('_id')}")
                    print(f"   제목: {job.get('title')}")
                    print(f"   부서: {job.get('department')}")
                    print(f"   직무: {job.get('position')}")
                    print(f"   경력: {job.get('experience')}")
                    print(f"   상태: {job.get('status')}")
            else:
                print("등록된 채용공고가 없습니다.")
        else:
            print(f"API 호출 실패: {response.text}")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    check_job_postings()