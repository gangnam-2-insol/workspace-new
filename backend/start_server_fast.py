"""
최적화된 FastAPI 서버 시작 스크립트
개발 환경에서 빠른 시작을 위한 설정
"""
import os
import sys

import uvicorn
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Python 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 최적화된 백엔드 서버 시작 중...")
    print("📊 최적화 설정:")
    print("  - 로그 레벨: WARNING")
    print("  - 액세스 로그: 비활성화")
    print("  - 소스맵: 비활성화")
    print("  - 워커: 1개")
    print("  - 루프: asyncio")
    print("")

    # 최적화된 설정으로 서버 시작
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."],
        log_level="warning",      # 로그 레벨 낮춤
        access_log=False,         # 액세스 로그 비활성화
        workers=1,               # 단일 워커
        loop="asyncio",          # asyncio 루프 사용
        reload_excludes=[        # 리로드 제외 파일들
            "*.log",
            "*.pyc",
            "__pycache__",
            "*.cache",
            "node_modules"
        ]
    )
