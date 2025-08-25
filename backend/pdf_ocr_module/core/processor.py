"""
PDF Processor
============

PDF 문서를 처리하는 메인 클래스입니다.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.config import Settings
from ..utils.storage import MongoStorage, VectorStorage
from .ai_analyzer import AIAnalyzer
from .ocr_engine import OCREngine
from .text_extractor import TextExtractor

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF 문서 처리 클래스"""

    def __init__(self, settings: Optional[Settings] = None):
        """
        PDFProcessor 초기화

        Args:
            settings: 설정 객체 (None이면 기본 설정 사용)
        """
        self.settings = settings or Settings()
        self.ocr_engine = OCREngine(self.settings)
        self.text_extractor = TextExtractor()
        self.ai_analyzer = AIAnalyzer(self.settings)
        self.mongo_storage = MongoStorage(self.settings)
        self.vector_storage = VectorStorage(self.settings)

        # 디렉토리 생성
        self._ensure_directories()

    def _ensure_directories(self):
        """필요한 디렉토리들을 생성합니다."""
        directories = [
            self.settings.images_dir,
            self.settings.thumbnails_dir,
            self.settings.output_dir,
            self.settings.temp_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def process_pdf(self, pdf_path: str | Path) -> Dict[str, Any]:
        """
        PDF 파일을 처리합니다.

        Args:
            pdf_path: PDF 파일 경로

        Returns:
            처리 결과 딕셔너리
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {pdf_path}")

        logger.info(f"PDF 처리 시작: {pdf_path}")
        start_time = datetime.now()

        try:
            # 1. 텍스트 추출 (내장 텍스트 + 레이아웃)
            layout_result = self.text_extractor.extract_text_with_layout(pdf_path)

            # 2. PDF → 이미지 변환 (선택적)
            page_image_dir = self.settings.images_dir / pdf_path.stem
            image_paths = []
            ocr_results = []

            try:
                image_paths = self._convert_pdf_to_images(pdf_path, page_image_dir)

                # 3. OCR 처리 (이미지가 있는 경우에만)
                if image_paths:
                    ocr_results = self.ocr_engine.ocr_images_with_quality(image_paths)

                    # 4. 텍스트 결합 (내장 텍스트 우선, OCR 보완)
                    page_texts = self._combine_texts(layout_result, ocr_results)
                    full_text = "\n\n".join(page_texts)
                else:
                    # OCR 없이 내장 텍스트만 사용
                    full_text = layout_result.get("full_text", "")

            except Exception as e:
                logger.warning(f"PDF 이미지 변환 실패, 내장 텍스트만 사용: {str(e)}")
                # OCR 없이 내장 텍스트만 사용
                full_text = layout_result.get("full_text", "")

            # 5. AI 분석
            ai_analysis = self.ai_analyzer.analyze_text(full_text)

            # 6. 결과 구성
            result = {
                "document_id": str(uuid.uuid4()),
                "filename": pdf_path.name,
                "file_path": str(pdf_path),
                "num_pages": len(image_paths) if image_paths else layout_result.get("num_pages", 1),
                "full_text": full_text,
                "layout_data": layout_result,
                "ocr_results": ocr_results,
                "ai_analysis": ai_analysis,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "created_at": datetime.now().isoformat()
            }

            # 7. 저장 (선택적)
            if self.settings.auto_save:
                self._save_result(result)

            logger.info(f"PDF 처리 완료: {pdf_path} ({result['processing_time']:.2f}초)")
            return result

        except Exception as e:
            logger.error(f"PDF 처리 실패: {pdf_path}, 오류: {str(e)}")
            raise

    def _convert_pdf_to_images(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """PDF를 이미지로 변환합니다."""
        from ..utils.pdf_converter import PDFConverter

        converter = PDFConverter(self.settings)
        return converter.convert_to_images(pdf_path, output_dir)

    def _combine_texts(self, layout_result: Dict, ocr_results: List[Dict]) -> List[str]:
        """내장 텍스트와 OCR 텍스트를 결합합니다."""
        page_texts = []

        for i, ocr_result in enumerate(ocr_results):
            # 내장 텍스트 추출
            page_spans = next(
                (p.get("spans", []) for p in layout_result.get("pages", [])
                 if p.get("page") == i + 1),
                []
            )
            embedded_text = " ".join([s.get("text", "") for s in page_spans]).strip()

            # OCR 텍스트
            ocr_text = ocr_result.get("result", {}).get("text", "")

            # 우선순위: 내장 텍스트가 충분하면 사용, 아니면 OCR 사용
            chosen_text = embedded_text if len(embedded_text) >= max(50, len(ocr_text) * 0.5) else ocr_text
            page_texts.append(chosen_text)

        return page_texts

    def _save_result(self, result: Dict[str, Any]):
        """결과를 저장합니다."""
        try:
            # MongoDB 저장
            self.mongo_storage.save_document(result)

            # 벡터 저장 (선택적)
            if self.settings.enable_vector_storage:
                self.vector_storage.store_embeddings(result)

        except Exception as e:
            logger.warning(f"결과 저장 실패: {str(e)}")

    def process_multiple_pdfs(self, pdf_paths: List[str | Path]) -> List[Dict[str, Any]]:
        """여러 PDF 파일을 처리합니다."""
        results = []

        for pdf_path in pdf_paths:
            try:
                result = self.process_pdf(pdf_path)
                results.append(result)
            except Exception as e:
                logger.error(f"PDF 처리 실패: {pdf_path}, 오류: {str(e)}")
                results.append({
                    "error": str(e),
                    "file_path": str(pdf_path),
                    "success": False
                })

        return results

    def get_processing_stats(self) -> Dict[str, Any]:
        """처리 통계를 반환합니다."""
        return {
            "total_processed": len(self.mongo_storage.get_all_documents()),
            "storage_size": self.mongo_storage.get_storage_size(),
            "vector_count": self.vector_storage.get_vector_count() if self.settings.enable_vector_storage else 0
        }
