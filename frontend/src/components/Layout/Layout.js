import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
	FiHome, 
	FiFileText, 
	FiVideo, 
	FiCalendar,
	FiCode, 
	FiEdit3, 
	FiUsers, 
	FiUser, 
	FiSettings,
	FiDatabase,
	FiMenu,
	FiX,
	FiBell,
	FiSearch,
	FiBriefcase,
	FiUserCheck,
	FiGitBranch,
	FiMessageCircle
} from 'react-icons/fi';

const LayoutContainer = styled.div`
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const Sidebar = styled(motion.div)`
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  padding: 24px 0;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: 1000;

  @media (max-width: 768px) {
    transform: translateX(${props => props.$isOpen ? '0' : '-100%'});
    width: 100%;
    transition: transform 0.3s ease;
  }
`;

const MainContent = styled.div`
  flex: 1;
  margin-left: 280px;
  min-height: 100vh;
  background: var(--background-secondary);

  @media (max-width: 768px) {
    margin-left: 0;
  }
`;

const Header = styled.header`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Logo = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 12px;
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const IconButton = styled.button`
  background: none;
  border: none;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const MobileMenuButton = styled(IconButton)`
  display: none;
  
  @media (max-width: 768px) {
    display: flex;
  }
`;

const Content = styled.main`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const NavItem = styled(Link)`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: var(--transition);
  border-left: 3px solid transparent;
  font-weight: 500;

  &:hover {
    background: rgba(0, 200, 81, 0.1);
    color: var(--primary-color);
    border-left-color: var(--primary-color);
  }

  &.active {
    background: rgba(0, 200, 81, 0.1);
    color: var(--primary-color);
    border-left-color: var(--primary-color);
  }
`;

const NavSection = styled.div`
  margin-bottom: 32px;
`;

const NavSectionTitle = styled.h3`
  font-size: 12px;
  font-weight: 600;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 24px 12px;
`;

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: none;

  @media (max-width: 768px) {
    display: ${props => props.$isOpen ? 'block' : 'none'};
  }
`;

const navigationItems = [
  {
    title: '메인',
    items: [
      { name: '대시보드', path: '/', icon: FiHome }
    ]
  },
  {
    title: '채용 관리',
    items: [
      { name: '채용공고 등록', path: '/job-posting', icon: FiBriefcase },
      { name: '지원자 관리', path: '/applicants', icon: FiUserCheck },
    ]
  },
  {
    title: '시스템',
    items: [
      { name: '설정 및 지원', path: '/settings', icon: FiSettings },
      { name: '샘플 데이터 관리', path: '/sample-data', icon: FiDatabase }
    ]
  },
  {
    title: '개발 도구',
    items: [
      { name: 'GitHub 테스트', path: '/github-test', icon: FiGitBranch }
    ]
  }
];

const Layout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const location = useLocation();

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <LayoutContainer>
      <Overlay $isOpen={isSidebarOpen} onClick={toggleSidebar} />
      <Sidebar
        initial={{ x: -280 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.3 }}
        $isOpen={isSidebarOpen}
      >
        <div style={{ padding: '0 24px 24px' }}>
          <Logo>
            <div style={{ 
              width: '32px', 
              height: '32px', 
              background: 'linear-gradient(135deg, #00c851, #00a844)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '18px',
              fontWeight: 'bold'
            }}>
              AI
            </div>
            AI 채용 관리
          </Logo>
        </div>

        <nav>
          {navigationItems.map((section, index) => (
            <NavSection key={index}>
              <NavSectionTitle>{section.title}</NavSectionTitle>
              {section.items.map((item, itemIndex) => {
                const Icon = item.icon;
                return (
                  <NavItem
                    key={itemIndex}
                    to={item.path}
                    className={location.pathname === item.path ? 'active' : ''}
                    onClick={() => setIsSidebarOpen(false)}
                  >
                    <Icon size={20} />
                    {item.name}
                  </NavItem>
                );
              })}
            </NavSection>
          ))}
        </nav>
      </Sidebar>

      <MainContent>
        <Header>
          <MobileMenuButton onClick={toggleSidebar}>
            {isSidebarOpen ? <FiX size={24} /> : <FiMenu size={24} />}
          </MobileMenuButton>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <IconButton>
              <FiSearch size={20} />
            </IconButton>
            <IconButton>
              <FiBell size={20} />
            </IconButton>
				<IconButton title="에이전트 챗봇" onClick={() => window.dispatchEvent(new Event('openAgentChatbot'))}>
					<FiMessageCircle size={20} />
				</IconButton>
				<IconButton title="픽톡 챗봇" onClick={() => {
					sessionStorage.setItem('pickChatbotIsOpen', 'true');
					window.location.reload();
				}}>
					💬
				</IconButton>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #00c851, #00a844)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 'bold'
            }}>
              A
            </div>
          </div>
        </Header>

        <Content>
          {children}
        </Content>
      </MainContent>
    </LayoutContainer>
  );
};

export default Layout; 