import React from 'react';
import styled from 'styled-components';

const TestButton = styled.button`
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 15px;

  &:hover {
    background: linear-gradient(135deg, #ff5252, #d63031);
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 10px rgba(255, 107, 107, 0.3);
  }

  @media (max-width: 768px) {
    padding: 8px 16px;
    font-size: 12px;
    margin-left: 10px;
  }
`;

const Icon = styled.span`
  font-size: 16px;
`;

// 샘플 데이터 정의
const SAMPLE_DATA = {
  // 기본 정보
  companyName: '(주)테크혁신',
  jobTitle: '웹개발자',
  department: '개발팀',
  employmentType: '정규직',
  experienceLevel: '2년이상',
  headCount: '0명',
  
  // 위치 및 근무조건
  workLocation: '서울특별시 강남구 테헤란로 123',
  workingHours: '9시부터 3시',
  workDays: '주중',
  salary: '연봉 4,000만원 - 6,000만원 (경력에 따라 협의)',
  
  // 채용 정보
  recruitmentPeriod: '9월 3일까지',
  hiringProcess: '서류전형 → 1차 면접 → 2차 면접 → 최종합격',
  startDate: '2024.10.01 (협의 가능)',
  
  // 업무 내용
  jobDescription: `웹개발`,
  
  // 자격 요건
  requirements: `• 컴퓨터공학 또는 관련 전공 학사 이상
• JavaScript, React, Node.js 실무 경험 2년 이상
• MySQL, MongoDB 등 데이터베이스 활용 경험
• Git을 활용한 협업 경험
• 원활한 의사소통 능력`,
  
  // 우대 사항
  preferred: `• TypeScript 개발 경험
• AWS, Docker 등 클라우드 및 컨테이너 기술 경험
• 스타트업 또는 기술 기업 근무 경험
• 개인 프로젝트 또는 오픈소스 기여 경험
• 영어 가능자`,
  
  // 복리후생
  benefits: `주말보장, 재택가능`,
  
  // 회사 소개
  companyInfo: `저희 (주)테크혁신은 2018년 설립된 핀테크 스타트업으로, 
혁신적인 금융 솔루션을 개발하는 회사입니다.
현재 직원 50명 규모로 빠르게 성장하고 있으며,
개발자 친화적인 문화와 자율적인 업무 환경을 자랑합니다.`,
  
  // 연락처
  contactInfo: `담당자: 김철수 팀장
이메일: test@test.com
전화: 02-1234-5678
주소: 서울특별시 강남구 테헤란로 123, 테크빌딩 10층`
};

const TestAutoFillButton = ({ onAutoFill }) => {
  const handleAutoFill = () => {
    if (onAutoFill) {
      onAutoFill(SAMPLE_DATA);
    }
  };

  return (
    <TestButton onClick={handleAutoFill} title="테스트용 샘플 데이터를 자동으로 입력합니다">
      <Icon>🧪</Icon>
      테스트 자동입력
    </TestButton>
  );
};

export default TestAutoFillButton;
