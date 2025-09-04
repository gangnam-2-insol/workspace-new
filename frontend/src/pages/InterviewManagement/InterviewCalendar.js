import React, { useState, useEffect } from 'react';
import { FiChevronLeft, FiChevronRight, FiPlus, FiCalendar, FiClock, FiUser, FiSettings, FiX, FiCheckCircle, FiAlertCircle, FiMessageSquare } from 'react-icons/fi';
import './InterviewCalendar.css';
import CalendarScheduleModal from './components/CalendarScheduleModal';

// 서류 합격자 데이터 샘플 (InterviewManagement에서 가져옴)
const applicantsData = [
  {
    id: 1,
    name: '김철수',
    position: '프론트엔드 개발자',
    email: 'kim***@gmail.com',
    phone: '010-****-1234',
    interviewDate: '2024-01-20',
    interviewTime: '14:00',
    duration: '60분',
    status: 'scheduled',
    type: '대면',
    platform: '회사 면접실',
    aiScore: 85,
    documentStatus: 'pass',
    documents: {
      resume: { exists: true, summary: '', keywords: [], content: '' },
      portfolio: { exists: true, summary: '', keywords: [], content: '' },
      coverLetter: { exists: false, summary: '', keywords: [], content: '' }
    },
    questions: [],
    evaluation: {
      technicalScore: 0,
      communicationScore: 0,
      cultureScore: 0,
      overallScore: 0,
      memo: '',
      result: 'pending'
    },
    feedback: {
      sent: false,
      content: '',
      channel: 'email',
      sentAt: null
    }
  },
  {
    id: 2,
    name: '이영희',
    position: '백엔드 개발자',
    email: 'lee***@naver.com',
    phone: '010-****-5678',
    interviewDate: '2024-01-19',
    interviewTime: '15:30',
    duration: '90분',
    status: 'completed',
    type: '대면',
    platform: '회사 면접실',
    aiScore: 92,
    documentStatus: 'pass',
    documents: {
      resume: { exists: true, summary: '', keywords: [], content: '' },
      portfolio: { exists: true, summary: '', keywords: [], content: '' },
      coverLetter: { exists: true, summary: '', keywords: [], content: '' }
    },
    questions: [],
    evaluation: {
      technicalScore: 0,
      communicationScore: 0,
      cultureScore: 0,
      overallScore: 0,
      memo: '',
      result: 'pending'
    },
    feedback: {
      sent: false,
      content: '',
      channel: 'email',
      sentAt: null
    }
  },
  {
    id: 3,
    name: '박민수',
    position: 'UI/UX 디자이너',
    email: 'park***@daum.net',
    phone: '010-****-9012',
    interviewDate: '2024-01-21',
    interviewTime: '10:00',
    duration: '60분',
    status: 'in-progress',
    type: '대면',
    platform: '회사 면접실',
    aiScore: 78,
    documentStatus: 'pass',
    documents: {
      resume: { exists: true, summary: '', keywords: [], content: '' },
      portfolio: { exists: true, summary: '', keywords: [], content: '' },
      coverLetter: { exists: false, summary: '', keywords: [], content: '' }
    },
    questions: [],
    evaluation: {
      technicalScore: 0,
      communicationScore: 0,
      cultureScore: 0,
      overallScore: 0,
      memo: '',
      result: 'pending'
    },
    feedback: {
      sent: false,
      content: '',
      channel: 'email',
      sentAt: null
    }
  },
  {
    id: 4,
    name: '최지영',
    position: '데이터 분석가',
    email: 'choi***@gmail.com',
    phone: '010-****-3456',
    interviewDate: '2024-01-22',
    interviewTime: '16:00',
    duration: '60분',
    status: 'scheduled',
    type: '대면',
    platform: '회사 면접실',
    aiScore: 0,
    documentStatus: 'pass',
    documents: {
      resume: { exists: true, summary: '', keywords: [], content: '' },
      portfolio: { exists: false, summary: '', keywords: [], content: '' },
      coverLetter: { exists: true, summary: '', keywords: [], content: '' }
    },
    questions: [],
    evaluation: {
      technicalScore: 0,
      communicationScore: 0,
      cultureScore: 0,
      overallScore: 0,
      memo: '',
      result: 'pending'
    },
    feedback: {
      sent: false,
      content: '',
      channel: 'email',
      sentAt: null
    }
  }
];

