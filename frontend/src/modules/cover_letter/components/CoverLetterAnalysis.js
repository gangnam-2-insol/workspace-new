import React, { useState, useRef, useEffect, useMemo } from 'react';
import styled from 'styled-components';
import CustomRadarChart from './CustomRadarChart';

const Container = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: 16px;
  background: transparent;

  @keyframes fadeInScale {
    0% {
      opacity: 0;
      transform: scale(0.95);
    }
    100% {
      opacity: 1;
      transform: scale(1);
    }
  }

  @keyframes fadeInPoint {
    0% {
      opacity: 0;
      transform: scale(0);
    }
    100% {
      opacity: 1;
      transform: scale(1);
    }
  }
`;

// 새로운 레이아웃을 위한 스타일드 컴포넌트들
const HeaderSection = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
  border: none;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    pointer-events: none;
  }
`;

const HeaderTitle = styled.h1`
  font-size: 24px;
  font-weight: 800;
  color: white;
  margin: 0 0 8px 0;
  text-align: center;
  letter-spacing: -0.025em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
`;

const HeaderSubtitle = styled.p`
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  text-align: center;
  position: relative;
  z-index: 1;
`;

const MainContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const RightPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const Card = styled.div`
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
<<<<<<< Updated upstream
=======
  min-height: ${props => props.minHeight || 'auto'};
>>>>>>> Stashed changes

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2);
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }
`;

const CardTitle = styled.h3`
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: -0.025em;
`;

const FullWidthCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid #f1f3f4;
  margin-bottom: 16px;
`;

const RadarChartSection = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e2e8f0;
`;

const SummaryText = styled.p`
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
<<<<<<< Updated upstream
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 16px;
  border-radius: 12px;
  margin: 0;
  border: 1px solid #e2e8f0;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
=======
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin: 0;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  min-height: 280px;
  max-height: 400px;
  overflow-y: auto;
>>>>>>> Stashed changes
`;

const BarChartContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const BarItem = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #667eea, #764ba2);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-color: #cbd5e1;
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);

    &::before {
      opacity: 1;
    }
  }

  &.active {
    background: linear-gradient(135deg, #f0f7ff 0%, #e0f2fe 100%);
    border-color: #3b82f6;
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);

    &::before {
      opacity: 1;
      background: #3b82f6;
    }
  }
`;

const BarLabel = styled.div`
  flex: 3;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  flex-shrink: 0;
  padding-right: 16px;
  word-break: keep-all;
  line-height: 1.4;
`;

const BarContainer = styled.div`
  flex: 7;
  height: 20px;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  margin-right: 0;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
`;

const BarFill = styled.div`
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  background: ${props => props.color || 'linear-gradient(90deg, #667eea, #764ba2)'};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const BarScore = styled.div`
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  font-weight: 700;
  color: #1e293b;
  z-index: 2;
`;

const NoDataMessage = styled.div`
  text-align: center;
  padding: 48px;
  color: #666;
  font-size: 16px;
`;

