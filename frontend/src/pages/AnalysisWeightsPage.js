import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FiSettings, FiSave, FiRotateCcw, FiInfo, FiBarChart2 } from 'react-icons/fi';

const PageContainer = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const PageHeader = styled.div`
  margin-bottom: 32px;
`;

const PageTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const PageSubtitle = styled.p`
  font-size: 16px;
  color: #6b7280;
  margin: 0;
`;

const SettingsCard = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
`;

const SettingsHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
`;

const SettingsTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0;
`;

const InfoBox = styled.div`
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
`;

const InfoIcon = styled.div`
  color: #0ea5e9;
  margin-top: 2px;
`;

const InfoText = styled.div`
  color: #0c4a6e;
  font-size: 14px;
  line-height: 1.5;
`;

const WeightGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr 1fr;
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const WeightItem = styled.div`
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;

  &:hover {
    background: #f3f4f6;
    border-color: #d1d5db;
  }
`;

const WeightInfo = styled.div`
  margin-bottom: 16px;
`;

const WeightLabel = styled.div`
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
`;

const WeightDescription = styled.div`
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
`;

const WeightControls = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const WeightSlider = styled.input`
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 8px;
  border-radius: 4px;
  background: #e5e7eb;
  outline: none;
  transition: background 0.2s;

  &:hover {
    background: #d1d5db;
  }

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #3b82f6;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transition: all 0.2s;

    &:hover {
      background: #2563eb;
      transform: scale(1.1);
    }
  }

  &::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #3b82f6;
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
`;

const WeightValue = styled.div`
  font-size: 16px;
  font-weight: 700;
  color: #3b82f6;
  min-width: 50px;
  text-align: center;
  background: #eff6ff;
  padding: 8px 12px;
  border-radius: 6px;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &.save {
    background: #3b82f6;
    color: white;

    &:hover:not(:disabled) {
      background: #2563eb;
      transform: translateY(-1px);
    }

    &:disabled {
      background: #9ca3af;
      cursor: not-allowed;
    }
  }

  &.reset {
    background: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;

    &:hover {
      background: #e5e7eb;
      transform: translateY(-1px);
    }
  }
`;

const PreviewSection = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  margin-top: 24px;
`;

const PreviewTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
`;

const PreviewExample = styled.div`
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
`;

const AnalysisWeightsPage = () => {
  // 기본 가중치 설정 (중요도 기반)
  const defaultWeights = {
    technical_skills: 25,
    experience: 30,
    education: 15,
    projects: 20,
    achievements: 5,
    communication: 5
  };

  const [weights, setWeights] = useState(defaultWeights);
  const [hasChanges, setHasChanges] = useState(false);

  // 로컬 스토리지에서 가중치 로드
  useEffect(() => {
    const savedWeights = localStorage.getItem('analysisWeights');
    if (savedWeights) {
      try {
        const parsed = JSON.parse(savedWeights);
        setWeights(parsed);
      } catch (error) {
        console.error('가중치 로드 실패:', error);
      }
    }
  }, []);

  // 가중치 변경 핸들러
  const handleWeightChange = (key, value) => {
    const newWeights = { ...weights, [key]: parseInt(value) };
    setWeights(newWeights);
    setHasChanges(true);
  };

  // 가중치 저장
  const handleSave = () => {
    localStorage.setItem('analysisWeights', JSON.stringify(weights));
    setHasChanges(false);

    // 전역 이벤트 발생 (다른 컴포넌트에서 감지 가능)
    window.dispatchEvent(new CustomEvent('analysisWeightsChanged', {
      detail: weights
    }));

    alert('가중치 설정이 저장되었습니다!');
  };

  // 가중치 초기화
  const handleReset = () => {
    setWeights(defaultWeights);
    setHasChanges(true);
  };

  const weightConfig = {
    technical_skills: {
      label: '기술 스킬',
      description: '프로그래밍 언어, 프레임워크, 도구 사용 능력'
    },
    experience: {
      label: '경력',
      description: '실무 경험, 프로젝트 참여 기간, 업무 성과'
    },
    education: {
      label: '학력',
      description: '학위, 전공, 관련 자격증, 교육 과정'
    },
    projects: {
      label: '프로젝트',
      description: '포트폴리오, 개인/팀 프로젝트, 오픈소스 기여'
    },
    achievements: {
      label: '성과',
      description: '수상 경력, 인증, 특별한 성취'
    },
    communication: {
      label: '커뮤니케이션',
      description: '팀워크, 리더십, 문서화 능력'
    }
  };

  // 가중치 합계 계산
  const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);

  return (
    <PageContainer>
      <PageHeader>
        <PageTitle>
          <FiBarChart2 />
          분석 가중치 설정
        </PageTitle>
        <PageSubtitle>
          회사의 인재상에 맞게 이력서 분석 항목의 중요도를 조정하세요
        </PageSubtitle>
      </PageHeader>

      <SettingsCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <SettingsHeader>
          <FiSettings size={24} />
          <SettingsTitle>이력서 분석 가중치</SettingsTitle>
        </SettingsHeader>

        <InfoBox>
          <InfoIcon>
            <FiInfo size={20} />
          </InfoIcon>
          <InfoText>
            <strong>중요도 기반 점수 조정:</strong> 가중치가 높은 항목은 상대적으로 더 중요하게 평가됩니다.
            예를 들어 경력 가중치를 높이면, 경력이 좋은 지원자가 더 높은 점수를 받게 됩니다.
          </InfoText>
        </InfoBox>

        <WeightGrid>
          {Object.entries(weightConfig).map(([key, config]) => (
            <WeightItem key={key}>
              <WeightInfo>
                <WeightLabel>{config.label}</WeightLabel>
                <WeightDescription>{config.description}</WeightDescription>
              </WeightInfo>
              <WeightControls>
                <WeightSlider
                  type="range"
                  min="0"
                  max="50"
                  value={weights[key]}
                  onChange={(e) => handleWeightChange(key, e.target.value)}
                />
                <WeightValue>{weights[key]}%</WeightValue>
              </WeightControls>
            </WeightItem>
          ))}
        </WeightGrid>

        <PreviewSection>
          <PreviewTitle>설정 미리보기</PreviewTitle>
          <PreviewExample>
            현재 설정으로는 <strong>경력({weights.experience}%)</strong>과 <strong>기술 스킬({weights.technical_skills}%)</strong>이
            가장 중요하게 평가됩니다. 총 가중치: {totalWeight}%
          </PreviewExample>
        </PreviewSection>

        <ActionButtons>
          <ActionButton
            className="save"
            onClick={handleSave}
            disabled={!hasChanges}
          >
            <FiSave size={18} />
            설정 저장
          </ActionButton>
          <ActionButton
            className="reset"
            onClick={handleReset}
          >
            <FiRotateCcw size={18} />
            기본값으로 초기화
          </ActionButton>
        </ActionButtons>
      </SettingsCard>
    </PageContainer>
  );
};

export default AnalysisWeightsPage;
