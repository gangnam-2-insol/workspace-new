import React from 'react';
import { FiChevronLeft, FiChevronRight, FiPlus } from 'react-icons/fi';
import './CalendarView.css';

const InterviewCalendarView = ({
  currentDate,
  applicants,
  navigateMonth,
  openCalendarScheduleModal,
  getStatusText
}) => {
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

  return (
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
  );
};

export default InterviewCalendarView;