const CoverLetterAnalysis = ({ analysisData, applicant }) => {
  const [selectedCategory, setSelectedCategory] = useState(null);

  // 🔍 디버깅: 컴포넌트 렌더링 로그
  console.log('🚀 [CoverLetterAnalysis] 컴포넌트 렌더링:', {
    hasAnalysisData: !!analysisData,
    hasApplicant: !!applicant,
    applicantName: applicant?.name,
    applicantId: applicant?.id,
    timestamp: new Date().toISOString()
  });

  // 🔍 디버깅: props 변경 감지
  useEffect(() => {
    console.log('🔄 [CoverLetterAnalysis] Props 변경 감지:', {
      hasAnalysisData: !!analysisData,
      hasApplicant: !!applicant,
      applicantName: applicant?.name,
      applicantId: applicant?.id,
      analysisDataKeys: analysisData ? Object.keys(analysisData) : [],
      timestamp: new Date().toISOString()
    });
  }, [analysisData, applicant]);

  console.log('🔍 [CoverLetterAnalysis] analysisData 상세:', {
    type: typeof analysisData,
    keys: analysisData ? Object.keys(analysisData) : [],
    overallScore: analysisData?.overallScore,
    analysisResult: analysisData?.analysisResult,
    technical_suitability: analysisData?.technical_suitability,
    detailedAnalysis: analysisData?.detailedAnalysis,
    dataSize: analysisData ? JSON.stringify(analysisData).length : 0
  });

  console.log('🔍 [CoverLetterAnalysis] applicant 상세:', {
    name: applicant?.name,
    id: applicant?.id,
    type: typeof applicant,
    keys: applicant ? Object.keys(applicant) : []
  });

  // 자소서 분석 카테고리 정의
  const categories = [
    { key: 'technical_suitability', label: '기술적합성', color: '#3b82f6' },
    { key: 'job_understanding', label: '직무이해도', color: '#10b981' },
    { key: 'growth_potential', label: '성장 가능성', color: '#f59e0b' },
    { key: 'teamwork_communication', label: '팀워크 및 커뮤니케이션', color: '#8b5cf6' },
    { key: 'motivation_company_fit', label: '지원동기/회사 가치관 부합도', color: '#ef4444' }
  ];

  // 새로운 분석 데이터 구조에서 점수 추출 (100점 만점으로 처리)
  const extractScores = (analysisData) => {
    console.log('🔍 [CoverLetterAnalysis] extractScores 함수 호출:', {
      hasAnalysisData: !!analysisData,
      type: typeof analysisData,
      keys: analysisData ? Object.keys(analysisData) : [],
      timestamp: new Date().toISOString()
    });

    if (!analysisData || typeof analysisData !== 'object') {
      console.log('❌ [CoverLetterAnalysis] analysisData가 유효하지 않음 - 기본값 사용');
      return {
        technical_suitability: 75,
        job_understanding: 80,
        growth_potential: 85,
        teamwork_communication: 70,
        motivation_company_fit: 90
      };
    }

    // 새로운 구조: analysisData.analysisResult.technical_suitability.score 형태
    if (analysisData.analysisResult?.technical_suitability?.score) {
      console.log('✅ [CoverLetterAnalysis] 새로운 구조 사용 (analysisResult 내부):', {
        technical_suitability: analysisData.analysisResult.technical_suitability.score,
        job_understanding: analysisData.analysisResult.job_understanding?.score,
        growth_potential: analysisData.analysisResult.growth_potential?.score,
        teamwork_communication: analysisData.analysisResult.teamwork_communication?.score,
        motivation_company_fit: analysisData.analysisResult.motivation_company_fit?.score
      });
      return {
        technical_suitability: analysisData.analysisResult.technical_suitability.score,
        job_understanding: analysisData.analysisResult.job_understanding?.score || 80,
        growth_potential: analysisData.analysisResult.growth_potential?.score || 85,
        teamwork_communication: analysisData.analysisResult.teamwork_communication?.score || 70,
        motivation_company_fit: analysisData.analysisResult.motivation_company_fit?.score || 90
      };
    }

    // 중간 구조: analysisData.technical_suitability.score 형태
    if (analysisData.technical_suitability && typeof analysisData.technical_suitability.score === 'number') {
      console.log('✅ [CoverLetterAnalysis] 중간 구조 사용 (score 속성):', {
        technical_suitability: analysisData.technical_suitability.score,
        job_understanding: analysisData.job_understanding?.score,
        growth_potential: analysisData.growth_potential?.score,
        teamwork_communication: analysisData.teamwork_communication?.score,
        motivation_company_fit: analysisData.motivation_company_fit?.score
      });
      return {
        technical_suitability: analysisData.technical_suitability.score,
        job_understanding: analysisData.job_understanding?.score || 80,
        growth_potential: analysisData.growth_potential?.score || 85,
        teamwork_communication: analysisData.teamwork_communication?.score || 70,
        motivation_company_fit: analysisData.motivation_company_fit?.score || 90
      };
    }

    // 기존 구조: analysisData.technical_suitability 형태
    console.log('✅ [CoverLetterAnalysis] 기존 구조 사용 (직접 접근):', {
      technical_suitability: analysisData.technical_suitability,
      job_understanding: analysisData.job_understanding,
      growth_potential: analysisData.growth_potential,
      teamwork_communication: analysisData.teamwork_communication,
      motivation_company_fit: analysisData.motivation_company_fit
    });
    return {
      technical_suitability: analysisData.technical_suitability || 75,
      job_understanding: analysisData.job_understanding || 80,
      growth_potential: analysisData.growth_potential || 85,
      teamwork_communication: analysisData.teamwork_communication || 70,
      motivation_company_fit: analysisData.motivation_company_fit || 90
    };
  };

  // 🔍 메모이제이션된 데이터 처리
  const processedAnalysisData = useMemo(() => {
    console.log('🔍 [CoverLetterAnalysis] useMemo - 데이터 처리 시작:', {
      hasAnalysisData: !!analysisData,
      timestamp: new Date().toISOString()
    });

    // analysisData가 없으면 기본값 반환
    if (!analysisData) {
      console.log('❌ [CoverLetterAnalysis] analysisData가 없음 - 기본값 반환');
      return {
        data: {
          technical_suitability: 75,
          job_understanding: 80,
          growth_potential: 85,
          teamwork_communication: 70,
          motivation_company_fit: 90
        },
        overallScore: 80,
        summary: '자소서 분석 결과를 확인할 수 있습니다.',
        allRecommendations: ['지속적인 성장과 발전을 권장합니다.']
      };
    }

    // 분석 데이터에서 점수 추출
    const data = extractScores(analysisData);
    console.log('✅ [CoverLetterAnalysis] 점수 추출 완료:', data);

    // 전체 점수 계산 (실제 데이터 우선)
    const overallScore = analysisData?.analysis_result?.overall_score || analysisData?.overallScore || analysisData?.overall_score ||
      Math.round(Object.values(data).reduce((sum, score) => sum + score, 0) / Object.values(data).length);

    console.log('🔍 [CoverLetterAnalysis] 전체 점수 계산:', {
      analysisResultOverallScore: analysisData?.analysis_result?.overall_score,
      overallScore: analysisData?.overallScore,
      overall_score: analysisData?.overall_score,
      calculatedScore: Math.round(Object.values(data).reduce((sum, score) => sum + score, 0) / Object.values(data).length),
      finalOverallScore: overallScore
    });

    // 분석 요약 가져오기 (실제 데이터 우선)
    const summary = analysisData?.detailedAnalysis || analysisData?.summary || '자소서 분석 결과를 확인할 수 있습니다.';

    // 개선 권장사항 가져오기 (실제 데이터 우선)
    const allRecommendations = analysisData?.analysis_result?.recommendations || analysisData?.recommendations || ['지속적인 성장과 발전을 권장합니다.'];

    console.log('🔍 [CoverLetterAnalysis] 데이터 처리 결과:', {
      추출된점수데이터: data,
      전체점수: overallScore,
      분석요약: summary,
      권장사항: allRecommendations,
      권장사항개수: allRecommendations?.length
    });

    return {
      data,
      overallScore,
      summary,
      allRecommendations
    };
  }, [analysisData]);

  // 메모이제이션된 데이터 구조분해
  const { data, overallScore, summary, allRecommendations } = processedAnalysisData;

  // 🔍 메모이제이션된 레이더 차트 데이터
  const radarData = useMemo(() => {
    const chartData = categories.map(cat => (data[cat.key] || 0));
    console.log('🔍 [CoverLetterAnalysis] 레이더 차트 데이터 (100점 만점):', {
      radarData: chartData,
      원본데이터: categories.map(cat => data[cat.key] || 0),
      카테고리순서: categories.map(cat => cat.key),
      카테고리라벨: categories.map(cat => cat.label)
    });
    return chartData;
  }, [data]);

  // 🔍 메모이제이션된 권장사항 처리
  const processedRecommendations = useMemo(() => {
    // 권장사항이 있는 경우에만 표시 (더미 데이터 제거)
    const recommendations = allRecommendations || [];

    // 권장사항을 문자열로 변환 (객체인 경우 message 속성 사용, 점수는 100점 만점으로 표시)
    const stringRecommendations = recommendations.map(rec => {
      if (typeof rec === 'string') {
        return rec;
      } else if (rec && typeof rec === 'object' && rec.message) {
        // 점수가 포함된 메시지인 경우 100점 만점으로 표시
        if (rec.score && rec.message.includes('/10점')) {
          return rec.message.replace(`(${rec.score}/10점)`, `(${rec.score}점)`);
        }
        return rec.message;
      } else {
        return '지속적인 성장과 발전을 권장합니다.';
      }
    });

    console.log('🔍 [CoverLetterAnalysis] 권장사항 처리:', {
      recommendations원본: recommendations,
      stringRecommendations변환: stringRecommendations,
      권장사항개수: recommendations.length
    });

    return {
      recommendations,
      stringRecommendations
    };
  }, [allRecommendations]);

  const { recommendations, stringRecommendations } = processedRecommendations;

  // 분석 시간 가져오기
  const analyzedAt = analysisData?.analyzed_at ? new Date(analysisData.analyzed_at).toLocaleString('ko-KR') : null;
  console.log('🔍 [CoverLetterAnalysis] 분석 시간:', analyzedAt);

  // 카테고리 클릭 핸들러
  const handleCategoryClick = (categoryKey) => {
    console.log('🔍 [CoverLetterAnalysis] 카테고리 클릭:', categoryKey);
    setSelectedCategory(categoryKey);
  };

  // analysisData가 없으면 로딩 상태 표시 (useMemo 이후에 체크)
  if (!analysisData) {
    console.log('❌ [CoverLetterAnalysis] analysisData가 없음 - 로딩 상태 표시');
    return (
      <Container>
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
<<<<<<< Updated upstream
          <div>분석 데이터를 불러오는 중...</div>
=======
          <div>분석 데이터를 불러오는 중.</div>
>>>>>>> Stashed changes
        </div>
      </Container>
    );
  }

  // 분석 데이터가 있는지 체크 (더 유연하게)
  const hasValidData = analysisData &&
    typeof analysisData === 'object' &&
    Object.keys(analysisData).length > 0 &&
    (analysisData.overallScore || analysisData.technical_suitability || analysisData.detailedAnalysis);

  console.log('🔍 [CoverLetterAnalysis] hasValidData 체크:', {
    hasAnalysisData: !!analysisData,
    isObject: typeof analysisData === 'object',
    hasKeys: analysisData ? Object.keys(analysisData).length > 0 : false,
    hasOverallScore: !!analysisData?.overallScore,
    hasTechnicalSuitability: !!analysisData?.technical_suitability,
    hasDetailedAnalysis: !!analysisData?.detailedAnalysis,
    hasValidData
  });

  if (!hasValidData) {
    console.log('❌ [CoverLetterAnalysis] hasValidData가 false - NoDataMessage 표시');
    return (
      <Container>
        <NoDataMessage>
          자소서 분석 데이터가 없습니다.<br/>
          자소서를 업로드하고 분석을 완료한 후 다시 시도해주세요.
        </NoDataMessage>
      </Container>
    );
  }

  console.log('✅ [CoverLetterAnalysis] 유효한 데이터 확인됨 - 렌더링 시작');

  return (
    <Container>
      {/* 헤더 섹션 */}
      <HeaderSection>
        <HeaderTitle>자소서 분석 결과</HeaderTitle>
        <HeaderSubtitle>
          {applicant && applicant.name ? `${applicant.name}님의 ` : ''}자소서를 종합적으로 분석한 결과입니다
        </HeaderSubtitle>
        {overallScore && (
          <div style={{
            marginTop: '16px',
            textAlign: 'center',
            background: 'rgba(255, 255, 255, 0.15)',
            borderRadius: '12px',
            padding: '16px',
            color: 'white',
            maxWidth: '250px',
            margin: '16px auto 0',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{
              fontSize: '20px',
              fontWeight: '800',
              marginBottom: '4px',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
            }}>
              종합 점수: {Math.round(overallScore)}점
            </div>
            {analyzedAt && (
              <div style={{
                fontSize: '11px',
                opacity: 0.8,
                fontStyle: 'italic'
              }}>
                분석 시간: {analyzedAt}
              </div>
            )}
          </div>
        )}
      </HeaderSection>

<<<<<<< Updated upstream
      {/* 메인 콘텐츠 */}
=======
      {/* 첫 번째 행 - 종합 평가와 항목별 상세 분석 */}
>>>>>>> Stashed changes
      <MainContent>
        {/* 왼쪽 패널 */}
        <LeftPanel>
          {/* 레이더 차트 */}
          <Card>
            <CardTitle>📊 종합 평가</CardTitle>
            <RadarChartSection>
              <CustomRadarChart
                data={categories.map(cat => (data[cat.key] || 0))}
                labels={categories.map(cat => cat.label)}
                maxValue={100}
              />
            </RadarChartSection>
          </Card>
<<<<<<< Updated upstream

          {/* 전체적인 총평 */}
          <Card>
            <CardTitle>📝 전체적인 총평</CardTitle>
            <SummaryText>
              {summary}
            </SummaryText>
          </Card>
=======
>>>>>>> Stashed changes
        </LeftPanel>

        {/* 오른쪽 패널 */}
        <RightPanel>
          {/* 항목별 상세 분석 */}
          <Card>
            <CardTitle>📈 항목별 상세 분석</CardTitle>
            <BarChartContainer>
              {categories.map((category) => (
                <BarItem
                  key={category.key}
                  className={selectedCategory === category.key ? 'active' : ''}
                  onClick={() => handleCategoryClick(category.key)}
                >
                  <BarLabel>{category.label}</BarLabel>
                  <BarContainer>
                    <BarFill
                      style={{
                        width: `${(data[category.key] || 0)}%`
                      }}
                      color={category.color}
                    />
                    <BarScore>{Math.round(data[category.key] || 0)}점</BarScore>
                  </BarContainer>
                </BarItem>
              ))}
            </BarChartContainer>
          </Card>
        </RightPanel>
      </MainContent>

<<<<<<< Updated upstream
=======
      {/* 두 번째 행 - 전체적인 총평과 상세분석 설명을 같은 선상에 배치 */}
      <MainContent>
        {/* 왼쪽 패널 */}
        <LeftPanel>
          {/* 전체적인 총평 */}
          <Card>
            <CardTitle>📝 전체적인 총평</CardTitle>
            <SummaryText>
              {summary}
            </SummaryText>
          </Card>
        </LeftPanel>

        {/* 오른쪽 패널 */}
        <RightPanel>
          {/* 상세분석 설명 */}
          <Card>
            <CardTitle>
              {selectedCategory 
                ? `📋 ${categories.find(cat => cat.key === selectedCategory)?.label} 상세 분석`
                : '📋 상세분석 설명'
              }
            </CardTitle>
            <div style={{
              padding: '20px',
              backgroundColor: 'white',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
              minHeight: '280px',
              maxHeight: '400px',
              overflowY: 'auto'
            }}>
              {selectedCategory ? (
                <div style={{ fontSize: '14px', lineHeight: '1.6', color: '#4b5563' }}>
                  <p style={{ marginBottom: '12px', fontWeight: '600' }}>
                    현재 점수: <span style={{ color: '#3b82f6' }}>{Math.round(data[selectedCategory] || 0)}점</span>
                  </p>
                  <p>
                    {selectedCategory === 'technical_suitability' && (
                      analysisData?.technical_suitability?.feedback ||
                      (data[selectedCategory] >= 80 ?
                        '기술적 역량이 매우 우수합니다. 직무 요구사항과 높은 일치도를 보입니다.' :
                       data[selectedCategory] >= 60 ?
                        '기본적인 기술 역량은 갖추고 있으나, 보완이 필요합니다.' :
                        '기술적 역량 향상이 필요합니다.')
                    )}
                    {selectedCategory === 'job_understanding' && (
                      analysisData?.job_understanding?.feedback ||
                      (data[selectedCategory] >= 80 ?
                        '직무에 대한 이해도가 매우 높습니다.' :
                       data[selectedCategory] >= 60 ?
                        '직무의 기본적인 내용은 파악하고 있으나, 더욱 심화할 필요가 있습니다.' :
                        '직무에 대한 기본적인 이해부터 시작해야 합니다.')
                    )}
                    {selectedCategory === 'growth_potential' && (
                      analysisData?.growth_potential?.feedback ||
                      (data[selectedCategory] >= 80 ?
                        '성장 가능성이 매우 높습니다. 새로운 기술 학습과 변화 적응 능력이 뛰어납니다.' :
                       data[selectedCategory] >= 60 ?
                        '기본적인 성장 가능성은 있으나, 더 적극적인 태도가 필요합니다.' :
                        '성장을 위한 적극적인 노력이 필요합니다.')
                    )}
                    {selectedCategory === 'teamwork_communication' && (
                      analysisData?.teamwork_communication?.feedback ||
                      (data[selectedCategory] >= 80 ?
                        '팀워크와 커뮤니케이션 능력이 매우 우수합니다.' :
                       data[selectedCategory] >= 60 ?
                        '기본적인 협업 능력은 있으나, 개선이 필요합니다.' :
                        '팀워크와 커뮤니케이션 능력 향상이 필요합니다.')
                    )}
                    {selectedCategory === 'motivation_company_fit' && (
                      analysisData?.motivation_company_fit?.feedback ||
                      (data[selectedCategory] >= 80 ?
                        '지원동기와 회사 가치관 부합도가 매우 높습니다.' :
                       data[selectedCategory] >= 60 ?
                        '기본적인 지원동기는 있으나, 회사와의 부합도를 높일 필요가 있습니다.' :
                        '지원동기와 회사 가치관에 대한 이해를 더욱 명확히 해야 합니다.')
                    )}
                  </p>
                </div>
              ) : (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  color: '#475569',
                  lineHeight: '1.6',
                  background: 'white',
                  padding: '20px',
                  borderRadius: '12px',
                  margin: 0,
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                  minHeight: '280px',
                  maxHeight: '400px',
                  overflowY: 'auto'
                }}>
                  <p style={{
                    color: '#6b7280',
                    fontSize: '14px',
                    textAlign: 'center',
                    margin: 0,
                    lineHeight: '1.5'
                  }}>
                    항목을 클릭하여<br/>상세 분석을 확인하세요
                  </p>
                </div>
              )}
            </div>
          </Card>
        </RightPanel>
      </MainContent>

>>>>>>> Stashed changes
      {/* 개선 권장사항 섹션 */}
      {recommendations && recommendations.length > 0 && (
        <FullWidthCard>
          <CardTitle>
            💡 개선 권장사항
          </CardTitle>
          <div style={{
            padding: '24px',
            backgroundColor: '#fafbfc',
            borderRadius: '16px',
            border: '1px solid #e2e8f0',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
          }}>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px'
            }}>
              {stringRecommendations.length > 0 ? (
                stringRecommendations.map((recommendation, index) => (
                  <div key={index} style={{
                    padding: '20px',
                    backgroundColor: 'white',
                    borderRadius: '12px',
                    border: '1px solid #e2e8f0',
                    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                    transition: 'all 0.2s ease',
                    position: 'relative'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '12px'
                    }}>
                      <div style={{
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        backgroundColor: '#3b82f6',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        marginTop: '2px'
                      }}>
                        <span style={{
                          color: 'white',
                          fontWeight: '700',
                          fontSize: '12px'
                        }}>{index + 1}</span>
                      </div>
                      <span style={{
                        color: '#374151',
                        lineHeight: '1.6',
                        fontSize: '15px',
                        fontWeight: '500'
                      }}>{recommendation}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div style={{
                  padding: '20px',
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                  textAlign: 'center',
                  color: '#6b7280'
                }}>
                  분석 결과에 따른 구체적인 개선 권장사항이 없습니다.
                </div>
              )}
            </div>
          </div>
        </FullWidthCard>
      )}

<<<<<<< Updated upstream
      {/* 상세 설명 섹션 */}
      {selectedCategory && (
        <Card style={{ marginTop: '24px' }}>
          <CardTitle>
            {categories.find(cat => cat.key === selectedCategory)?.label} 상세 분석
          </CardTitle>
          <div style={{ fontSize: '14px', lineHeight: '1.6', color: '#4b5563' }}>
            <p style={{ marginBottom: '12px', fontWeight: '600' }}>
              현재 점수: <span style={{ color: '#3b82f6' }}>{Math.round(data[selectedCategory] || 0)}점</span>
            </p>
            <p>
              {selectedCategory === 'technical_suitability' && (
                analysisData?.technical_suitability?.feedback ||
                (data[selectedCategory] >= 80 ?
                  '기술적 역량이 매우 우수합니다. 직무 요구사항과 높은 일치도를 보입니다.' :
                 data[selectedCategory] >= 60 ?
                  '기본적인 기술 역량은 갖추고 있으나, 보완이 필요합니다.' :
                  '기술적 역량 향상이 필요합니다.')
              )}
              {selectedCategory === 'job_understanding' && (
                analysisData?.job_understanding?.feedback ||
                (data[selectedCategory] >= 80 ?
                  '직무에 대한 이해도가 매우 높습니다.' :
                 data[selectedCategory] >= 60 ?
                  '직무의 기본적인 내용은 파악하고 있으나, 더욱 심화할 필요가 있습니다.' :
                  '직무에 대한 기본적인 이해부터 시작해야 합니다.')
              )}
              {selectedCategory === 'growth_potential' && (
                analysisData?.growth_potential?.feedback ||
                (data[selectedCategory] >= 80 ?
                  '성장 가능성이 매우 높습니다. 새로운 기술 학습과 변화 적응 능력이 뛰어납니다.' :
                 data[selectedCategory] >= 60 ?
                  '기본적인 성장 가능성은 있으나, 더 적극적인 태도가 필요합니다.' :
                  '성장을 위한 적극적인 노력이 필요합니다.')
              )}
              {selectedCategory === 'teamwork_communication' && (
                analysisData?.teamwork_communication?.feedback ||
                (data[selectedCategory] >= 80 ?
                  '팀워크와 커뮤니케이션 능력이 매우 우수합니다.' :
                 data[selectedCategory] >= 60 ?
                  '기본적인 협업 능력은 있으나, 개선이 필요합니다.' :
                  '팀워크와 커뮤니케이션 능력 향상이 필요합니다.')
              )}
              {selectedCategory === 'motivation_company_fit' && (
                analysisData?.motivation_company_fit?.feedback ||
                (data[selectedCategory] >= 80 ?
                  '지원동기와 회사 가치관 부합도가 매우 높습니다.' :
                 data[selectedCategory] >= 60 ?
                  '기본적인 지원동기는 있으나, 회사와의 부합도를 높일 필요가 있습니다.' :
                  '지원동기와 회사 가치관에 대한 이해를 더욱 명확히 해야 합니다.')
              )}
            </p>
          </div>
        </Card>
      )}
=======
      
>>>>>>> Stashed changes
    </Container>
  );
};

export default CoverLetterAnalysis;
