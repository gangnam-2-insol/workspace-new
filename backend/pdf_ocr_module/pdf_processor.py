from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
import io

from pdf2image import convert_from_path
from PIL import Image, ImageOps
import numpy as np
import cv2
import fitz  # PyMuPDF
import pytesseract

from .config import Settings


def detect_pdf_orientation(pdf_path: Path) -> str:
    """PDF의 방향을 감지합니다 (portrait/landscape)."""
    try:
        doc = fitz.open(str(pdf_path))
        if len(doc) == 0:
            return "portrait"
        
        # 첫 번째 페이지로 방향 판단
        page = doc[0]
        rect = page.rect
        
        # 페이지의 너비와 높이 비교
        width = rect.width
        height = rect.height
        
        print(f"PDF 페이지 크기: {width} x {height}")
        
        # 더 정확한 방향 감지를 위한 비율 계산
        ratio = width / height
        print(f"PDF 페이지 비율: {ratio:.3f}")
        
        # A4 비율 (1:1.414)을 기준으로 판단
        # 1.0에 가까우면 정사각형, 1.414에 가까우면 A4 세로, 0.707에 가까우면 A4 가로
        if ratio > 1.2:  # 가로가 훨씬 긴 경우
            return "landscape"
        elif ratio < 0.8:  # 세로가 훨씬 긴 경우
            return "portrait"
        else:
            # A4 비율 근처인 경우, 텍스트 방향으로 추가 판단
            return _detect_orientation_by_text(page)
        
        doc.close()
    except Exception as e:
        print(f"PDF 방향 감지 중 오류: {e}")
        return "portrait"  # 기본값


def _detect_orientation_by_text(page) -> str:
    """텍스트 방향을 기반으로 PDF 방향을 감지합니다."""
    try:
        # 페이지에서 텍스트 블록 추출
        text_dict = page.get_text("dict")
        blocks = text_dict.get("blocks", [])
        
        if not blocks:
            return "portrait"  # 텍스트가 없으면 기본값
        
        # 텍스트 블록들의 위치 분석
        horizontal_lines = 0
        vertical_lines = 0
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    if "spans" in line and line["spans"]:
                        # 첫 번째 span의 방향 확인
                        span = line["spans"][0]
                        if "bbox" in span:
                            x0, y0, x1, y1 = span["bbox"]
                            width = x1 - x0
                            height = y1 - y0
                            
                            if width > height * 2:  # 가로 텍스트
                                horizontal_lines += 1
                            elif height > width * 2:  # 세로 텍스트
                                vertical_lines += 1
        
        print(f"가로 텍스트 라인: {horizontal_lines}, 세로 텍스트 라인: {vertical_lines}")
        
        # 더 많은 텍스트 방향으로 판단
        if horizontal_lines > vertical_lines:
            return "portrait"  # 가로 텍스트가 많으면 세로 PDF
        else:
            return "portrait"  # 기본값
            
    except Exception as e:
        print(f"텍스트 기반 방향 감지 중 오류: {e}")
        return "portrait"


def get_pdf_page_size(pdf_path: Path) -> Tuple[float, float]:
    """PDF 페이지의 크기를 가져옵니다."""
    try:
        doc = fitz.open(str(pdf_path))
        if len(doc) == 0:
            return (595.0, 842.0)  # A4 기본 크기
        
        page = doc[0]
        rect = page.rect
        width = rect.width
        height = rect.height
        
        doc.close()
        
        print(f"PDF 페이지 크기: {width} x {height} 포인트")
        return (width, height)
    except Exception as e:
        print(f"PDF 크기 감지 중 오류: {e}")
        return (595.0, 842.0)  # A4 기본 크기


def _auto_rotate_and_deskew(pil_image: Image.Image) -> Image.Image:
    # 그레이스케일
    gray = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY)
    # OTSU 이진화
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 가장자리 검출 후 Hough transform으로 기울기 추정 대신
    # 최소 외접 사각형 각도로 deskew
    coords = np.column_stack(np.where(bw > 0))
    if coords.size == 0:
        return pil_image
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(np.array(pil_image), M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)


def _process_image_by_orientation(pil_image: Image.Image, orientation: str) -> Image.Image:
    """방향에 따라 이미지를 처리합니다."""
    # 기본 처리: 자동 회전/데스큐, 대비 강화
    processed = _auto_rotate_and_deskew(pil_image)
    processed = ImageOps.autocontrast(processed)
    
    # 방향에 따른 추가 처리
    if orientation == "landscape":
        # 가로 방향일 때는 추가적인 선명도 향상
        processed = _enhance_landscape_image(processed)
    else:
        # 세로 방향일 때는 텍스트 가독성 향상
        processed = _enhance_portrait_image(processed)
    
    return processed


def _enhance_landscape_image(image: Image.Image) -> Image.Image:
    """가로 방향 이미지의 선명도를 향상시킵니다."""
    # 가로 방향일 때는 더 선명하게 처리
    # 약간의 샤프닝 적용
    from PIL import ImageEnhance
    
    # 선명도 향상 (1.2배)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.2)
    
    # 대비 향상 (1.1배)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.1)
    
    return image


def _enhance_portrait_image(image: Image.Image) -> Image.Image:
    """세로 방향 이미지의 텍스트 가독성을 향상시킵니다."""
    # 세로 방향일 때는 텍스트 가독성에 중점
    from PIL import ImageEnhance
    
    # 대비 향상 (1.15배)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.15)
    
    # 밝기 조정 (1.05배)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.05)
    
    return image


