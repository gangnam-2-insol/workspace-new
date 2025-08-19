from __future__ import annotations

from pathlib import Path
from typing import List

from pdf2image import convert_from_path
from PIL import Image, ImageOps
import numpy as np
import cv2
import pytesseract

from .config import Settings


def _auto_rotate_and_deskew(pil_image: Image.Image) -> Image.Image:
    """OSD 기반 회전과 제한된 데스큐를 수행합니다."""
    # OSD (Orientation and Script Detection) 기반 회전만 허용
    try:
        # Tesseract OSD로 페이지 방향 감지
        osd_data = pytesseract.image_to_osd(pil_image, output_type=pytesseract.Output.DICT)
        rotation_angle = osd_data['rotate']
        
        # 90도 또는 270도 회전만 허용 (가로 페이지를 세로로 강제 회전 방지)
        if rotation_angle in [90, 270]:
            pil_image = pil_image.rotate(rotation_angle, expand=True)
    except Exception:
        # OSD 실패 시 원본 유지
        pass
    
    # 제한된 데스큐 (±5도 이내만)
    try:
        gray = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY)
        _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(bw > 0))
        
        if coords.size > 0:
            rect = cv2.minAreaRect(coords)
            angle = rect[-1]
            
            # 각도 정규화
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # ±5도 이내에서만 데스큐 적용
            if abs(angle) <= 5.0:
                (h, w) = gray.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(np.array(pil_image), M, (w, h), 
                                       flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                return Image.fromarray(rotated)
    except Exception:
        # 데스큐 실패 시 원본 유지
        pass
    
    return pil_image


def save_pdf_pages_to_images(pdf_path: Path, output_dir: Path, settings: Settings, dpi: int | None = None) -> List[Path]:
    """PDF를 이미지로 변환(300–400 DPI)하고 자동 회전/데스큐 후 저장합니다."""
    output_dir.mkdir(parents=True, exist_ok=True)

    images = convert_from_path(
        str(pdf_path),
        dpi=dpi or settings.dpi,
        poppler_path=settings.poppler_path if settings.poppler_path else None,
        # CropBox 무시하고 MediaBox 사용 (문서가 지정한 임시 크롭 때문에 좌우가 잘리거나 비율이 달라지는 문제 방지)
        use_cropbox=False,
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
        # CropBox 무시하고 MediaBox 사용
        use_cropbox=False,
    )
    return images


