import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import TemplateModal from './TemplateModal';
// EnhancedModalChatbot 컴포넌트 제거됨
import TitleRecommendationModal from '../../components/TitleRecommendationModal';
// import TestAutoFillButton from '../../components/TestAutoFillButton';
import './TextBasedRegistration.css';
import { FiX, FiArrowLeft, FiArrowRight, FiCheck, FiFileText, FiClock, FiMapPin, FiDollarSign, FiUsers, FiMail, FiCalendar, FiFolder, FiSettings } from 'react-icons/fi';
import companyCultureApi from '../../services/companyCultureApi';
import jobPostingApi from '../../services/jobPostingApi';

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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    background: linear-gradient(135deg, #00c851, #00a844);
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(0, 200, 81, 0.3);
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
    background: linear-gradient(135deg, #ff6b6b, #ee5a52);
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
    }
  }
`;

const AINotice = styled.div`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
`;

const TextBasedRegistration = ({
  isOpen,
  onClose,
  onComplete,
  organizationData = { departments: [] },
  autoFillData = null
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    department: '',
    position: '',
    experience: '신입',
    experienceYears: '',
    headcount: '',
    mainDuties: '',
    workHours: '',
    workDays: '',
    locationCity: '',
    salary: '',
    contactEmail: '',
    deadline: '',
    requirements: '',
    benefits: '',
    // 인재상 선택 필드 추가
    selected_culture_id: null
  });

  // 인재상 관련 상태
  const [cultures, setCultures] = useState([]);
  const [defaultCulture, setDefaultCulture] = useState(null);
  const [loadingCultures, setLoadingCultures] = useState(false);

  // 인재상 데이터 로드
  useEffect(() => {
    loadCultures();
  }, []);

  const loadCultures = async () => {
    try {
      setLoadingCultures(true);

      // 모든 인재상 데이터 로드
      const culturesData = await companyCultureApi.getAllCultures(true);
      setCultures(culturesData);

      // 기본 인재상 데이터 로드 (에러 처리 포함)
      let defaultCultureData = null;
      try {
        defaultCultureData = await companyCultureApi.getDefaultCulture();
        setDefaultCulture(defaultCultureData);
      } catch (error) {
        console.log('기본 인재상이 설정되지 않았습니다:', error.message);
        setDefaultCulture(null);
      }

      // 기본 인재상이 있으면 formData에 설정
      if (defaultCultureData) {
        setFormData(prev => ({
          ...prev,
          selected_culture_id: defaultCultureData.id
        }));
        console.log('기본 인재상이 formData에 설정됨:', defaultCultureData.id);
      } else {
        // 기본 인재상이 없으면 첫 번째 활성 인재상을 기본값으로 설정
        if (culturesData && culturesData.length > 0) {
          const firstCulture = culturesData[0];
          setFormData(prev => ({
            ...prev,
            selected_culture_id: firstCulture.id
          }));
          console.log('첫 번째 인재상이 formData에 설정됨:', firstCulture.id);
        }
      }
    } catch (error) {
      console.error('인재상 로드 실패:', error);
    } finally {
      setLoadingCultures(false);
    }
  };

  const [aiChatbot, setAiChatbot] = useState({
    isActive: false,
    currentQuestion: '',
    step: 1
  });

  const [titleRecommendationModal, setTitleRecommendationModal] = useState({
    isOpen: false,
    finalFormData: null
  });

  // WebSocket 연결 및 Agent 출력 관리
  const [wsConnection, setWsConnection] = useState(null);
  const [agentOutputs, setAgentOutputs] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  // 랭그래프 Agent 호출 함수
  const callLangGraphAgent = async (message) => {
    try {
      console.log('🤖 랭그래프 Agent 호출:', message);

      const response = await fetch('/api/langgraph-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          conversation_history: [],
          session_id: sessionId
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('🤖 랭그래프 Agent 응답:', result);

      // 추출된 필드 정보가 있으면 폼에 자동 적용
      if (result.extracted_fields && Object.keys(result.extracted_fields).length > 0) {
        console.log('✅ 추출된 필드 정보:', result.extracted_fields);

        setFormData(prev => {
          const newFormData = { ...prev, ...result.extracted_fields };
          console.log('📝 폼 데이터 업데이트:', newFormData);
          return newFormData;
        });

        // 성공 알림
        const fieldNames = Object.keys(result.extracted_fields).join(', ');
        console.log(`✅ 랭그래프 Agent에서 추출한 정보가 폼에 자동 입력되었습니다! (${fieldNames})`);
      }

      return result;
    } catch (error) {
      console.error('❌ 랭그래프 Agent 호출 오류:', error);
      return {
        success: false,
        response: `랭그래프 Agent 연결에 실패했습니다: ${error.message}`
      };
    }
  };

  // 랭그래프 Agent 테스트 함수
  const testLangGraphAgent = () => {
    const testMessages = [
      "개발자 2명 뽑고 싶어",
      "연봉 4000만원으로 프론트엔드 개발자 구해요",
      "서울에서 마케팅팀 1명 채용하려고 해",
      "신입 개발자 3명 모집, 9 to 6 근무"
    ];

    const randomMessage = testMessages[Math.floor(Math.random() * testMessages.length)];
    callLangGraphAgent(randomMessage);
  };

  // 모달이 열리면 자동으로 AI 도우미 시작
  useEffect(() => {
    if (isOpen) {
      console.log('=== TextBasedRegistration 모달 열림 - AI 도우미 자동 시작 ===');

      // 자동입력 데이터가 있으면 폼에 적용
      if (autoFillData) {
        console.log('자동입력 데이터 적용:', autoFillData);
        setFormData(prev => ({
          ...prev,
          ...autoFillData
        }));
      }

      // 먼저 모달을 AI 어시스턴트 크기로 설정
      setTimeout(() => {
        setAiChatbot({
          isActive: true,
          currentQuestion: '구인 부서를 알려주세요! (예: 개발, 마케팅, 영업, 디자인 등)',
          step: 1
        });
      }, 1200); // 1.2초 후 AI 도우미 시작 (모달 애니메이션 완료 후)
    }
  }, [isOpen, autoFillData]);



  // AI 챗봇이 비활성화될 때 플로팅 챗봇 다시 표시
  useEffect(() => {
    if (!aiChatbot.isActive) {
      console.log('=== AI 챗봇 비활성화 - 플로팅 챗봇 다시 표시 ===');
      const floatingChatbot = document.querySelector('.floating-chatbot');
      if (floatingChatbot) {
        floatingChatbot.style.display = 'flex';
      }
      // 커스텀 이벤트로 플로팅 챗봇에 알림
      window.dispatchEvent(new CustomEvent('showFloatingChatbot'));
    }
  }, [aiChatbot.isActive]);

  // formData 상태 변경 추적
  useEffect(() => {
    console.log('=== formData 상태 변경 ===');
    console.log('현재 formData:', formData);
    console.log('입력된 필드들:', Object.keys(formData).filter(key => formData[key]));
  }, [formData]);

  // 랭그래프 Agent 이벤트 수신
  useEffect(() => {
    const handleLangGraphFieldUpdate = (event) => {
      const extractedFields = event.detail.extracted_fields;
      console.log('🎯 랭그래프 Agent 이벤트 수신:', extractedFields);

      if (extractedFields && Object.keys(extractedFields).length > 0) {
        // 필드명 매핑 (백엔드 필드명 → 폼 필드명)
        const mappedFields = {};
        Object.entries(extractedFields).forEach(([key, value]) => {
          switch (key) {
            case 'location':
              mappedFields['locationCity'] = value;
              break;
            case 'department':
            case 'headcount':
            case 'salary':
            case 'experience':
            case 'mainDuties':
            case 'workHours':
            case 'workDays':
            case 'contactEmail':
            case 'deadline':
              mappedFields[key] = value;
              break;
            default:
              mappedFields[key] = value;
              break;
          }
        });

        console.log('🔄 필드 매핑 결과:', mappedFields);

        setFormData(prev => {
          const newFormData = { ...prev, ...mappedFields };
          console.log('📝 폼 데이터 업데이트:', newFormData);
          return newFormData;
        });

        // 성공 알림
        const fieldNames = Object.keys(mappedFields).join(', ');
        console.log(`✅ 랭그래프 Agent에서 추출한 정보가 폼에 자동 입력되었습니다! (${fieldNames})`);

        // 시각적 피드백 (임시 알림)
        const notification = document.createElement('div');
        notification.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          background: #667eea;
          color: white;
          padding: 15px 20px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          z-index: 10000;
          font-weight: bold;
          animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = `🎯 ${fieldNames} 필드가 자동으로 입력되었습니다!`;
        document.body.appendChild(notification);

        // 3초 후 알림 제거
        setTimeout(() => {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 3000);

      } else {
        console.log('⚠️ 추출된 필드가 없습니다.');
      }
    };

        window.addEventListener('langGraphDataUpdate', handleLangGraphFieldUpdate);

    return () => {
      window.removeEventListener('langGraphDataUpdate', handleLangGraphFieldUpdate);
    };
  }, []);

  // 폼 필드 업데이트 이벤트 리스너 추가
  useEffect(() => {
    const handleFormFieldUpdate = (event) => {
      const { field, value } = event.detail;
      console.log('=== TextBasedRegistration - 폼 필드 업데이트 이벤트 수신 ===');
      console.log('필드:', field);
      console.log('값:', value);

      setFormData(prev => {
        const newFormData = { ...prev, [field]: value };
        console.log('업데이트 후 formData:', newFormData);
        return newFormData;
      });
    };

    // 개별 필드 업데이트 이벤트 리스너들
    const handleDepartmentUpdate = (event) => {
      const { value } = event.detail;
      console.log('부서 업데이트:', value);
      setFormData(prev => ({ ...prev, department: value }));
    };

    const handleHeadcountUpdate = (event) => {
      const { value } = event.detail;
      console.log('인원 업데이트:', value);
      setFormData(prev => ({ ...prev, headcount: value }));
    };

    const handleSalaryUpdate = (event) => {
      const { value } = event.detail;
      console.log('연봉 업데이트:', value);
      setFormData(prev => ({ ...prev, salary: value }));
    };

    const handleWorkContentUpdate = (event) => {
      const { value } = event.detail;
      console.log('업무 내용 업데이트:', value);
      setFormData(prev => ({ ...prev, mainDuties: value }));
    };

    const handleWorkHoursUpdate = (event) => {
      const { value } = event.detail;
      console.log('근무 시간 업데이트:', value);
      setFormData(prev => ({ ...prev, workHours: value }));
    };

    const handleWorkDaysUpdate = (event) => {
      const { value } = event.detail;
      console.log('근무 요일 업데이트:', value);
      setFormData(prev => ({ ...prev, workDays: value }));
    };

    const handleLocationUpdate = (event) => {
      const { value } = event.detail;
      console.log('근무 위치 업데이트:', value);
      setFormData(prev => ({ ...prev, locationCity: value }));
    };

    const handleContactEmailUpdate = (event) => {
      const { value } = event.detail;
      console.log('연락처 이메일 업데이트:', value);
      setFormData(prev => ({ ...prev, contactEmail: value }));
    };

    const handleDeadlineUpdate = (event) => {
      const { value } = event.detail;
      console.log('마감일 업데이트:', value);
      setFormData(prev => ({ ...prev, deadline: value }));
    };

    // 이벤트 리스너 등록
    window.addEventListener('updateFormField', handleFormFieldUpdate);
    window.addEventListener('updateDepartment', handleDepartmentUpdate);
    window.addEventListener('updateHeadcount', handleHeadcountUpdate);
    window.addEventListener('updateSalary', handleSalaryUpdate);
    window.addEventListener('updateWorkContent', handleWorkContentUpdate);
    window.addEventListener('updateWorkHours', handleWorkHoursUpdate);
    window.addEventListener('updateWorkDays', handleWorkDaysUpdate);
    window.addEventListener('updateLocation', handleLocationUpdate);
    window.addEventListener('updateContactEmail', handleContactEmailUpdate);
    window.addEventListener('updateDeadline', handleDeadlineUpdate);

    // 클린업 함수
    return () => {
      window.removeEventListener('updateFormField', handleFormFieldUpdate);
      window.removeEventListener('updateDepartment', handleDepartmentUpdate);
      window.removeEventListener('updateHeadcount', handleHeadcountUpdate);
      window.removeEventListener('updateSalary', handleSalaryUpdate);
      window.removeEventListener('updateWorkContent', handleWorkContentUpdate);
      window.removeEventListener('updateWorkHours', handleWorkHoursUpdate);
      window.removeEventListener('updateWorkDays', handleWorkDaysUpdate);
      window.removeEventListener('updateLocation', handleLocationUpdate);
      window.removeEventListener('updateContactEmail', handleContactEmailUpdate);
      window.removeEventListener('updateDeadline', handleDeadlineUpdate);
    };
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    // 급여 필드에 대한 특별 처리
    if (name === 'salary') {
      // 입력값에서 숫자만 추출 (콤마, 하이픈, 틸드 포함)
      const numericValue = value.replace(/[^\d,~\-]/g, '');
      setFormData(prev => ({ ...prev, [name]: numericValue }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  // 급여를 표시용으로 포맷하는 함수
  const formatSalaryDisplay = (salaryValue) => {
    if (!salaryValue) return '';

    // 이미 "만원"이 포함되어 있으면 그대로 반환
    if (salaryValue.includes('만원') || salaryValue.includes('협의') || salaryValue.includes('면접')) {
      return salaryValue;
    }

    // 숫자만 있는 경우 "만원" 추가
    if (/^\d+([,\d~\-]*)?$/.test(salaryValue.trim())) {
      return `${salaryValue}만원`;
    }

    return salaryValue;
  };

  const startAIChatbot = () => {
    console.log('AI 채용공고 작성 도우미 시작 (상태 보존)');
    // 현재 페이지에서 재시작 시 기존 상태를 보존하고 표시만 ON
    setAiChatbot(prev => ({ ...prev, isActive: true }));
  };

  // 등록 버튼 클릭 시 제목 추천 모달 열기
  const handleRegistration = () => {
    console.log('등록 버튼 클릭 - 제목 추천 모달 열기');
    setTitleRecommendationModal({
      isOpen: true,
      finalFormData: { ...formData }
    });
  };

  // 제목 추천 모달에서 제목 선택
  const handleTitleSelect = (selectedTitle) => {
    console.log('추천 제목 선택:', selectedTitle);
    const finalData = {
      ...titleRecommendationModal.finalFormData,
      title: selectedTitle
    };

    // 제목 추천 모달 닫기
    setTitleRecommendationModal({
      isOpen: false,
      finalFormData: null
    });

    // 최종 등록 완료
    onComplete(finalData);
  };

  // 제목 추천 모달에서 직접 입력
  const handleDirectTitleInput = (customTitle) => {
    console.log('직접 입력 제목:', customTitle);
    const finalData = {
      ...titleRecommendationModal.finalFormData,
      title: customTitle
    };

    // 제목 추천 모달 닫기
    setTitleRecommendationModal({
      isOpen: false,
      finalFormData: null
    });

    // 최종 등록 완료
    onComplete(finalData);
  };

  // 제목 추천 모달 닫기
  const handleTitleModalClose = () => {
    setTitleRecommendationModal({
      isOpen: false,
      finalFormData: null
    });
  };

  // 모달 완전 초기화 함수
  const resetModalState = () => {
    console.log('=== TextBasedRegistration 상태 초기화 ===');

    // 폼 데이터 초기화
    setFormData({
      department: '',
      experience: '신입',
      experienceYears: '',
      headcount: '',
      mainDuties: '',
      workHours: '',
      workDays: '',
      locationCity: '',
      salary: '',
      contactEmail: '',
      deadline: ''
    });

    // AI 챗봇 상태 초기화
    setAiChatbot({
      isActive: false,
      currentQuestion: '',
      step: 1
    });

    // 제목 추천 모달 초기화
    setTitleRecommendationModal({
      isOpen: false,
      finalFormData: null
    });

    console.log('=== TextBasedRegistration 상태 초기화 완료 ===');
  };

  // 컴포넌트가 언마운트되거나 모달이 닫힐 때 초기화
  useEffect(() => {
    if (!isOpen) {
      resetModalState();
    }
  }, [isOpen]);

  // 테스트 자동입력 처리
  const handleTestAutoFill = (sampleData) => {
    console.log('테스트 자동입력 시작:', sampleData);

    // 하드코딩된 테스트 값들 (모든 필드 포함)
    const testData = {
      department: '개발팀',
      experience: '2년이상',
      experienceYears: '2',
      headcount: '2명',
      mainDuties: '웹개발, 프론트엔드 개발, React/Vue.js 활용',
      workHours: '09:00 - 18:00',
      workDays: '주중 (월-금)',
      locationCity: '서울특별시 강남구 테헤란로 123',
      salary: '연봉 4,000만원 - 6,000만원',
      contactEmail: 'hr@company.com',
      deadline: '2024년 9월 30일까지'
    };

    // 폼 데이터 일괄 업데이트
    setFormData(prev => ({ ...prev, ...testData }));

    console.log('테스트 자동입력 완료:', testData);

    // 사용자에게 알림
    alert('🧪 테스트 데이터가 자동으로 입력되었습니다!\n\n📋 입력된 정보:\n• 부서: 개발팀\n• 경력: 2년이상 (2년)\n• 모집인원: 2명\n• 주요업무: 웹개발, 프론트엔드 개발\n• 근무시간: 09:00-18:00\n• 근무일: 주중 (월-금)\n• 근무위치: 서울 강남구\n• 연봉: 4,000만원-6,000만원\n• 연락처: hr@company.com\n• 마감일: 2024년 9월 30일');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <Overlay
          key="text-based-overlay"
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
              <Title>🤖 AI 채용공고 등록 도우미</Title>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <button
                  onClick={handleTestAutoFill}
                  style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                    color: 'white',
                    fontSize: '12px',
                    cursor: 'pointer',
                    padding: '8px 16px',
                    borderRadius: '20px',
                    marginRight: '12px',
                    transition: 'all 0.3s ease',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.3)';
                  }}
                >
                  <span style={{ fontSize: '14px' }}>🧪</span>
                  테스트 데이터
                </button>
                <CloseButton onClick={onClose}>
                  <FiX />
                </CloseButton>
              </div>
            </Header>

            <Content aiActive={aiChatbot.isActive}>
              <AINotice>
                <FiSettings size={20} />
                AI 도우미가 단계별로 질문하여 자동으로 입력해드립니다!
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
                        borderColor: formData.department ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.department ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                    {formData.department && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
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
                      value={formData.headcount || '0명'}
                      onChange={handleInputChange}
                      placeholder="예: 0명, 1명, 2명, 3명"
                      required
                      className="custom-input"
                      style={{
                        borderColor: formData.headcount ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.headcount ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                    {formData.headcount && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
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
                        borderColor: formData.mainDuties ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.mainDuties ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                    {formData.mainDuties && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
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
                        borderColor: formData.workHours ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.workHours ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                    {formData.workHours && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
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
                        borderColor: formData.workDays ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.workDays ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                    {formData.workDays && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.workDays}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">연봉</label>
                    <div style={{ position: 'relative' }}>
                      <input
                        type="text"
                        name="salary"
                        value={formData.salary || ''}
                        onChange={handleInputChange}
                        placeholder="예: 3000~5000, 4000, 연봉 협의"
                        className="custom-input"
                        style={{
                          borderColor: formData.salary ? '#667eea' : '#cbd5e0',
                          boxShadow: formData.salary ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none',
                          paddingRight: '50px'
                        }}
                      />
                      {formData.salary && /^\d+([,\d~\-]*)?$/.test(formData.salary.trim()) && (
                        <span style={{
                          position: 'absolute',
                          right: '12px',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          color: '#667eea',
                          fontSize: '14px',
                          fontWeight: '500',
                          pointerEvents: 'none'
                        }}>
                          만원
                        </span>
                      )}
                    </div>
                    {formData.salary && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formatSalaryDisplay(formData.salary)}
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
                        borderColor: formData.contactEmail ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.contactEmail ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                    {formData.contactEmail && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.contactEmail}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">회사 인재상</label>
                    <select
                      name="selected_culture_id"
                      value={formData.selected_culture_id || ''}
                      onChange={handleInputChange}
                      className="custom-input"
                      style={{
                        borderColor: formData.selected_culture_id ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.selected_culture_id ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    >
                      <option value="">기본 인재상 사용</option>
                      {cultures.map(culture => (
                        <option key={culture.id} value={culture.id}>
                          {culture.name} {culture.is_default ? '(기본)' : ''}
                        </option>
                      ))}
                    </select>
                    {formData.selected_culture_id && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 선택됨: {cultures.find(c => c.id === formData.selected_culture_id)?.name}
                      </div>
                    )}
                    {!formData.selected_culture_id && defaultCulture && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#28a745',
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 기본 인재상: {defaultCulture.name}
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
                        borderColor: formData.deadline ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.deadline ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                    {formData.deadline && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
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
                        borderColor: formData.experience ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.experience ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                    {formData.experience && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.experience}
                      </div>
                    )}
                  </div>
                  <div className="custom-form-group">
                    <label className="custom-label">기타 항목</label>
                    <textarea
                      name="additionalInfo"
                      value={formData.additionalInfo || ''}
                      onChange={handleInputChange}
                      placeholder="주말보장, 원격근무, 유연근무제, 복리후생 등 추가 정보를 입력해주세요"
                      className="custom-textarea"
                      style={{
                        borderColor: formData.additionalInfo ? '#667eea' : '#cbd5e0',
                        boxShadow: formData.additionalInfo ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                    {formData.additionalInfo && (
                      <div style={{
                        fontSize: '0.8em',
                        color: '#667eea',
                        marginTop: '4px',
                        fontWeight: 'bold'
                      }}>
                        ✅ 입력됨: {formData.additionalInfo.length}자
                      </div>
                    )}
                    <div style={{
                      fontSize: '0.75em',
                      color: '#666',
                      marginTop: '8px',
                      fontStyle: 'italic'
                    }}>
                      💡 제안: 주말보장, 원격근무, 유연근무제, 식대지원, 교통비지원, 연차휴가, 교육지원, 동호회 등
                    </div>
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
                  🤖 AI 도우미 재시작
                    </Button>
                <Button
                  className="ai"
                  onClick={testLangGraphAgent}
                  style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
                >
                  🚀 랭그래프 Agent 테스트
                    </Button>
                <Button className="primary" onClick={handleRegistration}>
                  <FiCheck size={16} />
                  등록 완료
                </Button>
              </ButtonGroup>
            </Content>
          </Modal>
        </Overlay>
      )}

      {/* AI 챗봇 - EnhancedModalChatbot 컴포넌트 제거됨 */}

      {/* 제목 추천 모달 */}
      <TitleRecommendationModal
        isOpen={titleRecommendationModal.isOpen}
        onClose={handleTitleModalClose}
        formData={titleRecommendationModal.finalFormData}
        onTitleSelect={handleTitleSelect}
        onDirectInput={handleDirectTitleInput}
      />
    </AnimatePresence>
  );
};

export default TextBasedRegistration;
