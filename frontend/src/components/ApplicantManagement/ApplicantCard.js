import React, { useCallback } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import {
  FiMail,
  FiPhone,
  FiCalendar,
  FiCode,
  FiCheck,
  FiX,
  FiClock
} from 'react-icons/fi';
import CoverLetterSummary from '../CoverLetterSummary';
import { getStatusText } from '../../utils/analysisHelpers';
import { parseSkills, formatSkills } from '../../utils/skillParser';

// 스타일 컴포넌트들 - 순서 중요!
const ApplicantName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
`;

const ApplicantPosition = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
`;

const ApplicantCard = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: visible;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);

    /* hover 시에도 이름과 직무는 기본 색상 유지 */
    ${ApplicantName} {
      color: var(--text-primary);
    }

    ${ApplicantPosition} {
      color: var(--text-secondary);
    }
  }
`;

const TopRankBadge = styled.div`
  position: absolute;
  top: -12px;
  left: -12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  color: white;
  background: ${props => {
    switch (props.rank) {
      case 1: return '#ef4444'; // 빨간색 (1위)
      case 2: return '#f59e0b'; // 주황색 (2위)
      case 3: return '#10b981'; // 초록색 (3위)
      default: return '#666';
    }
  }};
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.3);
  z-index: 10;
  border: 3px solid white;

  &::before {
    content: '${props => {
      switch (props.rank) {
        case 1: return '🥇';
        case 2: return '🥈';
        case 3: return '🥉';
        default: return props.rank.toString();
      }
    }}';
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const ApplicantInfo = styled.div`
  flex: 1;
`;

const StatusBadge = styled.span`
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
  background: ${props => {
    switch (props.status) {
      case '서류합격':
      case '최종합격':
        return '#10b981';
      case '서류불합격':
        return '#ef4444';
      case '보류':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  }};
  color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const CardContent = styled.div`
  margin-bottom: 16px;
`;

const InfoRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text-secondary);

  svg {
    width: 16px;
    height: 16px;
    color: var(--text-tertiary);
  }
`;

const SkillsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
`;

const SkillTag = styled.span`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(102, 126, 234, 0.2);
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
  }
`;

const MoreSkills = styled.span`
  background: #f3f4f6;
  color: #6b7280;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
