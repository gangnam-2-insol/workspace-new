import React from 'react';
import { FiX, FiCalendar } from 'react-icons/fi';
import './CalendarScheduleModal.css';

const CalendarScheduleModal = ({
  isOpen,
  onClose,
  selectedDate,
  newSchedule,
  setNewSchedule,
  onSubmit,
  getInterviewsForDate,
  getStatusText,
  applicants
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={() => {}}>  {/* 배경 클릭 시 닫기 방지 */}
      <div className="modal-content schedule-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{selectedDate} 면접 일정 추가</h2>
          <button 
            className="btn-icon"
            onClick={onClose}
          >
            <FiX />
          </button>
        </div>
        <div className="modal-body">
          <div className="schedule-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="schedule_name">지원자 이름 *</label>
                <input
                  id="schedule_name"
                  name="name"
                  type="text"
                  value={newSchedule.name}
                  onChange={(e) => setNewSchedule(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="지원자 이름을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label htmlFor="schedule_position">지원 직무 *</label>
                <input
                  id="schedule_position"
                  name="position"
                  type="text"
                  value={newSchedule.position}
                  onChange={(e) => setNewSchedule(prev => ({ ...prev, position: e.target.value }))}
                  placeholder="지원 직무를 입력하세요"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="schedule_email">이메일 *</label>
                <input
                  id="schedule_email"
                  name="email"
                  type="email"
                  value={newSchedule.email}
                  onChange={(e) => setNewSchedule(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="이메일을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label htmlFor="schedule_phone">연락처 *</label>
                <input
                  id="schedule_phone"
                  name="phone"
                  type="tel"
                  value={newSchedule.phone}
                  onChange={(e) => setNewSchedule(prev => ({ ...prev, phone: e.target.value }))}
                  placeholder="010-0000-0000"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="schedule_date">면접 날짜</label>
                <input
                  id="schedule_date"
                  name="interviewDate"
                  type="date"
                  value={newSchedule.interviewDate}
                  onChange={(e) => setNewSchedule(prev => ({ ...prev, interviewDate: e.target.value }))}
                  disabled
                  style={{ backgroundColor: '#f3f4f6', cursor: 'not-allowed' }}
                />
              </div>
              <div className="form-group">
                <label htmlFor="schedule_time">면접 시간 *</label>
                <input
                  id="schedule_time"
                  name="interviewTime"
                  type="time"
                  value={newSchedule.interviewTime}
                  onChange={(e) => setNewSchedule(prev => ({ ...prev, interviewTime: e.target.value }))}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="schedule_duration">소요 시간</label>
                <select
                  id="schedule_duration"
                  name="duration"
                  value={newSchedule.duration}
                  onChange={(e) => setNewSchedule(prev => ({ ...prev, duration: e.target.value }))}
                >
                  <option value="30분">30분</option>
                  <option value="60분">60분</option>
                  <option value="90분">90분</option>
                  <option value="120분">120분</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="schedule_type">면접 유형</label>
                <select
                  id="schedule_type"
                  name="type"
                  value={newSchedule.type}
                  onChange={(e) => setNewSchedule(prev => ({ ...prev, type: e.target.value }))}
                >
                  <option value="대면">대면</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="schedule_platform">플랫폼/장소</label>
              <input
                id="schedule_platform"
                name="platform"
                type="text"
                value={newSchedule.platform}
                onChange={(e) => setNewSchedule(prev => ({ ...prev, platform: e.target.value }))}
                placeholder="Zoom, Teams, 회사 면접실 등"
              />
            </div>

            {/* 해당 날짜의 기존 면접 일정 표시 */}
            {selectedDate && getInterviewsForDate(selectedDate).length > 0 && (
              <div className="existing-interviews">
                <h4>이 날의 기존 면접 일정</h4>
                <div className="existing-list">
                  {getInterviewsForDate(selectedDate).map((applicant) => (
                    <div key={applicant.id} className="existing-interview">
                      <span className="time">{applicant.interviewTime}</span>
                      <span className="name">{applicant.name}</span>
                      <span className="position">({applicant.position})</span>
                      <span className={`status ${applicant.status}`}>
                        {getStatusText(applicant.status)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="form-actions">
              <button 
                className="btn btn-primary"
                onClick={onSubmit}
              >
                <FiCalendar />
                일정 추가
              </button>
              <button 
                className="btn btn-secondary"
                onClick={onClose}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarScheduleModal;