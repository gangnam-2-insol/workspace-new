import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import (
    pipeline, 
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification
)
import torch
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class AdvancedAnalysisService:
    """2단계 분석 시스템: Hugging Face + GPT-4o"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🔧 분석 서비스 초기화 - 디바이스: {self.device}")
        
        # 1단계: Hugging Face 모델들
        self._init_huggingface_models()
        
        # 2단계: OpenAI 서비스 (GPT-4o)
        self._init_openai_service()
        
        # 직무별 가중치 설정
        self.job_weights = {
            "개발자": {
                "직무_적합성": 0.4,
                "기술_역량": 0.3,
                "경력_성과": 0.1,
                "문제_해결": 0.1,
                "협업": 0.05,
                "성장성": 0.03,
                "표현력": 0.02
            },
            "기획자": {
                "직무_적합성": 0.3,
                "기술_역량": 0.1,
                "경력_성과": 0.25,
                "문제_해결": 0.2,
                "협업": 0.1,
                "성장성": 0.03,
                "표현력": 0.02
            },
            "디자이너": {
                "직무_적합성": 0.3,
                "기술_역량": 0.2,
                "경력_성과": 0.2,
                "문제_해결": 0.15,
                "협업": 0.1,
                "성장성": 0.03,
                "표현력": 0.02
            },
            "마케터": {
                "직무_적합성": 0.25,
                "기술_역량": 0.1,
                "경력_성과": 0.25,
                "문제_해결": 0.15,
                "협업": 0.15,
                "성장성": 0.05,
                "표현력": 0.05
            }
        }
        
        # 기본 가중치
        self.default_weights = {
            "직무_적합성": 0.25,
            "기술_역량": 0.2,
            "경력_성과": 0.2,
            "문제_해결": 0.15,
            "협업": 0.1,
            "성장성": 0.05,
            "표현력": 0.05
        }
    
    def _init_huggingface_models(self):
        """Hugging Face 모델들 초기화"""
        try:
            logger.info("🚀 Hugging Face 모델 초기화 시작...")
            
            # 1. 임베딩 모델: multi-qa-MiniLM-L6-cos-v1
            logger.info("📊 임베딩 모델 로딩 중...")
            self.embedding_model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1', device=self.device)
            
            # 2. 요약 모델: facebook/bart-large-cnn
            logger.info("📝 요약 모델 로딩 중...")
            self.summary_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
            self.summary_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
            if self.device == "cuda":
                self.summary_model = self.summary_model.to(self.device)
            
            # 3. 분류 모델: facebook/bart-large-mnli
            logger.info("🏷️ 분류 모델 로딩 중...")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if self.device == "cuda" else -1
            )
            
            # 4. 문법 검사 모델: prithivida/grammar_error_correcter_v1
            logger.info("✏️ 문법 검사 모델 로딩 중...")
            self.grammar_tokenizer = AutoTokenizer.from_pretrained("prithivida/grammar_error_correcter_v1")
            self.grammar_model = AutoModelForSeq2SeqLM.from_pretrained("prithivida/grammar_error_correcter_v1")
            if self.device == "cuda":
                self.grammar_model = self.grammar_model.to(self.device)
            
            logger.info("✅ Hugging Face 모델 초기화 완료!")
            
        except Exception as e:
            logger.error(f"❌ Hugging Face 모델 초기화 실패: {e}")
            raise
    
    def _init_openai_service(self):
        """OpenAI 서비스 초기화"""
        try:
            # 기존 openai_service 사용
            from openai_service import OpenAIService
            self.openai_service = OpenAIService()
            logger.info("✅ OpenAI 서비스 초기화 완료!")
        except Exception as e:
            logger.error(f"❌ OpenAI 서비스 초기화 실패: {e}")
            self.openai_service = None
    
    async def analyze_resume_two_stage(self, 
                                     resume_text: str, 
                                     cover_letter_text: str = "",
                                     job_description: str = "",
                                     job_position: str = "개발자") -> Dict[str, Any]:
        """2단계 이력서 분석"""
        try:
            logger.info("🔍 2단계 이력서 분석 시작...")
            
            # 1단계: Hugging Face 모델로 빠른 기계적 평가
            logger.info("📊 1단계: Hugging Face 기계적 평가 시작...")
            stage1_results = await self._stage1_huggingface_analysis(
                resume_text, cover_letter_text, job_description
            )
            
            # 2단계: GPT-4o로 사람다운 종합 평가
            logger.info("🧠 2단계: GPT-4o 종합 평가 시작...")
            stage2_results = await self._stage2_gpt_analysis(
                resume_text, cover_letter_text, stage1_results
            )
            
            # 최종 점수 계산 및 랭킹
            final_score = self._calculate_final_score(
                stage1_results, stage2_results, job_position
            )
            
            # 결과 통합
            analysis_result = {
                "analysis_timestamp": datetime.now().isoformat(),
                "job_position": job_position,
                "stage1_huggingface": stage1_results,
                "stage2_gpt": stage2_results,
                "final_score": final_score,
                "ranking_ready": True
            }
            
            logger.info(f"✅ 2단계 분석 완료! 최종 점수: {final_score:.2f}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ 2단계 분석 실패: {e}")
            raise
    
    async def _stage1_huggingface_analysis(self, 
                                          resume_text: str, 
                                          cover_letter_text: str,
                                          job_description: str) -> Dict[str, Any]:
        """1단계: Hugging Face 모델 기반 분석"""
        try:
            results = {}
            
            # 1. 임베딩 기반 직무 적합성 점수
            if job_description:
                job_fit_score = self._calculate_job_fit_score(resume_text, job_description)
                results["job_fit_score"] = job_fit_score
            
            # 2. 요약 생성
            summary = self._generate_summary(resume_text)
            results["summary"] = summary
            
            # 3. 스킬 분류 및 점수
            skill_scores = self._classify_skills(resume_text)
            results["skill_scores"] = skill_scores
            
            # 4. 문법 점수
            grammar_score = self._check_grammar(resume_text + " " + cover_letter_text)
            results["grammar_score"] = grammar_score
            
            # 5. 텍스트 품질 점수
            text_quality_score = self._analyze_text_quality(resume_text + " " + cover_letter_text)
            results["text_quality_score"] = text_quality_score
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 1단계 분석 실패: {e}")
            return {"error": str(e)}
    
    def _calculate_job_fit_score(self, resume_text: str, job_description: str) -> float:
        """임베딩 기반 직무 적합성 점수 계산"""
        try:
            # 텍스트를 청크로 분할
            resume_chunks = self._split_text_to_chunks(resume_text, max_length=512)
            job_chunks = self._split_text_to_chunks(job_description, max_length=512)
            
            # 임베딩 생성
            resume_embeddings = self.embedding_model.encode(resume_chunks)
            job_embeddings = self.embedding_model.encode(job_chunks)
            
            # 코사인 유사도 계산
            similarities = cosine_similarity(resume_embeddings, job_embeddings)
            
            # 최고 유사도 점수 반환 (0-100 스케일)
            max_similarity = np.max(similarities)
            return float(max_similarity * 100)
            
        except Exception as e:
            logger.error(f"직무 적합성 점수 계산 실패: {e}")
            return 50.0  # 기본값
    
    def _generate_summary(self, text: str, max_length: int = 150) -> str:
        """텍스트 요약 생성"""
        try:
            if len(text) < 100:
                return text
            
            # 텍스트를 적절한 길이로 자르기
            if len(text) > 1024:
                text = text[:1024]
            
            inputs = self.summary_tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            summary_ids = self.summary_model.generate(
                inputs["input_ids"], 
                max_length=max_length, 
                min_length=30, 
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            
            summary = self.summary_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary
            
        except Exception as e:
            logger.error(f"요약 생성 실패: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def _classify_skills(self, text: str) -> Dict[str, float]:
        """스킬 분류 및 점수"""
        try:
            # 일반적인 IT 스킬 카테고리
            skill_categories = [
                "프로그래밍 언어",
                "웹 개발",
                "데이터베이스",
                "클라우드/DevOps",
                "AI/ML",
                "모바일 개발",
                "프로젝트 관리",
                "디자인/UX"
            ]
            
            # Zero-shot 분류로 각 카테고리별 점수 계산
            results = {}
            for category in skill_categories:
                try:
                    classification = self.classifier(
                        text, 
                        candidate_labels=[category, "해당없음"],
                        hypothesis_template="이 텍스트는 {}에 관한 내용입니다."
                    )
                    score = classification['scores'][0] * 100
                    results[category] = round(score, 2)
                except Exception as e:
                    logger.warning(f"스킬 분류 실패 ({category}): {e}")
                    results[category] = 0.0
            
            return results
            
        except Exception as e:
            logger.error(f"스킬 분류 실패: {e}")
            return {"기본": 50.0}
    
    def _check_grammar(self, text: str) -> float:
        """문법 검사 및 점수"""
        try:
            if len(text) < 50:
                return 90.0  # 짧은 텍스트는 기본 높은 점수
            
            # 문법 검사 모델로 텍스트 처리
            inputs = self.grammar_tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            corrected_ids = self.grammar_model.generate(
                inputs["input_ids"],
                max_length=512,
                num_beams=5,
                early_stopping=True
            )
            
            corrected_text = self.grammar_tokenizer.decode(corrected_ids[0], skip_special_tokens=True)
            
            # 원본과 수정된 텍스트 비교로 문법 점수 계산
            original_words = text.split()
            corrected_words = corrected_text.split()
            
            if len(original_words) == 0:
                return 90.0
            
            # 단어 수 변화율로 문법 점수 추정
            change_ratio = abs(len(corrected_words) - len(original_words)) / len(original_words)
            grammar_score = max(0, 100 - (change_ratio * 100))
            
            return round(grammar_score, 2)
            
        except Exception as e:
            logger.error(f"문법 검사 실패: {e}")
            return 75.0  # 기본값
    
    def _analyze_text_quality(self, text: str) -> float:
        """텍스트 품질 분석"""
        try:
            if not text:
                return 0.0
            
            score = 0.0
            total_factors = 0
            
            # 1. 길이 점수 (적절한 길이)
            length_score = min(100, len(text) / 10)  # 1000자 = 100점
            score += length_score
            total_factors += 1
            
            # 2. 문장 구조 점수
            sentences = text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / len(sentences) if sentences else 0
            if 5 <= avg_sentence_length <= 25:
                structure_score = 100
            else:
                structure_score = max(0, 100 - abs(avg_sentence_length - 15) * 2)
            score += structure_score
            total_factors += 1
            
            # 3. 특수문자/숫자 비율 점수
            special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
            special_ratio = special_chars / len(text) if text else 0
            if 0.05 <= special_ratio <= 0.15:
                special_score = 100
            else:
                special_score = max(0, 100 - abs(special_ratio - 0.1) * 1000)
            score += special_score
            total_factors += 1
            
            return round(score / total_factors, 2)
            
        except Exception as e:
            logger.error(f"텍스트 품질 분석 실패: {e}")
            return 70.0
    
    async def _stage2_gpt_analysis(self, 
                                  resume_text: str, 
                                  cover_letter_text: str,
                                  stage1_results: Dict[str, Any]) -> Dict[str, Any]:
        """2단계: GPT-4o 기반 종합 평가"""
        try:
            if not self.openai_service:
                logger.warning("OpenAI 서비스 없음, 1단계 결과만 반환")
                return {"error": "OpenAI 서비스 사용 불가"}
            
            # GPT-4o 분석 프롬프트 구성
            analysis_prompt = self._build_gpt_analysis_prompt(
                resume_text, cover_letter_text, stage1_results
            )
            
            # GPT-4o로 분석 실행
            gpt_response = await self.openai_service.generate_detailed_analysis_with_gpt4o(
                analysis_prompt, "resume"
            )
            
            # 응답 파싱 및 구조화
            structured_analysis = self._parse_gpt_analysis_response(gpt_response)
            
            return structured_analysis
            
        except Exception as e:
            logger.error(f"❌ 2단계 GPT 분석 실패: {e}")
            return {"error": str(e)}
    
    def _build_gpt_analysis_prompt(self, 
                                  resume_text: str, 
                                  cover_letter_text: str,
                                  stage1_results: Dict[str, Any]) -> str:
        """GPT 분석용 프롬프트 구성"""
        
        # 1단계 결과 요약
        stage1_summary = f"""
