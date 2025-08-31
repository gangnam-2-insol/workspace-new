#!/usr/bin/env python3
"""
OpenAI 기반 이력서 분석기
"""

import json
import os
import time
from typing import Any, Dict

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from models.resume_analysis import ResumeAnalysisResult
from openai import OpenAI


class OpenAIResumeAnalyzer:
    """OpenAI 기반 이력서 분석기"""

    def __init__(self):
        """초기화"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=self.api_key
        )

        # 분석 프롬프트 템플릿
        self.analysis_prompt = ChatPromptTemplate.from_template("""
당신은 15년 경력의 시니어 HR 컨설턴트이자 이력서 분석 전문가입니다. 지원자의 이력서를 심층 분석하여 실무진이 바로 활용할 수 있는 구체적이고 실행 가능한 피드백을 제공해야 합니다.

**지원자 정보:**
- 이름: {name}
- 지원 직무: {position}
- 회사/부서: {department}

**이력서 내용:**
{resume_content}

**🎯 핵심 분석 원칙:**

1. **조건부 가중치 평가**: 지원 직무와 경력 수준에 따라 각 항목의 중요도를 다르게 적용
   - 개발직: 기술스택(40%) + 프로젝트경험(30%) + 경력(20%) + 학력(10%)
   - 신입: 학력(30%) + 성장가능성(30%) + 기술스택(25%) + 프로젝트(15%)
   - 경력직: 경력(40%) + 기술스택(30%) + 프로젝트(20%) + 학력(10%)
   - 가중치 적용 이유를 명시적으로 설명

2. **상황 대응형 분석**: 정형화된 문구 대신 지원자의 구체적 정보를 활용한 맞춤형 분석
   - 이력서에 명시된 기술명, 프로젝트명, 성과 수치를 직접 인용
   - 지원 직무 요구사항과의 구체적 매칭도 분석
   - 패턴 문구 금지: "잘하고 있습니다", "부족합니다" 등 일반적 표현

3. **실행 계획형 개선안**: 추상적 조언 대신 구체적 실행 방안과 기대 효과 제시
   - 구체적 기간, 방법, 예상 결과 포함
   - 지원 직무와의 연관성 명시
   - 우선순위와 단계별 접근법 제시

4. **동적 강점/개선점 비율**: 지원자 역량 수준에 따른 유연한 구성
   - 우수 지원자: 강점 70%, 개선점 30%
   - 보통 지원자: 강점 50%, 개선점 50%
   - 부족 지원자: 강점 30%, 개선점 70%

**📊 평가 기준 (가중치 적용):**
- **학력 및 전공**: 전공-직무 연관성, 학업 성취도, 추가 자격증
- **경력 및 직무 경험**: 경력 깊이, 성과의 구체성, 직무 관련성
- **보유 기술 및 역량**: 기술 스택 완성도, 최신성, 실무 적용 가능성
- **프로젝트 및 성과**: 프로젝트 규모, 개인 기여도, 측정 가능한 성과
- **자기계발 및 성장**: 학습 의지, 기술 트렌드 파악, 커리어 비전

**⚠️ 중요: 점수 산정 시 매우 엄격한 기준 적용**
- 75점 이상: 해당 분야에서 탁월한 수준 (상위 1% - 매우 드물게)
- 68-74점: 우수한 수준 (상위 10%)
- 62-67점: 양호한 수준 (상위 30%)
- 58-61점: 보통 수준 (상위 50%)
- 52-57점: 개선 필요 (하위 50%)
- 48-51점: 부족한 수준 (하위 30%)
- 48점 미만: 매우 부족한 수준 (하위 20%)
- 전체 점수는 가중치를 적용한 평균으로 계산

