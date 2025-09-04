import React from 'react';
import styled from 'styled-components';

const RadarContainer = styled.div`
  width: 100%;
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
`;

const RadarSVG = styled.svg`
  width: 100%;
  height: 100%;
`;

const GridCircle = styled.circle`
  fill: none;
  stroke: #e9ecef;
  stroke-width: 1;
`;

const GridLine = styled.line`
  stroke: #e9ecef;
  stroke-width: 1;
`;

const DataPolygon = styled.polygon`
  fill: rgba(59, 130, 246, 0.2);
  stroke: #3b82f6;
  stroke-width: 3;
  stroke-linejoin: round;
`;

const DataPoint = styled.circle`
  fill: #3b82f6;
  stroke: white;
  stroke-width: 2;
  r: 5;
`;

const LabelText = styled.text`
  font-size: 12px;
  font-weight: 600;
  fill: #495057;
  text-anchor: middle;
  dominant-baseline: middle;
`;

const TickText = styled.text`
  font-size: 10px;
  fill: #666;
  text-anchor: middle;
  dominant-baseline: middle;
`;

const CustomRadarChart = ({ data, labels, maxValue = 10 }) => {
  const centerX = 160;
  const centerY = 160;
  const radius = 120;
  const numAxes = labels.length;

  // 각 축의 각도 계산 (12시 방향부터 시계방향)
  const getAngle = (index) => {
    return (index * 360 / numAxes - 90) * (Math.PI / 180);
  };

  // 좌표 계산 함수
  const getCoordinates = (angle, distance) => {
    const x = centerX + Math.cos(angle) * distance;
    const y = centerY + Math.sin(angle) * distance;
    return { x, y };
  };

  // 그리드 원 생성
  const gridCircles = [];
  for (let i = 1; i <= 5; i++) {
    const gridRadius = (radius * i) / 5;
    gridCircles.push(
      <GridCircle
        key={i}
        cx={centerX}
        cy={centerY}
        r={gridRadius}
      />
    );
  }

  // 그리드 라인 생성
  const gridLines = [];
  for (let i = 0; i < numAxes; i++) {
    const angle = getAngle(i);
    const endCoords = getCoordinates(angle, radius);
    gridLines.push(
      <GridLine
        key={i}
        x1={centerX}
        y1={centerY}
        x2={endCoords.x}
        y2={endCoords.y}
      />
    );
  }

  // 데이터 포인트 좌표 계산
  const dataPoints = data.map((value, index) => {
    const angle = getAngle(index);
    const distance = (value / maxValue) * radius;
    return getCoordinates(angle, distance);
  });

  // 다각형 경로 생성
  const polygonPoints = dataPoints.map(point => `${point.x},${point.y}`).join(' ');

  // 라벨 위치 계산
  const labelPositions = labels.map((label, index) => {
    const angle = getAngle(index);
    // 긴 텍스트에 따라 간격 조정
    let labelDistance;
    if (label.includes('팀워크') || label.includes('커뮤니케이션')) {
      labelDistance = radius + 60; // 긴 텍스트
    } else if (label.includes('회사 가치관') || label.includes('부합도')) {
      labelDistance = radius + 70; // 가장 긴 텍스트
    } else {
      labelDistance = radius + 40; // 기본 텍스트
    }
    return {
      ...getCoordinates(angle, labelDistance),
      text: label
    };
  });

  // 틱 라벨 생성
  const tickLabels = [];
  for (let i = 1; i <= 5; i++) {
    const tickValue = (maxValue * i) / 5;
    const tickRadius = (radius * i) / 5;
    const tickCoords = getCoordinates(0, tickRadius); // 12시 방향

    tickLabels.push(
      <TickText
        key={i}
        x={centerX}
        y={centerY - tickRadius}
      >
        {tickValue}
      </TickText>
    );
  }

  return (
    <RadarContainer>
      <RadarSVG viewBox="0 0 320 320">
        {/* 그리드 원 */}
        {gridCircles}

        {/* 그리드 라인 */}
        {gridLines}

        {/* 틱 라벨 */}
        {tickLabels}

        {/* 데이터 다각형 */}
        <DataPolygon points={polygonPoints} />

        {/* 데이터 포인트 */}
        {dataPoints.map((point, index) => (
          <DataPoint
            key={index}
            cx={point.x}
            cy={point.y}
          />
        ))}

        {/* 축 라벨 */}
        {labelPositions.map((label, index) => (
          <LabelText
            key={index}
            x={label.x}
            y={label.y}
          >
            {label.text}
          </LabelText>
        ))}
      </RadarSVG>
    </RadarContainer>
  );
};

export default CustomRadarChart;
