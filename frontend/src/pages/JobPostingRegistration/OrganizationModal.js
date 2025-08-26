import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiX, 
  FiUsers,
  FiSave,
  FiCheck,
  FiPlus,
  FiTrash2,
  FiUpload,
  FiImage
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
  max-width: 600px;
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

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

const FileUploadArea = styled.div`
  width: 100%;
  min-height: 200px;
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: var(--background-tertiary);
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    border-color: var(--primary-color);
    background: rgba(0, 123, 255, 0.05);
  }

  &.has-file {
    border-color: var(--success-color);
    background: rgba(40, 167, 69, 0.05);
  }
`;

const UploadIcon = styled.div`
  font-size: 48px;
  color: var(--text-secondary);
  margin-bottom: 16px;
`;

const UploadText = styled.div`
  text-align: center;
  color: var(--text-secondary);
`;

const UploadTitle = styled.div`
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
`;

const UploadDescription = styled.div`
  font-size: 14px;
  margin-bottom: 16px;
`;

const FileInput = styled.input`
  display: none;
`;

const FilePreview = styled.div`
  width: 100%;
  max-width: 400px;
  margin-top: 16px;
`;

const PreviewImage = styled.img`
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
`;

const FileInfo = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--background-secondary);
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 12px;
`;

const FileName = styled.div`
  font-weight: 500;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FileSize = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(220, 53, 69, 0.1);
  }
`;

const AnalyzingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: white;
  z-index: 10;
`;

const Spinner = styled.div`
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const AnalyzingText = styled.div`
  font-size: 16px;
  font-weight: 500;
  text-align: center;
`;

const AnalyzingDescription = styled.div`
  font-size: 14px;
  opacity: 0.8;
  margin-top: 8px;
  text-align: center;
`;

const DepartmentList = styled.div`
  margin-top: 16px;
`;

const DepartmentItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--background-secondary);
  border-radius: 8px;
  margin-bottom: 8px;
`;

const DepartmentInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const DepartmentName = styled.span`
  font-weight: 500;
  color: var(--text-primary);
`;

const DepartmentCount = styled.span`
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
`;

const DeleteButton = styled.button`
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(220, 53, 69, 0.1);
  }
`;

const AddDepartmentForm = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
  margin-top: 16px;
  padding: 16px;
  background: var(--background-tertiary);
  border-radius: 8px;
