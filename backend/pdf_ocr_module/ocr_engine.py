from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Dict, Any
import base64
import io

from PIL import Image

from .config import Settings

# 동기식 OpenAI 클라이언트 (LLM OCR용)
try:
    from openai import OpenAI
    llm_client = OpenAI()
except ImportError:
    llm_client = None


def _image_to_base64(image_path: Path) -> str:
    """이미지를 base64로 인코딩합니다."""
    with Image.open(image_path) as img:
        # 이미지 크기 조정 (GPT Vision API 제한)
        max_size = 1024
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.LANCZOS)
        
        # JPEG로 변환하여 base64 인코딩
        buffer = io.BytesIO()
        img.convert('RGB').save(buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return img_base64

def _llm_ocr_extract_text(image_path: Path) -> str:
    """LLM을 사용하여 이미지에서 텍스트를 추출합니다."""
    if not llm_client:
        return ""
    
    try:
        # 이미지를 base64로 인코딩
        img_base64 = _image_to_base64(image_path)
        
        # GPT Vision API 호출
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "너는 OCR 전문가야. 이미지에서 모든 텍스트를 정확하게 추출해. 한글, 영어, 숫자, 특수문자 모두 포함해서 원본 그대로 추출해. 레이아웃과 줄바꿈도 유지해."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 이미지에서 모든 텍스트를 추출해주세요. 이력서나 문서의 모든 내용을 정확하게 읽어서 텍스트로 변환해주세요."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"LLM OCR 실패: {e}")
        return ""


# LLM OCR은 전처리가 필요 없으므로 제거


def ocr_images(image_paths: List[Path], settings: Settings) -> List[str]:
    """이미지 경로 목록에 대해 LLM OCR 텍스트를 추출합니다."""
    texts: List[str] = []
    for image_path in image_paths:
        text = _llm_ocr_extract_text(image_path)
        texts.append(text)
    return texts


# LLM OCR은 재시도 로직이 필요 없으므로 제거


def ocr_images_with_quality(image_paths: List[Path], settings: Settings) -> List[Dict[str, Any]]:
    """이미지 경로 목록에 대해 LLM OCR 텍스트를 추출합니다 (품질 정보 포함)."""
    outputs: List[Dict[str, Any]] = []
    for image_path in image_paths:
        text = _llm_ocr_extract_text(image_path)
        # LLM OCR은 기본적으로 높은 품질로 간주
        output = {
            "result": {
                "text": text,
                "quality": 0.95,  # LLM OCR은 높은 품질
                "method": "llm_ocr"
            },
            "attempts": [{"method": "llm_ocr", "quality": 0.95}]
        }
        outputs.append(output)
    return outputs


# 이미지에서 텍스트를 추출하는 LLM OCR 기능
def extract_text_from_image(image: Image.Image) -> str:
    """PIL Image에서 LLM OCR로 텍스트를 추출합니다."""
    if not llm_client:
        return ""
    
    try:
        # 이미지를 base64로 인코딩
        buffer = io.BytesIO()
        image.convert('RGB').save(buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # GPT Vision API 호출
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "너는 OCR 전문가야. 이미지에서 모든 텍스트를 정확하게 추출해."
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
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"LLM OCR 실패: {e}")
        return ""


