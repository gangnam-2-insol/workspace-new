import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import TemplateModal from './TemplateModal';
import EnhancedModalChatbot from '../../chatbot/components/EnhancedModalChatbot';
import './TextBasedRegistration.css';
import { FiX, FiArrowLeft, FiArrowRight, FiCheck, FiFileText, FiClock, FiMapPin, FiDollarSign, FiUsers, FiMail, FiCalendar, FiFolder, FiSettings } from 'react-icons/fi';

// Styled Components (기존과 동일)
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
`;

const Modal = styled(motion.div)`
  background: white;
  border-radius: 16px;
  width: 90%;
  height: 100%;
  max-width: 1000px;
  max-height: 95vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: white;
`;

const Title = styled.h2`
  font-size: 20px;
  font-weight: 600;
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`;

const Content = styled.div`
  padding: 32px;
  max-height: calc(95vh - 120px);
  overflow-y: auto;
`;

const FormSection = styled.div`
  margin-bottom: 32px;
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

const AINotice = styled.div`
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
  flex-wrap: wrap;
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;

  &.primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
  }

  &.secondary {
    background: #f8f9fa;
    color: #495057;
    border: 1px solid #e9ecef;

    &:hover {
      background: #e9ecef;
    }
  }

  &.ai {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    }
  }
`;

