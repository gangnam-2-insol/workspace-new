import React from 'react';
import { FiFileText } from 'react-icons/fi';
import * as S from '../styles/HeaderStyles';

const HeaderSection = ({ onNewResumeClick }) => {
  return (
    <S.Header>
      <S.HeaderContent>
        <S.HeaderLeft>
          <S.Title>지원자 관리</S.Title>
          <S.Subtitle>채용 공고별 지원자 현황을 관리하고 검토하세요</S.Subtitle>
        </S.HeaderLeft>
        <S.HeaderRight>
          <S.NewResumeButton onClick={onNewResumeClick}>
            <FiFileText size={16} />
            새 지원자 등록
          </S.NewResumeButton>
        </S.HeaderRight>
      </S.HeaderContent>
    </S.Header>
  );
};

export default HeaderSection;
