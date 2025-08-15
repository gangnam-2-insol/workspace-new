from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Dict, Any

import pytesseract
from PIL import Image, ImageFilter, ImageOps
import numpy as np

from .config import Settings


def _configure_tesseract(settings: Settings) -> None:
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


def _preprocess_for_ocr(pil_image: Image.Image, profile: str = "default") -> Image.Image:
    # 기본 전처리 (단순화)
    img = pil_image.convert("L")  # 그레이스케일
    
    # 이미지 크기 확대 (해상도 향상)
    width, height = img.size
    if width < 1000 or height < 1000:
        scale_factor = 2
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # 대비 강화 (단순하게)
    img = ImageOps.autocontrast(img, cutoff=2)
    
    # 샤프닝으로 텍스트 선명화
    img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
    
    return img


def _guess_psm_for_layout(pil_image: Image.Image) -> int:
    # 간단한 히스토그램 분석으로 다단/단일 추정 (고급화 여지)
    width, height = pil_image.size
    gray = np.array(pil_image.convert("L"))
    col_sum = (255 - gray).sum(axis=0)
    # 칼럼 최소값 분포를 보고 다단 가능성 추정
    valleys = (col_sum < col_sum.mean() * 0.5).sum()
    # OpenCV 제거: 간단 휴리스틱만 사용
    if valleys > width * 0.05:
        return 1  # ORIENTATION+SCRIPT, 다단 가능
    return 6  # 기본 단순 문단


def _tesseract_config(psm: int, settings: Settings) -> str:
    # 기본 설정 (단순화)
    config = f"--oem {settings.ocr_oem} --psm {psm}"
    
    # 기본적인 한국어 인식 설정만 추가
    config += " -c preserve_interword_spaces=1"
    
    return config


def ocr_images(image_paths: List[Path], settings: Settings) -> List[str]:
    """이미지 경로 목록에 대해 OCR 텍스트를 추출합니다."""
    _configure_tesseract(settings)

    texts: List[str] = []
    for image_path in image_paths:
        with Image.open(image_path) as img:
            # 전처리
            preprocessed = _preprocess_for_ocr(img, profile="default")
            # 레이아웃 기반 psm 추정
            psm = _guess_psm_for_layout(preprocessed) or settings.ocr_default_psm
            config = _tesseract_config(psm, settings)
            text = pytesseract.image_to_string(preprocessed, lang=settings.ocr_lang, config=config)
            texts.append(text)
    return texts


def _avg_confidence_from_data(data: str) -> float:
    # pytesseract.image_to_data output: TSV with conf column
    try:
        lines = data.splitlines()
        if not lines:
            return 0.0
        headers = lines[0].split("\t")
        conf_idx = headers.index("conf") if "conf" in headers else -1
        if conf_idx == -1:
            return 0.0
        confs: List[int] = []
        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) <= conf_idx:
                continue
            try:
                c = int(parts[conf_idx])
                if c >= 0:
                    confs.append(c)
            except Exception:
                continue
        if not confs:
            return 0.0
        return float(sum(confs)) / float(len(confs)) / 100.0
    except Exception:
        return 0.0


def perform_ocr_with_retries(pil_image: Image.Image, settings: Settings) -> Dict[str, Any]:
    profiles = ["default", "low_contrast"]
    attempts: List[Dict[str, Any]] = []
    best: Dict[str, Any] | None = None
    for attempt_idx in range(settings.max_retries + 1):
        profile = profiles[min(attempt_idx, len(profiles) - 1)]
        preprocessed = _preprocess_for_ocr(pil_image, profile=profile)
        psm = _guess_psm_for_layout(preprocessed) or settings.ocr_default_psm
        config = _tesseract_config(psm, settings)
        text = pytesseract.image_to_string(preprocessed, lang=settings.ocr_lang, config=config)
        data = pytesseract.image_to_data(preprocessed, lang=settings.ocr_lang, config=config)
        quality = _avg_confidence_from_data(data)
        record = {"psm": psm, "profile": profile, "quality": quality}
        attempts.append(record)
        current = {"text": text, "quality": quality, "psm": psm, "profile": profile}
        if best is None or current["quality"] > (best.get("quality") or 0.0):
            best = current
        if quality >= settings.quality_threshold:
            break
    return {"result": best or {"text": "", "quality": 0.0, "psm": settings.ocr_default_psm, "profile": profiles[0]}, "attempts": attempts}


def ocr_images_with_quality(image_paths: List[Path], settings: Settings) -> List[Dict[str, Any]]:
    _configure_tesseract(settings)
    outputs: List[Dict[str, Any]] = []
    for image_path in image_paths:
        with Image.open(image_path) as img:
            out = perform_ocr_with_retries(img, settings)
            outputs.append(out)
    return outputs


# 이미지에서 텍스트를 추출하는 OCR 기능
# pytesseract 사용, Tesseract 설치 필요
def extract_text_from_image(image: Image.Image) -> str:
    settings = Settings()
    _configure_tesseract(settings)
    img = image.convert("L")
    return pytesseract.image_to_string(img, lang=settings.ocr_lang)


