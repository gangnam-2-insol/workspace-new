import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  FaArrowLeft,
  FaUser,
  FaCode,
  FaLink,
  FaStar,
  FaEye,
  FaDownload,
  FaGithub,
  FaExternalLinkAlt,
  FaCalendar,
  FaTag
} from 'react-icons/fa';

const DetailContainer = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
`;

const BackButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  transition: var(--transition);
  font-weight: 500;

  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
  }
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
`;

const MainSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Section = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-light);
  border: 1px solid var(--border-color);
`;

const SectionTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const InfoItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const InfoLabel = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
`;

const InfoValue = styled.div`
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 600;
`;

const ScoreSection = styled.div`
  display: flex;
  gap: 16px;
  margin-top: 16px;
`;

const ScoreItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  flex: 1;
`;

const ScoreValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: ${props => {
    if (props.score >= 90) return '#27ae60';
    if (props.score >= 80) return '#3498db';
    if (props.score >= 70) return '#f39c12';
    return '#e74c3c';
  }};
`;

const ScoreLabel = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
`;

const ProjectSection = styled.div`
  margin-top: 16px;
`;

const ProjectItem = styled.div`
  background: var(--background-secondary);
  padding: 20px;
  border-radius: var(--border-radius);
  margin-bottom: 16px;
`;

const ProjectHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const ProjectTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const ProjectPeriod = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
`;

const ProjectDescription = styled.div`
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
`;

const ProjectTech = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
`;

const TechTag = styled.span`
  padding: 4px 8px;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
`;

const ProjectLinks = styled.div`
  display: flex;
  gap: 8px;
`;

const LinkButton = styled.a`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  text-decoration: none;
  font-size: 11px;
  color: var(--text-primary);
  transition: var(--transition);

  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
  }
`;

const SideSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const ActionButton = styled.button`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  font-size: 14px;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
  }

  &.primary {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
  }
`;

const SkillsSection = styled.div`
  margin-top: 16px;
`;

const SkillsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
`;

const SkillItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  text-align: center;
`;

const SkillName = styled.div`
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const SkillLevel = styled.div`
  font-size: 10px;
  color: var(--text-secondary);
`;

// 샘플 포트폴리오 데이터
const samplePortfolio = {
  id: 'portfolio_001',
  candidateName: '김철수',
  position: '프론트엔드 개발자',
  title: 'React 기반 웹 애플리케이션 포트폴리오',
  description: '사용자 중심의 웹 애플리케이션 개발 경험을 담은 포트폴리오입니다. React 생태계를 활용한 다양한 프로젝트들을 포함하고 있습니다.',
  createdAt: '2024-01-15',
  updatedAt: '2024-01-15',
  overallScore: 92,
  designScore: 88,
  functionalityScore: 95,
  codeQualityScore: 90,
  projects: [
    {
      id: 1,
      title: 'E-Commerce 플랫폼',
      period: '2023.06 - 2023.12',
      description: 'React와 TypeScript를 활용한 전자상거래 플랫폼입니다. Redux를 통한 상태 관리와 Stripe 결제 시스템을 구현했습니다.',
      technologies: ['React', 'TypeScript', 'Redux', 'Stripe', 'Node.js'],
      githubUrl: 'https://github.com/example/ecommerce',
      liveUrl: 'https://ecommerce-demo.com',
      imageUrl: 'https://via.placeholder.com/300x200'
    },
    {
      id: 2,
      title: '실시간 채팅 애플리케이션',
      period: '2023.03 - 2023.05',
      description: 'Socket.io를 활용한 실시간 채팅 애플리케이션입니다. 사용자 인증과 메시지 암호화 기능을 포함합니다.',
      technologies: ['React', 'Socket.io', 'Express', 'MongoDB', 'JWT'],
      githubUrl: 'https://github.com/example/chat-app',
      liveUrl: 'https://chat-demo.com',
      imageUrl: 'https://via.placeholder.com/300x200'
    },
    {
      id: 3,
      title: '대시보드 관리 시스템',
      period: '2023.01 - 2023.02',
      description: 'Chart.js와 D3.js를 활용한 데이터 시각화 대시보드입니다. 실시간 데이터 업데이트와 반응형 디자인을 구현했습니다.',
      technologies: ['React', 'Chart.js', 'D3.js', 'REST API', 'CSS3'],
      githubUrl: 'https://github.com/example/dashboard',
      liveUrl: 'https://dashboard-demo.com',
      imageUrl: 'https://via.placeholder.com/300x200'
    }
  ],
  skills: [
    { name: 'React', level: 'Expert' },
    { name: 'TypeScript', level: 'Advanced' },
    { name: 'JavaScript', level: 'Expert' },
    { name: 'Node.js', level: 'Intermediate' },
    { name: 'Redux', level: 'Advanced' },
    { name: 'CSS3', level: 'Expert' },
    { name: 'Git', level: 'Advanced' },
    { name: 'Docker', level: 'Intermediate' }
  ],
  githubUrl: 'https://github.com/example',
  linkedinUrl: 'https://linkedin.com/in/example',
  personalWebsite: 'https://example.com'
};

const PortfolioDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPortfolioDetail = async () => {
      try {
        // 실제 API 호출 시도
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/portfolios/${id}`);

        if (response.ok) {
          const data = await response.json();
          setPortfolio(data);
        } else {
          // API 호출 실패 시 샘플 데이터 사용
          setPortfolio(samplePortfolio);
        }
        setLoading(false);
      } catch (error) {
        console.error('포트폴리오 상세 정보 로드 실패:', error);
        // 에러 발생 시에도 샘플 데이터 사용
        setPortfolio(samplePortfolio);
        setLoading(false);
      }
    };

    fetchPortfolioDetail();
  }, [id]);

  if (loading) {
    return (
      <DetailContainer>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          로딩 중...
        </div>
      </DetailContainer>
    );
  }

  if (!portfolio) {
    return (
      <DetailContainer>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          포트폴리오 정보를 찾을 수 없습니다.
        </div>
      </DetailContainer>
    );
  }

  return (
    <DetailContainer>
      <Header>
        <BackButton onClick={() => navigate(-1)}>
          <FaArrowLeft />
          뒤로가기
        </BackButton>
        <Title>{portfolio.candidateName} 포트폴리오</Title>
      </Header>

      <ContentGrid>
        <MainSection>
          {/* 기본 정보 */}
          <Section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <SectionTitle>
              <FaUser />
              기본 정보
            </SectionTitle>
            <InfoGrid>
              <InfoItem>
                <InfoLabel>지원자</InfoLabel>
                <InfoValue>{portfolio.candidateName}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>지원 직무</InfoLabel>
                <InfoValue>{portfolio.position}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>포트폴리오 제목</InfoLabel>
                <InfoValue>{portfolio.title}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>생성일</InfoLabel>
                <InfoValue>{portfolio.createdAt}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>최종 수정일</InfoLabel>
                <InfoValue>{portfolio.updatedAt}</InfoValue>
              </InfoItem>
            </InfoGrid>

            <div style={{ marginTop: '16px', padding: '16px', background: 'var(--background-secondary)', borderRadius: 'var(--border-radius)' }}>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                {portfolio.description}
              </div>
            </div>
          </Section>

          {/* 평가 점수 */}
          <Section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <SectionTitle>
              <FaStar />
              평가 점수
            </SectionTitle>
            <ScoreSection>
              <ScoreItem>
                <ScoreValue score={portfolio.overallScore}>{portfolio.overallScore}</ScoreValue>
                <ScoreLabel>종합 점수</ScoreLabel>
              </ScoreItem>
              <ScoreItem>
                <ScoreValue score={portfolio.designScore}>{portfolio.designScore}</ScoreValue>
                <ScoreLabel>디자인</ScoreLabel>
              </ScoreItem>
              <ScoreItem>
                <ScoreValue score={portfolio.functionalityScore}>{portfolio.functionalityScore}</ScoreValue>
                <ScoreLabel>기능성</ScoreLabel>
              </ScoreItem>
              <ScoreItem>
                <ScoreValue score={portfolio.codeQualityScore}>{portfolio.codeQualityScore}</ScoreValue>
                <ScoreLabel>코드 품질</ScoreLabel>
              </ScoreItem>
            </ScoreSection>
          </Section>

          {/* 프로젝트 */}
          <Section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <SectionTitle>
              <FaCode />
              프로젝트
            </SectionTitle>
            <ProjectSection>
              {portfolio.projects.map((project, index) => (
                <ProjectItem key={project.id}>
                  <ProjectHeader>
                    <div>
                      <ProjectTitle>{project.title}</ProjectTitle>
                      <ProjectPeriod>{project.period}</ProjectPeriod>
                    </div>
                  </ProjectHeader>
                  <ProjectDescription>{project.description}</ProjectDescription>
                  <ProjectTech>
                    {project.technologies.map((tech, techIndex) => (
                      <TechTag key={techIndex}>{tech}</TechTag>
                    ))}
                  </ProjectTech>
                  <ProjectLinks>
                    <LinkButton href={project.githubUrl} target="_blank" rel="noopener noreferrer">
                      <FaGithub />
                      GitHub
                    </LinkButton>
                    <LinkButton href={project.liveUrl} target="_blank" rel="noopener noreferrer">
                      <FaExternalLinkAlt />
                      Live Demo
                    </LinkButton>
                  </ProjectLinks>
                </ProjectItem>
              ))}
            </ProjectSection>
          </Section>

          {/* 기술 스택 */}
          <Section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <SectionTitle>
              <FaTag />
              기술 스택
            </SectionTitle>
            <SkillsSection>
              <SkillsGrid>
                {portfolio.skills.map((skill, index) => (
                  <SkillItem key={index}>
                    <SkillName>{skill.name}</SkillName>
                    <SkillLevel>{skill.level}</SkillLevel>
                  </SkillItem>
                ))}
              </SkillsGrid>
            </SkillsSection>
          </Section>
        </MainSection>

        <SideSection>
          {/* 액션 버튼들 */}
          <Section
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <SectionTitle>액션</SectionTitle>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <ActionButton className="primary">
                <FaEye />
                포트폴리오 보기
              </ActionButton>
              <ActionButton>
                <FaDownload />
                포트폴리오 다운로드
              </ActionButton>
              <ActionButton>
                <FaGithub />
                GitHub 프로필
              </ActionButton>
              <ActionButton>
                <FaUser />
                지원자 프로필
              </ActionButton>
            </div>
          </Section>

          {/* 링크 */}
          <Section
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <SectionTitle>링크</SectionTitle>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {portfolio.githubUrl && (
                <LinkButton href={portfolio.githubUrl} target="_blank" rel="noopener noreferrer">
                  <FaGithub />
                  GitHub
                </LinkButton>
              )}
              {portfolio.linkedinUrl && (
                <LinkButton href={portfolio.linkedinUrl} target="_blank" rel="noopener noreferrer">
                  LinkedIn
                </LinkButton>
              )}
              {portfolio.personalWebsite && (
                <LinkButton href={portfolio.personalWebsite} target="_blank" rel="noopener noreferrer">
                  <FaExternalLinkAlt />
                  개인 웹사이트
                </LinkButton>
              )}
            </div>
          </Section>
        </SideSection>
      </ContentGrid>
    </DetailContainer>
  );
};

export default PortfolioDetail;
