import React from 'react';
import styled from 'styled-components';

const SummaryContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const SummaryTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SummaryContent = styled.div`
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
`;

const ScoreBadge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => props.color || '#f3f4f6'};
  color: ${props => props.textColor || '#374151'};
`;

const CoverLetterSummary = ({ coverLetterData, analysisData }) => {
  if (!coverLetterData && !analysisData) {
    return (
      <SummaryContainer>
        <SummaryTitle>📄 자소서 요약</SummaryTitle>
        <SummaryContent>
          자소서 데이터가 없습니다.
        </SummaryContent>
      </SummaryContainer>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 80) return { bg: '#dcfce7', text: '#166534' };
    if (score >= 60) return { bg: '#fef3c7', text: '#92400e' };
    return { bg: '#fee2e2', text: '#991b1b' };
  };

  return (
    <SummaryContainer>
      <SummaryTitle>📄 자소서 요약</SummaryTitle>
      <SummaryContent>
        {coverLetterData && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ marginBottom: '8px' }}>
              <strong>제목:</strong> {coverLetterData.title || '자소서'}
            </div>
            <div style={{ marginBottom: '8px' }}>
              <strong>지원 직무:</strong> {coverLetterData.position || '미지정'}
            </div>
            <div style={{ marginBottom: '8px' }}>
              <strong>글자 수:</strong> {coverLetterData.charCount || 0}자
            </div>
            <div style={{ marginBottom: '8px' }}>
              <strong>단어 수:</strong> {coverLetterData.wordCount || 0}개
            </div>
          </div>
        )}

        {analysisData && (
          <div>
            <div style={{ marginBottom: '12px' }}>
              <strong>분석 점수:</strong>{' '}
              <ScoreBadge
                color={getScoreColor(analysisData.overallScore * 10).bg}
                textColor={getScoreColor(analysisData.overallScore * 10).text}
              >
                {Math.round(analysisData.overallScore * 10)}점
              </ScoreBadge>
            </div>

            {analysisData.detailedAnalysis && (
              <div style={{ marginBottom: '12px' }}>
                <strong>분석 요약:</strong>
                <div style={{ marginTop: '4px', padding: '8px', backgroundColor: '#f9fafb', borderRadius: '6px' }}>
                  {analysisData.detailedAnalysis}
                </div>
              </div>
            )}

            {analysisData.recommendations && analysisData.recommendations.length > 0 && (
              <div>
                <strong>주요 개선사항:</strong>
                <ul style={{ marginTop: '4px', paddingLeft: '20px' }}>
                  {analysisData.recommendations.slice(0, 3).map((rec, index) => (
                    <li key={index} style={{ marginBottom: '4px' }}>
                      {typeof rec === 'string' ? rec : rec.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </SummaryContent>
    </SummaryContainer>
  );
};

export default CoverLetterSummary;
