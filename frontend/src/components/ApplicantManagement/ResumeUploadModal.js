import React from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FiFile, FiFileText } from 'react-icons/fi';

// 새 이력서 등록 모달 스타일 컴포넌트들
const ResumeModalOverlay = styled(motion.div).attrs({
  id: 'applicant-management-resume-modal-overlay'
})`
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

const ResumeModalContent = styled(motion.div)`
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
`;

const ResumeModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid var(--border-color);
`;

const ResumeModalTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const ResumeModalCloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const ResumeModalBody = styled.div`
  padding: 24px;
`;

const ResumeFormSection = styled.div`
  margin-bottom: 24px;
`;

const ResumeFormTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
`;

const ResumeFormDescription = styled.p`
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.5;
`;

const FileUploadArea = styled.div`
  border: 2px dashed ${props => props.isDragOver ? 'var(--primary-color)' : 'var(--border-color)'};
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  transition: all 0.2s;
  background: ${props => props.isDragOver ? 'rgba(0, 200, 81, 0.1)' : 'transparent'};

  &:hover {
    border-color: var(--primary-color);
    background: var(--background-secondary);
  }
`;

const FileUploadInput = styled.input`
  display: none;
`;

const FileUploadLabel = styled.label`
  cursor: pointer;
  display: block;
`;

const FileUploadPlaceholder = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);

  span {
    font-size: 16px;
    font-weight: 500;
  }

  small {
    font-size: 12px;
    color: var(--text-light);
  }
`;

const FileSelected = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-weight: 500;
`;

const ExistingApplicantInfo = styled.div`
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 1px solid #2196f3;
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
`;

const ExistingApplicantTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: #1976d2;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ExistingApplicantDetails = styled.div`
  font-size: 14px;
  color: #333;
  line-height: 1.6;

  ul {
    margin: 8px 0;
    padding-left: 20px;
  }

  li {
    margin: 4px 0;
  }
`;

const ReplaceOptionSection = styled.div`
  margin-top: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  border: 1px solid #e0e0e0;
`;

const ReplaceOptionLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1976d2;
  cursor: pointer;

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #1976d2;
  }

  span {
    font-size: 15px;
  }
`;

const ReplaceOptionDescription = styled.div`
  margin-top: 8px;
  font-size: 13px;
  color: #666;
  line-height: 1.4;
`;

const ResumeFormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
`;

const ResumeFormField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const ResumeFormLabel = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
`;

const ResumeFormInput = styled.input`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;

  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &::placeholder {
    color: var(--text-light);
  }
`;

// 문서 업로드 관련 스타일 컴포넌트들
const DocumentUploadContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const DocumentTypeSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const DocumentTypeLabel = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
`;

const DocumentTypeSelect = styled.select`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  background: white;
  cursor: pointer;
  transition: all 0.2s;

  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  option {
    padding: 8px;
  }
`;

const ResumeModalFooter = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid var(--border-color);
`;

const ResumeModalButton = styled.button`
  padding: 12px 24px;
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--background-secondary);
    border-color: var(--text-secondary);
  }
`;

const ResumeModalSubmitButton = styled.button`
  padding: 12px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--primary-dark);
  }

  &:disabled {
    background: var(--text-light);
    cursor: not-allowed;
  }
`;

// 분석 결과 스타일 컴포넌트들
const ResumeAnalysisSection = styled.div`
  margin-top: 24px;
  padding: 20px;
  background: var(--background-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
`;

const ResumeAnalysisTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
`;

const ResumeAnalysisSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;

  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  span {
    color: var(--text-secondary);
    font-size: 14px;
  }
`;

const ResumeAnalysisContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ResumeAnalysisItem = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
`;

const ResumeAnalysisLabel = styled.span`
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  min-width: 80px;
`;

const ResumeAnalysisValue = styled.span`
  font-size: 14px;
  color: var(--text-secondary);
  flex: 1;
`;

const ResumeAnalysisScore = styled.span`
  font-size: 16px;
  font-weight: 600;
  color: ${props => {
    if (props.score >= 90) return '#28a745';
    if (props.score >= 80) return '#ffc107';
    return '#dc3545';
  }};
`;

const AnalysisScoreDisplay = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
`;

const AnalysisScoreCircle = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
`;

const AnalysisScoreInfo = styled.div`
  flex: 1;
