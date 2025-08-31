import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import {
  FiEye,
  FiEdit,
  FiTrash2
} from 'react-icons/fi';
import DetailModal, {
  DetailSection,
  SectionTitle,
  DetailGrid,
  DetailItem,
  DetailLabel,
  DetailValue,
  DetailText,
  StatusBadge
} from '../../components/DetailModal/DetailModal';

const Container = styled.div`
  padding: 24px 0;
`;
const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
`;
const UserGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-top: 24px;
`;

const UserCard = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
  border: 1px solid var(--border-color);

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-medium);
  }
`;

const UserHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const UserInfo = styled.div`
  flex: 1;
`;

const UserName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
`;

const UserRole = styled.span`
  font-size: 14px;
  color: var(--text-secondary);
`;

// StatusBadge is imported from DetailModal

const UserDetails = styled.div`
  margin-bottom: 16px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
`;

// DetailLabel and DetailValue are imported from DetailModal

const UserActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`;

const ActionButton = styled.button`
  padding: 8px 12px;
  border: none;
  border-radius: var(--border-radius);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 4px;

  &.primary {
    background: var(--primary-color);
    color: white;
  }

  &.secondary {
    background: white;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
  }

  &.danger {
    background: #ef4444;
    color: white;
  }

  &:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-light);
  }
`;

// 샘플 사용자 데이터
const users = [
  {
    id: 1,
    name: '김관리',
    email: 'admin@hireme.com',
    role: '관리자',
    status: 'active',
    lastLogin: '2024-01-15 14:30',
    department: '인사팀',
    phone: '010-1234-5678',
    joinDate: '2023-01-15',
    permissions: ['사용자 관리', '데이터 분석', '시스템 설정']
  },
  {
    id: 2,
    name: '이채용',
    email: 'recruiter@hireme.com',
    role: '채용담당자',
    status: 'active',
    lastLogin: '2024-01-15 13:45',
    department: '채용팀',
    phone: '010-2345-6789',
    joinDate: '2023-03-20',
    permissions: ['이력서 관리', '인재 추천']
  },
  {
    id: 3,
    name: '박인사',
    email: 'hr@hireme.com',
    role: '인사담당자',
    status: 'active',
    lastLogin: '2024-01-15 12:20',
    department: '인사팀',
    phone: '010-3456-7890',
    joinDate: '2023-02-10',
    permissions: ['사용자 관리', '권한 관리', '보안 설정']
  },
  {
    id: 4,
    name: '최분석',
    email: 'analyst@hireme.com',
    role: '데이터분석가',
    status: 'inactive',
    lastLogin: '2024-01-10 09:15',
    department: '분석팀',
    phone: '010-4567-8901',
    joinDate: '2023-05-15',
    permissions: ['데이터 분석', '리포트 생성', '통계 조회']
  }
];

const getStatusText = (status) => {
  const statusMap = {
    active: '활성',
    inactive: '비활성',
    pending: '대기'
  };
  return statusMap[status] || status;
};

function UserManagement() {
  const [selectedUser, setSelectedUser] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  return (
    <Container>
      <Title>사용자 관리 및 보안</Title>

      <UserGrid>
        {users.map((user, index) => (
          <UserCard
            key={user.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <UserHeader>
              <UserInfo>
                <UserName>{user.name}</UserName>
                <UserRole>{user.role}</UserRole>
              </UserInfo>
              <StatusBadge className={user.status}>
                {getStatusText(user.status)}
              </StatusBadge>
            </UserHeader>

            <UserDetails>
              <DetailRow>
                <DetailLabel>이메일:</DetailLabel>
                <DetailValue>{user.email}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>부서:</DetailLabel>
                <DetailValue>{user.department}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>연락처:</DetailLabel>
                <DetailValue>{user.phone}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>최근 로그인:</DetailLabel>
                <DetailValue>{user.lastLogin}</DetailValue>
              </DetailRow>
            </UserDetails>

            <UserActions>
              <ActionButton onClick={() => {
                setSelectedUser(user);
                setIsDetailModalOpen(true);
              }}>
                <FiEye />
                상세보기
              </ActionButton>
              <ActionButton className="secondary">
                <FiEdit />
                수정
              </ActionButton>
              <ActionButton className="danger">
                <FiTrash2 />
                삭제
              </ActionButton>
            </UserActions>
          </UserCard>
        ))}
      </UserGrid>

      {/* 사용자 상세보기 모달 */}
      <DetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedUser(null);
        }}
        title={selectedUser ? `${selectedUser.name} 사용자 상세` : ''}
        onEdit={() => {
          // 수정 기능 구현
          console.log('사용자 수정:', selectedUser);
        }}
        onDelete={() => {
          // 삭제 기능 구현
          console.log('사용자 삭제:', selectedUser);
        }}
      >
        {selectedUser && (
          <>
            <DetailSection>
              <SectionTitle>기본 정보</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>이름</DetailLabel>
                  <DetailValue>{selectedUser.name}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>이메일</DetailLabel>
                  <DetailValue>{selectedUser.email}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>역할</DetailLabel>
                  <DetailValue>{selectedUser.role}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>부서</DetailLabel>
                  <DetailValue>{selectedUser.department}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>연락처</DetailLabel>
                  <DetailValue>{selectedUser.phone}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>가입일</DetailLabel>
                  <DetailValue>{selectedUser.joinDate}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>상태</DetailLabel>
                  <StatusBadge className={selectedUser.status}>
                    {getStatusText(selectedUser.status)}
                  </StatusBadge>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>최근 로그인</DetailLabel>
                  <DetailValue>{selectedUser.lastLogin}</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>권한 정보</SectionTitle>
              <DetailText>
                {selectedUser.permissions.map((permission, index) => (
                  <span key={index} style={{
                    display: 'inline-block',
                    margin: '4px',
                    padding: '4px 8px',
                    backgroundColor: '#dbeafe',
                    color: '#1e40af',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}>
                    {permission}
                  </span>
                ))}
              </DetailText>
            </DetailSection>
          </>
        )}
      </DetailModal>
    </Container>
  );
}
export default UserManagement;
