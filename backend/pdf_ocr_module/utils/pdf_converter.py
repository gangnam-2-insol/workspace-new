"""
PDF Converter
============

PDF를 이미지로 변환하는 유틸리티 클래스입니다.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import List, Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .config import Settings

logger = logging.getLogger(__name__)


class PDFConverter:
    """PDF를 이미지로 변환하는 클래스"""

    def __init__(self, settings: Settings):
        """
        PDFConverter 초기화

        Args:
            settings: 설정 객체
        """
        self.settings = settings
        self._check_dependencies()

    def _check_dependencies(self):
        """필요한 의존성을 확인합니다."""
        if not PIL_AVAILABLE:
            logger.warning("PIL이 설치되지 않았습니다. 이미지 처리 기능이 제한될 수 있습니다.")

        if not self.settings.poppler_path:
            logger.warning("Poppler 경로가 설정되지 않았습니다. PDF 변환 기능이 제한될 수 있습니다.")

    def convert_to_images(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """
        PDF를 이미지로 변환합니다.

        Args:
            pdf_path: PDF 파일 경로
            output_dir: 출력 디렉토리

        Returns:
            생성된 이미지 파일 경로 목록
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Poppler 사용 (우선)
        if self.settings.poppler_path:
            try:
                return self._convert_with_poppler(pdf_path, output_dir)
            except Exception as e:
                logger.warning(f"Poppler 변환 실패, PIL 사용: {str(e)}")

        # PIL 사용 (fallback)
        if PIL_AVAILABLE:
            try:
                return self._convert_with_pil(pdf_path, output_dir)
            except Exception as e:
                logger.error(f"PIL 변환 실패: {str(e)}")

        raise RuntimeError("PDF를 이미지로 변환할 수 없습니다.")

    def _convert_with_poppler(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """
        Poppler를 사용하여 PDF를 이미지로 변환합니다.

        Args:
            pdf_path: PDF 파일 경로
            output_dir: 출력 디렉토리

        Returns:
            생성된 이미지 파일 경로 목록
        """
        # pdftoppm 명령어 구성
        cmd = [
            os.path.join(self.settings.poppler_path, "pdftoppm"),
            "-png",  # PNG 형식
            "-r", str(self.settings.dpi),  # DPI 설정
            "-cropbox",  # 페이지 경계 사용
            str(pdf_path),
            str(output_dir / "page")  # 출력 파일명 패턴
        ]

        try:
            # 변환 실행
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # 생성된 파일 목록 수집
            image_files = []
            page_num = 1

            while True:
                image_path = output_dir / f"page-{page_num:02d}.png"
                if image_path.exists():
                    image_files.append(image_path)
                    page_num += 1
                else:
                    break

            logger.info(f"Poppler 변환 완료: {len(image_files)}개 페이지")
            return image_files

        except subprocess.CalledProcessError as e:
            logger.error(f"Poppler 변환 실패: {e.stderr}")
            raise

    def _convert_with_pil(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """
        PIL을 사용하여 PDF를 이미지로 변환합니다.

        Args:
            pdf_path: PDF 파일 경로
            output_dir: 출력 디렉토리

        Returns:
            생성된 이미지 파일 경로 목록
        """
        try:
            # pdf2image 사용 (PIL 기반)
            from pdf2image import convert_from_path

            # PDF를 이미지로 변환
            images = convert_from_path(
                str(pdf_path),
                dpi=self.settings.dpi,
                fmt="PNG"
            )

            # 이미지 저장
            image_files = []
            for i, image in enumerate(images):
                image_path = output_dir / f"page-{i+1:02d}.png"
                image.save(image_path, "PNG")
                image_files.append(image_path)

            logger.info(f"PIL 변환 완료: {len(image_files)}개 페이지")
            return image_files

        except ImportError:
            logger.error("pdf2image가 설치되지 않았습니다.")
            raise
        except Exception as e:
            logger.error(f"PIL 변환 실패: {str(e)}")
            raise

    def create_thumbnail(self, image_path: Path, size: tuple = (200, 200)) -> Optional[Path]:
        """
        이미지의 썸네일을 생성합니다.

        Args:
            image_path: 원본 이미지 경로
            size: 썸네일 크기 (width, height)

        Returns:
            썸네일 파일 경로 또는 None
        """
        if not PIL_AVAILABLE:
            logger.warning("PIL이 설치되지 않아 썸네일을 생성할 수 없습니다.")
            return None

        try:
            # 썸네일 디렉토리 생성
            thumbnail_dir = self.settings.thumbnails_dir
            thumbnail_dir.mkdir(parents=True, exist_ok=True)

            # 썸네일 파일명
            thumbnail_path = thumbnail_dir / f"thumb_{image_path.stem}.png"

            # 이미지 로드 및 리사이즈
            with Image.open(image_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, "PNG")

            logger.info(f"썸네일 생성 완료: {thumbnail_path}")
            return thumbnail_path

        except Exception as e:
            logger.error(f"썸네일 생성 실패: {str(e)}")
            return None

    def get_page_count(self, pdf_path: Path) -> int:
        """
        PDF의 페이지 수를 반환합니다.

        Args:
            pdf_path: PDF 파일 경로

        Returns:
            페이지 수
        """
        try:
            # PyMuPDF 사용 (가장 빠름)
            import fitz
            doc = fitz.open(str(pdf_path))
            count = len(doc)
            doc.close()
            return count

        except ImportError:
            # pdfplumber 사용
            try:
                import pdfplumber
                with pdfplumber.open(str(pdf_path)) as pdf:
                    return len(pdf.pages)
            except ImportError:
                logger.error("PDF 페이지 수를 확인할 수 없습니다.")
                return 0
        except Exception as e:
            logger.error(f"페이지 수 확인 실패: {str(e)}")
            return 0
