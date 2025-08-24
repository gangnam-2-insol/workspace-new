import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
// EnhancedModalChatbot 컴포넌트 제거됨
import { FiX, FiArrowLeft, FiArrowRight, FiCheck, FiFileText, FiClock, FiMapPin, FiDollarSign, FiUsers, FiMail, FiCalendar, FiFolder, FiSettings } from 'react-icons/fi';
import './LangGraphJobRegistration.css';

// UI 토스트/알림 및 상단 안내 배너 노출 제어
const SHOW_AI_TOASTS = false;

// Styled Components
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
  width: 70%;
  height: 100%;
  max-width: 85%;
  max-height: 95vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  margin-left: 2%;
  margin-right: auto;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  
  ${props => !props.aiActive && `
    width: 90%;
    max-width: 85%;
    margin-left: auto;
    margin-right: auto;
  `}
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
  padding-right: 16px;
  max-height: calc(95vh - 120px);
  overflow-y: auto;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  
  ${props => !props.aiActive && `
    padding-right: 32px;
  `}
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

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
`;

const Button = styled.button`
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;

  &.primary {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
    }
  }

  &.secondary {
    background: #f8f9fa;
    color: var(--text-primary);
    border: 2px solid #e2e8f0;

    &:hover {
      background: #e9ecef;
      border-color: #ced4da;
    }
  }

  &.ai {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
    }
  }
