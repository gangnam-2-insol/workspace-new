import React, { Suspense } from 'react';
import { Routes, Route, useLocation, useNavigate, Navigate } from 'react-router-dom';
import Layout from './components/Layout/Layout';

import NewPickChatbot from './components/NewPickChatbot';

// 코드 스플리팅으로 지연 로딩
const Dashboard = React.lazy(() => import('./pages/Dashboard/Dashboard'));
const JobPostingRegistration = React.lazy(() => import('./pages/JobPostingRegistration/JobPostingRegistration'));
const AIJobRegistrationPage = React.lazy(() => import('./pages/JobPostingRegistration/AIJobRegistrationPage'));
const ResumeManagement = React.lazy(() => import('./pages/ResumeManagement/ResumeManagement'));
const ApplicantManagement = React.lazy(() => import('./pages/ApplicantManagement'));
const InterviewManagement = React.lazy(() => import('./pages/InterviewManagement/InterviewManagement'));
const InterviewCalendar = React.lazy(() => import('./pages/InterviewManagement/InterviewCalendar'));
const CoverLetterValidation = React.lazy(() => import('./pages/CoverLetterValidation/CoverLetterValidation'));
const TalentRecommendation = React.lazy(() => import('./pages/TalentRecommendation/TalentRecommendation'));
const UserManagement = React.lazy(() => import('./pages/UserManagement/UserManagement'));
const Settings = React.lazy(() => import('./pages/Settings/Settings'));
const SampleDataManagement = React.lazy(() => import('./pages/SampleDataManagement/SampleDataManagement'));
const TestGithubSummary = React.lazy(() => import('./pages/TestGithubSummary'));
const PDFOCRPage = React.lazy(() => import('./pages/PDFOCRPage/PDFOCRPage'));
const CompanyCultureManagement = React.lazy(() => import('./pages/CompanyCultureManagement/CompanyCultureManagement'));



function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentPage = location.pathname.replace('/', '') || 'dashboard';
  // 에이전트 챗봇 상태 제거됨

  // 픽톡 챗봇 상태 관리
  const [pickChatbotState, setPickChatbotState] = React.useState(() => {
    const savedState = sessionStorage.getItem('pickChatbotIsOpen');
    // 항상 플로팅 상태로 시작하거나, 저장된 상태가 true인 경우에만 true로 설정
    return savedState === 'true' ? true : 'floating';
  });

  // 전역 이벤트 리스너 추가 (디버깅용)
  React.useEffect(() => {
    const handleGlobalLangGraphDataUpdate = (event) => {
      console.log('[App.js] 🌍 전역 이벤트 수신:', event);
      console.log('[App.js] 🌍 이벤트 타입:', event.type);
      console.log('[App.js] 🌍 이벤트 상세:', event.detail);
    };

    console.log('[App.js] 전역 이벤트 리스너 등록: langGraphDataUpdate');
    window.addEventListener('langGraphDataUpdate', handleGlobalLangGraphDataUpdate);

    // 전역 handlePageAction 함수 노출
    window.handlePageAction = handlePageAction;

    return () => {
      console.log('[App.js] 전역 이벤트 리스너 해제');
      window.removeEventListener('langGraphDataUpdate', handleGlobalLangGraphDataUpdate);
      delete window.handlePageAction;
    };
  }, []);

  // 에이전트 챗봇 이벤트 리스너 제거됨

  const handlePageAction = (action) => { // 이 함수는 'action'이라는 인자 하나만 받습니다.
    console.log('🎯 [App.js] 페이지 액션 수신:', action); // 디버깅을 위해 로그를 찍어보세요.

    // 챗봇에서 보낸 'changePage:' 액션 처리
    if (action.startsWith('changePage:')) {
      const targetPage = action.split(':')[1]; // 'job-posting' 추출
      console.log(`🎯 [App.js] 페이지 이동 요청 수신: /${targetPage}`); // 이동 요청 로그
      console.log(`🎯 [App.js] navigate 호출: /${targetPage}`); // 네비게이션 로그
      navigate(`/${targetPage}`); // 실제 페이지 이동
      console.log('🎯 [App.js] 페이지 이동 완료');
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
    } else if (action === 'openAIJobRegistration') {
      // AI 채용공고 등록 페이지로 이동
      navigate('/ai-job-registration');
    }
  };

  return (
    <>
      <Layout>
        <Suspense fallback={<div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/job-posting" element={<JobPostingRegistration />} />
            <Route path="/ai-job-registration" element={<AIJobRegistrationPage />} />
            <Route path="/resume" element={<ResumeManagement />} />
            <Route path="/applicants" element={<ApplicantManagement />} />
            <Route path="/interview" element={<InterviewManagement />} />
            <Route path="/interview-calendar" element={<InterviewCalendar />} />
            <Route path="/portfolio" element={<Navigate to="/github-test" replace />} />
            <Route path="/cover-letter" element={<CoverLetterValidation />} />
            <Route path="/talent" element={<TalentRecommendation />} />
            <Route path="/users" element={<UserManagement />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/sample-data" element={<SampleDataManagement />} />
            <Route path="/company-culture" element={<CompanyCultureManagement />} />
            <Route path="/github-test" element={<TestGithubSummary />} />
            <Route path="/pdf-ocr" element={<PDFOCRPage />} />
            <Route path="*" element={<div style={{ padding: '20px', textAlign: 'center' }}>페이지를 찾을 수 없습니다.</div>} />
          </Routes>
        </Suspense>
      </Layout>



      {/* 챗봇 컴포넌트 제거됨 */}

      {/* 픽톡 챗봇 */}
      <NewPickChatbot
        isOpen={pickChatbotState}
        onOpenChange={(newState) => {
          setPickChatbotState(newState);
          sessionStorage.setItem('pickChatbotIsOpen', newState ? 'true' : (newState === 'floating' ? 'floating' : 'false'));
        }}
      />
    </>
  );
}

export default App;
