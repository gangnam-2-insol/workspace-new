#!/usr/bin/env python3
"""
이력서 분석 서비스
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.resume_analysis import (
    ResumeAnalysisRequest, 
    BatchAnalysisRequest, 
    ResumeAnalysisResponse,
    AnalysisStatusResponse
)
from modules.ai.resume_analyzer import OpenAIResumeAnalyzer
from modules.ai.huggingface_analyzer import HuggingFaceResumeAnalyzer

class ResumeAnalysisService:
    """이력서 분석 서비스"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """초기화"""
        self.db = db
        self.analyzers = {}
        self._initialize_analyzers()
    
    def _initialize_analyzers(self):
        """분석기 초기화"""
        try:
            # OpenAI 분석기 초기화
            self.analyzers["openai"] = OpenAIResumeAnalyzer()
            print("✅ OpenAI 분석기 초기화 완료")
        except Exception as e:
            print(f"❌ OpenAI 분석기 초기화 실패: {str(e)}")
            self.analyzers["openai"] = None
        
        try:
            # HuggingFace 분석기 초기화
            self.analyzers["huggingface"] = HuggingFaceResumeAnalyzer()
            print("✅ HuggingFace 분석기 초기화 완료")
        except Exception as e:
            print(f"❌ HuggingFace 분석기 초기화 실패: {str(e)}")
            self.analyzers["huggingface"] = None
    
    async def analyze_resume(self, request: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
        """단일 이력서 분석"""
        try:
            start_time = time.time()
            
            # 지원자 정보 조회
            applicant = await self._get_applicant(request.applicant_id)
            if not applicant:
                return ResumeAnalysisResponse(
                    success=False,
                    message="지원자를 찾을 수 없습니다.",
                    data=None
                )
            
            # 기존 분석 결과 확인
            if not request.force_reanalysis:
                existing_analysis = await self._get_existing_analysis(request.applicant_id)
                if existing_analysis:
                    return ResumeAnalysisResponse(
                        success=True,
                        message="기존 분석 결과를 반환합니다.",
                        data=existing_analysis,
                        analysis_id=str(existing_analysis.get("_id")),
                        created_at=existing_analysis.get("created_at"),
                        processing_time=0.0
                    )
            
            # 분석기 선택
            analyzer = self._select_analyzer(request.analysis_type)
            if not analyzer:
                return ResumeAnalysisResponse(
                    success=False,
                    message=f"지원하지 않는 분석 타입입니다: {request.analysis_type}",
                    data=None
                )
            
            # 이력서 분석 실행
            analysis_result = await analyzer.analyze_resume(applicant)
            
            # 분석 결과 저장
            analysis_id = await self._save_analysis_result(
                request.applicant_id, 
                analysis_result, 
                request.analysis_type
            )
            
            # 처리 시간 계산
            processing_time = time.time() - start_time
            
            # 응답 데이터 구성
            response_data = {
                "analysis_result": analysis_result.dict(),
                "applicant_info": {
                    "id": str(applicant["_id"]),
                    "name": applicant.get("name", ""),
                    "position": applicant.get("position", ""),
                    "department": applicant.get("department", "")
                },
                "analysis_type": request.analysis_type,
                "created_at": datetime.now().isoformat()
            }
            
            return ResumeAnalysisResponse(
                success=True,
                message="이력서 분석이 완료되었습니다.",
                data=response_data,
                analysis_id=analysis_id,
                created_at=datetime.now(),
                processing_time=processing_time
            )
            
        except Exception as e:
            print(f"❌ 이력서 분석 실패: {str(e)}")
            return ResumeAnalysisResponse(
                success=False,
                message=f"이력서 분석에 실패했습니다: {str(e)}",
                data=None
            )
    
    async def batch_analyze(self, request: BatchAnalysisRequest) -> ResumeAnalysisResponse:
        """일괄 이력서 분석"""
        try:
            start_time = time.time()
            
            # 지원자 정보 일괄 조회
            applicants = await self._get_applicants(request.applicant_ids)
            if not applicants:
                return ResumeAnalysisResponse(
                    success=False,
                    message="지원자를 찾을 수 없습니다.",
                    data=None
                )
            
            # 분석기 선택
            analyzer = self._select_analyzer(request.analysis_type)
            if not analyzer:
                return ResumeAnalysisResponse(
                    success=False,
                    message=f"지원하지 않는 분석 타입입니다: {request.analysis_type}",
                    data=None
                )
            
            # 일괄 분석 실행
            analysis_results = await analyzer.batch_analyze(applicants)
            
            # 성공한 분석 결과만 저장
            saved_results = []
            for result in analysis_results:
                if result["success"]:
                    analysis_id = await self._save_analysis_result(
                        result["applicant_id"],
                        result["analysis_result"],
                        request.analysis_type
                    )
                    saved_results.append({
                        **result,
                        "analysis_id": analysis_id
                    })
            
            # 처리 시간 계산
            processing_time = time.time() - start_time
            
            # 응답 데이터 구성
            response_data = {
                "total_count": len(applicants),
                "success_count": len(saved_results),
                "failed_count": len(analysis_results) - len(saved_results),
                "results": saved_results,
                "analysis_type": request.analysis_type,
                "created_at": datetime.now().isoformat()
            }
            
            return ResumeAnalysisResponse(
                success=True,
                message=f"일괄 분석이 완료되었습니다. 성공: {len(saved_results)}/{len(applicants)}",
                data=response_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            print(f"❌ 일괄 분석 실패: {str(e)}")
            return ResumeAnalysisResponse(
                success=False,
                message=f"일괄 분석에 실패했습니다: {str(e)}",
                data=None
            )
    
    async def reanalyze_resume(self, request: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
        """이력서 재분석"""
        try:
            # 강제 재분석 설정
            request.force_reanalysis = True
            return await self.analyze_resume(request)
            
        except Exception as e:
            print(f"❌ 이력서 재분석 실패: {str(e)}")
            return ResumeAnalysisResponse(
                success=False,
                message=f"이력서 재분석에 실패했습니다: {str(e)}",
                data=None
            )
    
    async def get_analysis_status(self) -> AnalysisStatusResponse:
        """분석 상태 조회"""
        try:
            # 전체 지원자 수
            total_applicants = await self.db.applicants.count_documents({})
            
            # 분석 완료된 지원자 수
            analyzed_count = await self.db.ai_analysis_results.count_documents({})
            
            # 분석 진행률 계산
            progress_percentage = (analyzed_count / total_applicants * 100) if total_applicants > 0 else 0
            
            # 최근 분석 결과 통계
            recent_analyses = await self.db.ai_analysis_results.find().sort("created_at", -1).limit(10).to_list(10)
            
            # 점수 분포 분석
            score_distribution = await self._analyze_score_distribution()
            
            status_data = {
                "total_applicants": total_applicants,
                "analyzed_count": analyzed_count,
                "pending_count": total_applicants - analyzed_count,
                "failed_count": 0,  # 실패한 분석은 별도로 추적하지 않음
                "progress_percentage": round(progress_percentage, 2),
                "recent_analyses": recent_analyses,
                "score_distribution": score_distribution,
                "last_updated": datetime.now().isoformat()
            }
            
            return AnalysisStatusResponse(
                success=True,
                message="분석 상태 조회가 완료되었습니다.",
                data=status_data,
                total_applicants=total_applicants,
                analyzed_count=analyzed_count,
                pending_count=total_applicants - analyzed_count,
                failed_count=0,
                progress_percentage=round(progress_percentage, 2)
            )
            
        except Exception as e:
            print(f"❌ 분석 상태 조회 실패: {str(e)}")
            return AnalysisStatusResponse(
                success=False,
                message=f"분석 상태 조회에 실패했습니다: {str(e)}",
                data={},
                total_applicants=0,
                analyzed_count=0,
                pending_count=0,
                failed_count=0,
                progress_percentage=0.0
            )
    
    async def get_applicant_analysis(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자별 분석 결과 조회"""
        try:
            analysis = await self.db.ai_analysis_results.find_one(
                {"applicant_id": applicant_id}
            )
            
            if analysis:
                # ObjectId를 문자열로 변환
                analysis["id"] = str(analysis["_id"])
                del analysis["_id"]
                
                return analysis
            
            return None
            
        except Exception as e:
            print(f"❌ 분석 결과 조회 실패: {str(e)}")
            return None
    
    def _select_analyzer(self, analysis_type: str):
        """분석기 선택"""
        if analysis_type == "openai" and self.analyzers.get("openai"):
            return self.analyzers["openai"]
        elif analysis_type == "huggingface" and self.analyzers.get("huggingface"):
            return self.analyzers["huggingface"]
        else:
            # 기본값으로 OpenAI 사용
            return self.analyzers.get("openai")
    
    async def _get_applicant(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 정보 조회"""
        try:
            applicant = await self.db.applicants.find_one({"_id": ObjectId(applicant_id)})
            return applicant
        except Exception as e:
            print(f"❌ 지원자 정보 조회 실패: {str(e)}")
            return None
    
    async def _get_applicants(self, applicant_ids: List[str]) -> List[Dict[str, Any]]:
        """지원자 정보 일괄 조회"""
        try:
            object_ids = [ObjectId(aid) for aid in applicant_ids]
            applicants = await self.db.applicants.find({"_id": {"$in": object_ids}}).to_list(None)
            return applicants
        except Exception as e:
            print(f"❌ 지원자 정보 일괄 조회 실패: {str(e)}")
            return []
    
    async def _get_existing_analysis(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """기존 분석 결과 조회"""
        try:
            analysis = await self.db.ai_analysis_results.find_one(
                {"applicant_id": applicant_id}
            )
            return analysis
        except Exception as e:
            print(f"❌ 기존 분석 결과 조회 실패: {str(e)}")
            return None
    
    async def _save_analysis_result(self, applicant_id: str, analysis_result, analysis_type: str) -> str:
        """분석 결과 저장"""
        try:
            # 저장할 데이터 구성
            analysis_data = {
                "applicant_id": applicant_id,
                "analysis_result": analysis_result.dict(),
                "analysis_type": analysis_type,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 기존 분석 결과가 있으면 업데이트, 없으면 새로 생성
            result = await self.db.ai_analysis_results.update_one(
                {"applicant_id": applicant_id},
                {"$set": analysis_data},
                upsert=True
            )
            
            if result.upserted_id:
                return str(result.upserted_id)
            else:
                # 업데이트된 경우 기존 문서의 _id 조회
                existing = await self.db.ai_analysis_results.find_one({"applicant_id": applicant_id})
                return str(existing["_id"])
                
        except Exception as e:
            print(f"❌ 분석 결과 저장 실패: {str(e)}")
            raise
    
    async def _analyze_score_distribution(self) -> Dict[str, Any]:
        """점수 분포 분석"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "avg_score": {"$avg": "$analysis_result.overall_score"},
                        "min_score": {"$min": "$analysis_result.overall_score"},
                        "max_score": {"$max": "$analysis_result.overall_score"},
                        "total_count": {"$sum": 1}
                    }
                }
            ]
            
            result = list(await self.db.ai_analysis_results.aggregate(pipeline))
            
            if result:
                stats = result[0]
                return {
                    "average_score": round(stats["avg_score"], 2),
                    "min_score": stats["min_score"],
                    "max_score": stats["max_score"],
                    "total_count": stats["total_count"]
                }
            else:
                return {
                    "average_score": 0,
                    "min_score": 0,
                    "max_score": 0,
                    "total_count": 0
                }
                
        except Exception as e:
            print(f"❌ 점수 분포 분석 실패: {str(e)}")
            return {
                "average_score": 0,
                "min_score": 0,
                "max_score": 0,
                "total_count": 0
            }

# 사용 예시
if __name__ == "__main__":
    import asyncio
    import motor.motor_asyncio
    
    async def test_service():
        # MongoDB 연결
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.hireme
        
        # 서비스 초기화
        service = ResumeAnalysisService(db)
        
        # 테스트 요청
        request = ResumeAnalysisRequest(
            applicant_id="507f1f77bcf86cd799439011",  # 테스트용 ID
            analysis_type="openai"
        )
        
        try:
            # 단일 분석 테스트
            result = await service.analyze_resume(request)
            print(f"✅ 분석 결과: {result.success}")
            print(f"메시지: {result.message}")
            
            # 상태 조회 테스트
            status = await service.get_analysis_status()
            print(f"✅ 상태 조회: {status.success}")
            print(f"전체 지원자: {status.total_applicants}")
            print(f"분석 완료: {status.analyzed_count}")
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
        
        finally:
            client.close()
    
    # 테스트 실행
    asyncio.run(test_service())