`;

const AnalysisScoreTitle = styled.div`
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
`;

const AnalysisScoreValue = styled.div`
  font-size: 20px;
  font-weight: bold;
`;

const ResumeFormActions = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 24px;
`;

const ResumeSubmitButton = styled.button`
  padding: 14px 32px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--primary-dark);
  }

  &:disabled {
    background: var(--text-light);
    cursor: not-allowed;
  }
`;

const GithubInputContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const GithubInput = styled.input`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;

  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &::placeholder {
    color: var(--text-light);
  }
`;

const GithubInputDescription = styled.small`
  font-size: 12px;
  color: var(--text-secondary);
`;

const PreviewButton = styled.button`
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 12px;
  margin-left: 8px;
  text-decoration: underline;

  &:hover {
    color: var(--primary-dark);
  }
`;

const ResumeAnalysisSkills = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
`;

const ResumeSkillTag = styled.span`
  background: var(--primary-color);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
`;

const ResumeAnalysisRecommendations = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const ResumeRecommendationItem = styled.div`
  font-size: 13px;
  color: var(--text-secondary);
`;

const ResumeUploadModal = ({
  isOpen,
  onClose,
  resumeFile,
  coverLetterFile,
  githubUrl,
  isDragOver,
  existingApplicant,
  replaceExisting,
  isAnalyzing,
  isCheckingDuplicate,
  analysisResult,
  onFileChange,
  onCoverFileChange,
  onGithubUrlChange,
  onDragOver,
  onDragLeave,
  onDrop,
  onReplaceExistingChange,
  onSubmit,
  onPreviewDocument
}) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <ResumeModalOverlay
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <ResumeModalContent
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <ResumeModalHeader>
            <ResumeModalTitle>새 지원자 등록</ResumeModalTitle>
            <ResumeModalCloseButton onClick={onClose}>&times;</ResumeModalCloseButton>
          </ResumeModalHeader>

          <ResumeModalBody>
            <ResumeFormSection>
              <ResumeFormTitle>이력서 업로드</ResumeFormTitle>
              <DocumentUploadContainer>
                <FileUploadArea
                  isDragOver={isDragOver}
                  onDragOver={onDragOver}
                  onDragLeave={onDragLeave}
                  onDrop={onDrop}
                >
                  <FileUploadInput
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={onFileChange}
                    id="resume-file"
                  />
                  <FileUploadLabel htmlFor="resume-file">
                    {resumeFile ? (
                      <FileSelected>
                        <FiFile size={20} />
                        <span>{resumeFile.name}</span>
                      </FileSelected>
                    ) : (
                      <FileUploadPlaceholder>
                        {isDragOver ? (
                          <FiFile size={32} style={{ color: 'var(--primary-color)' }} />
                        ) : (
                          <FiFileText size={24} />
                        )}
                        <span>
                          {isDragOver
                            ? '파일을 여기에 놓으세요'
                            : '이력서 파일을 선택하거나 드래그하세요'
                          }
                        </span>
                        <small>PDF, DOC, DOCX, TXT 파일 지원</small>
                      </FileUploadPlaceholder>
                    )}
                  </FileUploadLabel>
                </FileUploadArea>
              </DocumentUploadContainer>
            </ResumeFormSection>

            <ResumeFormSection>
              <ResumeFormTitle>자기소개서 업로드</ResumeFormTitle>
              <DocumentUploadContainer>
                <FileUploadArea
                  isDragOver={isDragOver}
                  onDragOver={onDragOver}
                  onDragLeave={onDragLeave}
                  onDrop={onDrop}
                >
                  <FileUploadInput
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={onCoverFileChange}
                    id="cover-file"
                  />
                  <FileUploadLabel htmlFor="cover-file">
                    {coverLetterFile ? (
                      <FileSelected>
                        <FiFile size={20} />
                        <span>{coverLetterFile.name}</span>
                      </FileSelected>
                    ) : (
                      <FileUploadPlaceholder>
                        {isDragOver ? (
                          <FiFile size={32} style={{ color: 'var(--primary-color)' }} />
                        ) : (
                          <FiFileText size={24} />
                        )}
                        <span>
                          {isDragOver
                            ? '파일을 여기에 놓으세요'
                            : '자기소개서 파일을 선택하거나 드래그하세요'
                          }
                        </span>
                        <small>PDF, DOC, DOCX, TXT 파일 지원</small>
                      </FileUploadPlaceholder>
                    )}
                  </FileUploadLabel>
                </FileUploadArea>
              </DocumentUploadContainer>
            </ResumeFormSection>

            <ResumeFormSection>
              <ResumeFormTitle>깃허브 주소</ResumeFormTitle>
              <DocumentUploadContainer>
                <GithubInputContainer>
                  <GithubInput
                    type="text"
                    placeholder="https://github.com/username/repository"
                    value={githubUrl}
                    onChange={onGithubUrlChange}
                  />
                  <GithubInputDescription>
                    지원자의 깃허브 저장소 주소를 입력하세요
                  </GithubInputDescription>
                </GithubInputContainer>
              </DocumentUploadContainer>
            </ResumeFormSection>

            {/* 기존 지원자 정보 표시 */}
            {existingApplicant && (
              <ExistingApplicantInfo>
                <ExistingApplicantTitle>🔄 기존 지원자 발견</ExistingApplicantTitle>
                <ExistingApplicantDetails>
                  <div><strong>이름:</strong> {existingApplicant.name}</div>
                  <div><strong>이메일:</strong> {existingApplicant.email || 'N/A'}</div>
                  <div><strong>현재 서류:</strong></div>
                  <ul>
                    <li>
                      이력서: {existingApplicant.resume ? '✅ 있음' : '❌ 없음'}
                      {existingApplicant.resume && (
                        <PreviewButton onClick={() => onPreviewDocument('resume')}>
                          👁️ 미리보기
                        </PreviewButton>
                      )}
                    </li>
                    <li>
                      자기소개서: {existingApplicant.cover_letter ? '✅ 있음' : '❌ 없음'}
                      {existingApplicant.cover_letter && (
                        <PreviewButton onClick={() => onPreviewDocument('cover_letter')}>
                          👁️ 미리보기
                        </PreviewButton>
                      )}
                    </li>
                    <li>
                      깃허브: {existingApplicant.github_url ? '✅ 있음' : '❌ 없음'}
                      {existingApplicant.github_url && (
                        <a href={existingApplicant.github_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary-color)', textDecoration: 'none', marginLeft: '8px' }}>
                          🔗 링크 열기
                        </a>
                      )}
                    </li>
                  </ul>

                  {/* 교체 옵션 체크박스 */}
                  <ReplaceOptionSection>
                    <ReplaceOptionLabel>
                      <input
                        type="checkbox"
                        checked={replaceExisting}
                        onChange={(e) => onReplaceExistingChange(e.target.checked)}
                      />
                      <span>기존 서류를 새 서류로 교체</span>
                    </ReplaceOptionLabel>
                    <ReplaceOptionDescription>
                      체크하면 기존에 있는 서류를 새로 업로드한 서류로 교체합니다.
                      체크하지 않으면 중복 서류는 업로드되지 않습니다.
                    </ReplaceOptionDescription>
                  </ReplaceOptionSection>
                </ExistingApplicantDetails>
              </ExistingApplicantInfo>
            )}

            <ResumeFormActions>
              <ResumeSubmitButton
                onClick={onSubmit}
                disabled={(!resumeFile && !coverLetterFile && !githubUrl.trim()) || isAnalyzing || isCheckingDuplicate}
              >
                {isAnalyzing ? '처리 중...' : isCheckingDuplicate ? '중복 체크 중...' : '업로드 및 저장'}
              </ResumeSubmitButton>
            </ResumeFormActions>
          </ResumeModalBody>

          {isAnalyzing && (
            <ResumeAnalysisSection>
              <ResumeAnalysisTitle>문서 업로드 및 분석 중입니다...</ResumeAnalysisTitle>
              <ResumeAnalysisSpinner>
                <div className="spinner"></div>
                <span>AI가 문서를 분석하고 있습니다 (최대 5분 소요)</span>
                <small style={{ marginTop: '8px', color: 'var(--text-secondary)' }}>
                  대용량 파일이나 여러 파일을 동시에 처리할 때 시간이 오래 걸릴 수 있습니다.
                </small>
              </ResumeAnalysisSpinner>
            </ResumeAnalysisSection>
          )}

          {analysisResult && (
            <ResumeAnalysisSection>
              <ResumeAnalysisTitle>업로드 결과</ResumeAnalysisTitle>
              <ResumeAnalysisContent>
                <ResumeAnalysisItem>
                  <ResumeAnalysisLabel>문서 유형:</ResumeAnalysisLabel>
                  <ResumeAnalysisValue>{analysisResult.documentType}</ResumeAnalysisValue>
                </ResumeAnalysisItem>
                <ResumeAnalysisItem>
                  <ResumeAnalysisLabel>파일명:</ResumeAnalysisLabel>
                  <ResumeAnalysisValue>{analysisResult.fileName}</ResumeAnalysisValue>
                </ResumeAnalysisItem>
                <ResumeAnalysisItem>
                  <ResumeAnalysisLabel>업로드 일시:</ResumeAnalysisLabel>
                  <ResumeAnalysisValue>{analysisResult.analysisDate}</ResumeAnalysisValue>
                </ResumeAnalysisItem>
                {analysisResult.applicant && (
                  <>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>지원자 이름:</ResumeAnalysisLabel>
                      <ResumeAnalysisValue>{analysisResult.applicant.name || 'N/A'}</ResumeAnalysisValue>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>지원자 이메일:</ResumeAnalysisLabel>
                      <ResumeAnalysisValue>{analysisResult.applicant.email || 'N/A'}</ResumeAnalysisValue>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>지원자 전화번호:</ResumeAnalysisLabel>
                      <ResumeAnalysisValue>{analysisResult.applicant.phone || 'N/A'}</ResumeAnalysisValue>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>지원 직무:</ResumeAnalysisLabel>
                      <ResumeAnalysisValue>{analysisResult.applicant.position || 'N/A'}</ResumeAnalysisValue>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>기술 스택:</ResumeAnalysisLabel>
                      <ResumeAnalysisSkills>
                        {Array.isArray(analysisResult.applicant.skills)
                          ? analysisResult.applicant.skills.map((skill, index) => (
                              <ResumeSkillTag key={index}>{skill}</ResumeSkillTag>
                            ))
                          : typeof analysisResult.applicant.skills === 'string'
                          ? analysisResult.applicant.skills.split(',').map((skill, index) => (
                              <ResumeSkillTag key={index}>{skill.trim()}</ResumeSkillTag>
                            ))
                          : null
                        }
                      </ResumeAnalysisSkills>
                    </ResumeAnalysisItem>
                  </>
                )}
                <ResumeAnalysisItem>
                  <ResumeAnalysisLabel>업로드 결과:</ResumeAnalysisLabel>
                  <ResumeAnalysisRecommendations>
                    {analysisResult.uploadResults?.map((result, index) => (
                      <ResumeRecommendationItem key={index}>
                        ✅ {result.type === 'resume' ? '이력서' : result.type === 'cover_letter' ? '자기소개서' : '포트폴리오'} 업로드 성공
                      </ResumeRecommendationItem>
                    ))}
                    {analysisResult.analysisResult && Object.keys(analysisResult.analysisResult).map((docType, index) => (
                      <ResumeRecommendationItem key={`doc-${index}`}>
                        ✅ {docType === 'resume' ? '이력서' : docType === 'cover_letter' ? '자기소개서' : '포트폴리오'} OCR 처리 완료
                      </ResumeRecommendationItem>
                    ))}
                  </ResumeAnalysisRecommendations>
                </ResumeAnalysisItem>
                <ResumeAnalysisItem>
                  <ResumeAnalysisLabel>상태:</ResumeAnalysisLabel>
                  <ResumeAnalysisValue style={{ color: '#28a745', fontWeight: 'bold' }}>
                    ✅ 성공적으로 DB에 저장되었습니다
                  </ResumeAnalysisValue>
                </ResumeAnalysisItem>
              </ResumeAnalysisContent>
            </ResumeAnalysisSection>
          )}

          <ResumeModalFooter>
            <ResumeModalButton onClick={onClose}>
              {analysisResult ? '닫기' : '취소'}
            </ResumeModalButton>
          </ResumeModalFooter>
        </ResumeModalContent>
      </ResumeModalOverlay>
    </AnimatePresence>
  );
};

export default ResumeUploadModal;
