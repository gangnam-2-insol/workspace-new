import styled from 'styled-components';
import { motion } from 'framer-motion';

// 기본 레이아웃 컴포넌트
export const Container = styled.div.attrs({
  id: 'applicant-management-container'
})`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

export const Header = styled.div.attrs({
  id: 'applicant-management-header'
})`
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
`;

export const HeaderContent = styled.div.attrs({
  id: 'applicant-management-header-content'
})`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const HeaderLeft = styled.div.attrs({
  id: 'applicant-management-header-left'
})`
  flex: 1;
`;

export const HeaderRight = styled.div.attrs({
  id: 'applicant-management-header-right'
})`
  display: flex;
  align-items: center;
`;

export const Title = styled.h1.attrs({
  id: 'applicant-management-title'
})`
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
`;

export const Subtitle = styled.p.attrs({
  id: 'applicant-management-subtitle'
})`
  margin: 0;
  color: var(--text-secondary);
  font-size: 16px;
`;

// 버튼 컴포넌트
export const NewResumeButton = styled.button.attrs({
  id: 'applicant-management-new-resume-button'
})`
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
`;

export const FilterButton = styled.button.attrs({
  id: 'applicant-management-filter-button'
})`
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--background-hover);
    border-color: var(--primary-color);
  }

  &.active {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
  }
`;

export const ViewModeButton = styled.button.attrs({
  id: 'applicant-management-view-mode-button'
})`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: white;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--background-hover);
    color: var(--text-primary);
  }

  &.active {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
  }

  &:first-child {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }

  &:last-child {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: none;
  }
`;

export const ActionButton = styled.button.attrs({
  id: 'applicant-management-action-button'
})`
  display: flex;
  align-items: center;
  gap: 6px;
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--background-hover);
    border-color: var(--primary-color);
  }

  &.primary {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);

    &:hover {
      background: var(--primary-hover);
    }
  }

  &.danger {
    background: var(--danger-color);
    color: white;
    border-color: var(--danger-color);

    &:hover {
      background: var(--danger-hover);
    }
  }
`;

// 검색 및 필터 컴포넌트
export const SearchBar = styled.div.attrs({
  id: 'applicant-management-search-bar'
})`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
`;

export const SearchSection = styled.div.attrs({
  id: 'applicant-management-search-section'
})`
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
`;

export const SearchInputContainer = styled.div.attrs({
  id: 'applicant-management-search-input-container'
})`
  position: relative;
  flex: 1;
`;

export const SearchInput = styled.input.attrs({
  id: 'applicant-management-search-input',
  type: 'text',
  placeholder: '지원자 이름, 직무, 이메일, 스킬로 검색...'
})`
  width: 100%;
  padding: 10px 40px 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: var(--text-placeholder);
  }
`;

export const ClearButton = styled.button.attrs({
  id: 'applicant-management-clear-button'
})`
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background: var(--background-hover);
    color: var(--text-primary);
  }
`;

export const ViewModeSection = styled.div.attrs({
  id: 'applicant-management-view-mode-section'
})`
  display: flex;
  align-items: center;
  gap: 0;
`;

export const JobPostingSelect = styled.select.attrs({
  id: 'applicant-management-job-posting-select'
})`
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

// 통계 컴포넌트
export const StatsGrid = styled.div.attrs({
  id: 'applicant-management-stats-grid'
})`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
`;

export const StatCard = styled.div.attrs({
  id: 'applicant-management-stat-card'
})`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

export const StatValue = styled.div.attrs({
  id: 'applicant-management-stat-value'
})`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

export const StatLabel = styled.div.attrs({
  id: 'applicant-management-stat-label'
})`
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
`;

// 로딩 컴포넌트
export const LoadingIndicator = styled.div.attrs({
  id: 'applicant-management-loading-indicator'
})`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 16px;
`;

export const LoadingOverlay = styled.div.attrs({
  id: 'applicant-management-loading-overlay'
})`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
  border-radius: 8px;
`;

export const LoadingSpinner = styled.div.attrs({
  id: 'applicant-management-loading-spinner'
})`
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// 지원자 목록 컴포넌트
export const ApplicantsGrid = styled.div.attrs({
  id: 'applicant-management-applicants-grid'
})`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 24px;
`;

