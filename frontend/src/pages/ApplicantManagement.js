import React, { useState, useEffect, useCallback, useMemo } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiUser, 
  FiMail, 
  FiPhone, 
  FiCalendar, 
  FiFileText, 
  FiEye, 
  FiDownload,
  FiSearch,
  FiFilter,
  FiCheck,
  FiX,
  FiStar,
  FiBriefcase,
  FiMapPin,
  FiClock,
  FiFile,
  FiMessageSquare,
  FiCode,
  FiGrid,
  FiList,
  FiBarChart2
} from 'react-icons/fi';
import DetailedAnalysisModal from '../components/DetailedAnalysisModal';

// API 서비스 추가
const API_BASE_URL = 'http://localhost:8000';

const api = {
  // 모든 지원자 조회 (페이지네이션 지원)
  getAllApplicants: async (skip = 0, limit = 50, status = null, position = null) => {
    try {
      console.log('🔍 API 호출 시도:', `${API_BASE_URL}/api/applicants`);
      
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString()
      });
      
      if (status) params.append('status', status);
      if (position) params.append('position', position);
      
      const response = await fetch(`${API_BASE_URL}/api/applicants?${params}`);
      console.log('📡 응답 상태:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API 응답 오류:', errorText);
        throw new Error(`지원자 데이터 조회 실패: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ API 응답 데이터:', data);

      // UI 스키마로 정규화
      const normalizeApplicant = (a) => ({
        id: a._id || a.id || String(a.id || ''),
        name: a.name || '',
        position: a.position || '',
        department: a.department || '',
        email: a.email || '',
        phone: a.phone || '',
        appliedDate: a.applied_date || a.appliedDate || '',
        status: a.status || '지원',
        experience: a.experience || '',
        skills: Array.isArray(a.skills)
          ? a.skills
          : (typeof a.skills === 'string' ? a.skills.split(',').map(s => s.trim()).filter(Boolean) : []),
        rating: typeof a.rating === 'number' ? a.rating : 0,
        summary: a.summary || '',
        aiSuitability: (a.ai_suitability ?? a.aiSuitability ?? 0),
        aiScores: a.ai_scores ?? a.aiScores ?? null,
        documents: a.documents || {},
        created_at: a.created_at || a.createdAt || null,
      });

      return Array.isArray(data) ? data.map(normalizeApplicant) : [];
    } catch (error) {
      console.error('❌ 지원자 데이터 조회 오류:', error);
      throw error;
    }
  },

  // 지원자 상태 업데이트
  updateApplicantStatus: async (applicantId, newStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
      });
      if (!response.ok) {
        throw new Error('지원자 상태 업데이트 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('지원자 상태 업데이트 오류:', error);
      throw error;
    }
  },

  // 지원자 통계 조회
  getApplicantStats: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/stats/overview`);
      if (!response.ok) {
        throw new Error('지원자 통계 조회 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('지원자 통계 조회 오류:', error);
      throw error;
    }
  }
};

const Container = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: 32px;
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

const HeaderLeft = styled.div`
  flex: 1;
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
`;

const NewResumeButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  
  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  color: var(--text-secondary);
  font-size: 16px;
`;

const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-size: 14px;
  font-weight: 500;
  margin-top: 8px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const StatCard = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
`;

const StatValue = styled(motion.div)`
  font-size: 32px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  color: var(--text-secondary);
  font-size: 14px;
`;

const SearchBar = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  justify-content: space-between;
`;

const SearchSection = styled.div`
  display: flex;
  gap: 16px;
  align-items: center;
  flex: 1;
`;

const ViewModeSection = styled.div`
  display: flex;
  gap: 8px;
`;

const ViewModeButton = styled.button`
  padding: 8px 12px;
  background: ${props => props.active ? 'var(--primary-color)' : 'white'};
  color: ${props => props.active ? 'white' : 'var(--text-secondary)'};
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--primary-color);
    color: ${props => props.active ? 'white' : 'var(--primary-color)'};
  }
`;

// 헤더 스타일 컴포넌트들
const HeaderRow = styled.div`
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: var(--background-secondary);
  border-radius: 8px;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
`;

const HeaderRowBoard = styled.div`
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: var(--background-secondary);
  border-radius: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 11px;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  height: 36px;
  gap: 16px;
`;

const HeaderAvatar = styled.div`
  width: 28px;
  flex-shrink: 0;
`;

const HeaderName = styled.div`
  min-width: 90px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

const HeaderPosition = styled.div`
  min-width: 110px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

const HeaderDate = styled.div`
  min-width: 80px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 12px;
`;

const HeaderEmail = styled.div`
  min-width: 160px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

const HeaderPhone = styled.div`
  min-width: 110px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

const HeaderSkills = styled.div`
  min-width: 140px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

const HeaderActions = styled.div`
  min-width: 100px;
  flex-shrink: 0;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

const HeaderRanks = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 12px;
`;

const HeaderCheckbox = styled.div`
  min-width: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ApplicantCheckbox = styled.div`
  min-width: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const CheckboxInput = styled.input`
  width: 16px;
  height: 16px;
  accent-color: var(--primary-color);
  cursor: pointer;
`;

const FixedActionBar = styled.div`
  position: sticky;
  top: 0;
  background: var(--background-secondary);
  padding: 12px 24px;
  margin: 0 -24px 16px -24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 100;
`;

const ActionButtonsGroup = styled.div`
  display: flex;
  gap: 8px;
`;

const FixedActionButton = styled.button`
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }
`;

const FixedPassButton = styled(FixedActionButton)`
  background: ${props => props.active ? '#28a745' : 'white'};
  color: ${props => props.active ? 'white' : '#28a745'};
  border-color: #28a745;
  
  &:hover {
    background: ${props => props.active ? '#218838' : '#28a745'};
    border-color: ${props => props.active ? '#1e7e34' : '#28a745'};
    color: ${props => props.active ? 'white' : 'white'};
  }
`;

const FixedPendingButton = styled(FixedActionButton)`
  background: ${props => props.active ? '#ffc107' : 'white'};
  color: ${props => props.active ? '#212529' : '#ffc107'};
  border-color: #ffc107;
  
  &:hover {
    background: ${props => props.active ? '#e0a800' : '#ffc107'};
    border-color: ${props => props.active ? '#d39e00' : '#ffc107'};
    color: ${props => props.active ? '#212529' : '#212529'};
  }
`;

const FixedRejectButton = styled(FixedActionButton)`
  background: ${props => props.active ? '#dc3545' : 'white'};
  color: ${props => props.active ? 'white' : '#dc3545'};
  border-color: #dc3545;
  
  &:hover {
    background: ${props => props.active ? '#c82333' : '#dc3545'};
    border-color: ${props => props.active ? '#bd2130' : '#dc3545'};
    color: ${props => props.active ? 'white' : 'white'};
  }
`;

const SelectionInfo = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  
  &:focus {
    border-color: var(--primary-color);
  }
`;

// 누락된 스타일 컴포넌트들 추가
const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const CardContent = styled.div`
  margin-bottom: 12px;
`;

const InfoRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--text-secondary);
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
`;

const LoadingOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const LoadingSpinner = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  
  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadMoreButton = styled.button`
  width: 100%;
  padding: 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 24px;
  transition: all 0.2s;
  
  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
  }
`;

const EndMessage = styled.div`
  text-align: center;
  padding: 24px;
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: 24px;
`;

// 새 이력서 등록 모달 스타일 컴포넌트들
const ResumeModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ResumeModalContent = styled(motion.div)`
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
`;

const ResumeModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid var(--border-color);
`;

const ResumeModalTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const ResumeModalCloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
  
  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const ResumeModalBody = styled.div`
  padding: 24px;
`;

const ResumeFormSection = styled.div`
  margin-bottom: 24px;
`;

const ResumeFormTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
`;

const FileUploadArea = styled.div`
  border: 2px dashed ${props => props.isDragOver ? 'var(--primary-color)' : 'var(--border-color)'};
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  transition: all 0.2s;
  background: ${props => props.isDragOver ? 'rgba(0, 200, 81, 0.1)' : 'transparent'};
  
  &:hover {
    border-color: var(--primary-color);
    background: var(--background-secondary);
  }
`;

const FileUploadInput = styled.input`
  display: none;
`;

const FileUploadLabel = styled.label`
  cursor: pointer;
  display: block;
`;

const FileUploadPlaceholder = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  
  span {
    font-size: 16px;
    font-weight: 500;
  }
  
  small {
    font-size: 12px;
    color: var(--text-light);
  }
`;

const FileSelected = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-weight: 500;
`;

const ResumeFormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
`;

const ResumeFormField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const ResumeFormLabel = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
`;

const ResumeFormInput = styled.input`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  
  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  &::placeholder {
    color: var(--text-light);
  }
`;

// 문서 업로드 관련 스타일 컴포넌트들
const DocumentUploadContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const DocumentTypeSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const DocumentTypeLabel = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
`;

const DocumentTypeSelect = styled.select`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  
  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  option {
    padding: 8px;
  }
`;

const ResumeModalFooter = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid var(--border-color);
`;

const ResumeModalButton = styled.button`
  padding: 12px 24px;
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: var(--background-secondary);
    border-color: var(--text-secondary);
  }
`;

const ResumeModalSubmitButton = styled.button`
  padding: 12px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: var(--primary-dark);
  }
  
  &:disabled {
    background: var(--text-light);
    cursor: not-allowed;
  }
`;

// 분석 결과 스타일 컴포넌트들
const ResumeAnalysisSection = styled.div`
  margin-top: 24px;
  padding: 20px;
  background: var(--background-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
`;

const ResumeAnalysisTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
`;

const ResumeAnalysisSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  
  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  span {
    color: var(--text-secondary);
    font-size: 14px;
  }
`;

const ResumeAnalysisContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ResumeAnalysisItem = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
`;

const ResumeAnalysisLabel = styled.span`
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  min-width: 80px;
`;

const ResumeAnalysisValue = styled.span`
  font-size: 14px;
  color: var(--text-secondary);
  flex: 1;
`;

const ResumeAnalysisScore = styled.span`
  font-size: 16px;
  font-weight: 600;
  color: ${props => {
    if (props.score >= 90) return '#28a745';
    if (props.score >= 80) return '#ffc107';
    return '#dc3545';
  }};
`;

const ResumeAnalysisSkills = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
`;

const ResumeSkillTag = styled.span`
  padding: 4px 8px;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
`;

const ResumeAnalysisRecommendations = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
`;

const ResumeRecommendationItem = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.4;
`;

const DetailedAnalysisButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
`;

const FilterButton = styled.button`
  padding: 12px 16px;
  background: ${props => props.hasActiveFilters ? 'var(--primary-color)' : 'white'};
  color: ${props => props.hasActiveFilters ? 'white' : 'var(--text-primary)'};
  border: 1px solid ${props => props.hasActiveFilters ? 'var(--primary-color)' : 'var(--border-color)'};
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    background: ${props => props.hasActiveFilters ? 'var(--primary-dark)' : 'white'};
  }
`;

const FilterBadge = styled.span`
  background: ${props => props.hasActiveFilters ? 'white' : 'var(--primary-color)'};
  color: ${props => props.hasActiveFilters ? 'var(--primary-color)' : 'white'};
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
`;

// 필터 모달 스타일
const FilterModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1500;
  padding: 20px;
`;

const FilterModalContent = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 600px;
  width: 100%;
  position: relative;
`;

const FilterModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
`;

const FilterModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
`;

const FilterCloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
  
  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const FilterSection = styled.div`
  margin-bottom: 24px;
`;

const FilterSectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
`;

const FilterGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
`;

const FilterColumn = styled.div``;

const CheckboxGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const CheckboxItem = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
  
  &:hover {
    color: var(--primary-color);
  }
`;

const Checkbox = styled.input`
  width: 16px;
  height: 16px;
  accent-color: var(--primary-color);
`;

const ApplyButton = styled.button`
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

const ResetButton = styled.button`
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #e5e7eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const FilterButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
  
  ${ApplyButton}, ${ResetButton} {
    flex: 1;
  }
`;

const NoResultsMessage = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
  
  h3 {
    margin: 16px 0 8px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  p {
    margin: 0;
    font-size: 14px;
    color: var(--text-secondary);
  }
`;

const ApplicantsGrid = styled.div`
  display: grid;
  grid-template-columns: ${props => props.viewMode === 'grid' ? 'repeat(auto-fill, minmax(350px, 1fr))' : '1fr'};
  gap: ${props => props.viewMode === 'grid' ? '24px' : '16px'};
`;

const ApplicantsBoard = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ApplicantCard = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: ${props => props.viewMode === 'grid' ? '24px' : '20px'};
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
`;

const ApplicantCardBoard = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
  height: 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
`;

const ApplicantHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`;

const ApplicantHeaderBoard = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
`;

const ApplicantInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ApplicantInfoBoard = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
`;

const Avatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
`;

const AvatarBoard = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
`;

const AiSuitabilityAvatarBoard = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${props => {
    if (props.percentage >= 90) return 'linear-gradient(135deg, #22c55e, #16a34a)';
    if (props.percentage >= 80) return 'linear-gradient(135deg, #eab308, #ca8a04)';
    return 'linear-gradient(135deg, #ef4444, #dc2626)';
  }};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 10px;
  text-align: center;
  line-height: 1;
`;

const ApplicantDetails = styled.div`
  flex: 1;
`;

const ApplicantDetailsBoard = styled.div`
  display: flex;
  align-items: center;
  gap: 0;
  flex: 1;
  min-width: 0;
  overflow: hidden;
`;

const ApplicantName = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const ApplicantNameBoard = styled.h3`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 90px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ApplicantPosition = styled.p`
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
`;

const ApplicantPositionBoard = styled.p`
  color: var(--text-secondary);
  font-size: 12px;
  min-width: 110px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ApplicantDate = styled.p`
  color: var(--text-light);
  font-size: 12px;
`;

const ApplicantDateBoard = styled.p`
  color: var(--text-light);
  font-size: 11px;
  min-width: 80px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
`;

const ApplicantEmailBoard = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 160px;
  flex-shrink: 0;
`;

const ApplicantPhoneBoard = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 110px;
  flex-shrink: 0;
`;

const ContactItem = styled.div`
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  color: var(--text-secondary);
  justify-content: center;
`;

const ApplicantSkillsBoard = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  min-width: 150px;
  justify-content: center;
`;

const SkillTagBoard = styled.span`
  padding: 1px 4px;
  background: var(--background-secondary);
  border-radius: 4px;
  font-size: 9px;
  color: var(--text-secondary);
`;

const ApplicantActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  opacity: ${props => props.isHovered ? 1 : 0};
  transition: opacity 0.2s ease;
`;

const ApplicantActionsBoard = styled.div`
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  opacity: ${props => props.isHovered ? 1 : 0};
  transition: opacity 0.2s ease;
  margin-top: ${props => props.isHovered ? '8px' : '0'};
`;

const StatusBadge = styled(motion.span)`
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  background: ${props => {
    switch (props.status) {
      case '서류합격': return '#e8f5e8';
      case '서류불합격': return '#ffe8e8';
      case '면접대기': return '#fff3cd';
      case '최종합격': return '#d1ecf1';
      case '보류': return '#fff8dc';
      default: return '#f8f9fa';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case '서류합격': return '#28a745';
      case '서류불합격': return '#dc3545';
      case '면접대기': return '#856404';
      case '최종합격': return '#0c5460';
      case '보류': return '#856404';
      default: return '#6c757d';
    }
  }};
`;

const StatusColumnWrapper = styled.div`
  min-width: 200px;
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  white-space: nowrap;
`;

const ActionButton = styled.button`
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  color: var(--text-secondary);
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }
`;

const PassButton = styled(ActionButton)`
  background: ${props => props.active ? '#28a745' : 'white'};
  color: ${props => props.active ? 'white' : '#28a745'};
  border-color: #28a745;
  
  &:hover {
    background: ${props => props.active ? '#218838' : '#28a745'};
    border-color: ${props => props.active ? '#1e7e34' : '#28a745'};
    color: ${props => props.active ? 'white' : 'white'};
  }
`;

const PendingButton = styled(ActionButton)`
  background: ${props => props.active ? '#ffc107' : 'white'};
  color: ${props => props.active ? '#212529' : '#ffc107'};
  border-color: #ffc107;
  
  &:hover {
    background: ${props => props.active ? '#e0a800' : '#ffc107'};
    border-color: ${props => props.active ? '#d39e00' : '#ffc107'};
    color: ${props => props.active ? '#212529' : '#212529'};
  }
`;

const RejectButton = styled(ActionButton)`
  background: ${props => props.active ? '#dc3545' : 'white'};
  color: ${props => props.active ? 'white' : '#dc3545'};
  border-color: #dc3545;
  
  &:hover {
    background: ${props => props.active ? '#c82333' : '#dc3545'};
    border-color: ${props => props.active ? '#bd2130' : '#dc3545'};
    color: ${props => props.active ? 'white' : 'white'};
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 48px;
  color: var(--text-secondary);
`;

// 모달 스타일
const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
`;

const ModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
`;

const ModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
  
  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const ProfileSection = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ProfileGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
`;

const ProfileItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--background-secondary);
  border-radius: 8px;
`;

const ProfileLabel = styled.span`
  font-size: 14px;
  color: var(--text-secondary);
  min-width: 80px;
`;

const ProfileValue = styled.span`
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
`;

const SummarySection = styled.div`
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  padding: 20px;
  margin-top: 24px;
`;

const SummaryTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SummaryText = styled.p`
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  background: white;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
`;

const DocumentButtons = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 50px;
`;

const DocumentButton = styled.button`
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

// 문서 모달 스타일
const DocumentModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
`;

const DocumentModalContent = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
`;

const DocumentModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
`;

const DocumentModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
`;

const DocumentCloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
  
  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const DocumentHeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const DocumentOriginalButton = styled.button`
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const DocumentContent = styled.div`
  line-height: 1.8;
  color: var(--text-primary);
`;

const DocumentSection = styled.div`
  margin-bottom: 24px;
`;

const DocumentSectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary-color);
`;

const DocumentText = styled.p`
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  text-align: justify;
`;

const DocumentList = styled.ul`
  margin: 16px 0;
  padding-left: 20px;
`;

const DocumentListItem = styled.li`
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.6;
`;

const DocumentGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 16px 0;
`;

const DocumentCard = styled.div`
  background: var(--background-secondary);
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
`;

const DocumentCardTitle = styled.h4`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

const DocumentCardText = styled.p`
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
`;

const SkillsSection = styled.div`
  margin-top: 24px;
`;

const SkillsTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SkillsGrid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const SkillTag = styled.span`
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  color: white;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
`;

const AiAnalysisSection = styled.div`
  margin-top: 16px;
  padding: 16px;
  background: var(--background-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
`;

const AiAnalysisTitle = styled.h4`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const AiAnalysisContent = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const SuitabilityGraph = styled.div`
  position: relative;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const CircularProgress = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(
    ${props => {
      if (props.percentage >= 90) return '#10b981';
      if (props.percentage >= 80) return '#f59e0b';
      return '#ef4444';
    }} 0deg ${props => props.percentage * 3.6}deg,
    #e5e7eb ${props => props.percentage * 3.6}deg 360deg
  );
  display: flex;
  align-items: center;
  justify-content: center;
  
  &::before {
    content: '';
    position: absolute;
    width: 80%;
    height: 80%;
    background: white;
    border-radius: 50%;
  }
`;

const PercentageText = styled.div`
  position: absolute;
  font-size: 12px;
  font-weight: 700;
  color: ${props => {
    if (props.percentage >= 90) return '#10b981';
    if (props.percentage >= 80) return '#f59e0b';
    return '#ef4444';
  }};
`;

const SuitabilityInfo = styled.div`
  flex: 1;
`;

const SuitabilityLabel = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
`;

const SuitabilityValue = styled.div`
  font-size: 16px;
  font-weight: 700;
  color: ${props => {
    if (props.percentage >= 90) return '#10b981';
    if (props.percentage >= 80) return '#f59e0b';
    return '#ef4444';
  }};
`;

// Board view specific AI analysis components
const AiAnalysisSectionBoard = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
`;

const AiAnalysisTitleBoard = styled.h4`
  font-size: 10px;
  font-weight: 600;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
`;

const SuitabilityGraphBoard = styled.div`
  position: relative;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const CircularProgressBoard = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(
    ${props => {
      if (props.percentage >= 90) return '#10b981';
      if (props.percentage >= 80) return '#f59e0b';
      return '#ef4444';
    }} 0deg ${props => props.percentage * 3.6}deg,
    #e5e7eb ${props => props.percentage * 3.6}deg 360deg
  );
  display: flex;
  align-items: center;
  justify-content: center;
  
  &::before {
    content: '';
    position: absolute;
    width: 80%;
    height: 80%;
    background: white;
    border-radius: 50%;
  }
`;

const PercentageTextBoard = styled.div`
  position: absolute;
  font-size: 8px;
  font-weight: 700;
  color: ${props => {
    if (props.percentage >= 90) return '#10b981';
    if (props.percentage >= 80) return '#f59e0b';
    return '#ef4444';
  }};
`;

const SuitabilityValueBoard = styled.div`
  font-size: 10px;
  font-weight: 600;
  color: ${props => {
    if (props.percentage >= 90) return '#10b981';
    if (props.percentage >= 80) return '#f59e0b';
    return '#ef4444';
  }};
`;

const ApplicantRanksBoard = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;
  flex-wrap: nowrap;
  white-space: nowrap;
  margin-left: -70px;
`;

const RankItem = styled.div`
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 9px;
  color: var(--text-secondary);
  white-space: nowrap;
`;

const RankBadge = styled.span`
  padding: 1px 3px;
  border-radius: 3px;
  font-size: 8px;
  font-weight: 600;
  background: ${props => {
    if (props.rank <= 2) return '#10b981';
    if (props.rank <= 4) return '#f59e0b';
    return '#ef4444';
  }};
  color: white;
`;

const sampleApplicants = [
  {
    id: 1,
    name: '김지원',
    position: '프론트엔드 개발자',
    department: '개발팀',
    email: 'kim.jiwon@email.com',
    phone: '010-1234-5678',
    appliedDate: '2024-01-15',
    status: '지원',
    experience: '3년',
    skills: ['React', 'TypeScript', 'JavaScript'],
    rating: 4.5,
    summary: 'React와 TypeScript에 능숙하며, 사용자 경험을 중시하는 프론트엔드 개발자입니다. 팀 프로젝트에서 리더 역할을 수행한 경험이 있고, 새로운 기술 학습에 적극적입니다.',
    documents: {
      resume: {
        personalInfo: {
          name: '김지원',
          email: 'kim.jiwon@email.com',
          phone: '010-1234-5678',
          address: '서울시 강남구',
          birth: '1995.03.15'
        },
        education: [
          {
            school: '서울대학교',
            major: '컴퓨터공학과',
            degree: '학사',
            period: '2014.03 - 2018.02',
            gpa: '4.2/4.5'
          }
        ],
        experience: [
          {
            company: '테크스타트업',
            position: '프론트엔드 개발자',
            period: '2021.03 - 현재',
            description: 'React와 TypeScript를 활용한 웹 애플리케이션 개발, 사용자 경험 개선 프로젝트 리드'
          },
          {
            company: 'IT컨설팅',
            position: '웹 개발자',
            period: '2018.03 - 2021.02',
            description: 'JavaScript 기반 웹사이트 개발, 반응형 디자인 구현'
          }
        ],
        skills: {
          programming: ['JavaScript', 'TypeScript', 'React', 'Vue.js', 'HTML/CSS'],
          tools: ['Git', 'Webpack', 'VS Code', 'Figma'],
          languages: ['한국어', '영어']
        }
      },
      coverLetter: {
        motivation: '사용자 중심의 웹 애플리케이션을 개발하여 더 나은 디지털 경험을 제공하고 싶습니다. React 생태계에 대한 깊은 이해와 팀 협업 경험을 바탕으로 혁신적인 제품 개발에 기여하고자 합니다.',
        strengths: [
          '사용자 경험을 중시하는 개발 철학',
          '새로운 기술 학습에 대한 적극적인 자세',
          '팀 프로젝트에서의 리더십 경험',
          '문제 해결 능력과 창의적 사고'
        ],
        goals: '3년 내에 프론트엔드 아키텍트로 성장하여 팀의 기술적 방향을 이끌고, 사용자에게 최고의 경험을 제공하는 제품을 만들어가고 싶습니다.'
      },
      portfolio: {
        projects: [
          {
            title: 'E-커머스 플랫폼',
            description: 'React와 TypeScript를 활용한 온라인 쇼핑몰 개발',
            technologies: ['React', 'TypeScript', 'Redux', 'Styled-components'],
            features: ['반응형 디자인', '장바구니 기능', '결제 시스템 연동', '관리자 대시보드'],
            github: 'https://github.com/kimjiwon/ecommerce',
            demo: 'https://ecommerce-demo.com'
          },
          {
            title: '실시간 채팅 앱',
            description: 'Socket.io를 활용한 실시간 메신저 애플리케이션',
            technologies: ['React', 'Socket.io', 'Node.js', 'MongoDB'],
            features: ['실시간 메시징', '파일 공유', '그룹 채팅', '이모지 지원'],
            github: 'https://github.com/kimjiwon/chat-app',
            demo: 'https://chat-app-demo.com'
          },
          {
            title: '날씨 정보 앱',
            description: 'OpenWeather API를 활용한 날씨 정보 제공 애플리케이션',
            technologies: ['React', 'OpenWeather API', 'Chart.js', 'PWA'],
            features: ['실시간 날씨 정보', '5일 예보', '위치 기반 서비스', '오프라인 지원'],
            github: 'https://github.com/kimjiwon/weather-app',
            demo: 'https://weather-app-demo.com'
          }
        ],
        achievements: [
          '2023년 개발자 컨퍼런스 발표자 선정',
          '오픈소스 프로젝트 50+ 기여',
          'GitHub 스타 200+ 획득',
          '개발 블로그 월 10,000+ 방문자'
        ]
      }
    },
    aiSuitability: 92,
    aiScores: {
      resume: 88,
      coverLetter: 92,
      portfolio: 95
    }
  },
  {
    id: 2,
    name: '박민수',
    position: '백엔드 개발자',
    department: '개발팀',
    email: 'park.minsu@email.com',
    phone: '010-2345-6789',
    appliedDate: '2024-01-14',
    status: '지원',
    experience: '5년',
    skills: ['Java', 'Spring', 'MySQL'],
    rating: 4.8,
    summary: 'Spring Framework와 Java 개발에 전문성을 가지고 있으며, 대용량 데이터 처리와 시스템 아키텍처 설계 경험이 풍부합니다. 마이크로서비스 아키텍처 구축 경험이 있습니다.',
    aiSuitability: 88,
    aiScores: {
      resume: 85,
      coverLetter: 88,
      portfolio: 90
    }
  },
  {
    id: 3,
    name: '이서연',
    position: 'UI/UX 디자이너',
    department: '디자인팀',
    email: 'lee.seoyeon@email.com',
    phone: '010-3456-7890',
    appliedDate: '2024-01-13',
    status: '지원',
    experience: '2년',
    skills: ['Figma', 'Adobe XD', 'Photoshop'],
    rating: 3.9,
    summary: '사용자 중심의 디자인을 추구하며, 프로토타이핑과 사용자 테스트를 통한 디자인 검증 경험이 있습니다. 브랜드 아이덴티티 디자인에도 관심이 많습니다.',
    aiSuitability: 75,
    aiScores: {
      resume: 72,
      coverLetter: 75,
      portfolio: 78
    }
  },
  {
    id: 4,
    name: '정현우',
    position: 'DevOps 엔지니어',
    department: '인프라팀',
    email: 'jung.hyunwoo@email.com',
    phone: '010-4567-8901',
    appliedDate: '2024-01-12',
    status: '지원',
    experience: '4년',
    skills: ['Docker', 'Kubernetes', 'AWS'],
    rating: 4.7,
    summary: '클라우드 인프라 구축과 컨테이너 오케스트레이션에 전문성을 가지고 있으며, CI/CD 파이프라인 구축과 모니터링 시스템 설계 경험이 풍부합니다.',
    aiSuitability: 95,
    aiScores: {
      resume: 92,
      coverLetter: 95,
      portfolio: 98
    }
  },
  {
    id: 5,
    name: '최수진',
    position: '데이터 분석가',
    department: '데이터팀',
    email: 'choi.sujin@email.com',
    phone: '010-5678-9012',
    appliedDate: '2024-01-11',
    status: '지원',
    experience: '3년',
    skills: ['Python', 'SQL', 'Tableau'],
    rating: 4.2,
    summary: '데이터 분석과 시각화에 전문성을 가지고 있으며, 비즈니스 인사이트 도출을 통한 의사결정 지원 경험이 풍부합니다. 머신러닝 모델 개발 경험도 있습니다.',
    aiSuitability: 82,
    aiScores: {
      resume: 80,
      coverLetter: 82,
      portfolio: 85
    }
  },
  {
    id: 6,
    name: '강동현',
    position: '모바일 개발자',
    department: '개발팀',
    email: 'kang.donghyun@email.com',
    phone: '010-6789-0123',
    appliedDate: '2024-01-10',
    status: '지원',
    experience: '6년',
    skills: ['iOS', 'Swift', 'Android'],
    rating: 4.6,
    summary: 'iOS와 Android 플랫폼 모두에서 앱 개발 경험이 풍부하며, 네이티브 앱과 크로스 플랫폼 개발 모두 가능합니다. 사용자 경험을 중시하는 앱 개발에 특화되어 있습니다.',
    aiSuitability: 89,
    aiScores: {
      resume: 87,
      coverLetter: 89,
      portfolio: 92
    }
  }
];

