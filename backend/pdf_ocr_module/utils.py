from __future__ import annotations

import json
import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import Any
import hashlib

import pytesseract
from PIL import Image
import numpy as np
import cv2

from pdf_ocr_module.config import Settings


def ensure_directories(settings: Settings) -> None:
    for directory in [
        settings.data_dir,
        settings.uploads_dir,
        settings.images_dir,
        settings.results_dir,
        Path(settings.chroma_persist_dir),
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def slugify_filename(filename: str) -> str:
    name, dot, ext = filename.rpartition(".")
    base = name or filename
    base = base.strip().lower()
    base = re.sub(r"[^a-z0-9\-_.]+", "-", base)
    base = re.sub(r"-+", "-", base).strip("-._")
    return f"{base}{dot}{ext}" if ext else base


def unique_stem(path: Path) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
    return f"{path.stem}-{timestamp}"


def save_upload_file(file_obj: Any, settings: Settings) -> Path:
    """FastAPI UploadFile 또는 file-like 객체를 저장.

    Args:
        file_obj: UploadFile과 유사한 객체 (.filename, .file 속성 필요)
        settings: 설정
    Returns:
        저장된 파일 경로
    """
    original_name: str = getattr(file_obj, "filename", "uploaded.pdf")
    safe_name = slugify_filename(original_name)
    destination = settings.uploads_dir / safe_name

    # 동일 파일명이 있으면 유니크한 이름으로 저장
    if destination.exists():
        destination = settings.uploads_dir / f"{unique_stem(destination)}.pdf"

    with open(destination, "wb") as out_file:
        # FastAPI UploadFile
        if hasattr(file_obj, "file"):
            while True:
                chunk = file_obj.file.read(1024 * 1024)
                if not chunk:
                    break
                out_file.write(chunk)
        else:
            # 일반 파일 객체
            out_file.write(file_obj.read())

    return destination


def _default_json_serializer(obj: Any) -> Any:
    """Serialize non-JSON-native types.

    - datetime/date -> ISO 8601 string
    - Path -> str path
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=_default_json_serializer)


def set_optional_binaries(settings: Settings) -> None:
    if settings.tesseract_cmd:
        os.environ["TESSERACT_CMD"] = settings.tesseract_cmd


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def correct_orientation_with_osd(image):
    """
    Tesseract OSD를 사용하여 이미지의 회전을 자동으로 교정합니다.
    
    Args:
        image: PIL Image 객체 또는 numpy array
        
    Returns:
        PIL Image: 교정된 이미지
    """
    try:
        # numpy array를 PIL Image로 변환 (필요한 경우)
        if isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
        else:
            pil_image = image
        
        # Tesseract OSD로 회전 각도와 신뢰도 파싱
        osd_data = pytesseract.image_to_osd(pil_image, lang="osd", config="--psm 0")
        
        # OSD 결과 파싱
        angle = None
        confidence = None
        
        for line in osd_data.split('\n'):
            if 'Rotate:' in line:
                angle = int(line.split(':')[1].strip())
            elif 'Confidence:' in line:
                confidence = float(line.split(':')[1].strip())
        
        print(f"[OSD] 감지된 회전 각도: {angle}도, 신뢰도: {confidence}%")
        
        # 조건 검사
        # ① angle이 {0,90,180,270}에 속하지 않으면 0으로 간주
        if angle not in [0, 90, 180, 270]:
            print(f"[OSD] 유효하지 않은 각도 {angle}도, 0도로 간주")
            angle = 0
        
        # ③ confidence < 10이면 회전하지 않음
        if confidence < 10:
            print(f"[OSD] 신뢰도가 낮음 ({confidence}%), 회전하지 않음")
            return pil_image
        
        # ④ angle==0이면 그대로 저장
        if angle == 0:
            print(f"[OSD] 회전 불필요 (0도)")
            return pil_image
        
        # ⑤ angle이 90/180/270일 때만 회전 적용
        if angle in [90, 180, 270]:
            print(f"[OSD] 이미지를 {angle}도 회전하여 교정")
            corrected_image = pil_image.rotate(-angle, expand=True)
            return corrected_image
        
        return pil_image
        
    except Exception as e:
        print(f"[OSD] 회전 교정 중 오류 발생: {e}")
        # 오류 발생 시 원본 이미지 반환
        if isinstance(image, np.ndarray):
            return Image.fromarray(image)
        return image




