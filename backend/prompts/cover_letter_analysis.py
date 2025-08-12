"""
자소서 분석을 위한 RAG 프롬프트 및 데이터 구조
"""

# 자소서 분석 프롬프트
COVER_LETTER_ANALYSIS_PROMPT = """
당신은 채용 전문가입니다. 지원자의 자기소개서를 분석하여 다음과 같은 항목들을 평가해주세요.

## 분석 대상
지원 직무: {position}
회사/부서: {department}
지원자 자기소개서 내용: {content}

## 참고 자료 (RAG)
{rag_context}

## 평가 기준
각 항목을 1-10점으로 평가하고, 구체적인 피드백을 제공해주세요.

### 1. 동기 및 열정 (Motivation & Passion)
- 지원 동기가 명확한가?
- 회사/직무에 대한 이해도는 높은가?
- 진정성 있는 열정이 드러나는가?

### 2. 문제해결 능력 (Problem Solving)
- 구체적인 문제 상황과 해결 과정이 제시되었는가?
- STAR 방법론이 잘 적용되었는가?
- 결과와 영향이 명확한가?

### 3. 팀워크 및 협업 (Teamwork & Collaboration)
- 팀 프로젝트 경험이 구체적으로 서술되었는가?
- 갈등 해결 능력이 드러나는가?
- 협업을 통한 성과가 명확한가?

### 4. 기술적 역량 (Technical Skills)
- 직무 관련 기술/도구 사용 경험이 구체적인가?
- 학습 능력과 적응력이 드러나는가?
- 프로젝트에서의 기술적 기여도는 높은가?

### 5. 성장 잠재력 (Growth Potential)
- 지속적인 학습 의지가 드러나는가?
- 도전적 과제에 대한 태도는 적극적인가?
- 미래 비전과 계획이 구체적인가?

## 출력 형식
다음 JSON 형식으로 응답해주세요:

```json
{{
  "analysis": {{
    "motivation_score": 점수,
    "motivation_feedback": "구체적인 피드백",
    "problem_solving_score": 점수,
    "problem_solving_feedback": "구체적인 피드백",
    "teamwork_score": 점수,
    "teamwork_feedback": "구체적인 피드백",
    "technical_score": 점수,
    "technical_feedback": "구체적인 피드백",
    "growth_score": 점수,
    "growth_feedback": "구체적인 피드백"
  }},
  "overall_score": "전체 평균 점수",
  "strengths": ["강점 1", "강점 2", "강점 3"],
  "weaknesses": ["개선점 1", "개선점 2", "개선점 3"],
  "recommendations": ["구체적인 개선 제안 1", "구체적인 개선 제안 2"],
  "rag_evidence": [
    {{
      "section": "참고한 RAG 섹션",
      "relevance": "해당 섹션과의 연관성",
      "impact": "분석에 미친 영향"
    }}
  ]
}}
```

## 주의사항
1. 점수는 1-10점 사이의 정수로 평가
2. 피드백은 구체적이고 실행 가능한 내용으로 작성
3. RAG 참고 자료를 적극 활용하여 근거 있는 평가 제공
4. 한국어로 응답
"""

# 자소서 타입별 세부 분석 프롬프트
COVER_LETTER_DETAILED_PROMPT = """
당신은 {position} 직무에 특화된 채용 전문가입니다.
지원자의 자기소개서를 {department} 부서의 채용 기준에 맞춰 심층 분석해주세요.

## 분석 대상
{content}

## 직무별 핵심 평가 요소
{position_specific_criteria}

## 부서별 문화적 적합성
{department_culture_fit}

## 참고 자료 (RAG)
{rag_context}

## 심층 분석 요청사항
1. 직무 적합성 (40%): 기술적 역량과 경험의 적합도
2. 문화적 적합성 (30%): 회사 가치관과의 일치도
3. 성장 잠재력 (20%): 미래 발전 가능성
4. 의사소통 능력 (10%): 글쓰기와 표현력

## 출력 형식
```json
{{
  "detailed_analysis": {{
    "job_fit": {{
      "score": 점수,
      "strengths": ["강점들"],
      "weaknesses": ["약점들"],
      "suggestions": ["개선 제안"]
    }},
    "culture_fit": {{
      "score": 점수,
      "alignment": "회사 가치와의 일치도",
      "concerns": "우려사항",
      "recommendations": ["문화적 적합성 향상 방안"]
    }},
    "growth_potential": {{
      "score": 점수,
      "learning_ability": "학습 능력 평가",
      "adaptability": "적응력 평가",
      "career_vision": "경력 비전 평가"
    }},
    "communication": {{
      "score": 점수,
      "clarity": "명확성",
      "structure": "구조화",
      "impact": "임팩트"
    }}
  }},
  "overall_assessment": "전체 종합 평가",
  "hiring_recommendation": "채용 추천도 (매우 추천/추천/보통/비추천)",
  "interview_focus": ["면접 시 중점 확인 사항들"],
  "onboarding_suggestions": ["입사 후 적응 지원 방안"]
}}
```
"""