1단계 기계적 분석 결과:
- 직무 적합성: {stage1_results.get('job_fit_score', 'N/A')}점
- 문법 점수: {stage1_results.get('grammar_score', 'N/A')}점
- 텍스트 품질: {stage1_results.get('text_quality_score', 'N/A')}점
- 주요 스킬: {', '.join([f'{k}({v}점)' for k, v in stage1_results.get('skill_scores', {}).items() if v > 50])}
"""
        
        prompt = f"""
당신은 15년 경력의 HR 전문가입니다. 다음 이력서와 자기소개서를 상세히 분석하여 평가해주세요.

[분석할 문서]
이력서: {resume_text[:2000]}{'...' if len(resume_text) > 2000 else ''}
자기소개서: {cover_letter_text[:1000]}{'...' if len(cover_letter_text) > 1000 else ''}

{stage1_summary}

[분석 항목 및 평가 기준]
1. 직무 적합성 (0-100점): 지원 직무와의 연관성 및 적합성
2. 핵심 기술 역량 (0-100점): 기술 스킬의 구체성과 수준
3. 경력 및 성과 (0-100점): 경력 사항의 구체성과 성과
4. 문제 해결 능력 (0-100점): 문제 해결 경험과 접근 방식
5. 협업/커뮤니케이션 (0-100점): 팀워크와 소통 능력
6. 성장 가능성 (0-100점): 학습 의지와 발전 가능성
7. 표현력/문법 (0-100점): 문서 작성 능력과 문법

