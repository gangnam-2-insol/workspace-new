import React from 'react';
import { FiMail, FiPhone } from 'react-icons/fi';
import * as S from '../styles';
import { formatDate, getStatusText } from '../utils';

const ApplicantBoard = ({ applicant, onClick, selected, onSelectToggle, selectedJob }) => {
  return (
    <S.BoardRow onClick={()=>onClick(applicant)}>
      <div>
        <input
          type="checkbox"
          checked={selected.includes(applicant.id)}
          onChange={(e) => { e.stopPropagation(); onSelectToggle(applicant.id); }}
        />
      </div>
      <div>{applicant.name}</div>
      <div>{applicant.position}</div>
      <div><FiMail size={10} /> {applicant.email}</div>
      <div><FiPhone size={10} /> {applicant.phone}</div>
      <div>
        {Array.isArray(applicant.skills)
          ? applicant.skills.slice(0, 2).map((s,i)=>(<span key={i} style={{
            background: 'var(--primary-color)',
            color: 'white',
            padding: '2px 6px',
            borderRadius: '8px',
            fontSize: '10px',
            fontWeight: '500',
            marginRight: '4px'
          }}>{s}</span>))
          : <span style={{
            background: 'var(--primary-color)',
            color: 'white',
            padding: '2px 6px',
            borderRadius: '8px',
            fontSize: '10px',
            fontWeight: '500'
          }}>기술스택 없음</span>}
        {Array.isArray(applicant.skills) && applicant.skills.length > 2 && (
          <span style={{
            background: 'var(--primary-color)',
            color: 'white',
            padding: '2px 6px',
            borderRadius: '8px',
            fontSize: '10px',
            fontWeight: '500'
          }}>+{applicant.skills.length - 2}</span>
        )}
      </div>
      <div>
        <S.StatusBadge status={applicant.status}>{getStatusText(applicant.status)}</S.StatusBadge>
      </div>
      <div>
        <span style={{
          background: (() => {
            const score = applicant.ranks?.total || 0;
            if (score >= 7) return '#10b981';
            if (score >= 5) return '#f59e0b';
            return '#ef4444';
          })(),
          color: 'white',
          padding: '4px 8px',
          borderRadius: '12px',
          fontSize: '12px',
          fontWeight: '600'
        }}>{applicant.ranks?.total || 0}점</span>
      </div>
    </S.BoardRow>
  );
};

export default ApplicantBoard;
