// 맥락(Context) 분류기 - LLM/임베딩 혼합 인터페이스 (간이 스텁)

export const CONTEXT_CATEGORIES = [
  'job_posting',
  'resume_analysis',
  'interview_mgmt',
  'report_stats',
  'post_process',
  'general_chat'
];

// 간이 LLM 분류 프롬프트 호출 대신, 키워드 휴리스틱 + 확장 포인트만 제공
export async function classifyContext(userInput, embeddingSearchFn = null) {
  const text = String(userInput || '').toLowerCase();

  // 1) 간단 휴리스틱 (우선순위 낮음, 빠른 경로)
  if (/(공고|채용문|모집|채용공고|채용\s*작성|공고\s*작성)/.test(text)) return 'job_posting';
  if (/(지원서|이력서|자소서|포트폴리오|합격\s*가능성)/.test(text)) return 'resume_analysis';
  if (/(면접|인터뷰|일정|스케줄|평가|질문)/.test(text)) return 'interview_mgmt';
  if (/(통계|리포트|보고서|pdf|분석\s*자료)/.test(text)) return 'report_stats';
  if (/(사후|후기|결과\s*정리|피드백|후속\s*조치)/.test(text)) return 'post_process';

  // 2) 벡터 검색 핸들 (있다면 활용)
  if (embeddingSearchFn) {
    try {
      const category = await embeddingSearchFn(text);
      if (CONTEXT_CATEGORIES.includes(category)) return category;
    } catch (_) {}
  }

  // 3) 기본값
  return 'general_chat';
}


