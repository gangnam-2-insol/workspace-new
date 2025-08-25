import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-width: 1200px;
  width: 100%;

  @keyframes fadeInScale {
    0% {
      opacity: 0;
      transform: scale(0.8);
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

const Title = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 24px;
  text-align: center;
`;

const AnalysisGrid = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
`;

const RadarChartSection = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const RadarChartTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
  animation: fadeInScale 1s ease-out forwards;
`;

const RadarChartContainer = styled.div`
  position: relative;
  width: 450px;
  height: 450px;
  margin: 0 auto;
`;

const RadarChart = styled.svg`
  width: 100%;
  height: 100%;
`;

const RadarGrid = styled.g`
  stroke: #e0e0e0;
  stroke-width: 1;
  fill: none;
`;

const RadarAxis = styled.g`
  stroke: #666;
  stroke-width: 2;
`;

const RadarData = styled.g`
  fill: rgba(59, 130, 246, 0.3);
  stroke: #3b82f6;
  stroke-width: 2;
`;

const RadarPoint = styled.g`
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: scale(1.1);
  }
`;

const RadarLabel = styled.text`
  font-size: 11px;
  font-weight: 500;
  fill: #333;
  text-anchor: middle;
  dominant-baseline: middle;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;

  &:hover {
    fill: #3b82f6;
    font-weight: 600;
    font-size: 12px;
  }
`;

const SummarySection = styled.div`
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid #3b82f6;
`;

const SummaryTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SummaryText = styled.p`
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  background: white;
  padding: 16px;
  border-radius: 8px;
  margin: 0;
`;

const BarChartSection = styled.div`
  margin-top: 32px;
`;

const BarChartTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
  text-align: center;
`;

const BarChartContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const BarItem = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
  transition: all 0.2s;
  cursor: pointer;

  &:hover {
    background: #e9ecef;
    transform: translateX(4px);
  }

  &.active {
    background: #e3f2fd;
    border-left-color: #1976d2;
  }
`;

const BarLabel = styled.div`
  width: 200px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  flex-shrink: 0;
`;

const BarContainer = styled.div`
  flex: 1;
  height: 24px;
  background: #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
`;

const BarFill = styled.div`
  height: 100%;
  border-radius: 12px;
  transition: width 0.8s ease-out;
  position: relative;
  background: ${props => props.color || 'linear-gradient(90deg, #3b82f6, #1d4ed8)'};
`;

const BarValue = styled.div`
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
`;

const BarScore = styled.div`
  width: 60px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  flex-shrink: 0;
`;

const DetailSection = styled.div`
  margin-top: 32px;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
`;

const DetailTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #3b82f6;
`;

const DetailContent = styled.div`
  font-size: 16px;
  color: #666;
  line-height: 1.6;
`;

const NoDataMessage = styled.div`
  text-align: center;
  padding: 48px;
  color: #666;
  font-size: 16px;
`;

const CoverLetterAnalysis = ({ analysisData }) => {
  const [selectedCategory, setSelectedCategory] = useState(null);

  // 자소서 분석 카테고리 정의
  const categories = [
    { key: 'technical_suitability', label: '기술적합성', color: '#3b82f6' },
    { key: 'job_understanding', label: '직무이해도', color: '#10b981' },
    { key: 'growth_potential', label: '성장 가능성', color: '#f59e0b' },
    { key: 'teamwork_communication', label: '팀워크 및 커뮤니케이션', color: '#8b5cf6' },
    { key: 'motivation_company_fit', label: '지원동기/회사 가치관 부합도', color: '#ef4444' }
  ];

  // 새로운 분석 데이터 구조에서 점수 추출
  const extractScores = (analysisData) => {
    if (!analysisData || typeof analysisData !== 'object') {
      return {
        technical_suitability: 75,
        job_understanding: 80,
        growth_potential: 85,
        teamwork_communication: 70,
        motivation_company_fit: 90
      };
    }

    // 새로운 구조: analysisData.technical_suitability.score 형태
    if (analysisData.technical_suitability && typeof analysisData.technical_suitability.score === 'number') {
      return {
        technical_suitability: analysisData.technical_suitability.score,
        job_understanding: analysisData.job_understanding?.score || 80,
        growth_potential: analysisData.growth_potential?.score || 85,
        teamwork_communication: analysisData.teamwork_communication?.score || 70,
        motivation_company_fit: analysisData.motivation_company_fit?.score || 90
      };
    }

    // 기존 구조: analysisData.technical_suitability 형태
    return {
      technical_suitability: analysisData.technical_suitability || 75,
      job_understanding: analysisData.job_understanding || 80,
      growth_potential: analysisData.growth_potential || 85,
      teamwork_communication: analysisData.teamwork_communication || 70,
      motivation_company_fit: analysisData.motivation_company_fit || 90
    };
  };

  // 분석 데이터에서 점수 추출
  const data = extractScores(analysisData);

  // 전체 점수 계산
  const overallScore = analysisData?.overall_score ||
    Math.round(Object.values(data).reduce((sum, score) => sum + score, 0) / Object.values(data).length);

  // 분석 요약 가져오기
  const summary = analysisData?.summary || '자소서 분석 결과를 확인할 수 있습니다.';

  // 개선 권장사항 가져오기 (항상 최대 2개로 제한)
  const allRecommendations = analysisData?.recommendations || ['지속적인 성장과 발전을 권장합니다.'];
  // slice(0, 2)를 사용하여 항상 최대 2개만 표시
  const recommendations = allRecommendations.slice(0, 2);
  
  // 권장사항이 2개 미만인 경우 기본 권장사항으로 채움
  while (recommendations.length < 2) {
    recommendations.push('지속적인 성장과 발전을 권장합니다.');
  }

  // 분석 시간 가져오기
  const analyzedAt = analysisData?.analyzed_at ? new Date(analysisData.analyzed_at).toLocaleString('ko-KR') : null;

  // 레이더차트 데이터 생성
  const generateRadarData = () => {
    const centerX = 225;
    const centerY = 225;
    const radius = 120;  // 차트 반지름을 키워서 더 큰 차트 생성
    const points = [];
    const labels = [];

    categories.forEach((category, index) => {
      const angle = (index * 2 * Math.PI) / categories.length;
      const score = data[category.key] || 0;
      const normalizedRadius = (score / 100) * radius;

      const x = centerX + normalizedRadius * Math.cos(angle);
      const y = centerY + normalizedRadius * Math.sin(angle);

      points.push(`${x},${y}`);

      // 라벨 위치 (바깥쪽) - 직무이해도만 차트에 좀 붙여서 간격 조정
      let labelRadius;
      if (index === 2) {  // 직무이해도 (3번째 항목, 인덱스 2)
        labelRadius = radius + 35;  // 간격을 35로 조정
      } else {
        labelRadius = radius + 70;  // 다른 항목들은 간격 조정
      }

      const labelX = centerX + labelRadius * Math.cos(angle);
      const labelY = centerY + labelRadius * Math.sin(angle);

      // 텍스트를 줄바꿔서 처리
      const textLines = category.label.split(' ');

      labels.push({
        x: labelX,
        y: labelY,
        text: category.label,
        textLines: textLines,
        category: category.key,
        angle: angle
      });
    });

    return { points, labels };
  };

  // 그리드 원 생성
  const generateGridCircles = () => {
    const circles = [];
    for (let i = 1; i <= 5; i++) {
      const radius = (120 / 5) * i;
      circles.push(radius);
    }
    return circles;
  };

  // 축 생성
  const generateAxes = () => {
    const axes = [];
    categories.forEach((_, index) => {
      const angle = (index * 2 * Math.PI) / categories.length;
      const x = 225 + 120 * Math.cos(angle);
      const y = 225 + 120 * Math.sin(angle);
      axes.push({ x1: 225, y1: 225, x2: x, y2: y });
    });
    return axes;
  };

  // 카테고리 클릭 핸들러
  const handleCategoryClick = (categoryKey) => {
    setSelectedCategory(categoryKey);
  };

  const { points, labels } = generateRadarData();
  const gridCircles = generateGridCircles();
  const axes = generateAxes();

  // 분석 데이터가 있는지 체크
  const hasValidData = analysisData &&
    typeof analysisData === 'object' &&
    Object.keys(analysisData).length > 0 &&
    analysisData.technical_suitability &&
    analysisData.technical_suitability.score;

  if (!hasValidData) {
    return (
      <Container>
        <NoDataMessage>
          자소서 분석 데이터가 없습니다.<br/>
          자소서를 업로드하고 분석을 완료한 후 다시 시도해주세요.
        </NoDataMessage>
      </Container>
    );
  }

  return (
    <Container>
             <Title>자소서 분석 결과</Title>

       {/* 새로운 레이아웃: 그래프(왼쪽) + 총평/권장사항(오른쪽) */}
       <div style={{
         display: 'grid',
         gridTemplateColumns: '1fr 1fr',
         gap: '32px',
         marginBottom: '32px',
         width: '100%',
         maxWidth: '1200px',
         margin: '0 auto 32px auto'
       }}>
         {/* 왼쪽: 레이더차트 */}
         <div>
           <RadarChartTitle>종합 평가</RadarChartTitle>
           <RadarChartContainer>
             <RadarChart viewBox="0 0 450 450">
                               {/* 그리드 원 */}
                {gridCircles.map((radius, index) => (
                  <RadarGrid key={index}>
                    <circle
                      cx="225"
                      cy="225"
                      r={radius}
                      fill="none"
                    />
                  </RadarGrid>
                ))}

                {/* 축 */}
                {axes.map((axis, index) => (
                  <RadarAxis key={index}>
                    <line
                      x1={axis.x1}
                      y1={axis.y1}
                      x2={axis.x2}
                      y2={axis.y2}
                    />
                  </RadarAxis>
                ))}

               {/* 데이터 영역 */}
               <RadarData>
                 <polygon
                   points={points.join(' ')}
                   style={{
                     animation: 'fadeInScale 1.5s ease-out forwards'
                   }}
                 />
               </RadarData>

               {/* 데이터 포인트 */}
               <RadarData>
                 {points.map((point, index) => {
                   const [x, y] = point.split(',').map(Number);
                   return (
                     <RadarPoint key={index}>
                       <circle
                         cx={x}
                         cy={y}
                         r="4"
                         fill="#3b82f6"
                         style={{
                           animation: `fadeInPoint 0.8s ease-out ${index * 0.1}s forwards`,
                           opacity: 0
                         }}
                       />
                     </RadarPoint>
                   );
                 })}
               </RadarData>

               {/* 라벨 */}
               {labels.map((label, index) => (
                 <g key={index}>
                   <text
                     x={label.x}
                     y={label.y}
                     textAnchor="middle"
                     dominantBaseline="middle"
                     fontSize="13"
                     fontWeight="600"
                     fill="#333"
                     cursor="pointer"
                     onClick={() => handleCategoryClick(label.category)}
                     style={{ userSelect: 'none' }}
                   >
                     {label.textLines.length > 1 ? (
                       label.textLines.map((line, lineIndex) => (
                         <tspan
                           key={lineIndex}
                           x={label.x}
                           dy={lineIndex === 0 ? "-1.0em" : "1.6em"}
                         >
                           {line}
                         </tspan>
                       ))
                     ) : (
                       label.text
                     )}
                   </text>
                 </g>
               ))}
             </RadarChart>
           </RadarChartContainer>
         </div>

         {/* 오른쪽: 총평 및 권장사항 */}
         <div style={{
           display: 'flex',
           flexDirection: 'column',
           gap: '24px'
         }}>
        {/* 전체적인 총평 */}
        <SummarySection>
          <SummaryTitle>
            📊 전체적인 총평
          </SummaryTitle>
          <SummaryText>
            {summary}
          </SummaryText>
          {overallScore && (
            <div style={{ marginTop: '16px', textAlign: 'center' }}>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#3b82f6',
                marginBottom: '8px'
              }}>
                종합 점수: {overallScore}점
              </div>
              {analyzedAt && (
                <div style={{
                  fontSize: '12px',
                  color: '#666',
                  fontStyle: 'italic'
                }}>
                  분석 시간: {analyzedAt}
                </div>
              )}
            </div>
          )}
        </SummarySection>

                 {/* 개선 권장사항 (항상 최대 2개 표시) */}
         {recommendations && recommendations.length > 0 && (
           <SummarySection>
             <SummaryTitle>
               💡 개선 권장사항
             </SummaryTitle>
             <div style={{
               padding: '16px',
               backgroundColor: '#f8f9fa',
               borderRadius: '12px',
               border: '2px solid #e9ecef',
               boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
             }}>
               <div style={{
                 display: 'flex',
                 flexDirection: 'column',
                 gap: '16px'
               }}>
                 {recommendations.map((recommendation, index) => (
                   <div key={index} style={{
                     padding: '16px',
                     backgroundColor: 'white',
                     borderRadius: '8px',
                     borderLeft: '4px solid #3b82f6',
                     boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                     transition: 'all 0.2s ease'
                   }}>
                     <div style={{
                       display: 'flex',
                       alignItems: 'flex-start',
                       gap: '12px'
                     }}>
                       <span style={{
                         color: '#3b82f6',
                         fontWeight: '700',
                         fontSize: '16px',
                         lineHeight: '1.4'
                       }}>•</span>
                       <span style={{
                         color: '#333',
                         lineHeight: '1.6',
                         fontSize: '14px'
                       }}>{recommendation}</span>
                     </div>
                   </div>
                 ))}
               </div>
             </div>
           </SummarySection>
         )}
         </div>
       </div>

      {/* 막대 그래프 섹션 */}
      <BarChartSection>
        <BarChartTitle>항목별 상세 분석</BarChartTitle>
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
                    width: `${data[category.key] || 0}%`
                  }}
                  color={category.color}
                />
                <BarValue>{data[category.key] || 0}%</BarValue>
              </BarContainer>
              <BarScore>{data[category.key] || 0}점</BarScore>
            </BarItem>
          ))}
        </BarChartContainer>
      </BarChartSection>

      {/* 상세 설명 섹션 */}
      {selectedCategory && (
        <DetailSection>
          <DetailTitle>
            {categories.find(cat => cat.key === selectedCategory)?.label} 상세 분석
          </DetailTitle>
          <DetailContent>
            {selectedCategory === 'technical_suitability' && (
              <div>
                <h5 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>지원자의 기술 스택이 직무 요구사항과 얼마나 일치하는지 평가</li>
                  <li>프로젝트에서 해당 기술을 사용한 경험과 깊이를 고려</li>
                  <li>문제 해결 과정에서의 기술적 창의성 반영</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {analysisData?.technical_suitability?.feedback ||
                    (data[selectedCategory] >= 80 ?
                      '기술적 역량이 매우 우수합니다. 직무 요구사항과 높은 일치도를 보이며, 프로젝트 경험과 기술적 창의성이 충분히 검증되었습니다.' :
                     data[selectedCategory] >= 60 ?
                      '기본적인 기술 역량은 갖추고 있으나, 직무 요구사항과의 일치도나 프로젝트 경험에서 보완이 필요합니다.' :
                      '기술적 역량 향상이 필요합니다. 직무 요구사항에 맞는 기술 스택 학습과 프로젝트 경험 축적이 필요합니다.')}
                </p>
                {analysisData?.technical_suitability?.details && (
                  <div style={{ marginTop: '16px', padding: '12px 0', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                    <h6 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>상세 분석</h6>
                    <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.6' }}>
                      <li>기술 스택 일치도: {analysisData.technical_suitability.details.tech_stack_alignment}점</li>
                      <li>프로젝트 경험: {analysisData.technical_suitability.details.project_experience}점</li>
                      <li>문제 해결 창의성: {analysisData.technical_suitability.details.problem_solving_creativity}점</li>
                    </ul>
                  </div>
                )}
              </div>
            )}
            {selectedCategory === 'job_understanding' && (
              <div>
                <h5 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>지원자가 해당 직무의 주요 역할과 책임을 명확히 이해하고 있는지 평가</li>
                  <li>직무 관련 산업 트렌드 또는 회사 제품/서비스 이해 여부 반영</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {analysisData?.job_understanding?.feedback ||
                    (data[selectedCategory] >= 80 ?
                      '직무에 대한 이해도가 매우 높습니다. 주요 역할과 책임을 명확히 파악하고 있으며, 산업 트렌드와 회사 제품/서비스에 대한 깊은 이해를 보여줍니다.' :
                     data[selectedCategory] >= 60 ?
                      '직무의 기본적인 내용은 파악하고 있으나, 세부적인 역할과 책임, 산업 트렌드에 대한 이해를 더욱 심화할 필요가 있습니다.' :
                      '직무에 대한 기본적인 이해부터 시작해야 합니다. 주요 역할과 책임, 산업 동향에 대한 학습이 필요합니다.')}
                </p>
                {analysisData?.job_understanding?.details && (
                  <div style={{ marginTop: '16px', padding: '12px 0', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                    <h6 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>상세 분석</h6>
                    <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.6' }}>
                      <li>역할 명확성: {analysisData.job_understanding.details.role_clarity}점</li>
                      <li>산업 트렌드: {analysisData.job_understanding.details.industry_trends}점</li>
                      <li>회사 제품 이해: {analysisData.job_understanding.details.company_products}점</li>
                    </ul>
                  </div>
                )}
              </div>
            )}
            {selectedCategory === 'growth_potential' && (
              <div>
                <h5 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>새로운 기술을 학습한 경험</li>
                  <li>변화에 빠르게 적응한 사례</li>
                  <li>자기 주도적 학습 태도</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {analysisData?.growth_potential?.feedback ||
                    (data[selectedCategory] >= 80 ?
                      '성장 가능성이 매우 높습니다. 새로운 기술 학습 경험이 풍부하고, 변화에 빠르게 적응하며, 자기 주도적 학습 태도가 뛰어납니다.' :
                     data[selectedCategory] >= 60 ?
                      '기본적인 성장 가능성은 있으나, 새로운 기술 학습이나 변화 적응에서 더 적극적인 태도가 필요합니다.' :
                      '성장을 위한 적극적인 노력이 필요합니다. 새로운 기술 학습과 변화 적응, 자기 주도적 학습 태도 개발이 필요합니다.')}
                </p>
                {analysisData?.growth_potential?.details && (
                  <div style={{ marginTop: '16px', padding: '12px 0', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                    <h6 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>상세 분석</h6>
                    <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.6' }}>
                      <li>새 기술 학습: {analysisData.growth_potential.details.new_tech_learning}점</li>
                      <li>적응력: {analysisData.growth_potential.details.adaptability}점</li>
                      <li>자기 주도 학습: {analysisData.growth_potential.details.self_driven_learning}점</li>
                    </ul>
                  </div>
                )}
              </div>
            )}
            {selectedCategory === 'teamwork_communication' && (
              <div>
                <h5 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>협업 경험</li>
                  <li>갈등 해결 과정</li>
                  <li>명확한 의사소통 능력</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {analysisData?.teamwork_communication?.feedback ||
                    (data[selectedCategory] >= 80 ?
                      '팀워크와 커뮤니케이션 능력이 매우 우수합니다. 풍부한 협업 경험과 갈등 해결 능력, 명확한 의사소통 능력을 보여줍니다.' :
                     data[selectedCategory] >= 60 ?
                      '기본적인 협업 능력은 갖추고 있으나, 갈등 해결이나 의사소통에서 더 나은 방법을 학습할 필요가 있습니다.' :
                      '팀워크와 커뮤니케이션 능력 향상이 필요합니다. 협업 경험 축적과 갈등 해결, 의사소통 능력 개발이 필요합니다.')}
                </p>
                {analysisData?.teamwork_communication?.details && (
                  <div style={{ marginTop: '16px', padding: '12px 0', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                    <h6 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>상세 분석</h6>
                    <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.6' }}>
                      <li>협업 경험: {analysisData.teamwork_communication.details.collaboration_experience}점</li>
                      <li>갈등 해결: {analysisData.teamwork_communication.details.conflict_resolution}점</li>
                      <li>의사소통 명확성: {analysisData.teamwork_communication.details.communication_clarity}점</li>
                    </ul>
                  </div>
                )}
              </div>
            )}
            {selectedCategory === 'motivation_company_fit' && (
              <div>
                <h5 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>지원 동기의 진정성</li>
                  <li>회사의 미션/비전과의 일치성</li>
                  <li>장기적 기여 가능성</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {analysisData?.motivation_company_fit?.feedback ||
                    (data[selectedCategory] >= 80 ?
                      '지원 동기가 매우 진정성 있고, 회사의 미션/비전과 높은 일치성을 보입니다. 장기적으로 회사에 크게 기여할 수 있는 잠재력을 가지고 있습니다.' :
                     data[selectedCategory] >= 60 ?
                      '기본적인 지원 동기는 있으나, 회사의 미션/비전과의 일치성이나 장기적 기여 가능성에서 더 구체적인 비전이 필요합니다.' :
                      '지원 동기와 회사 가치관 부합도 향상이 필요합니다. 회사의 미션/비전에 대한 이해와 장기적 기여 방향에 대한 명확한 비전이 필요합니다.')}
                </p>
                {analysisData?.motivation_company_fit?.details && (
                  <div style={{ marginTop: '16px', padding: '12px 0', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                    <h6 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#333' }}>상세 분석</h6>
                    <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.6' }}>
                      <li>동기 진정성: {analysisData.motivation_company_fit.details.motivation_authenticity}점</li>
                      <li>미션/비전 일치: {analysisData.motivation_company_fit.details.mission_vision_alignment}점</li>
                      <li>장기적 기여: {analysisData.motivation_company_fit.details.long_term_contribution}점</li>
                    </ul>
                  </div>
                )}
              </div>
            )}
          </DetailContent>
        </DetailSection>
      )}
    </Container>
  );
};

export default CoverLetterAnalysis;
