import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import {
  FiHome,
  FiBriefcase,
  FiUserCheck,
  FiSettings,
  FiDatabase,
  FiUsers,
  FiBarChart2,
  FiFileText,
  FiVideo,
  FiCalendar,
  FiCode,
  FiEdit3,
  FiUser,
  FiGitBranch,
  FiMessageCircle,
  FiSearch,
  FiUpload,
  FiDownload,
  FiEye,
  FiCheckCircle,
  FiXCircle,
  FiStar,
  FiTrendingUp,
  FiImage,
  FiBookOpen,
  FiMessageSquare,
  FiList
} from 'react-icons/fi';

const HelpPageContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const PageTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  text-align: center;
`;

const PageSubtitle = styled.p`
  font-size: 16px;
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 32px;
`;

const TabContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
  border-bottom: 2px solid var(--border-color);
  margin-bottom: 32px;
  padding-bottom: 8px;
`;

const Tab = styled.button`
  padding: 12px 16px;
  border: none;
  background: none;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  border-radius: 8px;
  transition: var(--transition);
  white-space: nowrap;
  min-width: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 14px;

  &:hover {
    color: var(--primary-color);
    background: rgba(0, 200, 81, 0.05);
  }

  &.active {
    color: var(--primary-color);
    background: rgba(0, 200, 81, 0.1);
    border: 1px solid rgba(0, 200, 81, 0.2);
  }
`;