const InterviewCalendar = () => {
  // 로컬 스토리지에서 데이터 로드 (InterviewManagement와 같은 키 사용)
  const loadApplicantsFromStorage = () => {
    try {
      const saved = localStorage.getItem('interviewManagement_applicants');
      return saved ? JSON.parse(saved) : applicantsData;
    } catch (error) {
      console.error('Failed to load data from localStorage:', error);
      return applicantsData;
    }
  };

  // 상태 관리
  const [applicants, setApplicants] = useState(loadApplicantsFromStorage);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [isCalendarScheduleModalOpen, setIsCalendarScheduleModalOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState('');
  const [newSchedule, setNewSchedule] = useState({
    name: '',
    position: '',
    email: '',
    phone: '',
    interviewDate: '',
    interviewTime: '',
    duration: '60분',
    type: '대면',
    platform: '회사 면접실'
  });
  const [notifications, setNotifications] = useState([]);

  // 데이터 변경 시 로컬 스토리지에 저장 (InterviewManagement와 같은 키 사용)
  useEffect(() => {
    try {
      localStorage.setItem('interviewManagement_applicants', JSON.stringify(applicants));
    } catch (error) {
      console.error('Failed to save data to localStorage:', error);
    }
  }, [applicants]);

  // localStorage 변경 감지하여 데이터 동기화
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'interviewManagement_applicants' && e.newValue) {
        try {
          const newData = JSON.parse(e.newValue);
          setApplicants(newData);
        } catch (error) {
          console.error('Failed to parse updated data:', error);
        }
      }
    };

      // 커스텀 이벤트 리스너 추가 (같은 탭에서의 변경 감지)
  const handleApplicantsUpdate = () => {
    try {
      const saved = localStorage.getItem('interviewManagement_applicants');
      if (saved) {
        const newData = JSON.parse(saved);
        console.log('Calendar: 데이터 업데이트 감지', newData.length, '명의 지원자');
        setApplicants(newData);
      }
    } catch (error) {
      console.error('Failed to load updated data:', error);
    }
  };

    // storage 이벤트 리스너 추가 (다른 탭에서의 변경 감지)
    window.addEventListener('storage', handleStorageChange);

    // 커스텀 이벤트 리스너 추가
    window.addEventListener('applicantsUpdated', handleApplicantsUpdate);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('applicantsUpdated', handleApplicantsUpdate);
    };
  }, []);

  // 캘린더 관련 유틸리티 함수들
  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const getInterviewsForDate = (dateStr) => {
    return applicants.filter(applicant => applicant.interviewDate === dateStr);
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const openCalendarScheduleModal = (dateStr) => {
    setSelectedDate(dateStr);
    setNewSchedule(prev => ({ ...prev, interviewDate: dateStr }));
    setIsCalendarScheduleModalOpen(true);
  };

  // 상태 텍스트 변환
  const getStatusText = (status) => {
    const statusMap = {
      scheduled: '예정됨',
      'in-progress': '진행중',
      completed: '완료',
      cancelled: '취소됨'
    };
    return statusMap[status] || status;
  };

  // 알림 시스템
  const showNotification = (message, type = 'success') => {
    const id = Date.now();
    const notification = { id, message, type };
    setNotifications(prev => [...prev, notification]);

    // 3초 후 자동 제거
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 3000);
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // 면접 일정 등록
  const createCalendarSchedule = () => {
    // 유효성 검사
    if (!newSchedule.name.trim()) {
      showNotification('지원자 이름을 입력해주세요.', 'error');
      return;
    }
    if (!newSchedule.position.trim()) {
      showNotification('지원 직무를 입력해주세요.', 'error');
      return;
    }
    if (!newSchedule.email.trim()) {
      showNotification('이메일을 입력해주세요.', 'error');
      return;
    }
    if (!newSchedule.phone.trim()) {
      showNotification('연락처를 입력해주세요.', 'error');
      return;
    }
    if (!newSchedule.interviewTime) {
        showNotification('면접 시간을 선택해주세요.', 'error');
        return;
      }

      // 새 지원자 생성
      const newApplicant = {
      id: Math.max(...applicants.map(a => a.id)) + 1,
        name: newSchedule.name,
        position: newSchedule.position,
        email: newSchedule.email,
        phone: newSchedule.phone,
        interviewDate: newSchedule.interviewDate,
      interviewTime: newSchedule.interviewTime,
        duration: newSchedule.duration,
        status: 'scheduled',
        type: newSchedule.type,
        platform: newSchedule.platform,
        aiScore: 0,
        documents: {
          resume: { exists: false, summary: '', keywords: [], content: '' },
          portfolio: { exists: false, summary: '', keywords: [], content: '' },
          coverLetter: { exists: false, summary: '', keywords: [], content: '' }
        },
        questions: [],
        evaluation: {
          technicalScore: 0,
          communicationScore: 0,
          cultureScore: 0,
          overallScore: 0,
          memo: '',
          result: 'pending'
        },
        feedback: {
          sent: false,
          content: '',
          channel: 'email',
          sentAt: null
        }
      };

      setApplicants(prev => [...prev, newApplicant]);
      setIsCalendarScheduleModalOpen(false);
      // 폼 초기화
      setNewSchedule({
        name: '',
        position: '',
        email: '',
        phone: '',
        interviewDate: '',
        interviewTime: '',
        duration: '60분',
        type: '대면',
        platform: '회사 면접실'
      });
      setSelectedDate('');
      showNotification('면접 일정이 성공적으로 등록되었습니다.');
    };

  // 통계 계산
  const stats = {
    scheduled: applicants.filter(a => a.status === 'scheduled').length,
    inProgress: applicants.filter(a => a.status === 'in-progress').length,
    completed: applicants.filter(a => a.status === 'completed').length,
    cancelled: applicants.filter(a => a.status === 'cancelled').length,
    total: applicants.length
  };

  return (
    <div className="interview-calendar">
      {/* 알림 토스트 */}
      <div className="notifications">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`notification ${notification.type}`}
            onClick={() => removeNotification(notification.id)}
          >
            <div className="notification-content">
              {notification.type === 'success' && <FiCheckCircle />}
              {notification.type === 'error' && <FiAlertCircle />}
              {notification.type === 'warning' && <FiAlertCircle />}
              {notification.type === 'info' && <FiMessageSquare />}
              <span>{notification.message}</span>
            </div>
            <button
              className="notification-close"
              onClick={(e) => {
                e.stopPropagation();
                removeNotification(notification.id);
              }}
            >
              <FiX />
            </button>
          </div>
        ))}
      </div>

      {/* 헤더 */}
      <div className="header">
        <h1>면접 캘린더</h1>
        <div className="header-actions">
          <div className="view-controls">
            <span>
              면접 일정 캘린더 뷰
            </span>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => openCalendarScheduleModal(formatDate(new Date()))}
          >
            <FiPlus />
            면접 일정 등록
          </button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">전체 면접</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.scheduled}</div>
          <div className="stat-label">예정된 면접</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.inProgress}</div>
          <div className="stat-label">진행중</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.completed}</div>
          <div className="stat-label">완료된 면접</div>
        </div>
      </div>

      {/* 캘린더 뷰 */}
      <div className="calendar-view">
        {/* 캘린더 헤더 */}
        <div className="calendar-header">
          <button
            className="btn btn-secondary"
            onClick={() => navigateMonth(-1)}
          >
            <FiChevronLeft />
          </button>
          <h2 className="calendar-title">
            {currentDate.getFullYear()}년 {currentDate.getMonth() + 1}월
          </h2>
          <button
            className="btn btn-secondary"
            onClick={() => navigateMonth(1)}
          >
            <FiChevronRight />
          </button>
        </div>

        {/* 요일 헤더 */}
        <div className="calendar-weekdays">
          {['일', '월', '화', '수', '목', '금', '토'].map(day => (
            <div key={day} className="weekday">{day}</div>
          ))}
        </div>

        {/* 캘린더 그리드 */}
        <div className="calendar-grid">
          {(() => {
            const daysInMonth = getDaysInMonth(currentDate);
            const firstDayOfMonth = getFirstDayOfMonth(currentDate);
            const days = [];

            // 이전 달의 빈 칸들
            for (let i = 0; i < firstDayOfMonth; i++) {
              days.push(
                <div key={`empty-${i}`} className="calendar-day empty"></div>
              );
            }

            // 현재 달의 날짜들
            for (let day = 1; day <= daysInMonth; day++) {
              const dateStr = formatDate(new Date(currentDate.getFullYear(), currentDate.getMonth(), day));
              const interviewsForDate = getInterviewsForDate(dateStr);
              const isToday = dateStr === formatDate(new Date());

              days.push(
                <div
                  key={day}
                  className={`calendar-day ${isToday ? 'today' : ''} ${interviewsForDate.length > 0 ? 'has-interviews' : ''}`}
                >
                  <div className="day-number">{day}</div>
                  {interviewsForDate.length > 0 && (
                    <div className="interviews-summary">
                      <div className="interview-count">
                        면접자 {interviewsForDate.length}명
                      </div>
                      <div className="interview-names">
                        {interviewsForDate.slice(0, 2).map((applicant, index) => (
                          <div key={applicant.id} className="interview-name">
                            <span className="time">{applicant.interviewTime}</span>
                            <span className="name">{applicant.name}</span>
                            <span className="position">({applicant.position})</span>
                          </div>
                        ))}
                        {interviewsForDate.length > 2 && (
                          <div className="more-interviews">
                            외 {interviewsForDate.length - 2}명 더...
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  <button
                    className="add-interview-btn"
                    onClick={() => openCalendarScheduleModal(dateStr)}
                    title="면접 일정 추가"
                  >
                    <FiPlus />
                  </button>
                </div>
              );
            }

            return days;
          })()}
        </div>
      </div>

      {/* 캘린더 면접 일정 등록 모달 */}
      <CalendarScheduleModal
        isOpen={isCalendarScheduleModalOpen}
        onClose={() => setIsCalendarScheduleModalOpen(false)}
        selectedDate={selectedDate}
        newSchedule={newSchedule}
        setNewSchedule={setNewSchedule}
        onSubmit={createCalendarSchedule}
        getInterviewsForDate={getInterviewsForDate}
        getStatusText={getStatusText}
        applicants={applicants}
      />
    </div>
  );
};

export default InterviewCalendar;