export const ApplicantsBoard = styled.div.attrs({
  id: 'applicant-management-applicants-board'
})`
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
`;

export const Wrapper = styled.div.attrs({
  id: 'applicant-management-wrapper'
})`
  position: relative;
  min-height: 400px;
`;

// 헤더 행 컴포넌트
export const HeaderRow = styled.div.attrs({
  id: 'applicant-management-header-row'
})`
  display: grid;
  grid-template-columns: 40px 1fr 120px 100px 150px 120px 100px 120px;
  gap: 16px;
  padding: 12px 16px;
  background: var(--background-secondary);
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

export const HeaderRowBoard = styled.div.attrs({
  id: 'applicant-management-header-row-board'
})`
  display: grid;
  grid-template-columns: 40px 1fr 120px 100px 150px 120px 100px 120px;
  gap: 16px;
  padding: 12px 16px;
  background: var(--background-secondary);
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

// 체크박스 컴포넌트
export const ApplicantCheckbox = styled.div.attrs({
  id: 'applicant-management-applicant-checkbox'
})`
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const CheckboxInput = styled.input.attrs({
  id: 'applicant-management-checkbox-input',
  type: 'checkbox'
})`
  width: 16px;
  height: 16px;
  cursor: pointer;
`;

// 액션 바 컴포넌트
export const FixedActionBar = styled.div.attrs({
  id: 'applicant-management-fixed-action-bar'
})`
  position: sticky;
  top: 0;
  background: white;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
  z-index: 100;
  margin-bottom: 16px;
`;

export const ActionButtonsGroup = styled.div.attrs({
  id: 'applicant-management-action-buttons-group'
})`
  display: flex;
  gap: 8px;
`;

export const FixedActionButton = styled.button.attrs({
  id: 'applicant-management-fixed-action-button'
})`
  display: flex;
  align-items: center;
  gap: 6px;
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--background-hover);
    border-color: var(--primary-color);
  }

  &.primary {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);

    &:hover {
      background: var(--primary-hover);
    }
  }

  &.danger {
    background: var(--danger-color);
    color: white;
    border-color: var(--danger-color);

    &:hover {
      background: var(--danger-hover);
    }
  }
`;

// 선택 정보 컴포넌트
export const SelectionInfo = styled.div.attrs({
  id: 'applicant-management-selection-info'
})`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--text-secondary);
`;

// 필터 배지 컴포넌트
export const FilterBadge = styled.span.attrs({
  id: 'applicant-management-filter-badge'
})`
  background: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
`;

// 빈 상태 컴포넌트
export const NoResultsMessage = styled.div.attrs({
  id: 'applicant-management-no-results-message'
})`
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 16px;
`;

export const EmptyState = styled.div.attrs({
  id: 'applicant-management-empty-state'
})`
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
`;

// 모달 컴포넌트
export const ModalHeader = styled.div.attrs({
  id: 'applicant-management-modal-header'
})`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
`;

export const ModalTitle = styled.h2.attrs({
  id: 'applicant-management-modal-title'
})`
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
`;

export const CloseButton = styled.button.attrs({
  id: 'applicant-management-close-button'
})`
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background: var(--background-hover);
    color: var(--text-primary);
  }
`;

// 문서 모달 컴포넌트
export const DocumentModalHeader = styled.div.attrs({
  id: 'applicant-management-document-modal-header'
})`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
`;

export const DocumentModalTitle = styled.h2.attrs({
  id: 'applicant-management-document-modal-title'
})`
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
`;

export const DocumentCloseButton = styled.button.attrs({
  id: 'applicant-management-document-close-button'
})`
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background: var(--background-hover);
    color: var(--text-primary);
  }
`;

export const DocumentHeaderActions = styled.div.attrs({
  id: 'applicant-management-document-header-actions'
})`
  display: flex;
  gap: 8px;
`;

export const DocumentOriginalButton = styled.button.attrs({
  id: 'applicant-management-document-original-button'
})`
  display: flex;
  align-items: center;
  gap: 6px;
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--background-hover);
    border-color: var(--primary-color);
  }
`;

export const DocumentContent = styled.div.attrs({
  id: 'applicant-management-document-content'
})`
  max-height: 500px;
  overflow-y: auto;
