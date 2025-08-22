import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FiCode, 
  FiGitBranch, 
  FiStar, 
  FiEye, 
  FiDownload,
  FiGithub,
  FiExternalLink,
  FiCheckCircle,
  FiAlertCircle
} from 'react-icons/fi';
import DetailModal, {
  DetailSection,
  SectionTitle,
  DetailGrid,
  DetailItem,
  DetailLabel,
  DetailValue,
  DetailText
} from '../../components/DetailModal/DetailModal';

const PortfolioContainer = styled.div`
  padding: 24px 0;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled.button`
  padding: 12px 24px;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  
  &.primary {
    background: var(--primary-color);
    color: white;
  }
  
  &.secondary {
    background: white;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
  }
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-light);
  }
`;

const PortfolioGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
`;

const PortfolioCard = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
  border: 1px solid var(--border-color);
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-medium);
  }
`;

const PortfolioHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const ProjectInfo = styled.div`
  flex: 1;
`;

const ProjectName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const ProjectDescription = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
`;

const ScoreBadge = styled.span`
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => {
    if (props.score >= 90) return '#d4edda';
    if (props.score >= 80) return '#d1ecf1';
    if (props.score >= 70) return '#fff3cd';
    return '#f8d7da';
  }};
  color: ${props => {
    if (props.score >= 90) return '#155724';
    if (props.score >= 80) return '#0c5460';
    if (props.score >= 70) return '#856404';
    return '#721c24';
  }};
`;

const PortfolioDetails = styled.div`
  margin-bottom: 16px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
`;

// DetailLabel and DetailValue are imported from DetailModal

const AnalysisResult = styled.div`
  margin-top: 16px;
  padding: 16px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
`;

const AnalysisTitle = styled.div`
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const AnalysisScore = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
`;

const ScoreBar = styled.div`
  flex: 1;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
`;

const ScoreFill = styled.div`
  height: 100%;
  background: var(--primary-color);
  width: ${props => props.score}%;
  transition: width 0.3s ease;
`;

const ScoreText = styled.span`
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 30px;
`;

const PortfolioActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`;

const ActionButton = styled.button`
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
  }
`;

const CodeMetrics = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 12px;
`;

const MetricItem = styled.div`
  text-align: center;
  padding: 8px;
  background: white;
  border-radius: var(--border-radius);
`;

const MetricValue = styled.div`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
`;

const MetricLabel = styled.div`
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 2px;
`;

// 샘플 데이터
const portfolios = [
  {
    id: 1,
    name: 'E-Commerce Platform',
    description: 'React와 Node.js를 활용한 온라인 쇼핑몰',
    githubUrl: 'https://github.com/user/ecommerce',
    liveUrl: 'https://ecommerce-demo.com',
    language: 'JavaScript',
    framework: 'React',
    stars: 45,
    forks: 12,
    commits: 234,
    lastCommit: '2024-01-15',
    analysisScore: 92,
    codeQuality: 95,
    documentation: 88,
    performance: 90,
    analysis: '코드 품질이 우수하고, 문서화가 잘 되어 있습니다. 성능 최적화도 잘 되어 있습니다.',
    issues: 3,
    pullRequests: 8,
    contributors: 5
  },
  {
    id: 2,
    name: 'Task Management App',
    description: 'Vue.js와 Firebase를 활용한 프로젝트 관리 도구',
    githubUrl: 'https://github.com/user/task-manager',
    liveUrl: 'https://task-manager-demo.com',
    language: 'JavaScript',
    framework: 'Vue.js',
    stars: 32,
    forks: 8,
    commits: 156,
    lastCommit: '2024-01-14',
    analysisScore: 85,
    codeQuality: 88,
    documentation: 82,
    performance: 87,
    analysis: '기능 구현이 잘 되어 있으나, 일부 성능 최적화가 필요합니다.',
    issues: 5,
    pullRequests: 12,
    contributors: 3
  },
  {
    id: 3,
    name: 'Data Visualization Dashboard',
    description: 'D3.js를 활용한 데이터 시각화 대시보드',
    githubUrl: 'https://github.com/user/data-viz',
    liveUrl: 'https://data-viz-demo.com',
    language: 'TypeScript',
    framework: 'React',
    stars: 67,
    forks: 23,
    commits: 412,
    lastCommit: '2024-01-13',
    analysisScore: 78,
    codeQuality: 82,
    documentation: 75,
    performance: 80,
    analysis: '시각화 기능이 뛰어나지만, 코드 구조 개선이 필요합니다.',
    issues: 8,
    pullRequests: 15,
    contributors: 7
  }
];

