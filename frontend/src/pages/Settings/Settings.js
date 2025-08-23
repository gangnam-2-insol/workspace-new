import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FiSettings, FiHelpCircle, FiMail, FiSave, FiEdit3, FiChevronRight, FiInfo } from 'react-icons/fi';

const Container = styled.div`
  padding: 24px 0;
`;
const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
`;
const Card = styled.div`
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-light);
  padding: 24px;
  margin-bottom: 16px;
`;



// 탭 스타일 컴포넌트들
const TabContainer = styled.div`
  margin-top: 20px;
`;

const TabList = styled.div`
  display: flex;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 20px;
`;

const TabButton = styled.button`
  padding: 12px 24px;
  background: ${props => props.active ? '#4299e1' : 'transparent'};
  color: ${props => props.active ? 'white' : '#4a5568'};
  border: none;
  border-radius: 8px 8px 0 0;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  
  &:hover {
    background: ${props => props.active ? '#3182ce' : '#f7fafc'};
  }
  
  &:not(:last-child) {
    margin-right: 4px;
  }
`;

const TabContent = styled.div`
  display: ${props => props.active ? 'block' : 'none'};
  animation: ${props => props.active ? 'fadeIn 0.3s ease-in' : 'none'};
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const TemplateCard = styled.div`
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
`;

const TemplateHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
`;

const TemplateTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const TemplateActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  padding: 8px 16px;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  background: white;
  color: #4a5568;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  
  &:hover {
    background: #edf2f7;
    border-color: #a0aec0;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 150px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s ease;
  line-height: 1.5;
  
  &:focus {
    outline: none;
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
  }
  
  &:disabled {
    background: #f7fafc;
    color: #a0aec0;
    cursor: not-allowed;
  }
`;

const SaveButton = styled.button`
  padding: 10px 20px;
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  
  &:hover {
    background: #38a169;
    transform: translateY(-1px);
  }
  
  &:disabled {
    background: #cbd5e0;
    cursor: not-allowed;
    transform: none;
  }
`;

const InputField = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  margin-bottom: 16px;
  
  &:focus {
    outline: none;
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
  }
  
  &:disabled {
    background: #f7fafc;
    color: #a0aec0;
    cursor: not-allowed;
  }
`;

const Label = styled.label`
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
  margin: 0;
`;

const VariableInfo = styled.div`
  margin-top: 12px;
  padding: 12px;
  background: #edf2f7;
  border-radius: 6px;
  font-size: 12px;
  color: #4a5568;
  
  h4 {
    margin: 0 0 8px 0;
    font-size: 13px;
    font-weight: 600;
  }
  
  ul {
    margin: 0;
    padding-left: 16px;
  }
  
  li {
    margin-bottom: 4px;
  }
`;

const LabelContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  line-height: 1;
`;

const HelpIcon = styled.div`
  position: relative;
  cursor: pointer;
  color: #718096;
  transition: color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: #4299e1;
  }
`;

const Tooltip = styled.div`
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #2d3748;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  
  &::before {
    content: '';
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 4px solid transparent;
    border-bottom-color: #2d3748;
  }
  
  ${props => props.show && `
    opacity: 1;
    visibility: visible;
  `}
`;

