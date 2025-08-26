"""
Text Extractor
==============

PDF에서 텍스트를 추출하는 클래스입니다.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TextSpan:
    """텍스트 스팬 정보"""
    text: str
    bbox: List[float]
    block: Optional[int] = None
    line: Optional[int] = None


class TextExtractor:
    """PDF 텍스트 추출 클래스"""
    
    def __init__(self):
        """TextExtractor 초기화"""
        self._check_dependencies()
    
    def _check_dependencies(self):
        """필요한 라이브러리들이 설치되어 있는지 확인합니다."""
        if not PYMUPDF_AVAILABLE:
            logger.warning("PyMuPDF가 설치되지 않았습니다. 일부 기능이 제한될 수 있습니다.")
        
        if not PDFPLUMBER_AVAILABLE:
            logger.warning("pdfplumber가 설치되지 않았습니다. 표 추출 기능이 제한될 수 있습니다.")
        
        if not PYPDF2_AVAILABLE:
            logger.warning("PyPDF2가 설치되지 않았습니다. 기본 텍스트 추출 기능이 제한될 수 있습니다.")
    
    def extract_text_with_layout(self, pdf_path: Path) -> Dict[str, Any]:
        """
        PyMuPDF로 텍스트와 레이아웃 정보를 추출합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            텍스트와 레이아웃 정보가 포함된 딕셔너리
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF가 설치되지 않았습니다. pip install PyMuPDF로 설치해주세요.")
        
        try:
            doc = fitz.open(str(pdf_path))
            pages: List[Dict[str, Any]] = []
            full_text_parts: List[str] = []
            
            # 각 페이지에서 텍스트와 레이아웃 추출
            for page_index in range(len(doc)):
                page = doc[page_index]
                textpage = page.get_text("dict")
                spans_out: List[Dict[str, Any]] = []
                
                # 블록별로 텍스트 추출
                for block_idx, block in enumerate(textpage.get("blocks", [])):
                    for line_idx, line in enumerate(block.get("lines", [])):
                        for span in line.get("spans", []):
                            txt = span.get("text") or ""
                            bbox = span.get("bbox") or [0, 0, 0, 0]
                            
                            if txt.strip():
                                spans_out.append({
                                    "text": txt,
                                    "bbox": [float(b) for b in bbox],
                                    "block": block_idx,
                                    "line": line_idx,
                                })
                                full_text_parts.append(txt)
                
                pages.append({"page": page_index + 1, "spans": spans_out, "tables": []})
            
            doc.close()
            
            # pdfplumber로 표 추출 (보조)
            if PDFPLUMBER_AVAILABLE:
                self._extract_tables_with_pdfplumber(pdf_path, pages)
            
            return {
                "pages": pages, 
                "full_text": "\n".join(full_text_parts)
            }
            
        except Exception as e:
            logger.error(f"텍스트 추출 실패: {pdf_path}, 오류: {str(e)}")
            raise
    
    def _extract_tables_with_pdfplumber(self, pdf_path: Path, pages: List[Dict[str, Any]]):
        """
        pdfplumber를 사용하여 표를 추출합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            pages: 페이지 정보 리스트
        """
        try:
            with pdfplumber.open(str(pdf_path)) as plumber_doc:
                for i, p in enumerate(plumber_doc.pages):
                    if i < len(pages):
                        try:
                            tables = p.extract_tables() or []
                            pages[i]["tables"] = tables
                        except Exception as e:
                            logger.warning(f"표 추출 실패 (페이지 {i+1}): {str(e)}")
                            pages[i]["tables"] = []
        except Exception as e:
            logger.warning(f"pdfplumber 표 추출 실패: {str(e)}")
    
    def extract_text_simple(self, pdf_path: Path) -> str:
        """
        간단한 텍스트 추출 (PyPDF2 사용)
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            추출된 텍스트
        """
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2가 설치되지 않았습니다. pip install PyPDF2로 설치해주세요.")
        
        try:
            text_parts = []
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"[페이지 {page_num + 1}]\n{page_text}")
                    else:
                        text_parts.append(f"[페이지 {page_num + 1}] - 텍스트 추출 불가")
            
            return "\n\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"간단한 텍스트 추출 실패: {pdf_path}, 오류: {str(e)}")
            raise
    
    def extract_text_with_pdfplumber(self, pdf_path: Path) -> str:
        """
        pdfplumber를 사용한 텍스트 추출
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            추출된 텍스트
        """
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber가 설치되지 않았습니다. pip install pdfplumber로 설치해주세요.")
        
        try:
            text_parts = []
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"[페이지 {page_num + 1}]\n{page_text}")
                    else:
                        text_parts.append(f"[페이지 {page_num + 1}] - 텍스트 추출 불가")
            
            return "\n\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"pdfplumber 텍스트 추출 실패: {pdf_path}, 오류: {str(e)}")
            raise
    
    def extract_text_with_fallback(self, pdf_path: Path) -> str:
        """
        여러 방법을 순차적으로 시도하여 텍스트를 추출합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            추출된 텍스트
        """
        # 1차: PyMuPDF (가장 정확)
        if PYMUPDF_AVAILABLE:
            try:
                result = self.extract_text_with_layout(pdf_path)
                if result.get("full_text", "").strip():
                    return result["full_text"]
            except Exception as e:
                logger.warning(f"PyMuPDF 추출 실패, 다음 방법 시도: {str(e)}")
        
        # 2차: pdfplumber
        if PDFPLUMBER_AVAILABLE:
            try:
                text = self.extract_text_with_pdfplumber(pdf_path)
                if text.strip():
                    return text
            except Exception as e:
                logger.warning(f"pdfplumber 추출 실패, 다음 방법 시도: {str(e)}")
        
        # 3차: PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                text = self.extract_text_simple(pdf_path)
                if text.strip():
                    return text
            except Exception as e:
                logger.warning(f"PyPDF2 추출 실패: {str(e)}")
        
        # 모든 방법 실패
        raise ValueError("모든 텍스트 추출 방법이 실패했습니다.")
    
    def get_page_count(self, pdf_path: Path) -> int:
        """
        PDF 페이지 수를 반환합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            페이지 수
        """
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(str(pdf_path))
                count = len(doc)
                doc.close()
                return count
            except Exception as e:
                logger.warning(f"PyMuPDF로 페이지 수 확인 실패: {str(e)}")
        
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(str(pdf_path)) as pdf:
                    return len(pdf.pages)
            except Exception as e:
                logger.warning(f"pdfplumber로 페이지 수 확인 실패: {str(e)}")
        
        if PYPDF2_AVAILABLE:
            try:
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_reader = PdfReader(pdf_file)
                    return len(pdf_reader.pages)
            except Exception as e:
                logger.warning(f"PyPDF2로 페이지 수 확인 실패: {str(e)}")
        
        raise ValueError("페이지 수를 확인할 수 없습니다.")
    
    def extract_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """
        PDF 메타데이터를 추출합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            메타데이터 딕셔너리
        """
        metadata = {
            "filename": pdf_path.name,
            "file_size": pdf_path.stat().st_size,
            "page_count": 0,
            "title": "",
            "author": "",
            "subject": "",
            "creator": "",
            "producer": "",
            "creation_date": "",
            "modification_date": ""
        }
        
        try:
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(str(pdf_path))
                metadata["page_count"] = len(doc)
                
                # 메타데이터 추출
                meta = doc.metadata
                if meta:
                    metadata.update({
                        "title": meta.get("title", ""),
                        "author": meta.get("author", ""),
                        "subject": meta.get("subject", ""),
                        "creator": meta.get("creator", ""),
                        "producer": meta.get("producer", ""),
                        "creation_date": meta.get("creationDate", ""),
                        "modification_date": meta.get("modDate", "")
                    })
                
                doc.close()
            
        except Exception as e:
            logger.warning(f"메타데이터 추출 실패: {str(e)}")
        
        return metadata
