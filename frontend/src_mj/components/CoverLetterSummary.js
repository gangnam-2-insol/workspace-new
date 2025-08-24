import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FiEye, FiFileText, FiStar, FiCheck, FiAlertCircle, FiX } from 'react-icons/fi';
import CoverLetterAnalysisModal from './CoverLetterAnalysisModal';

const SummaryContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1e5e9;
  margin: 16px 0;
`;

const SummaryHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
`;

const HeaderIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
`;

const HeaderContent = styled.div`
  flex: 1;
`;

const HeaderTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 4px 0;
`;

const HeaderSubtitle = styled.p`
  font-size: 14px;
  color: #666;
  margin: 0;
`;

const SummaryContent = styled.div`
  margin-bottom: 20px;
`;

const OverallScore = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 16px 0;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  text-align: center;
`;

const ScoreCircle = styled.div`
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  border: 3px solid rgba(255, 255, 255, 0.3);
`;

const ScoreInfo = styled.div`
  text-align: left;
`;

const ScoreLabel = styled.div`
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 4px;
`;

const ScoreValue = styled.div`
  font-size: 18px;
  font-weight: 600;
  opacity: 0.8;
`;

const AnalysisGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin: 20px 0;
`;

const AnalysisItem = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 5) return '#ffc107';
    return '#dc3545';
  }};
  transition: all 0.2s;

  &:hover {
    background: #e9ecef;
    transform: translateY(-2px);
  }
`;

const ItemHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
`;

const ItemTitle = styled.h4`
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  margin: 0;
`;

const ItemScore = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
`;

const ScoreNumber = styled.span`
  font-size: 18px;
  color: ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 5) return '#ffc107';
    return '#dc3545';
  }};
`;

const ScoreMax = styled.span`
  font-size: 14px;
  color: #6c757d;
`;

const StatusIcon = styled.div`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  background: ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 5) return '#ffc107';
    return '#dc3545';
  }};
`;

const ScoreBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  margin-top: 12px;
`;

const ScoreFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 5) return '#ffc107';
    return '#dc3545';
  }};
  width: ${props => (props.score / 10) * 100}%;
  border-radius: 4px;
  transition: width 0.3s ease;
`;

const ScoreFeedback = styled.div`
  font-size: 13px;
  color: #6c757d;
  line-height: 1.4;
  margin-top: 8px;
`;

const ViewDetailsButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
`;