function Settings() {
  const [mailTemplates, setMailTemplates] = useState({
    passed: {
      subject: '축하합니다! 서류 전형 합격 안내',
      content: `안녕하세요, {applicant_name}님

축하드립니다! {job_posting_title} 포지션에 대한 서류 전형에 합격하셨습니다.

다음 단계인 면접 일정은 추후 별도로 안내드리겠습니다.

감사합니다.
{company_name} 채용팀`
    },
    rejected: {
      subject: '서류 전형 결과 안내',
      content: `안녕하세요, {applicant_name}님

{job_posting_title} 포지션에 대한 서류 전형 결과를 안내드립니다.

안타깝게도 이번 전형에서는 합격하지 못했습니다.
앞으로 더 좋은 기회가 있을 때 다시 지원해 주시기 바랍니다.

감사합니다.
{company_name} 채용팀`
    }
  });

  const [editingTemplate, setEditingTemplate] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('passed'); // 기본값은 합격 탭
  const [mailSettings, setMailSettings] = useState({
    senderEmail: '',
    senderPassword: '',
    senderName: '',
    smtpServer: 'smtp.gmail.com',
    smtpPort: 587
  });
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [tooltipStates, setTooltipStates] = useState({});
  const [testEmail, setTestEmail] = useState('');
  const [isSendingTest, setIsSendingTest] = useState(false);

  // 툴팁 표시/숨김 핸들러
  const handleTooltipShow = (field) => {
    setTooltipStates(prev => ({ ...prev, [field]: true }));
  };

  const handleTooltipHide = (field) => {
    setTooltipStates(prev => ({ ...prev, [field]: false }));
  };

  // 테스트 메일 발송
  const handleSendTestMail = async () => {
    if (!testEmail.trim()) {
      alert('테스트 이메일 주소를 입력해주세요.');
      return;
    }

    if (!mailSettings.senderEmail || !mailSettings.senderPassword) {
      alert('메일 서버 설정이 완료되지 않았습니다. 발송자 이메일과 앱 비밀번호를 설정해주세요.');
      return;
    }

    setIsSendingTest(true);
    try {
      const response = await fetch('http://localhost:8000/api/send-test-mail', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          testEmail: testEmail.trim(),
          mailSettings: mailSettings
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ 테스트 메일이 성공적으로 발송되었습니다!\n\n받는 사람: ${testEmail}\n제목: ${result.subject}`);
        setTestEmail('');
      } else {
        const error = await response.json();
        alert(`❌ 테스트 메일 발송 실패: ${error.error}`);
      }
    } catch (error) {
      console.error('테스트 메일 발송 실패:', error);
      alert('테스트 메일 발송 중 오류가 발생했습니다.');
    } finally {
      setIsSendingTest(false);
    }
  };

  // DB에서 템플릿과 설정 불러오기
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 메일 템플릿 조회
        const templatesResponse = await fetch('http://localhost:8000/api/mail-templates');
        if (templatesResponse.ok) {
          const templates = await templatesResponse.json();
          setMailTemplates(templates);
        }
        
        // 메일 설정 조회
        const settingsResponse = await fetch('http://localhost:8000/api/mail-settings');
        if (settingsResponse.ok) {
          const settings = await settingsResponse.json();
          setMailSettings(settings);
        }
      } catch (error) {
        console.error('데이터 로드 실패:', error);
        // 로컬 스토리지에서 폴백
        const savedTemplates = localStorage.getItem('mailTemplates');
        if (savedTemplates) {
          setMailTemplates(JSON.parse(savedTemplates));
        }
        
        const savedMailSettings = localStorage.getItem('mailSettings');
        if (savedMailSettings) {
          setMailSettings(JSON.parse(savedMailSettings));
        }
      }
    };
    
    fetchData();
  }, []);

  // 템플릿 편집 시작
  const handleEditTemplate = (type) => {
    setEditingTemplate(type);
  };

  // 템플릿 저장
  const handleSaveTemplate = async (type) => {
    setIsSaving(true);
    try {
      // DB에 저장
      const response = await fetch('http://localhost:8000/api/mail-templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mailTemplates)
      });
      
      if (response.ok) {
        const result = await response.json();
        setEditingTemplate(null);
        alert(result.message || '메일 양식이 저장되었습니다.');
      } else {
        throw new Error('저장 실패');
      }
    } catch (error) {
      console.error('템플릿 저장 실패:', error);
      alert('저장 중 오류가 발생했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  // 템플릿 내용 변경
  const handleTemplateChange = (type, field, value) => {
    setMailTemplates(prev => ({
      ...prev,
      [type]: {
        ...prev[type],
        [field]: value
      }
    }));
  };

  // 탭 변경 핸들러
  const handleTabChange = (tabName) => {
    setActiveTab(tabName);
    setEditingTemplate(null); // 탭 변경 시 편집 모드 해제
  };

  // 메일 설정 저장
  const handleSaveMailSettings = async () => {
    setIsSaving(true);
    try {
      // DB에 저장
      const response = await fetch('http://localhost:8000/api/mail-settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mailSettings)
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(result.message || '메일 설정이 저장되었습니다.');
      } else {
        throw new Error('저장 실패');
      }
    } catch (error) {
      console.error('메일 설정 저장 실패:', error);
      alert('저장 중 오류가 발생했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  // 메일 설정 변경
  const handleMailSettingsChange = (field, value) => {
    setMailSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Container>
      <Title>설정 및 지원</Title>
      
      <Card>
        <h2><FiMail /> 메일 양식 관리</h2>
        <p>지원자들에게 자동으로 발송되는 메일의 양식을 관리할 수 있습니다.</p>
        
        <TabContainer>
          <TabList>
            <TabButton 
              active={activeTab === 'passed'} 
              onClick={() => handleTabChange('passed')}
            >
              <FiMail size={16} />
              합격 안내 메일
            </TabButton>
            <TabButton 
              active={activeTab === 'rejected'} 
              onClick={() => handleTabChange('rejected')}
            >
              <FiMail size={16} />
              불합격 안내 메일
            </TabButton>
            <TabButton 
              active={activeTab === 'settings'} 
              onClick={() => handleTabChange('settings')}
            >
              <FiSettings size={16} />
              메일 서버 설정
            </TabButton>
          </TabList>

          {/* 합격 메일 양식 탭 */}
          <TabContent active={activeTab === 'passed'}>
            <TemplateCard>
              <TemplateHeader>
                <TemplateTitle>
                  <FiMail size={20} />
                  합격 안내 메일
                </TemplateTitle>
                <TemplateActions>
                  {editingTemplate === 'passed' ? (
                    <SaveButton 
                      onClick={() => handleSaveTemplate('passed')}
                      disabled={isSaving}
                    >
                      <FiSave size={14} />
                      {isSaving ? '저장 중...' : '저장'}
                    </SaveButton>
                  ) : (
                    <ActionButton onClick={() => handleEditTemplate('passed')}>
                      <FiEdit3 size={14} />
                      편집
                    </ActionButton>
                  )}
                </TemplateActions>
              </TemplateHeader>
              
                             <div>
                 <LabelContainer>
                   <Label>제목:</Label>
                   <HelpIcon
                     onMouseEnter={() => handleTooltipShow('passedSubject')}
                     onMouseLeave={() => handleTooltipHide('passedSubject')}
                   >
                     <FiInfo size={14} />
                     <Tooltip show={tooltipStates.passedSubject}>
                       합격자에게 발송될 메일의 제목
                     </Tooltip>
                   </HelpIcon>
                 </LabelContainer>
                 <InputField
                   type="text"
                   value={mailTemplates.passed.subject}
                   onChange={(e) => handleTemplateChange('passed', 'subject', e.target.value)}
                   disabled={editingTemplate !== 'passed'}
                   placeholder="메일 제목을 입력하세요..."
                 />
                 
                 <LabelContainer>
                   <Label>내용:</Label>
                   <HelpIcon
                     onMouseEnter={() => handleTooltipShow('passedContent')}
                     onMouseLeave={() => handleTooltipHide('passedContent')}
                   >
                     <FiInfo size={14} />
                     <Tooltip show={tooltipStates.passedContent}>
                       합격자에게 발송될 메일의 내용 (변수 사용 가능)
                     </Tooltip>
                   </HelpIcon>
                 </LabelContainer>
                 <TextArea
                   value={mailTemplates.passed.content}
                   onChange={(e) => handleTemplateChange('passed', 'content', e.target.value)}
                   disabled={editingTemplate !== 'passed'}
                   placeholder="메일 내용을 입력하세요..."
                 />
               </div>
              
              <VariableInfo>
                <h4>사용 가능한 변수:</h4>
                <ul>
                  <li><code>{'{applicant_name}'}</code> - 지원자 이름</li>
                  <li><code>{'{job_posting_title}'}</code> - 채용공고 제목</li>
                  <li><code>{'{company_name}'}</code> - 회사명</li>
                  <li><code>{'{position}'}</code> - 지원 직무</li>
                </ul>
              </VariableInfo>
            </TemplateCard>
          </TabContent>

          {/* 불합격 메일 양식 탭 */}
          <TabContent active={activeTab === 'rejected'}>
            <TemplateCard>
              <TemplateHeader>
                <TemplateTitle>
                  <FiMail size={20} />
                  불합격 안내 메일
                </TemplateTitle>
                <TemplateActions>
                  {editingTemplate === 'rejected' ? (
                    <SaveButton 
                      onClick={() => handleSaveTemplate('rejected')}
                      disabled={isSaving}
                    >
                      <FiSave size={14} />
                      {isSaving ? '저장 중...' : '저장'}
                    </SaveButton>
                  ) : (
                    <ActionButton onClick={() => handleEditTemplate('rejected')}>
                      <FiEdit3 size={14} />
                      편집
                    </ActionButton>
                  )}
                </TemplateActions>
              </TemplateHeader>
              
                             <div>
                 <LabelContainer>
                   <Label>제목:</Label>
                   <HelpIcon
                     onMouseEnter={() => handleTooltipShow('rejectedSubject')}
                     onMouseLeave={() => handleTooltipHide('rejectedSubject')}
                   >
                     <FiInfo size={14} />
                     <Tooltip show={tooltipStates.rejectedSubject}>
                       불합격자에게 발송될 메일의 제목
                     </Tooltip>
                   </HelpIcon>
                 </LabelContainer>
                 <InputField
                   type="text"
                   value={mailTemplates.rejected.subject}
                   onChange={(e) => handleTemplateChange('rejected', 'subject', e.target.value)}
                   disabled={editingTemplate !== 'rejected'}
                   placeholder="메일 제목을 입력하세요..."
                 />
                 
                 <LabelContainer>
                   <Label>내용:</Label>
                   <HelpIcon
                     onMouseEnter={() => handleTooltipShow('rejectedContent')}
                     onMouseLeave={() => handleTooltipHide('rejectedContent')}
                   >
                     <FiInfo size={14} />
                     <Tooltip show={tooltipStates.rejectedContent}>
                       불합격자에게 발송될 메일의 내용 (변수 사용 가능)
                     </Tooltip>
                   </HelpIcon>
                 </LabelContainer>
                 <TextArea
                   value={mailTemplates.rejected.content}
                   onChange={(e) => handleTemplateChange('rejected', 'content', e.target.value)}
                   disabled={editingTemplate !== 'rejected'}
                   placeholder="메일 내용을 입력하세요..."
                 />
               </div>
              
              <VariableInfo>
                <h4>사용 가능한 변수:</h4>
                <ul>
                  <li><code>{'{applicant_name}'}</code> - 지원자 이름</li>
                  <li><code>{'{job_posting_title}'}</code> - 채용공고 제목</li>
                  <li><code>{'{company_name}'}</code> - 회사명</li>
                  <li><code>{'{position}'}</code> - 지원 직무</li>
                </ul>
              </VariableInfo>
            </TemplateCard>
          </TabContent>

          {/* 메일 서버 설정 탭 */}
          <TabContent active={activeTab === 'settings'}>
            <TemplateCard>
              <TemplateHeader>
                <TemplateTitle>
                  <FiSettings size={20} />
                  메일 서버 설정
                </TemplateTitle>
                <TemplateActions>
                  <SaveButton 
                    onClick={handleSaveMailSettings}
                    disabled={isSaving}
                  >
                    <FiSave size={14} />
                    {isSaving ? '저장 중...' : '설정 저장'}
                  </SaveButton>
                </TemplateActions>
              </TemplateHeader>
              
                             <div>
                 <LabelContainer>
                   <Label>발송자 이메일 주소:</Label>
                   <HelpIcon
                     onMouseEnter={() => handleTooltipShow('senderEmail')}
                     onMouseLeave={() => handleTooltipHide('senderEmail')}
                   >
                     <FiInfo size={14} />
                     <Tooltip show={tooltipStates.senderEmail}>
                       메일을 보낼 Gmail 계정 주소를 입력하세요
                     </Tooltip>
                   </HelpIcon>
                 </LabelContainer>
                 <InputField
                   type="email"
                   value={mailSettings.senderEmail}
                   onChange={(e) => handleMailSettingsChange('senderEmail', e.target.value)}
                   placeholder="your-email@gmail.com"
                 />
                 
                 <LabelContainer>
                   <Label>발송자 이름:</Label>
                   <HelpIcon
                     onMouseEnter={() => handleTooltipShow('senderName')}
                     onMouseLeave={() => handleTooltipHide('senderName')}
                   >
                     <FiInfo size={14} />
                     <Tooltip show={tooltipStates.senderName}>
                       받는 사람에게 표시될 발송자 이름
                     </Tooltip>
                   </HelpIcon>
                 </LabelContainer>
                 <InputField
                   type="text"
                   value={mailSettings.senderName}
                   onChange={(e) => handleMailSettingsChange('senderName', e.target.value)}
                   placeholder="회사명 채용팀"
                 />
                 
                 <ActionButton 
                   onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                   style={{ marginBottom: '16px' }}
                 >
                   <FiChevronRight 
                     size={14} 
                     style={{ 
                       transform: showAdvancedSettings ? 'rotate(90deg)' : 'rotate(0deg)',
                       transition: 'transform 0.2s ease'
                     }} 
                   />
                   {showAdvancedSettings ? '고급 설정 숨기기' : '고급 설정 보기'}
                 </ActionButton>
                 
                                   {showAdvancedSettings && (
                    <div style={{ 
                      padding: '16px', 
                      background: '#f8f9fa', 
                      border: '1px solid #e9ecef', 
                      borderRadius: '8px',
                      marginBottom: '16px'
                    }}>
                      <LabelContainer>
                        <Label>이메일 비밀번호 (앱 비밀번호):</Label>
                        <HelpIcon
                          onMouseEnter={() => handleTooltipShow('senderPassword')}
                          onMouseLeave={() => handleTooltipHide('senderPassword')}
                        >
                          <FiInfo size={14} />
                          <Tooltip show={tooltipStates.senderPassword}>
                            메일 2단계 인증 후 생성하는 16자리 앱 비밀번호
                          </Tooltip>
                        </HelpIcon>
                      </LabelContainer>
                      <InputField
                        type="password"
                        value={mailSettings.senderPassword}
                        onChange={(e) => handleMailSettingsChange('senderPassword', e.target.value)}
                        placeholder="Gmail 앱 비밀번호를 입력하세요"
                      />
                      
                      <LabelContainer>
                        <Label>SMTP 서버:</Label>
                        <HelpIcon
                          onMouseEnter={() => handleTooltipShow('smtpServer')}
                          onMouseLeave={() => handleTooltipHide('smtpServer')}
                        >
                          <FiInfo size={14} />
                          <Tooltip show={tooltipStates.smtpServer}>
                            Gmail의 SMTP 서버 주소 (기본값: smtp.gmail.com)
                          </Tooltip>
                        </HelpIcon>
                      </LabelContainer>
                      <InputField
                        type="text"
                        value={mailSettings.smtpServer}
                        onChange={(e) => handleMailSettingsChange('smtpServer', e.target.value)}
                        placeholder="smtp.gmail.com"
                      />
                      
                      <LabelContainer>
                        <Label>SMTP 포트:</Label>
                        <HelpIcon
                          onMouseEnter={() => handleTooltipShow('smtpPort')}
                          onMouseLeave={() => handleTooltipHide('smtpPort')}
                        >
                          <FiInfo size={14} />
                          <Tooltip show={tooltipStates.smtpPort}>
                            Gmail의 SMTP 포트 번호 (기본값: 587)
                          </Tooltip>
                        </HelpIcon>
                      </LabelContainer>
                      <InputField
                        type="number"
                        value={mailSettings.smtpPort}
                        onChange={(e) => handleMailSettingsChange('smtpPort', parseInt(e.target.value))}
                        placeholder="587"
                      />
                    </div>
                  )}
               </div>
              
              <VariableInfo>
                <h4>🔒 보안 안내:</h4>
                <ul>
                  <li>Gmail을 사용하는 경우 <strong>앱 비밀번호</strong>를 생성해야 합니다.</li>
                  <li>Google 계정 → 보안 → 2단계 인증 → 앱 비밀번호에서 생성 가능합니다.</li>
                  <li>일반 Gmail 비밀번호로는 로그인할 수 없습니다.</li>
                  <li>모든 설정 정보는 안전하게 암호화되어 저장됩니다.</li>
                </ul>
              </VariableInfo>

              <VariableInfo style={{marginTop: '16px', background: '#f0f9ff', borderLeft: '4px solid #3b82f6'}}>
                <h4>📧 메일 발송 테스트:</h4>
                <p>설정을 저장한 후 아래에서 테스트 메일을 발송해보세요.</p>
                <p><strong>현재 상태:</strong> {mailSettings.senderEmail ? '✅ 발송자 이메일 설정됨' : '❌ 발송자 이메일 미설정'}</p>
                
                <div style={{ marginTop: '16px', padding: '16px', background: 'white', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <LabelContainer>
                    <Label>테스트 이메일 주소:</Label>
                    <HelpIcon
                      onMouseEnter={() => handleTooltipShow('testEmail')}
                      onMouseLeave={() => handleTooltipHide('testEmail')}
                    >
                      <FiInfo size={14} />
                      <Tooltip show={tooltipStates.testEmail}>
                        테스트 메일을 받을 이메일 주소를 입력하세요
                      </Tooltip>
                    </HelpIcon>
                  </LabelContainer>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
                    <InputField
                      type="email"
                      value={testEmail}
                      onChange={(e) => setTestEmail(e.target.value)}
                      placeholder="test@example.com"
                      style={{ marginBottom: 0, flex: 1 }}
                    />
                    <SaveButton 
                      onClick={handleSendTestMail}
                      disabled={isSendingTest || !testEmail.trim()}
                      style={{ 
                        background: '#3b82f6', 
                        minWidth: '120px',
                        height: '44px'
                      }}
                    >
                      {isSendingTest ? '발송 중...' : '테스트 발송'}
                    </SaveButton>
                  </div>
                  <p style={{ marginTop: '8px', fontSize: '12px', color: '#6b7280' }}>
                    💡 테스트 메일에는 합격 안내 메일 양식이 사용됩니다.
                  </p>
                </div>
              </VariableInfo>
            </TemplateCard>
          </TabContent>
        </TabContainer>
      </Card>

      <Card>
        <h2><FiSettings /> 시스템 설정</h2>
        <p>AI 모델 파라미터, 알림 설정 등 시스템 관련 설정을 할 수 있습니다.</p>
      </Card>
      <Card>
        <h2><FiHelpCircle /> 도움말 / FAQ</h2>
        <p>자주 묻는 질문과 답변, 시스템 사용법 안내를 제공합니다.</p>
      </Card>
      <Card>
        <h2><FiMail /> 고객 지원 문의</h2>
        <p>고객 지원 문의를 남기거나, 지원팀에 연락할 수 있습니다.</p>
      </Card>
    </Container>
  );
}
export default Settings; 