import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { FiUpload, FiFileText, FiDownload, FiCopy, FiCheck, FiX } from 'react-icons/fi';

const PDFOCRPage = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [processingMode, setProcessingMode] = useState('fast'); // 'fast' 또는 'detailed'
  const [backgroundTaskId, setBackgroundTaskId] = useState(null);
  const [backgroundTaskStatus, setBackgroundTaskStatus] = useState(null);
  const [isMonitoringBackground, setIsMonitoringBackground] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    } else {
      setError('PDF 파일만 업로드 가능합니다.');
      setFile(null);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
      setError(null);
      setResult(null);
    } else {
      setError('PDF 파일만 업로드 가능합니다.');
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleUpload = async () => {
    if (!file) {
      setError('파일을 선택해주세요.');
      return;
    }

    setIsProcessing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // 처리 모드에 따라 다른 API 엔드포인트 사용
      const endpoint = processingMode === 'fast' 
        ? '/api/pdf-ocr/upload-pdf-fast' 
        : '/api/pdf-ocr/upload-pdf';
      
      console.log(`🚀 ${processingMode === 'fast' ? '빠른' : '상세'} 처리 모드로 업로드 시작`);
      
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      
      // 빠른 처리 모드에서 백그라운드 작업 ID가 있으면 모니터링 시작
      if (processingMode === 'fast' && data.background_task_id) {
        setBackgroundTaskId(data.background_task_id);
        startBackgroundMonitoring(data.background_task_id);
      }
      
      console.log(`✅ ${processingMode === 'fast' ? '빠른' : '상세'} 처리 완료`);
    } catch (err) {
      setError(`${processingMode === 'fast' ? '빠른' : '상세'} OCR 처리 중 오류가 발생했습니다: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // 백그라운드 작업 모니터링 시작
  const startBackgroundMonitoring = (taskId) => {
    setIsMonitoringBackground(true);
    setBackgroundTaskStatus('queued');
    
    // 주기적으로 상태 확인
    const checkStatus = async () => {
      try {
        const response = await fetch(`/api/pdf-ocr/background-tasks/${taskId}`);
        if (response.ok) {
          const statusData = await response.json();
          setBackgroundTaskStatus(statusData.status);
          
          if (statusData.status === 'completed') {
            console.log('✅ 백그라운드 AI 분석 완료');
            setIsMonitoringBackground(false);
            // 완료된 경우 결과를 새로고침하거나 알림
            showCompletionNotification();
          } else if (statusData.status === 'failed') {
            console.log('❌ 백그라운드 AI 분석 실패');
            setIsMonitoringBackground(false);
            setError(`백그라운드 AI 분석 실패: ${statusData.error}`);
          }
        }
      } catch (error) {
        console.error('백그라운드 작업 상태 확인 실패:', error);
      }
    };
    
    // 5초마다 상태 확인
    const intervalId = setInterval(checkStatus, 5000);
    
    // 컴포넌트 언마운트 시 인터벌 정리
    return () => clearInterval(intervalId);
  };

  // 완료 알림 표시
  const showCompletionNotification = () => {
    // 브라우저 알림 또는 토스트 메시지 표시
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('AI 분석 완료', {
        body: '백그라운드 AI 분석이 완료되었습니다.',
        icon: '/favicon.ico'
      });
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      setError('클립보드 복사에 실패했습니다.');
    }
  };

  const downloadText = (text, filename) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const resetForm = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setCopied(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // 헬퍼 함수들
  const getDocumentTypeLabel = (type) => {
    const labels = {
      'resume': '이력서',
      'cover_letter': '자기소개서',
      'report': '보고서',
      'contract': '계약서',
      'manual': '매뉴얼',
      'general': '일반 문서'
    };
    return labels[type] || type;
  };



  const getInfoTypeLabel = (type) => {
    const labels = {
      'emails': '이메일',
      'phones': '전화번호',
      'dates': '날짜',
      'numbers': '숫자',
      'urls': 'URL',
      'names': '이름',
      'positions': '직책',
      'companies': '회사',
      'education': '학력',
      'skills': '스킬/기술',
      'addresses': '주소'
    };
    return labels[type] || type;
  };

  return (
    <Container>
      <Header>
        <Title>📄 PDF OCR 처리</Title>
        <Subtitle>PDF 파일을 업로드하여 텍스트를 추출하고 분석합니다</Subtitle>
      </Header>

      <Content>
        <UploadSection>
          <ProcessingModeSelector>
            <ModeLabel>처리 모드 선택:</ModeLabel>
            <ModeButtons>
              <ModeButton 
                active={processingMode === 'fast'} 
                onClick={() => setProcessingMode('fast')}
              >
                🚀 빠른 처리
                <ModeDescription>기본 OCR + 간단한 분석 (빠름)</ModeDescription>
              </ModeButton>
              <ModeButton 
                active={processingMode === 'detailed'} 
                onClick={() => setProcessingMode('detailed')}
              >
                🔍 상세 분석
                <ModeDescription>AI 분석 + 상세 정보 추출 (느림)</ModeDescription>
              </ModeButton>
            </ModeButtons>
          </ProcessingModeSelector>

          <UploadArea
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            hasFile={!!file}
            isProcessing={isProcessing}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            
            {!file ? (
              <UploadContent>
                <FiUpload size={48} />
                <UploadText>
                  PDF 파일을 드래그하여 놓거나 클릭하여 선택하세요
                </UploadText>
                <UploadButton onClick={() => fileInputRef.current?.click()}>
                  파일 선택
                </UploadButton>
              </UploadContent>
            ) : (
              <FileInfo>
                <FiFileText size={32} />
                <div>
                  <FileName>{file.name}</FileName>
                  <FileSize>{(file.size / 1024 / 1024).toFixed(2)} MB</FileSize>
                </div>
                <RemoveButton onClick={resetForm}>
                  <FiX size={20} />
                </RemoveButton>
              </FileInfo>
            )}
          </UploadArea>

          {file && (
            <ActionButtons>
              <ProcessButton 
                onClick={handleUpload} 
                disabled={isProcessing}
              >
                {isProcessing ? '처리 중...' : 'OCR 처리 시작'}
              </ProcessButton>
            </ActionButtons>
          )}
        </UploadSection>

        {error && (
          <ErrorMessage>
            <FiX size={16} />
            {error}
          </ErrorMessage>
        )}

        {isProcessing && (
          <ProcessingMessage>
            <div className="spinner"></div>
            {processingMode === 'fast' 
              ? 'PDF 파일을 빠르게 분석하고 있습니다... (예상 시간: 10-30초)' 
              : 'PDF 파일을 상세하게 분석하고 있습니다... (예상 시간: 1-3분)'
            }
          </ProcessingMessage>
        )}

        {/* 백그라운드 AI 분석 상태 표시 */}
        {isMonitoringBackground && backgroundTaskStatus && (
          <BackgroundProcessingMessage>
            <div className="spinner"></div>
            <div>
              <div className="status-title">🚀 백그라운드 AI 분석 진행 중</div>
              <div className="status-detail">
                {backgroundTaskStatus === 'queued' && '대기 중...'}
                {backgroundTaskStatus === 'processing' && 'AI 분석 중... (예상 시간: 2-5분)'}
                {backgroundTaskStatus === 'completed' && 'AI 분석 완료! ✅'}
                {backgroundTaskStatus === 'failed' && 'AI 분석 실패 ❌'}
              </div>
              <div className="task-id">작업 ID: {backgroundTaskId}</div>
            </div>
          </BackgroundProcessingMessage>
        )}

        {result && (
          <ResultSection>
            <ResultHeader>
              <h3>📋 OCR 처리 결과</h3>
              <ResultInfo>
                <ProcessingModeBadge mode={result.processing_mode || processingMode}>
                  {result.processing_mode === 'fast' || processingMode === 'fast' ? '🚀 빠른 처리' : '🔍 상세 분석'}
                </ProcessingModeBadge>
              </ResultInfo>
              <ResultActions>
                <ActionButton onClick={() => copyToClipboard(result.extracted_text)}>
                  {copied ? <FiCheck size={16} /> : <FiCopy size={16} />}
                  {copied ? '복사됨' : '텍스트 복사'}
                </ActionButton>
                <ActionButton onClick={() => downloadText(result.extracted_text, 'ocr_result.txt')}>
                  <FiDownload size={16} />
                  텍스트 다운로드
                </ActionButton>
              </ResultActions>
            </ResultHeader>

            <ResultTabs>
              <TabContent>
                <TabHeader>
                  <TabButton active>📝 추출된 텍스트</TabButton>
                </TabHeader>
                <TabPanel>
                  <TextContent>
                    {result.extracted_text || '텍스트를 추출할 수 없습니다.'}
                  </TextContent>
                </TabPanel>
              </TabContent>

              {result.summary && (
                <TabContent>
                  <TabHeader>
                    <TabButton>📊 요약</TabButton>
                  </TabHeader>
                  <TabPanel>
                    <SummaryContent>
                      {result.summary}
                    </SummaryContent>
                  </TabPanel>
                </TabContent>
              )}

              {result.keywords && result.keywords.length > 0 && (
                <TabContent>
                  <TabHeader>
                    <TabButton>🏷️ 키워드</TabButton>
                  </TabHeader>
                  <TabPanel>
                    <KeywordsContainer>
                      {result.keywords.map((keyword, index) => (
                        <KeywordTag key={index}>{keyword}</KeywordTag>
                      ))}
                    </KeywordsContainer>
                  </TabPanel>
                </TabContent>
              )}

              {result.document_type && (
                <TabContent>
                  <TabHeader>
                    <TabButton>📄 문서 유형</TabButton>
                  </TabHeader>
                  <TabPanel>
                    <DocumentTypeContent>
                      <DocumentTypeBadge type={result.document_type}>
                        {getDocumentTypeLabel(result.document_type)}
                      </DocumentTypeBadge>
                    </DocumentTypeContent>
                  </TabPanel>
                </TabContent>
              )}



              {result.basic_info && Object.keys(result.basic_info).length > 0 && (
                <TabContent>
                  <TabHeader>
                    <TabButton>📞 기본 정보</TabButton>
                  </TabHeader>
                  <TabPanel>
                    <BasicInfoContainer>
                      {Object.entries(result.basic_info).map(([infoType, infoList]) => (
                        infoList.length > 0 && (
                          <InfoGroup key={infoType}>
                            <InfoTypeTitle>{getInfoTypeLabel(infoType)}</InfoTypeTitle>
                            <InfoList>
                              {infoList.map((info, index) => (
                                <InfoTag key={index}>{info}</InfoTag>
                              ))}
                            </InfoList>
                          </InfoGroup>
                        )
                      ))}
                    </BasicInfoContainer>
                  </TabPanel>
                </TabContent>
              )}
            </ResultTabs>
          </ResultSection>
        )}
      </Content>
    </Container>
  );
};

// Styled Components
const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: #718096;
  margin: 0;
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const UploadSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ProcessingModeSelector = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px 20px;
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
`;

const ModeLabel = styled.span`
  font-size: 1rem;
  color: #4a5568;
  font-weight: 600;
`;

const ModeButtons = styled.div`
  display: flex;
  gap: 15px;
`;

const ModeButton = styled.button`
  background-color: ${props => props.active ? '#4299e1' : 'transparent'};
  color: ${props => props.active ? 'white' : '#4a5568'};
  border: 1px solid ${props => props.active ? '#4299e1' : '#e2e8f0'};
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: flex-start;

  &:hover {
    background-color: ${props => props.active ? '#3182ce' : '#f7fafc'};
  }
`;

const ModeDescription = styled.span`
  font-size: 0.8rem;
  color: #718096;
  margin-top: 4px;
`;

const UploadArea = styled.div`
  border: 2px dashed ${props => props.hasFile ? '#48bb78' : '#e2e8f0'};
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  background-color: ${props => props.hasFile ? '#f0fff4' : '#fafafa'};
  transition: all 0.3s ease;
  cursor: ${props => props.isProcessing ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.isProcessing ? 0.6 : 1};

  &:hover {
    border-color: ${props => props.hasFile ? '#48bb78' : '#cbd5e0'};
    background-color: ${props => props.hasFile ? '#f0fff4' : '#f7fafc'};
  }
`;

const UploadContent = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #718096;
`;

const UploadText = styled.p`
  font-size: 1.1rem;
  margin: 0;
  max-width: 300px;
`;

const UploadButton = styled.button`
  background-color: #4299e1;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #3182ce;
  }
`;

const FileInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  color: #2d3748;
`;

const FileName = styled.div`
  font-weight: 600;
  font-size: 1.1rem;
`;

const FileSize = styled.div`
  color: #718096;
  font-size: 0.9rem;
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: #e53e3e;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #fed7d7;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  justify-content: center;
  gap: 12px;
`;

const ProcessButton = styled.button`
  background-color: #48bb78;
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 160px;

  &:hover:not(:disabled) {
    background-color: #38a169;
    transform: translateY(-1px);
  }

  &:disabled {
    background-color: #cbd5e0;
    cursor: not-allowed;
    transform: none;
  }
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #fed7d7;
  color: #c53030;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #feb2b2;
`;

const ProcessingMessage = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background-color: #ebf8ff;
  color: #2b6cb0;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #bee3f8;

  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #bee3f8;
    border-top: 2px solid #3182ce;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const BackgroundProcessingMessage = styled(ProcessingMessage)`
  background-color: #f0fff4;
  color: #2f855a;
  border: 1px solid #c6f6d5;
  margin-top: 20px;
  padding: 15px;

  .status-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 5px;
  }

  .status-detail {
    font-size: 0.9rem;
    color: #4a5568;
    margin-bottom: 5px;
  }

  .task-id {
    font-size: 0.8rem;
    color: #718096;
  }
`;

const ResultSection = styled.div`
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const ResultHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  background-color: #f7fafc;

  h3 {
    margin: 0;
    color: #2d3748;
    font-size: 1.25rem;
  }
`;

const ResultInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
`;

const ProcessingModeBadge = styled.span`
  background-color: ${props => {
    switch(props.mode) {
      case 'fast': return '#48bb78';
      case 'detailed': return '#4299e1';
      default: return '#718096';
    }
  }};
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
`;

const ResultActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: white;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background-color: #f7fafc;
    border-color: #cbd5e0;
  }