`;

const AINotice = styled.div`
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
`;

const LangGraphJobRegistration = ({ isOpen, onClose, initialData = {} }) => {
  // 랭그래프 모드 닫기 시 기존 세트를 다시 열기 위한 함수
  const handleClose = () => {
    console.log('=== 랭그래프 모드 닫기 - 기존 세트 복원 시작 ===');
    
    // 1. 플로팅 챗봇 다시 표시
    const floatingChatbot = document.querySelector('.floating-chatbot');
    if (floatingChatbot) {
      floatingChatbot.style.display = 'flex';
    }
    
    // 2. 기존 세트 복원 이벤트 발생
    window.dispatchEvent(new CustomEvent('restoreOriginalSet'));
    
    // 3. 랭그래프 모드 닫기
    onClose();
    
    console.log('=== 랭그래프 모드 닫기 - 기존 세트 복원 완료 ===');
  };
  const [formData, setFormData] = useState({
    department: '',
    position: '',
    headcount: '',
    experience: '',
    experienceYears: '',
    workType: '',
    workHours: '',
    workDays: '',
    locationCity: '',
    locationDistrict: '',
    salary: '',
    mainDuties: '',
    requirements: '',
    benefits: '',
    contactEmail: '',
    deadline: '',
    ...initialData
  });

  const [aiChatbot, setAiChatbot] = useState({
    isActive: true  // LangGraph 페이지가 열리면 AI 어시스턴트도 자동으로 열기
  });

  // 준비중 상태 관리
  const [isPreparing, setIsPreparing] = useState(true);
  const [preparationMessage, setPreparationMessage] = useState('채용공고 등록 도우미_for langgraph 준비중...');

  // 랭그래프 모드 강제 설정
  useEffect(() => {
    if (isOpen && aiChatbot.isActive) {
      console.log('=== LangGraph 모드 강제 설정 ===');
      // 랭그래프 모드 시작 이벤트 발생
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('forceLangGraphMode'));
      }, 500);
    }
  }, [isOpen, aiChatbot.isActive]);

  // AI에서 추출된 텍스트를 분석하여 동적 폼 필드로 변환
  const [dynamicFields, setDynamicFields] = useState([]);
  const [extractedText, setExtractedText] = useState('');
  
  // 토스트 메시지 상태
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  // 텍스트를 분석하여 폼 필드로 변환하는 함수
  const analyzeTextAndCreateFields = (text) => {
    const fields = [];
    const extractedData = {};

    // 부서 정보 추출
    const deptMatch = text.match(/(개발팀|마케팅팀|영업팀|인사팀|기획팀|디자인팀|운영팀|고객지원팀|재무팀|법무팀|IT팀|기술팀)/);
    if (deptMatch) {
      fields.push({
        id: 'department',
        label: '구인 부서',
        type: 'text',
        value: deptMatch[1],
        required: true,
        icon: '🏢'
      });
      extractedData.department = deptMatch[1];
    }

    // 직무 정보 추출
    const positionMatch = text.match(/(개발자|프로그래머|엔지니어|매니저|대리|과장|차장|부장|사원|인턴|디자이너|기획자|마케터|영업사원)/);
    if (positionMatch) {
      fields.push({
        id: 'position',
        label: '직무명',
        type: 'text',
        value: positionMatch[1],
        required: true,
        icon: '👨‍💼'
      });
      extractedData.position = positionMatch[1];
    }

    // 인원 수 추출
    const headcountMatch = text.match(/(\d+)명/);
    if (headcountMatch) {
      fields.push({
        id: 'headcount',
        label: '채용 인원',
        type: 'select',
        value: headcountMatch[1] + '명',
        options: ['1명', '2명', '3명', '5명', '10명'],
        required: true,
        icon: '👥'
      });
      extractedData.headcount = headcountMatch[1] + '명';
    }

    // 경력 요건 추출
    if (text.includes('신입')) {
      fields.push({
        id: 'experience',
        label: '경력 요건',
        type: 'select',
        value: '신입',
        options: ['신입', '경력', '신입/경력'],
        required: true,
        icon: '🎓'
      });
      extractedData.experience = '신입';
    } else if (text.includes('경력')) {
      fields.push({
        id: 'experience',
        label: '경력 요건',
        type: 'select',
        value: '경력',
        options: ['신입', '경력', '신입/경력'],
        required: true,
        icon: '🎓'
      });
      extractedData.experience = '경력';
    }

    // 급여 정보 추출
    const salaryMatch = text.match(/(\d+)[천만]원/);
    if (salaryMatch) {
      fields.push({
        id: 'salary',
        label: '연봉',
        type: 'text',
        value: salaryMatch[1] + '만원',
        required: true,
        icon: '💰'
      });
      extractedData.salary = salaryMatch[1] + '만원';
    }

    // 지역 정보 추출
    const locationMatch = text.match(/(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)/);
    if (locationMatch) {
      fields.push({
        id: 'locationCity',
        label: '근무 지역',
        type: 'select',
        value: locationMatch[1],
        options: ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'],
        required: true,
        icon: '📍'
      });
      extractedData.locationCity = locationMatch[1];
    }

    // 근무 시간 추출
    const workTimeMatch = text.match(/(\d{1,2}):(\d{2})\s*[~-]\s*(\d{1,2}):(\d{2})/);
    if (workTimeMatch) {
      fields.push({
        id: 'workHours',
        label: '근무 시간',
        type: 'text',
        value: `${workTimeMatch[1]}:${workTimeMatch[2]} ~ ${workTimeMatch[3]}:${workTimeMatch[4]}`,
        required: true,
        icon: '⏰'
      });
      extractedData.workHours = `${workTimeMatch[1]}:${workTimeMatch[2]} ~ ${workTimeMatch[3]}:${workTimeMatch[4]}`;
    }

    // 근무 형태 추출
    if (text.includes('정규직')) {
      fields.push({
        id: 'workType',
        label: '근무 형태',
        type: 'select',
        value: '정규직',
        options: ['정규직', '계약직', '인턴', '프리랜서'],
        required: true,
        icon: '💼'
      });
      extractedData.workType = '정규직';
    }

    // 추가 정보 (자유 텍스트)
    if (text.length > 50) {
      fields.push({
        id: 'additionalInfo',
        label: '추가 정보',
        type: 'textarea',
        value: text,
        required: false,
        icon: '📝'
      });
      extractedData.additionalInfo = text;
    }

    return { fields, extractedData };
  };

  // AI에서 추출된 데이터를 받아서 동적 폼으로 변환
  useEffect(() => {
    console.log('[LangGraphJobRegistration] 컴포넌트 마운트됨 - 이벤트 리스너 등록 시작');
    
    let processingTimeout;
    
    const handleLangGraphDataUpdate = (event) => {
      console.log('[LangGraphJobRegistration] ✅ 이벤트 수신 성공!');
      console.log('[LangGraphJobRegistration] 이벤트 수신:', event);
      console.log('[LangGraphJobRegistration] event.detail:', event.detail);
      const { action, data } = event.detail;
      
      console.log('[LangGraphJobRegistration] action:', action);
      console.log('[LangGraphJobRegistration] data:', data);
      console.log('[LangGraphJobRegistration] data 타입:', typeof data);
      console.log('[LangGraphJobRegistration] data 키 개수:', data ? Object.keys(data).length : 0);
      
      if (action === 'updateLangGraphData' && data && Object.keys(data).length > 0) {
        // 중복 처리 방지
        if (processingTimeout) {
          clearTimeout(processingTimeout);
        }
        
        processingTimeout = setTimeout(() => {
          console.log('[LangGraphJobRegistration] AI에서 추출된 데이터 수신:', data);
          console.log('[LangGraphJobRegistration] 추출된 필드들:', Object.keys(data));
          console.log('[LangGraphJobRegistration] 추출된 값들:', Object.values(data));
          
          // 준비중 상태 해제 (조용히)
          setIsPreparing(false);
          setPreparationMessage('');
        
          // 텍스트 데이터인 경우 분석하여 동적 폼 생성
          if (typeof data === 'string') {
            setExtractedText(data);
            const { fields, extractedData } = analyzeTextAndCreateFields(data);
            setDynamicFields(fields);
            
            // 기존 데이터와 병합하여 업데이트
            setFormData(prev => {
              const updatedData = { ...prev, ...extractedData };
              console.log('[LangGraphJobRegistration] 폼 데이터 업데이트:', updatedData);
              return updatedData;
            });
            
            displayToast(`✅ AI에서 추출한 정보를 분석하여 ${fields.length}개의 폼 필드를 생성했습니다!`);
          } else {
            // 객체 데이터인 경우 동적 폼 생성
            if (typeof data === 'object' && data !== null) {
              // 키-값 쌍으로 동적 폼 필드 생성
              const dynamicFormFields = [];
              const fieldTitles = {
                'department': '구인 부서',
                'position': '직무명',
                'headcount': '모집인원',
                'experience': '경력요건',
                'experienceYears': '경력연차',
                'workType': '근무형태',
                'workHours': '근무시간',
                'workDays': '근무요일',
                'locationCity': '근무위치(도시)',
                'locationDistrict': '근무위치(구/군)',
                'salary': '연봉',
                'mainDuties': '주요업무',
                'requirements': '자격요건',
                'benefits': '복리후생',
                'contactEmail': '연락처 이메일',
                'deadline': '마감일'
              };
              
              // 각 키-값 쌍에 대해 동적 폼 필드 생성
              console.log('[LangGraphJobRegistration] fieldTitles:', fieldTitles);
              Object.entries(data).forEach(([key, value]) => {
                console.log(`[LangGraphJobRegistration] 처리 중인 필드: ${key} = ${value}`);
                console.log(`[LangGraphJobRegistration] fieldTitles[${key}]:`, fieldTitles[key]);
                console.log(`[LangGraphJobRegistration] value 존재 여부:`, !!value);
                
                if (value && fieldTitles[key]) {
                  const field = {
                    id: key,
                    label: fieldTitles[key],
                    type: getFieldType(key, value),
                    value: value,
                    required: isRequiredField(key),
                    icon: getFieldIcon(key),
                    options: getFieldOptions(key)
                  };
                  dynamicFormFields.push(field);
                  console.log(`[LangGraphJobRegistration] 동적 폼 필드 생성: ${key} = ${value}`);
                } else {
                  console.log(`[LangGraphJobRegistration] 필드 생성 실패: ${key} = ${value} (fieldTitles[${key}]: ${fieldTitles[key]})`);
                }
              });
              
              // 동적 폼 필드 설정
              setDynamicFields(dynamicFormFields);
              
              // 폼 데이터 업데이트
              setFormData(prev => {
                const updatedData = { ...prev, ...data };
                console.log('[LangGraphJobRegistration] 동적 폼 데이터 업데이트:', updatedData);
                return updatedData;
              });
              
              displayToast(`✅ AI에서 추출한 정보로 ${dynamicFormFields.length}개의 폼 필드를 생성했습니다!`);
            }
          }
        }, 100);
      }
    };
    
    // 필드 타입 결정 함수
    const getFieldType = (key, value) => {
      if (key === 'mainDuties' || key === 'requirements' || key === 'benefits') {
        return 'textarea';
      } else if (key === 'contactEmail') {
        return 'email';
      } else if (key === 'deadline') {
        return 'date';
      } else if (key === 'experience' || key === 'workType' || key === 'workDays') {
        return 'select';
      } else {
        return 'text';
      }
    };
    
    // 필수 필드 여부 결정 함수
    const isRequiredField = (key) => {
      const requiredFields = ['department', 'position', 'headcount', 'experience'];
      return requiredFields.includes(key);
    };
    
    // 필드 아이콘 결정 함수
    const getFieldIcon = (key) => {
      const icons = {
        'department': '🏢',
        'position': '👨‍💼',
        'headcount': '👥',
        'experience': '🎓',
        'experienceYears': '📅',
        'workType': '💼',
        'workHours': '⏰',
        'workDays': '📅',
        'locationCity': '📍',
        'locationDistrict': '🏢',
        'salary': '💰',
        'mainDuties': '📝',
        'requirements': '✅',
        'benefits': '🎉',
        'contactEmail': '📧',
        'deadline': '⏰'
      };
      return icons[key] || '📋';
    };
    
    // 필드 옵션 결정 함수
    const getFieldOptions = (key) => {
      const options = {
        'experience': ['신입', '경력', '신입/경력'],
        'workType': ['정규직', '계약직', '인턴', '파트타임'],
        'workDays': ['월~금', '월~토', '평일']
      };
      return options[key] || [];
    };
    
    // 이벤트 리스너 등록
    console.log('[LangGraphJobRegistration] 이벤트 리스너 등록: langGraphDataUpdate');
    window.addEventListener('langGraphDataUpdate', handleLangGraphDataUpdate);
    
    return () => {
      console.log('[LangGraphJobRegistration] 컴포넌트 언마운트 - 이벤트 리스너 해제');
      window.removeEventListener('langGraphDataUpdate', handleLangGraphDataUpdate);
    };
  }, []);

  // 토스트 알림 상태 (이미 위에서 선언됨)
  
  const displayToast = (message) => {
    if (!SHOW_AI_TOASTS) return;
    setToastMessage(message);
    setShowToast(true);
    
    // 5초 후 토스트 숨기기
    setTimeout(() => {
      setShowToast(false);
    }, 5000);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('LangGraph 채용공고 등록:', formData);
    // 여기서 실제 제출 로직 구현
    alert('LangGraph 채용공고 등록이 완료되었습니다!');
    handleClose();
  };

  const handleTestAutoFill = () => {
    const testData = {
      department: '개발팀',
      position: '백엔드 개발자',
      headcount: '2명',
      experience: '경력',
      experienceYears: '3년 이상',
      workType: '정규직',
      workHours: '09:00 ~ 18:00',
      workDays: '월~금',
      locationCity: '서울',
      locationDistrict: '강남구',
      salary: '4,000만원 ~ 6,000만원',
      mainDuties: '웹 서비스 백엔드 개발 및 운영, API 설계 및 구현, 데이터베이스 설계 및 최적화, 마이크로서비스 아키텍처 설계',
      requirements: 'Java/Spring Boot 경험 3년 이상, RESTful API 설계 경험, MySQL/PostgreSQL 사용 경험, Docker/Kubernetes 경험 우대',
      benefits: '점심식대 지원, 야근식대 지원, 경조사 지원, 생일 축하금, 명절 선물, 연차휴가, 건강검진, 교육비 지원',
      contactEmail: 'hr@company.com',
      deadline: '2024-12-31'
    };
    
    setFormData(testData);
    
    // 사용자에게 알림
    alert('🧪 테스트 데이터가 자동으로 입력되었습니다!\n\n📋 입력된 정보:\n• 부서: 개발팀\n• 직무: 백엔드 개발자\n• 모집인원: 2명\n• 경력: 3년 이상\n• 근무형태: 정규직\n• 근무시간: 09:00-18:00\n• 근무일: 월-금\n• 근무위치: 서울 강남구\n• 연봉: 4,000만원-6,000만원\n• 연락처: hr@company.com\n• 마감일: 2024-12-31');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <Overlay
          key="langgraph-overlay"
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
            aiActive={aiChatbot.isActive}
          >
            <Header>
              <Title>AI 채용공고 등록 도우미_for LangGraph</Title>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <button
                  onClick={() => setAiChatbot(prev => ({ ...prev, isActive: true }))}
                  style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    color: 'white',
                    fontSize: '12px',
                    cursor: 'pointer',
                    padding: '6px 12px',
                    borderRadius: '16px',
                    marginRight: '12px',
                    transition: 'all 0.3s ease',
                    fontWeight: '500'
                  }}
                  onMouseEnter={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.3)'}
                  onMouseLeave={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.2)'}
                >
                  🤖 AI 어시스턴트
                </button>
                <button
                  onClick={handleTestAutoFill}
                  style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    color: 'white',
                    fontSize: '12px',
                    cursor: 'pointer',
                    padding: '6px 12px',
                    borderRadius: '16px',
                    marginRight: '12px',
                    transition: 'all 0.3s ease',
                    fontWeight: '500'
                  }}
                  onMouseEnter={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.3)'}
                  onMouseLeave={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.2)'}
                >
                  🧪 테스트 데이터
                </button>
                <CloseButton onClick={handleClose}>
                  <FiX />
                </CloseButton>
              </div>
            </Header>

            <Content aiActive={aiChatbot.isActive}>
              {/* 준비중 상태 표시 */}
              {isPreparing && (
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '300px',
                  textAlign: 'center',
                  color: '#666',
                  background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                  borderRadius: '12px',
                  margin: '20px 0',
                  border: '2px dashed #cbd5e0'
                }}>
                  <div style={{
                    fontSize: '48px',
                    marginBottom: '16px',
                    animation: 'pulse 2s infinite'
                  }}>
                    ⏳
                  </div>
                  <h3 style={{
                    fontSize: '20px',
                    fontWeight: '600',
                    marginBottom: '8px',
                    color: '#374151'
                  }}>
                    {preparationMessage}
                  </h3>
                  <p style={{
                    fontSize: '14px',
                    color: '#6b7280',
                    maxWidth: '400px',
                    lineHeight: '1.5'
                  }}>
                    AI가 채팅창에서 추출한 정보를 분석하여 동적 폼을 생성하고 있습니다...
                  </p>
                  <div style={{
                    marginTop: '20px',
                    padding: '12px 24px',
                    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    color: 'white',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '500'
                  }}>
                    🤖 AI 어시스턴트에서 채용 정보를 입력해주세요
                  </div>
                </div>
              )}

              {/* 준비 완료 후 폼 표시 */}
              {!isPreparing && (
                <>
                  {SHOW_AI_TOASTS && (
                    <AINotice>
                      <FiSettings size={20} />
                      LangGraph AI가 단계별로 질문하여 자동으로 입력해드립니다! (LangGraph 템플릿 기반)
                    </AINotice>
                  )}

                  <form onSubmit={handleSubmit}>
                {/* 동적 폼 필드 렌더링 */}
                {dynamicFields.length > 0 && (
                  <FormSection>
                    <SectionTitle>
                      <FiSettings size={18} />
                      AI 추출 정보 (수정 가능)
                    </SectionTitle>
                    <FormGrid>
                      {dynamicFields.map((field) => (
                        <div key={field.id} className="custom-form-group">
                          <label className="custom-label">
                            {field.icon} {field.label}
                            {field.required && <span style={{ color: '#ef4444' }}> *</span>}
                          </label>
                          
                          {field.type === 'text' && (
                            <input
                              type="text"
                              name={field.id}
                              value={formData[field.id] || field.value || ''}
                              onChange={handleInputChange}
                              placeholder={`${field.label} 입력`}
                              required={field.required}
                              className="custom-input"
                              style={{
                                borderColor: formData[field.id] ? '#f093fb' : '#cbd5e0',
                                boxShadow: formData[field.id] ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                              }}
                            />
                          )}
                          
                          {field.type === 'select' && (
                            <select
                              name={field.id}
                              value={formData[field.id] || field.value || ''}
                              onChange={handleInputChange}
                              required={field.required}
                              className="custom-input"
                              style={{
                                borderColor: formData[field.id] ? '#f093fb' : '#cbd5e0',
                                boxShadow: formData[field.id] ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                              }}
                            >
                              <option value="">선택해주세요</option>
                              {field.options?.map(option => (
                                <option key={option} value={option}>{option}</option>
                              ))}
                            </select>
                          )}
                          
                          {field.type === 'textarea' && (
                            <textarea
                              name={field.id}
                              value={formData[field.id] || field.value || ''}
                              onChange={handleInputChange}
                              placeholder={`${field.label} 입력`}
                              required={field.required}
                              className="custom-textarea"
                              style={{
                                borderColor: formData[field.id] ? '#f093fb' : '#cbd5e0',
                                boxShadow: formData[field.id] ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                              }}
                            />
                          )}
                          
                          {(formData[field.id] || field.value) && (
                            <div style={{ 
                              fontSize: '0.8em', 
                              color: '#f093fb', 
                              marginTop: '4px',
                              fontWeight: 'bold'
                            }}>
                              ✅ AI 추출: {formData[field.id] || field.value}
                            </div>
                          )}
                        </div>
                      ))}
                    </FormGrid>
                  </FormSection>
                )}

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
                          borderColor: formData.department ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.department ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.department && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.department}
                        </div>
                      )}
                    </div>

                    <div className="custom-form-group">
                      <label className="custom-label">직무명</label>
                      <input
                        type="text"
                        name="position" 
                        value={formData.position || ''} 
                        onChange={handleInputChange}
                        placeholder="예: 백엔드 개발자, 프론트엔드 개발자"
                        required
                        className="custom-input"
                        style={{
                          borderColor: formData.position ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.position ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.position && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.position}
                        </div>
                      )}
                    </div>

                    <div className="custom-form-group">
                      <label className="custom-label">채용 인원</label>
                      <input
                        type="text"
                        name="headcount" 
                        value={formData.headcount || ''} 
                        onChange={handleInputChange}
                        placeholder="예: 2명, 3명"
                        required
                        className="custom-input"
                        style={{
                          borderColor: formData.headcount ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.headcount ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.headcount && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.headcount}
                        </div>
                      )}
                    </div>

                    <div className="custom-form-group">
                      <label className="custom-label">경력 요건</label>
                      <select
                        name="experience" 
                        value={formData.experience || ''} 
                        onChange={handleInputChange}
                        required
                        className="custom-input"
                        style={{
                          borderColor: formData.experience ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.experience ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      >
                        <option value="">선택해주세요</option>
                        <option value="신입">신입</option>
                        <option value="경력">경력</option>
                        <option value="신입/경력">신입/경력</option>
                      </select>
                      {formData.experience && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.experience}
                        </div>
                      )}
                    </div>

                    <div className="custom-form-group">
                      <label className="custom-label">경력 연차</label>
                      <input
                        type="text"
                        name="experienceYears" 
                        value={formData.experienceYears || ''} 
                        onChange={handleInputChange}
                        placeholder="예: 3년 이상, 5년 이상"
                        className="custom-input"
                        style={{
                          borderColor: formData.experienceYears ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.experienceYears ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.experienceYears && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.experienceYears}
                        </div>
                      )}
                    </div>

                    <div className="custom-form-group">
                      <label className="custom-label">근무 형태</label>
                      <select
                        name="workType" 
                        value={formData.workType || ''} 
                        onChange={handleInputChange}
                        required
                        className="custom-input"
                        style={{
                          borderColor: formData.workType ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.workType ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      >
                        <option value="">선택해주세요</option>
                        <option value="정규직">정규직</option>
                        <option value="계약직">계약직</option>
                        <option value="인턴">인턴</option>
                        <option value="프리랜서">프리랜서</option>
                      </select>
                      {formData.workType && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.workType}
                        </div>
                      )}
                    </div>
                  </FormGrid>
                </FormSection>

                <FormSection>
                  <SectionTitle>
                    <FiClock size={18} />
                    근무 조건
                  </SectionTitle>
                  <FormGrid>
                    <div className="custom-form-group">
                      <label className="custom-label">근무 시간</label>
                      <input
                        type="text"
                        name="workHours" 
                        value={formData.workHours || ''} 
                        onChange={handleInputChange}
                        placeholder="예: 09:00 ~ 18:00, 유연근무제"
                        className="custom-input"
                        style={{
                          borderColor: formData.workHours ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.workHours ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.workHours && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
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
                        placeholder="예: 월~금, 월~토"
                        className="custom-input"
                        style={{
                          borderColor: formData.workDays ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.workDays ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.workDays && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.workDays}
                        </div>
                      )}
                    </div>
                  </FormGrid>
                </FormSection>

                <FormSection>
                  <SectionTitle>
                    <FiMapPin size={18} />
                    근무 위치
                  </SectionTitle>
                  <FormGrid>
                    <div className="custom-form-group">
                      <label className="custom-label">도시</label>
                      <input
                        type="text"
                        name="locationCity" 
                        value={formData.locationCity || ''} 
                        onChange={handleInputChange}
                        placeholder="예: 서울, 인천, 부산"
                        required
                        className="custom-input"
                        style={{
                          borderColor: formData.locationCity ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.locationCity ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.locationCity && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.locationCity}
                        </div>
                      )}
                    </div>

                    <div className="custom-form-group">
                      <label className="custom-label">구/군</label>
                      <input
                        type="text"
                        name="locationDistrict" 
                        value={formData.locationDistrict || ''} 
                        onChange={handleInputChange}
                        placeholder="예: 강남구, 서초구"
                        className="custom-input"
                        style={{
                          borderColor: formData.locationDistrict ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.locationDistrict ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.locationDistrict && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.locationDistrict}
                        </div>
                      )}
                    </div>
                  </FormGrid>
                </FormSection>

                <FormSection>
                  <SectionTitle>
                    <FiDollarSign size={18} />
                    급여 조건
                  </SectionTitle>
                  <div className="custom-form-group">
                    <label className="custom-label">연봉</label>
                    <input
                      type="text"
                      name="salary" 
                      value={formData.salary || ''} 
                      onChange={handleInputChange}
                      placeholder="예: 4,000만원 ~ 6,000만원, 협의"
                      className="custom-input"
                      style={{
                        borderColor: formData.salary ? '#f093fb' : '#cbd5e0',
                        boxShadow: formData.salary ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                      }}
                    />
                    {formData.salary && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#f093fb', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.salary}
                      </div>
                    )}
                  </div>
                </FormSection>

                <FormSection>
                  <SectionTitle>
                    <FiFileText size={18} />
                    업무 및 자격
                  </SectionTitle>
                  <div className="custom-form-group">
                    <label className="custom-label">주요 업무</label>
                    <textarea
                      name="mainDuties" 
                      value={formData.mainDuties || ''} 
                      onChange={handleInputChange}
                      placeholder="담당하실 주요 업무를 상세히 입력해주세요."
                      required
                      className="custom-textarea"
                      rows="4"
                      style={{
                        borderColor: formData.mainDuties ? '#f093fb' : '#cbd5e0',
                        boxShadow: formData.mainDuties ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                      }}
                    />
                    {formData.mainDuties && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#f093fb', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.mainDuties.length}자
                      </div>
                    )}
                  </div>

                  <div className="custom-form-group">
                    <label className="custom-label">자격 요건</label>
                    <textarea
                      name="requirements" 
                      value={formData.requirements || ''} 
                      onChange={handleInputChange}
                      placeholder="필요한 자격 요건을 입력해주세요."
                      className="custom-textarea"
                      rows="4"
                      style={{
                        borderColor: formData.requirements ? '#f093fb' : '#cbd5e0',
                        boxShadow: formData.requirements ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                      }}
                    />
                    {formData.requirements && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#f093fb', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.requirements.length}자
                      </div>
                    )}
                  </div>

                  <div className="custom-form-group">
                    <label className="custom-label">복리후생</label>
                    <textarea
                      name="benefits" 
                      value={formData.benefits || ''} 
                      onChange={handleInputChange}
                      placeholder="제공되는 복리후생을 입력해주세요."
                      className="custom-textarea"
                      rows="4"
                      style={{
                        borderColor: formData.benefits ? '#f093fb' : '#cbd5e0',
                        boxShadow: formData.benefits ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                      }}
                    />
                    {formData.benefits && (
                      <div style={{ 
                        fontSize: '0.8em', 
                        color: '#f093fb', 
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.benefits.length}자
                      </div>
                    )}
                  </div>
                </FormSection>

                <FormSection>
                  <SectionTitle>
                    <FiMail size={18} />
                    연락처 및 마감일
                  </SectionTitle>
                  <FormGrid>
                    <div className="custom-form-group">
                      <label className="custom-label">연락처 이메일</label>
                      <input
                        type="email"
                        name="contactEmail" 
                        value={formData.contactEmail || ''} 
                        onChange={handleInputChange}
                        placeholder="예: hr@company.com"
                        required
                        className="custom-input"
                        style={{
                          borderColor: formData.contactEmail ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.contactEmail ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.contactEmail && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
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
                          borderColor: formData.deadline ? '#f093fb' : '#cbd5e0',
                          boxShadow: formData.deadline ? '0 0 0 3px rgba(240, 147, 251, 0.2)' : 'none'
                        }}
                      />
                      {formData.deadline && (
                        <div style={{ 
                          fontSize: '0.8em', 
                          color: '#f093fb', 
                          marginTop: '4px',
                          fontWeight: 'bold'
                        }}>
                          ✅ 입력됨: {formData.deadline}
                        </div>
                      )}
                    </div>
                  </FormGrid>
                </FormSection>

                <ButtonGroup>
                  <Button type="button" className="secondary" onClick={handleClose}>
                    취소
                  </Button>
                  <Button type="submit" className="primary">
                    <FiCheck size={16} />
                    채용공고 등록
                  </Button>
                </ButtonGroup>
                </form>
                </>
              )}

              {/* AI 어시스턴트 - EnhancedModalChatbot 컴포넌트 제거됨 */}
            </Content>
          </Modal>
        </Overlay>
      )}

      {/* 토스트 알림 */}
      {SHOW_AI_TOASTS && showToast && (
        <div
          style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white',
            padding: '16px 20px',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(240, 147, 251, 0.3)',
            zIndex: 10000,
            maxWidth: '400px',
            fontSize: '14px',
            lineHeight: '1.5',
            animation: 'slideInRight 0.3s ease-out',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(10px)'
          }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px'
          }}>
            <div style={{
              fontSize: '20px',
              marginTop: '2px'
            }}>
              ✅
            </div>
            <div style={{ flex: 1 }}>
              {toastMessage.split('\n').map((line, index) => (
                <div key={index} style={{
                  marginBottom: index < toastMessage.split('\n').length - 1 ? '4px' : '0'
                }}>
                  {line}
                </div>
              ))}
            </div>
            <button
              onClick={() => setShowToast(false)}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                cursor: 'pointer',
                fontSize: '16px',
                padding: '0',
                marginLeft: '8px'
              }}
            >
              ×
            </button>
          </div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default LangGraphJobRegistration;
