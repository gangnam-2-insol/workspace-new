import requests

# 현재 인재상 목록 조회
response = requests.get('http://localhost:8000/api/company-culture/')
cultures = response.json()

print(f'현재 인재상 개수: {len(cultures)}개')
print()

# 첫 번째 인재상 정보 출력
if cultures:
    first_culture = cultures[0]
    print(f'첫 번째 인재상: {first_culture["name"]}')
    print(f'ID: {first_culture["id"]}')
    print(f'기본 인재상: {first_culture["is_default"]}')
    print()

    # 삭제 테스트
    culture_id = first_culture["id"]
    print(f'삭제 테스트 시작: {culture_id}')

    delete_response = requests.delete(f'http://localhost:8000/api/company-culture/{culture_id}')

    print(f'삭제 응답 상태: {delete_response.status_code}')
    print(f'삭제 응답 내용: {delete_response.text}')

    # 삭제 후 다시 조회
    response_after = requests.get('http://localhost:8000/api/company-culture/')
    cultures_after = response_after.json()

    print(f'삭제 후 인재상 개수: {len(cultures_after)}개')
else:
    print('인재상이 없습니다.')
