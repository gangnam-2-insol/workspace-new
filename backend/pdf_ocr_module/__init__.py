"""
PDF OCR Module
==============

PDF 문서의 텍스트 추출과 OCR 기능을 제공하는 모듈입니다.
"""

__version__ = "2.0.0"

# from .core.ai_analyzer import AIAnalyzer  # 임시로 주석 처리
from .core.ocr_engine import OCREngine
from .core.processor import PDFProcessor
from .core.text_extractor import TextExtractor
from .utils.config import Settings
from .utils.pdf_converter import PDFConverter
from .utils.storage import MongoStorage, VectorStorage

__all__ = [
    'PDFProcessor',
    'OCREngine',
    'TextExtractor',
    # 'AIAnalyzer',  # 임시로 주석 처리
    'Settings',
    'MongoStorage',
    'VectorStorage',
    'PDFConverter'
]





