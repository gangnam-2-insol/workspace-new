from __future__ import annotations

from pathlib import Path
from typing import List

from pdf2image import convert_from_path
from PIL import Image, ImageOps
import numpy as np
import cv2

from .config import Settings


def _auto_rotate_and_deskew(pil_image: Image.Image) -> Image.Image:
    # 그레이스케일
    gray = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY)
    # OTSU 이진화
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 가장자리 검출 후 Hough transform으로 기울기 추정 대신
    # 최소 외접 사각형 각도로 deskew
    coords = np.column_stack(np.where(bw > 0))
    if coords.size == 0:
        return pil_image
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(np.array(pil_image), M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)


def save_pdf_pages_to_images(pdf_path: Path, output_dir: Path, settings: Settings, dpi: int | None = None) -> List[Path]:
    """PDF를 이미지로 변환(300–400 DPI)하고 자동 회전/데스큐 후 저장합니다."""
    output_dir.mkdir(parents=True, exist_ok=True)

    images = convert_from_path(
        str(pdf_path),
        dpi=dpi or settings.dpi,
        poppler_path=settings.poppler_path if settings.poppler_path else None,
    )

    image_paths: List[Path] = []
    for index, image in enumerate(images, start=1):
        # 컬러→그레이스케일, 자동 회전/데스큐, 대비 강화
        processed = _auto_rotate_and_deskew(image)
        processed = ImageOps.autocontrast(processed)
        image_path = output_dir / f"{pdf_path.stem}_page{index:04d}.png"
        processed.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths


def create_thumbnails(image_paths: List[Path], max_width: int = 240) -> List[Path]:
    """페이지 이미지들의 썸네일을 생성하고 경로 목록을 반환합니다."""
    thumb_paths: List[Path] = []
    for path in image_paths:
        with Image.open(path) as img:
            w, h = img.size
            if w > max_width:
                new_h = int(h * (max_width / float(w)))
                thumb = img.resize((max_width, new_h), Image.LANCZOS)
            else:
                thumb = img.copy()
            thumb_path = path.parent / f"thumb_{path.name}"
            thumb.save(thumb_path, "PNG")
            thumb_paths.append(thumb_path)
    return thumb_paths


# PDF 파일을 페이지별 이미지로 변환하는 기능
# 내부적으로 pdf2image 사용, poppler 필요
def convert_pdf_to_images(pdf_path: str) -> List[Image.Image]:
    settings = Settings()
    images = convert_from_path(
        str(pdf_path),
        dpi=200,
        poppler_path=settings.poppler_path if settings.poppler_path else None,
    )
    return images


