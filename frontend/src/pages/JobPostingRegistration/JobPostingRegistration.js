import React, { useState, useEffect } from 'react';
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
  FiFolder
} from 'react-icons/fi';
import JobDetailModal from './JobDetailModal';
import RegistrationMethodModal from './RegistrationMethodModal';
import TextBasedRegistration from './TextBasedRegistration';
import ImageBasedRegistration from './ImageBasedRegistration';
import TemplateModal from './TemplateModal';
import OrganizationModal from './OrganizationModal';

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
  const [showForm, setShowForm] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [modalMode, setModalMode] = useState('view'); // 'view' or 'edit'
  const [showModal, setShowModal] = useState(false);
  const [showMethodModal, setShowMethodModal] = useState(false);
  const [showTextRegistration, setShowTextRegistration] = useState(false);
  const [showImageRegistration, setShowImageRegistration] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showOrganizationModal, setShowOrganizationModal] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [organizationData, setOrganizationData] = useState({
    structure: '',
    departments: [],
    organizationImage: null
  });
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
    deadline: ''
  });

  // 챗봇 액션 이벤트 리스너
  useEffect(() => {
    const handleRegistrationMethod = () => {
      setShowMethodModal(true);
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

    const handleOrganizationModal = () => {
      setShowOrganizationModal(true);
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
      
      setShowTextRegistration(true);
      console.log('텍스트 기반 등록 모달 열기 완료');
      
      // 2초 후 자동으로 AI 챗봇 시작
      setTimeout(() => {
        console.log('2초 타이머 완료 - startTextBasedAIChatbot 이벤트 발생');
        window.dispatchEvent(new CustomEvent('startTextBasedAIChatbot'));
      }, 2000);
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
    window.addEventListener('openOrganizationModal', handleOrganizationModal);
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
      window.removeEventListener('openOrganizationModal', handleOrganizationModal);
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

  const [jobPostings, setJobPostings] = useState([
    {
      id: 1,
      title: '시니어 프론트엔드 개발자',
      company: '테크스타트업',
      location: '서울 강남구',
      type: 'full-time',
      salary: '4,000만원 ~ 6,000만원',
      experience: '5년 이상',
      education: '대졸 이상',
      status: 'draft',
      deadline: '2024-02-15',
      applicants: 24,
      views: 156,
      bookmarks: 8,
      shares: 3,
      description: 'React, Vue.js, TypeScript를 활용한 웹 애플리케이션 개발을 담당합니다. 사용자 경험을 최우선으로 하는 프론트엔드 개발을 진행하며, 팀과의 협업을 통해 고품질의 제품을 만들어갑니다.',
      requirements: '• React, Vue.js, TypeScript 3년 이상 경험\n• 웹 표준 및 접근성에 대한 이해\n• Git을 활용한 협업 경험\n• 성능 최적화 경험\n• 반응형 웹 개발 경험',
      benefits: '• 유연한 근무 시간\n• 원격 근무 가능\n• 건강보험, 국민연금\n• 점심식대 지원\n• 교육비 지원\n• 경조사 지원'
    },
    {
      id: 2,
      title: '백엔드 개발자 (Java)',
      company: 'IT 서비스 회사',
      location: '서울 마포구',
      type: 'full-time',
      salary: '3,500만원 ~ 5,500만원',
      experience: '3년 이상',
      education: '대졸 이상',
      status: 'draft',
      deadline: '2024-02-20',
      applicants: 0,
      views: 0,
      bookmarks: 0,
      shares: 0,
      description: 'Spring Boot를 활용한 백엔드 시스템 개발을 담당합니다. 대용량 데이터 처리 및 API 설계 경험이 필요하며, 클린 코드 작성과 테스트 코드 작성에 능숙한 분을 찾습니다.',
      requirements: '• Java, Spring Boot 3년 이상 경험\n• RESTful API 설계 경험\n• 데이터베이스 설계 및 최적화 경험\n• JUnit을 활용한 테스트 코드 작성 경험\n• Git을 활용한 협업 경험',
      benefits: '• 정시 퇴근 문화\n• 주 1회 원격 근무\n• 건강보험, 국민연금\n• 점심식대 지원\n• 자기계발비 지원\n• 생일 축하금'
    }
  ]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newJob = {
      id: Date.now(),
      ...formData,
      status: 'draft',
      applicants: 0
    };
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
      deadline: ''
    });
    setShowForm(false);
  };

  const handleDelete = (id) => {
    setJobPostings(prev => prev.filter(job => job.id !== id));
    setShowModal(false);
  };

  const handlePublish = (id) => {
    setJobPostings(prev => 
      prev.map(job => 
        job.id === id ? { ...job, status: 'active' } : job
      )
    );
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

  const handleSaveJob = (updatedJob) => {
    setJobPostings(prev => 
      prev.map(job => 
        job.id === updatedJob.id ? updatedJob : job
      )
    );
    setShowModal(false);
  };

  const handleMethodSelect = (method) => {
    setShowMethodModal(false);
    if (method === 'text') {
      setShowTextRegistration(true);
    } else if (method === 'image') {
      setShowImageRegistration(true);
    }
  };

  const handleTextRegistrationComplete = (data) => {
    const newJob = {
      id: Date.now(),
      title: data.title,
      company: '관리자 소속 회사', // 자동 적용
      location: data.locationCity && data.locationDistrict ? `${data.locationCity} ${data.locationDistrict}` : data.location,
      type: 'full-time',
      salary: data.salary,
      experience: data.experience,
      education: '대졸 이상',
      description: data.description,
      requirements: data.requirements,
      benefits: data.benefits,
      deadline: data.deadline,
      status: 'draft',
      applicants: 0,
      views: 0,
      bookmarks: 0,
      shares: 0
    };
    setJobPostings(prev => [newJob, ...prev]);
    setShowTextRegistration(false);
  };

  const handleImageRegistrationComplete = (data) => {
    const newJob = {
      id: Date.now(),
      title: data.title,
      company: '관리자 소속 회사', // 자동 적용
      location: data.locationCity && data.locationDistrict ? `${data.locationCity} ${data.locationDistrict}` : data.location,
      type: 'full-time',
      salary: data.salary,
      experience: data.experience,
      education: '대졸 이상',
      description: data.mainDuties,
      requirements: data.requirements,
      benefits: data.benefits,
      deadline: data.deadline,
      status: 'draft',
      applicants: 0,
      views: 0,
      bookmarks: 0,
      shares: 0,
      selectedImage: data.selectedImage
    };
    setJobPostings(prev => [newJob, ...prev]);
    setShowImageRegistration(false);
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

  const handleSaveOrganization = (data) => {
    setOrganizationData(data);
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
            onClick={() => setShowMethodModal(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiPlus size={20} />
            새 공고 등록
          </AddButton>
          <AddButton
            onClick={() => setShowOrganizationModal(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{ background: 'linear-gradient(135deg, #ff6b6b, #ee5a24)' }}
          >
            <FiUsers size={20} />
            조직도 설정
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
                <Input
                  type="text"
                  name="salary"
                  value={formData.salary}
                  onChange={handleInputChange}
                  placeholder="예: 4,000만원 ~ 6,000만원"
                />
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

        {jobPostings.map((job) => (
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

      <RegistrationMethodModal
        isOpen={showMethodModal}
        onClose={() => setShowMethodModal(false)}
        onSelectMethod={handleMethodSelect}
      />

              <TextBasedRegistration
          isOpen={showTextRegistration}
          onClose={() => setShowTextRegistration(false)}
          onComplete={handleTextRegistrationComplete}
          organizationData={organizationData}
        />

              <ImageBasedRegistration
          isOpen={showImageRegistration}
          onClose={() => setShowImageRegistration(false)}
          onComplete={handleImageRegistrationComplete}
          organizationData={organizationData}
        />

      <OrganizationModal
        isOpen={showOrganizationModal}
        onClose={() => setShowOrganizationModal(false)}
        organizationData={organizationData}
        onSave={handleSaveOrganization}
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