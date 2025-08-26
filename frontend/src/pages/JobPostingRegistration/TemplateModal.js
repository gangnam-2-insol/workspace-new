import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiX, 
  FiSave,
  FiFileText,
  FiBriefcase,
  FiUsers,
  FiClock,
  FiMapPin,
  FiDollarSign,
  FiAward,
  FiHeart,
  FiTrash2,
  FiEdit3,
  FiEye
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
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
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

const TabContainer = styled.div`
  display: flex;
  border-bottom: 2px solid var(--border-color);
  margin-bottom: 24px;
`;

const Tab = styled.button`
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 600;
  color: ${props => props.active ? 'var(--primary-color)' : 'var(--text-secondary)'};
  border-bottom: 2px solid ${props => props.active ? 'var(--primary-color)' : 'transparent'};
  transition: all 0.3s ease;

  &:hover {
    color: var(--primary-color);
  }
`;

const FormSection = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
`;

const Input = styled.input`
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const TextArea = styled.textarea`
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  min-height: 120px;
  resize: vertical;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const Select = styled.select`
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
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

const TemplateGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 24px;
`;

const TemplateCard = styled(motion.div)`
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;

  &:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 200, 81, 0.1);
  }
`;

const TemplateHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const TemplateTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const TemplateActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s ease;
  color: var(--text-secondary);

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }

  &.danger:hover {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
  }
`;

const TemplateInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
`;

const EmptyIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
`;

const TemplateModal = ({ 
  isOpen, 
  onClose, 
  onSaveTemplate,
  onLoadTemplate,
  onDeleteTemplate,
  templates = [],
  currentData = null
}) => {
  const [activeTab, setActiveTab] = useState('save');
  const [templateName, setTemplateName] = useState('');
  const [templateData, setTemplateData] = useState({
    department: '',
    experience: '',
    experienceYears: '',
    mainDuties: '',
    requirements: '',
    benefits: '',
    workHours: '',
    workDays: '',
    locationCity: '',
    locationDistrict: '',
    salary: '',
    process: ['서류', '실무면접', '최종면접', '입사'],
    contactEmail: '',
    deadline: ''
  });

  React.useEffect(() => {
    if (currentData) {
      setTemplateData(currentData);
    }
  }, [currentData]);

  const handleSaveTemplate = () => {
    if (templateName.trim() && onSaveTemplate) {
      onSaveTemplate({
        id: Date.now(),
        name: templateName,
        data: templateData,
        createdAt: new Date().toISOString()
      });
      setTemplateName('');
      onClose();
    }
  };

  const handleLoadTemplate = (template) => {
    if (onLoadTemplate) {
      onLoadTemplate(template.data);
      onClose();
    }
  };

  const handleDeleteTemplate = (templateId) => {
    if (onDeleteTemplate) {
      onDeleteTemplate(templateId);
    }
  };

  const renderSaveTab = () => (
    <div>
      <FormSection>
        <SectionTitle>
          <FiSave size={18} />
          템플릿 저장
        </SectionTitle>
        <FormGroup>
          <Label>템플릿 이름 *</Label>
          <Input
            type="text"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            placeholder="예: 프론트엔드 개발자 템플릿"
            required
          />
        </FormGroup>
      </FormSection>

      <FormSection>
        <SectionTitle>
          <FiFileText size={18} />
          저장될 정보 미리보기
        </SectionTitle>
        <FormGrid>
          <FormGroup>
            <Label>부서</Label>
            <Input value={templateData.department || ''} disabled />
          </FormGroup>
          <FormGroup>
            <Label>경력</Label>
            <Input value={templateData.experience || ''} disabled />
          </FormGroup>
          <FormGroup>
            <Label>근무시간</Label>
            <Input value={templateData.workHours || ''} disabled />
          </FormGroup>
          <FormGroup>
            <Label>근무지</Label>
            <Input value={`${templateData.locationCity || ''} ${templateData.locationDistrict || ''}`} disabled />
          </FormGroup>
        </FormGrid>
      </FormSection>
    </div>
  );

  const renderLoadTab = () => (
    <div>
      <SectionTitle>
        <FiFileText size={18} />
        저장된 템플릿 ({templates.length})
      </SectionTitle>
      
      {templates.length === 0 ? (
        <EmptyState>
          <EmptyIcon>📄</EmptyIcon>
          <div>저장된 템플릿이 없습니다.</div>
          <div style={{ fontSize: '12px', marginTop: '8px' }}>
            템플릿을 저장하면 다음 등록 시 빠르게 불러올 수 있습니다.
          </div>
        </EmptyState>
      ) : (
        <TemplateGrid>
          {templates.map((template) => (
            <TemplateCard
              key={template.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleLoadTemplate(template)}
            >
              <TemplateHeader>
                <TemplateTitle>{template.name}</TemplateTitle>
                <TemplateActions>
                  <ActionButton
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLoadTemplate(template);
                    }}
                    title="템플릿 사용"
                  >
                    <FiEye size={14} />
                  </ActionButton>
                  <ActionButton
                    className="danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteTemplate(template.id);
                    }}
                    title="템플릿 삭제"
                  >
                    <FiTrash2 size={14} />
                  </ActionButton>
                </TemplateActions>
              </TemplateHeader>
              <TemplateInfo>
                <InfoItem>
                  <FiBriefcase size={12} />
                  {template.data.department || '부서 미설정'}
                </InfoItem>
                <InfoItem>
                  <FiUsers size={12} />
                  {template.data.experience || '경력 미설정'}
                </InfoItem>
                <InfoItem>
                  <FiClock size={12} />
                  {template.data.workHours || '근무시간 미설정'}
                </InfoItem>
                <InfoItem>
                  <FiMapPin size={12} />
                  {template.data.locationCity ? `${template.data.locationCity} ${template.data.locationDistrict || ''}` : '근무지 미설정'}
                </InfoItem>
                <InfoItem>
                  <FiDollarSign size={12} />
                  {template.data.salary || '연봉 미설정'}
                </InfoItem>
              </TemplateInfo>
            </TemplateCard>
          ))}
        </TemplateGrid>
      )}
    </div>
  );

  console.log('[TemplateModal] 렌더링, isOpen:', isOpen);
  
  return (
    <AnimatePresence>
      {isOpen && (
        <Overlay
          key="template-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <Modal
            key="template-modal"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <Header>
              <Title>채용공고 템플릿 관리</Title>
              <CloseButton onClick={onClose}>
                <FiX />
              </CloseButton>
            </Header>

            <Content>
              <TabContainer>
                <Tab 
                  active={activeTab === 'save'} 
                  onClick={() => setActiveTab('save')}
                >
                  템플릿 저장
                </Tab>
                <Tab 
                  active={activeTab === 'load'} 
                  onClick={() => setActiveTab('load')}
                >
                  템플릿 불러오기
                </Tab>
              </TabContainer>

              {activeTab === 'save' ? renderSaveTab() : renderLoadTab()}

              {activeTab === 'save' && (
                <ButtonGroup>
                  <Button className="secondary" onClick={onClose}>
                    취소
                  </Button>
                  <Button 
                    className="primary" 
                    onClick={handleSaveTemplate}
                    disabled={!templateName.trim()}
                  >
                    <FiSave size={16} />
                    템플릿 저장
                  </Button>
                </ButtonGroup>
              )}
            </Content>
          </Modal>
        </Overlay>
      )}
    </AnimatePresence>
  );
};

export default TemplateModal; 