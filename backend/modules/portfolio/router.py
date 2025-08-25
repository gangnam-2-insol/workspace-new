from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
import motor.motor_asyncio
from .models import (
    PortfolioCreate, Portfolio, PortfolioUpdate
)
from .services import PortfolioService
from ..shared.models import BaseResponse

router = APIRouter(prefix="/api/portfolio-module", tags=["포트폴리오"])

def get_portfolio_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> PortfolioService:
    return PortfolioService(db)

@router.post("/", response_model=BaseResponse)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """포트폴리오 생성"""
    try:
        portfolio_id = await portfolio_service.create_portfolio(portfolio_data)
        return BaseResponse(
            success=True,
            message="포트폴리오가 성공적으로 생성되었습니다.",
            data={"portfolio_id": portfolio_id}
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"포트폴리오 생성에 실패했습니다: {str(e)}"
        )

@router.get("/{portfolio_id}", response_model=BaseResponse)
async def get_portfolio(
    portfolio_id: str,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """포트폴리오 조회"""
    try:
        portfolio = await portfolio_service.get_portfolio(portfolio_id)
        if not portfolio:
            return BaseResponse(
                success=False,
                message="포트폴리오를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="포트폴리오 조회 성공",
            data=portfolio.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"포트폴리오 조회에 실패했습니다: {str(e)}"
        )

@router.get("/", response_model=BaseResponse)
async def get_portfolios(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    applicant_id: Optional[str] = None,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """포트폴리오 목록 조회"""
    try:
        skip = (page - 1) * limit
        portfolios = await portfolio_service.get_portfolios(skip, limit, status, applicant_id)
        
        return BaseResponse(
            success=True,
            message="포트폴리오 목록 조회 성공",
            data={
                "portfolios": [portfolio.dict() for portfolio in portfolios],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(portfolios)
                }
            }
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"포트폴리오 목록 조회에 실패했습니다: {str(e)}"
        )

@router.put("/{portfolio_id}", response_model=BaseResponse)
async def update_portfolio(
    portfolio_id: str,
    update_data: PortfolioUpdate,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """포트폴리오 수정"""
    try:
        success = await portfolio_service.update_portfolio(portfolio_id, update_data)
        if not success:
            return BaseResponse(
                success=False,
                message="포트폴리오를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="포트폴리오가 성공적으로 수정되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"포트폴리오 수정에 실패했습니다: {str(e)}"
        )

@router.delete("/{portfolio_id}", response_model=BaseResponse)
async def delete_portfolio(
    portfolio_id: str,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """포트폴리오 삭제"""
    try:
        success = await portfolio_service.delete_portfolio(portfolio_id)
        if not success:
            return BaseResponse(
                success=False,
                message="포트폴리오를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="포트폴리오가 성공적으로 삭제되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"포트폴리오 삭제에 실패했습니다: {str(e)}"
        )
