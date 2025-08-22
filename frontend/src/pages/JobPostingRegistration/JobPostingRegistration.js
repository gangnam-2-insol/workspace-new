import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FiPlus, 
  FiEdit3, 
  FiTrash2, 
  FiEye, 
  FiCalendar,
  FiMapPin,
  FiDollarSign,
  FiUsers,
  FiBriefcase,
  FiClock,
  FiGlobe,
  FiFolder,
  FiZap
} from 'react-icons/fi';
import JobDetailModal from './JobDetailModal';

import TextBasedRegistration from './TextBasedRegistration';
import ImageBasedRegistration from './ImageBasedRegistration';
import TemplateModal from './TemplateModal';

import jobPostingApi from '../../services/jobPostingApi';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
`;

const AddButton = styled(motion.button)`
  background: linear-gradient(135deg, #00c851, #00a844);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 200, 81, 0.3);
  }
`;

const FormContainer = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
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
  gap: 16px;
  justify-content: flex-end;
`;

const Button = styled.button`
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;

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

const JobListContainer = styled.div`
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
`;

const JobCard = styled(motion.div)`
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
`;

const JobHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const JobTitle = styled.h3`
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
`;

const JobStatus = styled.span`
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;

  &.active {
    background: rgba(0, 200, 81, 0.1);
    color: var(--primary-color);
  }

  &.draft {
    background: rgba(255, 193, 7, 0.1);
    color: #ffc107;
  }

  &.closed {
    background: rgba(108, 117, 125, 0.1);
    color: #6c757d;
  }
`;

const JobDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
`;

const JobDetail = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
`;

const JobActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;

  &.edit {
    background: rgba(0, 123, 255, 0.1);
    color: #007bff;

    &:hover {
      background: rgba(0, 123, 255, 0.2);
    }
  }

  &.delete {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;

    &:hover {
      background: rgba(220, 53, 69, 0.2);
    }
  }

  &.view {
    background: rgba(40, 167, 69, 0.1);
    color: #28a745;

    &:hover {
      background: rgba(40, 167, 69, 0.2);
    }
  }

  &.publish {
    background: rgba(255, 193, 7, 0.1);
    color: #ffc107;

    &:hover {
      background: rgba(255, 193, 7, 0.2);
    }

    &.disabled {
      background: rgba(108, 117, 125, 0.1);
      color: #6c757d;
      cursor: not-allowed;

      &:hover {
        background: rgba(108, 117, 125, 0.1);
      }
    }
  }
`;

