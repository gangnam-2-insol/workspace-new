import styled from 'styled-components';
import { motion } from 'framer-motion';

// 기본 모달 스타일
export const ModalOverlay = styled(motion.div)`
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

export const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 16px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
`;

export const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid var(--border-color);
`;

export const ModalTitle = styled.h2`
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
`;

export const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  color: var(--text-secondary);
  transition: all 0.2s ease;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

// 문서 모달 스타일
export const DocumentModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
`;

export const DocumentModalContent = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 1200px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
`;

export const DocumentModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
`;

export const DocumentModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
`;

export const DocumentCloseButton = styled.button`
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

export const DocumentHeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

export const DocumentOriginalButton = styled.button`
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;

  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

export const DocumentContent = styled.div`
  line-height: 1.8;
  color: var(--text-primary);
`;

export const DocumentSection = styled.div`
  margin-bottom: 24px;
`;

export const DocumentSectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary-color);
`;

export const DocumentList = styled.ul`
  margin: 16px 0;
  padding-left: 20px;
`;

export const DocumentListItem = styled.li`
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.6;
`;

export const DocumentGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 16px 0;
`;

export const DocumentCard = styled.div`
  background: var(--background-secondary);
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
`;

export const DocumentCardTitle = styled.h4`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

export const DocumentCardText = styled.p`
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
`;

// 문서 미리보기 모달 스타일
export const DocumentPreviewModal = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

export const DocumentPreviewContent = styled.div`
  background-color: white;
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
`;

export const DocumentPreviewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  background-color: #f8fafc;
`;

export const DocumentPreviewTitle = styled.h3`
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
`;

export const DocumentPreviewFooter = styled.div`
  display: flex;
  justify-content: center;
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
`;

export const PreviewCloseButton = styled.button`
  background-color: #4a5568;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background-color: #2d3748;
    transform: translateY(-1px);
  }
`;

export const DocumentText = styled.div`
  padding: 20px 24px;
  max-height: 60vh;
  overflow-y: auto;
  line-height: 1.6;
  color: #2d3748;
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
  background-color: #f7fafc;
  border-radius: 8px;
  margin: 20px 24px;
  border: 1px solid #e2e8f0;
`;

export const PreviewButton = styled.button`
  background-color: #4299e1;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 8px;

  &:hover {
    background-color: #3182ce;
    transform: translateY(-1px);
  }
`;

// 선택 UI 스타일
export const SelectionGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 8px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

export const SelectionCard = styled(motion.div)`
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  background: white;

  &:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 200, 81, 0.1);
  }
`;

export const SelectionIcon = styled.div`
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  font-size: 22px;
  color: white;

  &.github {
    background: linear-gradient(135deg, #24292e, #57606a);
  }

  &.portfolio {
    background: linear-gradient(135deg, #667eea, #764ba2);
  }
`;

export const SelectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
`;

export const SelectionDesc = styled.p`
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
`;

// 프로필 섹션 스타일
export const ProfileSection = styled.div`
  margin-bottom: 24px;
`;

export const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary-color);
`;

export const ProfileGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

export const ProfileItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

export const ProfileLabel = styled.label`
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const ProfileValue = styled.div`
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
`;

// 요약 섹션 스타일
export const SummarySection = styled.div`
  margin-bottom: 24px;
`;

export const SummaryTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
`;

export const SummaryText = styled.p`
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
`;

// 문서 버튼 스타일
export const DocumentButtons = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 16px;
`;

export const DocumentButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    transform: translateY(-1px);
  }
`;

export const ResumeButton = styled(DocumentButton)`
  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }
`;
