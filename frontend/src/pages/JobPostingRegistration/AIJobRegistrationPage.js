import React, { useState, useEffect } from 'react';
import { flushSync } from 'react-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  FiArrowLeft,
  FiCheck,
  FiFileText,
  FiClock,
  FiMapPin,
  FiDollarSign,
  FiUsers,
  FiMail,
  FiCalendar,
  FiSettings,
  FiPlus, FiEdit3, FiTrash2, FiEye, FiBriefcase
} from 'react-icons/fi';
import TitleRecommendationModal from '../../components/TitleRecommendationModal';
import jobPostingApi from '../../services/jobPostingApi';
import companyCultureApi from '../../services/companyCultureApi';

// 헬퍼 함수들
const calculateDeadline = (daysFromNow) => {
  const today = new Date();
  const deadline = new Date(today.getTime() + (daysFromNow * 24 * 60 * 60 * 1000));
  return deadline.toISOString().split('T')[0]; // YYYY-MM-DD 형식
};

const extractExperienceYears = (experienceLevel) => {
  if (!experienceLevel) return '';

  // "3년차", "5년 이상" 등에서 숫자 추출
  const match = experienceLevel.match(/(\d+)/);
  if (match) {
    return match[1];
  }

  // "신입"인 경우
  if (experienceLevel.includes('신입')) {
    return '0';
  }

  return '';
};

// Styled Components
const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 24px;
`;

const ContentContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const Header = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const BackButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 12px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateX(-2px);
  }
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  margin: 0;
`;

const HeaderRight = styled.div`
  display: flex;
  gap: 12px;
`;



// AI 입력 상태 표시 컴포넌트
const AIStatusBar = styled.div`
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
  color: white;
  padding: 16px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(74, 222, 128, 0.2);
`;

const AIStatusLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const AIStatusSpinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const AIStatusProgress = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
`;

const AIProgressBar = styled.div`
  width: 120px;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  overflow: hidden;
`;

const AIProgressFill = styled.div`
  height: 100%;
  background: white;
  border-radius: 3px;
  transition: width 0.3s ease;
  width: ${props => (props.progress / props.total) * 100}%;
`;

const Content = styled.div`
  padding: 32px;
`;



const FormSection = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
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
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &.filled {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  min-height: 100px;
  resize: vertical;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &.filled {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &.filled {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const FilledIndicator = styled.div`
  font-size: 12px;
  color: #667eea;
  font-weight: 600;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
`;

const Button = styled.button`
  padding: 14px 28px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 16px;

  &.secondary {
    background: #f8f9fa;
    color: var(--text-primary);
    border: 2px solid #e5e7eb;

    &:hover {
      background: #e9ecef;
      border-color: #ced4da;
    }
  }

  &.primary {
    background: linear-gradient(135deg, #00c851, #00a844);
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(0, 200, 81, 0.3);
    }
  }

  &.ai {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
  }
`;

const SampleButtonGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
`;

const TestSection = styled.div`
  margin-bottom: 32px;
  padding: 20px;
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  border-radius: 12px;
  border: 2px dashed #ff6b6b;
`;

const TestSectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 700;
  color: #d63031;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TestDescription = styled.p`
  font-size: 14px;
  color: #6c5ce7;
  margin-bottom: 16px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.7);
  padding: 8px 12px;
  border-radius: 6px;
`;

const SampleButton = styled.button`
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: none;
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
`;

const AutoExtractButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const ExtractionIndicator = styled.div`
  margin-top: 8px;
  padding: 8px 12px;
  background: ${props =>
    props.isDefault
      ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'  // 주황색 (기본값)
      : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'  // 파란색 (추출)
  };
  color: white;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const ConfidenceScore = styled.span`
  margin-left: 8px;
  padding: 2px 6px;
  background: ${props =>
    props.confidence >= 0.8 ? '#10b981' :
    props.confidence >= 0.6 ? '#f59e0b' : '#ef4444'
  };
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
`;

