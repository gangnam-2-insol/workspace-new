import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import TemplateModal from './TemplateModal';
import EnhancedModalChatbot from '../../components/EnhancedModalChatbot';
import { 
  FiX, 
  FiArrowLeft, 
  FiArrowRight,
  FiCheck,
  FiUsers,
  FiBriefcase,
  FiCalendar,
  FiMail,
  FiMapPin,
  FiDollarSign,
  FiAward,
  FiClock,
  FiFileText,
  FiSave,
  FiFolder,
  FiRefreshCw
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
  max-width: 800px;
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

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  margin: 16px 0;
  overflow: hidden;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(135deg, #00c851, #00a844);
  transition: width 0.3s ease;
  width: ${props => props.progress}%;
`;

const StepIndicator = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 32px;
`;

const Step = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
`;

const StepNumber = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: white;
  background: ${props => 
    props.active ? 'linear-gradient(135deg, #00c851, #00a844)' : 
    props.completed ? 'var(--primary-color)' : 'var(--border-color)'
  };
`;

const StepLabel = styled.span`
  font-size: 12px;
  color: ${props => 
    props.active ? 'var(--primary-color)' : 
    props.completed ? 'var(--text-primary)' : 'var(--text-secondary)'
  };
  font-weight: ${props => props.active || props.completed ? '600' : '400'};
`;

const Content = styled.div`
  padding: 32px;
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

const RadioGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const RadioOption = styled.label`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--primary-color);
    background: rgba(0, 200, 81, 0.05);
  }

  &.selected {
    border-color: var(--primary-color);
    background: rgba(0, 200, 81, 0.1);
  }
`;

const RadioInput = styled.input`
  margin: 0;
`;

const RadioText = styled.div`
  flex: 1;
`;

const RadioTitle = styled.div`
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const RadioDescription = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: space-between;
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

const AISuggestion = styled.div`
  background: rgba(0, 200, 81, 0.1);
  border: 1px solid rgba(0, 200, 81, 0.2);
  border-radius: 8px;
  padding: 16px;
  margin-top: 12px;
`;

const AISuggestionTitle = styled.div`
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const AISuggestionText = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
`;

// AI 채용공고 작성 도우미 관련 styled components는 메인 챗봇으로 이동됨

