from typing import Optional, List, Dict, Any
from fastapi import HTTPException
import motor.motor_asyncio
from datetime import datetime
import logging

from ..shared.services import BaseService
from .models import (
    Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioStatus
)

logger = logging.getLogger(__name__)

class PortfolioService(BaseService):
    """포트폴리오 서비스"""

    def __init__(self, db: motor.motor_asyncio.AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = "portfolios"

    async def create_portfolio(self, portfolio_data: PortfolioCreate) -> str:
        """포트폴리오 생성"""
        try:
            portfolio = Portfolio(**portfolio_data.dict())
            result = await self.db[self.collection].insert_one(portfolio.dict(by_alias=True))
            portfolio_id = str(result.inserted_id)
            logger.info(f"포트폴리오 생성 완료: {portfolio_id}")
            return portfolio_id
        except Exception as e:
            logger.error(f"포트폴리오 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="포트폴리오 생성에 실패했습니다.")

    async def get_portfolio(self, portfolio_id: str) -> Optional[Portfolio]:
        """포트폴리오 조회"""
        try:
            portfolio_data = await self.db[self.collection].find_one({"_id": self._get_object_id(portfolio_id)})
            if portfolio_data:
                return Portfolio(**portfolio_data)
            return None
        except Exception as e:
            logger.error(f"포트폴리오 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="포트폴리오 조회에 실패했습니다.")

    async def get_portfolios(self, skip: int = 0, limit: int = 10, 
                            status: Optional[PortfolioStatus] = None,
                            applicant_id: Optional[str] = None) -> List[Portfolio]:
        """포트폴리오 목록 조회"""
        try:
            filter_query = {}
            if status:
                filter_query["status"] = status
            if applicant_id:
                filter_query["applicant_id"] = applicant_id

            cursor = self.db[self.collection].find(filter_query).skip(skip).limit(limit)
            portfolios = []
            async for portfolio_data in cursor:
                portfolios.append(Portfolio(**portfolio_data))
            return portfolios
        except Exception as e:
            logger.error(f"포트폴리오 목록 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="포트폴리오 목록 조회에 실패했습니다.")

    async def update_portfolio(self, portfolio_id: str, update_data: PortfolioUpdate) -> bool:
        """포트폴리오 수정"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            result = await self.db[self.collection].update_one(
                {"_id": self._get_object_id(portfolio_id)},
                {"$set": update_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"포트폴리오 수정 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="포트폴리오 수정에 실패했습니다.")

    async def delete_portfolio(self, portfolio_id: str) -> bool:
        """포트폴리오 삭제"""
        try:
            result = await self.db[self.collection].delete_one({"_id": self._get_object_id(portfolio_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"포트폴리오 삭제 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="포트폴리오 삭제에 실패했습니다.")
