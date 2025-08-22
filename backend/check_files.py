import json
from pathlib import Path

def check_files():
    results_dir = Path('pdf_ocr_data/results')
    files = list(results_dir.glob('*.json'))
    
    print(f'총 첨부파일 수: {len(files)}')
    print()
    
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                mongo_id = data.get('mongo_id', 'ID 없음')
                name = data.get('fields', {}).get('names', ['이름 없음'])[0] if data.get('fields', {}).get('names') else '이름 없음'
                print(f'파일: {f.name}')
                print(f'  - MongoDB ID: {mongo_id}')
                print(f'  - 이름: {name}')
                print(f'  - 이메일: {data.get("fields", {}).get("emails", ["없음"])[0] if data.get("fields", {}).get("emails") else "없음"}')
                print(f'  - 직무: {data.get("fields", {}).get("positions", ["없음"])[0] if data.get("fields", {}).get("positions") else "없음"}')
                print()
        except Exception as e:
            print(f'- {f.name}: 오류 - {e}')
            print()

if __name__ == "__main__":
    check_files()
