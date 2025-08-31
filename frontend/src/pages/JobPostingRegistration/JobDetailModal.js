import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiX,
  FiEdit3,
  FiSave,
  FiEye,
  FiCalendar,
  FiMapPin,
  FiDollarSign,
  FiUsers,
  FiBriefcase,
  FiClock,
  FiUser,
  FiBookOpen,
  FiAward,
  FiHeart
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

const Content = styled.div`
  padding: 32px;
`;

const StatusBadge = styled.span`
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  margin-left: 16px;

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

const JobHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
`;

const JobTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
`;

const JobMeta = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
  padding: 24px;
  background: var(--background-secondary);
  border-radius: 12px;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 14px;
`;

const MetaLabel = styled.span`
  font-weight: 600;
  color: var(--text-primary);
`;

const Section = styled.div`
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

const SectionContent = styled.div`
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  line-height: 1.6;
  color: var(--text-secondary);
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

  &:disabled {
    background: var(--background-secondary);
    cursor: not-allowed;
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

  &:disabled {
    background: var(--background-secondary);
    cursor: not-allowed;
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

  &:disabled {
    background: var(--background-secondary);
    cursor: not-allowed;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
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

  &.danger {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
    border: 2px solid rgba(220, 53, 69, 0.2);

    &:hover {
      background: rgba(220, 53, 69, 0.2);
    }
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

const StatCard = styled.div`
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 4px;
`;

const StatLabel = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-weight: 600;
`;

const JobDetailModal = ({
  isOpen,
  onClose,
  job,
  mode = 'view', // 'view' or 'edit'
  onSave,
  onDelete
}) => {
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
    status: 'draft',
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

  const [isEditing, setIsEditing] = useState(mode === 'edit');

  useEffect(() => {
    if (job) {
      setFormData({
        title: job.title || '',
        company: job.company || '',
        location: job.location || '',
        type: job.type || 'full-time',
        salary: job.salary || '',
        experience: job.experience || '',
        education: job.education || '',
        description: job.description || '',
        requirements: job.requirements || '',
        benefits: job.benefits || '',
        deadline: job.deadline || '',
        status: job.status || 'draft',
        // 지원자 요구 항목
        required_documents: job.required_documents || ['resume'],
        required_skills: job.required_skills || [],
        required_experience_years: job.required_experience_years || null,
        require_portfolio_pdf: job.require_portfolio_pdf || false,
        require_github_url: job.require_github_url || false,
        require_growth_background: job.require_growth_background || false,
        require_motivation: job.require_motivation || false,
        require_career_history: job.require_career_history || false,
        max_file_size_mb: job.max_file_size_mb || 50,
        allowed_file_types: job.allowed_file_types || ['pdf', 'doc', 'docx']
      });
    }
  }, [job]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = () => {
    if (onSave) {
      onSave({ ...job, ...formData });
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    if (job) {
      setFormData({
        title: job.title || '',
        company: job.company || '',
        location: job.location || '',
        type: job.type || 'full-time',
        salary: job.salary || '',
        experience: job.experience || '',
        education: job.education || '',
        description: job.description || '',
        requirements: job.requirements || '',
        benefits: job.benefits || '',
        deadline: job.deadline || '',
        status: job.status || 'draft',
        // 지원자 요구 항목
        required_documents: job.required_documents || ['resume'],
        required_skills: job.required_skills || [],
        required_experience_years: job.required_experience_years || null,
        require_portfolio_pdf: job.require_portfolio_pdf || false,
        require_github_url: job.require_github_url || false,
        require_growth_background: job.require_growth_background || false,
        require_motivation: job.require_motivation || false,
        require_career_history: job.require_career_history || false,
        max_file_size_mb: job.max_file_size_mb || 50,
        allowed_file_types: job.allowed_file_types || ['pdf', 'doc', 'docx']
      });
    }
    setIsEditing(false);
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return '모집중';
      case 'draft': return '임시저장';
      case 'closed': return '마감';
      default: return status;
    }
  };

  const getTypeText = (type) => {
    switch (type) {
      case 'full-time': return '정규직';
      case 'part-time': return '파트타임';
      case 'contract': return '계약직';
      case 'intern': return '인턴';
      default: return type;
    }
  };

  if (!job) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <Overlay
          key="jobdetail-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <Modal
            key="jobdetail-modal"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <Header>
              <Title>
                {isEditing ? '채용공고 수정' : '채용공고 상세'}
                <StatusBadge className={formData.status}>
                  {getStatusText(formData.status)}
                </StatusBadge>
              </Title>
              <CloseButton onClick={onClose}>
                <FiX />
              </CloseButton>
            </Header>

            <Content>
              {!isEditing ? (
                // View Mode
                <>
                  <JobHeader>
                    <JobTitle>{job.title}</JobTitle>
                  </JobHeader>

                  <JobMeta>
                    <MetaItem>
                      <FiBriefcase size={16} />
                      <MetaLabel>회사:</MetaLabel> {job.company}
                    </MetaItem>
                    <MetaItem>
                      <FiMapPin size={16} />
                      <MetaLabel>근무지:</MetaLabel> {job.location}
                    </MetaItem>
                    <MetaItem>
                      <FiDollarSign size={16} />
                      <MetaLabel>연봉:</MetaLabel>
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
                    </MetaItem>
                    <MetaItem>
                      <FiUsers size={16} />
                      <MetaLabel>경력:</MetaLabel> {job.experience}
                    </MetaItem>
                    <MetaItem>
                      <FiCalendar size={16} />
                      <MetaLabel>마감일:</MetaLabel> {job.deadline}
                    </MetaItem>
                    <MetaItem>
                      <FiClock size={16} />
                      <MetaLabel>지원자:</MetaLabel> {job.applicants || 0}명
                    </MetaItem>
                  </JobMeta>

                  <StatsGrid>
                    <StatCard>
                      <StatValue>{job.applicants || 0}</StatValue>
                      <StatLabel>지원자</StatLabel>
                    </StatCard>
                    <StatCard>
                      <StatValue>{job.views || 0}</StatValue>
                      <StatLabel>조회수</StatLabel>
                    </StatCard>
                    <StatCard>
                      <StatValue>{job.bookmarks || 0}</StatValue>
                      <StatLabel>북마크</StatLabel>
                    </StatCard>
                    <StatCard>
                      <StatValue>{job.shares || 0}</StatValue>
                      <StatLabel>공유</StatLabel>
                    </StatCard>
                  </StatsGrid>

                  <Section>
                    <SectionTitle>
                      <FiBookOpen size={18} />
                      업무 내용
                    </SectionTitle>
                    <SectionContent>
                      {job.description || '업무 내용이 없습니다.'}
                    </SectionContent>
                  </Section>

                  <Section>
                    <SectionTitle>
                      <FiAward size={18} />
                      자격 요건
                    </SectionTitle>
                    <SectionContent>
                      {job.requirements || '자격 요건이 없습니다.'}
                    </SectionContent>
                  </Section>

                  <Section>
                    <SectionTitle>
                      <FiHeart size={18} />
                      복리후생
                    </SectionTitle>
                    <SectionContent>
                      {job.benefits || '복리후생 정보가 없습니다.'}
                    </SectionContent>
                  </Section>

                  {/* 지원자 요구 항목 섹션 */}
                  <Section>
                    <SectionTitle>
                      📋 지원자 요구 항목
                    </SectionTitle>
                    <SectionContent>
                      <div style={{ display: 'grid', gap: '16px' }}>
                        <div>
                          <strong>필수 제출 서류:</strong>
                          <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {job.required_documents && job.required_documents.length > 0 ? (
                              job.required_documents.map((doc, index) => (
                                <span key={index} style={{
                                  background: '#e3f2fd',
                                  color: '#1976d2',
                                  padding: '4px 8px',
                                  borderRadius: '4px',
                                  fontSize: '12px',
                                  fontWeight: '500'
                                }}>
                                  {doc === 'resume' ? '이력서' :
                                   doc === 'cover_letter' ? '자기소개서' :
                                   doc === 'portfolio' ? '포트폴리오' : doc}
                                </span>
                              ))
                            ) : (
                              <span style={{ color: '#666' }}>이력서</span>
                            )}
                          </div>
                        </div>

                        {job.required_skills && job.required_skills.length > 0 && (
                          <div>
                            <strong>필수 기술 스택:</strong>
                            <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                              {job.required_skills.map((skill, index) => (
                                <span key={index} style={{
                                  background: '#f3e5f5',
                                  color: '#7b1fa2',
                                  padding: '4px 8px',
                                  borderRadius: '4px',
                                  fontSize: '12px',
                                  fontWeight: '500'
                                }}>
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {job.required_experience_years && (
                          <div>
                            <strong>필수 경력 연차:</strong> {job.required_experience_years}년
                          </div>
                        )}

                        {(job.require_portfolio_pdf || job.require_github_url) && (
                          <div>
                            <strong>포트폴리오 요구사항:</strong>
                            <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                              {job.require_portfolio_pdf && (
                                <span style={{ color: '#2e7d32' }}>✓ 포트폴리오 PDF 제출 필수</span>
                              )}
                              {job.require_github_url && (
                                <span style={{ color: '#2e7d32' }}>✓ GitHub URL 제출 필수</span>
                              )}
                            </div>
                          </div>
                        )}

                        {(job.require_growth_background || job.require_motivation || job.require_career_history) && (
                          <div>
                            <strong>자기소개서 추가 요구사항:</strong>
                            <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                              {job.require_growth_background && (
                                <span style={{ color: '#2e7d32' }}>✓ 성장 배경 작성 필수</span>
                              )}
                              {job.require_motivation && (
                                <span style={{ color: '#2e7d32' }}>✓ 지원 동기 작성 필수</span>
                              )}
                              {job.require_career_history && (
                                <span style={{ color: '#2e7d32' }}>✓ 경력 사항 작성 필수</span>
                              )}
                            </div>
                          </div>
                        )}

                        <div>
                          <strong>파일 업로드 설정:</strong>
                          <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            <span>최대 파일 크기: {job.max_file_size_mb || 50}MB</span>
                            <span>허용 파일 형식: {job.allowed_file_types ? job.allowed_file_types.join(', ') : 'pdf, doc, docx'}</span>
                          </div>
                        </div>
                      </div>
                    </SectionContent>
                  </Section>
                </>
              ) : (
                // Edit Mode
                <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
                  <FormGrid>
                    <FormGroup>
                      <Label>공고 제목 *</Label>
                      <Input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleInputChange}
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
                      />
                    </FormGroup>

                    <FormGroup>
                      <Label>경력 요구사항</Label>
                      <Input
                        type="text"
                        name="experience"
                        value={formData.experience}
                        onChange={handleInputChange}
                      />
                    </FormGroup>

                    <FormGroup>
                      <Label>학력 요구사항</Label>
                      <Input
                        type="text"
                        name="education"
                        value={formData.education}
                        onChange={handleInputChange}
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

                    <FormGroup>
                      <Label>상태</Label>
                      <Select
                        name="status"
                        value={formData.status}
                        onChange={handleInputChange}
                      >
                        <option value="draft">임시저장</option>
                        <option value="active">모집중</option>
                        <option value="closed">마감</option>
                      </Select>
                    </FormGroup>
                  </FormGrid>

                  <FormGroup>
                    <Label>업무 내용 *</Label>
                    <TextArea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      required
                    />
                  </FormGroup>

                  <FormGroup>
                    <Label>자격 요건</Label>
                    <TextArea
                      name="requirements"
                      value={formData.requirements}
                      onChange={handleInputChange}
                    />
                  </FormGroup>

                  <FormGroup>
                    <Label>복리후생</Label>
                    <TextArea
                      name="benefits"
                      value={formData.benefits}
                      onChange={handleInputChange}
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
                </form>
              )}

              <ButtonGroup>
                {!isEditing ? (
                  <>
                    <Button
                      className="secondary"
                      onClick={() => setIsEditing(true)}
                    >
                      <FiEdit3 size={16} />
                      수정
                    </Button>
                    <Button
                      className="danger"
                      onClick={() => onDelete && onDelete(job.id)}
                    >
                      삭제
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      className="secondary"
                      onClick={handleCancel}
                    >
                      취소
                    </Button>
                    <Button
                      className="primary"
                      onClick={handleSave}
                    >
                      <FiSave size={16} />
                      저장
                    </Button>
                  </>
                )}
              </ButtonGroup>
            </Content>
          </Modal>
        </Overlay>
      )}
    </AnimatePresence>
  );
};

export default JobDetailModal;