// 메모이제이션된 지원자 카드 컴포넌트
const MemoizedApplicantCard = React.memo(({ applicant, onCardClick, onStatusUpdate }) => {
  const handleStatusUpdate = useCallback(async (newStatus) => {
    try {
      await onStatusUpdate(applicant.id, newStatus);
    } catch (error) {
      console.error('상태 업데이트 실패:', error);
    }
  }, [applicant.id, onStatusUpdate]);

  return (
    <ApplicantCard
      onClick={() => onCardClick(applicant)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <CardHeader>
        <ApplicantInfo>
          <ApplicantName>{applicant.name}</ApplicantName>
          <ApplicantPosition>{applicant.position}</ApplicantPosition>
        </ApplicantInfo>
        <StatusBadge status={applicant.status}>
          {applicant.status}
        </StatusBadge>
      </CardHeader>
      
      <CardContent>
        <InfoRow>
          <FiMail />
          <span>{applicant.email}</span>
        </InfoRow>
        <InfoRow>
          <FiPhone />
          <span>{applicant.phone}</span>
        </InfoRow>
        <InfoRow>
          <FiCalendar />
          <span>{applicant.appliedDate}</span>
        </InfoRow>
        <InfoRow>
          <FiCode />
          <span>{applicant.skills.join(', ')}</span>
        </InfoRow>
      </CardContent>
      
      <CardActions>
        <PassButton 
          active={applicant.status === '서류합격' || applicant.status === '최종합격'}
          onClick={(e) => {
            e.stopPropagation();
            handleStatusUpdate('서류합격');
          }}
        >
          <FiCheck />
          합격
        </PassButton>
        <PendingButton 
          active={applicant.status === '보류'}
          onClick={(e) => {
            e.stopPropagation();
            handleStatusUpdate('보류');
          }}
        >
          <FiClock />
          보류
        </PendingButton>
        <RejectButton 
          active={applicant.status === '서류불합격'}
          onClick={(e) => {
            e.stopPropagation();
            handleStatusUpdate('서류불합격');
          }}
        >
          <FiX />
          불합격
        </RejectButton>
      </CardActions>
    </ApplicantCard>
  );
});

MemoizedApplicantCard.displayName = 'MemoizedApplicantCard';

const ApplicantManagement = () => {
  const [applicants, setApplicants] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('전체');
  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [documentModal, setDocumentModal] = useState({ isOpen: false, type: '', applicant: null });
  const [filterModal, setFilterModal] = useState(false);
  const [selectedJobs, setSelectedJobs] = useState([]);
  const [selectedExperience, setSelectedExperience] = useState([]);
  const [viewMode, setViewMode] = useState('grid');
  const [hoveredApplicant, setHoveredApplicant] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedApplicants, setSelectedApplicants] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    passed: 0,
    waiting: 0,
    rejected: 0
  });

  // 페이지네이션 상태
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize] = useState(20);
  const [hasMore, setHasMore] = useState(true);

  // 새 이력서 등록 모달 상태
  const [isResumeModalOpen, setIsResumeModalOpen] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [documentType, setDocumentType] = useState('이력서');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [showDetailedAnalysis, setShowDetailedAnalysis] = useState(false);
  const [resumeData, setResumeData] = useState({
    name: '',
    email: '',
    phone: '',
    position: '',
    experience: '',
    skills: []
  });

  // 메모이제이션된 필터링된 지원자 목록
  const filteredApplicants = useMemo(() => {
    // 검색/필터가 비었으면 전체 반환
    const noSearch = !searchTerm || searchTerm.trim() === '';
    const noStatus = filterStatus === '전체';
    const noJobs = selectedJobs.length === 0;
    const noExp = selectedExperience.length === 0;
    if (noSearch && noStatus && noJobs && noExp) return applicants;

    return applicants.filter(applicant => {
      const searchLower = (searchTerm || '').toLowerCase();
      const skillsArr = Array.isArray(applicant.skills) ? applicant.skills : [];
      
      const matchesSearch = (applicant.name || '').toLowerCase().includes(searchLower) ||
                          (applicant.position || '').toLowerCase().includes(searchLower) ||
                          (applicant.email || '').toLowerCase().includes(searchLower) ||
                          skillsArr.some(skill => (skill || '').toLowerCase().includes(searchLower));
      
      const matchesStatus = filterStatus === '전체' || applicant.status === filterStatus;
      const matchesJob = selectedJobs.length === 0 || 
                        selectedJobs.some(job => (applicant.position || '').includes(job));
      
      // 경험 필터는 엄격 매칭 대신 포함 여부 완화
      const expStr = (applicant.experience || '').toString();
      const matchesExperience = selectedExperience.length === 0 || 
                              selectedExperience.some(exp => expStr.includes(exp.replace(/\s+/g, '')));
      
      return matchesSearch && matchesStatus && matchesJob && matchesExperience;
    });
  }, [applicants, searchTerm, filterStatus, selectedJobs, selectedExperience]);

  // 메모이제이션된 페이지네이션된 지원자 목록
  const paginatedApplicants = useMemo(() => {
    const src = filteredApplicants.length > 0 ? filteredApplicants : applicants;
    const startIndex = currentPage * pageSize;
    return src.slice(startIndex, startIndex + pageSize);
  }, [filteredApplicants, applicants, currentPage, pageSize]);

  // 초기 데이터 로드
  useEffect(() => {
    loadApplicants();
    loadStats();
  }, []);

  // applicants 상태가 변경될 때마다 통계 업데이트
  useEffect(() => {
    updateLocalStats();
  }, [applicants]);

  // 지원자 데이터 로드 (페이지네이션 지원)
  const loadApplicants = useCallback(async (page = 0, append = false) => {
    try {
      setIsLoading(true);
      console.log('지원자 데이터를 불러오는 중...');
      
      const skip = page * pageSize;
      const apiApplicants = await api.getAllApplicants(skip, pageSize);

      let merged = apiApplicants || [];

      // API가 비어있거나 최소 보장을 위해 OCR 문서를 지원자 형태로 병합
      try {
        const ocrRes = await fetch(`${API_BASE_URL}/api/pdf/documents/applicants`);
        if (ocrRes.ok) {
          const ocrApplicants = await ocrRes.json();
          if (Array.isArray(ocrApplicants) && ocrApplicants.length > 0) {
            // _id 기준 중복 제거하여 병합
            const byId = new Map();
            for (const a of merged) byId.set(a._id, a);
            for (const b of ocrApplicants) if (!byId.has(b._id)) byId.set(b._id, b);
            merged = Array.from(byId.values());
          }
        }
      } catch (e) {
        console.warn('OCR 문서 병합 실패(무시):', e);
      }
      
      if (merged && merged.length > 0) {
        console.log(`✅ 총 ${merged.length}명의 지원자 데이터를 로드/병합했습니다.`);
        if (append) {
          setApplicants(prev => {
            const map = new Map(prev.map(a => [a._id, a]));
            for (const m of merged) map.set(m._id, m);
            return Array.from(map.values());
          });
        } else {
          setApplicants(merged);
        }
        setHasMore(apiApplicants && apiApplicants.length === pageSize);
      } else {
        console.log('⚠️ API/OCR 모두 데이터가 없어 빈 배열을 유지합니다.');
        setApplicants([]);
        setHasMore(false);
      }
    } catch (error) {
      console.error('❌ API 연결 실패:', error);
      setApplicants([]);
      setHasMore(false);
    } finally {
      setIsLoading(false);
    }
  }, [API_BASE_URL, pageSize]);

  // 통계 데이터 로드
  const loadStats = useCallback(async () => {
    try {
      const apiStats = await api.getApplicantStats();
      setStats(apiStats);
    } catch (error) {
      console.error('통계 데이터 로드 실패:', error);
      // 기본 통계 계산
      updateLocalStats();
    }
  }, []);

  // 로컬 통계 업데이트
  const updateLocalStats = useCallback(() => {
    const currentStats = {
      total: applicants.length,
      passed: applicants.filter(a => a.status === '서류합격' || a.status === '최종합격').length,
      waiting: applicants.filter(a => a.status === '보류').length,
      rejected: applicants.filter(a => a.status === '서류불합격').length
    };
    setStats(currentStats);
  }, [applicants]);

  // 지원자 상태 업데이트
  const handleUpdateStatus = useCallback(async (applicantId, newStatus) => {
    try {
      // 현재 지원자의 이전 상태 확인
      const currentApplicant = applicants.find(a => a.id === applicantId);
      const previousStatus = currentApplicant ? currentApplicant.status : '지원';
      
      console.log(`🔄 상태 변경: ${previousStatus} → ${newStatus}`);
      
      // API 호출 시도 (실패해도 로컬 상태는 업데이트)
      try {
        await api.updateApplicantStatus(applicantId, newStatus);
        console.log(`✅ API 호출 성공`);
      } catch (apiError) {
        console.log(`⚠️ API 호출 실패, 로컬 상태만 업데이트:`, apiError.message);
      }
      
      // 로컬 상태 업데이트 및 통계 즉시 계산
      setApplicants(prev => {
        const updatedApplicants = prev.map(applicant => 
          applicant.id === applicantId 
            ? { ...applicant, status: newStatus }
            : applicant
        );
        
        // 통계 즉시 업데이트
        const newStats = {
          total: updatedApplicants.length,
          passed: updatedApplicants.filter(a => a.status === '서류합격' || a.status === '최종합격').length,
          waiting: updatedApplicants.filter(a => a.status === '보류').length,
          rejected: updatedApplicants.filter(a => a.status === '서류불합격').length
        };
        
        console.log(`📊 통계 업데이트:`, {
          이전상태: previousStatus,
          새상태: newStatus,
          총지원자: newStats.total,
          서류합격: newStats.passed,
          보류: newStats.waiting,
          서류불합격: newStats.rejected
        });
        
        setStats(newStats);
        
        return updatedApplicants;
      });
      
      console.log(`✅ 지원자 ${applicantId}의 상태가 ${newStatus}로 업데이트되었습니다.`);
    } catch (error) {
      console.error('지원자 상태 업데이트 실패:', error);
    }
  }, [applicants]);

  // 무한 스크롤 핸들러
  const handleLoadMore = useCallback(() => {
    if (!isLoading && hasMore) {
      const nextPage = currentPage + 1;
      setCurrentPage(nextPage);
      loadApplicants(nextPage, true);
    }
  }, [isLoading, hasMore, currentPage, loadApplicants]);

  const handleCardClick = (applicant) => {
    setSelectedApplicant(applicant);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedApplicant(null);
  };

  const handleDocumentClick = (type, applicant) => {
    setDocumentModal({ isOpen: true, type, applicant });
  };

  const handleCloseDocumentModal = () => {
    setDocumentModal({ isOpen: false, type: '', applicant: null });
  };

  const handleFilterClick = () => {
    setFilterModal(true);
  };

  const handleCloseFilterModal = () => {
    setFilterModal(false);
  };

  const handleJobChange = (job) => {
    setSelectedJobs(prev => 
      prev.includes(job) 
        ? prev.filter(j => j !== job)
        : [...prev, job]
    );
  };

  const handleExperienceChange = (experience) => {
    setSelectedExperience(prev => 
      prev.includes(experience) 
        ? prev.filter(e => e !== experience)
        : [...prev, experience]
    );
  };

  const handleApplyFilter = () => {
    setFilterModal(false);
  };

  const handleResetFilter = () => {
    setSelectedJobs([]);
    setSelectedExperience([]);
    setFilterStatus('전체');
    setSearchTerm('');
  };

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
  };

  // 체크박스 관련 핸들러들
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedApplicants([]);
      setSelectAll(false);
    } else {
      setSelectedApplicants(paginatedApplicants.map(applicant => applicant.id));
      setSelectAll(true);
    }
  };

  const handleSelectApplicant = (applicantId) => {
    setSelectedApplicants(prev => {
      if (prev.includes(applicantId)) {
        const newSelected = prev.filter(id => id !== applicantId);
        setSelectAll(newSelected.length === paginatedApplicants.length);
        return newSelected;
      } else {
        const newSelected = [...prev, applicantId];
        setSelectAll(newSelected.length === paginatedApplicants.length);
        return newSelected;
      }
    });
  };

  const handleBulkStatusUpdate = async (newStatus) => {
    if (selectedApplicants.length === 0) {
      return;
    }

    try {
      // 선택된 모든 지원자의 상태를 일괄 업데이트
      for (const applicantId of selectedApplicants) {
        await handleUpdateStatus(applicantId, newStatus);
      }
      
      // 선택 해제
      setSelectedApplicants([]);
      setSelectAll(false);
    } catch (error) {
      console.error('일괄 상태 업데이트 실패:', error);
    }
  };

  // 현재 적용된 필터 상태 확인
  const hasActiveFilters = searchTerm !== '' || 
                          filterStatus !== '전체' || 
                          selectedJobs.length > 0 || 
                          selectedExperience.length > 0;

  // 필터 상태 텍스트 생성
  const getFilterStatusText = () => {
    const filters = [];
    if (searchTerm) filters.push(`검색: "${searchTerm}"`);
    if (filterStatus !== '전체') filters.push(`상태: ${filterStatus}`);
    if (selectedJobs.length > 0) filters.push(`직무: ${selectedJobs.join(', ')}`);
    if (selectedExperience.length > 0) filters.push(`경력: ${selectedExperience.join(', ')}`);
    return filters.join(' | ');
  };

  // 새 이력서 등록 핸들러들
  const handleResumeModalOpen = () => {
    setIsResumeModalOpen(true);
  };

  const handleResumeModalClose = () => {
    setIsResumeModalOpen(false);
    setResumeFile(null);
    setDocumentType('이력서');
    setIsAnalyzing(false);
    setAnalysisResult(null);
    setIsDragOver(false);
  };

  // 드래그 앤 드롭 이벤트 핸들러들
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      // 파일 타입 검증
      const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (allowedTypes.includes(fileExtension)) {
        setResumeFile(file);
        console.log('드래그 앤 드롭으로 파일이 업로드되었습니다:', file.name);
        // 성공 메시지 표시 (선택사항)
        // alert(`${file.name} 파일이 성공적으로 업로드되었습니다.`);
      } else {
        alert('지원하지 않는 파일 형식입니다. PDF, DOC, DOCX, TXT 파일만 업로드 가능합니다.');
      }
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setResumeFile(file);
      // 파일명에서 기본 정보 추출 시도
      const fileName = file.name.toLowerCase();
      if (fileName.includes('이력서') || fileName.includes('resume')) {
        // 파일명에서 정보 추출 로직
        console.log('이력서 파일이 선택되었습니다:', file.name);
      }
    }
  };

  const handleResumeDataChange = (field, value) => {
    setResumeData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSkillsChange = (skillsString) => {
    const skillsArray = skillsString.split(',').map(skill => skill.trim()).filter(skill => skill);
    setResumeData(prev => ({
      ...prev,
      skills: skillsArray
    }));
  };

  const handleResumeSubmit = async () => {
    try {
      if (!resumeFile) {
        alert('이력서 파일을 선택해주세요.');
        return;
      }

      // 분석 시작
      setIsAnalyzing(true);
      setAnalysisResult(null);

      // FormData 생성 - PDF OCR/Index API 사용
      const formData = new FormData();
      formData.append('file', resumeFile);

      // PDF OCR 업로드 호출 (백엔드에서 MongoDB 저장 + VectorDB 인덱싱 + 지원자 생성)
      const response = await fetch('http://localhost:8000/api/pdf/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || '파일 처리에 실패했습니다.');
      }

      const result = await response.json();

      // 간단한 분석 요약을 화면에 표시(기존 UI 유지)
      const analysisResult = {
        documentType: '이력서',
        fileName: result.file_name || resumeFile.name,
        analysisDate: new Date().toLocaleString(),
        summary: result.summary || '분석 요약 없음',
        skills: [],
        experience: [],
        education: [],
        recommendations: [],
        score: 0,
        processingTime: 0,
        extractedTextLength: 0,
        detailedAnalysis: {},
      };

      setAnalysisResult(analysisResult);
      setIsAnalyzing(false);

      // 신규 지원자 반영을 위해 목록 갱신
      await loadApplicants(0, false);

      alert('PDF 처리 및 인덱싱이 완료되었습니다. 지원자 목록에 반영되었습니다.');
    } catch (error) {
      console.error('이력서 분석 실패:', error);
      alert(`이력서 분석에 실패했습니다: ${error.message}`);
      setIsAnalyzing(false);
    }
  };

  // 상세 분석 결과에서 정보 추출하는 헬퍼 함수들
  const extractSkillsFromAnalysis = (analysisData, documentType) => {
    const skills = [];
    
    // 백엔드에서 이미 필터링된 결과만 전달되므로, 해당하는 섹션만 확인
    if (documentType === '이력서' && analysisData.resume_analysis) {
      if (analysisData.resume_analysis.tech_stack_clarity?.feedback) {
        skills.push(analysisData.resume_analysis.tech_stack_clarity.feedback);
      }
    } else if (documentType === '자기소개서' && analysisData.cover_letter_analysis) {
      // 자기소개서 관련 기술 스택 정보가 있다면 추가
      if (analysisData.cover_letter_analysis.keyword_diversity?.feedback) {
        skills.push(analysisData.cover_letter_analysis.keyword_diversity.feedback);
      }
    } else if (documentType === '포트폴리오' && analysisData.portfolio_analysis) {
      if (analysisData.portfolio_analysis.tech_stack?.feedback) {
        skills.push(analysisData.portfolio_analysis.tech_stack.feedback);
      }
    }
    
    return skills.length > 0 ? skills : ['기술 스택 정보를 추출할 수 없습니다.'];
  };

  const extractExperienceFromAnalysis = (analysisData, documentType) => {
    const experiences = [];
    
    // 백엔드에서 이미 필터링된 결과만 전달되므로, 해당하는 섹션만 확인
    if (documentType === '이력서' && analysisData.resume_analysis) {
      if (analysisData.resume_analysis.experience_clarity?.feedback) {
        experiences.push(analysisData.resume_analysis.experience_clarity.feedback);
      }
      if (analysisData.resume_analysis.achievement_metrics?.feedback) {
        experiences.push(analysisData.resume_analysis.achievement_metrics.feedback);
      }
    } else if (documentType === '자기소개서' && analysisData.cover_letter_analysis) {
      if (analysisData.cover_letter_analysis.unique_experience?.feedback) {
        experiences.push(analysisData.cover_letter_analysis.unique_experience.feedback);
      }
    } else if (documentType === '포트폴리오' && analysisData.portfolio_analysis) {
      if (analysisData.portfolio_analysis.personal_contribution?.feedback) {
        experiences.push(analysisData.portfolio_analysis.personal_contribution.feedback);
      }
    }
    
    return experiences.length > 0 ? experiences.join(' ') : '경력 정보를 추출할 수 없습니다.';
  };

  const extractEducationFromAnalysis = (analysisData, documentType) => {
    // 백엔드에서 이미 필터링된 결과만 전달되므로, 해당하는 섹션만 확인
    if (documentType === '이력서' && analysisData.resume_analysis?.basic_info_completeness?.feedback) {
      return analysisData.resume_analysis.basic_info_completeness.feedback;
    } else if (documentType === '자기소개서' && analysisData.cover_letter_analysis?.job_understanding?.feedback) {
      return analysisData.cover_letter_analysis.job_understanding.feedback;
    } else if (documentType === '포트폴리오' && analysisData.portfolio_analysis?.project_overview?.feedback) {
      return analysisData.portfolio_analysis.project_overview.feedback;
    }
    return '학력 정보를 추출할 수 없습니다.';
  };

  const extractRecommendationsFromAnalysis = (analysisData, documentType) => {
    // 선택한 항목에 대한 요약 정보 반환
    if (documentType === '이력서' && analysisData.resume_analysis) {
      const itemCount = Object.keys(analysisData.resume_analysis).length;
      const totalScore = analysisData.overall_summary.total_score;
      return [`이력서 분석 완료: 총 ${itemCount}개 항목 분석, 평균 점수 ${totalScore}/10점`];
    } else if (documentType === '자기소개서' && analysisData.cover_letter_analysis) {
      const itemCount = Object.keys(analysisData.cover_letter_analysis).length;
      const totalScore = analysisData.overall_summary.total_score;
      return [`자기소개서 분석 완료: 총 ${itemCount}개 항목 분석, 평균 점수 ${totalScore}/10점`];
    } else if (documentType === '포트폴리오' && analysisData.portfolio_analysis) {
      const itemCount = Object.keys(analysisData.portfolio_analysis).length;
      const totalScore = analysisData.overall_summary.total_score;
      return [`포트폴리오 분석 완료: 총 ${itemCount}개 항목 분석, 평균 점수 ${totalScore}/10점`];
    }
    
    return ['문서 분석이 완료되었습니다.'];
  };

  return (
    <Container>
      <Header>
        <HeaderContent>
          <HeaderLeft>
            <Title>지원자 관리</Title>
            <Subtitle>채용 공고별 지원자 현황을 관리하고 검토하세요</Subtitle>
          </HeaderLeft>
          <HeaderRight>
            <NewResumeButton onClick={handleResumeModalOpen}>
              <FiFileText size={16} />
              새 이력서 등록
            </NewResumeButton>
          </HeaderRight>
        </HeaderContent>
        {/* 로딩 상태 표시 */}
        {isLoading && (
          <LoadingOverlay>
            <LoadingSpinner>
              <div className="spinner"></div>
              <span>데이터를 불러오는 중...</span>
            </LoadingSpinner>
          </LoadingOverlay>
        )}
      </Header>

      <StatsGrid>
        <StatCard
          key={`total-${stats.total}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
        >
          <StatValue
            key={stats.total}
            initial={{ scale: 1 }}
            animate={{ scale: [1, 1.02, 1] }}
            transition={{ duration: 0.1 }}
          >
            {stats.total}
          </StatValue>
          <StatLabel>총 지원자</StatLabel>
        </StatCard>
        <StatCard
          key={`passed-${stats.passed}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <StatValue
            key={stats.passed}
            initial={{ scale: 1 }}
            animate={{ scale: [1, 1.02, 1] }}
            transition={{ duration: 0.1 }}
          >
            {stats.passed}
          </StatValue>
          <StatLabel>서류 합격</StatLabel>
        </StatCard>
                 <StatCard
           key={`waiting-${stats.waiting}`}
           initial={{ opacity: 0, y: 20 }}
           animate={{ opacity: 1, y: 0 }}
           transition={{ delay: 0.15 }}
         >
           <StatValue
             key={stats.waiting}
             initial={{ scale: 1 }}
             animate={{ scale: [1, 1.02, 1] }}
             transition={{ duration: 0.1 }}
           >
             {stats.waiting}
           </StatValue>
           <StatLabel>보류</StatLabel>
         </StatCard>
        <StatCard
          key={`rejected-${stats.rejected}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <StatValue
            key={stats.rejected}
            initial={{ scale: 1 }}
            animate={{ scale: [1, 1.02, 1] }}
            transition={{ duration: 0.1 }}
          >
            {stats.rejected}
          </StatValue>
          <StatLabel>서류 불합격</StatLabel>
        </StatCard>
      </StatsGrid>

      <SearchBar>
        <SearchSection>
          <SearchInput
            type="text"
            placeholder={hasActiveFilters ? getFilterStatusText() : "지원자 이름,직무,기술스택을 입력하세요"}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <FilterButton onClick={handleFilterClick} hasActiveFilters={hasActiveFilters}>
            <FiFilter size={16} />
            필터 {hasActiveFilters && <FilterBadge>{selectedJobs.length + selectedExperience.length + (filterStatus !== '전체' ? 1 : 0)}</FilterBadge>}
          </FilterButton>
        </SearchSection>
        <ViewModeSection>
                              <ViewModeButton
                      active={viewMode === 'grid'}
                      onClick={() => handleViewModeChange('grid')}
                    >
                      <FiGrid size={14} />
                      그리드
                    </ViewModeButton>
                    <ViewModeButton
                      active={viewMode === 'board'}
                      onClick={() => handleViewModeChange('board')}
                    >
                      <FiList size={14} />
                      게시판
                    </ViewModeButton>
        </ViewModeSection>
      </SearchBar>

      {/* 게시판 보기 헤더 */}
      {viewMode === 'board' && (
        <>
          {/* 고정된 액션 바 */}
          <FixedActionBar>
            <SelectionInfo>
              <FiCheck size={14} />
              {selectedApplicants.length}개 선택됨
            </SelectionInfo>
            <ActionButtonsGroup>
              <FixedPassButton
                onClick={() => handleBulkStatusUpdate('서류합격')}
                disabled={selectedApplicants.length === 0}
              >
                <FiCheck size={12} />
                합격
              </FixedPassButton>
              <FixedPendingButton
                onClick={() => handleBulkStatusUpdate('보류')}
                disabled={selectedApplicants.length === 0}
              >
                <FiClock size={12} />
                보류
              </FixedPendingButton>
              <FixedRejectButton
                onClick={() => handleBulkStatusUpdate('서류불합격')}
                disabled={selectedApplicants.length === 0}
              >
                <FiX size={12} />
                불합격
              </FixedRejectButton>
            </ActionButtonsGroup>
          </FixedActionBar>
          
          <HeaderRowBoard>
            <HeaderCheckbox>
              <CheckboxInput
                type="checkbox"
                checked={selectAll}
                onChange={handleSelectAll}
              />
            </HeaderCheckbox>
            <HeaderAvatar></HeaderAvatar>
            <HeaderName>이름</HeaderName>
            <HeaderPosition>직무</HeaderPosition>
            <HeaderEmail>이메일</HeaderEmail>
            <HeaderPhone>전화번호</HeaderPhone>
            <HeaderSkills>기술스택</HeaderSkills>
            <HeaderDate>지원일</HeaderDate>
            <HeaderRanks>각 항목별 등수</HeaderRanks>
            <HeaderActions>상태</HeaderActions>
          </HeaderRowBoard>
        </>
      )}

      {viewMode === 'grid' ? (
        <ApplicantsGrid viewMode={viewMode}>
          {paginatedApplicants.length > 0 ? (
            paginatedApplicants.map((applicant, index) => (
              <MemoizedApplicantCard
                key={applicant._id || applicant.id || `${index}`}
                applicant={applicant}
                onCardClick={handleCardClick}
                onStatusUpdate={handleUpdateStatus}
              />
            ))
          ) : (
            <NoResultsMessage>
              <FiSearch size={48} />
              <h3>검색 결과가 없습니다</h3>
              <p>다른 검색어나 필터 조건을 시도해보세요.</p>
            </NoResultsMessage>
          )}
        </ApplicantsGrid>
      ) : (
        <ApplicantsBoard>
            {paginatedApplicants.length > 0 ? (
              paginatedApplicants.map((applicant, index) => (
                <ApplicantCardBoard
                  key={applicant._id || applicant.id || `${index}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05, duration: 0.1 }}
                  onClick={() => handleCardClick(applicant)}
                  onMouseEnter={() => setHoveredApplicant(applicant.id)}
                  onMouseLeave={() => setHoveredApplicant(null)}
                  isHovered={hoveredApplicant === applicant.id}
                >
                  <ApplicantHeaderBoard>
                    <ApplicantCheckbox onClick={(e) => e.stopPropagation()}>
                      <CheckboxInput
                        type="checkbox"
                        checked={selectedApplicants.includes(applicant.id)}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleSelectApplicant(applicant.id);
                        }}
                      />
                    </ApplicantCheckbox>
                    <ApplicantInfoBoard>
                      <AiSuitabilityAvatarBoard percentage={applicant.aiSuitability}>
                        {applicant.aiSuitability}%
                      </AiSuitabilityAvatarBoard>
                      <ApplicantDetailsBoard>
                        <ApplicantNameBoard>{applicant.name}</ApplicantNameBoard>
                        <ApplicantPositionBoard>{applicant.position}</ApplicantPositionBoard>
                      </ApplicantDetailsBoard>
                    </ApplicantInfoBoard>
                    <ApplicantEmailBoard>
                      <ContactItem>
                        <FiMail size={10} />
                        {applicant.email}
                      </ContactItem>
                    </ApplicantEmailBoard>
                    <ApplicantPhoneBoard>
                      <ContactItem>
                        <FiPhone size={10} />
                        {applicant.phone}
                      </ContactItem>
                    </ApplicantPhoneBoard>
                    <ApplicantSkillsBoard>
                      {applicant.skills.slice(0, 3).map((skill, skillIndex) => (
                        <SkillTagBoard key={skillIndex}>
                          {skill}
                        </SkillTagBoard>
                      ))}
                      {applicant.skills.length > 3 && (
                        <SkillTagBoard>+{applicant.skills.length - 3}</SkillTagBoard>
                      )}
                    </ApplicantSkillsBoard>
                    <ApplicantDateBoard>{applicant.appliedDate}</ApplicantDateBoard>
                    <ApplicantRanksBoard>
                      <RankItem>
                        <span>이력서</span>
                        <RankBadge rank={applicant.ranks?.resume || 0}>
                          {applicant.ranks?.resume || 0}
                        </RankBadge>
                      </RankItem>
                      <RankItem>
                        <span>자소서</span>
                        <RankBadge rank={applicant.ranks?.coverLetter || 0}>
                          {applicant.ranks?.coverLetter || 0}
                        </RankBadge>
                      </RankItem>
                      <RankItem>
                        <span>포폴</span>
                        <RankBadge rank={applicant.ranks?.portfolio || 0}>
                          {applicant.ranks?.portfolio || 0}
                        </RankBadge>
                      </RankItem>
                      <RankItem>
                        <span>총점</span>
                        <RankBadge rank={applicant.ranks?.total || 0}>
                          {applicant.ranks?.total || 0}
                        </RankBadge>
                      </RankItem>
                    </ApplicantRanksBoard>
                    {applicant.status !== '지원' && (
                      <StatusColumnWrapper>
                                              <StatusBadge 
                        status={applicant.status}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.08, ease: "easeOut" }}
                      >
                        {applicant.status}
                      </StatusBadge>
                      </StatusColumnWrapper>
                    )}
                  </ApplicantHeaderBoard>
                </ApplicantCardBoard>
              ))
            ) : (
              <NoResultsMessage>
                <FiSearch size={48} />
                <h3>검색 결과가 없습니다</h3>
                <p>다른 검색어나 필터 조건을 시도해보세요.</p>
              </NoResultsMessage>
            )}
          </ApplicantsBoard>
        )}

      {/* 무한 스크롤 로딩 */}
      {hasMore && !isLoading && (
        <LoadMoreButton onClick={handleLoadMore}>
          더 많은 지원자 보기
        </LoadMoreButton>
      )}

      {/* 더 이상 데이터가 없을 때 */}
      {!hasMore && paginatedApplicants.length > 0 && (
        <EndMessage>
          모든 지원자를 불러왔습니다.
        </EndMessage>
      )}

      {/* 지원자 상세 모달 */}
      <AnimatePresence>
        {isModalOpen && selectedApplicant && (
          <ModalOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleCloseModal}
          >
            <ModalContent
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <ModalHeader>
                <ModalTitle>지원자 상세 정보</ModalTitle>
                <CloseButton onClick={handleCloseModal}>&times;</CloseButton>
              </ModalHeader>

              <ProfileSection>
                <SectionTitle>
                  <FiUser size={20} />
                  기본 정보
                </SectionTitle>
                <ProfileGrid>
                  <ProfileItem>
                    <ProfileLabel>이름</ProfileLabel>
                    <ProfileValue>{selectedApplicant.name}</ProfileValue>
                  </ProfileItem>
                  <ProfileItem>
                    <ProfileLabel>경력</ProfileLabel>
                    <ProfileValue>{selectedApplicant.experience}</ProfileValue>
                  </ProfileItem>
                  <ProfileItem>
                    <ProfileLabel>희망부서</ProfileLabel>
                    <ProfileValue>{selectedApplicant.department}</ProfileValue>
                  </ProfileItem>
                  <ProfileItem>
                    <ProfileLabel>희망직책</ProfileLabel>
                    <ProfileValue>{selectedApplicant.position}</ProfileValue>
                  </ProfileItem>
                  {selectedApplicant?.documents?.ocr_fields && (
                    <>
                      <ProfileItem>
                        <ProfileLabel>이메일(추출)</ProfileLabel>
                        <ProfileValue>
                          {(selectedApplicant.documents.ocr_fields.email || []).join(', ')}
                        </ProfileValue>
                      </ProfileItem>
                      <ProfileItem>
                        <ProfileLabel>전화번호(추출)</ProfileLabel>
                        <ProfileValue>
                          {(selectedApplicant.documents.ocr_fields.phone || []).join(', ')}
                        </ProfileValue>
                      </ProfileItem>
                      {selectedApplicant.documents.ocr_fields.periods?.length > 0 && (
                        <ProfileItem>
                          <ProfileLabel>경력기간(추정)</ProfileLabel>
                          <ProfileValue>
                            {selectedApplicant.documents.ocr_fields.periods.join(', ')}
                          </ProfileValue>
                        </ProfileItem>
                      )}
                    </>
                  )}
                </ProfileGrid>
              </ProfileSection>

              <SkillsSection>
                <SkillsTitle>
                  <FiCode size={20} />
                  기술스택
                </SkillsTitle>
                <SkillsGrid>
                  {selectedApplicant.skills.map((skill, index) => (
                    <SkillTag key={index}>
                      {skill}
                    </SkillTag>
                  ))}
                </SkillsGrid>
              </SkillsSection>

              <SummarySection>
                <SummaryTitle>
                  <FiFile size={20} />
                  AI 분석 요약
                </SummaryTitle>
                <SummaryText>
                  {selectedApplicant.summary}
                </SummaryText>
              </SummarySection>

              <DocumentButtons>
                <DocumentButton onClick={() => handleDocumentClick('resume', selectedApplicant)}>
                  <FiFileText size={16} />
                  이력서
                </DocumentButton>
                <DocumentButton onClick={() => handleDocumentClick('coverLetter', selectedApplicant)}>
                  <FiMessageSquare size={16} />
                  자소서
                </DocumentButton>
                <DocumentButton onClick={() => handleDocumentClick('portfolio', selectedApplicant)}>
                  <FiCode size={16} />
                  포트폴리오
                </DocumentButton>
              </DocumentButtons>
            </ModalContent>
          </ModalOverlay>
        )}
      </AnimatePresence>

      {/* 문서 모달 */}
      <AnimatePresence>
        {documentModal.isOpen && documentModal.applicant && (
          <DocumentModalOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleCloseDocumentModal}
          >
            <DocumentModalContent
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <DocumentModalHeader>
                <DocumentModalTitle>
                  {documentModal.type === 'resume' && '이력서'}
                  {documentModal.type === 'coverLetter' && '자기소개서'}
                  {documentModal.type === 'portfolio' && '포트폴리오'}
                  - {documentModal.applicant.name}
                </DocumentModalTitle>
                <DocumentHeaderActions>
                  <DocumentOriginalButton>
                    원본보기
                  </DocumentOriginalButton>
                  <DocumentCloseButton onClick={handleCloseDocumentModal}>&times;</DocumentCloseButton>
                </DocumentHeaderActions>
              </DocumentModalHeader>

              <DocumentContent>
                {documentModal.type === 'resume' && documentModal.applicant.documents?.resume && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>개인정보</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>이름</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.documents.resume.personalInfo.name}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>이메일</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.documents.resume.personalInfo.email}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>연락처</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.documents.resume.personalInfo.phone}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>주소</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.documents.resume.personalInfo.address}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>학력사항</DocumentSectionTitle>
                      {documentModal.applicant.documents.resume.education.map((edu, index) => (
                        <DocumentCard key={index}>
                          <DocumentCardTitle>{edu.school}</DocumentCardTitle>
                          <DocumentCardText>{edu.major} ({edu.degree})</DocumentCardText>
                          <DocumentCardText>기간: {edu.period}</DocumentCardText>
                          <DocumentCardText>학점: {edu.gpa}</DocumentCardText>
                        </DocumentCard>
                      ))}
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>경력사항</DocumentSectionTitle>
                      {documentModal.applicant.documents.resume.experience.map((exp, index) => (
                        <DocumentCard key={index}>
                          <DocumentCardTitle>{exp.company} - {exp.position}</DocumentCardTitle>
                          <DocumentCardText>기간: {exp.period}</DocumentCardText>
                          <DocumentCardText>{exp.description}</DocumentCardText>
                        </DocumentCard>
                      ))}
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>기술스택</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>프로그래밍 언어</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.documents.resume.skills.programming.join(', ')}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>개발 도구</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.documents.resume.skills.tools.join(', ')}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>언어</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.documents.resume.skills.languages.join(', ')}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>
                  </>
                )}

                {documentModal.type === 'coverLetter' && documentModal.applicant.documents?.coverLetter && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>지원 동기</DocumentSectionTitle>
                      <DocumentText>{documentModal.applicant.documents.coverLetter.motivation}</DocumentText>
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>나의 강점</DocumentSectionTitle>
                      <DocumentList>
                        {documentModal.applicant.documents.coverLetter.strengths.map((strength, index) => (
                          <DocumentListItem key={index}>{strength}</DocumentListItem>
                        ))}
                      </DocumentList>
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>향후 목표</DocumentSectionTitle>
                      <DocumentText>{documentModal.applicant.documents.coverLetter.goals}</DocumentText>
                    </DocumentSection>
                  </>
                )}

                {documentModal.type === 'portfolio' && documentModal.applicant.documents?.portfolio && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>프로젝트</DocumentSectionTitle>
                      {documentModal.applicant.documents.portfolio.projects.map((project, index) => (
                        <DocumentCard key={index}>
                          <DocumentCardTitle>{project.title}</DocumentCardTitle>
                          <DocumentCardText>{project.description}</DocumentCardText>
                          <DocumentCardText><strong>기술스택:</strong> {project.technologies.join(', ')}</DocumentCardText>
                          <DocumentCardText><strong>주요 기능:</strong></DocumentCardText>
                          <DocumentList>
                            {project.features.map((feature, idx) => (
                              <DocumentListItem key={idx}>{feature}</DocumentListItem>
                            ))}
                          </DocumentList>
                          <DocumentCardText><strong>GitHub:</strong> <a href={project.github} target="_blank" rel="noopener noreferrer">{project.github}</a></DocumentCardText>
                          <DocumentCardText><strong>Demo:</strong> <a href={project.demo} target="_blank" rel="noopener noreferrer">{project.demo}</a></DocumentCardText>
                        </DocumentCard>
                      ))}
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>성과 및 수상</DocumentSectionTitle>
                      <DocumentList>
                        {documentModal.applicant.documents.portfolio.achievements.map((achievement, index) => (
                          <DocumentListItem key={index}>{achievement}</DocumentListItem>
                        ))}
                      </DocumentList>
                    </DocumentSection>
                  </>
                )}
              </DocumentContent>
            </DocumentModalContent>
          </DocumentModalOverlay>
        )}
      </AnimatePresence>

      {/* 필터 모달 */}
      <AnimatePresence>
        {filterModal && (
          <FilterModalOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleCloseFilterModal}
          >
            <FilterModalContent
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <FilterModalHeader>
                <FilterModalTitle>필터</FilterModalTitle>
                <FilterCloseButton onClick={handleCloseFilterModal}>&times;</FilterCloseButton>
              </FilterModalHeader>

              <FilterGrid>
                <FilterColumn>
                  <FilterSection>
                    <FilterSectionTitle>직무</FilterSectionTitle>
                    <CheckboxGroup>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedJobs.includes('프론트엔드')}
                          onChange={() => handleJobChange('프론트엔드')}
                        />
                        프론트엔드
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedJobs.includes('풀스택')}
                          onChange={() => handleJobChange('풀스택')}
                        />
                        풀스택
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedJobs.includes('PM')}
                          onChange={() => handleJobChange('PM')}
                        />
                        PM
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedJobs.includes('DevOps')}
                          onChange={() => handleJobChange('DevOps')}
                        />
                        DevOps
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedJobs.includes('백엔드')}
                          onChange={() => handleJobChange('백엔드')}
                        />
                        백엔드
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedJobs.includes('데이터 분석')}
                          onChange={() => handleJobChange('데이터 분석')}
                        />
                        데이터 분석
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedJobs.includes('UI/UX')}
                          onChange={() => handleJobChange('UI/UX')}
                        />
                        UI/UX
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedJobs.includes('QA')}
                          onChange={() => handleJobChange('QA')}
                        />
                        QA
                      </CheckboxItem>
                    </CheckboxGroup>
                  </FilterSection>
                </FilterColumn>

                <FilterColumn>
                  <FilterSection>
                    <FilterSectionTitle>경력</FilterSectionTitle>
                    <CheckboxGroup>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedExperience.includes('신입')}
                          onChange={() => handleExperienceChange('신입')}
                        />
                        신입
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedExperience.includes('1-3년')}
                          onChange={() => handleExperienceChange('1-3년')}
                        />
                        1-3년
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedExperience.includes('3-5년')}
                          onChange={() => handleExperienceChange('3-5년')}
                        />
                        3-5년
                      </CheckboxItem>
                      <CheckboxItem>
                        <Checkbox
                          type="checkbox"
                          checked={selectedExperience.includes('5년이상')}
                          onChange={() => handleExperienceChange('5년이상')}
                        />
                        5년이상
                      </CheckboxItem>
                    </CheckboxGroup>
                  </FilterSection>
                </FilterColumn>
              </FilterGrid>

              <FilterButtonGroup>
                <ResetButton onClick={handleResetFilter}>
                  초기화
                </ResetButton>
                <ApplyButton onClick={handleApplyFilter}>
                  적용
                </ApplyButton>
              </FilterButtonGroup>
            </FilterModalContent>
          </FilterModalOverlay>
        )}
      </AnimatePresence>

      {/* 새 이력서 등록 모달 */}
      <AnimatePresence>
        {isResumeModalOpen && (
          <ResumeModalOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleResumeModalClose}
          >
            <ResumeModalContent
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <ResumeModalHeader>
                <ResumeModalTitle>새 이력서 등록</ResumeModalTitle>
                <ResumeModalCloseButton onClick={handleResumeModalClose}>&times;</ResumeModalCloseButton>
              </ResumeModalHeader>

              <ResumeModalBody>
                <ResumeFormSection>
                  <ResumeFormTitle>문서 업로드</ResumeFormTitle>
                  <DocumentUploadContainer>
                    <DocumentTypeSection>
                      <DocumentTypeLabel>문서 유형</DocumentTypeLabel>
                      <DocumentTypeSelect
                        value={documentType}
                        onChange={(e) => setDocumentType(e.target.value)}
                      >
                        <option value="이력서">이력서</option>
                        <option value="자소서">자소서</option>
                        <option value="포트폴리오">포트폴리오</option>
                      </DocumentTypeSelect>
                    </DocumentTypeSection>
                    
                    <FileUploadArea
                      isDragOver={isDragOver}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                    >
                      <FileUploadInput
                        type="file"
                        accept=".pdf,.doc,.docx,.txt"
                        onChange={handleFileChange}
                        id="resume-file"
                      />
                      <FileUploadLabel htmlFor="resume-file">
                        {resumeFile ? (
                          <FileSelected>
                            <FiFile size={20} />
                            <span>{resumeFile.name}</span>
                          </FileSelected>
                        ) : (
                          <FileUploadPlaceholder>
                            {isDragOver ? (
                              <FiFile size={32} style={{ color: 'var(--primary-color)' }} />
                            ) : (
                              <FiFileText size={24} />
                            )}
                            <span>
                              {isDragOver 
                                ? '파일을 여기에 놓으세요' 
                                : `${documentType} 파일을 선택하거나 드래그하세요`
                              }
                            </span>
                            <small>PDF, DOC, DOCX, TXT 파일 지원</small>
                          </FileUploadPlaceholder>
                        )}
                      </FileUploadLabel>
                    </FileUploadArea>
                  </DocumentUploadContainer>
                </ResumeFormSection>


              </ResumeModalBody>

              {isAnalyzing && (
                <ResumeAnalysisSection>
                  <ResumeAnalysisTitle>분석 중입니다...</ResumeAnalysisTitle>
                  <ResumeAnalysisSpinner>
                    <div className="spinner"></div>
                    <span>AI가 문서를 분석하고 있습니다</span>
                  </ResumeAnalysisSpinner>
                </ResumeAnalysisSection>
              )}

              {analysisResult && (
                <ResumeAnalysisSection>
                  <ResumeAnalysisTitle>분석 결과</ResumeAnalysisTitle>
                  <ResumeAnalysisContent>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>문서 유형:</ResumeAnalysisLabel>
                      <ResumeAnalysisValue>{analysisResult.documentType}</ResumeAnalysisValue>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>파일명:</ResumeAnalysisLabel>
                      <ResumeAnalysisValue>{analysisResult.fileName}</ResumeAnalysisValue>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>분석 일시:</ResumeAnalysisLabel>
                      <ResumeAnalysisValue>{analysisResult.analysisDate}</ResumeAnalysisValue>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>적합도 점수:</ResumeAnalysisLabel>
                      <ResumeAnalysisScore score={analysisResult.score}>
                        {analysisResult.score}점
                      </ResumeAnalysisScore>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>추출된 기술:</ResumeAnalysisLabel>
                      <ResumeAnalysisSkills>
                        {analysisResult.skills.map((skill, index) => (
                          <ResumeSkillTag key={index}>{skill}</ResumeSkillTag>
                        ))}
                      </ResumeAnalysisSkills>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>추천 사항:</ResumeAnalysisLabel>
                      <ResumeAnalysisRecommendations>
                        {analysisResult.recommendations.map((rec, index) => (
                          <ResumeRecommendationItem key={index}>• {rec}</ResumeRecommendationItem>
                        ))}
                      </ResumeAnalysisRecommendations>
                    </ResumeAnalysisItem>
                    {analysisResult.detailedAnalysis && (
                      <ResumeAnalysisItem>
                        <ResumeAnalysisLabel>상세 분석:</ResumeAnalysisLabel>
                        <DetailedAnalysisButton onClick={() => setShowDetailedAnalysis(true)}>
                          <FiBarChart2 size={16} />
                          상세 분석 결과 보기
                        </DetailedAnalysisButton>
                      </ResumeAnalysisItem>
                    )}
                  </ResumeAnalysisContent>
                </ResumeAnalysisSection>
              )}

              <ResumeModalFooter>
                <ResumeModalButton onClick={handleResumeModalClose}>
                  {analysisResult ? '닫기' : '취소'}
                </ResumeModalButton>
                {!isAnalyzing && !analysisResult && (
                  <ResumeModalSubmitButton onClick={handleResumeSubmit}>
                    등록하기
                  </ResumeModalSubmitButton>
                )}
              </ResumeModalFooter>
            </ResumeModalContent>
          </ResumeModalOverlay>
        )}
      </AnimatePresence>

      {/* 상세 분석 모달 */}
      <DetailedAnalysisModal
        isOpen={showDetailedAnalysis}
        onClose={() => setShowDetailedAnalysis(false)}
        analysisData={analysisResult}
      />
    </Container>
  );
};

export default ApplicantManagement; 