# RAG 검색을 위한 프롬프트
RAG_SEARCH_PROMPT = """
다음 지원자의 자기소개서 내용과 가장 관련성이 높은 참고 자료를 찾아주세요.

## 지원 정보
- 직무: {position}
- 부서: {department}
- 자기소개서 내용: {content}

## 검색 요청사항
1. 직무 관련 기술/역량 참고 자료
2. 회사/부서 문화 및 가치관 참고 자료
3. 유사한 성공 사례 참고 자료
4. 평가 기준 및 루브릭 참고 자료

## 출력 형식
```json
{{
  "relevant_sections": [
    {{
      "section_id": "섹션 ID",
      "title": "섹션 제목",
      "content": "관련 내용",
      "relevance_score": "관련성 점수 (1-10)",
      "relevance_reason": "관련성 이유"
    }}
  ],
  "search_summary": "검색 결과 요약",
  "missing_context": "추가로 필요한 참고 자료"
}}
```
"""

# 자소서 개선 제안 프롬프트
IMPROVEMENT_SUGGESTION_PROMPT = """
지원자의 자기소개서를 분석한 결과를 바탕으로 구체적인 개선 제안을 제공해주세요.

## 현재 자기소개서 분석 결과
{analysis_result}

## 개선 제안 요청사항
1. 각 평가 항목별 구체적인 개선 방안
2. STAR 방법론 적용 예시
3. 더 설득력 있는 표현 방법
4. 직무 관련성 강화 방안

## 출력 형식
```json
{{
  "improvement_suggestions": {{
    "motivation": {{
      "current_issues": ["현재 문제점들"],
      "improvements": ["개선 방안들"],
      "examples": ["구체적 예시들"]
    }},
    "problem_solving": {{
      "current_issues": ["현재 문제점들"],
      "improvements": ["개선 방안들"],
      "star_examples": ["STAR 방법론 적용 예시"]
    }},
    "teamwork": {{
      "current_issues": ["현재 문제점들"],
      "improvements": ["개선 방안들"],
      "collaboration_examples": ["협업 경험 강화 예시"]
    }},
    "technical": {{
      "current_issues": ["현재 문제점들"],
      "improvements": ["개선 방안들"],
      "skill_demonstration": ["기술 역량 어필 방법"]
    }}
  }},
  "rewrite_suggestions": [
    "문장별 개선 제안 1",
    "문장별 개선 제안 2"
  ],
  "overall_improvement_plan": "전체적인 개선 계획"
}}
```
"""

# RAG 데이터 구조
RAG_DATA_STRUCTURE = {
    "job_descriptions": {
        "backend_developer": {
            "required_skills": ["Python", "FastAPI", "MongoDB", "Docker"],
            "preferred_skills": ["AWS", "Kubernetes", "Microservices"],
            "responsibilities": ["백엔드 API 개발", "데이터베이스 설계", "성능 최적화"],
            "evaluation_criteria": ["코딩 품질", "아키텍처 설계 능력", "문제 해결 능력"]
        },
        "frontend_developer": {
            "required_skills": ["React", "JavaScript", "HTML/CSS", "TypeScript"],
            "preferred_skills": ["Next.js", "Redux", "Tailwind CSS"],
            "responsibilities": ["사용자 인터페이스 개발", "반응형 웹 구현", "사용자 경험 최적화"],
            "evaluation_criteria": ["UI/UX 감각", "코드 품질", "사용자 중심 사고"]
        }
    },
    "company_values": {
        "innovation": "혁신적인 솔루션 개발",
        "collaboration": "팀워크와 협업 중시",
        "quality": "높은 품질의 결과물 추구",
        "growth": "지속적인 학습과 성장"
    },
    "evaluation_rubrics": {
        "motivation": {
            "excellent": "명확한 동기와 진정성 있는 열정",
            "good": "적절한 동기와 관심",
            "fair": "일반적인 동기",
            "poor": "모호하거나 부족한 동기"
        },
        "problem_solving": {
            "excellent": "구체적이고 체계적인 문제 해결 과정",
            "good": "적절한 문제 해결 방법",
            "fair": "기본적인 문제 해결",
            "poor": "문제 해결 과정 부족"
        }
    }
}

if __name__ == "__main__":
    print("자소서 분석 RAG 프롬프트 및 데이터 구조가 생성되었습니다.")
