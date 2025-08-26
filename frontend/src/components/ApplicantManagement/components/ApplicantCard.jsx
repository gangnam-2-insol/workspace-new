import React, { memo, useCallback } from 'react';
import { FiCheck, FiClock, FiX, FiMail, FiPhone, FiCalendar, FiCode, FiBriefcase } from 'react-icons/fi';
import * as S from '../styles';
import { formatDate, getStatusText } from '../utils';
import api from '../services/api';

const ApplicantCard = memo(({ applicant, onClick, selectedJob, onStatusChange }) => {
  const handleStatus = useCallback(async (newStatus) => {
    try {
      await api.updateApplicantStatus(applicant.id, newStatus);
      // 상태 변경 후 상위 컴포넌트에 알림
      if (onStatusChange) {
        onStatusChange(applicant.id, newStatus);
      }
    } catch(e){
      console.error(e);
    }
  }, [applicant.id, onStatusChange]);

  return (
    <S.ApplicantCard onClick={() => onClick(applicant)} whileHover={{scale:1.02}} whileTap={{scale:0.98}}>
      <S.CardHeader>
        <S.ApplicantInfo>
          <S.ApplicantName>{applicant.name}</S.ApplicantName>
          <S.ApplicantPosition>{applicant.position}</S.ApplicantPosition>
        </S.ApplicantInfo>
        <S.StatusBadge status={applicant.status}>{getStatusText(applicant.status)}</S.StatusBadge>
      </S.CardHeader>

      <S.CardContent>
        <S.InfoRow><FiMail /> {applicant.email || '이메일 정보 없음'}</S.InfoRow>
        <S.InfoRow><FiPhone /> {applicant.phone || '전화번호 없음'}</S.InfoRow>
        <S.InfoRow><FiCalendar /> {formatDate(applicant.appliedDate || applicant.created_at)}</S.InfoRow>
        <S.InfoRow><FiCode /> {Array.isArray(applicant.skills) ? applicant.skills.join(', ') : applicant.skills || '기술 정보 없음'}</S.InfoRow>
        {applicant.job_posting_info && (
          <S.InfoRow>
            <FiBriefcase />
            {applicant.job_posting_info.title} ({applicant.job_posting_info.company})
          </S.InfoRow>
        )}
      </S.CardContent>

      <S.CardActions>
        <S.ActionButton
          color="#10b981"
          active={['서류합격','최종합격'].includes(applicant.status)}
          onClick={e=>{e.stopPropagation();handleStatus('서류합격');}}
        >
          <FiCheck /> 합격
        </S.ActionButton>
        <S.ActionButton
          color="#f59e0b"
          active={applicant.status==='보류'}
          onClick={e=>{e.stopPropagation();handleStatus('보류');}}
        >
          <FiClock /> 보류
        </S.ActionButton>
        <S.ActionButton
          color="#ef4444"
          active={applicant.status==='서류불합격'}
          onClick={e=>{e.stopPropagation();handleStatus('서류불합격');}}
        >
          <FiX /> 불합격
        </S.ActionButton>
      </S.CardActions>
    </S.ApplicantCard>
  );
});

export default ApplicantCard;