`;

const Input = styled.input`
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const NumberInput = styled.input`
  width: 80px;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  text-align: center;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const AddButton = styled.button`
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;

  &:hover {
    background: var(--primary-dark);
  }

  &:disabled {
    background: var(--border-color);
    cursor: not-allowed;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
`;

const Button = styled.button`
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;

  &.secondary {
    background: var(--background-secondary);
    color: var(--text-primary);

    &:hover {
      background: var(--border-color);
    }
  }

  &.primary {
    background: var(--primary-color);
    color: white;

    &:hover {
      background: var(--primary-dark);
    }
  }
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

const OrganizationModal = ({ 
  isOpen, 
  onClose, 
  organizationData, 
  onSave 
}) => {
  const [formData, setFormData] = useState({
    structure: organizationData.structure || '',
    departments: organizationData.departments || [],
    organizationImage: organizationData.organizationImage || null
  });

  const [newDepartment, setNewDepartment] = useState({
    name: '',
    count: 1
  });

  const [uploadedFile, setUploadedFile] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddDepartment = () => {
    if (newDepartment.name.trim()) {
      setFormData(prev => ({
        ...prev,
        departments: [...prev.departments, { ...newDepartment }]
      }));
      setNewDepartment({ name: '', count: 1 });
    }
  };

  const handleDeleteDepartment = (index) => {
    setFormData(prev => ({
      ...prev,
      departments: prev.departments.filter((_, i) => i !== index)
    }));
  };

  const handleSave = () => {
    onSave(formData);
    onClose();
  };

  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzeOrganizationImage = async (imageData) => {
    setIsAnalyzing(true);
    
    try {
      // AI 분석 시뮬레이션 (실제로는 API 호출)
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // 다양한 조직도 패턴에 따른 시뮬레이션된 AI 분석 결과
      const possibleResults = [
        {
          departments: [
            { name: '영업', count: 3 },
            { name: '마케팅', count: 2 },
            { name: '기획', count: 3 },
            { name: '디자인', count: 8 },
            { name: '개발', count: 3 },
            { name: '인사', count: 2 },
            { name: '재무', count: 1 }
          ],
          structure: '대표 - 부장 - 영업(3), 마케팅(2), 기획(3), 디자인(8), 개발(3), 인사(2), 재무(1)'
        },
        {
          departments: [
            { name: '개발', count: 5 },
            { name: '디자인', count: 3 },
            { name: '기획', count: 2 },
            { name: '마케팅', count: 2 },
            { name: '영업', count: 2 },
            { name: '인사', count: 1 },
            { name: '재무', count: 1 }
          ],
          structure: '대표 - 개발(5), 디자인(3), 기획(2), 마케팅(2), 영업(2), 인사(1), 재무(1)'
        },
        {
          departments: [
            { name: '영업', count: 4 },
            { name: '마케팅', count: 3 },
            { name: '개발', count: 6 },
            { name: '디자인', count: 4 },
            { name: '기획', count: 2 },
            { name: '인사', count: 2 },
            { name: '재무', count: 1 },
            { name: '고객지원', count: 3 }
          ],
          structure: '대표 - 영업(4), 마케팅(3), 개발(6), 디자인(4), 기획(2), 인사(2), 재무(1), 고객지원(3)'
        }
      ];
      
      // 랜덤하게 결과 선택 (실제로는 AI 분석 결과)
      const mockAnalysisResult = possibleResults[Math.floor(Math.random() * possibleResults.length)];
      
      // 분석 결과를 부서 목록에 자동 추가
      setFormData(prev => ({
        ...prev,
        departments: mockAnalysisResult.departments,
        structure: mockAnalysisResult.structure
      }));
      
      // 성공 메시지
      alert(`AI 분석이 완료되었습니다!\n\n추출된 부서: ${mockAnalysisResult.departments.length}개\n총 인원: ${mockAnalysisResult.departments.reduce((sum, dept) => sum + dept.count, 0)}명\n\n부서 정보가 자동으로 추가되었습니다.`);
      
    } catch (error) {
      alert('AI 분석 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // 파일 크기 체크 (5MB 이하)
      if (file.size > 5 * 1024 * 1024) {
        alert('파일 크기는 5MB 이하여야 합니다.');
        return;
      }

      // 이미지 파일 체크
      if (!file.type.startsWith('image/')) {
        alert('이미지 파일만 업로드 가능합니다.');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const imageData = e.target.result;
        setUploadedFile({
          file: file,
          preview: imageData,
          name: file.name,
          size: file.size
        });
        setFormData(prev => ({
          ...prev,
          organizationImage: imageData
        }));
        
        // 이미지 업로드 후 자동으로 AI 분석 시작
        analyzeOrganizationImage(imageData);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setFormData(prev => ({
      ...prev,
      organizationImage: null
    }));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <Overlay
          key="organization-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <Modal
            key="organization-modal"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.3 }}
          >
            <Header>
              <Title>회사 조직도 설정</Title>
              <CloseButton onClick={onClose}>
                <FiX />
              </CloseButton>
            </Header>

            <Content>
              <Section>
                <SectionTitle>
                  <FiImage size={18} />
                  조직도 이미지 업로드
                </SectionTitle>
                <FormGroup>
                  <Label>조직도 이미지</Label>
                  <div style={{ position: 'relative' }}>
                    <FileUploadArea 
                      className={uploadedFile ? 'has-file' : ''}
                      onClick={() => !isAnalyzing && document.getElementById('organization-image').click()}
                      style={{ pointerEvents: isAnalyzing ? 'none' : 'auto' }}
                    >
                      {uploadedFile ? (
                        <>
                          <UploadIcon>
                            <FiImage size={48} />
                          </UploadIcon>
                          <UploadText>
                            <UploadTitle>이미지 업로드 완료</UploadTitle>
                            <UploadDescription>클릭하여 다른 이미지로 변경</UploadDescription>
                          </UploadText>
                          <FilePreview>
                            <PreviewImage src={uploadedFile.preview} alt="조직도" />
                            <FileInfo>
                              <FileName>
                                <FiImage size={16} />
                                {uploadedFile.name}
                              </FileName>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <FileSize>{formatFileSize(uploadedFile.size)}</FileSize>
                                <RemoveButton onClick={handleRemoveFile}>
                                  <FiTrash2 size={14} />
                                </RemoveButton>
                              </div>
                            </FileInfo>
                          </FilePreview>
                        </>
                      ) : (
                        <>
                          <UploadIcon>
                            <FiUpload size={48} />
                          </UploadIcon>
                          <UploadText>
                            <UploadTitle>이미지를 업로드하세요</UploadTitle>
                            <UploadDescription>
                              PNG, JPG, JPEG 파일 (최대 5MB)
                            </UploadDescription>
                          </UploadText>
                        </>
                      )}
                      
                      {isAnalyzing && (
                        <AnalyzingOverlay>
                          <Spinner />
                          <AnalyzingText>AI 분석 중...</AnalyzingText>
                          <AnalyzingDescription>
                            조직도 이미지를 분석하여 부서 정보를 추출하고 있습니다
                          </AnalyzingDescription>
                        </AnalyzingOverlay>
                      )}
                    </FileUploadArea>
                  </div>
                  <FileInput
                    id="organization-image"
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                  />
                </FormGroup>
                <AISuggestion>
                  <AISuggestionTitle>
                    <FiCheck size={16} />
                    AI 추천
                  </AISuggestionTitle>
                  <AISuggestionText>
                    조직도 이미지를 업로드하면 AI가 적합한 구인 부서를 추천해드립니다.
                  </AISuggestionText>
                </AISuggestion>
              </Section>

              <Section>
                <SectionTitle>
                  <FiUsers size={18} />
                  부서 목록
                </SectionTitle>
                <DepartmentList>
                  {formData.departments.map((dept, index) => (
                    <DepartmentItem key={index}>
                      <DepartmentInfo>
                        <DepartmentName>{dept.name}</DepartmentName>
                        <DepartmentCount>{dept.count}명</DepartmentCount>
                      </DepartmentInfo>
                      <DeleteButton onClick={() => handleDeleteDepartment(index)}>
                        <FiTrash2 size={14} />
                      </DeleteButton>
                    </DepartmentItem>
                  ))}
                </DepartmentList>

                <AddDepartmentForm>
                  <div>
                    <Label>부서명</Label>
                    <Input
                      type="text"
                      value={newDepartment.name}
                      onChange={(e) => setNewDepartment(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="부서명"
                    />
                  </div>
                  <div>
                    <Label>인원수</Label>
                    <NumberInput
                      type="number"
                      min="1"
                      value={newDepartment.count}
                      onChange={(e) => setNewDepartment(prev => ({ ...prev, count: parseInt(e.target.value) || 1 }))}
                    />
                  </div>
                  <AddButton onClick={handleAddDepartment} disabled={!newDepartment.name.trim()}>
                    <FiPlus size={14} />
                    추가
                  </AddButton>
                </AddDepartmentForm>
              </Section>

              <ButtonGroup>
                <Button className="secondary" onClick={onClose}>
                  취소
                </Button>
                <Button className="primary" onClick={handleSave}>
                  <FiSave size={16} />
                  저장
                </Button>
              </ButtonGroup>
            </Content>
          </Modal>
        </Overlay>
      )}
    </AnimatePresence>
  );
};

export default OrganizationModal; 