const JobPostingRegistration = () => {
  const navigate = useNavigate();
  const [showForm, setShowForm] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [modalMode, setModalMode] = useState('view'); // 'view' or 'edit'
  const [showModal, setShowModal] = useState(false);

  const [showTextRegistration, setShowTextRegistration] = useState(false);
  const [showImageRegistration, setShowImageRegistration] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);

  const [templates, setTemplates] = useState([]);
  const [autoFillData, setAutoFillData] = useState(null);

  const [formData, setFormData] = useState({
    title: '',
    company: '',
    location: '',
    type: 'full-time',
    salary: '',
    experience: '',
    education: '',
    description: '',
    requirements: '',
    benefits: '',
    deadline: '',
    // 지원자 요구 항목 (MongoDB 컬렉션 구조 기반)
    required_documents: ['resume'],
    required_skills: [],
    required_experience_years: null,
    require_portfolio_pdf: false,
    require_github_url: false,
    require_growth_background: false,
    require_motivation: false,
    require_career_history: false,
    max_file_size_mb: 50,
    allowed_file_types: ['pdf', 'doc', 'docx']
  });

      // 챗봇 액션 이벤트 리스너
    useEffect(() => {
      // URL 파라미터에서 자동입력 데이터 확인
      const urlParams = new URLSearchParams(window.location.search);
      const autoFillParam = urlParams.get('autoFill');
      if (autoFillParam) {
        try {
          const decodedData = JSON.parse(decodeURIComponent(autoFillParam));
          setAutoFillData(decodedData);
          console.log('자동입력 데이터 감지:', decodedData);
        } catch (error) {
          console.error('자동입력 데이터 파싱 오류:', error);
        }
      }

      const handleRegistrationMethod = () => {
        console.log('=== 새 공고 등록 - 픽톡 에이전트 시작 ===');
        setShowTextRegistration(true);
        // AI 챗봇 자동 시작
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('startTextBasedAIChatbot'));
        }, 500);
      };

      const handleTextRegistration = () => {
        setShowTextRegistration(true);
      };

      const handleImageRegistration = () => {
        setShowImageRegistration(true);
      };

      const handleTemplateModal = () => {
        setShowTemplateModal(true);
      };



    // 새로운 자동 플로우 핸들러들
    const handleStartTextBasedFlow = () => {
      setShowTextRegistration(true);
      // TextBasedRegistration 컴포넌트에서 AI 챗봇 자동 시작을 위해 이벤트 발생
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('startTextBasedAIChatbot'));
      }, 500);
    };

    const handleStartImageBasedFlow = () => {
      setShowImageRegistration(true);
      // ImageBasedRegistration 컴포넌트에서 AI 자동 시작을 위해 이벤트 발생
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('startImageBasedAIFlow'));
      }, 500);
    };

    // AI 도우미 시작 핸들러 추가
    const handleStartAIAssistant = () => {
      console.log('=== AI 도우미 시작됨 ===');
      console.log('현재 상태: showTextRegistration =', showTextRegistration);
      console.log('이벤트 리스너가 제대로 등록되었는지 확인');
      
      setShowTextRegistration(true);
      console.log('텍스트 기반 등록 모달 열기 완료 - showTextRegistration = true로 설정됨');
      
      // 즉시 상태 확인
      setTimeout(() => {
        console.log('1초 후 상태 확인: showTextRegistration =', showTextRegistration);
      }, 1000);
      
      // 1초 후 자동으로 AI 챗봇 시작
      setTimeout(() => {
        console.log('1초 타이머 완료 - startTextBasedAIChatbot 이벤트 발생');
        window.dispatchEvent(new CustomEvent('startTextBasedAIChatbot'));
      }, 1000);
    };

    // 채팅봇 수정 명령 핸들러들
    const handleUpdateDepartment = (event) => {
      const newDepartment = event.detail.value;
      console.log('부서 업데이트:', newDepartment);
      // 현재 열린 모달이나 폼에서 부서 정보 업데이트
      if (showTextRegistration) {
        window.dispatchEvent(new CustomEvent('updateTextFormDepartment', { 
          detail: { value: newDepartment } 
        }));
      }
    };

    const handleUpdateHeadcount = (event) => {
      const newHeadcount = event.detail.value;
      console.log('인원 업데이트:', newHeadcount);
      // 현재 열린 모달이나 폼에서 인원 정보 업데이트
      if (showTextRegistration) {
        window.dispatchEvent(new CustomEvent('updateTextFormHeadcount', { 
          detail: { value: newHeadcount } 
        }));
      }
    };

    const handleUpdateSalary = (event) => {
      const newSalary = event.detail.value;
      console.log('급여 업데이트:', newSalary);
      // 현재 열린 모달이나 폼에서 급여 정보 업데이트
      if (showTextRegistration) {
        window.dispatchEvent(new CustomEvent('updateTextFormSalary', { 
          detail: { value: newSalary } 
        }));
      }
    };

    const handleUpdateWorkContent = (event) => {
      const newWorkContent = event.detail.value;
      console.log('업무 내용 업데이트:', newWorkContent);
      // 현재 열린 모달이나 폼에서 업무 내용 업데이트
      if (showTextRegistration) {
        window.dispatchEvent(new CustomEvent('updateTextFormWorkContent', { 
          detail: { value: newWorkContent } 
        }));
      }
    };





    // 이벤트 리스너 등록
    window.addEventListener('openRegistrationMethod', handleRegistrationMethod);
    window.addEventListener('openTextRegistration', handleTextRegistration);
    window.addEventListener('openImageRegistration', handleImageRegistration);
    window.addEventListener('openTemplateModal', handleTemplateModal);

    window.addEventListener('startTextBasedFlow', handleStartTextBasedFlow);
    window.addEventListener('startImageBasedFlow', handleStartImageBasedFlow);
    window.addEventListener('startAIAssistant', handleStartAIAssistant);

    
    // 채팅봇 수정 명령 이벤트 리스너 등록
    window.addEventListener('updateDepartment', handleUpdateDepartment);
    window.addEventListener('updateHeadcount', handleUpdateHeadcount);
    window.addEventListener('updateSalary', handleUpdateSalary);
    window.addEventListener('updateWorkContent', handleUpdateWorkContent);

    // 클린업
    return () => {
      window.removeEventListener('openRegistrationMethod', handleRegistrationMethod);
      window.removeEventListener('openTextRegistration', handleTextRegistration);
      window.removeEventListener('openImageRegistration', handleImageRegistration);
      window.removeEventListener('openTemplateModal', handleTemplateModal);

      window.removeEventListener('startTextBasedFlow', handleStartTextBasedFlow);
      window.removeEventListener('startImageBasedFlow', handleStartImageBasedFlow);
      window.removeEventListener('startAIAssistant', handleStartAIAssistant);

      
      // 채팅봇 수정 명령 이벤트 리스너 제거
      window.removeEventListener('updateDepartment', handleUpdateDepartment);
      window.removeEventListener('updateHeadcount', handleUpdateHeadcount);
      window.removeEventListener('updateSalary', handleUpdateSalary);
      window.removeEventListener('updateWorkContent', handleUpdateWorkContent);
    };
  }, []);

  // 모든 모달창 초기화 함수
  const resetAllModals = () => {
    console.log('=== 모든 모달창 초기화 시작 ===');
    setShowForm(false);
    setShowModal(false);

    setShowTextRegistration(false);
    setShowImageRegistration(false);
    setShowTemplateModal(false);

    setSelectedJob(null);
    setModalMode('view');
    
    // 플로팅 챗봇 다시 표시
    const floatingChatbot = document.querySelector('.floating-chatbot');
    if (floatingChatbot) {
      floatingChatbot.style.display = 'flex';
    }
    window.dispatchEvent(new CustomEvent('showFloatingChatbot'));
    
    console.log('=== 모든 모달창 초기화 완료 ===');
  };

  const [jobPostings, setJobPostings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 채용공고 목록 로드
  useEffect(() => {
    loadJobPostings();
  }, []);

  const loadJobPostings = async () => {
    try {
      setLoading(true);
      const data = await jobPostingApi.getJobPostings();
      setJobPostings(data);
      setError(null);
    } catch (err) {
      console.error('채용공고 로드 실패:', err);
      setError('채용공고 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const newJob = await jobPostingApi.createJobPosting(formData);
      setJobPostings(prev => [newJob, ...prev]);
      setFormData({
        title: '',
        company: '',
        location: '',
        type: 'full-time',
        salary: '',
        experience: '',
        education: '',
        description: '',
        requirements: '',
        benefits: '',
        deadline: '',
        // 지원자 요구 항목 초기화
        required_documents: ['resume'],
        required_skills: [],
        required_experience_years: null,
        require_portfolio_pdf: false,
        require_github_url: false,
        require_growth_background: false,
        require_motivation: false,
        require_career_history: false,
        max_file_size_mb: 50,
        allowed_file_types: ['pdf', 'doc', 'docx']
      });
      setShowForm(false);
    } catch (err) {
      console.error('채용공고 생성 실패:', err);
      alert('채용공고 생성에 실패했습니다.');
    }
  };

  const handleDelete = async (id) => {
    try {
      await jobPostingApi.deleteJobPosting(id);
      setJobPostings(prev => prev.filter(job => job.id !== id));
      setShowModal(false);
    } catch (err) {
      console.error('채용공고 삭제 실패:', err);
      alert('채용공고 삭제에 실패했습니다.');
    }
  };

  const handlePublish = async (id) => {
    try {
      await jobPostingApi.publishJobPosting(id);
      setJobPostings(prev => 
        prev.map(job => 
          job.id === id ? { ...job, status: 'published' } : job
        )
      );
    } catch (err) {
      console.error('채용공고 발행 실패:', err);
      alert('채용공고 발행에 실패했습니다.');
    }
  };

  const handleViewJob = (job) => {
    setSelectedJob(job);
    setModalMode('view');
    setShowModal(true);
  };

  const handleEditJob = (job) => {
    setSelectedJob(job);
    setModalMode('edit');
    setShowModal(true);
  };

  const handleSaveJob = async (updatedJob) => {
    try {
      const { id, ...updateData } = updatedJob;
      await jobPostingApi.updateJobPosting(id, updateData);
      setJobPostings(prev => 
        prev.map(job => 
          job.id === updatedJob.id ? updatedJob : job
        )
      );
      setShowModal(false);
    } catch (err) {
      console.error('채용공고 수정 실패:', err);
      alert('채용공고 수정에 실패했습니다.');
    }
  };



  const handleTextRegistrationComplete = async (data) => {
    console.log('TextBasedRegistration 완료 데이터:', data);
    
    try {
      const jobData = {
        title: data.title,
        company: '관리자 소속 회사', // 자동 적용
        location: data.locationCity || data.location || '서울특별시 강남구',
        type: 'full-time',
        salary: data.salary || '연봉 4,000만원 - 6,000만원',
        experience: data.experience || '2년이상',
        education: '대졸 이상',
        description: data.mainDuties || data.description || '웹개발', // mainDuties를 description으로 매핑
        requirements: data.requirements || 'JavaScript, React 실무 경험',
        benefits: data.benefits || '주말보장, 재택가능',
        deadline: data.deadline || '9월 3일까지'
      };
      
      console.log('생성할 채용공고 데이터:', jobData);
      const newJob = await jobPostingApi.createJobPosting(jobData);
      setJobPostings(prev => [newJob, ...prev]);
      
      // 모든 모달창 초기화
      resetAllModals();
    } catch (err) {
      console.error('채용공고 생성 실패:', err);
      alert('채용공고 생성에 실패했습니다.');
    }
  };

  const handleImageRegistrationComplete = async (data) => {
    console.log('ImageBasedRegistration 완료 데이터:', data);
    
    try {
      const jobData = {
        title: data.title,
        company: '관리자 소속 회사', // 자동 적용
        location: data.locationCity || data.location || '서울특별시 강남구',
        type: 'full-time',
        salary: data.salary || '연봉 4,000만원 - 6,000만원',
        experience: data.experience || '2년이상',
        education: '대졸 이상',
        description: data.mainDuties || data.description || '웹개발',
        requirements: data.requirements || 'JavaScript, React 실무 경험',
        benefits: data.benefits || '주말보장, 재택가능',
        deadline: data.deadline || '9월 3일까지'
      };
      
      console.log('생성할 채용공고 데이터:', jobData);
      const newJob = await jobPostingApi.createJobPosting(jobData);
      setJobPostings(prev => [newJob, ...prev]);
      
      // 모든 모달창 초기화
      resetAllModals();
    } catch (err) {
      console.error('채용공고 생성 실패:', err);
      alert('채용공고 생성에 실패했습니다.');
    }
  };

  const handleSaveTemplate = (template) => {
    setTemplates(prev => [...prev, template]);
  };

  const handleLoadTemplate = (templateData) => {
    // 템플릿 데이터를 TextBasedRegistration에 전달
    setShowTemplateModal(false);
    setShowTextRegistration(true);
    // 여기서는 템플릿 데이터를 전달하는 로직이 필요합니다
  };

  const handleDeleteTemplate = (templateId) => {
    setTemplates(prev => prev.filter(template => template.id !== templateId));
  };



  const getStatusText = (status) => {
    switch (status) {
      case 'active': return '모집중';
      case 'draft': return '임시저장';
      case 'closed': return '마감';
      default: return status;
    }
  };

  return (
    <Container>
      <Header>
        <Title>채용공고 등록</Title>
        <div style={{ display: 'flex', gap: '12px' }}>
          <AddButton
            data-testid="add-job-button"
            onClick={() => navigate('/ai-job-registration')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiPlus size={20} />
            새 공고 등록
          </AddButton>
          <AddButton
            onClick={() => setShowTemplateModal(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }}
          >
            <FiFolder size={20} />
            템플릿 관리
          </AddButton>
        </div>
      </Header>

      {showForm && (
        <FormContainer
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <form onSubmit={handleSubmit}>
            <FormGrid>
              <FormGroup>
                <Label>공고 제목 *</Label>
                <Input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="예: 시니어 프론트엔드 개발자"
                  required
                />
              </FormGroup>

              <FormGroup>
                <Label>회사명 *</Label>
                <Input
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleInputChange}
                  placeholder="회사명을 입력하세요"
                  required
                />
              </FormGroup>

              <FormGroup>
                <Label>근무지 *</Label>
                <Input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="예: 서울 강남구"
                  required
                />
              </FormGroup>

              <FormGroup>
                <Label>고용 형태 *</Label>
                <Select
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  required
                >
                  <option value="full-time">정규직</option>
                  <option value="part-time">파트타임</option>
                  <option value="contract">계약직</option>
                  <option value="intern">인턴</option>
                </Select>
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

              <FormGroup>
                <Label>경력 요구사항</Label>
                <Input
                  type="text"
                  name="experience"
                  value={formData.experience}
                  onChange={handleInputChange}
                  placeholder="예: 3년 이상"
                />
              </FormGroup>

              <FormGroup>
                <Label>학력 요구사항</Label>
                <Input
                  type="text"
                  name="education"
                  value={formData.education}
                  onChange={handleInputChange}
                  placeholder="예: 대졸 이상"
                />
              </FormGroup>

              <FormGroup>
                <Label>마감일</Label>
                <Input
                  type="date"
                  name="deadline"
                  value={formData.deadline}
                  onChange={handleInputChange}
                />
              </FormGroup>
            </FormGrid>

            <FormGroup>
              <Label>업무 내용 *</Label>
              <TextArea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="담당 업무와 주요 역할을 설명해주세요"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>자격 요건</Label>
              <TextArea
                name="requirements"
                value={formData.requirements}
                onChange={handleInputChange}
                placeholder="필요한 기술 스택, 자격증, 경험 등을 작성해주세요"
              />
            </FormGroup>

            <FormGroup>
              <Label>복리후생</Label>
              <TextArea
                name="benefits"
                value={formData.benefits}
                onChange={handleInputChange}
                placeholder="제공되는 복리후생을 작성해주세요"
              />
            </FormGroup>

            {/* 지원자 요구 항목 섹션 */}
            <div style={{ 
              borderTop: '2px solid #e5e7eb', 
              marginTop: '32px', 
              paddingTop: '24px' 
            }}>
              <h3 style={{ 
                marginBottom: '24px', 
                color: 'var(--text-primary)', 
                fontSize: '18px',
                fontWeight: '600'
              }}>
                📋 지원자 요구 항목
              </h3>
              
              <FormGrid>
                <FormGroup>
                  <Label>필수 제출 서류 *</Label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        checked={formData.required_documents.includes('resume')}
                        onChange={(e) => {
                          const newDocs = e.target.checked 
                            ? [...formData.required_documents, 'resume']
                            : formData.required_documents.filter(doc => doc !== 'resume');
                          setFormData(prev => ({ ...prev, required_documents: newDocs }));
                        }}
                      />
                      이력서 (필수)
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        checked={formData.required_documents.includes('cover_letter')}
                        onChange={(e) => {
                          const newDocs = e.target.checked 
                            ? [...formData.required_documents, 'cover_letter']
                            : formData.required_documents.filter(doc => doc !== 'cover_letter');
                          setFormData(prev => ({ ...prev, required_documents: newDocs }));
                        }}
                      />
                      자기소개서
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        checked={formData.required_documents.includes('portfolio')}
                        onChange={(e) => {
                          const newDocs = e.target.checked 
                            ? [...formData.required_documents, 'portfolio']
                            : formData.required_documents.filter(doc => doc !== 'portfolio');
                          setFormData(prev => ({ ...prev, required_documents: newDocs }));
                        }}
                      />
                      포트폴리오
                    </label>
                  </div>
                </FormGroup>

                <FormGroup>
                  <Label>필수 기술 스택</Label>
                  <Input
                    type="text"
                    placeholder="예: JavaScript, React, TypeScript (쉼표로 구분)"
                    value={formData.required_skills.join(', ')}
                    onChange={(e) => {
                      const skills = e.target.value.split(',').map(skill => skill.trim()).filter(skill => skill);
                      setFormData(prev => ({ ...prev, required_skills: skills }));
                    }}
                  />
                </FormGroup>

                <FormGroup>
                  <Label>필수 경력 연차</Label>
                  <Input
                    type="number"
                    placeholder="예: 3"
                    value={formData.required_experience_years || ''}
                    onChange={(e) => {
                      const years = e.target.value ? parseInt(e.target.value) : null;
                      setFormData(prev => ({ ...prev, required_experience_years: years }));
                    }}
                  />
                </FormGroup>

                <FormGroup>
                  <Label>포트폴리오 요구사항</Label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        checked={formData.require_portfolio_pdf}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          require_portfolio_pdf: e.target.checked 
                        }))}
                      />
                      포트폴리오 PDF 제출 필수
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        checked={formData.require_github_url}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          require_github_url: e.target.checked 
                        }))}
                      />
                      GitHub URL 제출 필수
                    </label>
                  </div>
                </FormGroup>

                <FormGroup>
                  <Label>자기소개서 추가 요구사항</Label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        checked={formData.require_growth_background}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          require_growth_background: e.target.checked 
                        }))}
                      />
                      성장 배경 작성 필수
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        checked={formData.require_motivation}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          require_motivation: e.target.checked 
                        }))}
                      />
                      지원 동기 작성 필수
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        checked={formData.require_career_history}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          require_career_history: e.target.checked 
                        }))}
                      />
                      경력 사항 작성 필수
                    </label>
                  </div>
                </FormGroup>

                <FormGroup>
                  <Label>파일 업로드 설정</Label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div>
                      <label>최대 파일 크기 (MB):</label>
                      <Input
                        type="number"
                        value={formData.max_file_size_mb}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          max_file_size_mb: parseInt(e.target.value) || 50 
                        }))}
                        style={{ width: '100px', marginLeft: '8px' }}
                      />
                    </div>
                    <div>
                      <label>허용 파일 형식:</label>
                      <Input
                        type="text"
                        value={formData.allowed_file_types.join(', ')}
                        onChange={(e) => {
                          const types = e.target.value.split(',').map(type => type.trim()).filter(type => type);
                          setFormData(prev => ({ ...prev, allowed_file_types: types }));
                        }}
                        placeholder="pdf, doc, docx"
                        style={{ marginLeft: '8px' }}
                      />
                    </div>
                  </div>
                </FormGroup>
              </FormGrid>
            </div>

            <ButtonGroup>
              <Button type="button" className="secondary" onClick={() => setShowForm(false)}>
                취소
              </Button>
              <Button type="submit" className="primary">
                공고 등록
              </Button>
            </ButtonGroup>
          </form>
        </FormContainer>
      )}

      <JobListContainer>
        <h2 style={{ marginBottom: '24px', color: 'var(--text-primary)' }}>
          등록된 채용공고 ({jobPostings.length})
        </h2>

        {loading && (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
            채용공고 목록을 불러오는 중...
          </div>
        )}

        {error && (
          <div style={{ 
            textAlign: 'center', 
            padding: '20px', 
            color: '#dc3545', 
            backgroundColor: '#f8d7da',
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            {error}
          </div>
        )}

        {!loading && !error && jobPostings.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
            등록된 채용공고가 없습니다. 새로운 채용공고를 등록해보세요.
          </div>
        )}

        {!loading && !error && jobPostings.map((job) => (
          <JobCard
            key={job.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <JobHeader>
              <JobTitle>{job.title}</JobTitle>
              <JobStatus className={job.status}>
                {getStatusText(job.status)}
              </JobStatus>
            </JobHeader>

            <JobDetails>
              <JobDetail>
                <FiBriefcase size={16} />
                {job.company}
              </JobDetail>
              <JobDetail>
                <FiMapPin size={16} />
                {job.location}
              </JobDetail>
              <JobDetail>
                <FiDollarSign size={16} />
                {job.salary ? 
                  (() => {
                    // 천 단위 구분자 제거 후 숫자 추출
                    const cleanSalary = job.salary.replace(/[,\s]/g, '');
                    const numbers = cleanSalary.match(/\d+/g);
                    if (numbers && numbers.length > 0) {
                      if (numbers.length === 1) {
                        const num = parseInt(numbers[0]);
                        if (num >= 1000) {
                          return `${Math.floor(num/1000)}천${num%1000 > 0 ? num%1000 : ''}만원`;
                        }
                        return `${num}만원`;
                      } else {
                        const num1 = parseInt(numbers[0]);
                        const num2 = parseInt(numbers[1]);
                        const formatNum = (num) => {
                          if (num >= 1000) {
                            return `${Math.floor(num/1000)}천${num%1000 > 0 ? num%1000 : ''}만원`;
                          }
                          return `${num}만원`;
                        };
                        return `${formatNum(num1)}~${formatNum(num2)}`;
                      }
                    }
                    return job.salary;
                  })() : 
                  '협의'
                }
              </JobDetail>
              <JobDetail>
                <FiUsers size={16} />
                {job.experience}
              </JobDetail>
              <JobDetail>
                <FiCalendar size={16} />
                마감일: {job.deadline}
              </JobDetail>
              <JobDetail>
                <FiClock size={16} />
                지원자: {job.applicants}명
              </JobDetail>
            </JobDetails>

            <JobActions>
              <ActionButton className="view" onClick={() => handleViewJob(job)}>
                <FiEye size={14} />
                보기
              </ActionButton>
              <ActionButton className="edit" onClick={() => handleEditJob(job)}>
                <FiEdit3 size={14} />
                수정
              </ActionButton>
              <ActionButton 
                className={`publish ${job.status === 'active' ? 'disabled' : ''}`}
                onClick={() => job.status === 'draft' && handlePublish(job.id)}
                disabled={job.status === 'active'}
              >
                <FiGlobe size={14} />
                홈페이지 등록
              </ActionButton>
              <ActionButton className="delete" onClick={() => handleDelete(job.id)}>
                <FiTrash2 size={14} />
                삭제
              </ActionButton>
            </JobActions>
          </JobCard>
        ))}
      </JobListContainer>

      <JobDetailModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        job={selectedJob}
        mode={modalMode}
        onSave={handleSaveJob}
        onDelete={handleDelete}
      />



              <TextBasedRegistration
          isOpen={showTextRegistration}
          onClose={() => setShowTextRegistration(false)}
          onComplete={handleTextRegistrationComplete}
          autoFillData={autoFillData}
        />

              <ImageBasedRegistration
          isOpen={showImageRegistration}
          onClose={() => setShowImageRegistration(false)}
          onComplete={handleImageRegistrationComplete}

        />

      <TemplateModal
        isOpen={showTemplateModal}
        onClose={() => setShowTemplateModal(false)}
        onSaveTemplate={handleSaveTemplate}
        onLoadTemplate={handleLoadTemplate}
        onDeleteTemplate={handleDeleteTemplate}
        templates={templates}
        currentData={null}
      />
    </Container>
  );
};

export default JobPostingRegistration; 