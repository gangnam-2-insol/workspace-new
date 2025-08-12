import React from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiX, 
  FiFileText, 
  FiImage,
  FiCheck,
  FiArrowRight
} from 'react-icons/fi';

const Overlay = styled(motion.div)`
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

const Modal = styled(motion.div)`
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid var(--border-color);
`;

const Title = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const Content = styled.div`
  padding: 32px;
`;

const MethodGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 32px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const MethodCard = styled(motion.div)`
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

  &.selected {
    border-color: var(--primary-color);
    background: rgba(0, 200, 81, 0.05);
  }
`;

const MethodIcon = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  font-size: 24px;
  color: white;

  &.text {
    background: linear-gradient(135deg, #667eea, #764ba2);
  }

  &.image {
    background: linear-gradient(135deg, #f093fb, #f5576c);
  }
`;

const MethodTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
`;

const MethodDescription = styled.p`
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
`;

const MethodFeatures = styled.ul`
  list-style: none;
  padding: 0;
  margin: 16px 0 0 0;
`;

const MethodFeature = styled.li`
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;

  &:before {
    content: "✓";
    color: var(--primary-color);
    font-weight: bold;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const Button = styled.button`
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;

  &.primary {
    background: linear-gradient(135deg, #00c851, #00a844);
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(0, 200, 81, 0.3);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
  }

  &.secondary {
    background: white;
    color: var(--text-secondary);
    border: 2px solid var(--border-color);

    &:hover {
      background: var(--background-secondary);
      border-color: var(--text-secondary);
    }
  }
`;

const RegistrationMethodModal = ({ 
  isOpen, 
  onClose, 
  onSelectMethod 
}) => {
  const [selectedMethod, setSelectedMethod] = React.useState(null);

  const handleMethodSelect = (method) => {
    setSelectedMethod(method);
  };

  const handleConfirm = () => {
    if (selectedMethod && onSelectMethod) {
      onSelectMethod(selectedMethod);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <Overlay
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <Modal
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <Header>
              <Title>채용공고 등록 방법 선택</Title>
              <CloseButton onClick={onClose}>
                <FiX />
              </CloseButton>
            </Header>

            <Content>
              <MethodGrid>
                <MethodCard
                  className={selectedMethod === 'text' ? 'selected' : ''}
                  onClick={() => handleMethodSelect('text')}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <MethodIcon className="text">
                    <FiFileText />
                  </MethodIcon>
                  <MethodTitle>텍스트 기반 등록</MethodTitle>
                  <MethodDescription>
                    AI가 추천하는 문구로 자동 생성되는 텍스트 기반 채용공고
                  </MethodDescription>
                  <MethodFeatures>
                    <MethodFeature>회사 정보 자동 적용</MethodFeature>
                    <MethodFeature>AI 추천 문구 제공</MethodFeature>
                    <MethodFeature>빠른 등록 가능</MethodFeature>
                    <MethodFeature>실시간 수정 가능</MethodFeature>
                  </MethodFeatures>
                </MethodCard>

                <MethodCard
                  className={selectedMethod === 'image' ? 'selected' : ''}
                  onClick={() => handleMethodSelect('image')}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <MethodIcon className="image">
                    <FiImage />
                  </MethodIcon>
                  <MethodTitle>이미지 기반 등록</MethodTitle>
                  <MethodDescription>
                    AI가 생성한 이미지로 시각적 채용공고 제작
                  </MethodDescription>
                  <MethodFeatures>
                    <MethodFeature>시각적 임팩트</MethodFeature>
                    <MethodFeature>AI 이미지 생성</MethodFeature>
                    <MethodFeature>다양한 스타일 선택</MethodFeature>
                    <MethodFeature>브랜드 일관성</MethodFeature>
                  </MethodFeatures>
                </MethodCard>
              </MethodGrid>

              <ButtonGroup>
                <Button className="secondary" onClick={onClose}>
                  취소
                </Button>
                <Button 
                  className="primary" 
                  onClick={handleConfirm}
                  disabled={!selectedMethod}
                >
                  <FiArrowRight size={16} />
                  다음 단계
                </Button>
              </ButtonGroup>
            </Content>
          </Modal>
        </Overlay>
      )}
    </AnimatePresence>
  );
};

export default RegistrationMethodModal; 