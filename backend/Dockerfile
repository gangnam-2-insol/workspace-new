FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    pkg-config \
    curl \
    wget \
    libasound2-dev \
    portaudio19-dev \
    libopencv-dev \
    tesseract-ocr \
    tesseract-ocr-kor \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 (프로젝트 루트에서)
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사 (backend 폴더만)
COPY ./backend .

# 포트 노출
EXPOSE 8000

# 개발 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]