const TextBasedRegistrationNoRAG = ({ 
  isOpen, 
  onClose, 
  onComplete,
  organizationData = { departments: [] }
}) => {
  const [formData, setFormData] = useState({
    department: '',
    headcount: '',
    mainDuties: '',
    workHours: '',
    workDays: '',
    salary: '',
    contactEmail: '',
    deadline: '',
    experience: ''
  });

  const [aiChatbot, setAiChatbot] = useState({
    isActive: false,
    currentQuestion: '',
    step: 1
  });

  // 모달이 열릴 때 AI 도우미 자동 시작
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        setAiChatbot({
          isActive: true,
          currentQuestion: '구인 부서를 알려주세요! (예: 개발, 마케팅, 영업, 디자인 등)',
          step: 1
        });
      }, 500); // 0.5초 후 AI 도우미 시작
    }
  }, [isOpen]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const startAIChatbot = () => {
    console.log('RAG 없이 AI 채용공고 작성 도우미 시작');
    setAiChatbot({
      isActive: true,
      currentQuestion: '구인 부서를 알려주세요! (예: 개발, 마케팅, 영업, 디자인 등)',
      step: 1
    });
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
              <Title>🤖 AI 채용공고 등록 도우미 (RAG 없이)</Title>
              <CloseButton onClick={onClose}>
                <FiX />
              </CloseButton>
            </Header>

            <Content>
              <AINotice>
                <FiSettings size={20} />
                RAG 없이 AI 도우미가 단계별로 질문하여 자동으로 입력해드립니다!
              </AINotice>

              <FormSection>
                <SectionTitle>
                  <FiUsers size={18} />
                  구인 정보
                </SectionTitle>
                <FormGrid>
                  <div className="custom-form-group">
                    <label className="custom-label">구인 부서</label>
                    <input
                      type="text"
                      name="department" 
                      value={formData.department || ''} 
                      onChange={handleInputChange}
                      placeholder="예: 개발팀, 기획팀, 마케팅팀"
                      required
                      className="custom-input"
                      style={{
                        borderColor: formData.department ? '#ff6b6b' : '#cbd5e0',
                        boxShadow: formData.department ? '0 0 0 3px rgba(255, 107, 107, 0.2)' : 'none'
                      }}
                    />
                    {formData.department && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#ff6b6b', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.department}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">구인 인원수</label>
                    <input
                      type="text"
                      name="headcount" 
                      value={formData.headcount || ''} 
                      onChange={handleInputChange} 
                      placeholder="예: 1명, 2명, 3명"
                      required 
                      className="custom-input"
                      style={{
                        borderColor: formData.headcount ? '#ff6b6b' : '#cbd5e0',
                        boxShadow: formData.headcount ? '0 0 0 3px rgba(255, 107, 107, 0.2)' : 'none'
                      }}
                    />
                    {formData.headcount && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#ff6b6b', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.headcount}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">주요 업무</label>
                    <textarea
                      name="mainDuties"
                      value={formData.mainDuties || ''}
                      onChange={handleInputChange}
                      placeholder="담당할 주요 업무를 입력해주세요"
                      required
                      className="custom-textarea"
                      style={{
                        borderColor: formData.mainDuties ? '#ff6b6b' : '#cbd5e0',
                        boxShadow: formData.mainDuties ? '0 0 0 3px rgba(255, 107, 107, 0.2)' : 'none'
                      }}
                    />
                    {formData.mainDuties && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#ff6b6b', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.mainDuties.length}자
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">근무 시간</label>
                    <input
                      type="text"
                      name="workHours" 
                      value={formData.workHours || ''} 
                      onChange={handleInputChange} 
                      placeholder="예: 09:00 ~ 18:00, 유연근무제"
                      required 
                      className="custom-input"
                      style={{
                        borderColor: formData.workHours ? '#ff6b6b' : '#cbd5e0',
                        boxShadow: formData.workHours ? '0 0 0 3px rgba(255, 107, 107, 0.2)' : 'none'
                      }}
                    />
                    {formData.workHours && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#ff6b6b', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.workHours}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">근무 요일</label>
                    <input
                      type="text"
                      name="workDays" 
                      value={formData.workDays || ''} 
                      onChange={handleInputChange} 
                      placeholder="예: 월~금, 월~토, 유연근무"
                      required 
                      className="custom-input"
                      style={{
                        borderColor: formData.workDays ? '#ff6b6b' : '#cbd5e0',
                        boxShadow: formData.workDays ? '0 0 0 3px rgba(255, 107, 107, 0.2)' : 'none'
                      }}
                    />
                    {formData.workDays && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#ff6b6b', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.workDays}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">연봉</label>
                    <input
                      type="text"
                      name="salary"
                      value={formData.salary || ''}
                      onChange={handleInputChange}
                      placeholder="예: 3,000만원 ~ 5,000만원, 연봉 협의"
                      className="custom-input"
                      style={{
                        borderColor: formData.salary ? '#ff6b6b' : '#cbd5e0',
                        boxShadow: formData.salary ? '0 0 0 3px rgba(255, 107, 107, 0.2)' : 'none'
                      }}
                    />
                    {formData.salary && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#ff6b6b', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.salary}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">연락처 이메일</label>
                    <input
                      type="email"
                      name="contactEmail"
                      value={formData.contactEmail || ''}
                      onChange={handleInputChange}
                      placeholder="인사담당자 이메일"
                      required
                      className="custom-input"
                      style={{
                        borderColor: formData.contactEmail ? '#ff6b6b' : '#cbd5e0',
                        boxShadow: formData.contactEmail ? '0 0 0 3px rgba(255, 107, 107, 0.2)' : 'none'
                      }}
                    />
                    {formData.contactEmail && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#ff6b6b', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.contactEmail}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">마감일</label>
                    <input
                      type="date"
                      name="deadline"
                      value={formData.deadline || ''}
                      onChange={handleInputChange}
                      required
                      className="custom-input"
                      style={{
                        borderColor: formData.deadline ? '#ff6b6b' : '#cbd5e0',
                        boxShadow: formData.deadline ? '0 0 0 3px rgba(255, 107, 107, 0.2)' : 'none'
                      }}
                    />
                    {formData.deadline && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#ff6b6b', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.deadline}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">경력 요건</label>
                    <input
                      type="text"
                      name="experience"
                      value={formData.experience || ''}
                      onChange={handleInputChange}
                      placeholder="예: 신입, 경력 3년 이상, 경력 무관"
                      className="custom-input"
                      style={{
                        borderColor: formData.experience ? '#ff6b6b' : '#cbd5e0',
                        boxShadow: formData.experience ? '0 0 0 3px rgba(255, 107, 107, 0.2)' : 'none'
                      }}
                    />
                    {formData.experience && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#ff6b6b', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.experience}
                      </div>
                    )}
                  </div>
                </FormGrid>
              </FormSection>

              <ButtonGroup>
                <Button className="secondary" onClick={onClose}>
                  <FiArrowLeft size={16} />
                  취소
                </Button>
                <Button className="secondary" onClick={() => {}}>
                  <FiFolder size={16} />
                  템플릿
                </Button>
                <Button className="ai" onClick={startAIChatbot}>
                  🤖 RAG 없이 AI 도우미 재시작
                </Button>
                <Button className="primary" onClick={() => onComplete(formData)}>
                  <FiCheck size={16} />
                  등록 완료
                </Button>
              </ButtonGroup>
            </Content>
          </Modal>
        </Overlay>
      )}

      {/* RAG 없이 AI 챗봇 */}
      {aiChatbot.isActive && (
        <EnhancedModalChatbot
          isOpen={aiChatbot.isActive}
          onClose={() => setAiChatbot({ isActive: false, currentQuestion: '', step: 1 })}
          onFieldUpdate={(field, value) => {
            console.log('=== TextBasedRegistrationNoRAG - RAG 없이 필드 업데이트 콜백 ===');
            console.log('필드:', field);
            console.log('값:', value);
            console.log('업데이트 전 formData:', formData);
            
            setFormData(prev => {
              const newFormData = { ...prev, [field]: value };
              console.log('업데이트 후 formData:', newFormData);
              return newFormData;
            });
          }}
          onComplete={(data) => {
            console.log('RAG 없이 AI 챗봇 완료:', data);
            setFormData(prev => ({ ...prev, ...data }));
            setAiChatbot({ isActive: false, currentQuestion: '', step: 1 });
          }}
          formData={formData}
          fields={[
            { key: 'department', label: '구인 부서', type: 'text' },
            { key: 'headcount', label: '채용 인원', type: 'text' },
            { key: 'mainDuties', label: '주요 업무', type: 'textarea' },
            { key: 'workHours', label: '근무 시간', type: 'text' },
            { key: 'salary', label: '급여 조건', type: 'text' },
            { key: 'contactEmail', label: '연락처 이메일', type: 'email' },
            { key: 'experience', label: '경력 요건', type: 'text' }
          ]}
          aiAssistant={true}
          ragEnabled={false}
        />
      )}
    </AnimatePresence>
  );
};

export default TextBasedRegistrationNoRAG; 