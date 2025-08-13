import React, { useState } from 'react';
import styled from 'styled-components';
import EnhancedModalChatbot from '../../chatbot/components/EnhancedModalChatbot';
import AIChatbotService from '../../services/AIChatbotService';

const Container = styled.div`
  padding: 20px;
  
  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;

const Button = styled.button`
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
`;

const FormField = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #374151;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const EnhancedJobRegistration = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    department: '',
    headcount: '',
    workType: '',
    workHours: '',
    location: '',
    salary: '',
    deadline: '',
    email: '',
    requirements: '',
    benefits: ''
  });
  
  // AI 어시스턴트로 입력된 필드 추적
  const [aiFilledFields, setAiFilledFields] = useState({});
  
  // 실시간 알림 토스트 상태
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  
  // AI 필드 업데이트 이벤트 리스너
  useEffect(() => {
    const handleAIFieldUpdate = (event) => {
      const { field, value, fieldName } = event.detail;
      console.log(`AI 필드 업데이트 이벤트 수신: ${fieldName} = ${value}`);
      
      // 토스트 알림 표시
      setToastMessage(`${fieldName}에 "${value}"이(가) 입력되었습니다!`);
      setShowToast(true);
      
      // 3초 후 토스트 숨기기
      setTimeout(() => {
        setShowToast(false);
      }, 3000);
      
      // 필드 요소에 시각적 피드백 추가
      const fieldElement = document.querySelector(`[name="${field}"]`);
      if (fieldElement) {
        // 애니메이션 효과 추가
        fieldElement.style.transition = 'all 0.3s ease';
        fieldElement.style.borderColor = '#667eea';
        fieldElement.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.2)';
        fieldElement.style.transform = 'scale(1.02)';
        
        // 3초 후 원래 스타일로 복원
        setTimeout(() => {
          fieldElement.style.borderColor = '#e5e7eb';
          fieldElement.style.boxShadow = 'none';
          fieldElement.style.transform = 'scale(1)';
        }, 3000);
      }
    };
    
    window.addEventListener('aiFieldUpdated', handleAIFieldUpdate);
    
    return () => {
      window.removeEventListener('aiFieldUpdated', handleAIFieldUpdate);
    };
  }, []);

  // 필드 정의
  const fields = [
    { key: 'department', label: '구인 부서', type: 'text' },
    { key: 'headcount', label: '채용 인원', type: 'text' },
    { key: 'workType', label: '업무 내용', type: 'text' },
    { key: 'workHours', label: '근무 시간', type: 'text' },
    { key: 'location', label: '근무 위치', type: 'text' },
    { key: 'salary', label: '급여 조건', type: 'text' },
    { key: 'deadline', label: '마감일', type: 'text' },
    { key: 'email', label: '연락처 이메일', type: 'email' },
    { key: 'requirements', label: '자격 요건', type: 'textarea' },
    { key: 'benefits', label: '복리후생', type: 'textarea' }
  ];

  const handleFieldUpdate = (fieldKey, value) => {
    console.log('AI 어시스턴트를 통한 필드 업데이트:', fieldKey, value);
    setFormData(prev => ({
      ...prev,
      [fieldKey]: value
    }));
    
    // AI 어시스턴트로 입력된 필드 추적
    setAiFilledFields(prev => ({
      ...prev,
      [fieldKey]: true
    }));
    
    // 필드가 업데이트되었음을 시각적으로 표시
    const fieldElement = document.querySelector(`[name="${fieldKey}"]`);
    if (fieldElement) {
      fieldElement.style.borderColor = '#667eea';
      fieldElement.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.2)';
      
      // 3초 후 원래 스타일로 복원
      setTimeout(() => {
        fieldElement.style.borderColor = '#e5e7eb';
        fieldElement.style.boxShadow = 'none';
      }, 3000);
    }
  };

  const handleComplete = () => {
    console.log('모든 필드 입력 완료:', formData);
    // 여기서 실제 제출 로직 구현
    alert('채용공고 등록이 완료되었습니다!');
    setIsModalOpen(false);
  };

  const handleInputChange = (fieldKey, value) => {
    // 급여 필드에 대한 특별 처리
    if (fieldKey === 'salary') {
      // 입력값에서 숫자만 추출 (콤마 포함)
      const numericValue = value.replace(/[^\d,]/g, '');
      
      setFormData(prev => ({
        ...prev,
        [fieldKey]: numericValue
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [fieldKey]: value
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
    if (/^\d+([,\d]*)?$/.test(salaryValue.trim())) {
      return `${salaryValue}만원`;
    }
    
    return salaryValue;
  };

  return (
    <Container>
      {/* 실시간 알림 토스트 */}
      {showToast && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '16px 20px',
          borderRadius: '8px',
          boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)',
          zIndex: 1000,
          animation: 'slideInRight 0.3s ease',
          maxWidth: '300px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '18px' }}>🤖</span>
            <span style={{ fontSize: '14px', fontWeight: '600' }}>{toastMessage}</span>
          </div>
        </div>
      )}
      
      <h1 style={{ marginBottom: '30px', color: '#1f2937' }}>
        AI 어시스턴트와 함께하는 채용공고 등록
      </h1>
      
      <div style={{ marginBottom: '30px' }}>
        <p style={{ color: '#6b7280', lineHeight: '1.6' }}>
          AI 어시스턴트가 채용공고 작성을 도와드립니다. 
          오른쪽 채팅창에서 AI와 대화하면서 정보를 입력하거나, 
          직접 폼에 입력하실 수 있습니다.
        </p>
        
        {/* AI 입력 진행률 표시 */}
        {Object.keys(aiFilledFields).length > 0 && (
          <div style={{ 
            marginTop: '15px', 
            padding: '12px', 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
            borderRadius: '8px',
            color: 'white'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600' }}>
                🤖 AI 어시스턴트 입력 진행률
              </span>
              <span style={{ fontSize: '12px', opacity: 0.9 }}>
                {Object.keys(aiFilledFields).length} / {fields.length} 필드 완료
              </span>
            </div>
            <div style={{ 
              width: '100%', 
              height: '6px', 
              background: 'rgba(255, 255, 255, 0.2)', 
              borderRadius: '3px',
              overflow: 'hidden'
            }}>
              <div style={{ 
                width: `${(Object.keys(aiFilledFields).length / fields.length) * 100}%`, 
                height: '100%', 
                background: 'rgba(255, 255, 255, 0.8)', 
                borderRadius: '3px',
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>
        )}
      </div>

      <Button onClick={() => setIsModalOpen(true)}>
        🤖 AI 어시스턴트와 함께 시작하기
      </Button>

      <EnhancedModalChatbot
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="채용공고 등록"
        fields={fields}
        onFieldUpdate={handleFieldUpdate}
        onComplete={handleComplete}
        aiAssistant={true}
        key={isModalOpen ? 'open' : 'closed'} // 모달 상태에 따른 키 변경으로 상태 초기화 방지
      >
        <div style={{ display: 'grid', gap: '20px' }}>
          {/* 부서 */}
          <FormField>
            <Label>
              구인 부서 *
              {aiFilledFields.department && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <Input
              name="department"
              type="text"
              value={formData.department}
              onChange={(e) => handleInputChange('department', e.target.value)}
              placeholder="예: 개발팀, 마케팅팀, 영업팀"
            />
          </FormField>

          {/* 채용 인원 */}
          <FormField>
            <Label>
              채용 인원 *
              {aiFilledFields.headcount && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <Select
              name="headcount"
              value={formData.headcount}
              onChange={(e) => handleInputChange('headcount', e.target.value)}
            >
              <option value="">선택해주세요</option>
              <option value="1명">1명</option>
              <option value="2명">2명</option>
              <option value="3명">3명</option>
              <option value="5명">5명</option>
              <option value="10명">10명</option>
            </Select>
          </FormField>

          {/* 업무 내용 */}
          <FormField>
            <Label>
              업무 내용 *
              {aiFilledFields.workType && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <Input
              name="workType"
              type="text"
              value={formData.workType}
              onChange={(e) => handleInputChange('workType', e.target.value)}
              placeholder="예: 웹 개발, 앱 개발, 디자인"
            />
          </FormField>

          {/* 근무 시간 */}
          <FormField>
            <Label>
              근무 시간 *
              {aiFilledFields.workHours && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <Select
              name="workHours"
              value={formData.workHours}
              onChange={(e) => handleInputChange('workHours', e.target.value)}
            >
              <option value="">선택해주세요</option>
              <option value="09:00-18:00">09:00-18:00</option>
              <option value="10:00-19:00">10:00-19:00</option>
              <option value="유연근무제">유연근무제</option>
            </Select>
          </FormField>

          {/* 근무 위치 */}
          <FormField>
            <Label>
              근무 위치 *
              {aiFilledFields.location && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <Select
              name="location"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
            >
              <option value="">선택해주세요</option>
              <option value="서울">서울</option>
              <option value="부산">부산</option>
              <option value="대구">대구</option>
              <option value="인천">인천</option>
              <option value="대전">대전</option>
              <option value="원격근무">원격근무</option>
            </Select>
          </FormField>

          {/* 급여 조건 */}
          <FormField>
            <Label>
              급여 조건 *
              {aiFilledFields.salary && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <div style={{ position: 'relative' }}>
              <Input
                name="salary"
                type="text"
                value={formData.salary}
                onChange={(e) => handleInputChange('salary', e.target.value)}
                placeholder="예: 3000, 4000~5000, 면접 후 협의"
                style={{ paddingRight: '50px' }}
              />
              {formData.salary && /^\d+([,\d]*)?$/.test(formData.salary.trim()) && (
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
          </FormField>

          {/* 마감일 */}
          <FormField>
            <Label>
              마감일 *
              {aiFilledFields.deadline && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <Input
              name="deadline"
              type="text"
              value={formData.deadline}
              onChange={(e) => handleInputChange('deadline', e.target.value)}
              placeholder="예: 2024년 12월 31일"
            />
          </FormField>

          {/* 연락처 이메일 */}
          <FormField>
            <Label>
              연락처 이메일 *
              {aiFilledFields.email && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <Input
              name="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              placeholder="예: hr@company.com"
            />
          </FormField>

          {/* 자격 요건 */}
          <FormField>
            <Label>
              자격 요건
              {aiFilledFields.requirements && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <TextArea
              name="requirements"
              value={formData.requirements}
              onChange={(e) => handleInputChange('requirements', e.target.value)}
              placeholder="필요한 자격, 경력, 기술 스택 등을 입력해주세요"
            />
          </FormField>

          {/* 복리후생 */}
          <FormField>
            <Label>
              복리후생
              {aiFilledFields.benefits && (
                <span style={{ 
                  marginLeft: '8px', 
                  color: '#667eea', 
                  fontSize: '12px',
                  fontWeight: 'normal'
                }}>
                  🤖 AI 입력됨
                </span>
              )}
            </Label>
            <TextArea
              name="benefits"
              value={formData.benefits}
              onChange={(e) => handleInputChange('benefits', e.target.value)}
              placeholder="제공되는 복리후생을 입력해주세요"
            />
          </FormField>

          {/* AI 입력 요약 */}
          {Object.keys(aiFilledFields).length > 0 && (
            <div style={{ 
              marginTop: '20px', 
              padding: '16px', 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
              borderRadius: '8px',
              color: 'white'
            }}>
              <h4 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>
                🤖 AI 어시스턴트 입력 완료 항목
              </h4>
              <div style={{ fontSize: '14px', opacity: 0.9 }}>
                {Object.keys(aiFilledFields).map(fieldKey => {
                  const fieldLabel = fields.find(f => f.key === fieldKey)?.label || fieldKey;
                  return (
                    <div key={fieldKey} style={{ marginBottom: '4px' }}>
                      ✅ {fieldLabel}: {formData[fieldKey]}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* 완료 버튼 */}
          <div style={{ 
            marginTop: '30px', 
            padding: '20px', 
            background: '#f8fafc', 
            borderRadius: '8px',
            border: '1px solid #e5e7eb'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#1f2937' }}>
              📋 입력 완료 확인
            </h3>
            <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
              모든 필수 항목이 입력되었는지 확인 후 완료 버튼을 눌러주세요.
            </p>
            <Button 
              onClick={handleComplete}
              style={{ 
                marginTop: '15px',
                background: 'linear-gradient(135deg, #10b981, #059669)'
              }}
            >
              ✅ 채용공고 등록 완료
            </Button>
          </div>
        </div>
      </EnhancedModalChatbot>
    </Container>
  );
};

export default EnhancedJobRegistration; 