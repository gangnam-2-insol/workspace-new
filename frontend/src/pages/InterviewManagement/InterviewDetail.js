import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  FaArrowLeft,
  FaUser,
  FaCalendar,
  FaClock,
  FaMapMarkerAlt,
  FaStar,
  FaComments,
  FaFileAlt,
  FaCheckCircle,
  FaTimesCircle,
  FaExclamationTriangle
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

const StatusBadge = styled.span`
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => {
    if (props.status === 'completed') return '#d4edda';
    if (props.status === 'scheduled') return '#d1ecf1';
    if (props.status === 'cancelled') return '#f8d7da';
    return '#fff3cd';
  }};
  color: ${props => {
    if (props.status === 'completed') return '#155724';
    if (props.status === 'scheduled') return '#0c5460';
    if (props.status === 'cancelled') return '#721c24';
    return '#856404';
  }};
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

const EvaluationSection = styled.div`
  margin-top: 16px;
`;

const EvaluationItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
  
  &:last-child {
    border-bottom: none;
  }
`;

const EvaluationLabel = styled.div`
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
`;

const EvaluationScore = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const StarRating = styled.div`
  display: flex;
  gap: 2px;
`;

const Star = styled.span`
  color: ${props => props.filled ? '#f39c12' : '#e5e7eb'};
  font-size: 14px;
`;

const NotesSection = styled.div`
  margin-top: 16px;
`;

const NoteItem = styled.div`
  background: var(--background-secondary);
  padding: 16px;
  border-radius: var(--border-radius);
  margin-bottom: 12px;
`;

const NoteHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const NoteAuthor = styled.div`
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
`;

const NoteTime = styled.div`
  font-size: 11px;
  color: var(--text-secondary);
`;

