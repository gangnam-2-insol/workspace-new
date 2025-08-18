import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiCheck, FiAlertCircle, FiStar, FiTrendingUp, FiTrendingDown, FiFileText, FiMessageSquare, FiCode, FiBarChart2 } from 'react-icons/fi';

const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: 32px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
`;

const CloseButton = styled.button`
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;

  &:hover {
    background: #f5f5f5;
    color: #333;
  }
`;

const Header = styled.div`
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
`;

const Title = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  font-size: 14px;
  color: #666;
  margin: 0;
`;

const OverallScore = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
`;

const ScoreCircle = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
`;

const ScoreInfo = styled.div`
  flex: 1;
`;

const ScoreLabel = styled.div`
  font-size: 14px;
  opacity: 0.9;
`;

const OverallScoreValue = styled.div`
  font-size: 24px;
  font-weight: 700;
`;

const AnalysisSection = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ScoreGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
`;

const ScoreCard = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 6) return '#ffc107';
    return '#dc3545';
  }};
`;

const ScoreVisualization = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
`;

const ScoreBar = styled.div`
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
`;

const ScoreFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 6) return '#ffc107';
    return '#dc3545';
  }};
  width: ${props => (props.score / 10) * 100}%;
  border-radius: 4px;
  transition: width 0.3s ease;
`;

const ScoreHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const ScoreName = styled.div`
  font-weight: 600;
  color: #333;
  font-size: 14px;
`;

const ScoreValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 6) return '#ffc107';
    return '#dc3545';
  }};
`;

const ScoreFeedback = styled.div`
  font-size: 13px;
  color: #666;
  line-height: 1.4;
`;

const RecommendationSection = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 24px;
`;

const RecommendationTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RecommendationList = styled.ul`
  margin: 0;
  padding-left: 20px;
`;

const RecommendationItem = styled.li`
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
  line-height: 1.5;
`;

const DetailedAnalysisSection = styled.div`
  margin-top: 32px;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
`;

const DetailedAnalysisTitle = styled.h3`
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const DetailedAnalysisSubSection = styled.div`
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
`;

const DetailedAnalysisSubTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #007bff;
`;

const DetailedAnalysisContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const DetailedAnalysisItem = styled.div`
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #007bff;
`;

const DetailedAnalysisItemTitle = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
`;

const DetailedAnalysisItemFeedback = styled.div`
  font-size: 13px;
  color: #555;
  line-height: 1.6;
  margin-bottom: 8px;
  background: white;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
`;

const DetailedAnalysisItemScore = styled.div`
  font-size: 12px;
  font-weight: 600;
  color: #007bff;
  text-align: right;
