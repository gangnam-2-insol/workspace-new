from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import pdfplumber


@dataclass
class TextSpan:
    page: int
    text: str
    bbox: Tuple[float, float, float, float]
    block: Optional[int] = None
    line: Optional[int] = None


def extract_text_with_layout(pdf_path: Path) -> Dict[str, Any]:
    """PyMuPDF로 텍스트+박스, pdfplumber로 표를 보조 추출.

    Returns:
        {
          'pages': [
            {
              'page': 1,
              'spans': [{'text': str, 'bbox': [x0,y0,x1,y1]}...],
              'tables': [[[cell,...], ...]]
            }, ...
          ],
          'full_text': str
        }
    """
    path = str(pdf_path)
    doc = fitz.open(path)
    pages: List[Dict[str, Any]] = []
    full_text_parts: List[str] = []

    # 텍스트/레이아웃
    for page_index in range(len(doc)):
        page = doc[page_index]
        textpage = page.get_text("dict")
        spans_out: List[Dict[str, Any]] = []
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

    # 표 추출(pdfplumber)
    try:
        with pdfplumber.open(path) as plumber_doc:
            for i, p in enumerate(plumber_doc.pages):
                try:
                    tables = p.extract_tables() or []
                    pages[i]["tables"] = tables
                except Exception:
                    pages[i]["tables"] = []
    except Exception:
        pass

    return {"pages": pages, "full_text": "\n".join(full_text_parts)}


