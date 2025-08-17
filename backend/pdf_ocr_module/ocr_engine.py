from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Dict, Any
import base64
import io
import os
import asyncio
import logging

import pytesseract
from PIL import Image, ImageFilter, ImageOps
import numpy as np
from openai import AsyncOpenAI
from dotenv import load_dotenv

from .config import Settings

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

# OpenAI 클라이언트 초기화
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _configure_tesseract(settings: Settings) -> None:
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


def _detect_image_orientation(pil_image: Image.Image) -> str:
    """이미지의 방향을 감지합니다 (portrait/landscape)."""
    width, height = pil_image.size
    
    if width > height:
        return "landscape"
    else:
        return "portrait"


def _preprocess_image_by_orientation(pil_image: Image.Image, orientation: str) -> Image.Image:
    """방향에 따라 이미지를 전처리합니다."""
    # 기본 전처리
    img = pil_image.convert("L")  # 그레이스케일
    
    # 방향에 따른 추가 전처리
    if orientation == "landscape":
        # 가로 방향일 때는 더 높은 해상도로 처리
        width, height = img.size
        if width < 1500 or height < 1000:
            scale_factor = 2.5
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # 가로 방향에 최적화된 대비 강화
        img = ImageOps.autocontrast(img, cutoff=1)
        
        # 선명도 향상
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=200, threshold=2))
    else:
        # 세로 방향일 때는 텍스트 가독성에 중점
        width, height = img.size
        if width < 1000 or height < 1500:
            scale_factor = 2
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # 세로 방향에 최적화된 대비 강화
        img = ImageOps.autocontrast(img, cutoff=2)
        
        # 텍스트 선명도 향상
        img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
    
    return img


def _preprocess_for_ocr(pil_image: Image.Image, profile: str = "default") -> Image.Image:
    # 방향 감지 및 방향별 전처리 사용
    orientation = _detect_image_orientation(pil_image)
    return _preprocess_image_by_orientation(pil_image, orientation)


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


def _image_to_base64(pil_image: Image.Image) -> str:
    """PIL 이미지를 base64 인코딩된 문자열로 변환"""
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str


async def _extract_text_with_openai(pil_image: Image.Image, settings: Settings) -> Dict[str, Any]:
    """OpenAI GPT-4o-mini를 사용하여 이미지에서 텍스트 추출"""
    try:
        # 이미지를 base64로 인코딩
        base64_image = _image_to_base64(pil_image)
        
        # OpenAI API 호출
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """당신은 이미지에서 텍스트를 정확하게 추출하는 OCR 전문가입니다. 
                    다음 지침을 따라주세요:
                    1. 이미지의 모든 텍스트를 정확하게 읽어주세요
                    2. 한국어와 영어 모두 지원합니다
                    3. 텍스트의 원래 형식과 레이아웃을 최대한 유지해주세요
                    4. 표나 리스트의 구조도 보존해주세요
                    5. 오타나 잘못 인식된 부분이 있다면 문맥에 맞게 수정해주세요
                    6. 텍스트만 추출하고, 추가 설명이나 분석은 하지 마세요"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 이미지에서 모든 텍스트를 추출해주세요."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000,
            temperature=0.1
        )
        
        extracted_text = response.choices[0].message.content.strip()
        
        return {
            "text": extracted_text,
            "quality": 0.95,  # OpenAI는 높은 품질로 가정
            "provider": "openai",
            "model": "gpt-4o-mini"
        }
        
    except Exception as e:
        logger.error(f"OpenAI OCR 실패: {str(e)}")
        # 폴백으로 Tesseract 사용
        return await _extract_text_with_tesseract_fallback(pil_image, settings)


async def _extract_text_with_tesseract_fallback(pil_image: Image.Image, settings: Settings) -> Dict[str, Any]:
    """Tesseract를 폴백으로 사용"""
    try:
        preprocessed = _preprocess_for_ocr(pil_image, profile="default")
        psm = _guess_psm_for_layout(preprocessed) or settings.ocr_default_psm
        config = _tesseract_config(psm, settings)
        text = pytesseract.image_to_string(preprocessed, lang=settings.ocr_lang, config=config)
        
        return {
            "text": text,
            "quality": 0.7,  # Tesseract 기본 품질
            "provider": "tesseract",
            "model": "tesseract"
        }
    except Exception as e:
        logger.error(f"Tesseract 폴백도 실패: {str(e)}")
        return {
            "text": "",
            "quality": 0.0,
            "provider": "none",
            "model": "none",
            "error": str(e)
        }


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


async def ocr_images_with_openai(image_paths: List[Path], settings: Settings) -> List[Dict[str, Any]]:
    """OpenAI GPT-4o-mini를 사용하여 이미지 목록에서 OCR 텍스트를 추출합니다."""
    outputs: List[Dict[str, Any]] = []
    
    for image_path in image_paths:
        with Image.open(image_path) as img:
            # 이미지 방향 감지
            orientation = _detect_image_orientation(img)
            print(f"이미지 방향 감지: {orientation}")
            
            # 방향에 따른 이미지 전처리
            processed_img = _preprocess_image_by_orientation(img, orientation)
            
            result = await _extract_text_with_openai(processed_img, settings)
            outputs.append({
                "result": result,
                "attempts": [result],  # OpenAI는 단일 시도
                "orientation": orientation
            })
    
    return outputs


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

    return {"result": best, "attempts": attempts}


def ocr_images_with_quality(image_paths: List[Path], settings: Settings) -> List[Dict[str, Any]]:
    """이미지 경로 목록에 대해 품질 정보와 함께 OCR 텍스트를 추출합니다."""
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
    
    preprocessed = _preprocess_for_ocr(image, profile="default")
    psm = _guess_psm_for_layout(preprocessed) or settings.ocr_default_psm
    config = _tesseract_config(psm, settings)
    text = pytesseract.image_to_string(preprocessed, lang=settings.ocr_lang, config=config)
    return text


