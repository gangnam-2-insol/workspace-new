from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Dict, Any

import pytesseract
from PIL import Image, ImageFilter, ImageOps
import cv2
import numpy as np

from .config import Settings


def _configure_tesseract(settings: Settings) -> None:
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


def _preprocess_for_ocr(pil_image: Image.Image, profile: str = "default") -> Image.Image:
    """OCR 품질 강화를 위한 다중 프로파일 전처리.
    - default: 기본 그레이스케일 + 확대 + 자동대비 + 샤프닝
    - low_contrast: CLAHE(대비 향상) + 미디언 블러로 노이즈 저감
    - binary: Otsu 이진화 + 모폴로지 열림/닫힘으로 잡티 제거 및 문자 연결
    - adaptive: 적응형 임계값 + 모폴로지 미세 정리
    """
    img = pil_image.convert("L")
    width, height = img.size
    if width < 1800 or height < 1800:
        scale_factor = 2
        img = img.resize((int(width * scale_factor), int(height * scale_factor)), Image.LANCZOS)

    np_img = np.array(img)

    if profile == "adaptive":
        # 적응형 임계값 + 작은 블랍 제거 (원래 방식으로 복귀)
        np_img = cv2.adaptiveThreshold(np_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 25, 11)
        kernel = np.ones((2, 2), np.uint8)
        np_img = cv2.morphologyEx(np_img, cv2.MORPH_OPEN, kernel, iterations=1)
    elif profile == "binary":
        # 전역 Otsu 이진화 + 모폴로지로 잡음 제거/문자 연결 (원래 방식)
        np_img = cv2.GaussianBlur(np_img, (3, 3), 0)
        _, np_img = cv2.threshold(np_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), np.uint8)
        np_img = cv2.morphologyEx(np_img, cv2.MORPH_OPEN, kernel, iterations=1)
        np_img = cv2.morphologyEx(np_img, cv2.MORPH_CLOSE, kernel, iterations=1)
    elif profile == "low_contrast":
        # CLAHE로 대비 향상 + 미세 노이즈 제거
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        np_img = clahe.apply(np_img)
        np_img = cv2.medianBlur(np_img, 3)
    else:
        # default: 자동 대비와 약한 샤프닝 위주
        img = Image.fromarray(np_img)
        img = ImageOps.autocontrast(img, cutoff=2)
        img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
        return img

    img = Image.fromarray(np_img)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=160, threshold=3))
    return img


def _guess_psm_for_layout(pil_image: Image.Image) -> int:
    """간단한 히스토그램 분석으로 다단/단일 레이아웃 추정.
    - 다단 가능성이 높으면 psm=4 (동일 크기의 텍스트 열 가정)
    - 그 외엔 psm=6 (단일 블록)
    참고: psm=1은 OSD 포함이므로 일반 인식용으로 부적절합니다.
    """
    width, height = pil_image.size
    gray = np.array(pil_image.convert("L"))
    col_sum = (255 - gray).sum(axis=0)
    valleys = (col_sum < col_sum.mean() * 0.5).sum()
    if valleys > width * 0.05:
        return 4
    return 6


def _tesseract_config(psm: int, settings: Settings) -> str:
    config = f"--oem {settings.ocr_oem} --psm {psm}"
    # 단어 간 공백 보존 및 약간의 테이블/레이아웃 도움 옵션
    config += " -c preserve_interword_spaces=1"
    # 화이트리스트 제거(원래 상태로 복귀)
    return config


def _choose_lang(pil_image: Image.Image, settings: Settings) -> str:
    """한글 우선 인식 기본값."""
    return "kor"


