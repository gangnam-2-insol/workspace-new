import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { FiX, FiUpload, FiFileText, FiGithub, FiUser, FiMail, FiBriefcase, FiAward, FiCode, FiEdit3, FiAlertCircle } from 'react-icons/fi';

const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
`;

const CloseButton = styled.button`
  position: fixed;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  z-index: 3010;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const ModalBody = styled.div`
  padding: 0 24px 24px 24px;
`;

const ResumeFormSection = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h3`
  margin: 0 0 16px 0;
  font-size: 18px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FileUploadArea = styled.div`
  border: 2px dashed ${props => props.isDragOver ? 'var(--primary-color)' : 'var(--border-color)'};
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  transition: all 0.2s;
  background: ${props => props.isDragOver ? 'rgba(0, 200, 81, 0.1)' : 'transparent'};
  cursor: pointer;

  &:hover {
    border-color: var(--primary-color);
    background: var(--background-secondary);
  }
`;

const UploadIcon = styled.div`
  font-size: 48px;
  color: var(--text-secondary);
  margin-bottom: 16px;
`;

const UploadText = styled.p`
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 500;
`;

const UploadSubtext = styled.p`
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
`;

const FileInput = styled.input`
  display: none;
`;

const ResumeFormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const FormLabel = styled.label`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FormInput = styled.input`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const FormSelect = styled.select`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const FormTextarea = styled.textarea`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const ExistingApplicantInfo = styled.div`
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 1px solid #2196f3;
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
`;

const ExistingApplicantTitle = styled.h4`
  margin: 0 0 12px 0;
  color: #1976d2;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ExistingApplicantText = styled.p`
  margin: 0 0 8px 0;
  color: #1976d2;
  font-size: 14px;
`;

const ReplaceCheckbox = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #1976d2;
`;

const ResumeModalFooter = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
`;

const Button = styled.button`
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--border-color);

  &.secondary {
    background: white;
    color: var(--text-primary);

    &:hover {
      background: var(--background-secondary);
    }
  }

  &.primary {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);

    &:hover {
      background: var(--primary-dark);
    }

    &:disabled {
      background: var(--text-light);
      cursor: not-allowed;
    }
  }
