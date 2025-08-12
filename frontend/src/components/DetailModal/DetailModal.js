import React from 'react';
import styled from 'styled-components';
import { FiX, FiEdit, FiTrash2 } from 'react-icons/fi';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
`;

const ModalTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;

  &:hover {
    color: #374151;
  }
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const OriginalViewButton = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    background: #2563eb;
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &.primary {
    background-color: #3b82f6;
    color: white;
    
    &:hover {
      background-color: #2563eb;
    }
  }

  &.secondary {
    background-color: #f3f4f6;
    color: #374151;
    
    &:hover {
      background-color: #e5e7eb;
    }
  }

  &.danger {
    background-color: #ef4444;
    color: white;
    
    &:hover {
      background-color: #dc2626;
    }
  }
`;

const DetailSection = styled.div`
  margin-bottom: 20px;
`;

const SectionTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
`;

const DetailGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
`;

const DetailItem = styled.div`
  display: flex;
  flex-direction: column;
`;

const DetailLabel = styled.span`
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 4px;
`;

const DetailValue = styled.span`
  font-size: 1rem;
  color: #111827;
  font-weight: 500;
`;

const DetailText = styled.div`
  font-size: 1rem;
  color: #111827;
  line-height: 1.6;
  margin-bottom: 16px;
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;

  &.success {
    background-color: #d1fae5;
    color: #065f46;
  }

  &.warning {
    background-color: #fef3c7;
    color: #92400e;
  }

  &.danger {
    background-color: #fee2e2;
    color: #991b1b;
  }

  &.info {
    background-color: #dbeafe;
    color: #1e40af;
  }
`;

const DetailModal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  onEdit, 
  onDelete, 
  showActions = true 
}) => {
  if (!isOpen) return null;

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>{title}</ModalTitle>
          <HeaderActions>
            <OriginalViewButton>
              원본보기
            </OriginalViewButton>
            <CloseButton onClick={onClose}>
              <FiX />
            </CloseButton>
          </HeaderActions>
        </ModalHeader>
        
        {children}
        
        {showActions && (
          <ActionButtons>
            {onEdit && (
              <ActionButton className="primary" onClick={onEdit}>
                <FiEdit />
                수정
              </ActionButton>
            )}
            {onDelete && (
              <ActionButton className="danger" onClick={onDelete}>
                <FiTrash2 />
                삭제
              </ActionButton>
            )}
            <ActionButton className="secondary" onClick={onClose}>
              닫기
            </ActionButton>
          </ActionButtons>
        )}
      </ModalContent>
    </ModalOverlay>
  );
};

export default DetailModal;

// Export styled components for use in other files
export {
  DetailSection,
  SectionTitle,
  DetailGrid,
  DetailItem,
  DetailLabel,
  DetailValue,
  DetailText,
  StatusBadge
}; 