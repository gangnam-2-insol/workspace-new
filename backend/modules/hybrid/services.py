from typing import Optional, List, Dict, Any
from fastapi import HTTPException
import motor.motor_asyncio
from datetime import datetime
import logging
from ..shared.services import BaseService
from .models import (
    HybridDocument, HybridCreate, HybridUpdate, HybridAnalysis,
    HybridSearchRequest, HybridComparisonRequest, HybridStatistics,
    CrossReferenceAnalysis, IntegratedEvaluation, HybridAnalysisType,
    IntegratedDocumentType
)

logger = logging.getLogger(__name__)

class HybridService(BaseService):
    """하이브리드 통합 분석 서비스"""
    
    def __init__(self, db: motor.motor_asyncio.AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = "hybrid_analyses"
    
    async def create_hybrid_analysis(self, hybrid_data: HybridCreate) -> str:
        """하이브리드 분석 생성"""
        try:
            # 통합 문서 타입 결정
            integrated_type = self._determine_document_type(hybrid_data)
            
            hybrid_dict = hybrid_data.dict()
            hybrid_dict["integrated_document_type"] = integrated_type
            hybrid_dict["document_type"] = "hybrid"
            
            hybrid_id = await self.create(self.collection, hybrid_dict)
            logger.info(f"하이브리드 분석 생성 완료: {hybrid_id}")
            return hybrid_id
        except Exception as e:
            logger.error(f"하이브리드 분석 생성 실패: {e}")
            raise HTTPException(status_code=500, detail="하이브리드 분석 생성 중 오류가 발생했습니다")
    
    def _determine_document_type(self, hybrid_data: HybridCreate) -> IntegratedDocumentType:
        """통합 문서 타입 결정"""
        has_resume = bool(hybrid_data.resume_id)
        has_cover_letter = bool(hybrid_data.cover_letter_id)
        has_portfolio = bool(hybrid_data.portfolio_id)
        
        if has_resume and has_cover_letter and has_portfolio:
            return IntegratedDocumentType.ALL_DOCUMENTS
        elif has_resume and has_cover_letter:
            return IntegratedDocumentType.RESUME_COVER_LETTER
        elif has_resume and has_portfolio:
            return IntegratedDocumentType.RESUME_PORTFOLIO
        elif has_cover_letter and has_portfolio:
            return IntegratedDocumentType.COVER_LETTER_PORTFOLIO
        elif has_resume:
            return IntegratedDocumentType.RESUME_ONLY
        elif has_cover_letter:
            return IntegratedDocumentType.COVER_LETTER_ONLY
        elif has_portfolio:
            return IntegratedDocumentType.PORTFOLIO_ONLY
        else:
            raise HTTPException(status_code=400, detail="최소 하나의 문서가 필요합니다")
    
    async def get_hybrid_analysis(self, hybrid_id: str) -> Optional[HybridDocument]:
        """하이브리드 분석 조회"""
        try:
            hybrid_data = await self.get_by_id(self.collection, hybrid_id)
            if hybrid_data:
                return HybridDocument(**hybrid_data)
            return None
        except Exception as e:
            logger.error(f"하이브리드 분석 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="하이브리드 분석 조회 중 오류가 발생했습니다")
    
    async def get_hybrid_analyses(self, applicant_id: Optional[str] = None, 
                                 skip: int = 0, limit: int = 10) -> List[HybridDocument]:
        """하이브리드 분석 목록 조회"""
        try:
            filters = {}
            if applicant_id:
                filters["applicant_id"] = applicant_id
            
            hybrid_data = await self.get_list(self.collection, filters, skip, limit)
            return [HybridDocument(**hybrid) for hybrid in hybrid_data]
        except Exception as e:
            logger.error(f"하이브리드 분석 목록 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="하이브리드 분석 목록 조회 중 오류가 발생했습니다")
    
    async def update_hybrid_analysis(self, hybrid_id: str, update_data: HybridUpdate) -> bool:
        """하이브리드 분석 업데이트"""
        try:
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            success = await self.update(self.collection, hybrid_id, update_dict)
            if success:
                logger.info(f"하이브리드 분석 업데이트 완료: {hybrid_id}")
            return success
        except Exception as e:
            logger.error(f"하이브리드 분석 업데이트 실패: {e}")
            raise HTTPException(status_code=500, detail="하이브리드 분석 업데이트 중 오류가 발생했습니다")
    
    async def delete_hybrid_analysis(self, hybrid_id: str) -> bool:
        """하이브리드 분석 삭제"""
        try:
            success = await self.delete(self.collection, hybrid_id)
            if success:
                logger.info(f"하이브리드 분석 삭제 완료: {hybrid_id}")
            return success
        except Exception as e:
            logger.error(f"하이브리드 분석 삭제 실패: {e}")
            raise HTTPException(status_code=500, detail="하이브리드 분석 삭제 중 오류가 발생했습니다")
    
    async def perform_comprehensive_analysis(self, hybrid_id: str) -> HybridAnalysis:
        """종합 분석 수행"""
        try:
            hybrid_doc = await self.get_hybrid_analysis(hybrid_id)
            if not hybrid_doc:
                raise HTTPException(status_code=404, detail="하이브리드 분석을 찾을 수 없습니다")
            
            # 각 문서별 분석 결과 수집
            resume_analysis = None
            cover_letter_analysis = None
            portfolio_analysis = None
            
            if hybrid_doc.resume_id:
                resume_analysis = await self._get_resume_analysis(hybrid_doc.resume_id)
            
            if hybrid_doc.cover_letter_id:
                cover_letter_analysis = await self._get_cover_letter_analysis(hybrid_doc.cover_letter_id)
            
            if hybrid_doc.portfolio_id:
                portfolio_analysis = await self._get_portfolio_analysis(hybrid_doc.portfolio_id)
            
            # 교차 참조 분석
            cross_references = await self._perform_cross_reference_analysis(
                resume_analysis, cover_letter_analysis, portfolio_analysis
            )
            
            # 종합 점수 계산
            overall_score = self._calculate_overall_score(
                resume_analysis, cover_letter_analysis, portfolio_analysis
            )
            
            # 일관성 점수 계산
            consistency_score = self._calculate_consistency_score(cross_references)
            
            # 완성도 점수 계산
            completeness_score = self._calculate_completeness_score(
                resume_analysis, cover_letter_analysis, portfolio_analysis
            )
            
            # 논리성 점수 계산
            coherence_score = self._calculate_coherence_score(
                resume_analysis, cover_letter_analysis, portfolio_analysis
            )
            
            # 분석 결과 생성
            analysis = HybridAnalysis(
                applicant_id=hybrid_doc.applicant_id,
                analysis_type=HybridAnalysisType.COMPREHENSIVE,
                integrated_document_type=hybrid_doc.integrated_document_type,
                resume_id=hybrid_doc.resume_id,
                cover_letter_id=hybrid_doc.cover_letter_id,
                portfolio_id=hybrid_doc.portfolio_id,
                overall_score=overall_score,
                consistency_score=consistency_score,
                completeness_score=completeness_score,
                coherence_score=coherence_score,
                summary=self._generate_comprehensive_summary(
                    resume_analysis, cover_letter_analysis, portfolio_analysis
                ),
                strengths=self._extract_strengths(
                    resume_analysis, cover_letter_analysis, portfolio_analysis
                ),
                weaknesses=self._extract_weaknesses(
                    resume_analysis, cover_letter_analysis, portfolio_analysis
                ),
                recommendations=self._generate_recommendations(
                    resume_analysis, cover_letter_analysis, portfolio_analysis
                ),
                resume_analysis=resume_analysis,
                cover_letter_analysis=cover_letter_analysis,
                portfolio_analysis=portfolio_analysis,
                cross_references=cross_references,
                contradictions=self._find_contradictions(cross_references),
                reinforcements=self._find_reinforcements(cross_references),
                model_used="hybrid-comprehensive-v1",
                confidence=0.85
            )
            
            # 분석 결과 저장
            analysis_id = await self.save_analysis_result(hybrid_id, analysis)
            logger.info(f"종합 분석 완료: {analysis_id}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"종합 분석 실패: {e}")
            raise HTTPException(status_code=500, detail="종합 분석 중 오류가 발생했습니다")
    
    async def _get_resume_analysis(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """이력서 분석 결과 조회"""
        try:
            resume_data = await self.db["resumes"].find_one({"_id": resume_id})
            if resume_data and "analysis_results" in resume_data:
                return resume_data["analysis_results"][-1] if resume_data["analysis_results"] else None
            return None
        except Exception as e:
            logger.error(f"이력서 분석 결과 조회 실패: {e}")
            return None
    
    async def _get_cover_letter_analysis(self, cover_letter_id: str) -> Optional[Dict[str, Any]]:
        """자기소개서 분석 결과 조회"""
        try:
            cover_letter_data = await self.db["cover_letters"].find_one({"_id": cover_letter_id})
            if cover_letter_data and "analysis_results" in cover_letter_data:
                return cover_letter_data["analysis_results"][-1] if cover_letter_data["analysis_results"] else None
            return None
        except Exception as e:
            logger.error(f"자기소개서 분석 결과 조회 실패: {e}")
            return None
    
    async def _get_portfolio_analysis(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """포트폴리오 분석 결과 조회"""
        try:
            portfolio_data = await self.db["portfolios"].find_one({"_id": portfolio_id})
            if portfolio_data and "analysis_results" in portfolio_data:
                return portfolio_data["analysis_results"][-1] if portfolio_data["analysis_results"] else None
            return None
        except Exception as e:
            logger.error(f"포트폴리오 분석 결과 조회 실패: {e}")
            return None
    
    async def _perform_cross_reference_analysis(self, resume_analysis: Optional[Dict], 
                                              cover_letter_analysis: Optional[Dict], 
                                              portfolio_analysis: Optional[Dict]) -> Dict[str, Any]:
        """교차 참조 분석 수행"""
        cross_references = {}
        
        # 기술 스택 교차 참조
        if resume_analysis and portfolio_analysis:
            resume_skills = resume_analysis.get("skills", {})
            portfolio_skills = portfolio_analysis.get("technology_analysis", {})
            
            cross_references["skills"] = {
                "resume_skills": resume_skills,
                "portfolio_skills": portfolio_skills,
                "consistency_score": self._calculate_skill_consistency(resume_skills, portfolio_skills)
            }
        
        # 경력 정보 교차 참조
        if resume_analysis and cover_letter_analysis:
            resume_experience = resume_analysis.get("experience_analysis", {})
            cover_letter_experience = cover_letter_analysis.get("job_suitability", {})
            
            cross_references["experience"] = {
                "resume_experience": resume_experience,
                "cover_letter_experience": cover_letter_experience,
                "consistency_score": self._calculate_experience_consistency(resume_experience, cover_letter_experience)
            }
        
        return cross_references
    
    def _calculate_overall_score(self, resume_analysis: Optional[Dict], 
                               cover_letter_analysis: Optional[Dict], 
                               portfolio_analysis: Optional[Dict]) -> float:
        """종합 점수 계산"""
        scores = []
        weights = []
        
        if resume_analysis:
            scores.append(resume_analysis.get("overall_score", 0))
            weights.append(0.4)  # 이력서 가중치 40%
        
        if cover_letter_analysis:
            scores.append(cover_letter_analysis.get("overall_score", 0))
            weights.append(0.3)  # 자기소개서 가중치 30%
        
        if portfolio_analysis:
            scores.append(portfolio_analysis.get("overall_score", 0))
            weights.append(0.3)  # 포트폴리오 가중치 30%
        
        if not scores:
            return 0.0
        
        # 가중 평균 계산
        total_weight = sum(weights)
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        
        return round(weighted_sum / total_weight, 2)
    
    def _calculate_consistency_score(self, cross_references: Dict[str, Any]) -> float:
        """일관성 점수 계산"""
        if not cross_references:
            return 0.0
        
        consistency_scores = []
        for ref_type, ref_data in cross_references.items():
            if "consistency_score" in ref_data:
                consistency_scores.append(ref_data["consistency_score"])
        
        return round(sum(consistency_scores) / len(consistency_scores), 2) if consistency_scores else 0.0
    
    def _calculate_completeness_score(self, resume_analysis: Optional[Dict], 
                                    cover_letter_analysis: Optional[Dict], 
                                    portfolio_analysis: Optional[Dict]) -> float:
        """완성도 점수 계산"""
        completeness_scores = []
        
        if resume_analysis:
            completeness_scores.append(resume_analysis.get("completeness_score", 0))
        
        if cover_letter_analysis:
            completeness_scores.append(cover_letter_analysis.get("completeness_score", 0))
        
        if portfolio_analysis:
            completeness_scores.append(portfolio_analysis.get("completeness_score", 0))
        
        return round(sum(completeness_scores) / len(completeness_scores), 2) if completeness_scores else 0.0
    
    def _calculate_coherence_score(self, resume_analysis: Optional[Dict], 
                                 cover_letter_analysis: Optional[Dict], 
                                 portfolio_analysis: Optional[Dict]) -> float:
        """논리성 점수 계산"""
        coherence_scores = []
        
        if resume_analysis:
            coherence_scores.append(resume_analysis.get("clarity_score", 0))
        
        if cover_letter_analysis:
            coherence_scores.append(cover_letter_analysis.get("clarity_score", 0))
        
        if portfolio_analysis:
            coherence_scores.append(portfolio_analysis.get("presentation_score", 0))
        
        return round(sum(coherence_scores) / len(coherence_scores), 2) if coherence_scores else 0.0
    
    def _generate_comprehensive_summary(self, resume_analysis: Optional[Dict], 
                                      cover_letter_analysis: Optional[Dict], 
                                      portfolio_analysis: Optional[Dict]) -> str:
        """종합 요약 생성"""
        summary_parts = []
        
        if resume_analysis:
            summary_parts.append(f"이력서: {resume_analysis.get('summary', '분석 완료')}")
        
        if cover_letter_analysis:
            summary_parts.append(f"자기소개서: {cover_letter_analysis.get('summary', '분석 완료')}")
        
        if portfolio_analysis:
            summary_parts.append(f"포트폴리오: {portfolio_analysis.get('summary', '분석 완료')}")
        
        return " | ".join(summary_parts) if summary_parts else "종합 분석이 완료되었습니다."
    
    def _extract_strengths(self, resume_analysis: Optional[Dict], 
                          cover_letter_analysis: Optional[Dict], 
                          portfolio_analysis: Optional[Dict]) -> List[str]:
        """강점 추출"""
        strengths = []
        
        if resume_analysis:
            strengths.extend(resume_analysis.get("strengths", []))
        
        if cover_letter_analysis:
            strengths.extend(cover_letter_analysis.get("strengths", []))
        
        if portfolio_analysis:
            strengths.extend(portfolio_analysis.get("strengths", []))
        
        return list(set(strengths))  # 중복 제거
    
    def _extract_weaknesses(self, resume_analysis: Optional[Dict], 
                           cover_letter_analysis: Optional[Dict], 
                           portfolio_analysis: Optional[Dict]) -> List[str]:
        """개선점 추출"""
        weaknesses = []
        
        if resume_analysis:
            weaknesses.extend(resume_analysis.get("weaknesses", []))
        
        if cover_letter_analysis:
            weaknesses.extend(cover_letter_analysis.get("weaknesses", []))
        
        if portfolio_analysis:
            weaknesses.extend(portfolio_analysis.get("weaknesses", []))
        
        return list(set(weaknesses))  # 중복 제거
    
    def _generate_recommendations(self, resume_analysis: Optional[Dict], 
                                cover_letter_analysis: Optional[Dict], 
                                portfolio_analysis: Optional[Dict]) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        if resume_analysis:
            recommendations.extend(resume_analysis.get("recommendations", []))
        
        if cover_letter_analysis:
            recommendations.extend(cover_letter_analysis.get("recommendations", []))
        
        if portfolio_analysis:
            recommendations.extend(portfolio_analysis.get("recommendations", []))
        
        return list(set(recommendations))  # 중복 제거
    
    def _find_contradictions(self, cross_references: Dict[str, Any]) -> List[str]:
        """모순점 찾기"""
        contradictions = []
        
        for ref_type, ref_data in cross_references.items():
            if ref_data.get("consistency_score", 100) < 70:
                contradictions.append(f"{ref_type}에서 일관성 문제 발견")
        
        return contradictions
    
    def _find_reinforcements(self, cross_references: Dict[str, Any]) -> List[str]:
        """강화점 찾기"""
        reinforcements = []
        
        for ref_type, ref_data in cross_references.items():
            if ref_data.get("consistency_score", 0) > 90:
                reinforcements.append(f"{ref_type}에서 높은 일관성 확인")
        
        return reinforcements
    
    def _calculate_skill_consistency(self, resume_skills: Dict, portfolio_skills: Dict) -> float:
        """기술 스택 일관성 계산"""
        # 간단한 일관성 계산 로직
        return 85.0  # 예시 값
    
    def _calculate_experience_consistency(self, resume_experience: Dict, cover_letter_experience: Dict) -> float:
        """경력 정보 일관성 계산"""
        # 간단한 일관성 계산 로직
        return 90.0  # 예시 값
    
    async def save_analysis_result(self, hybrid_id: str, analysis: HybridAnalysis) -> str:
        """분석 결과 저장"""
        try:
            analysis_dict = analysis.dict()
            analysis_id = await self.create("hybrid_analyses", analysis_dict)
            
            # 하이브리드 문서에 분석 결과 추가
            await self.db[self.collection].update_one(
                {"_id": hybrid_id},
                {"$push": {"analysis_results": analysis_dict}}
            )
            
            logger.info(f"하이브리드 분석 결과 저장 완료: {analysis_id}")
            return analysis_id
        except Exception as e:
            logger.error(f"하이브리드 분석 결과 저장 실패: {e}")
            raise HTTPException(status_code=500, detail="분석 결과 저장 중 오류가 발생했습니다")
    
    async def search_hybrid_analyses(self, search_request: HybridSearchRequest) -> List[HybridDocument]:
        """하이브리드 분석 검색"""
        try:
            query = {"$text": {"$search": search_request.query}}
            
            filters = {}
            if search_request.analysis_type:
                filters["analysis_type"] = search_request.analysis_type
            if search_request.integrated_document_type:
                filters["integrated_document_type"] = search_request.integrated_document_type
            if search_request.min_score:
                filters["overall_score"] = {"$gte": search_request.min_score}
            
            if filters:
                query = {"$and": [query, filters]}
            
            hybrid_data = await self.get_list(
                self.collection, query, 0, search_request.limit, "created_at", -1
            )
            return [HybridDocument(**hybrid) for hybrid in hybrid_data]
        except Exception as e:
            logger.error(f"하이브리드 분석 검색 실패: {e}")
            raise HTTPException(status_code=500, detail="하이브리드 분석 검색 중 오류가 발생했습니다")
    
    async def compare_hybrid_analyses(self, comparison_request: HybridComparisonRequest) -> Dict[str, Any]:
        """하이브리드 분석 비교"""
        try:
            hybrid_analyses = []
            for hybrid_id in comparison_request.hybrid_ids:
                hybrid = await self.get_hybrid_analysis(hybrid_id)
                if hybrid:
                    hybrid_analyses.append(hybrid)
            
            if len(hybrid_analyses) < 2:
                raise HTTPException(status_code=400, detail="비교할 분석이 2개 이상 필요합니다")
            
            comparison_result = {
                "hybrid_ids": comparison_request.hybrid_ids,
                "comparison_type": comparison_request.comparison_type,
                "comparison_data": {}
            }
            
            # 비교 유형에 따른 분석
            if comparison_request.comparison_type == "overall":
                comparison_result["comparison_data"] = self._compare_overall_scores(hybrid_analyses)
            elif comparison_request.comparison_type == "consistency":
                comparison_result["comparison_data"] = self._compare_consistency_scores(hybrid_analyses)
            elif comparison_request.comparison_type == "completeness":
                comparison_result["comparison_data"] = self._compare_completeness_scores(hybrid_analyses)
            
            return comparison_result
        except Exception as e:
            logger.error(f"하이브리드 분석 비교 실패: {e}")
            raise HTTPException(status_code=500, detail="하이브리드 분석 비교 중 오류가 발생했습니다")
    
    def _compare_overall_scores(self, hybrid_analyses: List[HybridDocument]) -> Dict[str, Any]:
        """종합 점수 비교"""
        scores = {}
        for hybrid in hybrid_analyses:
            if hybrid.analysis_results:
                latest_analysis = hybrid.analysis_results[-1]
                scores[hybrid.id] = latest_analysis.get("overall_score", 0)
        
        return {
            "scores": scores,
            "average": sum(scores.values()) / len(scores) if scores else 0,
            "highest": max(scores.values()) if scores else 0,
            "lowest": min(scores.values()) if scores else 0
        }
    
    def _compare_consistency_scores(self, hybrid_analyses: List[HybridDocument]) -> Dict[str, Any]:
        """일관성 점수 비교"""
        scores = {}
        for hybrid in hybrid_analyses:
            if hybrid.analysis_results:
                latest_analysis = hybrid.analysis_results[-1]
                scores[hybrid.id] = latest_analysis.get("consistency_score", 0)
        
        return {
            "scores": scores,
            "average": sum(scores.values()) / len(scores) if scores else 0,
            "highest": max(scores.values()) if scores else 0,
            "lowest": min(scores.values()) if scores else 0
        }
    
    def _compare_completeness_scores(self, hybrid_analyses: List[HybridDocument]) -> Dict[str, Any]:
        """완성도 점수 비교"""
        scores = {}
        for hybrid in hybrid_analyses:
            if hybrid.analysis_results:
                latest_analysis = hybrid.analysis_results[-1]
                scores[hybrid.id] = latest_analysis.get("completeness_score", 0)
        
        return {
            "scores": scores,
            "average": sum(scores.values()) / len(scores) if scores else 0,
            "highest": max(scores.values()) if scores else 0,
            "lowest": min(scores.values()) if scores else 0
        }
    
    async def get_hybrid_statistics(self) -> HybridStatistics:
        """하이브리드 분석 통계 조회"""
        try:
            total_analyses = await self.count(self.collection)
            
            # 평균 종합 점수 계산
            pipeline = [
                {"$unwind": "$analysis_results"},
                {"$group": {"_id": None, "avg_score": {"$avg": "$analysis_results.overall_score"}}}
            ]
            cursor = self.db[self.collection].aggregate(pipeline)
            result = await cursor.to_list(length=1)
            average_overall_score = result[0]["avg_score"] if result else 0.0
            
            # 분석 타입 분포
            pipeline = [
                {"$group": {"_id": "$analysis_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            cursor = self.db[self.collection].aggregate(pipeline)
            analysis_type_distribution = await cursor.to_list(length=10)
            
            # 문서 타입 분포
            pipeline = [
                {"$group": {"_id": "$integrated_document_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            cursor = self.db[self.collection].aggregate(pipeline)
            document_type_distribution = await cursor.to_list(length=10)
            
            # 점수 분포
            pipeline = [
                {"$unwind": "$analysis_results"},
                {"$bucket": {
                    "groupBy": "$analysis_results.overall_score",
                    "boundaries": [0, 20, 40, 60, 80, 100],
                    "default": "100+",
                    "output": {"count": {"$sum": 1}}
                }}
            ]
            cursor = self.db[self.collection].aggregate(pipeline)
            score_distribution = await cursor.to_list(length=10)
            
            return HybridStatistics(
                total_analyses=total_analyses,
                average_overall_score=average_overall_score,
                analysis_type_distribution={item["_id"]: item["count"] for item in analysis_type_distribution},
                document_type_distribution={item["_id"]: item["count"] for item in document_type_distribution},
                score_distribution={item["_id"]: item["count"] for item in score_distribution}
            )
        except Exception as e:
            logger.error(f"하이브리드 분석 통계 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="하이브리드 분석 통계 조회 중 오류가 발생했습니다")