def _basic_image_processing(pil_image: Image.Image) -> Image.Image:
    """기본 이미지 처리 (OSD 기반 방향 감지와 호환)."""
    # 기본 대비 강화
    processed = ImageOps.autocontrast(pil_image)
    
    # 기본적인 선명도 향상
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Sharpness(processed)
    processed = enhancer.enhance(1.1)
    
    return processed


def save_pdf_pages_to_images(pdf_path: Path, output_dir: Path, settings: "Settings", dpi: int | None = None) -> List[Path]:
    """PDF를 이미지로 변환합니다 (전체 페이지 강제 보장, 가로/세로 왜곡 방지)."""

    # 1) 출력 디렉토리
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2) DPI
    if dpi is None:
        dpi = settings.dpi

    # 3) PDF 열기
    doc = fitz.open(str(pdf_path))
    saved_paths: List[Path] = []

    try:
        # 4) 각 페이지
        for page_num in range(len(doc)):
            page = doc[page_num]

            # 5) **MediaBox 기준 전체 렌더** (CropBox 영향 배제)
            mediabox = page.mediabox  # 원본 박스
            print(f"[{page_num+1}] MediaBox: {mediabox.width} x {mediabox.height}, rotation={page.rotation}")

            # 6) DPI 매트릭스 (72 DPI 기준)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)

            # 7) 렌더 (alpha=False, RGB 권장)
            pix = page.get_pixmap(matrix=mat,
                                  alpha=False,
                                  colorspace=fitz.csRGB,
                                  clip=mediabox)  # CropBox 대신 MediaBox로 고정

            # 8) PIL Image로 변환 (EXIF/메타 회전 없이 그대로)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data)).convert("RGB")

            # 9) **방향 보정**: OSD가 90/270일 때만 회전, 180은 선택 적용
            rot = _detect_osd_rotation(image)
            if rot in (90, 270):
                # PIL은 반시계+값, OSD는 시계 기준이라 보정
                image = image.rotate(360 - rot, expand=True)
            elif rot == 180:
                # 180은 내용에 따라 가독성 차이가 적으므로 필요 시에만
                # 원치 않으면 아래 줄 주석 처리
                # image = image.rotate(180, expand=True)
                pass

            # 10) **소각도 데스큐만 허용(±5°)** — 과잉 기울임 방지
            image = _deskew_small_angles(image, max_deg=5)

            # 11) 기본 전처리 (자동 크롭은 기본 OFF 권장)
            #     _basic_image_processing 내부에서 aggressive crop / 강제 회전이 있으면 제거/옵션화하세요.
            processed = _basic_image_processing(image)

            # 12) 저장
            image_path = output_dir / f"{pdf_path.stem}_page{page_num + 1:04d}.png"
            processed.save(image_path, "PNG")
            saved_paths.append(image_path)

    finally:
        doc.close()

    return saved_paths


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
# 새로운 워크플로우와 일치하도록 수정
def convert_pdf_to_images(pdf_path: str) -> List[Image.Image]:
    settings = Settings()
    
    # 기본 DPI 사용
    dpi = 200
    
    print("PDF 변환: 새로운 워크플로우 적용 (convert_pdf_to_images)")
    
    # PyMuPDF를 사용하여 PDF를 이미지로 변환
    doc = fitz.open(str(pdf_path))
    processed_images = []
    
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # MediaBox 기준 전체 렌더
            mediabox = page.mediabox
            print(f"[{page_num+1}] MediaBox: {mediabox.width} x {mediabox.height}, rotation={page.rotation}")
            
            # DPI 매트릭스
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            
            # 렌더
            pix = page.get_pixmap(matrix=mat,
                                  alpha=False,
                                  colorspace=fitz.csRGB,
                                  clip=mediabox)
            
            # PIL Image로 변환
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data)).convert("RGB")
            
            # OSD 기반 방향 보정
            rot = _detect_osd_rotation(image)
            if rot in (90, 270):
                image = image.rotate(360 - rot, expand=True)
            elif rot == 180:
                # 180도 회전은 선택적 적용
                pass
            
            # 소각도 데스큐
            image = _deskew_small_angles(image, max_deg=5)
            
            # 기본 전처리
            processed = _basic_image_processing(image)
            processed_images.append(processed)
            
            print(f"페이지 {page_num + 1} 변환 완료: {image.size[0]} x {image.size[1]}")
    
    finally:
        doc.close()
    
    return processed_images


# --- 도움 함수: OSD로 0/90/180/270 중 회전 각도만 판단 ---
def _detect_osd_rotation(pil_img: Image.Image) -> int:
    try:
        osd = pytesseract.image_to_osd(pil_img, output_type=pytesseract.Output.DICT)
        rot = int(osd.get("rotate", 0))
        # 방어: 값이 0/90/180/270이 아닐 경우 0 처리
        return rot if rot in (0, 90, 180, 270) else 0
    except Exception:
        return 0


# --- 도움 함수: ±max_deg (기본 5°) 내에서만 데스큐 ---
def _deskew_small_angles(pil_img: Image.Image, max_deg: int = 5) -> Image.Image:
    img = np.array(pil_img.convert("L"))
    # OTSU로 텍스트 윤곽 강화
    _, bw = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    coords = np.column_stack(np.where(bw == 0))  # 글자를 검정(0)으로 가정
    if coords.shape[0] < 100:  # 텍스트 부족하면 스킵
        return pil_img

    angle = cv2.minAreaRect(coords)[-1]  # [-90, 0) 범위
    if angle < -45:
        angle = 90 + angle  # 예: -80° → 10°

    if abs(angle) > max_deg:
        return pil_img  # 과도한 각도면 방향 오판 가능성 → 스킵

    (h, w) = img.shape
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(np.array(pil_img), M, (w, h),
                             flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)


