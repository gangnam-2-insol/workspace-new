import React from 'react';
import styled from 'styled-components';
import { FiMessageSquare, FiStar, FiCheckCircle, FiAlertCircle, FiInfo } from 'react-icons/fi';

const ResultContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin: 20px 0;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Title = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const Icon = styled.div`
  color: var(--primary-color);
  font-size: 24px;
`;

const OverallScore = styled.div`
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  border-radius: 12px;
  color: white;
  margin-bottom: 24px;
`;

const ScoreValue = styled.div`
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 8px;
`;

const ScoreLabel = styled.div`
  font-size: 16px;
  opacity: 0.9;
`;

const ScoreSubtext = styled.div`
  font-size: 14px;
  opacity: 0.8;
  margin-top: 8px;
`;

const AnalysisGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 24px;
`;

const AnalysisCard = styled.div`
  background: var(--background-light);
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid var(--primary-color);
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`;

const CardTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const CardScore = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  background: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  color: var(--primary-color);
  font-size: 14px;
`;

const CardContent = styled.div`
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
`;

const ConfidenceIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 16px;
`;

const ConfidenceBar = styled.div`
  width: 60px;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
`;

const ConfidenceFill = styled.div`
  height: 100%;
  background: var(--success-color);
  width: ${props => props.confidence * 100}%;
  transition: width 0.3s ease;
`;

const NoDataMessage = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
  font-size: 16px;
`;

const CoverLetterAnalysisResult = ({ analysisData, onClose }) => {
  if (!analysisData || !analysisData.cover_letter_analysis) {
    return (
      <ResultContainer>
        <NoDataMessage>
          <FiInfo size={24} style={{ marginBottom: '12px', opacity: 0.5 }} />
          <div>자기소개서 분석 데이터가 없습니다.</div>
        </NoDataMessage>
      </ResultContainer>
    );
  }

  const { overall_summary, cover_letter_analysis } = analysisData;
  const analysisItems = Object.entries(cover_letter_analysis);

  const getScoreColor = (score) => {
    if (score >= 8.5) return '#10B981'; // Green
    if (score >= 7.0) return '#F59E0B'; // Yellow
    return '#EF4444'; // Red
  };

  const getScoreIcon = (score) => {
    if (score >= 8.5) return <FiCheckCircle />;
    if (score >= 7.0) return <FiStar />;
    return <FiAlertCircle />;
  };

  return (
    <ResultContainer>
      <Header>
        <HeaderLeft>
          <Icon>
            <FiMessageSquare />
          </Icon>
          <Title>자기소개서 분석 결과</Title>
        </HeaderLeft>
      </Header>

      <OverallScore>
        <ScoreValue>{overall_summary.total_score}/10</ScoreValue>
        <ScoreLabel>전체 평점</ScoreLabel>
        <ScoreSubtext>
          신뢰도: {(overall_summary.confidence * 100).toFixed(0)}%
        </ScoreSubtext>
      </OverallScore>

      <AnalysisGrid>
        {analysisItems.map(([key, item]) => (
          <AnalysisCard key={key}>
            <CardHeader>
              <CardTitle>
                {key === 'job_understanding' && '직무 이해도'}
                {key === 'unique_experience' && '독특한 경험'}
                {key === 'keyword_diversity' && '키워드 다양성'}
                {key === 'motivation_clarity' && '동기 명확성'}
                {key === 'writing_quality' && '작성 품질'}
                {key === 'career_alignment' && '경력 일치도'}
                {key}
              </CardTitle>
              <CardScore style={{ color: getScoreColor(item.score) }}>
                {getScoreIcon(item.score)}
                {item.score}/10
              </CardScore>
            </CardHeader>
            <CardContent>{item.feedback}</CardContent>
          </AnalysisCard>
        ))}
      </AnalysisGrid>

      <ConfidenceIndicator>
        <FiInfo size={12} />
        <span>분석 신뢰도</span>
        <ConfidenceBar>
          <ConfidenceFill confidence={overall_summary.confidence} />
        </ConfidenceBar>
        <span>{(overall_summary.confidence * 100).toFixed(0)}%</span>
      </ConfidenceIndicator>
    </ResultContainer>
  );
};

export default CoverLetterAnalysisResult;
