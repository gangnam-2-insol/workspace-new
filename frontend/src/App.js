import React from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import JobPostingRegistration from './pages/JobPostingRegistration/JobPostingRegistration';
import ResumeManagement from './pages/ResumeManagement/ResumeManagement';
import ApplicantManagement from './pages/ApplicantManagement';
import InterviewManagement from './pages/InterviewManagement/InterviewManagement';
import InterviewCalendar from './pages/InterviewManagement/InterviewCalendar';
import PortfolioAnalysis from './pages/PortfolioAnalysis/PortfolioAnalysis';
import CoverLetterValidation from './pages/CoverLetterValidation/CoverLetterValidation';
import TalentRecommendation from './pages/TalentRecommendation/TalentRecommendation';
import UserManagement from './pages/UserManagement/UserManagement';
import Settings from './pages/Settings/Settings';
import TestGithubSummary from './pages/TestGithubSummary';
import PDFOCRPage from './pages/PDFOCRPage/PDFOCRPage';
import FloatingChatbot from './chatbot/components/FloatingChatbot';
import AITooltip from './components/AITooltip';



function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentPage = location.pathname.replace('/', '') || 'dashboard';

  // 전역 이벤트 리스너 추가 (디버깅용)
  React.useEffect(() => {
    const handleGlobalLangGraphDataUpdate = (event) => {
      console.log('[App.js] 🌍 전역 이벤트 수신:', event);
      console.log('[App.js] 🌍 이벤트 타입:', event.type);
      console.log('[App.js] 🌍 이벤트 상세:', event.detail);
    };

    console.log('[App.js] 전역 이벤트 리스너 등록: langGraphDataUpdate');
    window.addEventListener('langGraphDataUpdate', handleGlobalLangGraphDataUpdate);

    return () => {
      console.log('[App.js] 전역 이벤트 리스너 해제');
      window.removeEventListener('langGraphDataUpdate', handleGlobalLangGraphDataUpdate);
    };
  }, []);

  const handlePageAction = (action) => { // 이 함수는 'action'이라는 인자 하나만 받습니다.
    console.log('App.js에서 받은 페이지 액션:', action); // 디버깅을 위해 로그를 찍어보세요.

    // 챗봇에서 보낸 'changePage:' 액션 처리
    if (action.startsWith('changePage:')) {
      const targetPage = action.split(':')[1]; // 'job-posting' 추출
      console.log(`App.js가 페이지 이동 요청 수신: /${targetPage}`); // 이동 요청 로그
      console.log(`navigate 호출: /${targetPage}`); // 네비게이션 로그
      navigate(`/${targetPage}`); // 실제 페이지 이동
      console.log('페이지 이동 완료');
      return; // 페이지 이동 처리 후 함수 종료
    }

    // job-posting 페이지 액션 처리
    if (action === 'openRegistrationMethod') {
      // RegistrationMethodModal 열기
      const event = new CustomEvent('openRegistrationMethod');
      window.dispatchEvent(event);
    } else if (action === 'openTextRegistration') {
      // TextBasedRegistration 열기
      const event = new CustomEvent('openTextRegistration');
      window.dispatchEvent(event);
    } else if (action === 'openTextBasedRegistration') {
      // AI 도우미 모드로 시작
      const event = new CustomEvent('startAIAssistant');
      window.dispatchEvent(event);
    } else if (action === 'openImageRegistration') {
      // ImageBasedRegistration 열기
      const event = new CustomEvent('openImageRegistration');
      window.dispatchEvent(event);
    } else if (action === 'openImageBasedRegistration') {
      // ImageBasedRegistration 열기 (챗봇에서 호출)
      const event = new CustomEvent('openImageRegistration');
      window.dispatchEvent(event);
    } else if (action === 'openTemplateModal') {
      // TemplateModal 열기
      const event = new CustomEvent('openTemplateModal');
      window.dispatchEvent(event);
    } else if (action === 'openOrganizationModal') {
      // OrganizationModal 열기
      const event = new CustomEvent('openOrganizationModal');
      window.dispatchEvent(event);
    } else if (action === 'startTextBasedFlow') {
      // 텍스트 기반 플로우 시작
      const event = new CustomEvent('startTextBasedFlow');
      window.dispatchEvent(event);
    } else if (action === 'startImageBasedFlow') {
      // 이미지 기반 플로우 시작
      const event = new CustomEvent('startImageBasedFlow');
      window.dispatchEvent(event);
    } else if (action === 'startAIAssistant') {
      // AI 도우미 시작
      const event = new CustomEvent('startAIAssistant');
      window.dispatchEvent(event);
    } else if (action === 'cancelAutoProgress') {
      // 자동 진행 취소
      const event = new CustomEvent('cancelAutoProgress');
      window.dispatchEvent(event);
    } else if (action === 'autoUploadImage') {
      // 이미지 자동 업로드
      const event = new CustomEvent('autoUploadImage');
      window.dispatchEvent(event);
    } else if (action.startsWith('updateDepartment:')) {
      // 부서 업데이트
      const newDepartment = action.split(':')[1];
      const event = new CustomEvent('updateDepartment', {
        detail: { value: newDepartment }
      });
      window.dispatchEvent(event);
    } else if (action.startsWith('updateHeadcount:')) {
      // 인원 업데이트
      const newHeadcount = action.split(':')[1];
      const event = new CustomEvent('updateHeadcount', {
        detail: { value: newHeadcount }
      });
      window.dispatchEvent(event);
    } else if (action.startsWith('updateSalary:')) {
      // 급여 업데이트
      const newSalary = action.split(':')[1];
      const event = new CustomEvent('updateSalary', {
        detail: { value: newSalary }
      });
      window.dispatchEvent(event);
    } else if (action.startsWith('updateWorkContent:')) {
      // 업무 내용 업데이트
      const newWorkContent = action.split(':')[1];
      const event = new CustomEvent('updateWorkContent', {
        detail: { value: newWorkContent }
      });
      window.dispatchEvent(event);
    } else if (action === 'openLangGraphRegistration') {
      // 랭그래프모드용 채용공고등록도우미 열기
      const event = new CustomEvent('openLangGraphRegistration');
      window.dispatchEvent(event);
    }
  };

  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/job-posting" element={<JobPostingRegistration />} />
          <Route path="/resume" element={<ResumeManagement />} />
          <Route path="/applicants" element={<ApplicantManagement />} />
          <Route path="/interview" element={<InterviewManagement />} />
          <Route path="/interview-calendar" element={<InterviewCalendar />} />
          <Route path="/portfolio" element={<PortfolioAnalysis />} />
          <Route path="/cover-letter" element={<CoverLetterValidation />} />
          <Route path="/talent" element={<TalentRecommendation />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/github-test" element={<TestGithubSummary />} />
          <Route path="/pdf-ocr" element={<PDFOCRPage />} />
          <Route path="*" element={<div style={{ padding: '20px', textAlign: 'center' }}>페이지를 찾을 수 없습니다.</div>} />
        </Routes>
      </Layout>

      {/* AI 말풍선 컴포넌트 */}
      <AITooltip />

      {/* 챗봇 컴포넌트 */}
      <FloatingChatbot
        page={currentPage}
        onFieldUpdate={(field, value) => {
          console.log('챗봇 필드 업데이트:', field, value);
          
          // 실제 폼 필드 업데이트를 위한 이벤트 발생
          const event = new CustomEvent('updateFormField', {
            detail: { field, value }
          });
          window.dispatchEvent(event);
          
          // 추가로 개별 필드별 이벤트도 발생
          const fieldEvents = {
            'department': 'updateDepartment',
            'headcount': 'updateHeadcount', 
            'salary': 'updateSalary',
            'mainDuties': 'updateWorkContent',
            'workHours': 'updateWorkHours',
            'workDays': 'updateWorkDays',
            'locationCity': 'updateLocation',
            'contactEmail': 'updateContactEmail',
            'deadline': 'updateDeadline'
          };
          
          const eventName = fieldEvents[field];
          if (eventName) {
            const specificEvent = new CustomEvent(eventName, {
              detail: { value }
            });
            window.dispatchEvent(specificEvent);
          }
        }}
        onComplete={() => {
          console.log('챗봇 완료');
        }}
        onPageAction={handlePageAction}
      />
    </>
  );
}

export default App; 