[응답 형식]
반드시 다음 JSON 형식으로만 응답하세요:
{{
    "직무_적합성": 85,
    "핵심_기술_역량": 90,
    "경력_및_성과": 70,
    "문제_해결_능력": 80,
    "협업": 75,
    "성장_가능성": 85,
    "표현력": 90,
    "종합_평가": "전반적으로 우수한 지원자이나, 경력 성과의 구체화가 필요합니다."
}}
"""
        return prompt
    
    def _parse_gpt_analysis_response(self, gpt_response: Any) -> Dict[str, Any]:
        """GPT 응답 파싱 및 구조화"""
        try:
            if hasattr(gpt_response, 'analysis_result'):
                analysis_text = gpt_response.analysis_result
            elif isinstance(gpt_response, str):
                analysis_text = gpt_response
            else:
                analysis_text = str(gpt_response)
            
            # JSON 추출 시도
            try:
                # JSON 부분 찾기
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = analysis_text[start_idx:end_idx]
                    parsed = json.loads(json_str)
                    
                    # 점수 정규화 (0-100 범위)
                    normalized_scores = {}
                    for key, value in parsed.items():
                        if key != "종합_평가" and isinstance(value, (int, float)):
                            normalized_scores[key] = min(100, max(0, int(value)))
                        elif key == "종합_평가":
                            normalized_scores[key] = value
                    
                    return normalized_scores
                else:
                    raise ValueError("JSON 형식을 찾을 수 없음")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON 파싱 실패, 기본값 사용: {e}")
                # 기본 점수 반환
                return {
                    "직무_적합성": 70,
                    "핵심_기술_역량": 70,
                    "경력_및_성과": 70,
                    "문제_해결_능력": 70,
                    "협업": 70,
                    "성장_가능성": 70,
                    "표현력": 70,
                    "종합_평가": "GPT 분석 실패로 기본 점수 적용"
                }
                
        except Exception as e:
            logger.error(f"GPT 응답 파싱 실패: {e}")
            return {"error": str(e)}
    
    def _calculate_final_score(self, 
                              stage1_results: Dict[str, Any], 
                              stage2_results: Dict[str, Any],
                              job_position: str) -> float:
        """최종 점수 계산 (가중치 적용)"""
        try:
            # 직무별 가중치 선택
            weights = self.job_weights.get(job_position, self.default_weights)
            
            # 1단계 점수들
            stage1_scores = {
                "직무_적합성": stage1_results.get("job_fit_score", 50),
                "기술_역량": np.mean(list(stage1_results.get("skill_scores", {}).values())) if stage1_results.get("skill_scores") else 50,
                "표현력": stage1_results.get("grammar_score", 75),
                "텍스트_품질": stage1_results.get("text_quality_score", 70)
            }
            
            # 2단계 점수들
            stage2_scores = {
                "직무_적합성": stage2_results.get("직무_적합성", 70),
                "기술_역량": stage2_results.get("핵심_기술_역량", 70),
                "경력_성과": stage2_results.get("경력_및_성과", 70),
                "문제_해결": stage2_results.get("문제_해결_능력", 70),
                "협업": stage2_results.get("협업", 70),
                "성장성": stage2_results.get("성장_가능성", 70),
                "표현력": stage2_results.get("표현력", 70)
            }
            
            # 가중 평균 계산
            final_score = 0.0
            total_weight = 0.0
            
            for category, weight in weights.items():
                if category in stage1_scores:
                    final_score += stage1_scores[category] * weight
                    total_weight += weight
                elif category in stage2_scores:
                    final_score += stage2_scores[category] * weight
                    total_weight += weight
            
            if total_weight > 0:
                final_score = final_score / total_weight
            
            return round(final_score, 2)
            
        except Exception as e:
            logger.error(f"최종 점수 계산 실패: {e}")
            return 70.0  # 기본값
    
    def _split_text_to_chunks(self, text: str, max_length: int = 512) -> List[str]:
        """텍스트를 청크로 분할"""
        try:
            words = text.split()
            chunks = []
            current_chunk = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= max_length:
                    current_chunk.append(word)
                    current_length += len(word) + 1
                else:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
            
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            return chunks if chunks else [text[:max_length]]
            
        except Exception as e:
            logger.error(f"텍스트 청킹 실패: {e}")
            return [text[:max_length]]
    
    async def get_ranking_data(self, applicants_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """지원자 랭킹 데이터 생성"""
        try:
            ranked_applicants = []
            
            for applicant in applicants_data:
                # 최종 점수 추출
                final_score = applicant.get("final_score", 0)
                
                # 랭킹 정보 추가
                ranked_applicant = applicant.copy()
                ranked_applicant["ranking_score"] = final_score
                ranked_applicants.append(ranked_applicant)
            
            # 점수 기준 내림차순 정렬
            ranked_applicants.sort(key=lambda x: x.get("ranking_score", 0), reverse=True)
            
            # 랭킹 순위 추가
            for i, applicant in enumerate(ranked_applicants):
                applicant["rank"] = i + 1
                applicant["rank_percentage"] = round((i + 1) / len(ranked_applicants) * 100, 1)
            
            return ranked_applicants
            
        except Exception as e:
            logger.error(f"랭킹 데이터 생성 실패: {e}")
            return applicants_data
