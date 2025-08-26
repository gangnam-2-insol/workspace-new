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
      case '서류합격':
      case 'passed':
      case 'reviewed': return 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)';
      case '서류불합격':
      case 'rejected': return 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)';
      case '최종합격':
      case 'approved':
      case 'interview_scheduled': return 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
      case '보류':
      case 'pending':
      case 'reviewing': return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
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
        // 실제 API 호출 시도 - 올바른 엔드포인트 사용
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/applicants/${id}`);

        if (response.ok) {
          const data = await response.json();
          console.log('받은 데이터:', data); // 디버깅용 로그
          setResume(data);
        } else {
          console.error('API 응답 오류:', response.status, response.statusText);
          setResume(null);
        }
        setLoading(false);
      } catch (error) {
        console.error('지원서 상세 정보 로드 실패:', error);
        setResume(null);
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
      case 'pending': return '보류';
      case 'reviewed': return '서류합격';
      case 'reviewing': return '보류';
      case 'approved': return '최종합격';
      case 'rejected': return '서류불합격';
      case 'passed': return '서류합격';
      case 'interview_scheduled': return '최종합격';
      case '서류합격': return '서류합격';
      case '서류불합격': return '서류불합격';
      case '최종합격': return '최종합격';
      case '보류': return '보류';
      default: return '보류';
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
              <InfoValue>{resume.position}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>부서:</InfoLabel>
              <InfoValue>{resume.department}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>경력:</InfoLabel>
              <InfoValue>{resume.experience}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>등록일:</InfoLabel>
              <InfoValue>
                {resume.created_at
                  ? new Date(resume.created_at).toLocaleDateString('ko-KR', {
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit'
                    }).replace(/\. /g, '.').replace(' ', '')
                  : '정보 없음'
                }
              </InfoValue>
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
            {resume.skills ? (
              resume.skills.split(', ').map((skill, index) => (
                <SkillTag key={index}>{skill.trim()}</SkillTag>
              ))
            ) : (
              <span style={{ color: '#7f8c8d' }}>기술 스택 정보가 없습니다.</span>
            )}
          </SkillsContainer>

          <SectionTitle>
            <FaBriefcase />
            분석 결과
          </SectionTitle>
          <ContentText>{resume.analysisResult || '분석 결과가 없습니다.'}</ContentText>

          <SectionTitle>
            <FaStar />
            분석 점수
          </SectionTitle>
          <ContentText>{resume.analysisScore || 0}점</ContentText>

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
                <InfoValue>{resume.email || '이메일 정보 없음'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <FaPhone />
                <InfoValue>{resume.phone || '전화번호 정보 없음'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <FaMapMarkerAlt />
                <InfoValue>{resume.department || '부서 정보 없음'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <FaStar />
                <InfoValue>분석 점수: {resume.analysisScore || 0}점</InfoValue>
              </InfoItem>
              <InfoItem>
                <FaCheckCircle />
                <InfoValue>상태: {resume.status || '대기'}</InfoValue>
              </InfoItem>
            </InfoGrid>
          </ContentSection>

          <ContentSection>
            <SectionTitle>
              <FaGraduationCap />
              성장 배경
            </SectionTitle>
            <ContentText>{resume.growthBackground || '성장 배경 정보가 없습니다.'}</ContentText>
          </ContentSection>

          <ContentSection>
            <SectionTitle>
              <FaEnvelope />
              지원 동기
            </SectionTitle>
            <ContentText>{resume.motivation || '지원 동기 정보가 없습니다.'}</ContentText>
          </ContentSection>

          <ContentSection>
            <SectionTitle>
              <FaBriefcase />
              경력 사항
            </SectionTitle>
            <ContentText>{resume.careerHistory || '경력 사항 정보가 없습니다.'}</ContentText>
          </ContentSection>


        </Card>
      </ContentGrid>
    </Container>
  );
};

export default ResumeDetail;
