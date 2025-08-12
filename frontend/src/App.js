import React from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import JobPostingRegistration from './pages/JobPostingRegistration/JobPostingRegistration';
import ApplicantManagement from './pages/ApplicantManagement';
// import InterviewManagement from './pages/InterviewManagement/InterviewManagement';
// import InterviewCalendar from './pages/InterviewManagement/InterviewCalendar';

import UserManagement from './pages/UserManagement/UserManagement';
import Settings from './pages/Settings/Settings';
import FloatingChatbot from './components/FloatingChatbot';

function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentPage = location.pathname.replace('/', '') || 'dashboard';

  const handlePageAction = (action) => { // 이 함수는 'action'이라는 인자 하나만 받습니다.
    console.log('App.js에서 받은 페이지 액션:', action); // 디버깅을 위해 로그를 찍어보세요.

    // 챗봇에서 보낸 'changePage:' 액션 처리
    if (action.startsWith('changePage:')) {
      const targetPage = action.split(':')[1]; // 'job-posting' 추출
      console.log(`App.js가 페이지 이동 요청 수신: /${targetPage}`); // 이동 요청 로그
      navigate(`/${targetPage}`); // 실제 페이지 이동
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
    }
  };

  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/job-posting" element={<JobPostingRegistration />} />
          <Route path="/applicants" element={<ApplicantManagement />} />
          {/* <Route path="/interview" element={<InterviewManagement />} /> */}
          {/* <Route path="/interview-calendar" element={<InterviewCalendar />} /> */}

          <Route path="/users" element={<UserManagement />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>

      {/* 챗봇 컴포넌트 */}
      <FloatingChatbot
        page={currentPage}
        onFieldUpdate={(field, value) => {
          console.log('챗봇 필드 업데이트:', field, value);
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