`;

export const DocumentSection = styled.div.attrs({
  id: 'applicant-management-document-section'
})`
  margin-bottom: 24px;
`;

// 선택 그리드 컴포넌트
export const SelectionGrid = styled.div.attrs({
  id: 'applicant-management-selection-grid'
})`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

export const SelectionCard = styled.div.attrs({
  id: 'applicant-management-selection-card'
})`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
  }

  &.selected {
    border-color: var(--primary-color);
    background: var(--primary-light);
  }
`;

export const SelectionIcon = styled.div.attrs({
  id: 'applicant-management-selection-icon'
})`
  width: 48px;
  height: 48px;
  background: var(--background-secondary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  color: var(--text-secondary);
  font-size: 24px;
`;

export const SelectionTitle = styled.h3.attrs({
  id: 'applicant-management-selection-title'
})`
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
`;

export const SelectionDesc = styled.p.attrs({
  id: 'applicant-management-selection-desc'
})`
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
`;

// 프로필 섹션 컴포넌트
export const ProfileSection = styled.div.attrs({
  id: 'applicant-management-profile-section'
})`
  margin-bottom: 24px;
`;

export const SectionTitle = styled.h3.attrs({
  id: 'applicant-management-section-title'
})`
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
`;

export const ProfileGrid = styled.div.attrs({
  id: 'applicant-management-profile-grid'
})`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

export const ProfileItem = styled.div.attrs({
  id: 'applicant-management-profile-item'
})`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

export const ProfileLabel = styled.span.attrs({
  id: 'applicant-management-profile-label'
})`
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
`;

export const ProfileValue = styled.span.attrs({
  id: 'applicant-management-profile-value'
})`
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
`;

// 요약 섹션 컴포넌트
export const SummarySection = styled.div.attrs({
  id: 'applicant-management-summary-section'
})`
  margin-bottom: 24px;
`;

export const SummaryTitle = styled.h3.attrs({
  id: 'applicant-management-summary-title'
})`
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
`;

export const SummaryText = styled.p.attrs({
  id: 'applicant-management-summary-text'
})`
  margin: 0;
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
`;

// 문서 버튼 컴포넌트
export const DocumentButtons = styled.div.attrs({
  id: 'applicant-management-document-buttons'
})`
  display: flex;
  gap: 12px;
  margin-top: 16px;
`;

export const DocumentButton = styled.button.attrs({
  id: 'applicant-management-document-button'
})`
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--background-hover);
    border-color: var(--primary-color);
  }

  &.primary {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);

    &:hover {
      background: var(--primary-hover);
    }
  }
`;

// 상태 선택 컴포넌트
export const StatusSelect = styled.select.attrs({
  id: 'applicant-management-status-select'
})`
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

export const StatusColumnWrapper = styled.div.attrs({
  id: 'applicant-management-status-column-wrapper'
})`
  display: flex;
  align-items: center;
  gap: 8px;
`;

// 헤더 컴포넌트들
export const HeaderAvatar = styled.div.attrs({
  id: 'applicant-management-header-avatar'
})`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--background-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
`;

export const HeaderName = styled.div.attrs({
  id: 'applicant-management-header-name'
})`
  font-weight: 600;
  color: var(--text-primary);
`;

export const HeaderPosition = styled.div.attrs({
  id: 'applicant-management-header-position'
})`
  color: var(--text-secondary);
  font-size: 12px;
`;

export const HeaderDate = styled.div.attrs({
  id: 'applicant-management-header-date'
})`
  color: var(--text-secondary);
  font-size: 12px;
`;

export const HeaderEmail = styled.div.attrs({
  id: 'applicant-management-header-email'
})`
  color: var(--text-secondary);
  font-size: 12px;
`;

export const HeaderPhone = styled.div.attrs({
  id: 'applicant-management-header-phone'
})`
  color: var(--text-secondary);
  font-size: 12px;
`;

export const HeaderSkills = styled.div.attrs({
  id: 'applicant-management-header-skills'
})`
  color: var(--text-secondary);
  font-size: 12px;
`;

export const HeaderActions = styled.div.attrs({
  id: 'applicant-management-header-actions'
})`
  display: flex;
  gap: 4px;