const AIJobRegistrationPage = () => {
  const navigate = useNavigate();

  // 개발/테스트 환경 여부 확인 (실제 운영에서는 false로 설정)
  const isDevelopment = process.env.NODE_ENV === 'development' || process.env.REACT_APP_SHOW_TEST_SECTION === 'true';

  // 인재상 관련 상태
  const [cultures, setCultures] = useState([]);
  const [defaultCulture, setDefaultCulture] = useState(null);
  const [loadingCultures, setLoadingCultures] = useState(false);

  // AI 자동 입력 상태
  const [aiInputStatus, setAiInputStatus] = useState({
    isActive: false,
    currentField: '',
    progress: 0,
    totalFields: 0
  });

  // 분야 추출 결과 상태
  const [extractionResults, setExtractionResults] = useState({
    industry: null,
    jobCategory: null
  });

  // 추출 로딩 상태
  const [isExtracting, setIsExtracting] = useState(false);

  const [formData, setFormData] = useState({
    // 기본 정보
    department: '',
    position: '', // 채용 직무 추가
    experience: '신입',
    experienceYears: '',
    headcount: '',

    // 업무 정보
    mainDuties: '',
    workHours: '',
    workDays: '',
    locationCity: '',

    // 조건 정보
    salary: '',
    contactEmail: '',
    deadline: '',

    // 분석을 위한 추가 필드들
    jobKeywords: [], // 직무 키워드
    industry: '', // 산업 분야
    jobCategory: '', // 직무 카테고리
    experienceLevel: '신입', // 경력 수준
    experienceMinYears: null, // 최소 경력
    experienceMaxYears: null, // 최대 경력

    // 인재상 선택 필드 추가
    selected_culture_id: null
  });

  // 폼 데이터 변경 추적 디버깅 함수
  useEffect(() => {
    console.log('📊 formData 변경 감지:', {
      industry: formData.industry,
      jobCategory: formData.jobCategory,
      timestamp: new Date().toLocaleTimeString()
    });
  }, [formData.industry, formData.jobCategory]);

  // 폼 데이터 변경 추적 디버깅 함수
  const debugAIFormChange = (fieldName, oldValue, newValue, source = 'user') => {
    console.group(`📝 [AI 폼 필드 변경] ${fieldName}`);
    console.log('🔄 변경 소스:', source);
    console.log('📋 이전 값:', oldValue || '(비어있음)');
    console.log('📝 새 값:', newValue || '(비어있음)');

    // AI 폼 특화 분석
    if (fieldName === 'jobKeywords') {
      console.log('🏷️ 키워드 개수:', Array.isArray(newValue) ? newValue.length : 0);
    } else if (fieldName === 'experienceLevel') {
      console.log('💼 경력 수준 변경:', `${oldValue} → ${newValue}`);
    } else if (fieldName === 'selected_culture_id') {
      console.log('🏢 인재상 선택:', newValue ? '선택됨' : '미선택');
    }

    console.groupEnd();
  };

    // 향상된 폼 데이터 업데이트 함수
  const updateAIFormData = (updates, source = 'user') => {
    setFormData(prev => {
      const newData = { ...prev, ...updates };

      // 각 변경된 필드에 대해 디버깅
      Object.entries(updates).forEach(([key, value]) => {
        if (prev[key] !== value) {
          debugAIFormChange(key, prev[key], value, source);
        }
      });

      // 주요업무 자동 분리 체크
      if (updates.mainDuties && updates.mainDuties !== prev.mainDuties) {
        checkAutoSeparation(updates.mainDuties, source);
      }

      return newData;
    });
  };

    // 스마트 자동 분리 체크 함수 (즉시 실행)
  const checkAutoSeparation = async (mainDutiesText, source) => {
    // 자동 분리 조건 체크 (더 적극적으로)
    if (!mainDutiesText || mainDutiesText.length < 80) {
      console.log('📝 [스마트 분리 체크] 텍스트가 너무 짧음 - 자동 분리 안함');
      return;
    }

    // 더 넓은 조건으로 자동 분리 실행
    const shouldAutoSeparate = (
      source === 'ai_chatbot' ||           // AI 챗봇 입력
      source === 'ai_text_analysis' ||     // AI 텍스트 분석
      source === 'ai_object_data' ||       // AI 객체 데이터
      mainDutiesText.length > 150 ||       // 150자 이상 (기존 200자에서 낮춤)
      /[,.].*[,.]/.test(mainDutiesText)    // 여러 문장이 포함된 경우
    );

    if (shouldAutoSeparate) {
      console.log('🤖 [스마트 분리 트리거]:', {
        소스: source,
        텍스트길이: mainDutiesText.length,
        자동분리조건: '충족',
        실행방식: '즉시'
      });

      // 즉시 스마트 분리 실행 (대기 시간 없음)
      await performAutoSeparation(mainDutiesText);

    } else {
      console.log('📝 [스마트 분리 체크] 조건 미충족:', {
        소스: source,
        텍스트길이: mainDutiesText.length,
        여러문장여부: /[,.].*[,.]/.test(mainDutiesText)
      });
    }
  };

    // 스마트 자동 분리 실행 함수
  const performAutoSeparation = async (mainDutiesText) => {
    console.group('🤖 [스마트 자동 분리] 실행 시작');
    console.log('📝 대상 텍스트:', mainDutiesText.substring(0, 100) + '...');

    try {
      // 스마트 분리 API 사용
      const result = await jobPostingApi.separateMainDutiesSmart(mainDutiesText);

      if (result.success && result.smart_extraction) {
        const smartExtraction = result.smart_extraction;
        const displaySuggestions = smartExtraction.display_suggestions;

        console.log('✅ [스마트 분리 성공]:', {
          품질점수: (smartExtraction.quality_score * 100).toFixed(1) + '점',
          추천내용길이: smartExtraction.recommended_content.length,
          주요카테고리: displaySuggestions.primary_display?.length || 0,
          보조카테고리: displaySuggestions.secondary_display?.length || 0
        });

        // 분리된 데이터 저장
        setSeparatedDuties(result.separated_duties);

        // 스마트 추출된 가장 적합한 내용을 주요업무 필드에 설정
        const recommendedContent = smartExtraction.recommended_content ||
                                 result.separated_duties.core_responsibilities ||
                                 mainDutiesText;

        setFormData(prev => ({
          ...prev,
          mainDuties: recommendedContent
        }));

        console.log('🎯 [스마트 추출 적용] 가장 적합한 내용으로 업데이트');
        console.log('📝 추천 내용:', recommendedContent.substring(0, 80) + '...');
        console.log('💯 추출 품질:', (smartExtraction.quality_score * 100).toFixed(1) + '점');

        // UI에 스마트 분리 결과 표시 (선택적)
        if (displaySuggestions.primary_display?.length > 0) {
          console.log('🎨 [주요 카테고리]:',
            displaySuggestions.primary_display.map(item =>
              `${item.category} (${item.score.toFixed(2)}점)`
            ).join(', ')
          );
        }

        // 사용자에게 스마트 분리 완료 알림
        console.log('🔔 [스마트 분리 완료] 최적화된 내용으로 자동 업데이트됨');

      } else {
        console.warn('⚠️ [스마트 분리 실패] 일반 분리로 폴백');
        // 일반 분리로 폴백
        await performBasicSeparation(mainDutiesText);
      }
    } catch (error) {
      console.error('❌ [스마트 분리 오류]:', error.message);
      console.log('🔄 [폴백] 일반 분리로 재시도');
      // 오류 시 일반 분리로 폴백
      await performBasicSeparation(mainDutiesText);
    } finally {
      console.groupEnd();
    }
  };

  // 일반 분리 폴백 함수
  const performBasicSeparation = async (mainDutiesText) => {
    try {
      const result = await jobPostingApi.separateMainDuties(mainDutiesText);

      if (result.success) {
        setSeparatedDuties(result.separated_duties);

        const coreContent = result.separated_duties.core_responsibilities || mainDutiesText;
        setFormData(prev => ({
          ...prev,
          mainDuties: coreContent
        }));

        console.log('✅ [일반 분리 완료] 핵심업무 추출됨');
      }
    } catch (error) {
      console.error('❌ [일반 분리도 실패]:', error.message);
      // 최후의 수단: 원본 텍스트를 적절히 줄임
      const truncatedContent = mainDutiesText.length > 200
        ? mainDutiesText.substring(0, 200) + '...'
        : mainDutiesText;

      setFormData(prev => ({
        ...prev,
        mainDuties: truncatedContent
      }));

      console.log('🔄 [최종 폴백] 원본 텍스트 요약 적용');
    }
  };

  const [titleRecommendationModal, setTitleRecommendationModal] = useState({
    isOpen: false,
    finalFormData: null
  });

  // 주요업무 분리 기능 상태
  const [separatedDuties, setSeparatedDuties] = useState(null);
  const [isSeparating, setIsSeparating] = useState(false);

  // AI 챗봇 자동 입력 데이터 로드
  useEffect(() => {
    // 🎯 sessionStorage에서 자동 입력 데이터 확인
    const autoFillData = sessionStorage.getItem('autoFillJobPostingData');
    if (autoFillData) {
      try {
        const data = JSON.parse(autoFillData);
        console.log('🤖 [자동 입력] AI 채팅에서 전달받은 데이터:', data);

        // 자동 입력 데이터 매핑 (백엔드 필드 → 프론트엔드 필드)
        const mappedData = {
          // 기본 정보
          department: data.department || '개발팀',
          position: data.position || data.title || '',
          experience: data.experience_level || '신입',
          experienceLevel: data.experience_level || '신입',
          headcount: String(data.headcount || data.team_size || '0'),
          salary: data.salary || '',  // 급여 필드 추가

          // 업무 정보
          mainDuties: data.description || '',
          locationCity: data.location || '서울',
          workHours: data.working_hours || '09:00-18:00',  // 근무 시간 추가
          workDays: '평일 (월~금)',  // 근무 요일 기본값

          // 연락처 및 마감일
          contactEmail: data.contact_email || '',  // 연락처 이메일
          deadline: calculateDeadline(30),  // 30일 후 마감일 계산

          // 경력 연수 매핑
          experienceYears: extractExperienceYears(data.experience_level),

          // 기술 스택을 키워드로 매핑
          jobKeywords: Array.isArray(data.tech_stack) ? data.tech_stack : [],

          // 추가 정보는 자동 추출 API로 설정
          industry: '',
          jobCategory: '',
        };

        // 추가 필드 매핑
        if (data.requirements && Array.isArray(data.requirements)) {
          mappedData.mainDuties += (mappedData.mainDuties ? '\n\n' : '') +
            '• 주요 요구사항:\n' + data.requirements.map(req => `  - ${req}`).join('\n');
        }

        if (data.preferred_qualifications && Array.isArray(data.preferred_qualifications)) {
          mappedData.mainDuties += (mappedData.mainDuties ? '\n\n' : '') +
            '• 우대사항:\n' + data.preferred_qualifications.map(pref => `  - ${pref}`).join('\n');
        }

        if (data.benefits && Array.isArray(data.benefits)) {
          mappedData.mainDuties += (mappedData.mainDuties ? '\n\n' : '') +
            '• 혜택:\n' + data.benefits.map(benefit => `  - ${benefit}`).join('\n');
        }

                console.log('🎯 [자동 입력] 매핑된 폼 데이터:', mappedData);

        // 자동 입력 데이터 상세 분석
        console.log('📊 [자동 입력 분석]:', {
          총필드수: Object.keys(mappedData).length,
          채워진필드수: Object.values(mappedData).filter(v => v && v !== '').length,
          주요업무길이: (mappedData.mainDuties || '').length,
          키워드수: Array.isArray(mappedData.jobKeywords) ? mappedData.jobKeywords.length : 0,
          데이터크기: JSON.stringify(mappedData).length
        });

        // 🎭 애니메이션 자동 입력 시작 (사용자가 보는 앞에서 실시간으로)
        startAnimatedAutoFill(mappedData);

        // 사용 후 데이터 정리
        sessionStorage.removeItem('autoFillJobPostingData');
        console.log('✅ [자동 입력] sessionStorage 정리 완료');

      } catch (error) {
        console.error('❌ [자동 입력] 데이터 파싱 오류:', error);
      }
    }
  }, []);

  // AI 챗봇 이벤트 리스너
  useEffect(() => {
    const handleFormFieldUpdate = (event) => {
      const { field, value } = event.detail;
      console.log('🤖 [AI 필드 업데이트]:', field, value);

      updateAIFormData({ [field]: value }, 'ai_chatbot');
    };

    // 개별 필드 업데이트 이벤트 리스너들
    const fieldEvents = {
      'updateDepartment': 'department',
      'updateHeadcount': 'headcount',
      'updateSalary': 'salary',
      'updateWorkContent': 'mainDuties',
      'updateWorkHours': 'workHours',
      'updateWorkDays': 'workDays',
      'updateLocation': 'locationCity',
      'updateContactEmail': 'contactEmail',
      'updateDeadline': 'deadline'
    };

    console.log('🔧 [이벤트 리스너] AI 폼 이벤트 등록:', Object.keys(fieldEvents));

    window.addEventListener('updateFormField', handleFormFieldUpdate);

    Object.entries(fieldEvents).forEach(([eventName, fieldName]) => {
      const handler = (event) => {
        const { value } = event.detail;
        console.log(`🎯 [개별 이벤트] ${eventName} → ${fieldName}:`, value);
        updateAIFormData({ [fieldName]: value }, 'ai_individual_event');
      };
      window.addEventListener(eventName, handler);
    });

    return () => {
      window.removeEventListener('updateFormField', handleFormFieldUpdate);
      Object.keys(fieldEvents).forEach(eventName => {
        window.removeEventListener(eventName, () => {});
      });
    };
  }, []);

  // 인재상 데이터 로드
  useEffect(() => {
    loadCultures();
  }, []);

  // 🎭 애니메이션 자동 입력 함수
  const startAnimatedAutoFill = async (mappedData) => {
    console.log('🎬 [애니메이션 자동 입력] 시작!');

    // 입력할 필드들을 순서대로 정의 (빠른 속도로 조정)
    const fillSequence = [
      { field: 'department', value: mappedData.department, label: '구인 부서', delay: 200 },
      { field: 'position', value: mappedData.position, label: '채용 직무', delay: 300 },
      { field: 'experience', value: mappedData.experience, label: '경력 요구사항', delay: 250 },
      { field: 'experienceYears', value: mappedData.experienceYears, label: '경력 연수', delay: 200 },
      { field: 'headcount', value: mappedData.headcount, label: '채용 인원', delay: 200 },
      { field: 'salary', value: mappedData.salary, label: '급여 조건', delay: 200 },
      { field: 'workHours', value: mappedData.workHours, label: '근무 시간', delay: 200 },
      { field: 'workDays', value: mappedData.workDays, label: '근무 요일', delay: 200 },
      { field: 'locationCity', value: mappedData.locationCity, label: '근무 지역', delay: 250 },
      { field: 'contactEmail', value: mappedData.contactEmail, label: '연락처 이메일', delay: 200 },
      { field: 'deadline', value: mappedData.deadline, label: '마감일', delay: 200 },
      { field: 'mainDuties', value: mappedData.mainDuties, label: '주요 업무', delay: 400 },
    ];

    // 🎯 AI 입력 상태 활성화
    const validFields = fillSequence.filter(item => item.value && item.value.toString().trim());
    setAiInputStatus({
      isActive: true,
      currentField: '시작 중...',
      progress: 0,
      totalFields: validFields.length
    });

    console.log('🤖 [AI 입력] AI가 추출한 정보를 자동으로 입력하고 있습니다...');

    // 각 필드를 순차적으로 애니메이션과 함께 입력
    for (let i = 0; i < validFields.length; i++) {
      const { field, value, label, delay } = validFields[i];

      // 현재 입력 중인 필드 상태 업데이트
      setAiInputStatus(prev => ({
        ...prev,
        currentField: label,
        progress: i + 1
      }));

      console.log(`✍️ [AI 입력] ${i + 1}/${validFields.length}: ${label} 입력 중...`);

      // 타이핑 애니메이션 (긴 텍스트는 점진적으로)
      if (field === 'mainDuties' && value.length > 50) {
        await animateTyping(field, value, 15); // 15ms 간격으로 빠른 타이핑
      } else {
        // 짧은 필드는 바로 입력
        setFormData(prev => ({
          ...prev,
          [field]: value
        }));
      }

      // 다음 필드로 넘어가기 전 잠시 대기
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    // 키워드 배열은 마지막에 한번에 처리
    if (mappedData.jobKeywords && mappedData.jobKeywords.length > 0) {
      setAiInputStatus(prev => ({
        ...prev,
        currentField: '기술 키워드 설정 중...'
      }));

      setFormData(prev => ({
        ...prev,
        jobKeywords: mappedData.jobKeywords,
        industry: mappedData.industry,
        jobCategory: mappedData.jobCategory,
        experienceLevel: mappedData.experienceLevel
      }));

      await new Promise(resolve => setTimeout(resolve, 200));
    }

    // 🎉 완료 상태로 전환
    setAiInputStatus(prev => ({
      ...prev,
      currentField: '완료!',
      isActive: false
    }));

    console.log('🎉 [애니메이션 자동 입력] 완료! 모든 정보가 입력되었습니다.');

    // 1초 후 상태 초기화 및 자동 분야 추출 실행
    setTimeout(async () => {
      setAiInputStatus({
        isActive: false,
        currentField: '',
        progress: 0,
        totalFields: 0
      });

      // 자동 분야 추출 실행
      console.log('🤖 [자동 분야 추출] AI 입력 완료 후 자동 실행');
      try {
        await handleAutoExtractFields();
      } catch (error) {
        console.error('❌ [자동 분야 추출] 실패:', error);
      }
    }, 1000);
  };

  // 🎭 타이핑 애니메이션 함수
  const animateTyping = async (fieldName, fullText, typingSpeed = 50) => {
    const words = fullText.split(' ');
    let currentText = '';

    for (let i = 0; i < words.length; i++) {
      currentText += (i > 0 ? ' ' : '') + words[i];

      setFormData(prev => ({
        ...prev,
        [fieldName]: currentText
      }));

      // 타이핑 속도 조절
      await new Promise(resolve => setTimeout(resolve, typingSpeed));
    }
  };

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

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    // 급여 필드에 대한 특별 처리
    if (name === 'salary') {
      const numericValue = value.replace(/[^\d,~\-]/g, '');
      setFormData(prev => ({ ...prev, [name]: numericValue }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  // 급여를 표시용으로 포맷하는 함수
  const formatSalaryDisplay = (salaryValue) => {
    if (!salaryValue) return '';

    if (salaryValue.includes('만원') || salaryValue.includes('협의') || salaryValue.includes('면접')) {
      return salaryValue;
    }

    if (/^\d+([,\d~\-]*)?$/.test(salaryValue.trim())) {
      return `${salaryValue}만원`;
    }

    return salaryValue;
  };

  // 분야 값 매핑 함수 (백엔드 값 → 프론트엔드 옵션)
  const mapFieldValues = (backendValue, fieldType) => {
    if (fieldType === 'industry') {
      const industryMapping = {
        '기술/IT': 'IT/소프트웨어',
        'IT': 'IT/소프트웨어',
        '기술': 'IT/소프트웨어',
        // 다른 매핑들도 필요시 추가
      };
      return industryMapping[backendValue] || backendValue;
    }

    if (fieldType === 'jobCategory') {
      const categoryMapping = {
        '기술': '개발',
        'IT': '개발',
        '소프트웨어': '개발',
        // 다른 매핑들도 필요시 추가
      };
      return categoryMapping[backendValue] || backendValue;
    }

    return backendValue;
  };

  // 자동 분야 추출 함수
  const handleAutoExtractFields = async () => {
    if (isExtracting) return;

    setIsExtracting(true);

    try {
      console.log('🤖 분야 자동 추출 시작...');

      const inputData = {
        input_text: `${formData.department} ${formData.position} ${formData.mainDuties}`,
        department: formData.department || '',
        position: formData.position || '',
        main_duties: formData.mainDuties || ''
      };

      const response = await jobPostingApi.extractJobFields(inputData);

      if (response.success) {
        const { extracted_fields, confidence_scores } = response;

        // 백엔드 값을 프론트엔드 옵션에 맞게 매핑
        const mappedIndustry = mapFieldValues(extracted_fields.industry, 'industry');
        const mappedJobCategory = mapFieldValues(extracted_fields.job_category, 'jobCategory');

        console.log('🔄 [분야 매핑]:', {
          원본: { industry: extracted_fields.industry, jobCategory: extracted_fields.job_category },
          매핑후: { industry: mappedIndustry, jobCategory: mappedJobCategory }
        });

        // 추출 결과 저장
        setExtractionResults({
          industry: {
            value: mappedIndustry,
            confidence: confidence_scores.industry,
            isExtracted: true
          },
          jobCategory: {
            value: mappedJobCategory,
            confidence: confidence_scores.job_category,
            isExtracted: true
          }
        });

        // 폼 데이터 업데이트 (flushSync로 즉시 적용)
        flushSync(() => {
          setFormData(prev => {
            const updatedData = {
              ...prev,
              industry: mappedIndustry,
              jobCategory: mappedJobCategory
            };
            console.log('📝 폼 데이터 업데이트 (flushSync):', {
              이전값: { industry: prev.industry, jobCategory: prev.jobCategory },
              새로운값: { industry: mappedIndustry, jobCategory: mappedJobCategory },
              전체데이터: updatedData
            });
            return updatedData;
          });
        });

                console.log('✅ 분야 추출 완료:', {
          원본: { industry: extracted_fields.industry, jobCategory: extracted_fields.job_category },
          매핑후: { industry: mappedIndustry, jobCategory: mappedJobCategory },
          confidence: confidence_scores
        });

        // 성공 알림 (기본값 사용 여부에 따라 메시지 구분)
        const isDefaultIndustry = mappedIndustry === 'IT/소프트웨어' && confidence_scores.industry <= 0.5;
        const isDefaultJobCategory = mappedJobCategory === '개발' && confidence_scores.job_category <= 0.5;

        let message = '분야 추출이 완료되었습니다!\n\n';
        message += `산업 분야: ${mappedIndustry}`;
        if (isDefaultIndustry) {
          message += ' (기본값)';
        } else {
          message += ` (신뢰도: ${Math.round(confidence_scores.industry * 100)}%)`;
        }

        message += `\n직무 카테고리: ${mappedJobCategory}`;
        if (isDefaultJobCategory) {
          message += ' (기본값)';
        } else {
          message += ` (신뢰도: ${Math.round(confidence_scores.job_category * 100)}%)`;
        }

        if (isDefaultIndustry || isDefaultJobCategory) {
          message += '\n\n※ 일부 항목은 기본값이 적용되었습니다. 필요시 수정해주세요.';
        }

        alert(message);

      } else {
        throw new Error('추출 실패');
      }

    } catch (error) {
      console.error('❌ 분야 추출 실패:', error);

      // 추출 실패 시 기본값 설정 (flushSync로 즉시 적용)
      flushSync(() => {
        setFormData(prev => ({
          ...prev,
          industry: 'IT/소프트웨어',
          jobCategory: '개발'
        }));
      });

      setExtractionResults({
        industry: {
          value: 'IT/소프트웨어',
          confidence: 0.3,
          isExtracted: true,
          isDefault: true
        },
        jobCategory: {
          value: '개발',
          confidence: 0.3,
          isExtracted: true,
          isDefault: true
        }
      });

      alert('분야 추출에 실패하여 기본값을 설정했습니다.\n\n산업 분야: IT/소프트웨어 (기본값)\n직무 카테고리: 개발 (기본값)\n\n필요시 직접 수정해주세요.');
    } finally {
      setIsExtracting(false);
    }
  };

  // 주요업무 분리 함수
  const handleSeparateMainDuties = async () => {
    const startTime = Date.now();

    console.group('🔄 [AI 페이지 주요업무 분리] 프로세스 시작');
    console.log('📝 원본 텍스트 길이:', formData.mainDuties?.length || 0);
    console.log('📊 원본 텍스트 미리보기:', (formData.mainDuties || '').substring(0, 100) + '...');

    // 입력 검증 디버깅
    if (!formData.mainDuties || formData.mainDuties.length < 10) {
      console.warn('⚠️ [검증 실패] 주요업무 텍스트가 너무 짧음:', formData.mainDuties?.length || 0);
      console.groupEnd();
      alert('주요업무 내용이 너무 짧습니다. 더 상세히 입력해주세요.');
      return;
    }

    console.log('✅ [검증 통과] 분리 작업 시작');
    setIsSeparating(true);

    try {
      console.log('🚀 API 호출 시작');
      const apiStart = Date.now();
      const result = await jobPostingApi.separateMainDuties(formData.mainDuties);
      const apiTime = Date.now() - apiStart;

      console.log('📊 [API 응답 분석]:', {
        소요시간: `${apiTime}ms`,
        성공여부: result.success,
        응답크기: JSON.stringify(result).length,
        카테고리수: result.summary?.total_categories || 0
      });

      if (result.success) {
        // 분리 결과 상세 분석
        console.log('🎯 [분리 결과 상세]:', {
          총카테고리: result.summary.total_categories,
          채워진카테고리: result.summary.filled_categories,
          총문자수: result.summary.total_chars,
          분리품질: result.summary.separation_quality
        });

        // 각 카테고리별 내용 분석
        Object.entries(result.separated_duties).forEach(([category, content]) => {
          if (content && content.trim()) {
            console.log(`  📋 ${category}: ${content.length}자 - "${content.substring(0, 50)}..."`);
          }
        });

        setSeparatedDuties(result.separated_duties);

        // 분리된 내용을 폼 데이터에 적용
        updateAIFormData({
          mainDuties: result.separated_duties.core_responsibilities || formData.mainDuties
        }, 'duties_separation');

        alert(`✅ ${result.summary.total_categories}개 카테고리로 분리되었습니다!`);

        console.log('✅ [분리 완료] UI 업데이트 성공');
      } else {
        console.error('❌ [분리 실패] 서버에서 실패 응답');
        alert('주요업무 분리에 실패했습니다.');
      }
    } catch (error) {
      const errorTime = Date.now() - startTime;

      console.error('❌ [분리 오류]:', {
        오류타입: error.name,
        오류메시지: error.message,
        소요시간: `${errorTime}ms`,
        원본길이: formData.mainDuties?.length || 0
      });

      alert('주요업무 분리 중 오류가 발생했습니다.');
    } finally {
      const totalTime = Date.now() - startTime;
      setIsSeparating(false);

      console.log(`⏱️ [분리 완료] 총 소요시간: ${totalTime}ms`);
      console.groupEnd();
    }
  };

  const handleRegistration = () => {
    console.log('등록 버튼 클릭 - 제목 추천 모달 열기');
    setTitleRecommendationModal({
      isOpen: true,
      finalFormData: { ...formData }
    });
  };

  const handleTitleSelect = async (selectedTitle) => {
    const startTime = Date.now();

    console.group('🎯 [제목 선택 및 최종 제출]');
    console.log('📝 선택된 제목:', selectedTitle);
    console.log('🕐 제출 시작:', new Date().toISOString());

    const finalData = {
      ...titleRecommendationModal.finalFormData,
      title: selectedTitle
    };

    console.log('📋 [최종 데이터 준비]:', {
      제목: selectedTitle,
      부서: finalData.department,
      직무: finalData.position,
      위치: finalData.locationCity,
      인재상ID: finalData.selected_culture_id
    });

    try {
      // 채용공고 데이터 준비
      const jobData = {
        title: selectedTitle,
        company: '관리자 소속 회사', // 기본값
        location: finalData.locationCity || '서울특별시',
        type: 'full-time',
        salary: finalData.salary || '연봉 협의',
        experience: finalData.experienceLevel || '신입',
        description: finalData.mainDuties || '',
        requirements: '',
        benefits: '',
        deadline: finalData.deadline || '',
        department: finalData.department || '',
        headcount: finalData.headcount || '',
        work_type: finalData.mainDuties || '',
        work_hours: finalData.workHours || '',
        contact_email: finalData.contactEmail || '',

        // 분석용 필드들
        position: finalData.position || '',
        experience_min_years: finalData.experienceMinYears || null,
        experience_max_years: finalData.experienceMaxYears || null,
        experience_level: finalData.experienceLevel || '신입',
        main_duties: finalData.mainDuties || '',
        industry: finalData.industry || '',
        job_category: finalData.jobCategory || '',

        // 인재상 선택 필드
        selected_culture_id: finalData.selected_culture_id || null,

        // 기본 요구사항
        required_documents: ['resume'],
        required_skills: [],
        preferred_skills: [],
        require_portfolio_pdf: false,
        require_github_url: false,
        require_growth_background: false,
        require_motivation: false,
        require_career_history: false
      };

      console.log('📊 [최종 제출 데이터 분석]:', {
        총필드수: Object.keys(jobData).length,
        필수필드채움: {
          제목: jobData.title ? '✅' : '❌',
          부서: jobData.department ? '✅' : '❌',
          주요업무: jobData.main_duties ? '✅' : '❌',
          연락처: jobData.contact_email ? '✅' : '❌'
        },
        데이터크기: JSON.stringify(jobData).length,
        인재상선택: jobData.selected_culture_id ? '예' : '아니오'
      });

      console.log('🚀 [API 호출] 최종 채용공고 생성');
      const apiStart = Date.now();

      // API 호출하여 DB에 저장
      const newJob = await jobPostingApi.createJobPosting(jobData);
      const apiTime = Date.now() - apiStart;

      console.log('📊 [API 응답 분석]:', {
        소요시간: `${apiTime}ms`,
        성공여부: newJob ? '성공' : '실패',
        생성된ID: newJob?.id || 'N/A',
        응답크기: JSON.stringify(newJob || {}).length
      });

      setTitleRecommendationModal({
        isOpen: false,
        finalFormData: null
      });

      // 성공 메시지
      alert('채용공고가 성공적으로 등록되었습니다!');

      // 완료 후 job-posting 페이지로 이동
      navigate('/job-posting');
    } catch (error) {
      console.error('채용공고 생성 실패:', error);
      alert('채용공고 등록에 실패했습니다. 다시 시도해주세요.');
    }
  };

  const handleDirectTitleInput = async (customTitle) => {
    const startTime = Date.now();
    const selectedTitle = customTitle;

    console.group('🎯 [직접 제목 입력 및 최종 제출]');
    console.log('📝 입력된 제목:', selectedTitle);
    console.log('🕐 제출 시작:', new Date().toISOString());

    const finalData = {
      ...titleRecommendationModal.finalFormData,
      title: customTitle
    };

    try {
      // 채용공고 데이터 준비
      const jobData = {
        title: customTitle,
        company: '관리자 소속 회사', // 기본값
        location: finalData.locationCity || '서울특별시',
        type: 'full-time',
        salary: finalData.salary || '연봉 협의',
        experience: finalData.experienceLevel || '신입',
        description: finalData.mainDuties || '',
        requirements: '',
        benefits: '',
        deadline: finalData.deadline || '',
        department: finalData.department || '',
        headcount: finalData.headcount || '',
        work_type: finalData.mainDuties || '',
        work_hours: finalData.workHours || '',
        contact_email: finalData.contactEmail || '',

        // 분석용 필드들
        position: finalData.position || '',
        experience_min_years: finalData.experienceMinYears || null,
        experience_max_years: finalData.experienceMaxYears || null,
        experience_level: finalData.experienceLevel || '신입',
        main_duties: finalData.mainDuties || '',
        industry: finalData.industry || '',
        job_category: finalData.jobCategory || '',

        // 인재상 선택 필드
        selected_culture_id: finalData.selected_culture_id || null,

        // 기본 요구사항
        required_documents: ['resume'],
        required_skills: [],
        preferred_skills: [],
        require_portfolio_pdf: false,
        require_github_url: false,
        require_growth_background: false,
        require_motivation: false,
        require_career_history: false
      };

      console.log('생성할 채용공고 데이터:', jobData);

      // API 호출하여 DB에 저장
      const newJob = await jobPostingApi.createJobPosting(jobData);

      setTitleRecommendationModal({
        isOpen: false,
        finalFormData: null
      });

      if (newJob) {
        const totalTime = Date.now() - startTime;
        console.log('🎉 [등록 성공]:', {
          총처리시간: `${totalTime}ms`,
          생성된ID: newJob.id || 'N/A',
          제목: selectedTitle
        });

        // 성공 메시지
        alert('채용공고가 성공적으로 등록되었습니다!');

        // 완료 후 job-posting 페이지로 이동
        navigate('/job-posting');
      } else {
        console.error('❌ [등록 실패] API에서 빈 응답');
        alert('채용공고 등록에 실패했습니다.');
      }

    } catch (error) {
      const errorTime = Date.now() - startTime;

      console.error('❌ [제목 선택 제출 오류]:', {
        오류타입: error.name,
        오류메시지: error.message,
        소요시간: `${errorTime}ms`,
        선택제목: selectedTitle
      });

      alert('채용공고 등록에 실패했습니다. 다시 시도해주세요.');
    } finally {
      const totalTime = Date.now() - startTime;
      console.log(`⏱️ [제목 선택 완료] 총 소요시간: ${totalTime}ms`);
      console.groupEnd();
    }
  };

  const handleTitleModalClose = () => {
    setTitleRecommendationModal({
      isOpen: false,
      finalFormData: null
    });
  };

  const handleBack = () => {
    navigate('/job-posting');
  };

  const handleHome = () => {
    navigate('/');
  };

     // 샘플 데이터 자동입력 함수 (모든 필드 포함)
   const fillSampleData = (type) => {
     const sampleData = {
       frontend: {
         department: '개발팀',
         position: '프론트엔드 개발자',
         experience: '경력',
         experienceYears: '3',
         headcount: '2명',
         salary: '4000~6000만원',
         experienceLevel: '경력',
         experienceMinYears: 3,
         experienceMaxYears: 7,
         mainDuties: 'React, Vue.js를 활용한 웹 프론트엔드 개발, UI/UX 구현, 반응형 웹 개발, 컴포넌트 설계 및 개발',
         workHours: '09:00~18:00',
         workDays: '주 5일 (월~금)',
         locationCity: '서울특별시 강남구 테헤란로 123',
         contactEmail: 'recruit@company.com',
         deadline: '2024-03-31',
         industry: 'IT/소프트웨어',
         jobCategory: '개발',
         jobKeywords: ['React', 'Vue.js', 'JavaScript', 'TypeScript', 'HTML', 'CSS', '프론트엔드']
       },
       backend: {
         department: '개발팀',
         position: '백엔드 개발자',
         experience: '경력',
         experienceYears: '4',
         headcount: '3명',
         salary: '4500~7000만원',
         experienceLevel: '경력',
         experienceMinYears: 4,
         experienceMaxYears: 8,
         mainDuties: 'Node.js, Python 기반 서버 개발, API 설계 및 구현, 데이터베이스 설계, 마이크로서비스 아키텍처 구축',
         workHours: '10:00~19:00',
         workDays: '주 5일 (월~금)',
         locationCity: '서울특별시 강남구 테헤란로 123',
         contactEmail: 'tech@company.com',
         deadline: '2024-04-15',
         industry: 'IT/소프트웨어',
         jobCategory: '개발',
         jobKeywords: ['Node.js', 'Python', 'Java', 'Spring Boot', 'MySQL', 'PostgreSQL', 'MongoDB']
       },
       designer: {
         department: '디자인팀',
         position: 'UI/UX 디자이너',
         experience: '경력',
         experienceYears: '2',
         headcount: '1명',
         salary: '3500~5000만원',
         experienceLevel: '경력',
         experienceMinYears: 2,
         experienceMaxYears: 5,
         mainDuties: '웹/모바일 UI 디자인, 사용자 경험 설계, 프로토타이핑, 디자인 시스템 구축, 사용자 리서치',
         workHours: '09:30~18:30',
         workDays: '주 5일 (월~금)',
         locationCity: '서울특별시 강남구 테헤란로 123',
         contactEmail: 'design@company.com',
         deadline: '2024-03-25',
         industry: 'IT/소프트웨어',
         jobCategory: '디자인',
         jobKeywords: ['Figma', 'Adobe XD', 'Sketch', 'UI/UX', '프로토타이핑', '디자인 시스템']
       },
       marketing: {
         department: '마케팅팀',
         position: '디지털 마케팅 전문가',
         experience: '경력',
         experienceYears: '2',
         headcount: '2명',
         salary: '3000~4500만원',
         experienceLevel: '경력',
         experienceMinYears: 2,
         experienceMaxYears: 6,
         mainDuties: '온라인 광고 운영, SNS 마케팅, 콘텐츠 기획 및 제작, 데이터 분석, 마케팅 전략 수립',
         workHours: '09:00~18:00',
         workDays: '주 5일 (월~금)',
         locationCity: '서울특별시 강남구 테헤란로 123',
         contactEmail: 'marketing@company.com',
         deadline: '2024-04-01',
         industry: 'IT/소프트웨어',
         jobCategory: '마케팅',
         jobKeywords: ['Google Ads', 'Facebook Ads', 'SNS 마케팅', '콘텐츠 마케팅', '데이터 분석']
       },
       pm: {
         department: '기획팀',
         position: '프로젝트 매니저',
         experience: '경력',
         experienceYears: '5',
         headcount: '1명',
         salary: '5000~7000만원',
         experienceLevel: '고급',
         experienceMinYears: 5,
         experienceMaxYears: 10,
         mainDuties: '프로젝트 기획 및 관리, 일정 관리, 팀 간 협업 조율, 리스크 관리, 고객 커뮤니케이션',
         workHours: '09:00~18:00',
         workDays: '주 5일 (월~금)',
         locationCity: '서울특별시 강남구 테헤란로 123',
         contactEmail: 'pm@company.com',
         deadline: '2024-04-10',
         industry: 'IT/소프트웨어',
         jobCategory: '기획',
         jobKeywords: ['프로젝트 관리', '일정 관리', '팀 관리', '리스크 관리', '고객 커뮤니케이션']
       },
       sales: {
         department: '영업팀',
         position: '영업 담당자',
         experience: '경력',
         experienceYears: '3',
         headcount: '3명',
         salary: '3000~5000만원 + 인센티브',
         experienceLevel: '경력',
         experienceMinYears: 1,
         experienceMaxYears: 5,
         mainDuties: '신규 고객 발굴, 기존 고객 관리, 영업 제안서 작성, 계약 협상, 매출 목표 달성',
         workHours: '09:00~18:00',
         workDays: '주 5일 (월~금)',
         locationCity: '서울특별시 강남구 테헤란로 123',
         contactEmail: 'sales@company.com',
         deadline: '2024-03-28',
         industry: 'IT/소프트웨어',
         jobCategory: '영업',
         jobKeywords: ['영업', '고객 관리', '제안서 작성', '계약 협상', '매출 관리']
       }
     };

    const selectedData = sampleData[type];
    if (selectedData) {
      setFormData(prev => ({
        ...prev,
        ...selectedData
      }));

      // 성공 알림 (상세 정보 포함)
      alert(`🧪 ${selectedData.position} 샘플 데이터가 자동으로 입력되었습니다!\n\n📋 입력된 정보:\n• 부서: ${selectedData.department}\n• 직무: ${selectedData.position}\n• 경력: ${selectedData.experience} (${selectedData.experienceYears}년)\n• 모집인원: ${selectedData.headcount}\n• 주요업무: ${selectedData.mainDuties}\n• 근무시간: ${selectedData.workHours}\n• 근무일: ${selectedData.workDays}\n• 근무위치: ${selectedData.locationCity}\n• 연봉: ${selectedData.salary}\n• 연락처: ${selectedData.contactEmail}\n• 마감일: ${selectedData.deadline}`);
    }
  };

  return (
    <PageContainer>
      <ContentContainer>
        <Header>
          <HeaderLeft>
            <BackButton onClick={handleBack}>
              <FiArrowLeft size={20} />
            </BackButton>
            <Title>🤖 AI 채용공고 등록 도우미</Title>
          </HeaderLeft>
          <HeaderRight>
          </HeaderRight>
        </Header>

        {/* 🤖 AI 자동 입력 상태 표시 */}
        {(aiInputStatus.isActive || aiInputStatus.currentField === '완료!') && (
          <AIStatusBar>
            <AIStatusLeft>
              {aiInputStatus.isActive && <AIStatusSpinner />}
              <span>
                {aiInputStatus.isActive
                  ? `🤖 AI가 자동으로 입력하고 있습니다: ${aiInputStatus.currentField}`
                  : '🎉 AI 자동 입력 완료!'
                }
              </span>
            </AIStatusLeft>
            <AIStatusProgress>
              {aiInputStatus.totalFields > 0 && (
                <>
                  <span>{aiInputStatus.progress}/{aiInputStatus.totalFields}</span>
                  <AIProgressBar>
                    <AIProgressFill
                      progress={aiInputStatus.progress}
                      total={aiInputStatus.totalFields}
                    />
                  </AIProgressBar>
                </>
              )}
            </AIStatusProgress>
          </AIStatusBar>
        )}

        <Content>

          <FormSection>
                         <SectionTitle>
               👥
               구인 정보
             </SectionTitle>
            <FormGrid>
                                            <FormGroup>
                 <Label>
                   🏢
                   구인 부서
                 </Label>
                 <Input
                   type="text"
                   name="department"
                   value={formData.department || ''}
                   onChange={handleInputChange}
                   placeholder="예: 개발팀, 기획팀, 마케팅팀"
                   required
                   className={formData.department ? 'filled' : ''}
                 />
                 {formData.department && (
                   <FilledIndicator>
                     ✅ 입력됨: {formData.department}
                   </FilledIndicator>
                 )}
               </FormGroup>

               <FormGroup>
                 <Label>
                   💼
                   채용 직무
                 </Label>
                 <Input
                   type="text"
                   name="position"
                   value={formData.position || ''}
                   onChange={handleInputChange}
                   placeholder="예: 프론트엔드 개발자, 백엔드 개발자"
                   required
                   className={formData.position ? 'filled' : ''}
                 />
                 {formData.position && (
                   <FilledIndicator>
                     ✅ 입력됨: {formData.position}
                   </FilledIndicator>
                 )}
               </FormGroup>

                             <FormGroup>
                 <Label>
                   👥
                   구인 인원수
                 </Label>
                                 <Input
                  type="text"
                  name="headcount"
                  value={formData.headcount || '0명'}
                  onChange={handleInputChange}
                  placeholder="예: 0명, 1명, 2명, 3명"
                  required
                  className={formData.headcount ? 'filled' : ''}
                />
                {formData.headcount && (
                  <FilledIndicator>
                    ✅ 입력됨: {formData.headcount}
                  </FilledIndicator>
                )}
              </FormGroup>

                             <FormGroup>
                 <Label>
                   💼
                   주요 업무
                 </Label>
                <TextArea
                  name="mainDuties"
                  value={formData.mainDuties || ''}
                  onChange={handleInputChange}
                  placeholder="담당할 주요 업무를 입력해주세요"
                  required
                  className={formData.mainDuties ? 'filled' : ''}
                />
                {formData.mainDuties && (
                  <FilledIndicator>
                    ✅ 입력됨: {formData.mainDuties.length}자
                  </FilledIndicator>
                )}

                {/* 주요업무 분리 버튼 */}
                {formData.mainDuties && formData.mainDuties.length > 50 && (
                  <div style={{ marginTop: '12px' }}>
                    <Button
                      type="button"
                      className="ai"
                      onClick={handleSeparateMainDuties}
                      disabled={isSeparating}
                      style={{
                        fontSize: '14px',
                        padding: '8px 16px',
                        background: isSeparating
                          ? 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)'
                          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        cursor: isSeparating ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {isSeparating ? '🔄 분리 중...' : '🔄 업무 내용 분리하기'}
                    </Button>
                  </div>
                )}

                {/* 분리된 업무 필드들 표시 */}
                {separatedDuties && (
                  <div style={{
                    marginTop: '16px',
                    padding: '16px',
                    background: '#f8f9fa',
                    borderRadius: '8px',
                    border: '2px solid #e9ecef'
                  }}>
                    <h4 style={{
                      margin: '0 0 12px 0',
                      color: '#495057',
                      fontSize: '14px',
                      fontWeight: '600'
                    }}>
                      📋 분리된 업무 카테고리
                    </h4>
                    {Object.entries(separatedDuties).map(([key, value]) => (
                      value && value.trim() && (
                        <div key={key} style={{
                          marginBottom: '8px',
                          padding: '8px 12px',
                          background: 'white',
                          borderRadius: '6px',
                          border: '1px solid #dee2e6'
                        }}>
                          <strong style={{ fontSize: '12px', color: '#667eea' }}>
                            {key === 'core_responsibilities' && '🎯 핵심 담당업무'}
                            {key === 'daily_tasks' && '📅 일상 업무'}
                            {key === 'project_tasks' && '🚀 프로젝트 업무'}
                            {key === 'collaboration_tasks' && '🤝 협업 업무'}
                            {key === 'technical_tasks' && '⚙️ 기술적 업무'}
                            {key === 'management_tasks' && '👔 관리 업무'}
                          </strong>
                          <div style={{
                            fontSize: '13px',
                            color: '#495057',
                            marginTop: '4px',
                            lineHeight: '1.4'
                          }}>
                            {value}
                          </div>
                        </div>
                      )
                    ))}
                  </div>
                )}
              </FormGroup>

                             <FormGroup>
                 <Label>
                   ⏰
                   근무 시간
                 </Label>
                <Input
                  type="text"
                  name="workHours"
                  value={formData.workHours || ''}
                  onChange={handleInputChange}
                  placeholder="예: 09:00 ~ 18:00, 유연근무제"
                  required
                  className={formData.workHours ? 'filled' : ''}
                />
                {formData.workHours && (
                  <FilledIndicator>
                    ✅ 입력됨: {formData.workHours}
                  </FilledIndicator>
                )}
              </FormGroup>

                             <FormGroup>
                 <Label>
                   📅
                   근무 요일
                 </Label>
                <Input
                  type="text"
                  name="workDays"
                  value={formData.workDays || ''}
                  onChange={handleInputChange}
                  placeholder="예: 월~금, 월~토, 유연근무"
                  required
                  className={formData.workDays ? 'filled' : ''}
                />
                {formData.workDays && (
                  <FilledIndicator>
                    ✅ 입력됨: {formData.workDays}
                  </FilledIndicator>
                )}
              </FormGroup>

                             <FormGroup>
                 <Label>
                   💰
                   연봉
                 </Label>
                <div style={{ position: 'relative' }}>
                  <Input
                    type="text"
                    name="salary"
                    value={formData.salary || ''}
                    onChange={handleInputChange}
                    placeholder="예: 3000~5000, 4000, 연봉 협의"
                    className={formData.salary ? 'filled' : ''}
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
                  <FilledIndicator>
                    ✅ 입력됨: {formatSalaryDisplay(formData.salary)}
                  </FilledIndicator>
                )}
              </FormGroup>

                             <FormGroup>
                 <Label>
                   📧
                   연락처 이메일
                 </Label>
                <Input
                  type="email"
                  name="contactEmail"
                  value={formData.contactEmail || ''}
                  onChange={handleInputChange}
                  placeholder="인사담당자 이메일"
                  required
                  className={formData.contactEmail ? 'filled' : ''}
                />
                {formData.contactEmail && (
                  <FilledIndicator>
                    ✅ 입력됨: {formData.contactEmail}
                  </FilledIndicator>
                )}
              </FormGroup>

                             <FormGroup>
                 <Label>
                   🏢
                   회사 인재상
                 </Label>
                <Select
                  name="selected_culture_id"
                  value={formData.selected_culture_id || ''}
                  onChange={handleInputChange}
                  className={formData.selected_culture_id ? 'filled' : ''}
                >
                  <option value="">기본 인재상 사용</option>
                  {cultures.map(culture => (
                    <option key={culture.id} value={culture.id}>
                      {culture.name} {culture.is_default ? '(기본)' : ''}
                    </option>
                  ))}
                </Select>
                {formData.selected_culture_id && (
                  <FilledIndicator>
                    ✅ 선택됨: {cultures.find(c => c.id === formData.selected_culture_id)?.name}
                  </FilledIndicator>
                )}
                {!formData.selected_culture_id && defaultCulture && (
                  <FilledIndicator style={{ color: '#28a745' }}>
                    ✅ 기본 인재상: {defaultCulture.name}
                  </FilledIndicator>
                )}
              </FormGroup>

                             <FormGroup>
                 <Label>
                   🗓️
                   마감일
                 </Label>
                <Input
                  type="date"
                  name="deadline"
                  value={formData.deadline || ''}
                  onChange={handleInputChange}
                  required
                  className={formData.deadline ? 'filled' : ''}
                />
                {formData.deadline && (
                  <FilledIndicator>
                    ✅ 입력됨: {formData.deadline}
                  </FilledIndicator>
                )}
              </FormGroup>

                                            <FormGroup>
                 <Label>
                   📋
                   경력 수준
                 </Label>
                 <Select
                   name="experienceLevel"
                   value={formData.experienceLevel || '신입'}
                   onChange={handleInputChange}
                   className={formData.experienceLevel ? 'filled' : ''}
                 >
                   <option value="신입">신입</option>
                   <option value="경력">경력</option>
                   <option value="고급">고급</option>
                   <option value="무관">무관</option>
                 </Select>
                 {formData.experienceLevel && (
                   <FilledIndicator>
                     ✅ 선택됨: {formData.experienceLevel}
                   </FilledIndicator>
                 )}
               </FormGroup>

               <FormGroup>
                 <Label>
                   📊
                   경력 연차
                 </Label>
                 <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                   <Input
                     type="number"
                     name="experienceMinYears"
                     value={formData.experienceMinYears || ''}
                     onChange={handleInputChange}
                     placeholder="최소"
                     style={{ flex: 1 }}
                     className={formData.experienceMinYears ? 'filled' : ''}
                   />
                   <span style={{ color: '#666' }}>~</span>
                   <Input
                     type="number"
                     name="experienceMaxYears"
                     value={formData.experienceMaxYears || ''}
                     onChange={handleInputChange}
                     placeholder="최대"
                     style={{ flex: 1 }}
                     className={formData.experienceMaxYears ? 'filled' : ''}
                   />
                   <span style={{ color: '#666', fontSize: '14px' }}>년</span>
                 </div>
                 {(formData.experienceMinYears || formData.experienceMaxYears) && (
                   <FilledIndicator>
                     ✅ 입력됨: {formData.experienceMinYears || 0}~{formData.experienceMaxYears || '무제한'}년
                   </FilledIndicator>
                 )}
               </FormGroup>

                             <FormGroup>
                 <Label>
                   📍
                   근무 위치
                 </Label>
                <Input
                  type="text"
                  name="locationCity"
                  value={formData.locationCity || ''}
                  onChange={handleInputChange}
                  placeholder="예: 서울, 인천, 부산"
                  required
                  className={formData.locationCity ? 'filled' : ''}
                />
                {formData.locationCity && (
                  <FilledIndicator>
                    ✅ 입력됨: {formData.locationCity}
                  </FilledIndicator>
                )}
              </FormGroup>
                         </FormGrid>
           </FormSection>

           {/* 분석을 위한 추가 정보 섹션 */}
           <FormSection>
             <SectionTitle>
               🔍
               분석용 추가 정보
                                                            <AutoExtractButton
                 onClick={handleAutoExtractFields}
                 disabled={(!formData.department && !formData.position && !formData.mainDuties) || isExtracting}
               >
                 {isExtracting ? '🔄 추출 중...' : '🤖 자동 추출'}
               </AutoExtractButton>
             </SectionTitle>
             <FormGrid>
               <FormGroup>
                 <Label>
                   🏭
                   산업 분야
                 </Label>
                 <Select
                   name="industry"
                   value={formData.industry || ''}
                   onChange={(e) => {
                     console.log('🔄 산업 분야 Select onChange:', e.target.value);
                     handleInputChange(e);
                   }}
                   className={formData.industry ? 'filled' : ''}
                 >
                   <option value="">선택해주세요</option>
                   <option value="IT/소프트웨어">IT/소프트웨어</option>
                   <option value="금융/보험">금융/보험</option>
                   <option value="제조업">제조업</option>
                   <option value="유통/서비스">유통/서비스</option>
                   <option value="미디어/엔터테인먼트">미디어/엔터테인먼트</option>
                   <option value="의료/바이오">의료/바이오</option>
                   <option value="교육">교육</option>
                   <option value="기타">기타</option>
                 </Select>
                 {formData.industry && (
                   <FilledIndicator>
                     ✅ 선택됨: {formData.industry}
                     {extractionResults.industry && (
                       <ConfidenceScore confidence={extractionResults.industry.confidence}>
                         신뢰도: {Math.round(extractionResults.industry.confidence * 100)}%
                       </ConfidenceScore>
                     )}
                   </FilledIndicator>
                 )}
                 {extractionResults.industry?.isExtracted && (
                   <ExtractionIndicator isDefault={extractionResults.industry?.isDefault}>
                     {extractionResults.industry?.isDefault
                       ? '⚠️ 추출 실패로 기본값이 적용되었습니다'
                       : '🤖 AI가 자동으로 추출한 분야입니다'
                     }
                   </ExtractionIndicator>
                 )}
               </FormGroup>

               <FormGroup>
                 <Label>
                   📂
                   직무 카테고리
                 </Label>
                 <Select
                   name="jobCategory"
                   value={formData.jobCategory || ''}
                   onChange={(e) => {
                     console.log('🔄 직무 카테고리 Select onChange:', e.target.value);
                     handleInputChange(e);
                   }}
                   className={formData.jobCategory ? 'filled' : ''}
                 >
                   <option value="">선택해주세요</option>
                   <option value="개발">개발</option>
                   <option value="기획">기획</option>
                   <option value="디자인">디자인</option>
                   <option value="마케팅">마케팅</option>
                   <option value="영업">영업</option>
                   <option value="운영">운영</option>
                   <option value="인사">인사</option>
                   <option value="기타">기타</option>
                 </Select>
                 {formData.jobCategory && (
                   <FilledIndicator>
                     ✅ 선택됨: {formData.jobCategory}
                     {extractionResults.jobCategory && (
                       <ConfidenceScore confidence={extractionResults.jobCategory.confidence}>
                         신뢰도: {Math.round(extractionResults.jobCategory.confidence * 100)}%
                       </ConfidenceScore>
                     )}
                   </FilledIndicator>
                 )}
                 {extractionResults.jobCategory?.isExtracted && (
                   <ExtractionIndicator isDefault={extractionResults.jobCategory?.isDefault}>
                     {extractionResults.jobCategory?.isDefault
                       ? '⚠️ 추출 실패로 기본값이 적용되었습니다'
                       : '🤖 AI가 자동으로 추출한 카테고리입니다'
                     }
                   </ExtractionIndicator>
                 )}
               </FormGroup>
             </FormGrid>
           </FormSection>

           {/* 🧪 테스트용 샘플 데이터 섹션 (개발/테스트 환경에서만 표시) */}
           {isDevelopment && (
             <TestSection>
               <TestSectionTitle>
                 🧪 테스트용 샘플 데이터 (개발/테스트 전용)
               </TestSectionTitle>
               <TestDescription>
                 실제 운영에서는 이 섹션이 숨겨집니다. 개발 및 테스트 목적으로만 사용됩니다.
               </TestDescription>
               <SampleButtonGrid>
                 <SampleButton onClick={() => fillSampleData('frontend')}>
                   💻 프론트엔드 개발자
                 </SampleButton>
                 <SampleButton onClick={() => fillSampleData('backend')}>
                   ⚙️ 백엔드 개발자
                 </SampleButton>
                 <SampleButton onClick={() => fillSampleData('designer')}>
                   🎨 UI/UX 디자이너
                 </SampleButton>
                 <SampleButton onClick={() => fillSampleData('marketing')}>
                   📢 마케팅 전문가
                 </SampleButton>
                 <SampleButton onClick={() => fillSampleData('pm')}>
                   📋 프로젝트 매니저
                 </SampleButton>
                 <SampleButton onClick={() => fillSampleData('sales')}>
                   💼 영업 담당자
                 </SampleButton>
               </SampleButtonGrid>
             </TestSection>
           )}

           <ButtonGroup>
            <Button className="secondary" onClick={handleBack}>
              <FiArrowLeft size={16} />
              취소
            </Button>
            <Button className="primary" onClick={handleRegistration}>
              <FiCheck size={16} />
              등록 완료
            </Button>
          </ButtonGroup>
        </Content>
      </ContentContainer>

      {/* 제목 추천 모달 */}
      <TitleRecommendationModal
        isOpen={titleRecommendationModal.isOpen}
        onClose={handleTitleModalClose}
        formData={titleRecommendationModal.finalFormData}
        onTitleSelect={handleTitleSelect}
        onDirectInput={handleDirectTitleInput}
      />
    </PageContainer>
  );
};

export default AIJobRegistrationPage;
