"""
라우터 끝단에서만 사용하는 안전한 응답 헬퍼
전역 영향 없이 ObjectId/datetime 직렬화 처리
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# 커스텀 인코더 정의
_CUSTOM_ENCODERS = {
    ObjectId: str,
    datetime: lambda v: v.isoformat(),
    date: lambda v: v.isoformat(),
    Decimal: float,
    bytes: lambda v: v.decode("utf-8", "ignore"),
}


def respond(payload: Any, status_code: int = 200) -> JSONResponse:
    """
    라우터 끝단에서만 직렬화 적용 (전역 영향 없음)

    Args:
        payload: 응답할 데이터 (ObjectId, datetime 포함 가능)
        status_code: HTTP 상태 코드 (기본값: 200)

    Returns:
        JSONResponse: 안전하게 직렬화된 응답
    """
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload, custom_encoder=_CUSTOM_ENCODERS),
    )
