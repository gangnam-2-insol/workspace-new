import React from 'react';
import { FiUser, FiCheck, FiClock, FiX } from 'react-icons/fi';
import * as S from '../styles';

const StatsCards = ({ stats, onSendMail }) => {
  const { total, passed, waiting, rejected } = stats;
  return (
    <>
      {/* 총 지원자 */}
      <S.StatCard initial={{ opacity:0, y:20, scale:.9 }} animate={{ opacity:1, y:0, scale:1 }} transition={{ delay:.05, duration:.3 }}>
        <S.StatValue key={total}>{total}</S.StatValue>
        <S.StatLabel>총 지원자</S.StatLabel>
      </S.StatCard>

      {/* 합격 */}
      <S.StatCard initial={{ opacity:0, y:20, scale:.9 }} animate={{ opacity:1, y:0, scale:1 }} transition={{ delay:.1, duration:.3 }}>
        <S.StatValue key={passed}>{passed}</S.StatValue>
        <S.StatLabel>합격</S.StatLabel>
      </S.StatCard>

      {/* 보류 */}
      <S.StatCard initial={{ opacity:0, y:20, scale:.9 }} animate={{ opacity:1, y:0, scale:1 }} transition={{ delay:.15, duration:.3 }}>
        <S.StatValue key={waiting}>{waiting}</S.StatValue>
        <S.StatLabel>보류</S.StatLabel>
      </S.StatCard>

      {/* 불합격 */}
      <S.StatCard initial={{ opacity:0, y:20, scale:.9 }} animate={{ opacity:1, y:0, scale:1 }} transition={{ delay:.2, duration:.3 }}>
        <S.StatValue key={rejected}>{rejected}</S.StatValue>
        <S.StatLabel>불합격</S.StatLabel>
      </S.StatCard>
    </>
  );
};

export default StatsCards;
