import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class CoverLetterAnalysisService:
    """자소서 분석 서비스 - 9개 평가 항목"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        
        # 9개 평가 항목 정의
        self.evaluation_items = [
            "직무 적합성 (Job Fit)",
            "기술 스택 일치 여부", 
            "경험한 프로젝트 관련성",
            "핵심 기술 역량 (Tech Competency)",
            "경력 및 성과 (Experience & Impact)",
            "문제 해결 능력 (Problem-Solving)",
            "커뮤니케이션/협업 (Collaboration)",
            "성장 가능성/학습 능력 (Growth Potential)",
            "자소서 표현력/논리성 (Clarity & Grammar)"
        ]
    
    async def analyze_cover_letter(self, cover_letter_text: str, job_description: str = "") -> Dict[str, Any]:
        """자소서 분석 실행"""
        try:
            logger.info("🔍 자소서 분석 시작...")
            
            # GPT-4o로 분석 실행
            analysis_result = await self._analyze_with_gpt4o(cover_letter_text, job_description)
            
            # 결과 구조화
            structured_result = {
                "analysis_timestamp": datetime.now().isoformat(),
                "cover_letter_analysis": analysis_result,
                "overall_score": self._calculate_overall_score(analysis_result)
            }
            
            logger.info(f"✅ 자소서 분석 완료! 종합 점수: {structured_result['overall_score']:.1f}/10점")
            return structured_result
            
        except Exception as e:
            logger.error(f"❌ 자소서 분석 실패: {e}")
            return {"error": str(e)}
    
    async def _analyze_with_gpt4o(self, cover_letter_text: str, job_description: str) -> Dict[str, Any]:
        """GPT-4o를 사용한 자소서 분석"""
        try:
            # 분석 프롬프트 구성
            prompt = self._build_analysis_prompt(cover_letter_text, job_description)
            
            # GPT-4o API 호출
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 15년 경력의 HR 전문가입니다. 자소서를 9개 항목으로 분석하여 각 항목별로 0-10점을 매기고 피드백을 제공해주세요."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 응답 파싱
            analysis_text = response.choices[0].message.content
            return self._parse_analysis_response(analysis_text)
            
        except Exception as e:
            logger.error(f"GPT-4o 분석 실패: {e}")
            return self._get_default_analysis()
    
    def _build_analysis_prompt(self, cover_letter_text: str, job_description: str) -> str:
        """분석용 프롬프트 구성"""
        prompt = f"""
다음 자소서를 9개 평가 항목으로 분석해주세요.

[자소서 내용]
{cover_letter_text[:3000]}{'...' if len(cover_letter_text) > 3000 else ''}

{f'[채용 공고 내용]\n{job_description[:1000]}{"..." if len(job_description) > 1000 else ""}' if job_description else ''}

[평가 항목 및 기준]
1. 직무 적합성 (Job Fit): 지원 직무와의 연관성 및 적합성
2. 기술 스택 일치 여부: JD 기술과 자소서 기술 스택 비교
3. 경험한 프로젝트 관련성: 직무와의 연관성
4. 핵심 기술 역량 (Tech Competency): 기술 스택의 깊이와 넓이
5. 경력 및 성과 (Experience & Impact): 주도적 역할과 수치화된 성과
6. 문제 해결 능력 (Problem-Solving): 구체적 사례와 구조화
7. 커뮤니케이션/협업 (Collaboration): 팀워크와 협업 도구 경험
8. 성장 가능성/학습 능력 (Growth Potential): 새로운 기술 학습과 적응력
9. 자소서 표현력/논리성 (Clarity & Grammar): 글의 품질과 문법

[응답 형식]
반드시 다음 JSON 형식으로만 응답하세요:
{{
    "motivation_relevance": {{
        "score": 8,
        "feedback": "지원 동기가 명확하고 구체적으로 표현되었습니다."
    }},
    "problem_solving_STAR": {{
        "score": 7,
        "feedback": "STAR 기법을 활용한 문제 해결 사례가 잘 정리되어 있습니다."
    }},
    "quantitative_impact": {{
        "score": 6,
        "feedback": "일부 정량적 성과가 제시되었으나 더 구체적인 수치가 필요합니다."
    }},
    "job_understanding": {{
        "score": 9,
        "feedback": "지원 직무에 대한 깊은 이해와 관련 경험이 잘 드러납니다."
    }},
    "unique_experience": {{
        "score": 8,
        "feedback": "다른 지원자와 차별화되는 독특한 경험이 잘 표현되었습니다."
    }},
    "logical_flow": {{
        "score": 7,
        "feedback": "전체적인 논리적 흐름이 자연스럽게 연결되어 있습니다."
    }},
    "keyword_diversity": {{
        "score": 6,
        "feedback": "관련 키워드가 적절히 사용되었으나 더 다양한 표현이 가능합니다."
    }},
    "sentence_readability": {{
        "score": 8,
        "feedback": "문장이 명확하고 읽기 쉽게 구성되어 있습니다."
    }},
    "typos_and_errors": {{
        "score": 9,
        "feedback": "오탈자나 문법 오류가 거의 발견되지 않았습니다."
    }}
}}

