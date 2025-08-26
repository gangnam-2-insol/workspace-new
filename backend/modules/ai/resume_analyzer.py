#!/usr/bin/env python3
"""
OpenAI 기반 이력서 분석기
"""

import os
import json
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from models.resume_analysis import ResumeAnalysisResult

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
당신은 전문적인 이력서 분석가입니다. 지원자의 이력서를 분석하여 객관적이고 구체적인 피드백을 제공해야 합니다.

**지원자 정보:**
- 이름: {name}
- 지원 직무: {position}
- 회사/부서: {department}

**이력서 내용:**
{resume_content}

**분석 요구사항:**
1. 각 항목별로 0-100점 점수를 매기되, 객관적이고 공정하게 평가하세요
2. 각 항목에 대해 구체적이고 개인 맞춤형 분석을 제공하세요
3. 강점과 개선점을 명확하게 제시하세요
4. 구체적이고 실행 가능한 개선 권장사항을 제시하세요
5. 지원 직무와의 연관성을 고려하여 평가하세요

**평가 기준:**
- **학력 및 전공**: 최종 학력, 전공 분야, 학업 성취도, 직무 연관성
- **경력 및 직무 경험**: 경력 기간, 직무 내용, 성과, 지원 직무와의 연관성
- **보유 기술 및 역량**: 기술 스택, 숙련도, 직무 적합성, 최신 기술 반영도
- **프로젝트 및 성과**: 프로젝트 규모, 역할, 기여도, 구체적 성과
- **자기계발 및 성장**: 학습 의지, 새로운 기술 습득, 커리어 목표의 명확성

**출력 형식:**
JSON 형태로 다음 구조를 따라주세요:
{{
  "overall_score": 85,
  "education_score": 90,
  "experience_score": 88,
  "skills_score": 82,
  "projects_score": 87,
  "growth_score": 83,
  "education_analysis": "학력이 우수하고 전공이 직무와 잘 맞습니다...",
  "experience_analysis": "관련 경험이 풍부하고 구체적인 성과가 있습니다...",
  "skills_analysis": "필요한 기술 스택을 대부분 보유하고 있습니다...",
  "projects_analysis": "다양한 프로젝트 경험과 명확한 기여도가 있습니다...",
  "growth_analysis": "지속적인 학습 의지와 성장 가능성이 보입니다...",
  "strengths": ["강한 문제 해결 능력", "팀워크 능력이 뛰어남"],
  "improvements": ["최신 기술 스택 부족", "대규모 프로젝트 경험 부족"],
  "overall_feedback": "전반적으로 우수한 지원자입니다...",
  "recommendations": ["기술 스택을 더 다양화하세요", "프로젝트 경험을 강화하세요"]
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
            
            # 처리 시간 계산
            processing_time = time.time() - start_time
            
            print(f"✅ 이력서 분석 완료: {name} (처리시간: {processing_time:.2f}초)")
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ 이력서 분석 실패: {str(e)}")
            raise
    
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