def _extract_english_tokens(text: str) -> set[str]:
    """영문/숫자 토큰(이메일/URL/도메인/대문자 약어/코드)을 추출합니다."""
    import re as _re
    tokens: set[str] = set()
    email_re = _re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    url_re = _re.compile(r"\bhttps?://[^\s]+\b")
    domain_re = _re.compile(r"\b[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    acronym_re = _re.compile(r"\b[A-Z]{2,}\b")
    code_re = _re.compile(r"\b[A-Za-z0-9]{4,}\b")
    for rx in (email_re, url_re, domain_re, acronym_re, code_re):
        for m in rx.finditer(text):
            tokens.add(m.group(0))
    return tokens


def _iter_english_matches(text: str) -> list[tuple[int, int, str, bool]]:
    """영문/숫자 토큰들을 위치 정보와 함께 반복합니다.
    Returns: [(start, end, token, has_alpha), ...]
    """
    import re as _re
    patterns = [
        _re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        _re.compile(r"\bhttps?://[^\s]+\b"),
        _re.compile(r"\b[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        _re.compile(r"\b[A-Z]{2,}\b"),
        _re.compile(r"\b[A-Za-z0-9]{4,}\b"),
    ]
    found: list[tuple[int, int, str, bool]] = []
    for rx in patterns:
        for m in rx.finditer(text):
            tok = m.group(0)
            has_alpha = any(ch.isalpha() and ("A" <= ch <= "Z" or "a" <= ch <= "z") for ch in tok)
            found.append((m.start(), m.end(), tok, has_alpha))
    # 중복/중첩 제거: 시작 위치, 길이 기준으로 정렬 후 고유화
    found.sort(key=lambda x: (x[0], -(x[1]-x[0])))
    unique: list[tuple[int, int, str, bool]] = []
    last_end = -1
    for s, e, t, a in found:
        if s >= last_end:
            unique.append((s, e, t, a))
            last_end = e
    return unique


def _merge_kor_and_koreng_text(text_kor: str, text_koreng: str) -> str:
    """한글(base)에 kor+eng 결과의 영문/숫자 토큰을 원문 위치 비율로 inline 삽입합니다.
    - 좌우 컨텍스트 매칭이 실패해도, 원문 인덱스 비율로 근사 위치에 삽입
    - 더 이상 하단으로 토큰을 내려보내지 않음(숫자 포함 모두 inline 시도)
    """
    import re as _re
    base = text_kor or ""
    mix = text_koreng or ""
    if not mix:
        return base

    def _nearby_has_token(b: str, token: str, pos: int, window: int = 40) -> bool:
        lo = max(0, pos - window)
        hi = min(len(b), pos + window)
        return token in b[lo:hi]

    matches = _iter_english_matches(mix)
    # 중복 방지 위해 뒤에서 앞으로 삽입하면 인덱스 어긋남 적음 → 역순 처리
    matches_sorted = sorted(matches, key=lambda m: m[0], reverse=True)

    for s, e, tok, _has_alpha in matches_sorted:
        if tok and tok in base:
            continue
        # 1) 좌/우 컨텍스트로 정밀 삽입 시도(한글/공백/구두점 포함)
        left_ctx = mix[max(0, s - 16):s]
        right_ctx = mix[e:min(len(mix), e + 16)]

        inserted = False
        if left_ctx:
            pos_l = base.rfind(left_ctx)
            if pos_l != -1:
                insert_at = pos_l + len(left_ctx)
                if not _nearby_has_token(base, tok, insert_at):
                    base = base[:insert_at] + (" " if insert_at and base[insert_at-1] != " " else "") + tok + (" " if insert_at < len(base) and base[insert_at:insert_at+1] != " " else "") + base[insert_at:]
                    inserted = True
        if not inserted and right_ctx:
            pos_r = base.find(right_ctx)
            if pos_r != -1:
                insert_at = pos_r
                if not _nearby_has_token(base, tok, insert_at):
                    base = base[:insert_at] + (" " if insert_at and base[insert_at-1] != " " else "") + tok + (" " if insert_at < len(base) and base[insert_at:insert_at+1] != " " else "") + base[insert_at:]
                    inserted = True

        # 2) 비율 기반 근사 위치 삽입(컨텍스트 실패 시)
        if not inserted:
            ratio = s / max(1, len(mix))
            insert_at = int(ratio * len(base))
            insert_at = max(0, min(len(base), insert_at))
            if not _nearby_has_token(base, tok, insert_at):
                base = base[:insert_at] + (" " if insert_at and base[insert_at-1] != " " else "") + tok + (" " if insert_at < len(base) and base[insert_at:insert_at+1] != " " else "") + base[insert_at:]

    return base


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


def _text_from_tsv(data: str, min_confidence: int = 60) -> str:
    """Tesseract TSV( image_to_data ) 출력에서 신뢰도 기반으로 단어를 조합해 텍스트를 생성합니다.

    - 낮은 신뢰도의 토큰(잡음 문자 등)을 제거해 가독성을 개선합니다.
    - line 전환을 감지해 줄바꿈을 최소한으로 복원합니다.
    """
    try:
        lines = data.splitlines()
        if not lines:
            return ""

        headers = lines[0].split("\t")
        def idx_of(name: str) -> int:
            try:
                return headers.index(name)
            except ValueError:
                return -1

        conf_idx = idx_of("conf")
        text_idx = idx_of("text")
        line_idx = idx_of("line_num")
        par_idx = idx_of("par_num")
        block_idx = idx_of("block_num")

        if conf_idx == -1 or text_idx == -1:
            return ""

        out_lines: list[str] = []
        current_key = None
        current_words: list[str] = []

        for row in lines[1:]:
            parts = row.split("\t")
            if len(parts) <= max(conf_idx, text_idx):
                continue
            try:
                conf = int(parts[conf_idx])
            except Exception:
                conf = -1
            word = parts[text_idx].strip()
            if not word:
                continue

            try:
                key = (
                    parts[block_idx] if block_idx != -1 else "0",
                    parts[par_idx] if par_idx != -1 else "0",
                    parts[line_idx] if line_idx != -1 else "0",
                )
            except Exception:
                key = ("0", "0", "0")

            if current_key is not None and key != current_key:
                if current_words:
                    out_lines.append(" ".join(current_words))
                current_words = []
            current_key = key

            if conf >= min_confidence and any(ch.isalnum() or ch in ".,!?;:-_()[]{}@#&*/+\\" for ch in word):
                if len(word) == 1 and not word.isalnum():
                    continue
                current_words.append(word)

        if current_words:
            out_lines.append(" ".join(current_words))

        return "\n".join([ln.strip() for ln in out_lines if ln.strip()])
    except Exception:
        return ""

def perform_ocr_with_retries(pil_image: Image.Image, settings: Settings) -> Dict[str, Any]:
    # 품질 개선: default, adaptive, binary 시도
    profiles = ["default", "adaptive", "binary"]
    attempts: List[Dict[str, Any]] = []
    best: Dict[str, Any] | None = None
    # 우선 추정값 기반 PSM 후보 생성
    base_psm = _guess_psm_for_layout(pil_image) or settings.ocr_default_psm
    psm_candidates = [base_psm]
    # 품질 개선: PSM 후보 6, 4, 11 시도
    for alt in [6, 4, 11]:
        if alt not in psm_candidates:
            psm_candidates.append(alt)

    for profile in profiles:
        preprocessed = _preprocess_for_ocr(pil_image, profile=profile)
        for psm in psm_candidates:
            config = _tesseract_config(psm, settings)
            # 1) 한국어 단독
            lang_kor = "kor"
            text_kor = pytesseract.image_to_string(preprocessed, lang=lang_kor, config=config)
            # 2) 한/영 혼합(설정값, 기본 'kor+eng')
            lang_mix = settings.ocr_lang if settings.ocr_lang else "kor+eng"
            text_mix = pytesseract.image_to_string(preprocessed, lang=lang_mix, config=config)
            # 3) 병합
            text_raw = _merge_kor_and_koreng_text(text_kor, text_mix)
            # 품질 추정은 혼합 언어 기준으로 계산
            data = pytesseract.image_to_data(preprocessed, lang=lang_mix, config=config)
            text_clean = None  # 계산 생략 또는 필요시 계산
            text = text_raw
            quality = _avg_confidence_from_data(data)
            record = {"psm": psm, "profile": profile, "quality": quality}
            attempts.append(record)
            current = {"text": text, "text_raw": text_raw, "text_clean": text_clean, "quality": quality, "psm": psm, "profile": profile}
            if best is None or current["quality"] > (best.get("quality") or 0.0):
                best = current
            if quality >= settings.quality_threshold:
                return {"result": current, "attempts": attempts}

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
    lang = _choose_lang(img, settings)
    return pytesseract.image_to_string(img, lang=lang)


