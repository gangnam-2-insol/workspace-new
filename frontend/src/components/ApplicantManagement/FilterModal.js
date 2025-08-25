import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

// 필터 모달 스타일
const FilterModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1500;
  padding: 20px;
`;

const FilterModalContent = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 600px;
  width: 100%;
  position: relative;
`;

const FilterModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
`;

const FilterModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
`;

const FilterCloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const FilterSection = styled.div`
  margin-bottom: 24px;
`;

const FilterSectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
`;

const FilterGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
`;

const FilterColumn = styled.div``;

const CheckboxGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const CheckboxItem = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);

  &:hover {
    color: var(--primary-color);
  }
`;

const Checkbox = styled.input`
  width: 16px;
  height: 16px;
  accent-color: var(--primary-color);
`;

const ApplyButton = styled.button`
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

const ResetButton = styled.button`
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #e5e7eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const FilterButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;

  ${ApplyButton}, ${ResetButton} {
    flex: 1;
  }
`;

// 필터 옵션 데이터
const JOB_OPTIONS = [
  '프론트엔드',
  '풀스택',
  'PM',
  'DevOps',
  '백엔드',
  '데이터 분석',
  'UI/UX',
  'QA'
];

const EXPERIENCE_OPTIONS = [
  '신입',
  '1-3년',
  '3-5년',
  '5년이상'
];

const STATUS_OPTIONS = [
  '서류합격',
  '최종합격',
  '보류',
  '서류불합격'
];

const FilterModal = ({
  isOpen,
  onClose,
  selectedJobs,
  selectedExperience,
  selectedStatus,
  onJobChange,
  onExperienceChange,
  onStatusChange,
  onApplyFilter,
  onResetFilter
}) => {
  if (!isOpen) return null;

  return (
    <FilterModalOverlay
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <FilterModalContent
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <FilterModalHeader>
          <FilterModalTitle>필터</FilterModalTitle>
          <FilterCloseButton onClick={onClose}>&times;</FilterCloseButton>
        </FilterModalHeader>

        <FilterGrid>
          <FilterColumn>
            <FilterSection>
              <FilterSectionTitle>직무</FilterSectionTitle>
              <CheckboxGroup>
                {JOB_OPTIONS.map(job => (
                  <CheckboxItem key={job}>
                    <Checkbox
                      type="checkbox"
                      checked={selectedJobs.includes(job)}
                      onChange={() => onJobChange(job)}
                    />
                    {job}
                  </CheckboxItem>
                ))}
              </CheckboxGroup>
            </FilterSection>
          </FilterColumn>

          <FilterColumn>
            <FilterSection>
              <FilterSectionTitle>경력</FilterSectionTitle>
              <CheckboxGroup>
                {EXPERIENCE_OPTIONS.map(experience => (
                  <CheckboxItem key={experience}>
                    <Checkbox
                      type="checkbox"
                      checked={selectedExperience.includes(experience)}
                      onChange={() => onExperienceChange(experience)}
                    />
                    {experience}
                  </CheckboxItem>
                ))}
              </CheckboxGroup>
            </FilterSection>

            <FilterSection>
              <FilterSectionTitle>상태</FilterSectionTitle>
              <CheckboxGroup>
                {STATUS_OPTIONS.map(status => (
                  <CheckboxItem key={status}>
                    <Checkbox
                      type="checkbox"
                      checked={selectedStatus.includes(status)}
                      onChange={() => onStatusChange(status)}
                    />
                    {status}
                  </CheckboxItem>
                ))}
              </CheckboxGroup>
            </FilterSection>
          </FilterColumn>
        </FilterGrid>

        <FilterButtonGroup>
          <ResetButton onClick={onResetFilter}>
            초기화
          </ResetButton>
          <ApplyButton onClick={onApplyFilter}>
            적용
          </ApplyButton>
        </FilterButtonGroup>
      </FilterModalContent>
    </FilterModalOverlay>
  );
};

export default FilterModal;