const TextBasedRegistration = ({ 
  isOpen, 
  onClose, 
  onComplete,
  organizationData = { departments: [] }
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [aiChatbot, setAiChatbot] = useState({
    isActive: false,
    currentQuestion: '',
    step: 1
  });
  const [aiResponse, setAiResponse] = useState('');
  
  // 모달이 열릴 때 자동으로 AI 챗봇 시작
  React.useEffect(() => {
    if (isOpen) {
      // 모달이 열린 후 약간의 지연을 두고 AI 챗봇 시작
      const timer = setTimeout(() => {
        setAiChatbot({
          isActive: true,
          currentQuestion: '구인 부서를 알려주세요! (예: 개발, 마케팅, 영업, 디자인 등)',
          step: 1
        });
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

    // 메인 챗봇에서 폼 데이터 업데이트 이벤트 리스너
  React.useEffect(() => {
    const handleExternalAIChatbotResponse = (event) => {
      if (aiChatbot.isActive) {
        const userResponse = event.detail.message;
        handleAIChatbotResponse(userResponse);
      }
    };

    // AI 자동 플로우 시작 이벤트 리스너
    const handleStartTextBasedAIChatbot = () => {
      console.log('=== AI 자동 플로우 시작됨 - 텍스트 기반 등록 ===');
      console.log('현재 aiChatbot 상태:', aiChatbot);
      console.log('현재 isOpen 상태:', isOpen);
      
      setAiChatbot({
        isActive: true,
        currentQuestion: '구인 부서를 알려주세요! (예: 개발, 마케팅, 영업, 디자인 등)',
        step: 1
      });
      
      console.log('AI 챗봇 상태 업데이트 완료');
      console.log('AI 챗봇이 활성화되었습니다. 사용자에게 질문을 시작합니다.');
    };

    // 자동 진행 이벤트 리스너
    const handleAutoProgress = () => {
      console.log('자동 진행 이벤트 수신됨');
      // 자동 진행은 AI 챗봇 내부에서 처리되므로 별도 처리 불필요
    };

    // 채팅봇 수정 명령 이벤트 리스너들
    const handleUpdateDepartment = (event) => {
      const newDepartment = event.detail.value;
      console.log('TextBasedRegistration - 부서 업데이트:', newDepartment);
      setFormData(prev => ({
        ...prev,
        department: newDepartment
      }));
    };

    const handleUpdateHeadcount = (event) => {
      const newHeadcount = event.detail.value;
      console.log('TextBasedRegistration - 인원 업데이트:', newHeadcount);
      setFormData(prev => ({
        ...prev,
        headcount: newHeadcount
      }));
    };

    const handleUpdateSalary = (event) => {
      const newSalary = event.detail.value;
      console.log('TextBasedRegistration - 급여 업데이트:', newSalary);
      setFormData(prev => ({
        ...prev,
        salary: newSalary
      }));
    };

    const handleUpdateWorkContent = (event) => {
      const newWorkContent = event.detail.value;
      console.log('TextBasedRegistration - 업무 내용 업데이트:', newWorkContent);
      setFormData(prev => ({
        ...prev,
        mainDuties: newWorkContent
      }));
    };

    window.addEventListener('aiChatbotResponse', handleExternalAIChatbotResponse);
    window.addEventListener('startTextBasedAIChatbot', handleStartTextBasedAIChatbot);
    window.addEventListener('autoProgress', handleAutoProgress);
    window.addEventListener('updateTextFormDepartment', handleUpdateDepartment);
    window.addEventListener('updateTextFormHeadcount', handleUpdateHeadcount);
    window.addEventListener('updateTextFormSalary', handleUpdateSalary);
    window.addEventListener('updateTextFormWorkContent', handleUpdateWorkContent);
    
    return () => {
      window.removeEventListener('aiChatbotResponse', handleExternalAIChatbotResponse);
      window.removeEventListener('startTextBasedAIChatbot', handleStartTextBasedAIChatbot);
      window.removeEventListener('autoProgress', handleAutoProgress);
      window.removeEventListener('updateTextFormDepartment', handleUpdateDepartment);
      window.removeEventListener('updateTextFormHeadcount', handleUpdateHeadcount);
      window.removeEventListener('updateTextFormSalary', handleUpdateSalary);
      window.removeEventListener('updateTextFormWorkContent', handleUpdateWorkContent);
    };
  }, [aiChatbot.isActive]);
  
  const [formData, setFormData] = useState({
    // Step 1: 구인 부서
    department: '',
    experience: '',
    experienceYears: '',
    
    // Step 2: 구인 정보
    headcount: '',
    mainDuties: '',
    
    // Step 3: 근무 조건
    workHours: '',
    workDays: '',
    locationCity: '',
    locationDistrict: '',
    salary: '',
    
    // Step 4: 전형 절차
    process: ['서류', '실무면접', '최종면접', '입사'],
    
    // Step 5: 지원 방법
    contactEmail: '',
    deadline: ''
  });

  const steps = [
    { number: 1, label: '구인 부서', icon: FiBriefcase },
    { number: 2, label: '구인 정보', icon: FiFileText },
    { number: 3, label: '근무 조건', icon: FiClock },
    { number: 4, label: '전형 절차', icon: FiAward },
    { number: 5, label: '지원 방법', icon: FiMail }
  ];

  const progress = (currentStep / steps.length) * 100;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const sendNotificationEmail = async (jobData) => {
    setIsSendingEmail(true);
    
    try {
      // 이메일 전송 시뮬레이션 (실제로는 API 호출)
      console.log('📧 이메일 전송 중...');
      console.log('받는 사람:', jobData.contactEmail);
      console.log('제목: 채용공고 등록 완료 알림');
      
      // 실제 구현 시 사용할 이메일 템플릿
      const emailTemplate = {
        to: jobData.contactEmail,
        subject: '[채용공고 등록 완료] 새로운 채용공고가 등록되었습니다',
        body: `
          안녕하세요, 인사담당자님!
          
          새로운 채용공고가 성공적으로 등록되었습니다.
          
          📋 채용공고 정보
          - 공고 제목: ${jobData.title || 'AI 생성 제목'}
          - 구인 부서: ${jobData.department}
          - 경력 구분: ${jobData.experience}
          - 구인 인원: ${jobData.headcount}
          - 근무지: ${jobData.locationCity} ${jobData.locationDistrict}
          - 연봉: ${jobData.salary}
          - 마감일: ${jobData.deadline}
          
          🎯 주요 업무
          ${jobData.mainDuties}
          
          📞 지원 문의
          - 이메일: ${jobData.contactEmail}
          - 전형 절차: ${jobData.process?.join(' → ') || '서류 → 실무면접 → 최종면접 → 입사'}
          
          채용공고 관리 시스템에서 언제든지 수정하거나 관리할 수 있습니다.
          
          감사합니다.
          채용관리팀
        `
      };
      
      // 시뮬레이션: 2초 후 완료
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      console.log('✅ 이메일 전송 완료');
      alert(`📧 인사담당자(${jobData.contactEmail})에게 등록 완료 알림 이메일이 전송되었습니다.`);
      
    } catch (error) {
      console.error('❌ 이메일 전송 실패:', error);
      alert('이메일 전송 중 오류가 발생했습니다. 채용공고는 정상적으로 등록되었습니다.');
    } finally {
      setIsSendingEmail(false);
    }
  };

  const handleComplete = async () => {
    // AI 추천 문구 생성 로직
    const aiGeneratedContent = generateAIContent(formData);
    const completeData = { ...formData, ...aiGeneratedContent };
    
    // 채용공고 등록 완료 처리
    onComplete(completeData);
    
    // 인사담당자에게 알림 이메일 전송
    if (formData.contactEmail) {
      await sendNotificationEmail(completeData);
    }
  };

  // AI 챗봇 시작
  // AI 채용공고 작성 도우미 시작 (메인 챗봇에서 호출됨)
  const startAIChatbot = () => {
    // 메인 챗봇에서 AI 모드가 시작되므로 여기서는 별도 처리 불필요
    console.log('AI 채용공고 작성 도우미가 메인 챗봇에서 시작됨');
  };

  // AI 챗봇 응답 처리
  const handleAIChatbotResponse = (userResponse) => {
    const currentStep = aiChatbot.step;
    
    // 현재 단계에 따라 폼 데이터 업데이트
    switch (currentStep) {
      case 1: // 구인 부서
        setFormData(prev => ({ ...prev, department: userResponse }));
        setAiChatbot(prev => ({
          ...prev,
          currentQuestion: '채용 인원은 몇 명인가요? (예: 1명, 2명, 3명)',
          step: 2
        }));
        break;
      case 2: // 채용 인원
        setFormData(prev => ({ ...prev, headcount: userResponse }));
        setAiChatbot(prev => ({
          ...prev,
          currentQuestion: '어떤 업무를 담당하게 되나요? (예: 웹 개발, 디자인, 마케팅)',
          step: 3
        }));
        break;
      case 3: // 업무 내용
        setFormData(prev => ({ ...prev, mainDuties: userResponse }));
        setAiChatbot(prev => ({
          ...prev,
          currentQuestion: '근무 시간은 어떻게 되나요? (예: 09:00-18:00, 유연근무제)',
          step: 4
        }));
        break;
      case 4: // 근무 시간
        setFormData(prev => ({ ...prev, workHours: userResponse }));
        setAiChatbot(prev => ({
          ...prev,
          currentQuestion: '근무 위치는 어디인가요? (예: 서울, 부산, 대구)',
          step: 5
        }));
        break;
      case 5: // 근무 위치
        setFormData(prev => ({ ...prev, locationCity: userResponse }));
        setAiChatbot(prev => ({
          ...prev,
          currentQuestion: '급여 조건은 어떻게 되나요? (예: 면접 후 협의, 3000만원)',
          step: 6
        }));
        break;
      case 6: // 급여 조건
        setFormData(prev => ({ ...prev, salary: userResponse }));
        setAiChatbot(prev => ({
          ...prev,
          currentQuestion: '마감일은 언제인가요? (예: 2024년 12월 31일)',
          step: 7
        }));
        break;
      case 7: // 마감일
        setFormData(prev => ({ ...prev, deadline: userResponse }));
        setAiChatbot(prev => ({
          ...prev,
          currentQuestion: '연락처 이메일을 알려주세요.',
          step: 8
        }));
        break;
      case 8: // 연락처 이메일
        setFormData(prev => ({ ...prev, contactEmail: userResponse }));
        setAiChatbot(prev => ({
          ...prev,
          isActive: false,
          currentQuestion: '',
          step: 1
        }));
        // AI 챗봇 완료 후 다음 단계로 이동
        setTimeout(() => {
          setCurrentStep(2);
        }, 1000);
        break;
      default:
        break;
    }
  };

  // FloatingChatbot에서 보낸 응답을 처리하는 이벤트 리스너

  const handleSaveTemplate = (template) => {
    setTemplates(prev => [...prev, template]);
  };

  const handleLoadTemplate = (templateData) => {
    setFormData(prev => ({ ...prev, ...templateData }));
  };

  const handleDeleteTemplate = (templateId) => {
    setTemplates(prev => prev.filter(template => template.id !== templateId));
  };

  const generateAIContent = (data) => {
    // AI 추천 문구 생성 (실제로는 API 호출)
    return {
      title: `${data.department} ${data.experience} 채용`,
      description: `저희 ${data.department}에서 함께할 ${data.experience}을 모집합니다.`,
      requirements: `• ${data.experience} 경력\n• 관련 분야 전공자\n• 팀워크와 소통 능력`,
      benefits: '• 건강보험, 국민연금\n• 점심식대 지원\n• 자기계발비 지원\n• 경조사 지원'
    };
  };

  const renderStep1 = () => (
    <FormSection>
      <SectionTitle>
        <FiBriefcase size={18} />
        구인 부서 및 경력 선택
      </SectionTitle>
      <FormGrid>
        <FormGroup>
          <Label>구인 부서</Label>
          <Select name="department" value={formData.department} onChange={handleInputChange} required>
            <option value="">부서 선택</option>
            {organizationData.departments && organizationData.departments.length > 0 ? (
              organizationData.departments.map((dept, index) => (
                <option key={index} value={dept.name}>
                  {dept.name} ({dept.count}명)
                </option>
              ))
            ) : (
              <>
                <option value="영업">영업</option>
                <option value="마케팅">마케팅</option>
                <option value="기획">기획</option>
                <option value="디자인">디자인</option>
                <option value="개발">개발</option>
              </>
            )}
          </Select>
          {organizationData.departments && organizationData.departments.length > 0 && (
            <div style={{ 
              marginTop: '8px', 
              fontSize: '12px', 
              color: 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              <FiUsers size={12} />
              조직도에서 설정된 {organizationData.departments.length}개 부서 중 선택
            </div>
          )}
        </FormGroup>
        <FormGroup>
          <Label>경력 구분</Label>
          <RadioGroup>
            <RadioOption className={formData.experience === '신입' ? 'selected' : ''}>
              <RadioInput
                type="radio"
                name="experience"
                value="신입"
                checked={formData.experience === '신입'}
                onChange={handleInputChange}
              />
              <RadioText>
                <RadioTitle>신입</RadioTitle>
                <RadioDescription>경력 없이 신입 채용</RadioDescription>
              </RadioText>
            </RadioOption>
            <RadioOption className={formData.experience === '경력' ? 'selected' : ''}>
              <RadioInput
                type="radio"
                name="experience"
                value="경력"
                checked={formData.experience === '경력'}
                onChange={handleInputChange}
              />
              <RadioText>
                <RadioTitle>경력</RadioTitle>
                <RadioDescription>관련 경력자 채용</RadioDescription>
              </RadioText>
            </RadioOption>
          </RadioGroup>
          {formData.experience === '경력' && (
            <div style={{ marginTop: '12px' }}>
              <Label>경력 연도</Label>
              <Select 
                name="experienceYears" 
                value={formData.experienceYears || ''} 
                onChange={handleInputChange}
                style={{ marginTop: '8px' }}
              >
                <option value="">경력 연도 선택</option>
                <option value="2년이상">2년이상</option>
                <option value="2~3년">2~3년</option>
                <option value="4~5년">4~5년</option>
                <option value="직접입력">직접입력</option>
              </Select>
              {formData.experienceYears === '직접입력' && (
                <Input
                  type="text"
                  name="experienceYearsCustom"
                  value={formData.experienceYearsCustom || ''}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    experienceYears: e.target.value 
                  }))}
                  placeholder="예: 3년 이상"
                  style={{ marginTop: '8px' }}
                />
              )}
            </div>
          )}
        </FormGroup>
      </FormGrid>
    </FormSection>
    );

  const renderStep2 = () => (
    <FormSection>
      <SectionTitle>
        <FiFileText size={18} />
        구인 정보
      </SectionTitle>
      <FormGrid>
        <FormGroup>
          <Label>구인 인원수</Label>
          <Select name="headcount" value={formData.headcount} onChange={handleInputChange} required>
            <option value="">인원 선택</option>
            <option value="1명">1명</option>
            <option value="2명">2명</option>
            <option value="3명">3명</option>
            <option value="4명">4명</option>
            <option value="5명 이상">5명 이상</option>
          </Select>
        </FormGroup>
        <FormGroup>
          <Label>주요 업무</Label>
          <TextArea
            name="mainDuties"
            value={formData.mainDuties}
            onChange={handleInputChange}
            placeholder="담당할 주요 업무를 입력해주세요"
            required
          />
        </FormGroup>
      </FormGrid>
    </FormSection>
  );

  const renderStep3 = () => (
    <FormSection>
      <SectionTitle>
        <FiClock size={18} />
        근무 조건
      </SectionTitle>
      <FormGrid>
        <FormGroup>
          <Label>근무 시간</Label>
          <Select name="workHours" value={formData.workHours} onChange={handleInputChange} required>
            <option value="">근무시간 선택</option>
            <option value="09:00 ~ 18:00">09:00 ~ 18:00</option>
            <option value="10:00 ~ 19:00">10:00 ~ 19:00</option>
            <option value="직접 입력">직접 입력</option>
          </Select>
          {formData.workHours === '직접 입력' && (
            <Input
              type="text"
              name="workHoursCustom"
              value={formData.workHoursCustom || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, workHours: e.target.value }))}
              placeholder="예: 08:30 ~ 17:30"
              style={{ marginTop: '8px' }}
            />
          )}
        </FormGroup>
        <FormGroup>
          <Label>근무 요일</Label>
          <Select name="workDays" value={formData.workDays} onChange={handleInputChange} required>
            <option value="">요일 선택</option>
            <option value="월~금">월~금</option>
            <option value="월~토">월~토</option>
            <option value="유연근무">유연근무</option>
          </Select>
        </FormGroup>
        <FormGroup>
          <Label>근무지</Label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Select 
              name="locationCity" 
              value={formData.locationCity || ''} 
              onChange={(e) => {
                setFormData(prev => ({ 
                  ...prev, 
                  locationCity: e.target.value,
                  locationDistrict: '' // 시가 변경되면 구 초기화
                }));
              }}
              style={{ flex: 1 }}
              required
            >
              <option value="">시 선택</option>
              <option value="서울특별시">서울특별시</option>
              <option value="부산광역시">부산광역시</option>
              <option value="대구광역시">대구광역시</option>
              <option value="인천광역시">인천광역시</option>
              <option value="광주광역시">광주광역시</option>
              <option value="대전광역시">대전광역시</option>
              <option value="울산광역시">울산광역시</option>
              <option value="세종특별자치시">세종특별자치시</option>
              <option value="경기도">경기도</option>
              <option value="강원도">강원도</option>
              <option value="충청북도">충청북도</option>
              <option value="충청남도">충청남도</option>
              <option value="전라북도">전라북도</option>
              <option value="전라남도">전라남도</option>
              <option value="경상북도">경상북도</option>
              <option value="경상남도">경상남도</option>
              <option value="제주특별자치도">제주특별자치도</option>
            </Select>
            <Select 
              name="locationDistrict" 
              value={formData.locationDistrict || ''} 
              onChange={(e) => setFormData(prev => ({ ...prev, locationDistrict: e.target.value }))}
              style={{ flex: 1 }}
              required
              disabled={!formData.locationCity}
            >
              <option value="">구 선택</option>
              {formData.locationCity === '서울특별시' && (
                <>
                  <option value="강남구">강남구</option>
                  <option value="강동구">강동구</option>
                  <option value="강북구">강북구</option>
                  <option value="강서구">강서구</option>
                  <option value="관악구">관악구</option>
                  <option value="광진구">광진구</option>
                  <option value="구로구">구로구</option>
                  <option value="금천구">금천구</option>
                  <option value="노원구">노원구</option>
                  <option value="도봉구">도봉구</option>
                  <option value="동대문구">동대문구</option>
                  <option value="동작구">동작구</option>
                  <option value="마포구">마포구</option>
                  <option value="서대문구">서대문구</option>
                  <option value="서초구">서초구</option>
                  <option value="성동구">성동구</option>
                  <option value="성북구">성북구</option>
                  <option value="송파구">송파구</option>
                  <option value="양천구">양천구</option>
                  <option value="영등포구">영등포구</option>
                  <option value="용산구">용산구</option>
                  <option value="은평구">은평구</option>
                  <option value="종로구">종로구</option>
                  <option value="중구">중구</option>
                  <option value="중랑구">중랑구</option>
                </>
              )}
              {formData.locationCity === '부산광역시' && (
                <>
                  <option value="강서구">강서구</option>
                  <option value="금정구">금정구</option>
                  <option value="남구">남구</option>
                  <option value="동구">동구</option>
                  <option value="동래구">동래구</option>
                  <option value="부산진구">부산진구</option>
                  <option value="북구">북구</option>
                  <option value="사상구">사상구</option>
                  <option value="사하구">사하구</option>
                  <option value="서구">서구</option>
                  <option value="수영구">수영구</option>
                  <option value="연제구">연제구</option>
                  <option value="영도구">영도구</option>
                  <option value="중구">중구</option>
                  <option value="해운대구">해운대구</option>
                  <option value="기장군">기장군</option>
                </>
              )}
              {formData.locationCity === '대구광역시' && (
                <>
                  <option value="남구">남구</option>
                  <option value="달서구">달서구</option>
                  <option value="달성군">달성군</option>
                  <option value="동구">동구</option>
                  <option value="북구">북구</option>
                  <option value="서구">서구</option>
                  <option value="수성구">수성구</option>
                  <option value="중구">중구</option>
                </>
              )}
              {formData.locationCity === '인천광역시' && (
                <>
                  <option value="계양구">계양구</option>
                  <option value="남구">남구</option>
                  <option value="남동구">남동구</option>
                  <option value="동구">동구</option>
                  <option value="부평구">부평구</option>
                  <option value="서구">서구</option>
                  <option value="연수구">연수구</option>
                  <option value="중구">중구</option>
                  <option value="강화군">강화군</option>
                  <option value="옹진군">옹진군</option>
                </>
              )}
              {formData.locationCity === '광주광역시' && (
                <>
                  <option value="광산구">광산구</option>
                  <option value="남구">남구</option>
                  <option value="동구">동구</option>
                  <option value="북구">북구</option>
                  <option value="서구">서구</option>
                </>
              )}
              {formData.locationCity === '대전광역시' && (
                <>
                  <option value="대덕구">대덕구</option>
                  <option value="동구">동구</option>
                  <option value="서구">서구</option>
                  <option value="유성구">유성구</option>
                  <option value="중구">중구</option>
                </>
              )}
              {formData.locationCity === '울산광역시' && (
                <>
                  <option value="남구">남구</option>
                  <option value="동구">동구</option>
                  <option value="북구">북구</option>
                  <option value="울주군">울주군</option>
                  <option value="중구">중구</option>
                </>
              )}
              {formData.locationCity === '경기도' && (
                <>
                  <option value="수원시">수원시</option>
                  <option value="성남시">성남시</option>
                  <option value="의정부시">의정부시</option>
                  <option value="안양시">안양시</option>
                  <option value="부천시">부천시</option>
                  <option value="광명시">광명시</option>
                  <option value="평택시">평택시</option>
                  <option value="동두천시">동두천시</option>
                  <option value="안산시">안산시</option>
                  <option value="고양시">고양시</option>
                  <option value="과천시">과천시</option>
                  <option value="구리시">구리시</option>
                  <option value="남양주시">남양주시</option>
                  <option value="오산시">오산시</option>
                  <option value="시흥시">시흥시</option>
                  <option value="군포시">군포시</option>
                  <option value="의왕시">의왕시</option>
                  <option value="하남시">하남시</option>
                  <option value="용인시">용인시</option>
                  <option value="파주시">파주시</option>
                  <option value="이천시">이천시</option>
                  <option value="안성시">안성시</option>
                  <option value="김포시">김포시</option>
                  <option value="화성시">화성시</option>
                  <option value="광주시">광주시</option>
                  <option value="여주시">여주시</option>
                  <option value="양평군">양평군</option>
                  <option value="고양군">고양군</option>
                  <option value="연천군">연천군</option>
                  <option value="가평군">가평군</option>
                </>
              )}
            </Select>
          </div>
        </FormGroup>
        <FormGroup>
          <Label>연봉</Label>
          <Input
            type="text"
            name="salary"
            value={formData.salary}
            onChange={handleInputChange}
            placeholder="예: 3,000만원 ~ 5,000만원"
          />
        </FormGroup>
      </FormGrid>
    </FormSection>
  );

  const renderStep4 = () => (
    <FormSection>
      <SectionTitle>
        <FiAward size={18} />
        전형 절차
      </SectionTitle>
      <FormGroup>
        <Label>전형 절차 (기본값: 서류 → 실무면접 → 최종면접 → 입사)</Label>
        <TextArea
          name="process"
          value={formData.process.join(' → ')}
          onChange={(e) => setFormData(prev => ({ ...prev, process: e.target.value.split(' → ') }))}
          placeholder="서류 → 실무면접 → 최종면접 → 입사"
        />
      </FormGroup>
    </FormSection>
  );

  const renderStep5 = () => (
    <FormSection>
      <SectionTitle>
        <FiMail size={18} />
        지원 방법
      </SectionTitle>
      <FormGrid>
        <FormGroup>
          <Label>연락처 이메일</Label>
          <Input
            type="email"
            name="contactEmail"
            value={formData.contactEmail}
            onChange={handleInputChange}
            placeholder="인사담당자 이메일"
            required
          />
        </FormGroup>
        <FormGroup>
          <Label>마감일</Label>
          <Input
            type="date"
            name="deadline"
            value={formData.deadline}
            onChange={handleInputChange}
            required
          />
        </FormGroup>
      </FormGrid>
    </FormSection>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      case 4: return renderStep4();
      case 5: return renderStep5();
      default: return null;
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
              <Title>텍스트 기반 채용공고 등록</Title>
              <CloseButton onClick={onClose}>
                <FiX />
              </CloseButton>
            </Header>

            <Content>
              <ProgressBar>
                <ProgressFill progress={progress} />
              </ProgressBar>

              <StepIndicator>
                {steps.map((step) => (
                  <Step key={step.number}>
                    <StepNumber 
                      active={currentStep === step.number}
                      completed={currentStep > step.number}
                    >
                      {currentStep > step.number ? <FiCheck size={16} /> : step.number}
                    </StepNumber>
                    <StepLabel 
                      active={currentStep === step.number}
                      completed={currentStep > step.number}
                    >
                      {step.label}
                    </StepLabel>
                  </Step>
                ))}
              </StepIndicator>

              {renderCurrentStep()}

              <ButtonGroup>
                <Button 
                  className="secondary" 
                  onClick={currentStep === 1 ? onClose : handlePrev}
                >
                  <FiArrowLeft size={16} />
                  {currentStep === 1 ? '취소' : '이전'}
                </Button>
                {currentStep === 1 && (
                  <>
                    <Button 
                      className="secondary" 
                      onClick={() => setShowTemplateModal(true)}
                    >
                      <FiFolder size={16} />
                      템플릿
                    </Button>
                    <Button 
                      className="primary" 
                      onClick={startAIChatbot}
                      style={{ background: 'linear-gradient(135deg, #ff6b6b, #ee5a52)' }}
                    >
                      🤖 AI 도우미
                    </Button>
                  </>
                )}
                <Button 
                  className="primary" 
                  onClick={currentStep === steps.length ? handleComplete : handleNext}
                  disabled={currentStep === steps.length && isSendingEmail}
                >
                  {currentStep === steps.length ? (
                    isSendingEmail ? (
                      <>
                        <FiRefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                        이메일 전송 중...
                      </>
                    ) : (
                      '완료'
                    )
                  ) : (
                    <>
                      다음
                      <FiArrowRight size={16} />
                    </>
                  )}
                </Button>
              </ButtonGroup>
            </Content>
          </Modal>
        </Overlay>
      )}

      {/* AI 챗봇이 활성화될 때 EnhancedModalChatbot 표시 */}
      {aiChatbot.isActive && (
        <EnhancedModalChatbot
          isOpen={aiChatbot.isActive}
          onClose={() => setAiChatbot({ isActive: false, currentQuestion: '', step: 1 })}
          title="AI 채용공고 작성 도우미"
          onFieldUpdate={(field, value) => {
            console.log('AI 챗봇에서 필드 업데이트:', field, value);
            setFormData(prev => ({
              ...prev,
              [field]: value
            }));
          }}
          onComplete={(data) => {
            console.log('AI 챗봇 완료:', data);
            setFormData(prev => ({ ...prev, ...data }));
            setAiChatbot({ isActive: false, currentQuestion: '', step: 1 });
          }}
          fields={[
            { key: 'department', label: '구인 부서', type: 'text' },
            { key: 'headcount', label: '채용 인원', type: 'text' },
            { key: 'mainDuties', label: '주요 업무', type: 'textarea' },
            { key: 'workHours', label: '근무 시간', type: 'text' },
            { key: 'locationCity', label: '근무 위치', type: 'text' },
            { key: 'salary', label: '급여 조건', type: 'text' },
            { key: 'deadline', label: '마감일', type: 'date' },
            { key: 'contactEmail', label: '연락처 이메일', type: 'email' }
          ]}
          aiAssistant={true}
        >
          <div>
            <h3>현재 입력된 정보</h3>
            <div style={{ fontSize: '14px', color: '#666' }}>
              <p><strong>구인 부서:</strong> {formData.department || '미입력'}</p>
              <p><strong>채용 인원:</strong> {formData.headcount || '미입력'}</p>
              <p><strong>주요 업무:</strong> {formData.mainDuties || '미입력'}</p>
              <p><strong>근무 시간:</strong> {formData.workHours || '미입력'}</p>
              <p><strong>근무 위치:</strong> {formData.locationCity || '미입력'}</p>
              <p><strong>급여 조건:</strong> {formData.salary || '미입력'}</p>
              <p><strong>마감일:</strong> {formData.deadline || '미입력'}</p>
              <p><strong>연락처:</strong> {formData.contactEmail || '미입력'}</p>
            </div>
          </div>
        </EnhancedModalChatbot>
      )}

      <TemplateModal
        isOpen={showTemplateModal}
        onClose={() => setShowTemplateModal(false)}
        onSaveTemplate={handleSaveTemplate}
        onLoadTemplate={handleLoadTemplate}
        onDeleteTemplate={handleDeleteTemplate}
        templates={templates}
        currentData={formData}
      />
    </AnimatePresence>
  );
};

export default TextBasedRegistration; 