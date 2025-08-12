import React, { useState } from 'react';
import styled from 'styled-components';
import { FiArrowLeft, FiDownload, FiShare2 } from 'react-icons/fi';
import CoverLetterAnalysis from '../components/CoverLetterAnalysis';
import CoverLetterAnalysisResult from '../components/CoverLetterAnalysisResult';
import { generateCoverLetterSummary, exportCoverLetterAnalysisToCSV } from '../utils/coverLetterUtils';

const PageContainer = styled.div`
  min-height: 100vh;
  background: var(--background-color);
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const BackButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 16px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
`;

const Subtitle = styled.p`
  color: var(--text-secondary);
  font-size: 16px;
  margin: 0;
`;

const HeaderRight = styled.div`
  display: flex;
  gap: 12px;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: ${props => props.variant === 'secondary' ? 'white' : 'var(--primary-color)'};
  color: ${props => props.variant === 'secondary' ? 'var(--primary-color)' : 'white'};
  border: 1px solid var(--primary-color);
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: ${props => props.variant === 'secondary' ? 'var(--background-hover)' : 'var(--primary-hover)'};
    transform: translateY(-1px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const Content = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const SummarySection = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
`;

const SummaryTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
`;

const SummaryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
`;

const SummaryCard = styled.div`
  background: var(--background-light);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
`;

const SummaryValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
`;

const SummaryLabel = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
`;

const StrengthsWeaknesses = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
`;

const StrengthsCard = styled.div`
  background: var(--success-background);
  border-radius: 8px;
  padding: 16px;
`;

const WeaknessesCard = styled.div`
  background: var(--error-background);
  border-radius: 8px;
  padding: 16px;
`;

const CardTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: var(--text-primary);
`;

const CardList = styled.ul`
  margin: 0;
  padding-left: 20px;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
`;

const CardListItem = styled.li`
  margin-bottom: 8px;
`;

const NoAnalysisMessage = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
  font-size: 18px;
`;

const CoverLetterAnalysisPage = () => {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isExporting, setIsExporting] = useState(false);

  const handleAnalysisComplete = (result) => {
    setAnalysisResult(result);
  };

  const handleBack = () => {
    // 이전 페이지로 이동하거나 메인 페이지로 이동
    window.history.back();
  };

  const handleExportCSV = async () => {
    if (!analysisResult) return;
    
    setIsExporting(true);
    try {
      const csv = exportCoverLetterAnalysisToCSV(analysisResult);
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', '자기소개서_분석_결과.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('CSV 내보내기 실패:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleShare = async () => {
    if (!analysisResult) return;
    
    try {
      const summary = generateCoverLetterSummary(analysisResult);
      const shareText = `자기소개서 분석 결과: ${summary.averageScore}/10점, ${summary.totalItems}개 항목 분석 완료`;
      
      if (navigator.share) {
        await navigator.share({
          title: '자기소개서 분석 결과',
          text: shareText,
          url: window.location.href
        });
      } else {
        // 클립보드에 복사
        await navigator.clipboard.writeText(shareText);
        alert('분석 결과가 클립보드에 복사되었습니다.');
      }
    } catch (error) {
      console.error('공유 실패:', error);
    }
  };

  const summary = analysisResult ? generateCoverLetterSummary(analysisResult) : null;

  return (
    <PageContainer>
      <Header>
        <HeaderLeft>
          <BackButton onClick={handleBack}>
            <FiArrowLeft />
            뒤로
          </BackButton>
          <div>
            <Title>자기소개서 분석</Title>
            <Subtitle>AI가 자기소개서를 분석하여 상세한 피드백을 제공합니다</Subtitle>
          </div>
        </HeaderLeft>
        <HeaderRight>
          {analysisResult && (
            <>
              <ActionButton variant="secondary" onClick={handleExportCSV} disabled={isExporting}>
                <FiDownload />
                {isExporting ? '내보내는 중...' : 'CSV 내보내기'}
              </ActionButton>
              <ActionButton variant="secondary" onClick={handleShare}>
                <FiShare2 />
                공유
              </ActionButton>
            </>
          )}
        </HeaderRight>
      </Header>

      <Content>
        {!analysisResult ? (
          <>
            <CoverLetterAnalysis onAnalysisComplete={handleAnalysisComplete} />
            <NoAnalysisMessage>
              자기소개서 파일을 업로드하여 AI 분석을 시작하세요
            </NoAnalysisMessage>
          </>
        ) : (
          <>
            {summary && (
              <SummarySection>
                <SummaryTitle>분석 요약</SummaryTitle>
                <SummaryGrid>
                  <SummaryCard>
                    <SummaryValue>{summary.totalItems}</SummaryValue>
                    <SummaryLabel>분석 항목 수</SummaryLabel>
                  </SummaryCard>
                  <SummaryCard>
                    <SummaryValue>{summary.averageScore.toFixed(1)}/10</SummaryValue>
                    <SummaryLabel>평균 점수</SummaryLabel>
                  </SummaryCard>
                  <SummaryCard>
                    <SummaryValue>{summary.strengths.length}</SummaryValue>
                    <SummaryLabel>강점 항목</SummaryLabel>
                  </SummaryCard>
                  <SummaryCard>
                    <SummaryValue>{summary.weaknesses.length}</SummaryValue>
                    <SummaryLabel>개선 항목</SummaryLabel>
                  </SummaryCard>
                </SummaryGrid>
                
                <StrengthsWeaknesses>
                  <StrengthsCard>
                    <CardTitle>강점</CardTitle>
                    <CardList>
                      {summary.strengths.length > 0 ? (
                        summary.strengths.map((item, index) => (
                          <CardListItem key={index}>
                            <strong>{item.category}</strong> ({item.score}/10): {item.feedback}
                          </CardListItem>
                        ))
                      ) : (
                        <CardListItem>강점으로 분류된 항목이 없습니다.</CardListItem>
                      )}
                    </CardList>
                  </StrengthsCard>
                  
                  <WeaknessesCard>
                    <CardTitle>개선점</CardTitle>
                    <CardList>
                      {summary.weaknesses.length > 0 ? (
                        summary.weaknesses.map((item, index) => (
                          <CardListItem key={index}>
                            <strong>{item.category}</strong> ({item.score}/10): {item.feedback}
                          </CardListItem>
                        ))
                      ) : (
                        <CardListItem>개선이 필요한 항목이 없습니다.</CardListItem>
                      )}
                    </CardList>
                  </WeaknessesCard>
                </StrengthsWeaknesses>
              </SummarySection>
            )}
            
            <CoverLetterAnalysisResult analysisData={analysisResult} />
            
            <CoverLetterAnalysis onAnalysisComplete={handleAnalysisComplete} />
          </>
        )}
      </Content>
    </PageContainer>
  );
};

export default CoverLetterAnalysisPage;
