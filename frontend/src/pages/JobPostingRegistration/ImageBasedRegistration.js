import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import TemplateModal from './TemplateModal';
import TitleRecommendationModal from '../../components/TitleRecommendationModal';
// import TestAutoFillButton from '../../components/TestAutoFillButton';
import {
  FiX,
  FiArrowLeft,
  FiArrowRight,
  FiCheck,
  FiImage,
  FiDownload,
  FiEye,
  FiRefreshCw,
  FiUsers,
  FiBriefcase,
  FiFileText,
  FiClock,
  FiAward,
  FiMail,
  FiFolder
} from 'react-icons/fi';
import companyCultureApi from '../../services/companyCultureApi';

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
  max-width: 1000px;
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

const StepIndicator = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  gap: 40px;
`;

const Step = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
`;

const StepNumber = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: ${props =>
    props.active ? 'linear-gradient(135deg, #f093fb, #f5576c)' :
    props.completed ? 'var(--primary-color)' : 'var(--border-color)'
  };
`;

const StepLabel = styled.span`
  font-size: 14px;
  color: ${props =>
    props.active ? 'var(--primary-color)' :
    props.completed ? 'var(--text-primary)' : 'var(--text-secondary)'
  };
  font-weight: ${props => props.active || props.completed ? '600' : '400'};
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

const RadioOption = styled.div`
  display: flex;
  align-items: center;
  padding: 16px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;

  &.selected {
    border-color: var(--primary-color);
    background: rgba(0, 123, 255, 0.05);
  }

  &:hover {
    border-color: var(--primary-color);
  }
`;

const RadioInput = styled.input`
  margin-right: 12px;
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

const AISuggestion = styled.div`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 16px;
  border-radius: 12px;
  margin-top: 16px;
`;

const AISuggestionTitle = styled.div`
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const AISuggestionText = styled.p`
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
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
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;

  &.primary {
    background: var(--primary-color);
    color: white;

    &:hover {
      background: var(--primary-hover);
    }

    &:disabled {
      background: var(--border-color);
      cursor: not-allowed;
    }
  }

  &.secondary {
    background: transparent;
    color: var(--text-primary);
    border: 2px solid var(--border-color);

    &:hover {
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
  }
`;

const GenerateButton = styled.button`
  padding: 16px 32px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ImageGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 24px;
`;

const ImageCard = styled(motion.div)`
  border: 2px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  }

  &.selected {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const ImagePlaceholder = styled.div`
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #f093fb, #f5576c);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
`;

const ImageInfo = styled.div`
  padding: 16px;
  background: white;
`;

const ImageTitle = styled.div`
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const ImageDescription = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
`;

const LoadingSection = styled.div`
  text-align: center;
  padding: 60px 20px;
`;

const LoadingSpinner = styled.div`
  width: 60px;
  height: 60px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingText = styled.div`
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 8px;
`;

const LoadingSubtext = styled.div`
  font-size: 14px;
  color: var(--text-light);
`;