**📋 출력 형식:**
JSON 형태로 다음 구조를 따라주세요:
{{
  "evaluation_weights": {{
    "education_weight": 0.1,
    "experience_weight": 0.4,
    "skills_weight": 0.3,
    "projects_weight": 0.2,
    "growth_weight": 0.0,
    "weight_reasoning": "경력직 개발자로 경력과 기술스택을 중점 평가"
  }},
  "overall_score": 58,
  "education_score": 62,
  "experience_score": 68,
  "skills_score": 58,
  "projects_score": 62,
  "growth_score": 52,
  "education_analysis": "컴퓨터공학 전공으로 기본기가 탄탄하며, AWS 자격증 보유로 클라우드 역량이 검증됨",
  "experience_analysis": "3년간 React 기반 프론트엔드 개발 경험으로 지원 직무와 정확히 일치하며, 사용자 경험 개선 프로젝트에서 30% 성능 향상 달성",
  "skills_analysis": "React, TypeScript, Node.js 실무 경험 보유. 특히 TypeScript 활용도가 높아 대규모 프로젝트 안정성 확보에 유리",
  "projects_analysis": "전자상거래 플랫폼 구축 프로젝트에서 결제 모듈 개발 담당, 월 거래액 50% 증가에 기여",
  "growth_analysis": "최근 Next.js, GraphQL 학습 이력으로 최신 기술 트렌드에 대한 적극적 학습 의지 확인",
  "analysis_notes": {{
    "key_technologies": ["React", "TypeScript", "Node.js", "AWS"],
    "project_highlights": ["전자상거래 플랫폼", "결제 모듈 개발"],
    "performance_metrics": ["30% 성능 향상", "월 거래액 50% 증가"]
  }},
  "strengths": [
    "React/TypeScript 실무 경험으로 대규모 프로젝트 안정성 확보 가능",
    "AWS 클라우드 인프라 경험으로 DevOps 역량 보유",
    "사용자 경험 개선 프로젝트 성과로 비즈니스 임팩트 창출 경험"
  ],
  "improvements": [
    "백엔드 API 설계 경험 부족으로 풀스택 역량 강화 필요"
  ],
  "overall_feedback": "프론트엔드 개발자로서 기본적인 실무 경험은 있으나, 기술적 깊이와 성과 측정 지표가 부족한 지원자. 더 구체적인 성과와 전문성을 보여줄 필요가 있음",
  "recommendations": [
    {{
      "priority": "high",
      "action": "백엔드 API 설계 및 데이터베이스 최적화 경험",
      "timeline": "6개월 내",
      "method": "Node.js Express 프레임워크를 활용한 RESTful API 개발 프로젝트 참여",
      "expected_impact": "풀스택 개발자로 성장하여 더 큰 규모의 프로젝트 담당 가능"
    }},
    {{
      "priority": "medium",
      "action": "마이크로서비스 아키텍처 이해도 향상",
      "timeline": "3개월 내",
      "method": "Docker, Kubernetes 기반 컨테이너 오케스트레이션 학습",
      "expected_impact": "현대적 개발 환경에서의 협업 효율성 증대"
    }}
  ]
}}
""")

        # Pydantic 출력 파서
        self.output_parser = PydanticOutputParser(pydantic_object=ResumeAnalysisResult)

    async def analyze_resume(self, applicant_data: Dict[str, Any]) -> ResumeAnalysisResult:
        """이력서 분석 실행"""
        try:
            start_time = time.time()

            # 지원자 정보 추출
            name = applicant_data.get("name", "알 수 없음")
            position = applicant_data.get("position", "알 수 없음")
            department = applicant_data.get("department", "알 수 없음")

            # 이력서 내용 구성
            resume_content = self._extract_resume_content(applicant_data)

            # 프롬프트에 변수 삽입
            prompt = self.analysis_prompt.format(
                name=name,
                position=position,
                department=department,
                resume_content=resume_content
            )

            # OpenAI API 호출
            response = await self.model.ainvoke(prompt)

            # 응답 파싱
            analysis_result = self._parse_response(response.content)

            # 가중치를 적용한 실제 점수 재계산
            analysis_result = self._apply_weighted_scoring(analysis_result, position)

            # 처리 시간 계산
            processing_time = time.time() - start_time

            print(f"✅ 이력서 분석 완료: {name} (처리시간: {processing_time:.2f}초)")

            return analysis_result

        except Exception as e:
            print(f"❌ 이력서 분석 실패: {str(e)}")
            raise

    def _apply_weighted_scoring(self, analysis_result: ResumeAnalysisResult, position: str) -> ResumeAnalysisResult:
        """가중치를 적용한 점수 재계산"""
        try:
            # 직무별 가중치 정의
            weights = self._get_position_weights(position)

            # 개별 점수에 엄격한 기준 적용 (점수 조정)
            adjusted_scores = {
                'education': self._adjust_score_strict(analysis_result.education_score),
                'experience': self._adjust_score_strict(analysis_result.experience_score),
                'skills': self._adjust_score_strict(analysis_result.skills_score),
                'projects': self._adjust_score_strict(analysis_result.projects_score),
                'growth': self._adjust_score_strict(analysis_result.growth_score)
            }

            # 가중치 적용한 종합 점수 계산
            weighted_score = (
                adjusted_scores['education'] * weights['education'] +
                adjusted_scores['experience'] * weights['experience'] +
                adjusted_scores['skills'] * weights['skills'] +
                adjusted_scores['projects'] * weights['projects'] +
                adjusted_scores['growth'] * weights['growth']
            )

            # 결과 업데이트
            analysis_result.education_score = adjusted_scores['education']
            analysis_result.experience_score = adjusted_scores['experience']
            analysis_result.skills_score = adjusted_scores['skills']
            analysis_result.projects_score = adjusted_scores['projects']
            analysis_result.growth_score = adjusted_scores['growth']
            analysis_result.overall_score = round(weighted_score)

            # 가중치 정보 업데이트
            if analysis_result.evaluation_weights:
                analysis_result.evaluation_weights.education_weight = weights['education']
                analysis_result.evaluation_weights.experience_weight = weights['experience']
                analysis_result.evaluation_weights.skills_weight = weights['skills']
                analysis_result.evaluation_weights.projects_weight = weights['projects']
                analysis_result.evaluation_weights.growth_weight = weights['growth']
                analysis_result.evaluation_weights.weight_reasoning = f"{position} 직무에 맞는 가중치 적용"

            print(f"📊 가중치 적용 완료: 종합점수 {analysis_result.overall_score}점")

            return analysis_result

        except Exception as e:
            print(f"❌ 가중치 적용 실패: {str(e)}")
            return analysis_result

    def _get_position_weights(self, position: str) -> Dict[str, float]:
        """직무별 가중치 반환"""
        position_lower = position.lower()

        if any(keyword in position_lower for keyword in ['개발', 'developer', 'engineer', '프로그래머']):
            # 개발직
            return {
                'education': 0.1,
                'experience': 0.2,
                'skills': 0.4,
                'projects': 0.3,
                'growth': 0.0
            }
        elif any(keyword in position_lower for keyword in ['신입', 'junior', '인턴', '신규']):
            # 신입
            return {
                'education': 0.3,
                'experience': 0.1,
                'skills': 0.25,
                'projects': 0.15,
                'growth': 0.2
            }
        else:
            # 경력직 (기본)
            return {
                'education': 0.1,
                'experience': 0.4,
                'skills': 0.3,
                'projects': 0.2,
                'growth': 0.0
            }

    def _adjust_score_strict(self, score: int) -> int:
        """매우 엄격한 기준으로 점수 조정"""
        # 90점 이상은 극도로 엄격하게 적용 (상위 1% 수준)
        if score >= 95:
            return 75  # 탁월한 수준 (매우 드물게)
        elif score >= 90:
            return 68  # 우수한 수준 (상위 10%)
        elif score >= 85:
            return 62  # 양호한 수준 (상위 30%)
        elif score >= 80:
            return 58  # 보통 수준 (상위 50%)
        elif score >= 75:
            return 52  # 개선 필요 (하위 50%)
        elif score >= 70:
            return 48  # 부족한 수준 (하위 30%)
        elif score >= 65:
            return 42  # 매우 부족한 수준 (하위 20%)
        else:
            return max(35, score - 15)  # 극도로 부족한 수준

    def _extract_resume_content(self, applicant_data: Dict[str, Any]) -> str:
        """이력서 내용 추출 및 구성"""
        content_parts = []

        # 기본 정보
        if applicant_data.get("name"):
            content_parts.append(f"이름: {applicant_data['name']}")
        if applicant_data.get("position"):
            content_parts.append(f"지원 직무: {applicant_data['position']}")
        if applicant_data.get("department"):
            content_parts.append(f"부서: {applicant_data['department']}")
        if applicant_data.get("experience"):
            content_parts.append(f"경력: {applicant_data['experience']}")
        if applicant_data.get("skills"):
            content_parts.append(f"기술 스택: {applicant_data['skills']}")

        # 상세 정보
        if applicant_data.get("growthBackground"):
            content_parts.append(f"성장 배경: {applicant_data['growthBackground']}")
        if applicant_data.get("motivation"):
            content_parts.append(f"지원 동기: {applicant_data['motivation']}")
        if applicant_data.get("careerHistory"):
            content_parts.append(f"경력 사항: {applicant_data['careerHistory']}")

        # 추출된 텍스트
        if applicant_data.get("extracted_text"):
            content_parts.append(f"이력서 내용:\n{applicant_data['extracted_text']}")

        return "\n\n".join(content_parts) if content_parts else "이력서 내용이 없습니다."

    def _parse_response(self, response_content: str) -> ResumeAnalysisResult:
        """API 응답 파싱"""
        try:
            # JSON 추출 시도
            if "```json" in response_content:
                json_start = response_content.find("```json") + 7
                json_end = response_content.find("```", json_start)
                json_content = response_content[json_start:json_end].strip()
            elif "```" in response_content:
                json_start = response_content.find("```") + 3
                json_end = response_content.find("```", json_start)
                json_content = response_content[json_start:json_end].strip()
            else:
                json_content = response_content.strip()

            # JSON 파싱
            analysis_data = json.loads(json_content)

            # Pydantic 모델로 변환
            return ResumeAnalysisResult(**analysis_data)

        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 실패: {str(e)}")
            print(f"응답 내용: {response_content}")
            raise ValueError(f"분석 결과 파싱에 실패했습니다: {str(e)}")
        except Exception as e:
            print(f"❌ 응답 파싱 실패: {str(e)}")
            raise

    def get_analysis_summary(self, analysis_result: ResumeAnalysisResult) -> Dict[str, Any]:
        """분석 결과 요약"""
        return {
            "overall_score": analysis_result.overall_score,
            "score_breakdown": {
                "학력": analysis_result.education_score,
                "경력": analysis_result.experience_score,
                "기술": analysis_result.skills_score,
                "프로젝트": analysis_result.projects_score,
                "성장": analysis_result.growth_score
            },
            "grade": self._calculate_grade(analysis_result.overall_score),
            "strengths_count": len(analysis_result.strengths),
            "improvements_count": len(analysis_result.improvements),
            "recommendations_count": len(analysis_result.recommendations)
        }

    def _calculate_grade(self, score: int) -> str:
        """점수별 등급 계산"""
        if score >= 90:
            return "A+ (우수)"
        elif score >= 80:
            return "A (우수)"
        elif score >= 70:
            return "B+ (양호)"
        elif score >= 60:
            return "B (양호)"
        elif score >= 50:
            return "C+ (보통)"
        elif score >= 40:
            return "C (보통)"
        else:
            return "D (미흡)"

    async def batch_analyze(self, applicants_data: list) -> list:
        """일괄 분석"""
        results = []

        for i, applicant_data in enumerate(applicants_data):
            try:
                print(f"📊 일괄 분석 진행률: {i+1}/{len(applicants_data)}")
                result = await self.analyze_resume(applicant_data)
                results.append({
                    "applicant_id": applicant_data.get("_id"),
                    "name": applicant_data.get("name"),
                    "analysis_result": result,
                    "success": True
                })
            except Exception as e:
                print(f"❌ {applicant_data.get('name', '알 수 없음')} 분석 실패: {str(e)}")
                results.append({
                    "applicant_id": applicant_data.get("_id"),
                    "name": applicant_data.get("name"),
                    "error": str(e),
                    "success": False
                })

        return results

# 사용 예시
if __name__ == "__main__":
    import asyncio

    async def test_analyzer():
        analyzer = OpenAIResumeAnalyzer()

        # 테스트 데이터
        test_applicant = {
            "name": "홍길동",
            "position": "백엔드 개발자",
            "department": "개발팀",
            "experience": "3년",
            "skills": "Python, Django, PostgreSQL, Docker",
            "growthBackground": "컴퓨터공학 전공, 다양한 프로젝트 경험",
            "motivation": "기술적 성장과 팀 기여를 원함",
            "careerHistory": "웹 개발 2년, 모바일 앱 개발 1년",
            "extracted_text": "상세한 이력서 내용..."
        }

        try:
            result = await analyzer.analyze_resume(test_applicant)
            print("✅ 분석 완료!")
            print(f"종합 점수: {result.overall_score}/100")
            print(f"강점: {result.strengths}")
            print(f"개선점: {result.improvements}")

            summary = analyzer.get_analysis_summary(result)
            print(f"등급: {summary['grade']}")

        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")

    # 테스트 실행
    asyncio.run(test_analyzer())