`;

const PassButton = styled.button`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.active ? '#10b981' : 'var(--gray-light)'};
  color: ${props => props.active ? 'white' : 'var(--text-secondary)'};

  &:hover {
    background: #10b981;
    color: white;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const PendingButton = styled.button`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.active ? '#f59e0b' : 'var(--gray-light)'};
  color: ${props => props.active ? 'white' : 'var(--text-secondary)'};

  &:hover {
    background: #f59e0b;
    color: white;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const RejectButton = styled.button`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.active ? '#ef4444' : 'var(--gray-light)'};
  color: ${props => props.active ? 'white' : 'var(--text-secondary)'};

  &:hover {
    background: #ef4444;
    color: white;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

// 메모이제이션된 지원자 카드 컴포넌트
const MemoizedApplicantCard = React.memo(({
  applicant,
  onCardClick,
  onStatusUpdate,
  rank,
  selectedJobPostingId,
  onStatusChange
}) => {
  // 🔍 디버깅: 렌더링 최적화를 위한 로깅 (개발 모드에서만)
  if (process.env.NODE_ENV === 'development') {
    console.log('🎯 MemoizedApplicantCard 렌더링:', {
      name: applicant?.name,
      id: applicant?.id,
      status: applicant?.status,
      rank,
      timestamp: new Date().toISOString()
    });
  }

  const handleStatusUpdate = useCallback(async (newStatus) => {
    try {
      await onStatusUpdate(applicant.id, newStatus);
      // 상태 변경 후 상위 컴포넌트에 알림
      if (onStatusChange) {
        onStatusChange(applicant.id, newStatus);
      }
    } catch (error) {
      console.error('상태 업데이트 실패:', error);
    }
  }, [applicant.id, onStatusUpdate, onStatusChange]);

  return (
    <ApplicantCard
      onClick={() => onCardClick(applicant)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      status={applicant.status}
    >
      {/* 상위 3명에게만 메달 표시 (채용공고가 선택된 경우에만) */}
      {rank && rank <= 3 && selectedJobPostingId && (
        <TopRankBadge rank={rank} />
      )}

      <CardHeader>
        <ApplicantInfo>
          <ApplicantName>{applicant.name}</ApplicantName>
          <ApplicantPosition>{applicant.position}</ApplicantPosition>
        </ApplicantInfo>
        <StatusBadge status={applicant.status}>
          {getStatusText(applicant.status)}
        </StatusBadge>
      </CardHeader>

      <CardContent>
        <InfoRow>
          <FiMail />
          <span>{applicant.email || '이메일 정보 없음'}</span>
        </InfoRow>
        <InfoRow>
          <FiPhone />
          <span>{applicant.phone || '전화번호 정보 없음'}</span>
        </InfoRow>
        <InfoRow>
          <FiCalendar />
          <span>
            {applicant.appliedDate || applicant.created_at
              ? new Date(applicant.appliedDate || applicant.created_at).toLocaleDateString('ko-KR', {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit'
                }).replace(/\. /g, '.').replace(' ', '')
              : '지원일 정보 없음'
            }
          </span>
        </InfoRow>
        <InfoRow>
          <FiCode />
          <SkillsContainer>
            {(() => {
              const skillData = formatSkills(applicant.skills, 3);
              if (skillData.totalCount === 0) {
                return <span>기술 정보 없음</span>;
              }
              return (
                <>
                  {skillData.displaySkills.map((skill, index) => (
                    <SkillTag key={index}>{skill}</SkillTag>
                  ))}
                  {skillData.remainingCount > 0 && (
                    <MoreSkills>+{skillData.remainingCount}</MoreSkills>
                  )}
                </>
              );
            })()}
          </SkillsContainer>
        </InfoRow>

        {/* 자소서 요약 섹션 */}
        {applicant.cover_letter_analysis && (
          <CoverLetterSummary
            coverLetterData={applicant.cover_letter}
            analysisData={applicant.cover_letter_analysis}
          />
        )}
      </CardContent>

      <CardActions>
        <PassButton
          active={applicant.status === '서류합격' || applicant.status === '최종합격'}
          onClick={(e) => {
            e.stopPropagation();
            handleStatusUpdate('서류합격');
          }}
        >
          <FiCheck />
          합격
        </PassButton>
        <PendingButton
          active={applicant.status === '보류'}
          onClick={(e) => {
            e.stopPropagation();
            handleStatusUpdate('보류');
          }}
        >
          <FiClock />
          보류
        </PendingButton>
        <RejectButton
          active={applicant.status === '서류불합격'}
          onClick={(e) => {
            e.stopPropagation();
            handleStatusUpdate('서류불합격');
          }}
        >
          <FiX />
          불합격
        </RejectButton>
      </CardActions>
    </ApplicantCard>
  );
}, (prevProps, nextProps) => {
  // 🔍 메모이제이션 비교 함수 - 실제로 변경된 props만 감지
  const prevApplicant = prevProps.applicant;
  const nextApplicant = nextProps.applicant;

  // 지원자 정보가 변경되었는지 확인
  if (prevApplicant?.id !== nextApplicant?.id ||
      prevApplicant?.name !== nextApplicant?.name ||
      prevApplicant?.status !== nextApplicant?.status ||
      prevApplicant?.position !== nextApplicant?.position ||
      prevApplicant?.email !== nextApplicant?.email ||
      prevApplicant?.phone !== nextApplicant?.phone ||
      prevApplicant?.skills !== nextApplicant?.skills) {
    return false; // 리렌더링 필요
  }

  // 다른 props 변경 확인
  if (prevProps.rank !== nextProps.rank ||
      prevProps.selectedJobPostingId !== nextProps.selectedJobPostingId) {
    return false; // 리렌더링 필요
  }

  // 함수 참조는 무시 (useCallback으로 최적화됨)
  return true; // 리렌더링 불필요
});

MemoizedApplicantCard.displayName = 'MemoizedApplicantCard';

export default MemoizedApplicantCard;