const ImageBasedRegistration = ({
  isOpen,
  onClose,
  onComplete,
  organizationData = { departments: [] }
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [templates, setTemplates] = useState([]);

  const [titleRecommendationModal, setTitleRecommendationModal] = useState({
    isOpen: false,
    finalFormData: null
  });

  // AI 자동 플로우 시작 이벤트 리스너
  React.useEffect(() => {
    const handleStartImageBasedAIFlow = () => {
      console.log('AI 자동 플로우 시작됨 - 이미지 기반 등록');
      // 이미지 기반 등록에서는 자동으로 이미지 생성 단계로 이동
      setTimeout(() => {
        setCurrentStep(6); // 이미지 생성 단계로 이동
        handleGenerateImages(); // 자동으로 이미지 생성 시작
      }, 1000);
    };

    window.addEventListener('startImageBasedAIFlow', handleStartImageBasedAIFlow);

    return () => {
      window.removeEventListener('startImageBasedAIFlow', handleStartImageBasedAIFlow);
    };
  }, []);
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
    deadline: '',
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

  // 모달이 열릴 때 챗봇 닫기
  useEffect(() => {
    if (isOpen) {
      console.log('ImageBasedRegistration 모달이 열림 - 챗봇 닫기 이벤트 발생');
      const event = new CustomEvent('closeChatbot');
      window.dispatchEvent(event);
    }
  }, [isOpen]);

  const [generatedImages, setGeneratedImages] = useState([]);

  const steps = [
    { number: 1, label: '구인 부서', icon: FiBriefcase },
    { number: 2, label: '구인 정보', icon: FiFileText },
    { number: 3, label: '근무 조건', icon: FiClock },
    { number: 4, label: '전형 절차', icon: FiAward },
    { number: 5, label: '지원 방법', icon: FiMail },
    { number: 6, label: '이미지 생성', icon: FiImage },
    { number: 7, label: '이미지 선택', icon: FiImage }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    // 급여 필드에 대한 특별 처리
    if (name === 'salary') {
      // 입력값에서 숫자만 추출 (콤마, 하이픈, 틸드 포함)
      const numericValue = value.replace(/[^\d,~\-]/g, '');
      setFormData(prev => ({
        ...prev,
        [name]: numericValue
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
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

  const handleGenerateImages = async () => {
    setIsGenerating(true);

    // AI 이미지 생성 시뮬레이션 (실제로는 API 호출)
    setTimeout(() => {
      const mockImages = [
        {
          id: 1,
          title: '모던 스타일',
          description: '깔끔하고 현대적인 디자인',
          url: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSJ1cmwoI2dyYWRpZW50KSIvPgo8ZGVmcz4KPGxpbmVhckdyYWRpZW50IGlkPSJncmFkaWVudCIgeDE9IjAiIHkxPSIwIiB4Mj0iMzAwIiB5Mj0iMjAwIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiNmMDkzZmI7c3RvcC1vcGFjaXR5OjEiLz4KPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdHlsZT0ic3RvcC1jb2xvcjojZjU1NzZjO3N0b3Atb3BhY2l0eToxIi8+CjwvbGluZWFyR3JhZGllbnQ+CjwvZGVmcz4KPC9zdmc+'
        },
        {
          id: 2,
          title: '비즈니스 스타일',
          description: '전문적이고 신뢰감 있는 디자인',
          url: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSJ1cmwoI2dyYWRpZW50KSIvPgo8ZGVmcz4KPGxpbmVhckdyYWRpZW50IGlkPSJncmFkaWVudCIgeDE9IjAiIHkxPSIwIiB4Mj0iMzAwIiB5Mj0iMjAwIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiM2NjdlZWE7c3RvcC1vcGFjaXR5OjEiLz4KPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdHlsZT0ic3RvcC1jb2xvcjojNzY0YmEyO3N0b3Atb3BhY2l0eToxIi8+CjwvbGluZWFyR3JhZGllbnQ+CjwvZGVmcz4KPC9zdmc+'
        },
        {
          id: 3,
          title: '크리에이티브 스타일',
          description: '창의적이고 독특한 디자인',
          url: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSJ1cmwoI2dyYWRpZW50KSIvPgo8ZGVmcz4KPGxpbmVhckdyYWRpZW50IGlkPSJncmFkaWVudCIgeDE9IjAiIHkxPSIwIiB4Mj0iMzAwIiB5Mj0iMjAwIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiMwMGM4NTE7c3RvcC1vcGFjaXR5OjEiLz4KPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdHlsZT0ic3RvcC1jb2xvcjojMDBhODQ0O3N0b3Atb3BhY2l0eToxIi8+CjwvbGluZWFyR3JhZGllbnQ+CjwvZGVmcz4KPC9zdmc+'
        }
      ];
      setGeneratedImages(mockImages);
      setIsGenerating(false);
      setCurrentStep(3);
    }, 3000);
  };

  const handleImageSelect = (image) => {
    setSelectedImage(image);
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
          - 근무지: ${jobData.location}
          - 연봉: ${jobData.salary}
          - 마감일: ${jobData.deadline}

          🎯 주요 업무
          ${jobData.mainDuties}

          📞 지원 문의
          - 이메일: ${jobData.contactEmail}

          🖼️ AI 생성 이미지
          선택된 이미지가 채용공고에 적용되었습니다.

          채용공고 관리 시스템에서 언제든지 수정하거나 관리할 수 있습니다.

          감사합니다.
          채용관리팀
        `
      };

      // 시뮬레이션: 1초 후 완료
      await new Promise(resolve => setTimeout(resolve, 1000));

      console.log('✅ 이메일 전송 완료');
      alert(`📧 인사담당자(${jobData.contactEmail})에게 등록 완료 알림 이메일이 전송되었습니다.`);

    } catch (error) {
      console.error('❌ 이메일 전송 실패:', error);
      alert('이메일 전송 중 오류가 발생했습니다. 채용공고는 정상적으로 등록되었습니다.');
    } finally {
      setIsSendingEmail(false);
    }
  };

  const handleSaveTemplate = (template) => {
    setTemplates(prev => [...prev, template]);
  };

  const handleLoadTemplate = (templateData) => {
    setFormData(prev => ({ ...prev, ...templateData }));
  };

  const handleDeleteTemplate = (templateId) => {
    setTemplates(prev => prev.filter(template => template.id !== templateId));
  };

  const handleComplete = async () => {
    if (selectedImage) {
      console.log('이미지 기반 등록 완료 - 제목 추천 모달 열기');
      const completeData = { ...formData, selectedImage };

      // 제목 추천 모달 열기
      setTitleRecommendationModal({
        isOpen: true,
        finalFormData: completeData
      });
    }
  };

  // 제목 추천 모달에서 제목 선택
  const handleTitleSelect = async (selectedTitle) => {
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

    // 인사담당자에게 알림 이메일 전송
    if (finalData.contactEmail) {
      await sendNotificationEmail(finalData);
    }
  };

  // 제목 추천 모달에서 직접 입력
  const handleDirectTitleInput = async (customTitle) => {
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

    // 인사담당자에게 알림 이메일 전송
    if (finalData.contactEmail) {
      await sendNotificationEmail(finalData);
    }
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
    console.log('=== ImageBasedRegistration 상태 초기화 ===');

    // 폼 데이터 초기화
    setFormData({
      department: '',
      experience: '',
      experienceYears: '',
      headcount: '',
      mainDuties: '',
      workHours: '',
      workDays: '',
      locationCity: '',
      locationDistrict: '',
      salary: '',
      process: ['서류', '실무면접', '최종면접', '입사'],
      deadline: '',
      contactEmail: '',
      notes: '',
      // 인재상 선택 필드 초기화
      selected_culture_id: null
    });

    // 단계 초기화
    setCurrentStep(1);
    setIsGenerating(false);
    setSelectedImage(null);
    setIsSendingEmail(false);
    setShowTemplateModal(false);
    setTemplates([]);

    // 제목 추천 모달 초기화
    setTitleRecommendationModal({
      isOpen: false,
      finalFormData: null
    });

    console.log('=== ImageBasedRegistration 상태 초기화 완료 ===');
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
      experience: '경력',
      experienceYears: '3',
      headCount: '2명',
      mainDuties: '웹개발, 프론트엔드 개발, React/Vue.js 활용, UI/UX 구현',
      workHours: '09:00 - 18:00',
      workDays: '주중 (월-금)',
      locationCity: '서울특별시 강남구 테헤란로 123',
      salary: '연봉 4,000만원 - 6,000만원',
      contactEmail: 'hr@company.com',
      deadline: '2024년 9월 30일까지',
      benefits: '점심식대 지원, 야근식대 지원, 경조사 지원, 생일 축하금, 명절 선물, 연차휴가, 건강검진, 교육비 지원'
    };

    // 폼 데이터 일괄 업데이트
    setFormData(prev => ({ ...prev, ...testData }));

    console.log('테스트 자동입력 완료:', testData);

    // 사용자에게 알림
    alert('🧪 테스트 데이터가 자동으로 입력되었습니다!\n\n📋 입력된 정보:\n• 부서: 개발팀\n• 경력: 경력 (3년)\n• 모집인원: 2명\n• 주요업무: 웹개발, 프론트엔드 개발\n• 근무시간: 09:00-18:00\n• 근무일: 주중 (월-금)\n• 근무위치: 서울 강남구\n• 연봉: 4,000만원-6,000만원\n• 연락처: hr@company.com\n• 마감일: 2024년 9월 30일\n• 복리후생: 점심식대, 야근식대, 경조사 지원 등');
  };

  // 단계별 렌더 함수들 (1~5단계)
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
            <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
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
                  onChange={(e) => setFormData(prev => ({ ...prev, experienceYears: e.target.value }))}
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
              onChange={(e) => setFormData(prev => ({
                ...prev,
                workHours: e.target.value
              }))}
              placeholder="예: 09:00 ~ 18:00"
              style={{ marginTop: '8px' }}
            />
          )}
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
          <div style={{ position: 'relative' }}>
            <Input
              type="text"
              name="salary"
              value={formData.salary}
              onChange={handleInputChange}
              placeholder="예: 4000~6000, 5000, 면접 후 협의"
              style={{ paddingRight: '50px' }}
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
        <Label>전형 절차</Label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {formData.process.map((step, index) => (
            <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>
                {index + 1}.
              </span>
              <span>{step}</span>
            </div>
          ))}
        </div>
        <div style={{ marginTop: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
          기본 전형 절차가 설정되어 있습니다. 필요시 수정 가능합니다.
        </div>
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
          <Label>인사담당자 이메일</Label>
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
          <Label>회사 인재상</Label>
          <Select
            name="selected_culture_id"
            value={formData.selected_culture_id || ''}
            onChange={handleInputChange}
          >
            <option value="">기본 인재상 사용</option>
            {cultures.map(culture => (
              <option key={culture.id} value={culture.id}>
                {culture.name} {culture.is_default ? '(기본)' : ''}
              </option>
            ))}
          </Select>
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

  const renderStep6 = () => (
    <FormSection>
      <SectionTitle>
        <FiImage size={18} />
        이미지 생성
      </SectionTitle>
      <div style={{ textAlign: 'center', padding: '40px 20px' }}>
        {isGenerating ? (
          <div>
            <LoadingSpinner />
            <LoadingText>AI가 이미지를 생성하고 있습니다...</LoadingText>
            <LoadingSubtext>잠시만 기다려주세요</LoadingSubtext>
          </div>
        ) : (
          <div>
            <GenerateButton onClick={handleGenerateImages}>
              <FiRefreshCw size={24} />
              이미지 생성 시작
            </GenerateButton>
          </div>
        )}
      </div>
    </FormSection>
  );

  const renderStep7 = () => (
    <FormSection>
      <SectionTitle>
        <FiImage size={18} />
        생성된 이미지 중 선택
      </SectionTitle>
      <ImageGrid>
        {generatedImages.map((image) => (
          <ImageCard
            key={image.id}
            className={selectedImage?.id === image.id ? 'selected' : ''}
            onClick={() => handleImageSelect(image)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <ImagePlaceholder>
              <FiImage />
            </ImagePlaceholder>
            <ImageInfo>
              <ImageTitle>{image.title}</ImageTitle>
              <ImageDescription>{image.description}</ImageDescription>
            </ImageInfo>
          </ImageCard>
        ))}
      </ImageGrid>
    </FormSection>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      case 4: return renderStep4();
      case 5: return renderStep5();
      case 6: return renderStep6();
      case 7: return renderStep7();
      default: return null;
    }
  };

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <Overlay
            key="image-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          >
            <Modal
              key="image-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <Header>
                <Title>이미지 기반 채용공고 등록</Title>
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

              <Content>
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
                    onClick={currentStep === 1 ? onClose : () => setCurrentStep(currentStep - 1)}
                  >
                    <FiArrowLeft size={16} />
                    {currentStep === 1 ? '취소' : '이전'}
                  </Button>
                  {currentStep === 1 && (
                    <Button
                      className="secondary"
                      onClick={() => setShowTemplateModal(true)}
                    >
                      <FiFolder size={16} />
                      템플릿
                    </Button>
                  )}
                  <Button
                    className="primary"
                    onClick={currentStep === steps.length ? handleComplete : () => setCurrentStep(currentStep + 1)}
                    disabled={(currentStep === steps.length && !selectedImage) || (currentStep === steps.length && isSendingEmail)}
                  >
                    {currentStep === steps.length ? (
                      isSendingEmail ? (
                        <>
                          <FiRefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                          이메일 전송 중...
                        </>
                      ) : (
                        <>
                          완료
                          <FiCheck size={16} />
                        </>
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
      </AnimatePresence>

      <TemplateModal
        isOpen={showTemplateModal}
        onClose={() => setShowTemplateModal(false)}
        onSaveTemplate={handleSaveTemplate}
        onLoadTemplate={handleLoadTemplate}
        onDeleteTemplate={handleDeleteTemplate}
        templates={templates}
        currentData={formData}
      />

      {/* 제목 추천 모달 */}
      <TitleRecommendationModal
        isOpen={titleRecommendationModal.isOpen}
        onClose={handleTitleModalClose}
        formData={titleRecommendationModal.finalFormData}
        onTitleSelect={handleTitleSelect}
        onDirectInput={handleDirectTitleInput}
      />
    </>
  );
};

export default ImageBasedRegistration;
