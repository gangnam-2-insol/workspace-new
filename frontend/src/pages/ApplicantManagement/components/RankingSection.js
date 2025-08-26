import React from 'react';
import { FiBarChart2, FiX } from 'react-icons/fi';
import * as S from '../styles/RankingStyles';

const RankingSection = ({
  selectedJobPostingId,
  rankingResults,
  setRankingResults,
  handleCardClick,
  handleUpdateStatus
}) => {
  if (!selectedJobPostingId || selectedJobPostingId === '' || !rankingResults || !rankingResults.results || rankingResults.results.length === 0) {
    return null;
  }

  return (
    <S.RankingResultsSection>
      <S.RankingHeader>
        <S.RankingTitle>
          <FiBarChart2 size={20} />
          {rankingResults.keyword} 랭킹 결과 (총 {rankingResults.totalCount}명)
        </S.RankingTitle>

        <S.RankingClearButton onClick={() => {
          setRankingResults(null);
          try {
            sessionStorage.removeItem('rankingResults');
          } catch (error) {
            console.error('랭킹 결과 세션 스토리지 삭제 실패:', error);
          }
        }}>
          <FiX size={16} />
          초기화
        </S.RankingClearButton>
      </S.RankingHeader>

      <S.RankingTable>
        <S.RankingTableHeader>
          <S.RankingTableHeaderCell>순위</S.RankingTableHeaderCell>
          <S.RankingTableHeaderCell>지원자</S.RankingTableHeaderCell>
          <S.RankingTableHeaderCell>직무</S.RankingTableHeaderCell>
          <S.RankingTableHeaderCell>총점</S.RankingTableHeaderCell>
          <S.RankingTableHeaderCell>세부 점수</S.RankingTableHeaderCell>
          <S.RankingTableHeaderCell>상태</S.RankingTableHeaderCell>
        </S.RankingTableHeader>

        <S.RankingTableBody>
          {rankingResults.results.map((result, index) => (
            <S.RankingTableRow
              key={result.applicant._id || result.applicant.id}
              onClick={() => handleCardClick(result.applicant)}
              style={{ cursor: 'pointer' }}
            >
              <S.RankingTableCell>
                <S.RankBadge rank={result.rank}>
                  {result.rankText}
                </S.RankBadge>
              </S.RankingTableCell>
              <S.RankingTableCell>
                <div>
                  <div style={{ fontWeight: '600', fontSize: '14px' }}>{result.applicant.name}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{result.applicant.email}</div>
                </div>
              </S.RankingTableCell>
              <S.RankingTableCell>
                <div style={{ fontSize: '13px' }}>{result.applicant.position}</div>
              </S.RankingTableCell>
              <S.RankingTableCell>
                <S.TotalScore>
                  {result.totalScore}점
                </S.TotalScore>
              </S.RankingTableCell>
              <S.RankingTableCell>
                <S.ScoreBreakdown>
                  <S.ScoreItem>
                    <span>이력서:</span>
                    <span style={{ color: result.breakdown.resume >= 7 ? '#10b981' : result.breakdown.resume >= 5 ? '#f59e0b' : '#ef4444' }}>
                      {result.breakdown.resume}점
                    </span>
                  </S.ScoreItem>
                  <S.ScoreItem>
                    <span>자소서:</span>
                    <span style={{ color: result.breakdown.coverLetter >= 7 ? '#10b981' : result.breakdown.coverLetter >= 5 ? '#f59e0b' : '#ef4444' }}>
                      {result.breakdown.coverLetter}점
                    </span>
                  </S.ScoreItem>
                  <S.ScoreItem>
                    <span>포트폴리오:</span>
                    <span style={{ color: result.breakdown.portfolio >= 7 ? '#10b981' : result.breakdown.portfolio >= 5 ? '#f59e0b' : '#ef4444' }}>
                      {result.breakdown.portfolio}점
                    </span>
                  </S.ScoreItem>
                  <S.ScoreItem>
                    <span>키워드:</span>
                    <span style={{ color: result.breakdown.keywordMatching >= 7 ? '#10b981' : result.breakdown.keywordMatching >= 5 ? '#f59e0b' : '#ef4444' }}>
                      {result.breakdown.keywordMatching}점
                    </span>
                  </S.ScoreItem>
                </S.ScoreBreakdown>
              </S.RankingTableCell>
              <S.RankingTableCell>
                <select
                  value={result.applicant.status}
                  onChange={(e) => {
                    e.stopPropagation();
                    handleUpdateStatus(result.applicant._id || result.applicant.id, e.target.value);
                  }}
                  onClick={(e) => e.stopPropagation()}
                  onMouseDown={(e) => e.stopPropagation()}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: '500',
                    border: '1px solid var(--border-color)',
                    background: 'white',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    minWidth: '80px'
                  }}
                >
                  <option value="보류">보류</option>
                  <option value="서류합격">서류합격</option>
                  <option value="최종합격">최종합격</option>
                  <option value="서류불합격">서류불합격</option>
                </select>
              </S.RankingTableCell>
            </S.RankingTableRow>
          ))}
        </S.RankingTableBody>
      </S.RankingTable>
    </S.RankingResultsSection>
  );
};

export default RankingSection;
