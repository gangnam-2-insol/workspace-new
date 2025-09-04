"""
PDF OCR Module
==============

PDF 문서의 텍스트 추출과 OCR 기능을 제공하는 모듈입니다.
"""

__version__ = "2.0.0"

from .ai_analyzer import (
    analyze_text,
    clean_text,
    extract_fields,
    extract_keywords,
    summarize_text,
)
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
    'analyze_text',
    'extract_keywords',
    'summarize_text',
    'extract_fields',
    'clean_text',
    'Settings',
    'MongoStorage',
    'VectorStorage',
    'PDFConverter'
]





