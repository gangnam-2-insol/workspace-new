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

// 스타일 컴포넌트들
const ApplicantCard = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
`;

const TopRankBadge = styled.div`
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  color: white;
  background: ${props => {
    switch (props.rank) {
      case 1: return '#FFD700'; // 금
      case 2: return '#C0C0C0'; // 은
      case 3: return '#CD7F32'; // 동
      default: return '#666';
    }
  }};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  z-index: 1;
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
        return 'var(--success-light)';
      case '서류불합격':
        return 'var(--error-light)';
      case '보류':
        return 'var(--warning-light)';
      default:
        return 'var(--gray-light)';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case '서류합격':
      case '최종합격':
        return 'var(--success)';
      case '서류불합격':
        return 'var(--error)';
      case '보류':
        return 'var(--warning)';
      default:
        return 'var(--text-secondary)';
    }
  }};
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

const CardActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
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
  background: ${props => props.active ? props.activeColor : 'var(--gray-light)'};
  color: ${props => props.active ? 'white' : 'var(--text-secondary)'};

  &:hover {
    background: ${props => props.activeColor};
    color: white;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const PassButton = styled(ActionButton)`
  activeColor: var(--success);
`;

const PendingButton = styled(ActionButton)`
  activeColor: var(--warning);
`;

const RejectButton = styled(ActionButton)`
  activeColor: var(--error);
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
  // 디버깅을 위한 로깅
  console.log('🎯 MemoizedApplicantCard 렌더링:', {
    name: applicant?.name,
    email: applicant?.email,
    phone: applicant?.phone,
    id: applicant?.id,
    allFields: Object.keys(applicant || {}),
    fullData: applicant
  });

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
          <span>
            {Array.isArray(applicant.skills)
              ? applicant.skills.join(', ')
              : applicant.skills || '기술 정보 없음'
            }
          </span>
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
});

MemoizedApplicantCard.displayName = 'MemoizedApplicantCard';

export default MemoizedApplicantCard;
