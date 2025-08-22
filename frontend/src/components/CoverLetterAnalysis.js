import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 24px;
  text-align: center;
`;

const AnalysisGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 32px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 24px;
  }
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
`;

const RadarChartContainer = styled.div`
  position: relative;
  width: 350px;
  height: 350px;
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
  min-width: 120px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
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
  min-width: 60px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: #333;
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
  font-size: 14px;
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

  // 분석 데이터가 없을 경우 기본값 설정
  const defaultData = {
    technical_suitability: 75,
    job_understanding: 80,
    growth_potential: 85,
    teamwork_communication: 70,
    motivation_company_fit: 90
  };

  // analysisData가 비어있거나 null인 경우 기본값 사용
  const data = analysisData && Object.keys(analysisData).length > 0 ? analysisData : defaultData;

  // 레이더차트 데이터 생성
  const generateRadarData = () => {
    const centerX = 175;
    const centerY = 175;
    const radius = 90;  // 차트 반지름을 줄여서 공간 확보
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
        labelRadius = radius + 25;  // 간격을 25로 줄여서 차트에 붙임
      } else {
        labelRadius = radius + 50;  // 다른 항목들은 기존 간격 유지
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
      const radius = (90 / 5) * i;
      circles.push(radius);
    }
    return circles;
  };

  // 축 생성
  const generateAxes = () => {
    const axes = [];
    categories.forEach((_, index) => {
      const angle = (index * 2 * Math.PI) / categories.length;
      const x = 175 + 90 * Math.cos(angle);
      const y = 175 + 90 * Math.sin(angle);
      axes.push({ x1: 175, y1: 175, x2: x, y2: y });
    });
    return axes;
  };

  // 총평 생성
  const generateSummary = () => {
    const scores = Object.values(data);
    const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    
    let summary = '';
    
    if (average >= 90) {
      summary = '전체적으로 매우 우수한 자소서입니다. 모든 항목에서 높은 점수를 받았으며, 특히 지원동기와 회사 가치관 부합도가 뛰어납니다. 기술적 역량과 직무 이해도도 충분히 검증되었습니다.';
    } else if (average >= 80) {
      summary = '전반적으로 양호한 자소서입니다. 기술적 적합성과 성장 가능성이 돋보이며, 팀워크와 커뮤니케이션 능력도 인정받을 수 있습니다. 다만 일부 항목에서 개선의 여지가 있습니다.';
    } else if (average >= 70) {
      summary = '기본적인 요구사항은 충족하는 자소서입니다. 직무 이해도와 지원동기는 적절하나, 기술적 역량이나 구체적인 성과 제시에서 보완이 필요합니다.';
    } else {
      summary = '전반적으로 보완이 필요한 자소서입니다. 기본적인 내용은 포함되어 있으나, 구체적인 경험이나 성과 제시가 부족하며, 직무에 대한 이해도 향상이 필요합니다.';
    }
    
    return summary;
  };

  // 카테고리 클릭 핸들러
  const handleCategoryClick = (categoryKey) => {
    setSelectedCategory(categoryKey);
  };

  const { points, labels } = generateRadarData();
  const gridCircles = generateGridCircles();
  const axes = generateAxes();

  // 분석 데이터가 없거나 모든 값이 0인 경우 체크
  const hasValidData = analysisData && 
    Object.values(analysisData).some(value => value > 0);

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
      
      <AnalysisGrid>
        {/* 레이더차트 섹션 */}
        <RadarChartSection>
          <RadarChartTitle>종합 평가</RadarChartTitle>
          <RadarChartContainer>
            <RadarChart viewBox="0 0 350 350">
              {/* 그리드 원 */}
              {gridCircles.map((radius, index) => (
                <RadarGrid key={index}>
                  <circle
                    cx="175"
                    cy="175"
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
                <polygon points={points.join(' ')} />
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
                      />
                    </RadarPoint>
                  );
                })}
              </RadarData>
               
              {/* 라벨 */}
              {labels.map((label, index) => (
                <g key={index}>
                  {/* 메인 텍스트 - 배경 없이 직접 표시 */}
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
                      // 긴 텍스트는 줄바꿔서 표시 - 간격을 더 넓게
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
                      // 짧은 텍스트는 한 줄로 표시
                      label.text
                    )}
                  </text>
                </g>
              ))}
            </RadarChart>
          </RadarChartContainer>
        </RadarChartSection>

        {/* 총평 섹션 */}
        <div>
          <SummarySection>
            <SummaryTitle>
              📊 전체적인 총평
            </SummaryTitle>
            <SummaryText>
              {generateSummary()}
            </SummaryText>
          </SummarySection>
        </div>
      </AnalysisGrid>

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
                <h5 style={{ fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>지원자의 기술 스택이 직무 요구사항과 얼마나 일치하는지 평가</li>
                  <li>프로젝트에서 해당 기술을 사용한 경험과 깊이를 고려</li>
                  <li>문제 해결 과정에서의 기술적 창의성 반영</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {data[selectedCategory] >= 80 ? 
                    '기술적 역량이 매우 우수합니다. 직무 요구사항과 높은 일치도를 보이며, 프로젝트 경험과 기술적 창의성이 충분히 검증되었습니다.' :
                   data[selectedCategory] >= 60 ? 
                    '기본적인 기술 역량은 갖추고 있으나, 직무 요구사항과의 일치도나 프로젝트 경험에서 보완이 필요합니다.' :
                    '기술적 역량 향상이 필요합니다. 직무 요구사항에 맞는 기술 스택 학습과 프로젝트 경험 축적이 필요합니다.'}
                </p>
              </div>
            )}
            {selectedCategory === 'job_understanding' && (
              <div>
                <h5 style={{ fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>지원자가 해당 직무의 주요 역할과 책임을 명확히 이해하고 있는지 평가</li>
                  <li>직무 관련 산업 트렌드 또는 회사 제품/서비스 이해 여부 반영</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {data[selectedCategory] >= 80 ? 
                    '직무에 대한 이해도가 매우 높습니다. 주요 역할과 책임을 명확히 파악하고 있으며, 산업 트렌드와 회사 제품/서비스에 대한 깊은 이해를 보여줍니다.' :
                   data[selectedCategory] >= 60 ? 
                    '직무의 기본적인 내용은 파악하고 있으나, 세부적인 역할과 책임, 산업 트렌드에 대한 이해를 더욱 심화할 필요가 있습니다.' :
                    '직무에 대한 기본적인 이해부터 시작해야 합니다. 주요 역할과 책임, 산업 동향에 대한 학습이 필요합니다.'}
                </p>
              </div>
            )}
            {selectedCategory === 'growth_potential' && (
              <div>
                <h5 style={{ fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>새로운 기술을 학습한 경험</li>
                  <li>변화에 빠르게 적응한 사례</li>
                  <li>자기 주도적 학습 태도</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {data[selectedCategory] >= 80 ? 
                    '성장 가능성이 매우 높습니다. 새로운 기술 학습 경험이 풍부하고, 변화에 빠르게 적응하며, 자기 주도적 학습 태도가 뛰어납니다.' :
                   data[selectedCategory] >= 60 ? 
                    '기본적인 성장 가능성은 있으나, 새로운 기술 학습이나 변화 적응에서 더 적극적인 태도가 필요합니다.' :
                    '성장을 위한 적극적인 노력이 필요합니다. 새로운 기술 학습과 변화 적응, 자기 주도적 학습 태도 개발이 필요합니다.'}
                </p>
              </div>
            )}
            {selectedCategory === 'teamwork_communication' && (
              <div>
                <h5 style={{ fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>협업 경험</li>
                  <li>갈등 해결 과정</li>
                  <li>명확한 의사소통 능력</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {data[selectedCategory] >= 80 ? 
                    '팀워크와 커뮤니케이션 능력이 매우 우수합니다. 풍부한 협업 경험과 갈등 해결 능력, 명확한 의사소통 능력을 보여줍니다.' :
                   data[selectedCategory] >= 60 ? 
                    '기본적인 협업 능력은 갖추고 있으나, 갈등 해결이나 의사소통에서 더 나은 방법을 학습할 필요가 있습니다.' :
                    '팀워크와 커뮤니케이션 능력 향상이 필요합니다. 협업 경험 축적과 갈등 해결, 의사소통 능력 개발이 필요합니다.'}
                </p>
              </div>
            )}
            {selectedCategory === 'motivation_company_fit' && (
              <div>
                <h5 style={{ fontWeight: '600', marginBottom: '12px', color: '#333' }}>평가 기준</h5>
                <ul style={{ marginBottom: '16px', paddingLeft: '20px', lineHeight: '1.6' }}>
                  <li>지원 동기의 진정성</li>
                  <li>회사의 미션/비전과의 일치성</li>
                  <li>장기적 기여 가능성</li>
                </ul>
                <p style={{ marginBottom: '12px' }}>
                  <strong>현재 점수: {data[selectedCategory]}점</strong>
                </p>
                <p style={{ lineHeight: '1.6' }}>
                  {data[selectedCategory] >= 80 ? 
                    '지원 동기가 매우 진정성 있고, 회사의 미션/비전과 높은 일치성을 보입니다. 장기적으로 회사에 크게 기여할 수 있는 잠재력을 가지고 있습니다.' :
                   data[selectedCategory] >= 60 ? 
                    '기본적인 지원 동기는 있으나, 회사의 미션/비전과의 일치성이나 장기적 기여 가능성에서 더 구체적인 비전이 필요합니다.' :
                    '지원 동기와 회사 가치관 부합도 향상이 필요합니다. 회사의 미션/비전에 대한 이해와 장기적 기여 방향에 대한 명확한 비전이 필요합니다.'}
                </p>
              </div>
            )}
          </DetailContent>
        </DetailSection>
      )}
    </Container>
  );
};

export default CoverLetterAnalysis;
