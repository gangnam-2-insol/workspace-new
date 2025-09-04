"""
PDF OCR Module Utils
===================

PDF OCR 모듈의 유틸리티 패키지입니다.
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from .config import Settings
from .pdf_converter import PDFConverter
from .storage import MongoStorage, VectorStorage

def ensure_directories(settings: Settings) -> None:
    """필요한 디렉토리들을 생성합니다."""
    directories = [
        settings.data_dir,
        settings.uploads_dir,
        settings.images_dir,
        settings.results_dir,
        settings.thumbnails_dir,
        settings.output_dir,
        settings.temp_dir,
        settings.tesseract_data_path
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def write_json(data: Dict[str, Any], file_path: Path) -> None:
    """JSON 파일로 데이터를 저장합니다."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def file_sha256(file_path: Path) -> str:
    """파일의 SHA256 해시를 계산합니다."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

__all__ = [
    'Settings',
    'MongoStorage',
    'VectorStorage',
    'PDFConverter',
    'ensure_directories',
    'write_json',
    'file_sha256'
]
