import React from 'react';
import styled from 'styled-components';
import { FiSettings, FiHelpCircle, FiMail } from 'react-icons/fi';

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

function Settings() {
  return (
    <Container>
      <Title>설정 및 지원</Title>
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