`;

const ResultTabs = styled.div`
  padding: 24px;
`;

const TabContent = styled.div`
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const TabHeader = styled.div`
  margin-bottom: 16px;
`;

const TabButton = styled.button`
  background-color: ${props => props.active ? '#4299e1' : 'transparent'};
  color: ${props => props.active ? 'white' : '#4a5568'};
  border: 1px solid ${props => props.active ? '#4299e1' : '#e2e8f0'};
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background-color: ${props => props.active ? '#3182ce' : '#f7fafc'};
  }
`;

const TabPanel = styled.div`
  background-color: #f7fafc;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e2e8f0;
`;

const TextContent = styled.div`
  white-space: pre-wrap;
  line-height: 1.6;
  color: #2d3748;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
`;

const SummaryContent = styled.div`
  line-height: 1.6;
  color: #2d3748;
`;

const KeywordsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const KeywordTag = styled.span`
  background-color: #4299e1;
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 500;
`;

// 새로운 스타일 컴포넌트들
const DocumentTypeContent = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
`;

const DocumentTypeBadge = styled.div`
  background-color: ${props => {
    switch(props.type) {
      case 'resume': return '#48bb78';
      case 'cover_letter': return '#4299e1';
      case 'report': return '#ed8936';
      case 'contract': return '#e53e3e';
      case 'manual': return '#9f7aea';
      default: return '#718096';
    }
  }};
  color: white;
  padding: 12px 24px;
  border-radius: 20px;
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
`;

const BasicInfoContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const InfoGroup = styled.div`
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  background-color: white;
`;

const InfoTypeTitle = styled.h4`
  margin: 0 0 12px 0;
  color: #2d3748;
  font-size: 1rem;
  font-weight: 600;
`;

const InfoList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const InfoTag = styled.span`
  background-color: #fef5e7;
  color: #c05621;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
`;

export default PDFOCRPage;