const PortfolioAnalysis = () => {
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  return (
    <PortfolioContainer>
      <Header>
        <Title>포트폴리오 분석</Title>
        <ActionButtons>
          <Button className="secondary">
            <FiGithub />
            GitHub 연동
          </Button>
          <Button className="primary">
            <FiCode />
            새 프로젝트 분석
          </Button>
        </ActionButtons>
      </Header>

      <PortfolioGrid>
        {portfolios.map((portfolio, index) => (
          <PortfolioCard
            key={portfolio.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <PortfolioHeader>
              <ProjectInfo>
                <ProjectName>{portfolio.name}</ProjectName>
                <ProjectDescription>{portfolio.description}</ProjectDescription>
              </ProjectInfo>
              <ScoreBadge score={portfolio.analysisScore}>
                {portfolio.analysisScore}점
              </ScoreBadge>
            </PortfolioHeader>

            <PortfolioDetails>
              <DetailRow>
                <DetailLabel>언어:</DetailLabel>
                <DetailValue>{portfolio.language}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>프레임워크:</DetailLabel>
                <DetailValue>{portfolio.framework}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Stars:</DetailLabel>
                <DetailValue>{portfolio.stars}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Forks:</DetailLabel>
                <DetailValue>{portfolio.forks}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>최근 커밋:</DetailLabel>
                <DetailValue>{portfolio.lastCommit}</DetailValue>
              </DetailRow>
            </PortfolioDetails>

            <AnalysisResult>
              <AnalysisTitle>
                <FiCheckCircle />
                AI 코드 분석
              </AnalysisTitle>
              <AnalysisScore>
                <ScoreText>종합 점수</ScoreText>
                <ScoreBar>
                  <ScoreFill score={portfolio.analysisScore} />
                </ScoreBar>
                <ScoreText>{portfolio.analysisScore}%</ScoreText>
              </AnalysisScore>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                {portfolio.analysis}
              </div>
              
              <CodeMetrics>
                <MetricItem>
                  <MetricValue>{portfolio.codeQuality}%</MetricValue>
                  <MetricLabel>코드 품질</MetricLabel>
                </MetricItem>
                <MetricItem>
                  <MetricValue>{portfolio.documentation}%</MetricValue>
                  <MetricLabel>문서화</MetricLabel>
                </MetricItem>
                <MetricItem>
                  <MetricValue>{portfolio.performance}%</MetricValue>
                  <MetricLabel>성능</MetricLabel>
                </MetricItem>
              </CodeMetrics>
            </AnalysisResult>

            <PortfolioActions>
              <ActionButton>
                <FiGithub />
                GitHub
              </ActionButton>
              <ActionButton>
                <FiExternalLink />
                Live Demo
              </ActionButton>
              <ActionButton onClick={() => {
                setSelectedPortfolio(portfolio);
                setIsDetailModalOpen(true);
              }}>
                <FiEye />
                상세보기
              </ActionButton>
              <ActionButton>
                <FiDownload />
                리포트
              </ActionButton>
            </PortfolioActions>
          </PortfolioCard>
        ))}
      </PortfolioGrid>

      {/* 포트폴리오 상세보기 모달 */}
      <DetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedPortfolio(null);
        }}
        title={selectedPortfolio ? `${selectedPortfolio.name} 포트폴리오 상세` : ''}
        onEdit={() => {
          // 수정 기능 구현
          console.log('포트폴리오 수정:', selectedPortfolio);
        }}
        onDelete={() => {
          // 삭제 기능 구현
          console.log('포트폴리오 삭제:', selectedPortfolio);
        }}
      >
        {selectedPortfolio && (
          <>
            <DetailSection>
              <SectionTitle>프로젝트 정보</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>프로젝트명</DetailLabel>
                  <DetailValue>{selectedPortfolio.name}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>설명</DetailLabel>
                  <DetailValue>{selectedPortfolio.description}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>언어</DetailLabel>
                  <DetailValue>{selectedPortfolio.language}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>프레임워크</DetailLabel>
                  <DetailValue>{selectedPortfolio.framework}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Stars</DetailLabel>
                  <DetailValue>{selectedPortfolio.stars}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Forks</DetailLabel>
                  <DetailValue>{selectedPortfolio.forks}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>최근 커밋</DetailLabel>
                  <DetailValue>{selectedPortfolio.lastCommit}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>분석 점수</DetailLabel>
                  <DetailValue>{selectedPortfolio.analysisScore}점</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>AI 코드 분석</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>종합 점수</DetailLabel>
                  <DetailValue>{selectedPortfolio.analysisScore}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>분석 결과</DetailLabel>
                  <DetailValue>{selectedPortfolio.analysis}</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>코드 메트릭</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>코드 품질</DetailLabel>
                  <DetailValue>{selectedPortfolio.codeQuality}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>문서화</DetailLabel>
                  <DetailValue>{selectedPortfolio.documentation}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>성능</DetailLabel>
                  <DetailValue>{selectedPortfolio.performance}%</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>GitHub 통계</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>Issues</DetailLabel>
                  <DetailValue>{selectedPortfolio.issues}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Pull Requests</DetailLabel>
                  <DetailValue>{selectedPortfolio.pullRequests}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Contributors</DetailLabel>
                  <DetailValue>{selectedPortfolio.contributors}</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>
          </>
        )}
      </DetailModal>
    </PortfolioContainer>
  );
};

export default PortfolioAnalysis; 