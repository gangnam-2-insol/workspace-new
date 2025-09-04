"""
자소서 자동 분석 서비스
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from models.cover_letter_models import (
    CoverLetterAnalysis,
    CoverLetterUploadRequest,
    EvaluationRubric,
    JobSuitability,
    SentenceImprovement,
    STARAnalysis,
    TopStrength,
)
from modules.core.services.llm_providers.base_provider import (
    LLMProviderFactory,
    LLMResponse,
)
from utils.text_extractor import extract_text_from_file, validate_upload_file

from .prompts import get_analysis_prompt

logger = logging.getLogger(__name__)


class CoverLetterAnalyzer:
    """자소서 자동 분석 서비스"""

    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.llm_provider = None
        self._initialize_llm_provider()

    def _initialize_llm_provider(self) -> None:
        """LLM 프로바이더 초기화"""
        try:
            provider_name = self.llm_config.get("provider", "openai")
            self.llm_provider = LLMProviderFactory.create_provider(provider_name, self.llm_config)

            if self.llm_provider:
                logger.info(f"LLM 프로바이더 초기화 성공: {provider_name}")
                # is_healthy() 체크 제거 - 이벤트 루프 충돌 방지
            else:
                logger.error(f"LLM 프로바이더 초기화 실패: {provider_name}")

        except Exception as e:
            logger.error(f"LLM 프로바이더 초기화 중 오류: {str(e)}")

    async def analyze_cover_letter_text(
        self,
        text_content: str,
        filename: str = "cover_letter.txt",
        job_description: str = "",
        analysis_type: str = "comprehensive"
    ) -> CoverLetterAnalysis:
        """
        DB에 저장된 텍스트 데이터를 직접 분석

        Args:
            text_content: 자소서 텍스트 내용
            filename: 파일명 (참고용)
            job_description: 직무 설명
            analysis_type: 분석 유형

        Returns:
            분석 결과
        """
        start_time = time.time()

        try:
            # 1. 텍스트 유효성 검사
            if not text_content or not text_content.strip():
                raise ValueError("자소서 내용이 비어있습니다.")

            # 2. 텍스트 전처리
            extracted_text = text_content.strip()

            # 3. LLM 분석 실행
            analysis_result = await self._run_llm_analysis(
                extracted_text,
                job_description,
                analysis_type
            )

            # 4. 결과 반환
            return CoverLetterAnalysis(
                filename=filename,
                original_text=extracted_text,
                extracted_text=extracted_text,
                analysis_result=analysis_result,
                processing_time=time.time() - start_time,
                status="success"
            )

        except Exception as e:
            logger.error(f"자소서 텍스트 분석 실패: {filename}, 오류: {str(e)}")
            return CoverLetterAnalysis(
                filename=filename,
                original_text=text_content,
                extracted_text=text_content,
                analysis_result=None,
                processing_time=time.time() - start_time,
                status="error",
                error_message=str(e)
            )

    async def analyze_cover_letter(
        self,
        file_bytes: bytes,
        filename: str,
        job_description: str = "",
        analysis_type: str = "comprehensive"
    ) -> CoverLetterAnalysis:
        """
        자소서 분석 실행

        Args:
            file_bytes: 파일 바이트 데이터
            filename: 파일명
            job_description: 직무 설명
            analysis_type: 분석 유형

        Returns:
            분석 결과
        """
        start_time = time.time()

        try:
            # 1. 파일 유효성 검사
            if not validate_upload_file(file_bytes, filename):
                raise ValueError("업로드 파일이 유효하지 않습니다.")

            # 2. 텍스트 추출
            extracted_text, file_type = extract_text_from_file(file_bytes, filename)

            # 3. 개인정보 마스킹 (선택사항)
            masked_text = await self._mask_personal_info(extracted_text)

            # 4. LLM 분석 실행
            analysis_result = await self._run_llm_analysis(
                masked_text, job_description, analysis_type
            )

            # 5. 결과 정제 및 검증
            cleaned_result = self._clean_analysis_result(analysis_result)

            # 6. 분석 결과 객체 생성
            analysis = CoverLetterAnalysis(
                filename=filename,
                original_text=masked_text,
                job_description=job_description,
                file_size=len(file_bytes),
                file_type=file_type,
                processing_time=time.time() - start_time,
                llm_model_used=self.llm_config.get("model_name", "unknown"),
                status="completed",
                **cleaned_result
            )

            logger.info(f"자소서 분석 완료: {filename} ({analysis.processing_time:.2f}초)")
            return analysis

        except Exception as e:
            logger.error(f"자소서 분석 실패: {filename}, 오류: {str(e)}")
            # 에러 상태로 분석 객체 생성
            return CoverLetterAnalysis(
                filename=filename,
                original_text="",
                job_description=job_description,
                file_size=len(file_bytes),
                file_type="unknown",
                processing_time=time.time() - start_time,
                status="error"
            )

    async def _mask_personal_info(self, text: str) -> str:
        """개인정보 마스킹 처리"""
        try:
            if not self.llm_provider:
                return text

            prompt = get_analysis_prompt("masking", text=text)
            response = await self.llm_provider.safe_generate(prompt)

            if response:
                try:
                    result = json.loads(response)
                    return result.get("masked_text", text)
                except json.JSONDecodeError:
                    logger.warning("개인정보 마스킹 응답 파싱 실패, 원본 텍스트 사용")

            return text

        except Exception as e:
            logger.warning(f"개인정보 마스킹 실패: {str(e)}, 원본 텍스트 사용")
            return text

    async def _run_llm_analysis(
        self,
        text: str,
        job_description: str,
        analysis_type: str
    ) -> Dict[str, Any]:
        """LLM을 사용한 분석 실행"""
        try:
            if not self.llm_provider:
                raise RuntimeError("LLM 프로바이더가 초기화되지 않았습니다.")

            # 프롬프트 생성
            prompt = get_analysis_prompt(
                analysis_type,
                cover_letter_text=text,
                job_description=job_description
            )

            # LLM 응답 생성
            response = await self.llm_provider.safe_generate(prompt)

            if not response:
                raise RuntimeError("LLM 응답을 받지 못했습니다.")

            # JSON 파싱
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"LLM 응답 JSON 파싱 실패: {str(e)}")
                logger.error(f"응답 내용: {response[:500]}...")
                raise ValueError("LLM 응답을 JSON으로 파싱할 수 없습니다.")

        except Exception as e:
            logger.error(f"LLM 분석 실행 실패: {str(e)}")
            raise

    def _clean_analysis_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """분석 결과 정제 및 검증"""
        cleaned = {}

        try:
            # 요약
            if "summary" in raw_result:
                cleaned["summary"] = str(raw_result["summary"]).strip()

            # 핵심 강점
            if "top_strengths" in raw_result and isinstance(raw_result["top_strengths"], list):
                cleaned["top_strengths"] = []
                for strength in raw_result["top_strengths"]:
                    if isinstance(strength, dict):
                        cleaned_strength = TopStrength(
                            strength=str(strength.get("strength", "")),
                            evidence=str(strength.get("evidence", "")),
                            confidence=float(strength.get("confidence", 0.0))
                        )
                        cleaned["top_strengths"].append(cleaned_strength)

            # STAR 사례
            if "star_cases" in raw_result and isinstance(raw_result["star_cases"], list):
                cleaned["star_cases"] = []
                for star in raw_result["star_cases"]:
                    if isinstance(star, dict):
                        cleaned_star = STARAnalysis(
                            situation=str(star.get("s", "")),
                            task=str(star.get("t", "")),
                            action=str(star.get("a", "")),
                            result=str(star.get("r", "")),
                            evidence_sentence_indices=star.get("evidence_sentence_indices", [])
                        )
                        cleaned["star_cases"].append(cleaned_star)

            # 직무 적합성
            if "job_suitability" in raw_result and isinstance(raw_result["job_suitability"], dict):
                suitability = raw_result["job_suitability"]
                cleaned["job_suitability"] = JobSuitability(
                    score=int(suitability.get("score", 0)),
                    matched_skills=suitability.get("matched_skills", []),
                    missing_skills=suitability.get("missing_skills", []),
                    explanation=str(suitability.get("explanation", ""))
                )

            # 평가 루브릭
            if "evaluation_rubric" in raw_result and isinstance(raw_result["evaluation_rubric"], dict):
                rubric = raw_result["evaluation_rubric"]
                cleaned["evaluation_rubric"] = EvaluationRubric(
                    job_relevance=float(rubric.get("job_relevance", 0.0)),
                    problem_solving=float(rubric.get("problem_solving", 0.0)),
                    impact=float(rubric.get("impact", 0.0)),
                    clarity=float(rubric.get("clarity", 0.0)),
                    professionalism=float(rubric.get("professionalism", 0.0)),
                    grammar=float(rubric.get("grammar", 0.0)),
                    keyword_coverage=float(rubric.get("keyword_coverage", 0.0)),
                    overall_score=float(rubric.get("overall_score", 0.0))
                )

            # 문장 개선 제안
            if "sentence_improvements" in raw_result and isinstance(raw_result["sentence_improvements"], list):
                cleaned["sentence_improvements"] = []
                for improvement in raw_result["sentence_improvements"]:
                    if isinstance(improvement, dict):
                        cleaned_improvement = SentenceImprovement(
                            original=str(improvement.get("original", "")),
                            improved=str(improvement.get("improved", "")),
                            improvement_type=str(improvement.get("improvement_type", ""))
                        )
                        cleaned["sentence_improvements"].append(cleaned_improvement)

            logger.info("분석 결과 정제 완료")
            return cleaned

        except Exception as e:
            logger.error(f"분석 결과 정제 실패: {str(e)}")
            return {}

    async def analyze_specific_aspect(
        self,
        text: str,
        aspect: str,
        job_description: str = ""
    ) -> Dict[str, Any]:
        """특정 측면만 분석"""
        try:
            result = await self._run_llm_analysis(text, job_description, aspect)
            return self._clean_analysis_result(result)
        except Exception as e:
            logger.error(f"특정 측면 분석 실패: {aspect}, 오류: {str(e)}")
            return {}

    def get_analysis_summary(self, analysis: CoverLetterAnalysis) -> Dict[str, Any]:
        """분석 결과 요약"""
        summary = {
            "id": str(analysis.id),
            "filename": analysis.filename,
            "status": analysis.status,
            "processing_time": analysis.processing_time,
            "file_size": analysis.file_size,
            "file_type": analysis.file_type
        }

        if analysis.summary:
            summary["summary"] = analysis.summary

        if analysis.top_strengths:
            summary["strengths_count"] = len(analysis.top_strengths)

        if analysis.star_cases:
            summary["star_cases_count"] = len(analysis.star_cases)

        if analysis.job_suitability:
            summary["job_suitability_score"] = analysis.job_suitability.score

        if analysis.evaluation_rubric:
            summary["overall_score"] = analysis.evaluation_rubric.overall_score

        return summary

    def is_healthy(self) -> bool:
        """서비스 상태 확인"""
        return self.llm_provider is not None and self.llm_provider.is_healthy()

    def get_provider_info(self) -> Dict[str, Any]:
        """LLM 프로바이더 정보 반환"""
        if self.llm_provider:
            return self.llm_provider.get_config()
        return {"error": "프로바이더가 초기화되지 않았습니다."}