`;

const modalVariants = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 }
};

const overlayVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 }
};

const NewApplicantModal = ({
  isOpen,
  onClose,
  onSubmit,
  existingApplicant,
  isCheckingDuplicate,
  onReplaceExisting
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [resumeData, setResumeData] = useState({
    name: '',
    email: '',
    position: '',
    department: '',
    experience: '',
    skills: '',
    githubUrl: ''
  });
  const [resumeFile, setResumeFile] = useState(null);
  const [coverFile, setCoverFile] = useState(null);
  const [replaceExisting, setReplaceExisting] = useState(false);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find(file => file.type === 'application/pdf');
    if (pdfFile) {
      setResumeFile(pdfFile);
    }
  }, []);

  const handleFileChange = useCallback((e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setResumeFile(file);
    }
  }, []);

  const handleCoverFileChange = useCallback((e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setCoverFile(file);
    }
  }, []);

  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    setResumeData(prev => ({
      ...prev,
      [name]: value
    }));
  }, []);

  const handleSubmit = useCallback(() => {
    if (!resumeFile || !resumeData.name || !resumeData.email) {
      alert('필수 항목을 모두 입력해주세요.');
      return;
    }

    const formData = new FormData();
    formData.append('resume', resumeFile);
    if (coverFile) {
      formData.append('coverLetter', coverFile);
    }
    formData.append('data', JSON.stringify(resumeData));
    formData.append('replaceExisting', replaceExisting);

    onSubmit(formData);
  }, [resumeFile, coverFile, resumeData, replaceExisting, onSubmit]);

  const handleClose = useCallback(() => {
    setResumeData({
      name: '',
      email: '',
      position: '',
      department: '',
      experience: '',
      skills: '',
      githubUrl: ''
    });
    setResumeFile(null);
    setCoverFile(null);
    setReplaceExisting(false);
    onClose();
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <ModalOverlay
      variants={overlayVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      onClick={handleClose}
    >
      <ModalContent
        variants={modalVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        onClick={(e) => e.stopPropagation()}
      >
        <ModalHeader>
          <ModalTitle>새 지원자 등록</ModalTitle>
          <CloseButton onClick={handleClose}>
            <FiX />
          </CloseButton>
        </ModalHeader>

        <ModalBody>
          <ResumeFormSection>
            <SectionTitle>
              <FiFileText />
              이력서 파일 업로드
            </SectionTitle>
            <FileUploadArea
              isDragOver={isDragOver}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('resumeFile').click()}
            >
              <UploadIcon>
                <FiUpload />
              </UploadIcon>
              <UploadText>
                {resumeFile ? resumeFile.name : 'PDF 파일을 드래그하거나 클릭하여 선택하세요'}
              </UploadText>
              <UploadSubtext>PDF 형식만 지원됩니다</UploadSubtext>
            </FileUploadArea>
            <FileInput
              id="resumeFile"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
            />
          </ResumeFormSection>

          <ResumeFormSection>
            <SectionTitle>
              <FiEdit3 />
              자기소개서 파일 업로드 (선택사항)
            </SectionTitle>
            <FileUploadArea
              onClick={() => document.getElementById('coverFile').click()}
            >
              <UploadIcon>
                <FiUpload />
              </UploadIcon>
              <UploadText>
                {coverFile ? coverFile.name : 'PDF 파일을 클릭하여 선택하세요'}
              </UploadText>
              <UploadSubtext>PDF 형식만 지원됩니다</UploadSubtext>
            </FileUploadArea>
            <FileInput
              id="coverFile"
              type="file"
              accept=".pdf"
              onChange={handleCoverFileChange}
            />
          </ResumeFormSection>

          <ResumeFormSection>
            <SectionTitle>
              <FiGithub />
              GitHub URL (선택사항)
            </SectionTitle>
            <FormInput
              type="url"
              name="githubUrl"
              placeholder="https://github.com/username"
              value={resumeData.githubUrl}
              onChange={handleInputChange}
            />
          </ResumeFormSection>

          <ResumeFormSection>
            <SectionTitle>
              <FiUser />
              지원자 정보
            </SectionTitle>
            <ResumeFormGrid>
              <FormGroup>
                <FormLabel>
                  <FiUser />
                  이름 *
                </FormLabel>
                <FormInput
                  type="text"
                  name="name"
                  placeholder="지원자 이름"
                  value={resumeData.name}
                  onChange={handleInputChange}
                  required
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>
                  <FiMail />
                  이메일 *
                </FormLabel>
                <FormInput
                  type="email"
                  name="email"
                  placeholder="email@example.com"
                  value={resumeData.email}
                  onChange={handleInputChange}
                  required
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>
                  <FiBriefcase />
                  직무
                </FormLabel>
                <FormInput
                  type="text"
                  name="position"
                  placeholder="지원 직무"
                  value={resumeData.position}
                  onChange={handleInputChange}
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>
                  <FiBriefcase />
                  부서
                </FormLabel>
                <FormInput
                  type="text"
                  name="department"
                  placeholder="지원 부서"
                  value={resumeData.department}
                  onChange={handleInputChange}
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>
                  <FiAward />
                  경력
                </FormLabel>
                <FormSelect
                  name="experience"
                  value={resumeData.experience}
                  onChange={handleInputChange}
                >
                  <option value="">경력 선택</option>
                  <option value="신입">신입</option>
                  <option value="1-3년">1-3년</option>
                  <option value="3-5년">3-5년</option>
                  <option value="5-10년">5-10년</option>
                  <option value="10년 이상">10년 이상</option>
                </FormSelect>
              </FormGroup>

              <FormGroup>
                <FormLabel>
                  <FiCode />
                  기술스택
                </FormLabel>
                <FormTextarea
                  name="skills"
                  placeholder="사용 가능한 기술들을 쉼표로 구분하여 입력하세요"
                  value={resumeData.skills}
                  onChange={handleInputChange}
                />
              </FormGroup>
            </ResumeFormGrid>
          </ResumeFormSection>

          {existingApplicant && (
            <ExistingApplicantInfo>
              <ExistingApplicantTitle>
                <FiAlertCircle />
                기존 지원자 발견
              </ExistingApplicantTitle>
              <ExistingApplicantText>
                {existingApplicant.name} ({existingApplicant.email}) 님이 이미 등록되어 있습니다.
              </ExistingApplicantText>
              <ReplaceCheckbox>
                <input
                  type="checkbox"
                  checked={replaceExisting}
                  onChange={(e) => setReplaceExisting(e.target.checked)}
                />
                기존 정보를 새 정보로 교체
              </ReplaceCheckbox>
            </ExistingApplicantInfo>
          )}

          <ResumeModalFooter>
            <Button className="secondary" onClick={handleClose}>
              취소
            </Button>
            <Button
              className="primary"
              onClick={handleSubmit}
              disabled={!resumeFile || !resumeData.name || !resumeData.email || isCheckingDuplicate}
            >
              {isCheckingDuplicate ? '중복 확인 중...' : '등록하기'}
            </Button>
          </ResumeModalFooter>
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};

export default NewApplicantModal;
