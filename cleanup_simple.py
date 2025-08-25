#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 정리 작업 스크립트
"""

import os
import shutil
from pathlib import Path


def cleanup_check_files():
    """체크 파일들을 정리"""
    print("🧹 체크 파일 정리 중...")

    # 체크 파일들을 backup 폴더로 이동
    backup_dir = Path("backup_files/check_scripts")
    backup_dir.mkdir(parents=True, exist_ok=True)

    check_files = list(Path(".").glob("check_*.py"))

    for file in check_files:
        if file.name != "check_project_status.py":  # 메인 체크 파일은 유지
            try:
                shutil.move(str(file), str(backup_dir / file.name))
                print(f"  ✅ {file.name} -> backup_files/check_scripts/")
            except Exception as e:
                print(f"  ❌ {file.name} 이동 실패: {e}")

    print(f"  📊 총 {len(check_files)}개 파일 처리 완료")
    print()

def cleanup_mj_files():
    """_mj.py 파일들을 정리"""
    print("🧹 _mj.py 파일 정리 중...")

    backup_dir = Path("backup_files/mj_files")
    backup_dir.mkdir(parents=True, exist_ok=True)

    mj_files = list(Path(".").rglob("*_mj.py"))

    for file in mj_files:
        try:
            # 상대 경로 유지
            relative_path = file.relative_to(Path("."))
            backup_path = backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(file), str(backup_path))
            print(f"  ✅ {relative_path} -> backup_files/mj_files/")
        except Exception as e:
            print(f"  ❌ {file.name} 이동 실패: {e}")

    print(f"  📊 총 {len(mj_files)}개 파일 처리 완료")
    print()

def create_simple_readme():
    """간단한 README 생성"""
    print("📝 간단한 README 생성 중...")

    readme_content = """# HireMe - AI 기반 스마트 채용 플랫폼

## 🚀 빠른 시작

### 1. 환경 설정
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
MONGODB_URI=mongodb://localhost:27017
```

### 3. 서버 실행
```bash
# 백엔드 서버
cd backend
uvicorn main:app --reload --port 8000

# 프론트엔드 서버
cd frontend
npm start
```

## 📁 프로젝트 구조

```
backend/
├── modules/           # 모듈화된 서비스들
│   ├── core/services/ # 핵심 서비스
│   ├── ai/services/   # AI 관련 서비스
│   ├── data/services/ # 데이터 관련 서비스
│   └── shared/        # 공통 모델 및 서비스
├── routers/           # API 라우터들
├── models/            # 데이터 모델들
└── utils/             # 유틸리티 함수들

frontend/
├── src/
│   ├── components/    # React 컴포넌트들
│   ├── pages/         # 페이지 컴포넌트들
│   └── services/      # API 서비스들
```

## 🔧 주요 기능

- 🤖 AI 기반 지원자 분석
- 📄 이력서/자기소개서 분석
- 🔍 하이브리드 검색
- 📊 대시보드 및 통계
- 👥 지원자 관리

## 📞 지원

문제가 있으시면 이슈를 등록해주세요.
"""

    with open("README_SIMPLE.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("  ✅ README_SIMPLE.md 생성 완료")
    print()

def main():
    """메인 함수"""
    print("=" * 50)
    print("🧹 간단한 정리 작업 시작")
    print("=" * 50)
    print()

    # 1. 체크 파일 정리
    cleanup_check_files()

    # 2. _mj.py 파일 정리
    cleanup_mj_files()

    # 3. 간단한 README 생성
    create_simple_readme()

    print("=" * 50)
    print("✅ 간단한 정리 작업 완료!")
    print("📁 backup_files/ 폴더에서 백업된 파일들을 확인할 수 있습니다.")
    print("=" * 50)

if __name__ == "__main__":
    main()
