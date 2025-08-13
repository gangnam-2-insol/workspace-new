"""
자소서 자동 분석을 위한 프롬프트 템플릿
"""

# 1. 요약 & 핵심강점 추출 프롬프트
SUMMARY_AND_STRENGTHS_PROMPT = """
당신은 10년 경력의 시니어 채용담당자 역할을 한다. 
지원자가 제출한 자소서를 읽고, 3문장 내로 핵심 요약과 가장 강한 '핵심 강점' 3가지를 추출해줘.

핵심 강점은 구체적 근거(문장 위치/문장 일부)와 함께 표기해라.

자소서:
{cover_letter_text}

응답은 반드시 다음 JSON 형식으로만 출력하라:
{{
  "summary": "한 문장 요약...",
  "top_strengths": [
    {{"strength":"팀 리딩 경험", "evidence":"3번째 문단: '팀을 이끌며...'", "confidence": 0.92}},
    {{"strength":"문제 해결 능력", "evidence":"2번째 문단: '어려운 상황에서...'", "confidence": 0.88}},
    {{"strength":"성과 지향적 사고", "evidence":"4번째 문단: '결과적으로...'", "confidence": 0.85}}
  ]
}}
"""

# 2. STAR 추출 프롬프트
STAR_EXTRACTION_PROMPT = """
다음 텍스트에서 STAR(상황, 과제, 행동, 결과) 구조의 사례를 찾아 각각을 분리해서 반환하라. 
찾을 수 없으면 "not_found" 반환.

텍스트:
{cover_letter_text}

응답은 반드시 다음 JSON 배열 형식으로만 출력하라:
[
  {{"s":"상황 설명", "t":"과제/목표", "a":"구체적 행동", "r":"결과/성과", "evidence_sentence_indices":[2,3]}},
  {{"s":"다른 상황", "t":"다른 과제", "a":"다른 행동", "r":"다른 결과", "evidence_sentence_indices":[5,6]}}
]

STAR 구조가 명확하지 않으면 빈 배열 []을 반환하라.
"""

# 3. 직무 적합성 점수 + 키워드 매칭 프롬프트
JOB_SUITABILITY_PROMPT = """
채용공고(직무 설명)를 주면 자소서의 '직무 적합성'을 0~100으로 점수화하고, 
어떤 스킬/경험이 일치하는지, 부족한 키워드는 무엇인지 정리한다.

채용공고:
{job_description}

자소서:
{cover_letter_text}

응답은 반드시 다음 JSON 형식으로만 출력하라:
{{
 "score": 78,
 "matched_skills":["Python", "팀리딩", "프로젝트 관리"],
 "missing_skills":["클라우드","데이터 파이프라인", "머신러닝"],
 "explanation":"지원자는 Python과 팀리딩 경험이 우수하지만, 클라우드 기술과 데이터 파이프라인 경험이 부족합니다."
}}
"""

# 4. 문장별 개선(문장 리라이터) 프롬프트
SENTENCE_IMPROVEMENT_PROMPT = """
각 문장을 더 간결하고 적극적으로 바꿔라. 
원래 문장과 개선 문장을 짝지어 반환.

자소서:
{cover_letter_text}

응답은 반드시 다음 JSON 배열 형식으로만 출력하라:
[
  {{"original":"원본 문장", "improved":"개선된 문장 (한 줄)", "improvement_type":"간결성"}},
  {{"original":"다른 원본 문장", "improved":"다른 개선 문장", "improvement_type":"적극성"}}
]

개선 유형은 "간결성", "적극성", "문법", "전문성" 중에서 선택하라.
"""