`;

const getScoreIcon = (score) => {
  if (score >= 8) return <FiCheck color="#28a745" />;
  if (score >= 6) return <FiAlertCircle color="#ffc107" />;
  return <FiX color="#dc3545" />;
};

const getResumeAnalysisLabel = (key) => {
  const labels = {
    'basic_info_completeness': '기본정보 완성도',
    'job_relevance': '직무 적합성',
    'experience_clarity': '경력 명확성',
    'tech_stack_clarity': '기술스택 명확성',
    'project_recency': '프로젝트 최신성',
    'achievement_metrics': '성과 지표',
    'readability': '가독성',
    'typos_and_errors': '오탈자',
    'update_freshness': '최신성'
  };
  return labels[key] || key.replace(/_/g, ' ');
};

const getCoverLetterAnalysisLabel = (key) => {
  const labels = {
    'motivation_relevance': '지원 동기',
    'problem_solving_STAR': 'STAR 기법',
    'quantitative_impact': '정량적 영향',
    'job_understanding': '직무 이해도',
    'unique_experience': '차별화 경험',
    'logical_flow': '논리적 흐름',
    'keyword_diversity': '키워드 다양성',
    'sentence_readability': '문장 가독성',
    'typos_and_errors': '오탈자'
  };
  return labels[key] || key.replace(/_/g, ' ');
};

const getPortfolioAnalysisLabel = (key) => {
  const labels = {
    'project_overview': '프로젝트 개요',
    'tech_stack': '기술 스택',
    'personal_contribution': '개인 기여도',
    'achievement_metrics': '성과 지표',
    'visual_quality': '시각적 품질',
    'documentation_quality': '문서화 품질',
    'job_relevance': '직무 관련성',
    'unique_features': '독창적 기능',
    'maintainability': '유지보수성'
  };
  return labels[key] || key.replace(/_/g, ' ');
};

const getScoreColor = (score) => {
  if (score >= 8) return '#28a745';
  if (score >= 6) return '#ffc107';
  return '#dc3545';
};

const DetailedAnalysisModal = ({ isOpen, onClose, analysisData }) => {
  const [showRaw, setShowRaw] = useState(false);
  if (!isOpen || !analysisData) return null;

  const { analysis_result } = analysisData;
  
  // 디버깅을 위한 콘솔 로그 추가
  console.log('DetailedAnalysisModal - analysisData:', analysisData);
  console.log('DetailedAnalysisModal - analysis_result:', analysis_result);
  
  if (!analysis_result) {
    return (
      <AnimatePresence>
        {isOpen && (
          <ModalOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          >
            <ModalContent
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <CloseButton onClick={onClose}>×</CloseButton>
              <Header>
                <Title>상세 분석 결과</Title>
                <Subtitle>분석 데이터를 찾을 수 없습니다.</Subtitle>
              </Header>
            </ModalContent>
          </ModalOverlay>
        )}
      </AnimatePresence>
    );
  }

  // 피드백 텍스트에서 불필요한 예시 구문 제거
  const sanitizeFeedback = (text) => {
    if (!text || typeof text !== 'string') return '';
    const patterns = [
      '예를 들어',
      '예:',
      '예)',
      '예시:',
      '예시로',
      '예시로는'
    ];
    // 문장 단위로 나눈 뒤, 예시 표현이 포함된 문장은 제외
    const sentences = text.split(/(?<=[.!?])\s+|\n+/);
    const filtered = sentences.filter((s) => {
      const trimmed = s.trim();
      if (!trimmed) return false;
      return !patterns.some((p) => trimmed.includes(p));
    });
    const result = filtered.join(' ').trim();
    return result.length > 0 ? result : text;
  };

  // 항목 값 정규화 (null/잘못된 형태 보호)
  const normalizeItem = (item) => {
    if (!item || typeof item !== 'object') {
      return { score: 0, feedback: '' };
    }
    const score = Number.isFinite(item.score) ? item.score : 0;
    const feedback = typeof item.feedback === 'string' ? item.feedback : '';
    return { score, feedback };
  };

  const renderAnalysisSection = (title, data, icon) => {
    if (!data) return null;

    return (
      <AnalysisSection>
        <SectionTitle>
          {icon} {title}
        </SectionTitle>
        <ScoreGrid>
          {Object.entries(data).map(([key, value]) => {
            const item = normalizeItem(value);
            return (
            <ScoreCard key={key} score={item.score}>
              <ScoreHeader>
                <ScoreName>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</ScoreName>
                <ScoreValue score={item.score}>
                  {item.score}/10 {getScoreIcon(item.score)}
                </ScoreValue>
              </ScoreHeader>
              <ScoreFeedback>{sanitizeFeedback(item.feedback) || '분석 결과가 제공되지 않았습니다.'}</ScoreFeedback>
              <ScoreVisualization>
                <ScoreBar>
                  <ScoreFill score={item.score} />
                </ScoreBar>
              </ScoreVisualization>
            </ScoreCard>
          )})}
        </ScoreGrid>
      </AnalysisSection>
    );
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <ModalOverlay
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <ModalContent
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <CloseButton onClick={onClose}>×</CloseButton>
            
            <Header>
              <Title>AI 상세 분석 결과</Title>
              <Subtitle>{analysisData.fileName} - {analysisData.analysisDate}</Subtitle>
              <div style={{position:'absolute', top: 20, right: 52}}>
                <button
                  onClick={() => setShowRaw(v => !v)}
                  style={{
                    padding: '6px 10px', borderRadius: 6, border: '1px solid #e5e7eb',
                    background: showRaw ? '#f3f4f6' : 'white', cursor: 'pointer', fontSize: 12
                  }}
                >{showRaw ? '원본 JSON 숨기기' : '원본 JSON 보기'}</button>
              </div>
            </Header>

            {/* 디버깅 정보 - 실제 파일 내용 확인 (표시 비활성화) */}
            {false && analysisData.extractedTextLength && (
              <div style={{ 
                background: '#f8f9fa', 
                padding: '16px', 
                borderRadius: '8px', 
                marginBottom: '20px',
                border: '1px solid #e9ecef'
              }}>
                <div style={{ fontSize: '14px', fontWeight: '600', color: '#333', marginBottom: '8px' }}>
                  📄 파일 분석 정보
                </div>
                <div style={{ fontSize: '13px', color: '#666' }}>
                  • 파일명: {analysisData.fileName}<br/>
                  • 파일 크기: {analysisData.fileSize ? `${(analysisData.fileSize / 1024).toFixed(1)}KB` : 'N/A'}<br/>
                  • 추출된 텍스트 길이: {analysisData.extractedTextLength}자<br/>
                  • 감지된 문서 타입: {analysisData.detected_type || 'N/A'}<br/>
                  • 신뢰도: {analysisData.detected_confidence || 'N/A'}%
                </div>
              </div>
            )}

            {analysis_result.overall_summary && analysis_result.overall_summary.total_score && analysis_result.overall_summary.total_score > 0 && (
              <OverallScore>
                <ScoreCircle>
                  {analysis_result.overall_summary.total_score}
                </ScoreCircle>
                <ScoreInfo>
                  <ScoreLabel>전체 평가 점수</ScoreLabel>
                  <ScoreValue>{analysis_result.overall_summary.total_score}/10</ScoreValue>
                </ScoreInfo>
              </OverallScore>
            )}

            {analysisData.analysisScore && analysisData.analysisScore > 0 && (
              <OverallScore style={{ background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)' }}>
                <ScoreCircle>
                  {analysisData.analysisScore}
                </ScoreCircle>
                <ScoreInfo>
                  <ScoreLabel>AI 분석 점수</ScoreLabel>
                  <ScoreValue>{analysisData.analysisScore}점</ScoreValue>
                </ScoreInfo>
              </OverallScore>
            )}

            {/* 타입 불일치 경고 메시지 */}
            {analysisData.wrong_placement && (
              <OverallScore style={{ background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)' }}>
                <ScoreCircle>
                  ⚠️
                </ScoreCircle>
                <ScoreInfo>
                  <ScoreLabel>문서 타입 불일치 경고</ScoreLabel>
                  <ScoreValue style={{ fontSize: '14px', lineHeight: '1.4' }}>
                    {analysisData.placement_message}
                  </ScoreValue>
                  <ScoreLabel style={{ fontSize: '12px', marginTop: '8px', opacity: 0.8 }}>
                    감지된 타입: {analysisData.detected_type} (신뢰도: {analysisData.detected_confidence}%)
                  </ScoreLabel>
                  <ScoreLabel style={{ fontSize: '12px', marginTop: '8px', opacity: 0.9, fontWeight: 'bold' }}>
                    ⚠️ 잘못된 문서 유형으로 분석이 제한됩니다
                  </ScoreLabel>
                </ScoreInfo>
              </OverallScore>
            )}

            {/* 문서 타입에 따라 해당하는 분석 결과만 표시 */}
            {analysis_result.resume_analysis && Object.keys(analysis_result.resume_analysis).length > 0 && 
              renderAnalysisSection('이력서 분석', analysis_result.resume_analysis, <FiFileText />)}
            {analysis_result.cover_letter_analysis && Object.keys(analysis_result.cover_letter_analysis).length > 0 && 
              renderAnalysisSection('자기소개서 분석', analysis_result.cover_letter_analysis, <FiMessageSquare />)}
            {analysis_result.portfolio_analysis && Object.keys(analysis_result.portfolio_analysis).length > 0 && 
              renderAnalysisSection('포트폴리오 분석', analysis_result.portfolio_analysis, <FiCode />)}

          </ModalContent>
        </ModalOverlay>
      )}
    </AnimatePresence>
  );
};

export default DetailedAnalysisModal;