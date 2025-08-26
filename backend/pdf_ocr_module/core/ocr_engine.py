"""
OCR Engine
==========

Tesseract OCR 엔진을 사용한 텍스트 추출 클래스입니다.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

from ..utils.config import Settings

logger = logging.getLogger(__name__)


class OCREngine:
    """Tesseract OCR 엔진 클래스"""
    
    def __init__(self, settings: Settings):
        """
        OCREngine 초기화
        
        Args:
            settings: 설정 객체
        """
        self.settings = settings
        self._configure_tesseract()
    
    def _configure_tesseract(self):
        """Tesseract 설정을 구성합니다."""
        if self.settings.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.settings.tesseract_path
        
        # 환경 변수 설정
        os.environ['TESSDATA_PREFIX'] = str(self.settings.tesseract_data_path)
    
    def ocr_images_with_quality(self, image_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        이미지 목록에 대해 OCR을 수행하고 품질 메트릭을 포함한 결과를 반환합니다.
        
        Args:
            image_paths: 이미지 파일 경로 목록
            
        Returns:
            OCR 결과 목록 (각 결과는 텍스트와 품질 메트릭 포함)
        """
        results = []
        
        for image_path in image_paths:
            try:
                logger.info(f"OCR 처리 중: {image_path}")
                
                with Image.open(image_path) as img:
                    # 이미지 전처리
                    preprocessed = self._preprocess_image(img)
                    
                    # PSM 모드 추정
                    psm = self._guess_psm_mode(preprocessed)
                    
                    # OCR 설정 구성
                    config = self._get_tesseract_config(psm)
                    
                    # OCR 수행
                    text = pytesseract.image_to_string(
                        preprocessed, 
                        lang=self.settings.ocr_language, 
                        config=config
                    )
                    
                    # 품질 메트릭 계산
                    quality_metrics = self._calculate_quality_metrics(preprocessed, text)
                    
                    results.append({
                        "result": {
                            "text": text.strip(),
                            "confidence": quality_metrics.get("confidence", 0.0)
                        },
                        "quality_metrics": quality_metrics,
                        "image_path": str(image_path),
                        "psm_mode": psm
                    })
                    
            except Exception as e:
                logger.error(f"OCR 처리 실패: {image_path}, 오류: {str(e)}")
                results.append({
                    "result": {"text": "", "confidence": 0.0},
                    "quality_metrics": {"error": str(e)},
                    "image_path": str(image_path),
                    "psm_mode": None
                })
        
        return results
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        OCR 성능 향상을 위한 이미지 전처리
        
        Args:
            image: 원본 이미지
            
        Returns:
            전처리된 이미지
        """
        # 그레이스케일 변환
        if image.mode != 'L':
            image = image.convert('L')
        
        # 노이즈 제거
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # 대비 향상
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # 선명도 향상
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        return image
    
    def _guess_psm_mode(self, image: Image.Image) -> int:
        """
        이미지 레이아웃을 기반으로 PSM 모드를 추정합니다.
        
        Args:
            image: 전처리된 이미지
            
        Returns:
            추정된 PSM 모드
        """
        # 기본값
        psm = self.settings.ocr_default_psm
        
        # 이미지 크기 기반 추정
        width, height = image.size
        aspect_ratio = width / height
        
        if aspect_ratio > 2.0:  # 가로가 긴 이미지 (표나 다중 컬럼)
            psm = 6  # Uniform block of text
        elif aspect_ratio < 0.5:  # 세로가 긴 이미지 (세로 텍스트)
            psm = 5  # Vertical uniform block of text
        else:  # 일반적인 문서
            psm = 3  # Fully automatic page segmentation
        
        return psm
    
    def _get_tesseract_config(self, psm: int) -> str:
        """
        Tesseract 설정 문자열을 생성합니다.
        
        Args:
            psm: PSM 모드
            
        Returns:
            Tesseract 설정 문자열
        """
        config = f"-psm {psm}"
        
        # 언어 설정
        if self.settings.ocr_language:
            config += f" -l {self.settings.ocr_language}"
        
        # 추가 설정
        config += " -c preserve_interword_spaces=1"
        config += " -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz가나다라마바사아자차카타파하거너더러머버서어저처커터퍼허기니디리미비시이지치키티피히구누두루무부수우주추쿠투푸후그느드르므브스으즈츠크트프흐긔늬듸리미비시이지치키티피히그느드르므브스으즈츠크트프흐기니디리미비시이지치키티피히구누두루무부수우주추쿠투푸후그느드르므브스으즈츠크트프흐긔늬듸리미비시이지치키티피히그느드르므브스으즈츠크트프흐"
        
        return config
    
    def _calculate_quality_metrics(self, image: Image.Image, text: str) -> Dict[str, Any]:
        """
        OCR 품질 메트릭을 계산합니다.
        
        Args:
            image: 전처리된 이미지
            text: 추출된 텍스트
            
        Returns:
            품질 메트릭 딕셔너리
        """
        metrics = {}
        
        try:
            # 텍스트 길이 기반 신뢰도
            text_length = len(text.strip())
            if text_length > 0:
                # 간단한 품질 추정 (실제로는 더 정교한 방법 필요)
                metrics["confidence"] = min(0.95, 0.5 + (text_length / 1000) * 0.3)
            else:
                metrics["confidence"] = 0.0
            
            # 이미지 품질 메트릭
            width, height = image.size
            metrics["image_size"] = {"width": width, "height": height}
            metrics["aspect_ratio"] = width / height
            
            # 텍스트 밀도 (간단한 추정)
            metrics["text_density"] = text_length / (width * height) if width * height > 0 else 0
            
        except Exception as e:
            logger.warning(f"품질 메트릭 계산 실패: {str(e)}")
            metrics["confidence"] = 0.0
            metrics["error"] = str(e)
        
        return metrics
    
    def ocr_single_image(self, image_path: Path) -> Dict[str, Any]:
        """
        단일 이미지에 대해 OCR을 수행합니다.
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            OCR 결과
        """
        results = self.ocr_images_with_quality([image_path])
        return results[0] if results else {"result": {"text": "", "confidence": 0.0}}
    
    def get_supported_languages(self) -> List[str]:
        """
        지원되는 언어 목록을 반환합니다.
        
        Returns:
            지원 언어 목록
        """
        try:
            return pytesseract.get_languages()
        except Exception as e:
            logger.error(f"언어 목록 조회 실패: {str(e)}")
            return ["eng"]  # 기본값


# 모듈 레벨 함수들 (기존 코드와의 호환성을 위해)
def ocr_images_with_quality(image_paths: List[Path], settings: Settings) -> List[Dict[str, Any]]:
    """
    이미지 목록에 대해 OCR을 수행하고 품질 메트릭을 포함한 결과를 반환합니다.
    
    Args:
        image_paths: 이미지 파일 경로 목록
        settings: 설정 객체
        
    Returns:
        OCR 결과 목록
    """
    engine = OCREngine(settings)
    return engine.ocr_images_with_quality(image_paths)


def ocr_images(image_paths: List[Path], settings: Settings) -> List[str]:
    """
    이미지 목록에 대해 OCR을 수행하고 텍스트만 반환합니다.
    
    Args:
        image_paths: 이미지 파일 경로 목록
        settings: 설정 객체
        
    Returns:
        텍스트 목록
    """
    results = ocr_images_with_quality(image_paths, settings)
    return [result.get("result", {}).get("text", "") for result in results]
