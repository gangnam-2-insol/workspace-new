import React, { useState } from 'react';
import styled from 'styled-components';
import EnhancedModalChatbot from '../../chatbot/components/EnhancedModalChatbot';
import LangGraphJobRegistration from '../JobPostingRegistration/LangGraphJobRegistration';

const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  color: #1f2937;
  font-size: 2.5rem;
  margin-bottom: 16px;
`;

const Subtitle = styled.p`
  color: #6b7280;
  font-size: 1.1rem;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
`;

const DemoSection = styled.div`
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 30px 0;
`;

const FeatureCard = styled.div`
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
`;

const FeatureTitle = styled.h3`
  color: #1f2937;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FeatureDescription = styled.p`
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
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

const ConversationExample = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
`;

const Message = styled.div`
  margin-bottom: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 80%;
  
  ${props => props.type === 'user' ? `
    background: #3b82f6;
    color: white;
    margin-left: auto;
  ` : `
    background: white;
    color: #1f2937;
    border: 1px solid #e5e7eb;
  `}
`;

const ConversationalAIDemo = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLangGraphModalOpen, setIsLangGraphModalOpen] = useState(false);
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
    setFormData(prev => ({
      ...prev,
      [fieldKey]: value
    }));
  };

  const handleComplete = () => {
    console.log('모든 필드 입력 완료:', formData);
    alert('채용공고 등록이 완료되었습니다!');
    setIsModalOpen(false);
  };

  const handleInputChange = (fieldKey, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldKey]: value
    }));
  };

  const handlePageAction = (action, data) => {
    if (action === 'openLangGraphRegistration') {
      setIsLangGraphModalOpen(true);
    } else if (action === 'updateLangGraphData') {
      // LangGraph 데이터 업데이트 이벤트 발생
      window.dispatchEvent(new CustomEvent('langGraphDataUpdate', {
        detail: { action, data }
      }));
    }
  };

  return (
    <Container>
      <Header>
        <Title>🤖 대화형 AI 어시스턴트 데모</Title>
        <Subtitle>
          별도의 AI 창을 열지 않고 모달 내에서 직접 대화형으로 질문하고 답변을 받는 
          혁신적인 채용공고 등록 시스템을 체험해보세요.
        </Subtitle>
      </Header>

      <DemoSection>
        <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>
          ✨ 주요 특징
        </h2>
        
        <FeatureGrid>
          <FeatureCard>
            <FeatureTitle>
              💬 대화형 질문-답변
            </FeatureTitle>
            <FeatureDescription>
              AI 창을 따로 열지 않고 모달 내에서 직접 궁금한 점을 물어보고 
              상세한 답변을 받을 수 있습니다.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureTitle>
              ⚡ 빠른 질문 버튼
            </FeatureTitle>
            <FeatureDescription>
              자주 묻는 질문들을 버튼으로 제공하여 클릭 한 번으로 
              즉시 답변을 받을 수 있습니다.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureTitle>
              🔄 실시간 동기화
            </FeatureTitle>
            <FeatureDescription>
              AI와의 대화 내용이 실시간으로 폼에 반영되어 
              입력 진행 상황을 즉시 확인할 수 있습니다.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureTitle>
              🎯 컨텍스트 인식
            </FeatureTitle>
            <FeatureDescription>
              이전 입력값을 고려한 맞춤형 질문과 답변을 제공하여 
              더 정확하고 유용한 정보를 얻을 수 있습니다.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureTitle>
              📝 자동 입력 제안
            </FeatureTitle>
            <FeatureDescription>
              AI가 추천하는 답변을 클릭 한 번으로 
              자동으로 폼에 입력할 수 있습니다.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureTitle>
              🔄 유연한 입력 방식
            </FeatureTitle>
            <FeatureDescription>
              직접 폼에 입력하거나 AI와 대화하거나, 
              두 방식을 자유롭게 전환하며 사용할 수 있습니다.
            </FeatureDescription>
          </FeatureCard>
        </FeatureGrid>
      </DemoSection>

      <DemoSection>
        <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>
          💡 대화 예시
        </h2>
        
        <ConversationExample>
          <Message type="bot">
            안녕하세요! 채용공고 등록 작성을 도와드리겠습니다. 🤖
            <br /><br />
            먼저 구인 부서에 대해 알려주세요.
          </Message>
          
          <Message type="user">
            개발팀은 어떤 업무를 하나요?
          </Message>
          
          <Message type="bot">
            개발팀은 주로 웹/앱 개발, 시스템 구축, 기술 지원 등을 담당합니다. 
            프론트엔드, 백엔드, 풀스택 개발자로 구성되어 있으며, 
            최신 기술 트렌드를 반영한 개발을 진행합니다.
          </Message>
          
          <Message type="user">
            그럼 개발팀으로 하겠습니다.
          </Message>
          
          <Message type="bot">
            개발팀으로 입력하겠습니다. 
            <br /><br />
            이제 채용 인원은 몇 명인가요?
          </Message>
        </ConversationExample>
      </DemoSection>

      <DemoSection>
        <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>
          🚀 체험해보기
        </h2>
        
        <p style={{ color: '#6b7280', marginBottom: '20px' }}>
          아래 버튼을 클릭하여 실제 대화형 AI 어시스턴트를 체험해보세요.
          궁금한 점이 있으면 언제든지 물어보실 수 있습니다!
        </p>
        
        <Button onClick={() => setIsModalOpen(true)}>
          🤖 대화형 AI 어시스턴트 시작하기
        </Button>
      </DemoSection>

      <EnhancedModalChatbot
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="채용공고 등록"
        fields={fields}
        onFieldUpdate={handleFieldUpdate}
        onComplete={handleComplete}
        onPageAction={handlePageAction}
        aiAssistant={true}
      >
        <div style={{ display: 'grid', gap: '20px' }}>
          {/* 부서 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              구인 부서 *
            </label>
            <input
              type="text"
              value={formData.department}
              onChange={(e) => handleInputChange('department', e.target.value)}
              placeholder="예: 개발팀, 마케팅팀, 영업팀"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                transition: 'border-color 0.3s ease'
              }}
            />
          </div>

          {/* 채용 인원 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              채용 인원 *
            </label>
            <select
              value={formData.headcount}
              onChange={(e) => handleInputChange('headcount', e.target.value)}
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                background: 'white'
              }}
            >
              <option value="">선택해주세요</option>
              <option value="1명">1명</option>
              <option value="2명">2명</option>
              <option value="3명">3명</option>
              <option value="5명">5명</option>
              <option value="10명">10명</option>
            </select>
          </div>

          {/* 업무 내용 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              업무 내용 *
            </label>
            <input
              type="text"
              value={formData.workType}
              onChange={(e) => handleInputChange('workType', e.target.value)}
              placeholder="예: 웹 개발, 앱 개발, 디자인"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px'
              }}
            />
          </div>

          {/* 근무 시간 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              근무 시간 *
            </label>
            <select
              value={formData.workHours}
              onChange={(e) => handleInputChange('workHours', e.target.value)}
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                background: 'white'
              }}
            >
              <option value="">선택해주세요</option>
              <option value="09:00-18:00">09:00-18:00</option>
              <option value="10:00-19:00">10:00-19:00</option>
              <option value="유연근무제">유연근무제</option>
            </select>
          </div>

          {/* 근무 위치 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              근무 위치 *
            </label>
            <select
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                background: 'white'
              }}
            >
              <option value="">선택해주세요</option>
              <option value="서울">서울</option>
              <option value="부산">부산</option>
              <option value="대구">대구</option>
              <option value="인천">인천</option>
              <option value="대전">대전</option>
              <option value="원격근무">원격근무</option>
            </select>
          </div>

          {/* 급여 조건 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              급여 조건 *
            </label>
            <input
              type="text"
              value={formData.salary}
              onChange={(e) => handleInputChange('salary', e.target.value)}
              placeholder="예: 면접 후 협의, 3000만원"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px'
              }}
            />
          </div>

          {/* 마감일 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              마감일 *
            </label>
            <input
              type="text"
              value={formData.deadline}
              onChange={(e) => handleInputChange('deadline', e.target.value)}
              placeholder="예: 2024년 12월 31일"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px'
              }}
            />
          </div>

          {/* 연락처 이메일 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              연락처 이메일 *
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              placeholder="예: hr@company.com"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px'
              }}
            />
          </div>

          {/* 자격 요건 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              자격 요건
            </label>
            <textarea
              value={formData.requirements}
              onChange={(e) => handleInputChange('requirements', e.target.value)}
              placeholder="필요한 자격, 경력, 기술 스택 등을 입력해주세요"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                resize: 'vertical',
                minHeight: '100px'
              }}
            />
          </div>

          {/* 복리후생 */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151' }}>
              복리후생
            </label>
            <textarea
              value={formData.benefits}
              onChange={(e) => handleInputChange('benefits', e.target.value)}
              placeholder="제공되는 복리후생을 입력해주세요"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                resize: 'vertical',
                minHeight: '100px'
              }}
            />
          </div>

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

      {/* LangGraph 채용공고 등록 페이지 */}
      <LangGraphJobRegistration
        isOpen={isLangGraphModalOpen}
        onClose={() => setIsLangGraphModalOpen(false)}
        initialData={formData}
      />
    </Container>
  );
};

export default ConversationalAIDemo; 