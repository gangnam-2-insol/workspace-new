from __future__ import annotations

import json
import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import Any
import hashlib

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
    """Tesseract OSD를 사용하여 이미지 방향을 자동으로 교정합니다."""
    try:
        import pytesseract
        from PIL import Image
        # Tesseract OSD를 사용하여 방향 감지 및 교정
        osd_data = pytesseract.image_to_osd(image)
        # OSD 결과에서 회전 각도 추출
        angle = int(re.search(r'Rotate: (\d+)', osd_data).group(1))
        if angle != 0:
            image = image.rotate(angle, expand=True)
        return image
    except Exception:
        # OSD 실패 시 원본 이미지 반환
        return image




