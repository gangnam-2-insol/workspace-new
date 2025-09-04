import React from 'react';
import styled, { keyframes } from 'styled-components';

// 회전 애니메이션
const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

// 로딩 오버레이 컨테이너
const LoadingOverlayContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 1);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  z-index: 1000;
  gap: 20px;
  padding-top: 40px;
`;

// 로딩 텍스트 박스
const LoadingText = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  text-align: center;
  margin-top: 8px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 20px 24px;
  border-radius: 12px;
  border: 2px solid #cbd5e0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

// 로딩 서브텍스트
const LoadingSubtext = styled.div`
  font-size: 14px;
  color: #718096;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
`;

// 회전하는 모래시계 이모지
const SpinningHourglass = styled.span`
  display: inline-block;
  animation: ${spin} 2s linear infinite;
`;

// 로딩 이미지
const LoadingImage = styled.img`
  width: 600px;
  height: 600px;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

/**
 * AI 분석 로딩 오버레이 컴포넌트
 * @param {Object} props
 * @param {boolean} props.isLoading - 로딩 상태
 * @param {string} props.mainText - 메인 텍스트 (기본값: "AI 분석중입니다.")
 * @param {string} props.subText - 서브 텍스트 (기본값: "잠시만 기다려주세요...")
 * @param {string} props.imageSrc - 로딩 이미지 경로 (기본값: "/cat_git.gif")
 * @param {string} props.imageAlt - 이미지 alt 텍스트 (기본값: "AI 분석 중")
 * @param {string} props.hourglassEmoji - 모래시계 이모지 (기본값: "⏳")
 */
const LoadingOverlay = ({
  isLoading,
  mainText = "AI 분석중입니다.",
  subText = "잠시만 기다려주세요...",
  imageSrc = "/cat_git.gif",
  imageAlt = "AI 분석 중",
  hourglassEmoji = "⏳"
}) => {
  if (!isLoading) return null;

  return (
    <LoadingOverlayContainer>
      <LoadingText>
        {mainText}
        <LoadingSubtext>
          <SpinningHourglass>{hourglassEmoji}</SpinningHourglass>
          {subText}
        </LoadingSubtext>
      </LoadingText>
      <LoadingImage
        src={imageSrc}
        alt={imageAlt}
      />
    </LoadingOverlayContainer>
  );
};

export default LoadingOverlay;
