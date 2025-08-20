/**
 * 사용자 입력의 맥락을 분류하는 유틸리티
 */

// 맥락 분류 키워드 정의
const contextKeywords = {
  job_posting: [
    '채용', '구인', '모집', '공고', '직원', '사원', '인재', '인력',
    '부서', '팀', '직무', '포지션', '업무', '담당', '책임',
    '근무', '근무시간', '근무일', '근무형태', '고용형태',
    '급여', '연봉', '월급', '보수', '복리후생', '혜택',
    '자격', '요건', '경력', '신입', '경험', '스킬', '기술',
    '지역', '위치', '근무지', '회사', '기업', '업체'
  ],
  resume_analysis: [
    '이력서', '자기소개서', '경력기술서', '포트폴리오',
    '학력', '경력', '자격증', '수상', '프로젝트', '활동',
    '분석', '평가', '검토', '검증', '확인', '점검'
  ],
  interview_management: [
    '면접', '인터뷰', '채용면접', '1차면접', '2차면접', '최종면접',
    '면접관', '지원자', '후보자', '면접일정', '면접시간',
    '면접장소', '면접방식', '온라인면접', '오프라인면접',
    '면접평가', '면접결과', '합격', '불합격', '대기'
  ],
  portfolio_analysis: [
    '포트폴리오', '작품', '프로젝트', '깃허브', '깃헙',
    '코딩', '개발', '디자인', '기술스택', '프레임워크',
    '언어', '라이브러리', 'API', '데이터베이스', '클라우드'
  ],
  cover_letter_validation: [
    '자기소개서', '지원동기', '입사동기', '성장과정',
    '장단점', '강점', '약점', '목표', '계획', '비전',
    '검증', '검토', '평가', '점검', '확인'
  ],
  applicant_management: [
    '지원자', '후보자', '지원현황', '지원상태', '지원자관리',
    '서류전형', '1차전형', '2차전형', '최종전형',
    '합격', '불합격', '대기', '보류', '취소',
    '통보', '연락', '안내', '일정', '스케줄'
  ]
};

/**
 * 사용자 입력의 맥락을 분류
 * @param {string} userInput - 사용자 입력 텍스트
 * @returns {string} 분류된 맥락 (기본값: 'job_posting')
 */
export const classifyContext = async (userInput) => {
  if (!userInput || typeof userInput !== 'string') {
    return 'job_posting';
  }

  const normalizedInput = userInput.toLowerCase().replace(/\s+/g, '');
  const contextScores = {};

  // 각 맥락별 키워드 매칭 점수 계산
  for (const [context, keywords] of Object.entries(contextKeywords)) {
    let score = 0;
    
    for (const keyword of keywords) {
      const normalizedKeyword = keyword.toLowerCase().replace(/\s+/g, '');
      
      // 정확한 키워드 매칭
      if (normalizedInput.includes(normalizedKeyword)) {
        score += 2;
      }
      
      // 부분 키워드 매칭
      if (normalizedKeyword.length > 2 && normalizedInput.includes(normalizedKeyword.substring(0, 2))) {
        score += 1;
      }
    }
    
    contextScores[context] = score;
  }

  // 가장 높은 점수의 맥락 반환
  const maxScore = Math.max(...Object.values(contextScores));
  const classifiedContext = Object.keys(contextScores).find(
    context => contextScores[context] === maxScore
  );

  // 점수가 0인 경우 기본값 반환
  return maxScore > 0 ? classifiedContext : 'job_posting';
};

/**
 * 맥락별 우선순위 설정
 * @param {string} primaryContext - 주요 맥락
 * @param {string} secondaryContext - 보조 맥락
 * @returns {object} 맥락 우선순위 정보
 */
export const getContextPriority = (primaryContext, secondaryContext = null) => {
  return {
    primary: primaryContext,
    secondary: secondaryContext,
    timestamp: Date.now()
  };
};

