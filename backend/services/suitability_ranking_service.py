from typing import List, Dict, Any, Optional
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SuitabilityRankingService:
    """지원자 적합도 랭킹 계산 서비스"""
    
    def __init__(self, db: Database):
        self.db = db
        
    def calculate_all_rankings(self) -> Dict[str, Any]:
        """모든 지원자의 적합도 랭킹을 계산합니다."""
        try:
            # 모든 지원자 조회
            applicants = list(self.db.applicants.find({}))
            
            if not applicants:
                logger.info("랭킹을 계산할 지원자가 없습니다.")
                return {"message": "랭킹을 계산할 지원자가 없습니다."}
            
            # 각 지원자별 점수 계산
            applicant_scores = []
            for applicant in applicants:
                scores = self._calculate_applicant_scores(applicant)
                applicant_scores.append({
                    "applicant_id": str(applicant["_id"]),
                    "name": applicant.get("name", ""),
                    "scores": scores
                })
            
            # 각 항목별 랭킹 계산
            rankings = self._calculate_rankings(applicant_scores)
            
            # 데이터베이스에 랭킹 저장
            self._save_rankings(rankings)
            
            logger.info(f"총 {len(applicants)}명의 지원자 랭킹 계산 완료")
            return {
                "message": f"총 {len(applicants)}명의 지원자 랭킹 계산 완료",
                "total_applicants": len(applicants),
                "rankings": rankings
            }
            
        except Exception as e:
            logger.error(f"랭킹 계산 중 오류 발생: {str(e)}")
            raise Exception(f"랭킹 계산 실패: {str(e)}")
    
    def _calculate_applicant_scores(self, applicant: Dict[str, Any]) -> Dict[str, float]:
        """개별 지원자의 점수를 계산합니다."""
        scores = {
            "resume": 0.0,
            "coverLetter": 0.0,
            "portfolio": 0.0,
            "total": 0.0
        }
        
        # 이력서 점수 계산
        if applicant.get("analysisScore"):
            scores["resume"] = float(applicant["analysisScore"])
        
        # 자기소개서 점수 계산
        if applicant.get("coverLetterAnalysis"):
            cover_letter_score = self._extract_cover_letter_score(applicant["coverLetterAnalysis"])
            scores["coverLetter"] = cover_letter_score
        
        # 포트폴리오 점수 계산
        if applicant.get("portfolioAnalysis"):
            portfolio_score = self._extract_portfolio_score(applicant["portfolioAnalysis"])
            scores["portfolio"] = portfolio_score
        
        # 총점 계산 (가중 평균)
        total_score = self._calculate_weighted_total(scores)
        scores["total"] = total_score
        
        return scores
    
    def _extract_cover_letter_score(self, analysis_data: Dict[str, Any]) -> float:
        """자기소개서 분석 결과에서 점수를 추출합니다."""
        try:
            if isinstance(analysis_data, dict):
                # 분석 결과가 딕셔너리인 경우
                if "overall_score" in analysis_data:
                    return float(analysis_data["overall_score"])
                elif "total_score" in analysis_data:
                    return float(analysis_data["total_score"])
                else:
                    # 개별 항목 점수들의 평균 계산
                    scores = []
                    for key, value in analysis_data.items():
                        if isinstance(value, dict) and "score" in value:
                            scores.append(float(value["score"]))
                    
                    if scores:
                        return sum(scores) / len(scores)
            
            # 문자열인 경우 숫자 추출
            if isinstance(analysis_data, str):
                import re
                numbers = re.findall(r'\d+', analysis_data)
                if numbers:
                    return float(numbers[0])
            
            return 0.0
        except Exception as e:
            logger.warning(f"자기소개서 점수 추출 실패: {str(e)}")
            return 0.0
    
    def _extract_portfolio_score(self, analysis_data: Dict[str, Any]) -> float:
        """포트폴리오 분석 결과에서 점수를 추출합니다."""
        try:
            if isinstance(analysis_data, dict):
                if "overall_score" in analysis_data:
                    return float(analysis_data["overall_score"])
                elif "total_score" in analysis_data:
                    return float(analysis_data["total_score"])
                else:
                    scores = []
                    for key, value in analysis_data.items():
                        if isinstance(value, dict) and "score" in value:
                            scores.append(float(value["score"]))
                    
                    if scores:
                        return sum(scores) / len(scores)
            
            if isinstance(analysis_data, str):
                import re
                numbers = re.findall(r'\d+', analysis_data)
                if numbers:
                    return float(numbers[0])
            
            return 0.0
        except Exception as e:
            logger.warning(f"포트폴리오 점수 추출 실패: {str(e)}")
            return 0.0
    
    def _calculate_weighted_total(self, scores: Dict[str, float]) -> float:
        """가중 평균으로 총점을 계산합니다."""
        weights = {
            "resume": 0.4,      # 이력서 40%
            "coverLetter": 0.3, # 자기소개서 30%
            "portfolio": 0.3    # 포트폴리오 30%
        }
        
        total = 0.0
        total_weight = 0.0
        
        for key, score in scores.items():
            if key != "total" and score > 0:
                total += score * weights[key]
                total_weight += weights[key]
        
        if total_weight > 0:
            return round(total / total_weight, 1)
        return 0.0
    
    def _calculate_rankings(self, applicant_scores: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """각 항목별 랭킹을 계산합니다."""
        rankings = {
            "resume": [],
            "coverLetter": [],
            "portfolio": [],
            "total": []
        }
        
        # 각 항목별로 점수 기준 정렬하여 랭킹 계산
        for category in rankings.keys():
            category_scores = []
            for applicant in applicant_scores:
                if applicant["scores"][category] > 0:
                    category_scores.append({
                        "applicant_id": applicant["applicant_id"],
                        "name": applicant["name"],
                        "score": applicant["scores"][category]
                    })
            
            # 점수 기준 내림차순 정렬
            category_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # 랭킹 부여
            for rank, item in enumerate(category_scores, 1):
                item["rank"] = rank
                rankings[category].append(item)
        
        return rankings
    
    def _save_rankings(self, rankings: Dict[str, List[Dict[str, Any]]]):
        """계산된 랭킹을 데이터베이스에 저장합니다."""
        try:
            # 기존 랭킹 데이터 삭제
            self.db.applicant_rankings.delete_many({})
            
            # 새로운 랭킹 데이터 저장
            for category, category_rankings in rankings.items():
                for ranking in category_rankings:
                    ranking_data = {
                        "category": category,
                        "applicant_id": ranking["applicant_id"],
                        "name": ranking["name"],
                        "score": ranking["score"],
                        "rank": ranking["rank"],
                        "created_at": datetime.utcnow()
                    }
                    self.db.applicant_rankings.insert_one(ranking_data)
            
            # 지원자 테이블에 랭킹 정보 업데이트
            for category, category_rankings in rankings.items():
                for ranking in category_rankings:
                    self.db.applicants.update_one(
                        {"_id": ObjectId(ranking["applicant_id"])},
                        {"$set": {f"ranks.{category}": ranking["rank"]}}
                    )
            
            logger.info("랭킹 데이터 저장 완료")
            
        except Exception as e:
            logger.error(f"랭킹 데이터 저장 실패: {str(e)}")
            raise Exception(f"랭킹 데이터 저장 실패: {str(e)}")
    
    def get_applicant_rankings(self, applicant_id: str) -> Dict[str, Any]:
        """특정 지원자의 랭킹 정보를 조회합니다."""
        try:
            applicant = self.db.applicants.find_one({"_id": ObjectId(applicant_id)})
            if not applicant:
                return {}
            
            return {
                "resume": applicant.get("ranks", {}).get("resume", 0),
                "coverLetter": applicant.get("ranks", {}).get("coverLetter", 0),
                "portfolio": applicant.get("ranks", {}).get("portfolio", 0),
                "total": applicant.get("ranks", {}).get("total", 0)
            }
            
        except Exception as e:
            logger.error(f"지원자 랭킹 조회 실패: {str(e)}")
            return {}
    
    def get_top_rankings(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """특정 카테고리의 상위 랭킹을 조회합니다."""
        try:
            rankings = list(self.db.applicant_rankings.find(
                {"category": category}
            ).sort("rank", 1).limit(limit))
            
            return rankings
            
        except Exception as e:
            logger.error(f"상위 랭킹 조회 실패: {str(e)}")
            return []
