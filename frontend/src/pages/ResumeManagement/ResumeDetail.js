import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FaArrowLeft,
  FaFileAlt, 
  FaEnvelope, 
  FaFolder, 
  FaUserTie,
  FaGraduationCap,
  FaBriefcase,
  FaStar,
  FaDownload,
  FaEdit,
  FaTrash,
  FaCheckCircle,
  FaTimesCircle,
  FaClock,
  FaEye,
  FaPhone,
  FaEnvelope as FaEmail,
  FaMapMarkerAlt,
  FaLinkedin,
  FaGithub
} from 'react-icons/fa';

const Container = styled.div`
  padding: 20px;
  background: linear-gradient(135deg, #a8b5e0 0%, #b8a5d0 100%);
  min-height: 100vh;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95);
  padding: 25px;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
`;

const BackButton = styled(motion.button)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
`;

const Title = styled.h1`
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
`;

const CardTitle = styled.h2`
  color: #2c3e50;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background: rgba(236, 240, 241, 0.5);
  border-radius: 12px;
`;

const InfoLabel = styled.span`
  font-weight: 600;
  color: #7f8c8d;
  min-width: 80px;
`;

const InfoValue = styled.span`
  font-weight: 500;
  color: #2c3e50;
`;

const StatusBadge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  background: ${props => {
    switch(props.status) {
      case 'approved': return 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)';
      case 'rejected': return 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)';
      case 'reviewed': return 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
      default: return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
    }
  }};
  color: white;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 15px;
  margin-top: 20px;
`;

const ActionButton = styled(motion.button)`
  background: ${props => {
    switch(props.action) {
      case 'download': return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
      case 'edit': return 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
      case 'delete': return 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)';
      default: return 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)';
    }
  }};
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
`;

const ContentSection = styled.div`
  margin-bottom: 25px;
`;

const SectionTitle = styled.h3`
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ContentText = styled.div`
  background: rgba(236, 240, 241, 0.5);
  padding: 20px;
  border-radius: 12px;
  line-height: 1.6;
  color: #2c3e50;
  white-space: pre-wrap;
`;

const SkillsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
`;

const SkillTag = styled.span`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  color: #7f8c8d;
  font-size: 1.1rem;
`;

const ResumeDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResumeDetail = async () => {
      try {
        // 실제 API 호출 시도
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/applications/${id}`);
        
        if (response.ok) {
          const data = await response.json();
          setResume(data);
        } else {
          // API 호출 실패 시 샘플 데이터 사용
          const sampleResume = {
            id: id,
            name: '김개발',
            title: '프론트엔드 개발자',
            type: 'resume',
            experience: '3년',
            date: '2024-01-15',
            status: 'approved',
            skills: ['React', 'TypeScript', 'Node.js', 'AWS'],
            summary: '3년간의 프론트엔드 개발 경험을 바탕으로 사용자 중심의 웹 애플리케이션을 개발해왔습니다. React와 TypeScript를 주로 사용하며, 최신 웹 기술에 대한 깊은 이해를 가지고 있습니다.',
            contact: {
              email: 'kim.dev@example.com',
              phone: '010-1234-5678',
              address: '서울시 강남구',
              linkedin: 'linkedin.com/in/kimdev',
              github: 'github.com/kimdev'
            },
            education: {
              degree: '컴퓨터공학 학사',
              school: '서울대학교',
              graduation: '2021년'
            },
            experience: [
              {
                company: '테크스타트업',
                position: '프론트엔드 개발자',
                period: '2021-2024',
                description: 'React 기반 웹 애플리케이션 개발 및 유지보수'
              },
              {
                company: 'IT 컨설팅',
                position: '웹 개발자 인턴',
                period: '2020-2021',
                description: 'JavaScript, HTML, CSS를 활용한 웹사이트 개발'
              }
            ],
            projects: [
              {
                name: '이커머스 플랫폼',
                description: 'React와 Node.js를 활용한 온라인 쇼핑몰 개발',
                technologies: ['React', 'Node.js', 'MongoDB']
              },
              {
                name: '관리자 대시보드',
                description: 'TypeScript와 Material-UI를 활용한 관리자 페이지 개발',
                technologies: ['TypeScript', 'Material-UI', 'Redux']
              }
            ]
          };
          setResume(sampleResume);
        }
        setLoading(false);
      } catch (error) {
        console.error('지원서 상세 정보 로드 실패:', error);
        // 에러 발생 시에도 샘플 데이터 사용
        const sampleResume = {
          id: id,
          name: '김개발',
          title: '프론트엔드 개발자',
          type: 'resume',
          experience: '3년',
          date: '2024-01-15',
          status: 'approved',
          skills: ['React', 'TypeScript', 'Node.js', 'AWS'],
          summary: '3년간의 프론트엔드 개발 경험을 바탕으로 사용자 중심의 웹 애플리케이션을 개발해왔습니다. React와 TypeScript를 주로 사용하며, 최신 웹 기술에 대한 깊은 이해를 가지고 있습니다.',
          contact: {
            email: 'kim.dev@example.com',
            phone: '010-1234-5678',
            address: '서울시 강남구',
            linkedin: 'linkedin.com/in/kimdev',
            github: 'github.com/kimdev'
          },
          education: {
            degree: '컴퓨터공학 학사',
            school: '서울대학교',
            graduation: '2021년'
          },
          experience: [
            {
              company: '테크스타트업',
              position: '프론트엔드 개발자',
              period: '2021-2024',
              description: 'React 기반 웹 애플리케이션 개발 및 유지보수'
            },
            {
              company: 'IT 컨설팅',
              position: '웹 개발자 인턴',
              period: '2020-2021',
              description: 'JavaScript, HTML, CSS를 활용한 웹사이트 개발'
            }
          ],
          projects: [
            {
              name: '이커머스 플랫폼',
              description: 'React와 Node.js를 활용한 온라인 쇼핑몰 개발',
              technologies: ['React', 'Node.js', 'MongoDB']
            },
            {
              name: '관리자 대시보드',
              description: 'TypeScript와 Material-UI를 활용한 관리자 페이지 개발',
              technologies: ['TypeScript', 'Material-UI', 'Redux']
            }
          ]
        };
        setResume(sampleResume);
        setLoading(false);
      }
    };

    fetchResumeDetail();
  }, [id]);

  const getTypeIcon = (type) => {
    switch(type) {
      case 'resume': return <FaFileAlt />;
      case 'coverletter': return <FaEnvelope />;
      case 'portfolio': return <FaFolder />;
      default: return <FaFileAlt />;
    }
  };

  const getTypeLabel = (type) => {
    switch(type) {
      case 'resume': return '이력서';
      case 'coverletter': return '자소서';
      case 'portfolio': return '포트폴리오';
      default: return '지원서';
    }
  };

  const getStatusLabel = (status) => {
    switch(status) {
      case 'pending': return '검토 대기';
      case 'reviewed': return '검토 완료';
      case 'approved': return '승인';
      case 'rejected': return '거절';
      default: return '대기';
    }
  };

  if (loading) {
    return (
      <Container>
        <LoadingContainer>
          지원서 정보를 불러오는 중...
        </LoadingContainer>
      </Container>
    );
  }

  if (!resume) {
    return (
      <Container>
        <LoadingContainer>
          지원서를 찾을 수 없습니다.
        </LoadingContainer>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <BackButton
          onClick={() => navigate('/resume')}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <FaArrowLeft />
          목록으로
        </BackButton>
        <Title>
          {getTypeIcon(resume.type)}
          {getTypeLabel(resume.type)} 상세보기
        </Title>
      </Header>

      <ContentGrid>
        <Card
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <CardTitle>
            <FaUserTie />
            기본 정보
          </CardTitle>
          
          <InfoGrid>
            <InfoItem>
              <InfoLabel>이름:</InfoLabel>
              <InfoValue>{resume.name}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>직무:</InfoLabel>
              <InfoValue>{resume.title}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>경력:</InfoLabel>
              <InfoValue>{resume.experience}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>등록일:</InfoLabel>
              <InfoValue>{resume.date}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>상태:</InfoLabel>
              <StatusBadge status={resume.status}>
                {resume.status === 'approved' && <FaCheckCircle />}
                {resume.status === 'rejected' && <FaTimesCircle />}
                {resume.status === 'reviewed' && <FaEye />}
                {resume.status === 'pending' && <FaClock />}
                {getStatusLabel(resume.status)}
              </StatusBadge>
            </InfoItem>
            <InfoItem>
              <InfoLabel>유형:</InfoLabel>
              <InfoValue>{getTypeLabel(resume.type)}</InfoValue>
            </InfoItem>
          </InfoGrid>

          <SectionTitle>
            <FaStar />
            기술 스택
          </SectionTitle>
          <SkillsContainer>
            {Array.isArray(resume.skills) ? resume.skills.map((skill, index) => (
              <SkillTag key={index}>{skill}</SkillTag>
            )) : (
              <span style={{ color: '#7f8c8d' }}>기술 스택 정보가 없습니다.</span>
            )}
          </SkillsContainer>

          <SectionTitle>
            <FaBriefcase />
            자기소개
          </SectionTitle>
          <ContentText>{resume.summary}</ContentText>

          <ActionButtons>
            <ActionButton
              action="download"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <FaDownload />
              다운로드
            </ActionButton>
            <ActionButton
              action="edit"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <FaEdit />
              수정
            </ActionButton>
            <ActionButton
              action="delete"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <FaTrash />
              삭제
            </ActionButton>
          </ActionButtons>
        </Card>

        <Card
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <CardTitle>
            <FaGraduationCap />
            연락처 및 학력
          </CardTitle>

          <ContentSection>
            <SectionTitle>
              <FaEnvelope />
              연락처
            </SectionTitle>
            <InfoGrid>
              <InfoItem>
                <FaEmail />
                <InfoValue>{resume.contact?.email || '이메일 정보 없음'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <FaPhone />
                <InfoValue>{resume.contact?.phone || '전화번호 정보 없음'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <FaMapMarkerAlt />
                <InfoValue>{resume.contact?.address || '주소 정보 없음'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <FaLinkedin />
                <InfoValue>{resume.contact?.linkedin || 'LinkedIn 정보 없음'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <FaGithub />
                <InfoValue>{resume.contact?.github || 'GitHub 정보 없음'}</InfoValue>
              </InfoItem>
            </InfoGrid>
          </ContentSection>

          <ContentSection>
            <SectionTitle>
              <FaGraduationCap />
              학력
            </SectionTitle>
            <InfoGrid>
              <InfoItem>
                <InfoLabel>학위:</InfoLabel>
                <InfoValue>{resume.education?.degree || '학위 정보 없음'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>학교:</InfoLabel>
                <InfoValue>{resume.education?.school || '학교 정보 없음'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>졸업:</InfoLabel>
                <InfoValue>{resume.education?.graduation || '졸업 정보 없음'}</InfoValue>
              </InfoItem>
            </InfoGrid>
          </ContentSection>

          <ContentSection>
            <SectionTitle>
              <FaBriefcase />
              경력 사항
            </SectionTitle>
            {Array.isArray(resume.experience) ? resume.experience.map((exp, index) => (
              <div key={index} style={{ marginBottom: '15px', padding: '15px', background: 'rgba(236, 240, 241, 0.5)', borderRadius: '12px' }}>
                <div style={{ fontWeight: '600', color: '#2c3e50', marginBottom: '5px' }}>
                  {exp.company} - {exp.position}
                </div>
                <div style={{ fontSize: '0.9rem', color: '#7f8c8d', marginBottom: '5px' }}>
                  {exp.period}
                </div>
                <div style={{ fontSize: '0.9rem', color: '#2c3e50' }}>
                  {exp.description}
                </div>
              </div>
            )) : (
              <div style={{ padding: '15px', background: 'rgba(236, 240, 241, 0.5)', borderRadius: '12px', color: '#7f8c8d' }}>
                경력 정보가 없습니다.
              </div>
            )}
          </ContentSection>

          <ContentSection>
            <SectionTitle>
              <FaFolder />
              프로젝트
            </SectionTitle>
            {Array.isArray(resume.projects) ? resume.projects.map((project, index) => (
              <div key={index} style={{ marginBottom: '15px', padding: '15px', background: 'rgba(236, 240, 241, 0.5)', borderRadius: '12px' }}>
                <div style={{ fontWeight: '600', color: '#2c3e50', marginBottom: '5px' }}>
                  {project.name}
                </div>
                <div style={{ fontSize: '0.9rem', color: '#2c3e50', marginBottom: '10px' }}>
                  {project.description}
                </div>
                <SkillsContainer>
                  {Array.isArray(project.technologies) ? project.technologies.map((tech, techIndex) => (
                    <SkillTag key={techIndex}>{tech}</SkillTag>
                  )) : (
                    <span style={{ color: '#7f8c8d' }}>기술 정보가 없습니다.</span>
                  )}
                </SkillsContainer>
              </div>
            )) : (
              <div style={{ padding: '15px', background: 'rgba(236, 240, 241, 0.5)', borderRadius: '12px', color: '#7f8c8d' }}>
                프로젝트 정보가 없습니다.
              </div>
            )}
          </ContentSection>
        </Card>
      </ContentGrid>
    </Container>
  );
};

export default ResumeDetail; 