`;

export const HeaderScore = styled.div.attrs({
  id: 'applicant-management-header-score'
})`
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
`;

export const HeaderCheckbox = styled.div.attrs({
  id: 'applicant-management-header-checkbox'
})`
  display: flex;
  align-items: center;
  justify-content: center;
`;

// 카드 컴포넌트들
export const CardHeader = styled.div.attrs({
  id: 'applicant-management-card-header'
})`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

export const CardContent = styled.div.attrs({
  id: 'applicant-management-card-content'
})`
  flex: 1;
`;

export const InfoRow = styled.div.attrs({
  id: 'applicant-management-info-row'
})`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
`;

export const CardActions = styled.div.attrs({
  id: 'applicant-management-card-actions'
})`
  display: flex;
  gap: 8px;
  margin-top: 12px;
`;

// 지원자 컴포넌트들
export const ApplicantHeader = styled.div.attrs({
  id: 'applicant-management-applicant-header'
})`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

export const ApplicantHeaderBoard = styled.div.attrs({
  id: 'applicant-management-applicant-header-board'
})`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`;

export const ApplicantInfo = styled.div.attrs({
  id: 'applicant-management-applicant-info'
})`
  flex: 1;
`;

export const ApplicantInfoBoard = styled.div.attrs({
  id: 'applicant-management-applicant-info-board'
})`
  display: grid;
  grid-template-columns: 40px 1fr 120px 100px 150px 120px 100px 120px;
  gap: 16px;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.2s;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`;

export const Avatar = styled.div.attrs({
  id: 'applicant-management-avatar'
})`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
`;

export const AvatarBoard = styled.div.attrs({
  id: 'applicant-management-avatar-board'
})`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 12px;
`;

export const AiSuitabilityAvatarBoard = styled.div.attrs({
  id: 'applicant-management-ai-suitability-avatar-board'
})`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${props => {
    const score = props.score || 0;
    if (score >= 80) return 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)';
    if (score >= 60) return 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)';
    return 'linear-gradient(135deg, #f87171 0%, #ef4444 100%)';
  }};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 12px;
`;

export const ApplicantDetails = styled.div.attrs({
  id: 'applicant-management-applicant-details'
})`
  flex: 1;
`;

export const ApplicantDetailsBoard = styled.div.attrs({
  id: 'applicant-management-applicant-details-board'
})`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

export const ApplicantName = styled.h3.attrs({
  id: 'applicant-management-applicant-name'
})`
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
`;

export const ApplicantNameBoard = styled.h3.attrs({
  id: 'applicant-management-applicant-name-board'
})`
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
`;

export const ApplicantPosition = styled.p.attrs({
  id: 'applicant-management-applicant-position'
})`
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
`;

export const ApplicantPositionBoard = styled.p.attrs({
  id: 'applicant-management-applicant-position-board'
})`
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const ApplicantDate = styled.p.attrs({
  id: 'applicant-management-applicant-date'
})`
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const ApplicantDateBoard = styled.p.attrs({
  id: 'applicant-management-applicant-date-board'
})`
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const ApplicantEmailBoard = styled.div.attrs({
  id: 'applicant-management-applicant-email-board'
})`
  font-size: 12px;
  color: var(--text-secondary);
`;

export const ApplicantPhoneBoard = styled.div.attrs({
  id: 'applicant-management-applicant-phone-board'
})`
  font-size: 12px;
  color: var(--text-secondary);
`;

export const ContactItem = styled.div.attrs({
  id: 'applicant-management-contact-item'
})`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const ApplicantSkillsBoard = styled.div.attrs({
  id: 'applicant-management-applicant-skills-board'
})`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
`;

export const SkillTagBoard = styled.span.attrs({
  id: 'applicant-management-skill-tag-board'
})`
  background: var(--background-secondary);
  color: var(--text-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
`;

export const ApplicantActions = styled.div.attrs({
  id: 'applicant-management-applicant-actions'
})`
  display: flex;
  gap: 8px;
  margin-top: 12px;
`;

export const ApplicantActionsBoard = styled.div.attrs({
  id: 'applicant-management-applicant-actions-board'
})`
  display: flex;
  gap: 4px;
`;