각 항목은 0-10점으로 평가하고, 구체적이고 도움이 되는 피드백을 제공해주세요.
"""
        return prompt
    
    def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """GPT 응답 파싱 및 구조화"""
        try:
            # JSON 부분 찾기
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = analysis_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # 점수 정규화 (0-10 범위)
                normalized_scores = {}
                for key, value in parsed.items():
                    if isinstance(value, dict) and 'score' in value:
                        score = value['score']
                        if isinstance(score, (int, float)):
                            normalized_scores[key] = {
                                'score': min(10, max(0, int(score))),
                                'feedback': value.get('feedback', '피드백이 없습니다.')
                            }
                        else:
                            normalized_scores[key] = {
                                'score': 5,
                                'feedback': '점수 파싱 오류'
                            }
                    else:
                        normalized_scores[key] = {
                            'score': 5,
                            'feedback': '기본 피드백'
                        }
                
                return normalized_scores
            else:
                raise ValueError("JSON 형식을 찾을 수 없음")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"JSON 파싱 실패, 기본값 사용: {e}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """기본 분석 결과 반환"""
        return {
            "motivation_relevance": {"score": 7, "feedback": "지원 동기에 대한 기본적인 분석 결과입니다."},
            "problem_solving_STAR": {"score": 7, "feedback": "STAR 기법 활용에 대한 기본 분석 결과입니다."},
            "quantitative_impact": {"score": 7, "feedback": "정량적 성과 제시에 대한 기본 분석 결과입니다."},
            "job_understanding": {"score": 7, "feedback": "직무 이해도에 대한 기본 분석 결과입니다."},
            "unique_experience": {"score": 7, "feedback": "차별화 경험에 대한 기본 분석 결과입니다."},
            "logical_flow": {"score": 7, "feedback": "논리적 흐름에 대한 기본 분석 결과입니다."},
            "keyword_diversity": {"score": 7, "feedback": "키워드 다양성에 대한 기본 분석 결과입니다."},
            "sentence_readability": {"score": 7, "feedback": "문장 가독성에 대한 기본 분석 결과입니다."},
            "typos_and_errors": {"score": 7, "feedback": "오탈자 검토에 대한 기본 분석 결과입니다."}
        }
    
    def _calculate_overall_score(self, analysis_result: Dict[str, Any]) -> float:
        """종합 점수 계산"""
        try:
            scores = []
            for key, value in analysis_result.items():
                if isinstance(value, dict) and 'score' in value:
                    scores.append(value['score'])
            
            if scores:
                return round(sum(scores) / len(scores), 1)
            else:
                return 7.0
                
        except Exception as e:
            logger.error(f"종합 점수 계산 실패: {e}")
            return 7.0
    
    def get_evaluation_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """평가 결과 요약"""
        try:
            summary = {
                "overall_score": self._calculate_overall_score(analysis_result),
                "top_strengths": [],
                "improvement_areas": [],
                "score_distribution": {
                    "excellent": 0,  # 8-10점
                    "good": 0,       # 5-7점
                    "needs_improvement": 0  # 0-4점
                }
            }
            
            for key, value in analysis_result.items():
                if isinstance(value, dict) and 'score' in value:
                    score = value['score']
                    
                    # 점수 분포 계산
                    if score >= 8:
                        summary["score_distribution"]["excellent"] += 1
                        summary["top_strengths"].append({
                            "item": key,
                            "score": score,
                            "feedback": value.get('feedback', '')
                        })
                    elif score >= 5:
                        summary["score_distribution"]["good"] += 1
                    else:
                        summary["score_distribution"]["needs_improvement"] += 1
                        summary["improvement_areas"].append({
                            "item": key,
                            "score": score,
                            "feedback": value.get('feedback', '')
                        })
            
            # 상위 강점과 개선 영역 정렬
            summary["top_strengths"].sort(key=lambda x: x["score"], reverse=True)
            summary["improvement_areas"].sort(key=lambda x: x["score"])
            
            return summary
            
        except Exception as e:
            logger.error(f"평가 요약 생성 실패: {e}")
            return {"overall_score": 7.0, "error": str(e)}


