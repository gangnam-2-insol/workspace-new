import React, { useState, useEffect } from 'react';
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

const AIJobRegistrationPage = () => {
  const navigate = useNavigate();

  // 개발/테스트 환경 여부 확인 (실제 운영에서는 false로 설정)
  const isDevelopment = process.env.NODE_ENV === 'development' || process.env.REACT_APP_SHOW_TEST_SECTION === 'true';

  // 인재상 관련 상태
  const [cultures, setCultures] = useState([]);
  const [defaultCulture, setDefaultCulture] = useState(null);
  const [loadingCultures, setLoadingCultures] = useState(false);

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

  const [titleRecommendationModal, setTitleRecommendationModal] = useState({
    isOpen: false,
    finalFormData: null
  });

  // AI 챗봇 이벤트 리스너
  useEffect(() => {
    const handleFormFieldUpdate = (event) => {
      const { field, value } = event.detail;
      console.log('AI 필드 업데이트:', field, value);

      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
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

    window.addEventListener('updateFormField', handleFormFieldUpdate);

    Object.entries(fieldEvents).forEach(([eventName, fieldName]) => {
      const handler = (event) => {
        const { value } = event.detail;
        setFormData(prev => ({ ...prev, [fieldName]: value }));
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

  const handleRegistration = () => {
    console.log('등록 버튼 클릭 - 제목 추천 모달 열기');
    setTitleRecommendationModal({
      isOpen: true,
      finalFormData: { ...formData }
    });
  };

  const handleTitleSelect = async (selectedTitle) => {
    console.log('추천 제목 선택:', selectedTitle);
    const finalData = {
      ...titleRecommendationModal.finalFormData,
      title: selectedTitle
    };

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

      console.log('생성할 채용공고 데이터:', jobData);

      // API 호출하여 DB에 저장
      const newJob = await jobPostingApi.createJobPosting(jobData);
      console.log('채용공고 생성 성공:', newJob);

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
    console.log('직접 입력 제목:', customTitle);
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
      console.log('채용공고 생성 성공:', newJob);

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
                  value={formData.headcount || ''}
                  onChange={handleInputChange}
                  placeholder="예: 1명, 2명, 3명"
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
                   onChange={handleInputChange}
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
                   </FilledIndicator>
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
                   onChange={handleInputChange}
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
                   </FilledIndicator>
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