const CoverLetterSummary = ({ coverLetterData, analysisData }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (!coverLetterData && !analysisData) {
    return (
      <SummaryContainer>
        <SummaryHeader>
          <HeaderIcon>
            <FiFileText />
          </HeaderIcon>
          <HeaderContent>
            <HeaderTitle>자기소개서 요약</HeaderTitle>
            <HeaderSubtitle>자기소개서가 등록되지 않았습니다.</HeaderSubtitle>
          </HeaderContent>
        </SummaryHeader>
        <SummaryContent>
          <div style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
            지원자가 자기소개서를 업로드하지 않았거나, 분석 데이터가 없습니다.
          </div>
        </SummaryContent>
      </SummaryContainer>
    );
  }

  // 자소서 분석 항목 데이터 구성 (9개 평가 항목)
  const getCoverLetterAnalysisItems = () => {
    if (!analysisData?.cover_letter_analysis) {
      // 기본 데이터 (예시)
      return [
        { key: 'motivation_relevance', label: '지원 동기', score: 8, feedback: '지원 동기가 명확하고 구체적으로 표현되었습니다.' },
        { key: 'problem_solving_STAR', label: 'STAR 기법', score: 7, feedback: 'STAR 기법을 활용한 문제 해결 사례가 잘 정리되어 있습니다.' },
        { key: 'quantitative_impact', label: '정량적 성과', score: 6, feedback: '일부 정량적 성과가 제시되었으나 더 구체적인 수치가 필요합니다.' },
        { key: 'job_understanding', label: '직무 이해도', score: 9, feedback: '지원 직무에 대한 깊은 이해와 관련 경험이 잘 드러납니다.' },
        { key: 'unique_experience', label: '차별화 경험', score: 8, feedback: '다른 지원자와 차별화되는 독특한 경험이 잘 표현되었습니다.' },
        { key: 'logical_flow', label: '논리적 흐름', score: 7, feedback: '전체적인 논리적 흐름이 자연스럽게 연결되어 있습니다.' },
        { key: 'keyword_diversity', label: '키워드 다양성', score: 6, feedback: '관련 키워드가 적절히 사용되었으나 더 다양한 표현이 가능합니다.' },
        { key: 'sentence_readability', label: '문장 가독성', score: 8, feedback: '문장이 명확하고 읽기 쉽게 구성되어 있습니다.' },
        { key: 'typos_and_errors', label: '오탈자', score: 9, feedback: '오탈자나 문법 오류가 거의 발견되지 않았습니다.' }
      ];
    }

    const coverLetterAnalysis = analysisData.cover_letter_analysis;
    const items = [
      { key: 'motivation_relevance', label: '지원 동기', score: coverLetterAnalysis.motivation_relevance?.score || 7, feedback: coverLetterAnalysis.motivation_relevance?.feedback || '지원 동기에 대한 분석 결과입니다.' },
      { key: 'problem_solving_STAR', label: 'STAR 기법', score: coverLetterAnalysis.problem_solving_STAR?.score || 7, feedback: coverLetterAnalysis.problem_solving_STAR?.feedback || 'STAR 기법 활용에 대한 분석 결과입니다.' },
      { key: 'quantitative_impact', label: '정량적 성과', score: coverLetterAnalysis.quantitative_impact?.score || 7, feedback: coverLetterAnalysis.quantitative_impact?.feedback || '정량적 성과 제시에 대한 분석 결과입니다.' },
      { key: 'job_understanding', label: '직무 이해도', score: coverLetterAnalysis.job_understanding?.score || 7, feedback: coverLetterAnalysis.job_understanding?.feedback || '직무 이해도에 대한 분석 결과입니다.' },
      { key: 'unique_experience', label: '차별화 경험', score: coverLetterAnalysis.unique_experience?.score || 7, feedback: coverLetterAnalysis.unique_experience?.feedback || '차별화 경험에 대한 분석 결과입니다.' },
      { key: 'logical_flow', label: '논리적 흐름', score: coverLetterAnalysis.logical_flow?.score || 7, feedback: coverLetterAnalysis.logical_flow?.feedback || '논리적 흐름에 대한 분석 결과입니다.' },
      { key: 'keyword_diversity', label: '키워드 다양성', score: coverLetterAnalysis.keyword_diversity?.score || 7, feedback: coverLetterAnalysis.keyword_diversity?.feedback || '키워드 다양성에 대한 분석 결과입니다.' },
      { key: 'sentence_readability', label: '문장 가독성', score: coverLetterAnalysis.sentence_readability?.score || 7, feedback: coverLetterAnalysis.sentence_readability?.feedback || '문장 가독성에 대한 분석 결과입니다.' },
      { key: 'typos_and_errors', label: '오탈자', score: coverLetterAnalysis.typos_and_errors?.score || 7, feedback: coverLetterAnalysis.typos_and_errors?.feedback || '오탈자 검토에 대한 분석 결과입니다.' }
    ];

    return items;
  };

  const analysisItems = getCoverLetterAnalysisItems();

  // 전체 점수 계산
  const overallScore = analysisItems.reduce((sum, item) => sum + item.score, 0) / analysisItems.length;

  const handleViewDetails = () => {
    setIsModalOpen(true);
  };

  const getScoreIcon = (score) => {
    if (score >= 8) return <FiCheck />;
    if (score >= 5) return <FiAlertCircle />;
    return <FiX />;
  };

  return (
    <>
      <SummaryContainer>
        <SummaryHeader>
          <HeaderIcon>
            <FiFileText />
          </HeaderIcon>
          <HeaderContent>
            <HeaderTitle>자기소개서 요약</HeaderTitle>
            <HeaderSubtitle>
              AI 분석 결과 • 총점: {overallScore.toFixed(1)}/10점
            </HeaderSubtitle>
          </HeaderContent>
        </SummaryHeader>

        <SummaryContent>
          {/* 전체 점수 표시 */}
          <OverallScore>
            <ScoreCircle>
              {overallScore.toFixed(1)}
            </ScoreCircle>
            <ScoreInfo>
              <ScoreLabel>자기소개서 종합 점수</ScoreLabel>
              <ScoreValue>{overallScore.toFixed(1)}/10점</ScoreValue>
            </ScoreInfo>
          </OverallScore>

          {/* 9개 평가 항목 그리드 */}
          <AnalysisGrid>
            {analysisItems.map((item, index) => (
              <AnalysisItem key={index} score={item.score}>
                <ItemHeader>
                  <ItemTitle>{item.label}</ItemTitle>
                  <ItemScore>
                    <ScoreNumber score={item.score}>{item.score}</ScoreNumber>
                    <ScoreMax>/10</ScoreMax>
                    <StatusIcon score={item.score}>
                      {getScoreIcon(item.score)}
                    </StatusIcon>
                  </ItemScore>
                </ItemHeader>
                
                {/* 막대 그래프 */}
                <ScoreBar>
                  <ScoreFill score={item.score} />
                </ScoreBar>
                
                {/* 피드백 */}
                <ScoreFeedback>
                  {item.feedback}
                </ScoreFeedback>
              </AnalysisItem>
            ))}
          </AnalysisGrid>
        </SummaryContent>

        <ViewDetailsButton onClick={handleViewDetails}>
          <FiEye />
          자세히보기
        </ViewDetailsButton>
      </SummaryContainer>

      {/* 상세 분석 모달 */}
      <CoverLetterAnalysisModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        coverLetterData={coverLetterData}
        analysisData={analysisData}
      />
    </>
  );
};

export default CoverLetterSummary;