const NoteContent = styled.div`
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
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

// 샘플 면접 데이터
const sampleInterview = {
  id: 'interview_001',
  candidateName: '김철수',
  position: '프론트엔드 개발자',
  date: '2024-01-15',
  time: '14:00',
  duration: '60분',
  location: '서울 강남구',
  status: 'completed',
  interviewer: '이영희 (개발팀장)',
  resumeScore: 95,
  technicalScore: 88,
  communicationScore: 92,
  cultureScore: 85,
  overallScore: 90,
  evaluations: [
    { category: '기술적 이해도', score: 88 },
    { category: '문제 해결 능력', score: 92 },
    { category: '의사소통 능력', score: 90 },
    { category: '팀워크', score: 85 },
    { category: '학습 의지', score: 94 }
  ],
  notes: [
    {
      author: '이영희',
      time: '2024-01-15 15:30',
      content: 'React 생태계에 대한 깊은 이해를 보여주었습니다. 특히 상태 관리와 성능 최적화에 대한 지식이 뛰어납니다.'
    },
    {
      author: '박민수',
      time: '2024-01-15 15:45',
      content: '코딩 테스트에서 알고리즘 문제를 효율적으로 해결했습니다. 코드 품질도 우수합니다.'
    },
    {
      author: '이영희',
      time: '2024-01-15 16:00',
      content: '프로젝트 경험을 바탕으로 한 구체적인 사례 설명이 인상적이었습니다. 팀 프로젝트에서의 역할도 명확했습니다.'
    }
  ],
  strengths: [
    'React 생태계에 대한 깊은 이해',
    '성능 최적화 경험',
    '명확한 의사소통',
    '지속적인 학습 의지'
  ],
  weaknesses: [
    '백엔드 지식 부족',
    '대규모 프로젝트 경험 부족'
  ],
  recommendation: '우수한 기술력과 학습 의지를 보유하고 있어 적합한 인재로 판단됩니다. 추가적인 백엔드 지식 습득을 권장합니다.'
};

const InterviewDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [interview, setInterview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInterviewDetail = async () => {
      try {
        console.log('=== 면접 상세 정보 로드 시작 ===');
        console.log('요청할 면접 ID:', id);
        
        // 실제 API 호출 시도
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/interviews/${id}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log('백엔드에서 받은 면접 데이터:', data);
          
          // 백엔드 데이터를 프론트엔드 형식으로 변환
          const transformedInterview = {
            id: data.id || data._id,
            candidateName: data.company || data.candidateName || '지원자',
            position: data.position,
            date: data.date ? (typeof data.date === 'string' ? data.date.split('T')[0] : data.date.toISOString().split('T')[0]) : '2024-01-15',
            time: data.date ? new Date(data.date).toLocaleTimeString('ko-KR', { 
              hour: '2-digit', 
              minute: '2-digit' 
            }) : '14:00',
            duration: '60분',
            location: data.location || '회의실',
            status: data.status || 'scheduled',
            interviewer: data.hrManager || '면접관',
            resumeScore: 95,
            technicalScore: 88,
            communicationScore: 92,
            cultureScore: 85,
            overallScore: 90,
            evaluations: [
              { category: '기술적 이해도', score: 88 },
              { category: '문제 해결 능력', score: 92 },
              { category: '의사소통 능력', score: 90 },
              { category: '팀워크', score: 85 },
              { category: '학습 의지', score: 94 }
            ],
            notes: [
              {
                author: data.hrManager || '면접관',
                time: `${data.date ? data.date.split('T')[0] : '2024-01-15'} 15:30`,
                content: data.notes || '면접 진행 중 특이사항이 기록됩니다.'
              }
            ],
            strengths: [
              '기술적 이해도가 뛰어남',
              '명확한 의사소통',
              '지속적인 학습 의지'
            ],
            weaknesses: [
              '추가 경험 필요',
              '개선 가능한 영역'
            ],
            recommendation: '전반적으로 우수한 지원자입니다. 추가 면접을 통해 더 자세히 평가할 수 있습니다.'
          };
          
          console.log('변환된 면접 데이터:', transformedInterview);
          setInterview(transformedInterview);
        } else {
          console.log('API 호출 실패, 샘플 데이터 사용');
          setInterview(sampleInterview);
        }
        setLoading(false);
      } catch (error) {
        console.error('면접 상세 정보 로드 실패:', error);
        // 에러 발생 시에도 샘플 데이터 사용
        setInterview(sampleInterview);
        setLoading(false);
      }
    };

    fetchInterviewDetail();
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

  if (!interview) {
    return (
      <DetailContainer>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          면접 정보를 찾을 수 없습니다.
        </div>
      </DetailContainer>
    );
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return '완료';
      case 'scheduled': return '예정';
      case 'cancelled': return '취소';
      default: return '미정';
    }
  };

  const renderStars = (score) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <Star key={i} filled={i <= score / 20}>
          ★
        </Star>
      );
    }
    return <StarRating>{stars}</StarRating>;
  };

  return (
    <DetailContainer>
      <Header>
        <BackButton onClick={() => navigate('/interview')}>
          <FaArrowLeft />
          면접 일정관리로 돌아가기
        </BackButton>
        <Title>{interview.candidateName} 면접 상세</Title>
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
                <InfoValue>{interview.candidateName}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>지원 직무</InfoLabel>
                <InfoValue>{interview.position}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>면접관</InfoLabel>
                <InfoValue>{interview.interviewer}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>상태</InfoLabel>
                <InfoValue>
                  <StatusBadge status={interview.status}>
                    {getStatusText(interview.status)}
                  </StatusBadge>
                </InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>면접 일시</InfoLabel>
                <InfoValue>{interview.date} {interview.time}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>소요 시간</InfoLabel>
                <InfoValue>{interview.duration}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>면접 장소</InfoLabel>
                <InfoValue>{interview.location}</InfoValue>
              </InfoItem>
            </InfoGrid>
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
                <ScoreValue score={interview.resumeScore}>{interview.resumeScore}</ScoreValue>
                <ScoreLabel>이력서 점수</ScoreLabel>
              </ScoreItem>
              <ScoreItem>
                <ScoreValue score={interview.technicalScore}>{interview.technicalScore}</ScoreValue>
                <ScoreLabel>기술 점수</ScoreLabel>
              </ScoreItem>
              <ScoreItem>
                <ScoreValue score={interview.communicationScore}>{interview.communicationScore}</ScoreValue>
                <ScoreLabel>의사소통</ScoreLabel>
              </ScoreItem>
              <ScoreItem>
                <ScoreValue score={interview.cultureScore}>{interview.cultureScore}</ScoreValue>
                <ScoreLabel>문화 적합성</ScoreLabel>
              </ScoreItem>
              <ScoreItem>
                <ScoreValue score={interview.overallScore}>{interview.overallScore}</ScoreValue>
                <ScoreLabel>종합 점수</ScoreLabel>
              </ScoreItem>
            </ScoreSection>

            <EvaluationSection>
              {interview.evaluations.map((evaluation, index) => (
                <EvaluationItem key={index}>
                  <EvaluationLabel>{evaluation.category}</EvaluationLabel>
                  <EvaluationScore>
                    {renderStars(evaluation.score)}
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {evaluation.score}점
                    </span>
                  </EvaluationScore>
                </EvaluationItem>
              ))}
            </EvaluationSection>
          </Section>

          {/* 면접 노트 */}
          <Section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <SectionTitle>
              <FaComments />
              면접 노트
            </SectionTitle>
            <NotesSection>
              {interview.notes.map((note, index) => (
                <NoteItem key={index}>
                  <NoteHeader>
                    <NoteAuthor>{note.author}</NoteAuthor>
                    <NoteTime>{note.time}</NoteTime>
                  </NoteHeader>
                  <NoteContent>{note.content}</NoteContent>
                </NoteItem>
              ))}
            </NotesSection>
          </Section>

          {/* 평가 요약 */}
          <Section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <SectionTitle>
              <FaFileAlt />
              평가 요약
            </SectionTitle>
            
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>
                <FaCheckCircle style={{ color: '#27ae60', marginRight: '8px' }} />
                강점
              </div>
              <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-secondary)' }}>
                {interview.strengths.map((strength, index) => (
                  <li key={index} style={{ marginBottom: '4px' }}>{strength}</li>
                ))}
              </ul>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>
                <FaExclamationTriangle style={{ color: '#f39c12', marginRight: '8px' }} />
                개선점
              </div>
              <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-secondary)' }}>
                {interview.weaknesses.map((weakness, index) => (
                  <li key={index} style={{ marginBottom: '4px' }}>{weakness}</li>
                ))}
              </ul>
            </div>

            <div>
              <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>
                <FaStar style={{ color: '#f39c12', marginRight: '8px' }} />
                추천 의견
              </div>
              <div style={{ color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                {interview.recommendation}
              </div>
            </div>
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
              <ActionButton 
                className="primary"
                onClick={() => {
                  // 지원자 프로필 보기 기능 (향후 구현)
                  alert('지원자 프로필 보기 기능은 향후 구현 예정입니다.');
                }}
              >
                <FaUser />
                지원자 프로필 보기
              </ActionButton>
              <ActionButton
                onClick={() => {
                  // 이력서 상세보기 기능 (향후 구현)
                  alert('이력서 상세보기 기능은 향후 구현 예정입니다.');
                }}
              >
                <FaFileAlt />
                이력서 상세보기
              </ActionButton>
              <ActionButton
                onClick={() => {
                  // 면접 노트 편집 기능 (향후 구현)
                  alert('면접 노트 편집 기능은 향후 구현 예정입니다.');
                }}
              >
                <FaComments />
                면접 노트 편집
              </ActionButton>
              <ActionButton
                onClick={() => {
                  // 평가 수정 기능 (향후 구현)
                  alert('평가 수정 기능은 향후 구현 예정입니다.');
                }}
              >
                <FaStar />
                평가 수정
              </ActionButton>
            </div>
          </Section>
        </SideSection>
      </ContentGrid>
    </DetailContainer>
  );
};

export default InterviewDetail; 