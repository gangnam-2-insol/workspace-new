import React, { useState } from 'react';
import styled from 'styled-components';
import { FiMessageSquare, FiUpload, FiX, FiCheck, FiAlertCircle } from 'react-icons/fi';

const CoverLetterAnalysisContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin: 20px 0;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
`;

const Title = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const Icon = styled.div`
  color: var(--primary-color);
  font-size: 20px;
`;

const UploadArea = styled.div`
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  background: var(--background-light);
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    border-color: var(--primary-color);
    background: var(--background-hover);
  }
  
  &.dragover {
    border-color: var(--primary-color);
    background: var(--background-hover);
  }
`;

const UploadText = styled.div`
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 8px;
`;

const UploadSubtext = styled.div`
  color: var(--text-tertiary);
  font-size: 14px;
`;

const FileInput = styled.input`
  display: none;
`;

const SelectedFile = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--background-light);
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
`;

const FileInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const FileIcon = styled.div`
  color: var(--primary-color);
  font-size: 20px;
`;

const FileDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const FileName = styled.div`
  font-weight: 500;
  color: var(--text-primary);
`;

const FileSize = styled.div`
  font-size: 12px;
  color: var(--text-tertiary);
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  
  &:hover {
    color: var(--error-color);
    background: var(--background-hover);
  }
`;

const AnalysisButton = styled.button`
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  
  &:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
  }
  
  &:disabled {
    background: var(--disabled-color);
    cursor: not-allowed;
    transform: none;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px;
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--error-color);
  background: var(--error-background);
  padding: 12px;
  border-radius: 8px;
  margin: 16px 0;
  font-size: 14px;
`;

const SuccessMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--success-color);
  background: var(--success-background);
  padding: 12px;
  border-radius: 8px;
  margin: 16px 0;
  font-size: 14px;
`;

const CoverLetterAnalysis = ({ onAnalysisComplete, onClose }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file) => {
    // 파일 타입 검증
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      setError('지원하지 않는 파일 형식입니다. PDF, Word, 또는 텍스트 파일을 업로드해주세요.');
      return;
    }
    
    // 파일 크기 검증 (10MB 제한)
    if (file.size > 10 * 1024 * 1024) {
      setError('파일 크기가 너무 큽니다. 10MB 이하의 파일을 업로드해주세요.');
      return;
    }
    
    setSelectedFile(file);
    setError(null);
    setSuccess(null);
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setError(null);
    setSuccess(null);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const analyzeCoverLetter = async () => {
    if (!selectedFile) {
      setError('분석할 파일을 선택해주세요.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('document_type', 'cover_letter');

      const response = await fetch('/api/upload/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`분석 요청 실패: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'success') {
        setSuccess('자기소개서 분석이 완료되었습니다!');
        // 부모 컴포넌트에 분석 결과 전달
        if (onAnalysisComplete) {
          onAnalysisComplete(result.analysis_result);
        }
      } else {
        throw new Error(result.message || '분석 중 오류가 발생했습니다.');
      }
    } catch (err) {
      setError(`분석 실패: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUploadClick = () => {
    document.getElementById('cover-letter-file-input').click();
  };

  return (
    <CoverLetterAnalysisContainer>
      <Header>
        <Icon>
          <FiMessageSquare />
        </Icon>
        <Title>자기소개서 분석</Title>
      </Header>

      {error && (
        <ErrorMessage>
          <FiAlertCircle />
          {error}
        </ErrorMessage>
      )}

      {success && (
        <SuccessMessage>
          <FiCheck />
          {success}
        </SuccessMessage>
      )}

      {!selectedFile ? (
        <UploadArea
          className={isDragging ? 'dragover' : ''}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleUploadClick}
        >
          <UploadText>자기소개서 파일을 업로드하세요</UploadText>
          <UploadSubtext>PDF, Word, 또는 텍스트 파일을 드래그하거나 클릭하여 선택</UploadSubtext>
        </UploadArea>
      ) : (
        <SelectedFile>
          <FileInfo>
            <FileIcon>
              <FiMessageSquare />
            </FileIcon>
            <FileDetails>
              <FileName>{selectedFile.name}</FileName>
              <FileSize>{formatFileSize(selectedFile.size)}</FileSize>
            </FileDetails>
          </FileInfo>
          <RemoveButton onClick={removeFile}>
            <FiX />
          </RemoveButton>
        </SelectedFile>
      )}

      <FileInput
        id="cover-letter-file-input"
        type="file"
        accept=".pdf,.doc,.docx,.txt"
        onChange={handleFileInputChange}
      />

      {selectedFile && (
        <AnalysisButton
          onClick={analyzeCoverLetter}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? (
            <>
              <LoadingSpinner />
              분석 중...
            </>
          ) : (
            '자기소개서 분석 시작'
          )}
        </AnalysisButton>
      )}
    </CoverLetterAnalysisContainer>
  );
};

export default CoverLetterAnalysis;