const TabContent = styled(motion.div)`
  min-height: 400px;
`;

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
`;

const FeatureCard = styled.div`
  background: var(--background-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  transition: var(--transition);

  &:hover {
    border-color: var(--primary-color);
    box-shadow: 0 4px 12px rgba(0, 200, 81, 0.1);
  }
`;

const FeatureTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FeatureDescription = styled.p`
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
`;

const FeatureSteps = styled.ul`
  color: var(--text-secondary);
  padding-left: 20px;
  margin: 0;
`;

const FeatureStep = styled.li`
  margin-bottom: 4px;
  line-height: 1.5;
`;

const tabs = [
  {
    id: 'overview',
    name: '개요',
    icon: FiHome
  },
  {
    id: 'dashboard',
    name: '대시보드',
    icon: FiBarChart2
  },
  {
    id: 'ai-recruitment',
    name: 'AI 채용공고',
    icon: FiMessageCircle
  },
  {
    id: 'resume-management',
    name: '이력서 관리',
    icon: FiFileText
  },
  {
    id: 'cover-letter-validation',
    name: '자기소개서 검증',
    icon: FiEdit3
  },
  {
    id: 'talent-recommendation',
    name: '인재 추천',
    icon: FiStar
  },
  {
    id: 'similar-talent',
    name: '유사인재 추천',
    icon: FiUsers
  },
  {
    id: 'plagiarism-check',
    name: '자소서 표절 검사',
    icon: FiSearch
  },
  {
    id: 'elasticsearch',
    name: 'Elasticsearch',
    icon: FiSearch
  },
  {
    id: 'pdf-ocr',
    name: 'PDF OCR',
    icon: FiImage
  },
  {
    id: 'github-test',
    name: 'GitHub 테스트',
    icon: FiGitBranch
  },
  {
    id: 'settings',
    name: '설정 및 지원',
    icon: FiSettings
  },
  {
    id: 'sample-data',
    name: '샘플 데이터 관리',
    icon: FiDatabase
  },
  {
    id: 'company-culture',
    name: '인재상 관리',
    icon: FiUsers
  },
  {
    id: 'analysis-weights',
    name: '분석 가중치 설정',
    icon: FiBarChart2
  },
  {
    id: 'pick-talk',
    name: '픽톡',
    icon: FiMessageCircle
  }
];

const HelpPage = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const renderOverview = () => (
    <Section>
      <SectionTitle>
        <FiHome size={24} />
        AI 채용 관리 시스템 개요
      </SectionTitle>
      <FeatureDescription>
        AI 채용 관리 시스템은 인공지능을 활용하여 채용 프로세스를 자동화하고 효율화하는 통합 솔루션입니다.
        지원자 관리, 채용공고 등록, AI 기반 분석 등 다양한 기능을 제공합니다.
      </FeatureDescription>

      <SectionTitle>
        <FiBarChart2 size={24} />
        시스템 아키텍처
      </SectionTitle>
      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiMessageCircle size={20} />
            AI 엔진
          </FeatureTitle>
          <FeatureDescription>
            <strong>적용 모델:</strong> OpenAI GPT-4, Claude-3.5-Sonnet<br/>
            <strong>기능:</strong> 자연어 처리, 문서 분석, 대화형 AI<br/>
            <strong>스펙:</strong> 실시간 응답, 다국어 지원, 컨텍스트 이해
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiDatabase size={20} />
            데이터베이스
          </FeatureTitle>
          <FeatureDescription>
            <strong>적용 모델:</strong> MongoDB Atlas<br/>
            <strong>기능:</strong> 지원자 정보 저장, 채용공고 관리, 분석 결과 저장<br/>
            <strong>스펙:</strong> NoSQL, 실시간 동기화, 자동 백업
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiUsers size={20} />
            사용자 인터페이스
          </FeatureTitle>
          <FeatureDescription>
            <strong>적용 모델:</strong> React 18, Styled Components<br/>
            <strong>기능:</strong> 반응형 웹, 실시간 업데이트, 직관적 UI<br/>
            <strong>스펙:</strong> SPA, PWA 지원, 다크모드
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>

      <SectionTitle>
        <FiSettings size={24} />
        주요 기능
      </SectionTitle>
      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiBriefcase size={20} />
            스마트 채용공고
          </FeatureTitle>
          <FeatureDescription>
            AI가 도와주는 채용공고 작성으로 더 나은 공고를 만들 수 있습니다.
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiUserCheck size={20} />
            지원자 분석
          </FeatureTitle>
          <FeatureDescription>
            이력서, 자기소개서, 포트폴리오를 종합적으로 분석하여 적합도를 평가합니다.
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiMessageCircle size={20} />
            AI 챗봇
          </FeatureTitle>
          <FeatureDescription>
            채용 관련 질문에 실시간으로 답변하고 도움을 제공합니다.
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderDashboard = () => (
    <Section>
      <SectionTitle>
        <FiBarChart2 size={24} />
        대시보드
      </SectionTitle>
      <FeatureDescription>
        채용 현황을 한눈에 파악할 수 있는 통합 대시보드입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            실시간 통계
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 지원자 수, 채용공고 현황, AI 분석 결과<br/>
            <strong>적용 모델:</strong> MongoDB Aggregation Pipeline<br/>
            <strong>스펙:</strong> 실시간 업데이트, 자동 새로고침 (5분 간격)<br/>
            <strong>사용방법:</strong> 메인 페이지에서 자동으로 표시되며, 각 통계를 클릭하면 상세 페이지로 이동
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiUsers size={20} />
            지원자 현황
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 지원자 상태별 분류, 최근 지원자 목록<br/>
            <strong>적용 모델:</strong> React Chart.js, MongoDB Query<br/>
            <strong>스펙:</strong> 차트 시각화, 필터링 기능<br/>
            <strong>사용방법:</strong> 차트 영역을 클릭하여 해당 상태의 지원자 목록 확인
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBriefcase size={20} />
            채용공고 현황
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 진행 중인 채용공고, 마감 예정 공고<br/>
            <strong>적용 모델:</strong> MongoDB Date Query<br/>
            <strong>스펙:</strong> 날짜 기반 정렬, 알림 기능<br/>
            <strong>사용방법:</strong> 각 공고 카드를 클릭하여 상세 정보 및 지원자 목록 확인
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderRecruitment = () => (
    <Section>
      <SectionTitle>
        <FiBriefcase size={24} />
        채용관리
      </SectionTitle>
      <FeatureDescription>
        AI 기반 채용공고 작성 및 관리 기능을 제공합니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiEdit3 size={20} />
            일반 채용공고 등록
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 수동 채용공고 작성, AI 제목 추천<br/>
            <strong>적용 모델:</strong> React Hook Form, Yup Validation, OpenAI GPT-4<br/>
            <strong>스펙:</strong> 실시간 유효성 검사, 자동 저장, AI 제목 생성<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>채용공고 등록 메뉴 선택</FeatureStep>
            <FeatureStep>회사 정보 및 직무 내용 입력</FeatureStep>
            <FeatureStep>AI 제목 추천 기능으로 매력적인 제목 생성</FeatureStep>
            <FeatureStep>필요한 자격요건 및 우대사항 작성</FeatureStep>
            <FeatureStep>공고 등록 및 발행</FeatureStep>
            <FeatureStep>AI 챗봇을 통한 등록 가능</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiMessageCircle size={20} />
            AI 채용공고 등록
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> AI 대화형 채용공고 작성, 자동 최적화<br/>
            <strong>적용 모델:</strong> OpenAI GPT-4, LangGraph<br/>
            <strong>스펙:</strong> 실시간 대화, 컨텍스트 기억, 다국어 지원<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>AI 채용공고 등록 메뉴 선택</FeatureStep>
            <FeatureStep>AI와 대화하며 채용공고 내용 구성</FeatureStep>
            <FeatureStep>AI가 제안하는 내용 검토 및 수정</FeatureStep>
            <FeatureStep>최종 검토 후 공고 등록</FeatureStep>
            <FeatureStep>상세내용 픽톡 참고</FeatureStep>
          </FeatureSteps>
        </FeatureCard>


      </FeatureGrid>
    </Section>
  );

  const renderApplicantManagement = () => (
    <Section>
      <SectionTitle>
        <FiUserCheck size={24} />
        지원자 관리
      </SectionTitle>
      <FeatureDescription>
        지원자의 이력서, 자기소개서, 포트폴리오를 AI가 분석하여 종합적으로 평가합니다.
      </FeatureDescription>

      <SectionTitle>
        <FiFileText size={20} />
        이력서 관리
      </SectionTitle>
      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiFileText size={20} />
            이력서 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 기본 항목 분석, 기술 스택 추출, 경력 연도 계산<br/>
            <strong>적용 모델:</strong> OpenAI GPT-4, NER (Named Entity Recognition)<br/>
            <strong>스펙:</strong> PDF/이미지 OCR, 텍스트 추출, 구조화된 데이터 변환<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>지원자 상세 페이지에서 이력서 탭 선택</FeatureStep>
            <FeatureStep>기본적으로는 DB에서 데이터를 불러오나, 새 지원자 등록 버튼을 통해 등록 가능(PDF)</FeatureStep>
            <FeatureStep>AI 분석 결과 확인 (경력, 기술, 학력 등)</FeatureStep>
            <FeatureStep>분석된 정보 검토 및 수정</FeatureStep>
            <FeatureStep>다른 지원자와 비교 분석</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiCode size={20} />
            기술 스택 매칭
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 요구 기술과 보유 기술 매칭, 기술 수준 평가<br/>
            <strong>적용 모델:</strong> Keyword Matching, Semantic Analysis<br/>
            <strong>스펙:</strong> 기술별 매칭률, 숙련도 추정<br/>
            <strong>사용방법:</strong> 채용공고의 요구 기술과 자동 비교하여 매칭률 표시<br/>
            <strong>가중치 설정:</strong> 인재상 관리 및 분석 가중치 설정을 통해 점수 가중치 설정 가능
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>

      <SectionTitle>
        <FiEdit3 size={20} />
        자기소개서 관리(백엔드 연동 안됨)
      </SectionTitle>
      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiEdit3 size={20} />
            자기소개서 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 내용 분석, 표현력 평가, 적합도 측정<br/>
            <strong>적용 모델:</strong> OpenAI GPT-4, Sentiment Analysis<br/>
            <strong>스펙:</strong> 자연어 처리, 감정 분석, 키워드 추출<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>지원자 상세 페이지에서 자기소개서 탭 선택</FeatureStep>
            <FeatureStep>AI 분석 결과 확인 (내용, 표현력, 적합도)</FeatureStep>
            <FeatureStep>핵심 키워드 및 강점/약점 확인</FeatureStep>
            <FeatureStep>다른 지원자와 비교 분석</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiMessageCircle size={20} />
            내용 적합도 평가
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 채용공고와의 적합도, 핵심 키워드 매칭<br/>
            <strong>적용 모델:</strong> Semantic Similarity, Keyword Extraction<br/>
            <strong>스펙:</strong> 코사인 유사도, TF-IDF 분석<br/>
            <strong>사용방법:</strong> 채용공고 내용과 자동 비교하여 적합도 점수 제공
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            표현력 평가
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 문장 구조, 어휘력, 논리성 평가<br/>
            <strong>적용 모델:</strong> NLP Pipeline, Grammar Analysis<br/>
            <strong>스펙:</strong> 문법 검사, 어휘 다양성, 논리 구조 분석<br/>
            <strong>사용방법:</strong> AI가 자동으로 표현력 점수를 산출하고 개선점 제안
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>

      <SectionTitle>
        <FiCode size={20} />
        포트폴리오 관리
      </SectionTitle>
      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiGitBranch size={20} />
            GitHub 프로필 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> GitHub API 연동, 레포지토리 분석, 기여도 측정<br/>
            <strong>적용 모델:</strong> GitHub API v4, GraphQL<br/>
            <strong>스펙:</strong> 실시간 데이터 수집, 언어별 분석, 활동 패턴 분석<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>지원자 상세 페이지에서 포트폴리오 탭 선택</FeatureStep>
            <FeatureStep>GitHub URL 입력 또는 DB 자동 감지</FeatureStep>
            <FeatureStep>AI 분석 결과 확인 (기술 스택, 활동도, 코드 품질)</FeatureStep>
            <FeatureStep>프로젝트별 상세 분석 및 평가</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiCode size={20} />
            기술 스택 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 사용 언어 분석, 프레임워크 식별, 숙련도 평가<br/>
            <strong>적용 모델:</strong> Language Detection, Repository Analysis<br/>
            <strong>스펙:</strong> 언어별 코드 라인 수, 최근 활동도, 프로젝트 규모<br/>
            <strong>사용방법:</strong> GitHub 데이터를 기반으로 기술 스택과 숙련도를 자동 분석
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            활동도 및 기여도
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 커밋 패턴 분석, 기여도 측정, 협업 능력 평가<br/>
            <strong>적용 모델:</strong> Git Statistics, Contribution Analysis<br/>
            <strong>스펙:</strong> 일별/월별 활동 패턴, PR/Issue 기여도<br/>
            <strong>사용방법:</strong> GitHub 활동 데이터를 시각화하여 개발 역량과 협업 능력 평가
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );



  const renderSettings = () => (
    <Section>
      <SectionTitle>
        <FiSettings size={24} />
        설정 및 지원
      </SectionTitle>
      <FeatureDescription>
        합격자/불합격자 관리 및 이메일 정보 설정 기능을 제공합니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiCheckCircle size={20} />
            합격자 관리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 합격자 목록 관리, 합격 통보, 상태 업데이트<br/>
            <strong>적용 모델:</strong> MongoDB, Status Management System<br/>
            <strong>스펙:</strong> 실시간 상태 동기화, 자동 알림 발송<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>설정 및 지원 메뉴 접속</FeatureStep>
            <FeatureStep>합격자 탭에서 합격자 목록 확인</FeatureStep>
            <FeatureStep>합격자 상태 업데이트 및 관리</FeatureStep>
            <FeatureStep>합격 통보 이메일 발송</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiXCircle size={20} />
            불합격자 관리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 불합격자 목록 관리, 불합격 통보, 피드백 제공<br/>
            <strong>적용 모델:</strong> MongoDB, Feedback System<br/>
            <strong>스펙:</strong> 상태 추적, 자동 알림, 피드백 템플릿<br/>
            <strong>사용방법:</strong> 불합격자 탭에서 불합격자 목록 확인 및 통보 관리
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiMessageCircle size={20} />
            이메일 정보 설정
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 이메일 템플릿 관리, 발송 설정, 연락처 관리<br/>
            <strong>적용 모델:</strong> Email Service, Template Engine<br/>
            <strong>스펙:</strong> SMTP 연동, 템플릿 커스터마이징, 발송 로그<br/>
            <strong>사용방법:</strong> 이메일 정보 탭에서 템플릿 설정 및 발송 옵션 관리
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderSampleData = () => (
    <Section>
      <SectionTitle>
        <FiDatabase size={24} />
        샘플 데이터 관리
      </SectionTitle>
      <FeatureDescription>
        시스템 테스트 및 데모를 위한 샘플 데이터를 관리합니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiDatabase size={20} />
            샘플 지원자 생성
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 가상 지원자 데이터 생성, 다양한 프로필 타입<br/>
            <strong>적용 모델:</strong> Faker.js, Custom Data Generator<br/>
            <strong>스펙:</strong> 한국어 이름, 이력서, 자기소개서 자동 생성<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>샘플 데이터 관리 메뉴 접속</FeatureStep>
            <FeatureStep>생성할 지원자 수 및 타입 선택</FeatureStep>
            <FeatureStep>샘플 데이터 생성 실행</FeatureStep>
            <FeatureStep>생성된 데이터 확인 및 테스트</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiUpload size={20} />
            JSON 데이터 등록
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> JSON 파일을 통한 대량 데이터 등록, 구조화된 데이터 관리<br/>
            <strong>적용 모델:</strong> JSON Parser, Data Validation, Batch Processing<br/>
            <strong>스펙:</strong> 지원자, 채용공고 데이터 일괄 등록, 데이터 검증<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>샘플 데이터 관리 메뉴 접속</FeatureStep>
            <FeatureStep>JSON 파일 업로드 선택</FeatureStep>
            <FeatureStep>sample_applicants_data.json 파일 업로드</FeatureStep>
            <FeatureStep>데이터 검증 및 등록 실행</FeatureStep>
            <FeatureStep>등록된 데이터 확인 및 관리</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiList size={20} />
            데이터 생성 순서
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 체계적인 데이터 생성 순서, 의존성 관리<br/>
            <strong>적용 모델:</strong> Dependency Management, Sequential Processing<br/>
            <strong>스펙:</strong> 순차적 데이터 생성, 관계형 데이터 관리<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>1단계: 채용공고 등록 (기본 정보 및 요구사항)</FeatureStep>
            <FeatureStep>2단계: 지원자 등록 (개인정보 및 경력사항)</FeatureStep>
            <FeatureStep>3단계: 자기소개서 등록 (지원자별 맞춤 자소서)</FeatureStep>
            <FeatureStep>각 단계별 데이터 검증 및 관계 설정</FeatureStep>
            <FeatureStep>전체 데이터 일관성 확인</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiFileText size={20} />
            데이터 초기화
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 테스트 데이터 삭제, 시스템 초기화<br/>
            <strong>적용 모델:</strong> MongoDB Delete Operations<br/>
            <strong>스펙:</strong> 선택적 삭제, 백업 기능<br/>
            <strong>사용방법:</strong> 테스트 완료 후 샘플 데이터를 안전하게 삭제
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            데이터 백업
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 데이터 백업, 복원, 내보내기<br/>
            <strong>적용 모델:</strong> MongoDB Export/Import<br/>
            <strong>스펙:</strong> JSON 형식<br/>
            <strong>사용방법:</strong> /docs 폴더 내 sample_applicants_data.json 파일 등록
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderCompanyCulture = () => (
    <Section>
      <SectionTitle>
        <FiUsers size={24} />
        인재상 관리
      </SectionTitle>
      <FeatureDescription>
        회사의 인재상과 문화를 정의하여 AI 분석에 반영합니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiUsers size={20} />
            인재상 정의
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 회사 가치관, 인재상, 문화적 특성 정의<br/>
            <strong>적용 모델:</strong> Custom Culture Model, NLP Analysis<br/>
            <strong>스펙:</strong> 키워드 기반 매칭, 가중치 조정<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>인재상 관리 메뉴 접속</FeatureStep>
            <FeatureStep>회사 인재상 및 가치관 정의</FeatureStep>
            <FeatureStep>문화적 특성 및 키워드 설정</FeatureStep>
            <FeatureStep>AI 분석에 반영하여 저장</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiMessageCircle size={20} />
            문화적 적합도 평가
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 지원자와 회사 문화의 적합도 측정<br/>
            <strong>적용 모델:</strong> Semantic Similarity, Culture Matching<br/>
            <strong>스펙:</strong> 0-100점 척도, 상세 분석 리포트<br/>
            <strong>사용방법:</strong> 지원자 분석 시 자동으로 문화적 적합도 점수 제공
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            가중치 설정
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 문화적 적합도 가중치 조정<br/>
            <strong>적용 모델:</strong> Weighted Scoring Algorithm<br/>
            <strong>스펙:</strong> 실시간 가중치 적용, 분석 결과 반영<br/>
            <strong>사용방법:</strong> 분석 가중치 설정에서 문화적 적합도 비중 조정
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderAnalysisWeights = () => (
    <Section>
      <SectionTitle>
        <FiBarChart2 size={24} />
        분석 가중치 설정
      </SectionTitle>
      <FeatureDescription>
        AI 분석 시 각 요소의 중요도를 조정하여 맞춤형 평가를 제공합니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            가중치 조정
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 각 분석 요소별 가중치 설정, 실시간 적용<br/>
            <strong>적용 모델:</strong> Weighted Scoring System<br/>
            <strong>스펙:</strong> 슬라이더 UI, 실시간 미리보기<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>분석 가중치 설정 메뉴 접속</FeatureStep>
            <FeatureStep>각 분석 요소별 가중치 조정</FeatureStep>
            <FeatureStep>미리보기로 결과 확인</FeatureStep>
            <FeatureStep>저장 후 새로운 분석에 적용<br></br>
              - 지원자 관리 분석기능 점수화에 자동 적용</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiFileText size={20} />
            분석 요소
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 경력, 기술, 자소서, 포트폴리오, 문화적 적합도<br/>
            <strong>적용 모델:</strong> Multi-factor Analysis<br/>
            <strong>스펙:</strong> 5개 주요 요소, 세부 하위 요소<br/>
            <strong>사용방법:</strong> 각 요소의 중요도에 따라 가중치를 0-100%로 설정
          </FeatureDescription>
        </FeatureCard>

      </FeatureGrid>
    </Section>
  );

  const renderAIRecruitment = () => (
    <Section>
      <SectionTitle>
        <FiMessageCircle size={24} />
        AI 채용공고 등록
      </SectionTitle>
      <FeatureDescription>
        AI와 대화하며 채용공고를 작성하고 최적화하는 고급 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiMessageCircle size={20} />
            대화형 채용공고 작성
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> AI와 실시간 대화, 단계별 가이드, 자동 최적화, 일반 자연어 대화 가능<br/>
            <strong>적용 모델:</strong> OpenAI GPT-4, LangGraph, Conversation Flow<br/>
            <strong>스펙:</strong> 컨텍스트 기억, 다국어 지원, 실시간 검증, 자연어 이해<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>AI 채용공고 등록 메뉴 선택</FeatureStep>
            <FeatureStep>AI와 자연스러운 대화로 채용공고 내용 구성</FeatureStep>
            <FeatureStep>AI가 제안하는 내용 검토 및 수정</FeatureStep>
            <FeatureStep>최종 검토 후 공고 등록</FeatureStep>
            <FeatureStep>'인재상 관리'를 통해 인재상 설정 가능</FeatureStep>
            <FeatureStep>상세내용 픽톡 참고</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        {/* <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            성과 분석 및 최적화
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 공고 성과 분석, A/B 테스트, 최적화 제안<br/>
            <strong>적용 모델:</strong> Analytics Engine, ML Optimization<br/>
            <strong>스펙:</strong> 실시간 성과 추적, 자동 최적화<br/>
            <strong>사용방법:</strong> 등록된 공고의 성과를 분석하여 개선점 제안
          </FeatureDescription>
        </FeatureCard> */}
      </FeatureGrid>
    </Section>
  );

  const renderResumeManagement = () => (
    <Section>
      <SectionTitle>
        <FiFileText size={24} />
        이력서 관리
      </SectionTitle>
      <FeatureDescription>
        지원자의 이력서를 체계적으로 관리하고 분석하는 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiUpload size={20} />
            이력서 업로드 및 파싱
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> PDF/이미지 업로드, OCR 텍스트 추출, 구조화된 데이터 변환<br/>
            <strong>적용 모델:</strong> Tesseract OCR, PDF Parser, NER<br/>
            <strong>스펙:</strong> 다중 형식 지원, 99% 정확도, 실시간 처리<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>이력서 관리 메뉴 접속</FeatureStep>
            <FeatureStep>PDF 또는 이미지 파일 업로드</FeatureStep>
            <FeatureStep>AI가 자동으로 텍스트 추출 및 구조화</FeatureStep>
            <FeatureStep>추출된 정보 검토 및 수정</FeatureStep>
            <FeatureStep>데이터베이스에 저장</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiSearch size={20} />
            이력서 검색 및 필터링
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 키워드 검색, 다중 필터, 고급 검색<br/>
            <strong>적용 모델:</strong> Elasticsearch, MongoDB Text Search<br/>
            <strong>스펙:</strong> 실시간 검색, 퍼지 매칭, 인덱싱<br/>
            <strong>사용방법:</strong> 검색어 입력 후 필터 옵션으로 결과 정제
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            이력서 분석 및 평가
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 경력 분석, 기술 스택 추출, 적합도 평가, 이력서 점수에 따른 ranking 처리<br/>
            <strong>적용 모델:</strong> OpenAI GPT-4, Custom Scoring Algorithm, Ranking System<br/>
            <strong>스펙:</strong> 0-100점 척도, 상세 분석 리포트, 자동 랭킹 정렬<br/>
            <strong>사용방법:</strong> 이력서 선택 후 AI 분석 실행하여 종합 평가 확인 및 랭킹 순위 확인
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderCoverLetterValidation = () => (
    <Section>
      <SectionTitle>
        <FiEdit3 size={24} />
        자기소개서 검증(백엔드 연동이 안됨)
      </SectionTitle>
      <FeatureDescription>
        지원자의 자기소개서를 AI가 검증하고 개선점을 제안하는 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiCheckCircle size={20} />
            내용 검증
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 사실 확인, 일관성 검사, 논리성 평가<br/>
            <strong>적용 모델:</strong> OpenAI GPT-4, Fact-checking AI<br/>
            <strong>스펙:</strong> 실시간 검증, 신뢰도 점수, 상세 리포트<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>자기소개서 검증 메뉴 접속</FeatureStep>
            <FeatureStep>검증할 자기소개서 선택</FeatureStep>
            <FeatureStep>AI가 내용 검증 실행</FeatureStep>
            <FeatureStep>검증 결과 및 개선점 확인</FeatureStep>
            <FeatureStep>필요시 수정 권고사항 적용</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiEdit3 size={20} />
            표현력 개선
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 문법 검사, 어휘 개선, 표현력 향상<br/>
            <strong>적용 모델:</strong> Grammar Checker, Style Transfer<br/>
            <strong>스펙:</strong> 실시간 수정 제안, 다국어 지원<br/>
            <strong>사용방법:</strong> AI가 자동으로 문법 오류 및 표현 개선점 제안
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiStar size={20} />
            적합도 평가
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 채용공고와의 적합도, 핵심 키워드 매칭<br/>
            <strong>적용 모델:</strong> Semantic Similarity, Keyword Matching<br/>
            <strong>스펙:</strong> 코사인 유사도, TF-IDF 분석<br/>
            <strong>사용방법:</strong> 채용공고와 비교하여 적합도 점수 및 매칭 키워드 제공
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderTalentRecommendation = () => (
    <Section>
      <SectionTitle>
        <FiStar size={24} />
        인재 추천
      </SectionTitle>
      <FeatureDescription>
        AI가 분석한 데이터를 바탕으로 최적의 인재를 추천하는 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiTrendingUp size={20} />
            AI 기반 추천
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 머신러닝 기반 추천, 다중 요소 분석, 실시간 랭킹<br/>
            <strong>적용 모델:</strong> Collaborative Filtering, Content-based Filtering<br/>
            <strong>스펙:</strong> 99% 정확도, 실시간 업데이트, 개인화 추천<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>인재 추천 메뉴 접속</FeatureStep>
            <FeatureStep>추천 기준 및 가중치 설정</FeatureStep>
            <FeatureStep>AI가 분석하여 추천 목록 생성</FeatureStep>
            <FeatureStep>추천된 인재 상세 정보 확인</FeatureStep>
            <FeatureStep>관심 있는 인재 선택 및 연락</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            매칭 점수 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 종합 매칭 점수, 세부 분석, 비교 기능<br/>
            <strong>적용 모델:</strong> Weighted Scoring, Multi-factor Analysis<br/>
            <strong>스펙:</strong> 0-100점 척도, 상세 분석 리포트<br/>
            <strong>사용방법:</strong> 각 지원자의 매칭 점수와 세부 분석 결과 확인
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiUsers size={20} />
            팀 적합성 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 팀 문화 적합성, 협업 능력, 리더십 평가<br/>
            <strong>적용 모델:</strong> Team Dynamics Analysis, Personality Assessment<br/>
            <strong>스펙:</strong> 팀별 맞춤 분석, 문화적 적합도 측정<br/>
            <strong>사용방법:</strong> 팀 구성원과의 적합성을 분석하여 팀워크 예측
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderSimilarTalent = () => (
    <Section>
      <SectionTitle>
        <FiUsers size={24} />
        유사인재 추천
      </SectionTitle>
      <FeatureDescription>
        특정 지원자와 유사한 프로필을 가진 다른 지원자들을 추천하는 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiSearch size={20} />
            유사도 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 프로필 유사도 계산, 다차원 비교, 실시간 매칭<br/>
            <strong>적용 모델:</strong> Cosine Similarity, Euclidean Distance, ML Clustering<br/>
            <strong>스펙:</strong> 0-100% 유사도 점수, 다중 기준 비교<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>지원자 관리 메뉴 접속</FeatureStep>
            <FeatureStep>기준이 될 지원자 선택</FeatureStep>
            <FeatureStep>하단 유사도 분석영역 확인</FeatureStep>
            <FeatureStep>AI가 유사한 인재 목록 생성</FeatureStep>
            <FeatureStep>유사도 점수와 함께 결과 확인</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            다중 기준 비교
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 경력, 기술, 학력, 경험 등 다중 기준 비교<br/>
            <strong>적용 모델:</strong> Multi-dimensional Analysis, Weighted Comparison<br/>
            <strong>스펙:</strong> 가중치 조정 가능, 상세 비교 리포트<br/>
            <strong>사용방법:</strong> 비교 기준별 가중치를 설정하여 맞춤형 유사도 분석
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiTrendingUp size={20} />
            추천 품질 관리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 추천 정확도 모니터링, 피드백 수집, 알고리즘 개선<br/>
            <strong>적용 모델:</strong> Recommendation Quality Metrics, Feedback Loop<br/>
            <strong>스펙:</strong> 실시간 품질 평가, 자동 개선<br/>
            <strong>사용방법:</strong> 추천 결과에 대한 피드백을 제공하여 추천 품질 향상
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderPlagiarismCheck = () => (
    <Section>
      <SectionTitle>
        <FiSearch size={24} />
        자소서 표절 검사
      </SectionTitle>
      <FeatureDescription>
        지원자의 자기소개서에서 표절 의심 부분을 AI가 검사하고 분석하는 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiSearch size={20} />
            표절 의심도 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 텍스트 유사도 검사, 표절 의심도 점수, 출처 추적<br/>
            <strong>적용 모델:</strong> Text Similarity Analysis, Plagiarism Detection AI<br/>
            <strong>스펙:</strong> 0-100% 의심도 점수, 실시간 검사, 상세 리포트<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>지원자 관리의 지원자 선택</FeatureStep>
            <FeatureStep>자소서 표절 의심도 검사 버튼 선택</FeatureStep>
            <FeatureStep>AI가 표절 의심도 분석 </FeatureStep>
            <FeatureStep>의심도 점수 및 상세 분석 결과 확인</FeatureStep>
            <FeatureStep>필요시 추가 검증 및 조치</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiFileText size={20} />
            텍스트 유사도 검사
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 문장별 유사도 분석, 패턴 인식, 출처 데이터베이스 비교<br/>
            <strong>적용 모델:</strong> NLP Similarity, Pattern Recognition, Database Matching<br/>
            <strong>스펙:</strong> 문장 단위 분석, 실시간 데이터베이스 검색<br/>
            <strong>사용방법:</strong> 문장별로 유사도 점수를 확인하고 의심 부분 상세 분석
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            의심도 리포트
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 종합 의심도 점수, 상세 분석 리포트, 개선 제안<br/>
            <strong>적용 모델:</strong> Report Generation, Risk Assessment<br/>
            <strong>스펙:</strong> PDF 리포트 생성, 시각화 차트, 개선 가이드<br/>
            <strong>사용방법:</strong> 의심도 리포트를 다운로드하여 상세 분석 결과 확인
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderElasticsearch = () => (
    <Section>
      <SectionTitle>
        <FiSearch size={24} />
        Elasticsearch
      </SectionTitle>
      <FeatureDescription>
        고성능 검색 엔진을 활용한 지원자 데이터 검색 및 분석 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiSearch size={20} />
            고성능 검색
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 실시간 검색, 전문 검색, 다중 필드 검색, 자동완성<br/>
            <strong>적용 모델:</strong> Elasticsearch, Lucene, Inverted Index<br/>
            <strong>스펙:</strong> 밀리초 단위 검색, 대용량 데이터 처리, 분산 검색<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>검색창에 키워드 입력</FeatureStep>
            <FeatureStep>Elasticsearch가 실시간으로 인덱스 검색</FeatureStep>
            <FeatureStep>관련도 점수 기반 결과 정렬</FeatureStep>
            <FeatureStep>필터링 및 세부 검색 옵션 활용</FeatureStep>
            <FeatureStep>검색 결과 상세 정보 확인</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            검색 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 검색 통계, 인기 키워드, 검색 패턴 분석<br/>
            <strong>적용 모델:</strong> Elasticsearch Aggregations, Analytics API<br/>
            <strong>스펙:</strong> 실시간 통계, 시계열 분석, 트렌드 분석<br/>
            <strong>사용방법:</strong> 검색 로그를 분석하여 사용자 검색 패턴 파악
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiDatabase size={20} />
            인덱스 관리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 자동 인덱싱, 인덱스 최적화, 데이터 동기화<br/>
            <strong>적용 모델:</strong> Elasticsearch Index Management, Data Pipeline<br/>
            <strong>스펙:</strong> 실시간 인덱싱, 자동 백업, 복제본 관리<br/>
            <strong>사용방법:</strong> 데이터 변경 시 자동으로 인덱스 업데이트 및 최적화
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderInterviewManagement = () => (
    <Section>
      <SectionTitle>
        <FiCalendar size={24} />
        면접 관리
      </SectionTitle>
      <FeatureDescription>
        면접 일정 관리, 면접관 배정, 면접 결과 관리 기능을 제공합니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiCalendar size={20} />
            면접 일정 관리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 일정 등록, 면접관 배정, 자동 알림, 캘린더 뷰<br/>
            <strong>적용 모델:</strong> Calendar API, Notification System<br/>
            <strong>스펙:</strong> 실시간 동기화, 자동 충돌 방지, 이메일/SMS 알림<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>면접 관리 메뉴 접속</FeatureStep>
            <FeatureStep>새 면접 일정 등록</FeatureStep>
            <FeatureStep>면접관 및 지원자 배정</FeatureStep>
            <FeatureStep>자동 알림 발송</FeatureStep>
            <FeatureStep>캘린더에서 일정 확인</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiUsers size={20} />
            면접관 관리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 면접관 프로필, 전문 분야, 가용 시간 관리<br/>
            <strong>적용 모델:</strong> Resource Management System<br/>
            <strong>스펙:</strong> 전문 분야별 자동 배정, 가용 시간 최적화<br/>
            <strong>사용방법:</strong> 면접관의 전문 분야와 가용 시간을 등록하여 자동 배정
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiFileText size={20} />
            면접 결과 관리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 면접 평가, 점수 입력, 종합 평가, 피드백 관리<br/>
            <strong>적용 모델:</strong> Evaluation System, Score Aggregation<br/>
            <strong>스펙:</strong> 실시간 평가, 자동 점수 계산, 상세 리포트<br/>
            <strong>사용방법:</strong> 면접 후 평가 점수와 피드백을 입력하여 종합 평가 생성
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderUserManagement = () => (
    <Section>
      <SectionTitle>
        <FiUser size={24} />
        사용자 관리
      </SectionTitle>
      <FeatureDescription>
        시스템 사용자들의 권한 관리, 프로필 관리, 활동 모니터링 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiUser size={20} />
            사용자 계정 관리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 계정 생성, 권한 설정, 프로필 관리, 비밀번호 관리<br/>
            <strong>적용 모델:</strong> RBAC (Role-Based Access Control)<br/>
            <strong>스펙:</strong> 다중 권한 레벨, 보안 인증, 자동 만료<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>사용자 관리 메뉴 접속</FeatureStep>
            <FeatureStep>새 사용자 계정 생성</FeatureStep>
            <FeatureStep>역할 및 권한 설정</FeatureStep>
            <FeatureStep>프로필 정보 입력</FeatureStep>
            <FeatureStep>계정 활성화 및 알림 발송</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiSettings size={20} />
            권한 및 역할 관리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 역할 정의, 권한 할당, 접근 제어, 감사 로그<br/>
            <strong>적용 모델:</strong> RBAC, ACL (Access Control List)<br/>
            <strong>스펙:</strong> 세밀한 권한 제어, 실시간 권한 변경<br/>
            <strong>사용방법:</strong> 역할별로 필요한 권한을 설정하여 사용자에게 할당
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBarChart2 size={20} />
            활동 모니터링
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 로그인 기록, 활동 추적, 보안 모니터링, 리포트 생성<br/>
            <strong>적용 모델:</strong> Audit System, Security Monitoring<br/>
            <strong>스펙:</strong> 실시간 모니터링, 이상 행동 탐지, 자동 알림<br/>
            <strong>사용방법:</strong> 사용자 활동을 실시간으로 모니터링하여 보안 이슈 탐지
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderPDFOCR = () => (
    <Section>
      <SectionTitle>
        <FiImage size={24} />
        PDF OCR
      </SectionTitle>
      <FeatureDescription>
        PDF 문서와 이미지에서 텍스트를 추출하고 분석하는 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiUpload size={20} />
            문서 업로드 및 처리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> PDF/이미지 업로드, OCR 텍스트 추출, 다국어 지원<br/>
            <strong>적용 모델:</strong> Tesseract OCR, Google Vision API<br/>
            <strong>스펙:</strong> 99% 정확도, 50+ 언어 지원, 실시간 처리<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>PDF OCR 메뉴 접속</FeatureStep>
            <FeatureStep>PDF 또는 이미지 파일 업로드</FeatureStep>
            <FeatureStep>OCR 처리 실행</FeatureStep>
            <FeatureStep>추출된 텍스트 검토 및 수정</FeatureStep>
            <FeatureStep>결과 다운로드 또는 저장</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiEdit3 size={20} />
            텍스트 후처리
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 텍스트 정리, 오타 수정, 포맷팅, 구조화<br/>
            <strong>적용 모델:</strong> NLP Pipeline, Text Processing<br/>
            <strong>스펙:</strong> 자동 정리, 스마트 수정, 구조화된 출력<br/>
            <strong>사용방법:</strong> AI가 추출된 텍스트를 자동으로 정리하고 구조화
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiDownload size={20} />
            결과 내보내기
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 다양한 형식 내보내기, 템플릿 적용, 배치 처리<br/>
            <strong>적용 모델:</strong> Export Engine, Template System<br/>
            <strong>스펙:</strong> PDF, Word, Excel, JSON 형식 지원<br/>
            <strong>사용방법:</strong> 처리된 텍스트를 원하는 형식으로 내보내기
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderGithubTest = () => (
    <Section>
      <SectionTitle>
        <FiGitBranch size={24} />
        GitHub 테스트
      </SectionTitle>
      <FeatureDescription>
        GitHub API를 통한 개발자 프로필 분석 및 테스트 기능입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiGitBranch size={20} />
            GitHub 프로필 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> GitHub API 연동, 레포지토리 분석, 기여도 측정<br/>
            <strong>적용 모델:</strong> GitHub API v4, GraphQL, Repository Analysis<br/>
            <strong>스펙:</strong> 실시간 데이터 수집, 언어별 분석, 활동 패턴 분석<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>GitHub URL 또는 사용자명 입력</FeatureStep>
            <FeatureStep>API를 통한 프로필 데이터 수집</FeatureStep>
            <FeatureStep>레포지토리 및 활동 분석</FeatureStep>
            <FeatureStep>종합 분석 결과 확인</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiCode size={20} />
            코드 품질 분석
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 코드 복잡도, 품질 지표, 기술 스택 분석<br/>
            <strong>적용 모델:</strong> Code Quality Metrics, Complexity Analysis<br/>
            <strong>스펙:</strong> 다중 언어 지원, 실시간 분석, 상세 리포트<br/>
            <strong>사용방법:</strong> GitHub 레포지토리의 코드 품질을 자동으로 분석
          </FeatureDescription>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiTrendingUp size={20} />
            개발 활동 추적
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 커밋 패턴, 기여도, 협업 능력, 성장 추이<br/>
            <strong>적용 모델:</strong> Git Statistics, Contribution Analysis<br/>
            <strong>스펙:</strong> 시계열 분석, 패턴 인식, 예측 모델<br/>
            <strong>사용방법:</strong> 개발자의 활동 패턴과 성장 추이를 시각화
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderPickTalk = () => (
    <Section>
      <SectionTitle>
        <FiMessageCircle size={24} />
        픽톡 (AI 챗봇)
      </SectionTitle>
      <FeatureDescription>
        자연어로 채용공고를 등록하고 채용 관련 질문에 실시간으로 답변하는 AI 챗봇입니다.
      </FeatureDescription>

      <FeatureGrid>
        <FeatureCard>
          <FeatureTitle>
            <FiMessageCircle size={20} />
            자연어 채용공고 등록
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 자연어 입력, 키워드 추출, 폼 자동 입력, 등록간 질문답변, 자동 등록<br/>
            <strong>적용 모델:</strong> OpenAI GPT-4, Claude-3.5-Sonnet, LangGraph<br/>
            <strong>스펙:</strong> 한국어 최적화, 채용 도메인 특화, 실시간 폼 업데이트<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>우측 하단의 픽톡 아이콘 클릭</FeatureStep>
            <FeatureStep>채용공고 등록 요청을 자연어로 입력('샘플 문장' 참고)</FeatureStep>
            <FeatureStep>AI가 키워드를 추출하여 폼에 자동 입력</FeatureStep>
            <FeatureStep>등록 과정에서 추가 질문 및 답변 가능</FeatureStep>
            <FeatureStep>사용자 최종 확인 후 등록요청시 자동 등록</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiBriefcase size={20} />
            샘플 문장
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 다양한 채용공고 등록 요청 예시<br/>
            <strong>적용 모델:</strong> 자연어 처리, 키워드 추출<br/>
            <strong>스펙:</strong> 직무별, 경력별, 기술별 다양한 패턴 지원<br/>
            <strong>사용방법:</strong> 아래 문장들을 참고하여 자연스럽게 요청
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>"백엔드 Node.js 개발자 경력 5년 이상 공고를 등록해줘. 주요 업무, 필수 스킬, 우대사항 포함해서."</FeatureStep>
            <FeatureStep>"AI/머신러닝 엔지니어 공고 작성해줘. TensorFlow·PyTorch 경험과 MLOps 역량 포함해서."</FeatureStep>
            <FeatureStep>"프론트엔드 React 개발자 신입/주니어 공고를 등록해줘. 필요 기술 스택과 성장 기회 포함해서."</FeatureStep>
            <FeatureStep>"풀스택 Java+Vue.js 개발자 경력 4년 이상 채용 공고 만들어줘. 프로젝트 경험 중심으로."</FeatureStep>
            <FeatureStep>"DevOps 엔지니어 공고 작성해줘. AWS·Docker·Kubernetes 필수, IaC 경험 우대 포함해서."</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiMessageSquare size={20} />
            자연어 질의 답변
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 자연어 질문 입력, 실시간 답변, 채용 관련 상담, 도움말 제공<br/>
            <strong>적용 모델:</strong> OpenAI GPT-4, Claude-3.5-Sonnet, LangGraph<br/>
            <strong>스펙:</strong> 한국어 최적화, 채용 도메인 특화, 컨텍스트 이해<br/>
            <strong>사용방법:</strong>
          </FeatureDescription>
          <FeatureSteps>
            <FeatureStep>픽톡 채팅창에 궁금한 내용을 자연어로 입력</FeatureStep>
            <FeatureStep>AI가 질문을 이해하고 관련 정보 분석</FeatureStep>
            <FeatureStep>채용 전문 지식을 바탕으로 상세한 답변 제공</FeatureStep>
            <FeatureStep>추가 질문이나 세부사항 문의 가능</FeatureStep>
            <FeatureStep>대화 기록을 통한 연속적인 상담 진행</FeatureStep>
          </FeatureSteps>
        </FeatureCard>

        <FeatureCard>
          <FeatureTitle>
            <FiSettings size={20} />
            채용 도우미
          </FeatureTitle>
          <FeatureDescription>
            <strong>기능:</strong> 채용공고 작성 도움, 지원자 분석 가이드, 채용 전략 조언<br/>
            <strong>적용 모델:</strong> Domain-specific AI, Knowledge Base<br/>
            <strong>스펙:</strong> 채용 전문 지식, 실무 경험 반영, 실시간 조언<br/>
            <strong>사용방법:</strong> 채용 관련 궁금한 점을 자유롭게 질문하여 전문적인 조언 획득
          </FeatureDescription>
        </FeatureCard>
      </FeatureGrid>
    </Section>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'dashboard':
        return renderDashboard();
      case 'recruitment':
        return renderRecruitment();
      case 'ai-recruitment':
        return renderAIRecruitment();
      case 'applicant-management':
        return renderApplicantManagement();
      case 'resume-management':
        return renderResumeManagement();
      case 'cover-letter-validation':
        return renderCoverLetterValidation();
      case 'talent-recommendation':
        return renderTalentRecommendation();
      case 'similar-talent':
        return renderSimilarTalent();
      case 'plagiarism-check':
        return renderPlagiarismCheck();
      case 'elasticsearch':
        return renderElasticsearch();
      case 'interview-management':
        return renderInterviewManagement();
      case 'user-management':
        return renderUserManagement();
      case 'pdf-ocr':
        return renderPDFOCR();
      case 'github-test':
        return renderGithubTest();
      case 'settings':
        return renderSettings();
      case 'sample-data':
        return renderSampleData();
      case 'company-culture':
        return renderCompanyCulture();
      case 'analysis-weights':
        return renderAnalysisWeights();
      case 'pick-talk':
        return renderPickTalk();
      default:
        return renderOverview();
    }
  };

  return (
    <HelpPageContainer>
      <PageTitle>도움말</PageTitle>
      <PageSubtitle>AI 채용 관리 시스템 사용 가이드</PageSubtitle>

      <TabContainer>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <Tab
              key={tab.id}
              className={activeTab === tab.id ? 'active' : ''}
              onClick={() => setActiveTab(tab.id)}
            >
              <Icon size={16} style={{ marginRight: '8px' }} />
              {tab.name}
            </Tab>
          );
        })}
      </TabContainer>

      <TabContent
        key={activeTab}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {renderTabContent()}
      </TabContent>
    </HelpPageContainer>
  );
};

export default HelpPage;