# 5. 평가 루브릭 점수화 프롬프트 (현업 IT기업 기준)
EVALUATION_RUBRIC_PROMPT = """
당신은 경력 15년의 IT기업 HR 전문가이다. 
자소서를 다음 현업 IT기업 평가 기준으로 0~10점 척도로 평가해라.

[현업 IT기업 자소서 평가 기준]
1. 기술 적합성 (Tech Fit) (0-10): 사용 기술 스택, 프로젝트 경험, 문제 해결 능력
2. 직무 이해도 (0-10): 해당 포지션의 역할·책임에 대한 명확한 이해
3. 성장 가능성 (0-10): 학습 태도, 새로운 기술 습득 경험
4. 팀워크/커뮤니케이션 (0-10): 협업 경험, 갈등 해결 사례
5. 동기/회사 이해도 (0-10): 지원 동기, 회사와의 가치관 일치 여부
6. 문제 해결 능력 (0-10): STAR 기법 적용, 구체적 사례 제시
7. 성과 지향성 (0-10): 정량적 성과, 임팩트 있는 결과
8. 문법 및 표현 (0-10): 문장 구조, 전문성, 오류 정도

자소서:
{cover_letter_text}

직무 설명:
{job_description}

응답은 반드시 다음 JSON 형식으로만 출력하라:
{{
  "tech_fit": 8.5,
  "job_understanding": 7.0,
  "growth_potential": 8.0,
  "teamwork_communication": 7.5,
  "motivation_company_fit": 8.0,
  "problem_solving": 7.0,
  "performance_orientation": 6.5,
  "grammar_expression": 9.0,
  "overall_score": 7.7
}}
"""

# 6. 종합 분석 프롬프트 (모든 분석을 한 번에) - 현업 IT기업 기준
COMPREHENSIVE_ANALYSIS_PROMPT = """
당신은 20년 경력의 IT기업 HR 컨설턴트이다.
지원자의 자소서를 종합적으로 분석하여 다음 항목들을 모두 평가해라.

자소서:
{cover_letter_text}

직무 설명:
{job_description}

다음 JSON 형식으로 응답하라:
{{
  "summary": "자소서 핵심 요약 (3문장 이내)",
  "top_strengths": [
    {{"strength":"강점1", "evidence":"증거 문장", "confidence": 0.9}},
    {{"strength":"강점2", "evidence":"증거 문장", "confidence": 0.85}},
    {{"strength":"강점3", "evidence":"증거 문장", "confidence": 0.8}}
  ],
  "star_cases": [
    {{"s":"상황", "t":"과제", "a":"행동", "r":"결과", "evidence_sentence_indices":[2,3]}}
  ],
  "job_suitability": {{
    "score": 85,
    "matched_skills": ["스킬1", "스킬2"],
    "missing_skills": ["부족한스킬1"],
    "explanation": "적합성 점수 근거"
  }},
  "evaluation_rubric": {{
    "tech_fit": 8.5,
    "job_understanding": 7.0,
    "growth_potential": 8.0,
    "teamwork_communication": 7.5,
    "motivation_company_fit": 8.0,
    "problem_solving": 7.0,
    "performance_orientation": 6.5,
    "grammar_expression": 9.0,
    "overall_score": 7.7
  }},
  "sentence_improvements": [
    {{"original":"원본", "improved":"개선안", "improvement_type":"간결성"}}
  ]
}}
"""

# 7. 개인정보 마스킹 프롬프트
PERSONAL_INFO_MASKING_PROMPT = """
다음 텍스트에서 개인정보(이름, 전화번호, 이메일, 주민번호, 주소 등)를 찾아 마스킹 처리해라.

원본 텍스트:
{text}

응답은 반드시 다음 JSON 형식으로만 출력하라:
{{
  "masked_text": "마스킹된 텍스트",
  "masked_items": [
    {{"type": "이름", "original": "홍길동", "masked": "***"}},
    {{"type": "전화번호", "original": "010-1234-5678", "masked": "***-****-****"}}
  ]
}}
"""

# 프롬프트 유틸리티 함수
def format_prompt(template: str, **kwargs) -> str:
    """프롬프트 템플릿에 변수를 적용하여 완성된 프롬프트를 반환"""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"프롬프트 템플릿에 필요한 변수가 누락되었습니다: {e}")

def get_analysis_prompt(analysis_type: str, **kwargs) -> str:
    """분석 유형에 따른 적절한 프롬프트를 반환"""
    prompts = {
        "summary": SUMMARY_AND_STRENGTHS_PROMPT,
        "star": STAR_EXTRACTION_PROMPT,
        "suitability": JOB_SUITABILITY_PROMPT,
        "improvement": SENTENCE_IMPROVEMENT_PROMPT,
        "rubric": EVALUATION_RUBRIC_PROMPT,
        "comprehensive": COMPREHENSIVE_ANALYSIS_PROMPT,
        "masking": PERSONAL_INFO_MASKING_PROMPT
    }
    
    if analysis_type not in prompts:
        raise ValueError(f"지원하지 않는 분석 유형입니다: {analysis_type}")
    
    return format_prompt(prompts[analysis_type], **kwargs)
