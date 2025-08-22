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
  FiBarChart2,
  FiCamera,
  FiGitBranch,
  FiArrowLeft,
  FiUsers
} from 'react-icons/fi';
import DetailedAnalysisModal from '../components/DetailedAnalysisModal';
import GithubSummaryPanel from './PortfolioSummary/GithubSummaryPanel';
import PortfolioSummaryPanel from './PortfolioSummary/PortfolioSummaryPanel';

// 평균 점수 계산 함수
const calculateAverageScore = (analysisData) => {
  if (!analysisData || typeof analysisData !== 'object') return 0;
  
  const scores = Object.values(analysisData)
    .filter(item => item && typeof item === 'object' && 'score' in item)
    .map(item => item.score);
  
  if (scores.length === 0) return 0;
  
  const total = scores.reduce((sum, score) => sum + score, 0);
  return Math.round((total / scores.length) * 10) / 10; // 소수점 첫째자리까지
};

// 이력서 분석 항목 라벨 함수
const getResumeAnalysisLabel = (key) => {
  const labels = {
    basic_info_completeness: '기본정보 완성도',
    job_relevance: '직무 적합성',
    experience_clarity: '경력 명확성',
    tech_stack_clarity: '기술스택 명확성',
    project_recency: '프로젝트 최신성',
    achievement_metrics: '성과 지표',
    readability: '가독성',
    typos_and_errors: '오탈자',
    update_freshness: '최신성'
  };
  return labels[key] || key;
};

// 자기소개서 분석 항목 라벨 함수
const getCoverLetterAnalysisLabel = (key) => {
  const labels = {
    motivation_relevance: '지원 동기',
    problem_solving_STAR: 'STAR 기법',
    quantitative_impact: '정량적 성과',
    job_understanding: '직무 이해도',
    unique_experience: '차별화 경험',
    logical_flow: '논리적 흐름',
    keyword_diversity: '키워드 다양성',
    sentence_readability: '문장 가독성',
    typos_and_errors: '오탈자'
  };
  return labels[key] || key;
};

// 포트폴리오 분석 항목 라벨 함수
const getPortfolioAnalysisLabel = (key) => {
  const labels = {
    project_overview: '프로젝트 개요',
    tech_stack: '기술 스택',
    personal_contribution: '개인 기여도',
    achievement_metrics: '성과 지표',
    visual_quality: '시각적 품질',
    documentation_quality: '문서화 품질',
    job_relevance: '직무 관련성',
    unique_features: '독창적 기능',
    maintainability: '유지보수성'
  };
  return labels[key] || key;
};

// API 서비스 추가
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
      return data.applicants || [];
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
  },

  // 포트폴리오 데이터 조회
  getPortfolioByApplicantId: async (applicantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/portfolios/applicant/${applicantId}`);
      if (!response.ok) {
        throw new Error('포트폴리오 데이터 조회 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('포트폴리오 데이터 조회 오류:', error);
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

const ResumeFormDescription = styled.p`
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.5;
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

const AnalysisScoreDisplay = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
`;

const AnalysisScoreCircle = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
`;

const AnalysisScoreInfo = styled.div`
  flex: 1;
`;

const AnalysisScoreLabel = styled.div`
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
`;

const AnalysisScoreValue = styled.div`
  font-size: 20px;
  font-weight: 700;
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
  opacity: 1;
  transition: opacity 0.2s ease;
`;

const ApplicantActionsBoard = styled.div`
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  opacity: 1;
  transition: opacity 0.2s ease;
  margin-top: 8px;
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

// 포트폴리오 뷰 선택 UI 스타일
const SelectionGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 8px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const SelectionCard = styled(motion.div)`
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  background: white;

  &:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 200, 81, 0.1);
  }
`;

const SelectionIcon = styled.div`
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  font-size: 22px;
  color: white;

  &.github {
    background: linear-gradient(135deg, #24292e, #57606a);
  }

  &.portfolio {
    background: linear-gradient(135deg, #667eea, #764ba2);
  }
`;

const SelectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
`;

const SelectionDesc = styled.p`
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
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

// 샘플 데이터 제거됨 - 이제 MongoDB에서만 데이터를 가져옵니다

// 메모이제이션된 지원자 카드 컴포넌트
const MemoizedApplicantCard = React.memo(({ applicant, onCardClick, onStatusUpdate, getStatusText }) => {
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
          {getStatusText(applicant.status)}
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
          <span>{applicant.skills || '기술 정보 없음'}</span>
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
  // Status 매핑 함수
  const getStatusText = (status) => {
    const statusMap = {
      'pending': '보류',
      'approved': '승인',
      'rejected': '거절',
      '서류합격': '서류합격',
      '최종합격': '최종합격', 
      '서류불합격': '서류불합격',
      '보류': '보류'
    };
    return statusMap[status] || status;
  };

  const [applicants, setApplicants] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('전체');
  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [documentModal, setDocumentModal] = useState({ isOpen: false, type: '', applicant: null, isOriginal: false, similarityData: null, isLoadingSimilarity: false, documentData: null });
  // 포트폴리오 모달 내 뷰 선택 상태: 'select' | 'github' | 'portfolio'
  const [portfolioView, setPortfolioView] = useState('select');
  // 포트폴리오 데이터 상태
  const [portfolioData, setPortfolioData] = useState(null);
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false);
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

  // 유사 인재 추천 상태
  const [similarCandidates, setSimilarCandidates] = useState({
    isLoading: false,
    data: null,
    error: null
  });

  // 페이지네이션 상태
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize] = useState(20);
  const [hasMore, setHasMore] = useState(true);

  // 새 이력서 등록 모달 상태
  const [isResumeModalOpen, setIsResumeModalOpen] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [coverLetterFile, setCoverLetterFile] = useState(null);
  const [portfolioFile, setPortfolioFile] = useState(null);
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
    return (applicants || []).filter(applicant => {
      const searchLower = searchTerm.toLowerCase();
      
      // 검색 필터링 (null/undefined 체크 추가)
      const matchesSearch = (applicant.name || '').toLowerCase().includes(searchLower) ||
                          (applicant.position || '').toLowerCase().includes(searchLower) ||
                          (applicant.email || '').toLowerCase().includes(searchLower) ||
                          (applicant.skills || '').toLowerCase().includes(searchLower);
      
      // 상태 필터링 (한국어 필터를 영어 상태와 매칭)
      const matchesStatus = filterStatus === '전체' || 
                           getStatusText(applicant.status) === filterStatus ||
                           applicant.status === filterStatus;
      
      // 직무 필터링
      const matchesJob = selectedJobs.length === 0 || 
                        selectedJobs.some(job => applicant.position.includes(job));
      
      // 경력 필터링
      const matchesExperience = selectedExperience.length === 0 || 
                              selectedExperience.some(exp => {
                                if (exp === '신입') return applicant.experience.includes('신입') || applicant.experience.includes('0년');
                                if (exp === '1-3년') return applicant.experience.includes('1년') || applicant.experience.includes('2년') || applicant.experience.includes('3년');
                                if (exp === '3-5년') return applicant.experience.includes('4년') || applicant.experience.includes('5년');
                                if (exp === '5년이상') return applicant.experience.includes('6년') || applicant.experience.includes('7년') || applicant.experience.includes('8년') || applicant.experience.includes('9년') || applicant.experience.includes('10년');
                                return false;
                              });
      
      return matchesSearch && matchesStatus && matchesJob && matchesExperience;
    });
  }, [applicants, searchTerm, filterStatus, selectedJobs, selectedExperience]);

  // 메모이제이션된 페이지네이션된 지원자 목록
  const paginatedApplicants = useMemo(() => {
    const startIndex = currentPage * pageSize;
    return filteredApplicants.slice(startIndex, startIndex + pageSize);
  }, [filteredApplicants, currentPage, pageSize]);

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
      
      if (apiApplicants && apiApplicants.length > 0) {
        console.log(`✅ API에서 ${apiApplicants.length}명의 지원자 데이터를 성공적으로 로드했습니다.`);
        
        if (append) {
          setApplicants(prev => [...prev, ...apiApplicants]);
        } else {
          setApplicants(apiApplicants);
        }
        
        setHasMore(apiApplicants.length === pageSize);
      } else {
        console.log('⚠️ API에서 데이터를 찾을 수 없습니다.');
        setApplicants([]);
        setHasMore(false);
      }
    } catch (error) {
      console.error('❌ API 연결 실패:', error);
      console.log('🔄 백엔드 서버 연결을 확인해주세요.');
      setApplicants([]);
      setHasMore(false);
    } finally {
      setIsLoading(false);
    }
  }, [pageSize]);

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
      total: (applicants || []).length,
      passed: (applicants || []).filter(a => a.status === '서류합격' || a.status === '최종합격').length,
      waiting: (applicants || []).filter(a => a.status === '보류').length,
      rejected: (applicants || []).filter(a => a.status === '서류불합격').length
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
        const updatedApplicants = (prev || []).map(applicant => 
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
    
    // 모달 열릴 때 자동으로 유사 인재 분석 시작
    handleSimilarCandidatesAnalysis(applicant);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedApplicant(null);
    // 유사 인재 분석 상태 초기화
    setSimilarCandidates({
      isLoading: false,
      data: null,
      error: null
    });
  };

  const handleDocumentClick = async (type, applicant) => {
    console.log('문서 클릭:', type, applicant);
    
    // applicant 객체에 _id가 없으면 id를 _id로 설정
    const applicantWithId = {
      ...applicant,
      _id: applicant._id || applicant.id
    };
    
    // 모달 먼저 열기
    setDocumentModal({ isOpen: true, type, applicant: applicantWithId, isOriginal: false, similarityData: null, isLoadingSimilarity: false });
    if (type === 'portfolio') {
      setPortfolioView('select');
    }
    
    // 각 문서 타입별로 해당 컬렉션에서 데이터 가져오기
    try {
      let documentData = null;
      const applicantId = applicantWithId._id;
      
      switch (type) {
        case 'resume':
          const resumeResponse = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/resume`);
          if (resumeResponse.ok) {
            documentData = await resumeResponse.json();
            console.log('✅ 이력서 데이터 로드 완료:', documentData);
          } else {
            console.error('❌ 이력서 데이터 로드 실패:', resumeResponse.status);
          }
          break;
          
        case 'coverLetter':
          const coverLetterResponse = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/cover-letter`);
          if (coverLetterResponse.ok) {
            documentData = await coverLetterResponse.json();
            console.log('✅ 자소서 데이터 로드 완료:', documentData);
          } else {
            console.error('❌ 자소서 데이터 로드 실패:', coverLetterResponse.status);
          }
          break;
          
        case 'portfolio':
          const portfolioResponse = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/portfolio`);
          if (portfolioResponse.ok) {
            documentData = await portfolioResponse.json();
            console.log('✅ 포트폴리오 데이터 로드 완료:', documentData);
          } else {
            console.error('❌ 포트폴리오 데이터 로드 실패:', portfolioResponse.status);
          }
          break;
      }
      
      // 문서 데이터를 모달 상태에 저장
      if (documentData) {
        setDocumentModal(prev => ({ 
          ...prev, 
          documentData,
          isLoadingSimilarity: false 
        }));
      }
      
    } catch (error) {
      console.error('❌ 문서 데이터 로드 오류:', error);
      setDocumentModal(prev => ({ ...prev, isLoadingSimilarity: false }));
    }
    
    // 자소서 타입일 때만 유사도 체크 실행
    if (type === 'coverLetter') {
      setDocumentModal(prev => ({ ...prev, isLoadingSimilarity: true }));
      
      try {
        const endpoint = 'coverletter';
        const response = await fetch(`${API_BASE_URL}/api/${endpoint}/similarity-check/${applicantWithId._id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const similarityData = await response.json();
          console.log('✅ 유사도 체크 완료:', similarityData);
          
          setDocumentModal(prev => ({ 
            ...prev, 
            similarityData, 
            isLoadingSimilarity: false 
          }));
        } else {
          console.error('❌ 유사도 체크 실패:', response.status);
          setDocumentModal(prev => ({ ...prev, isLoadingSimilarity: false }));
        }
      } catch (error) {
        console.error('❌ 유사도 체크 오류:', error);
        setDocumentModal(prev => ({ ...prev, isLoadingSimilarity: false }));
      }
    }
  };

  const handleOriginalClick = () => {
    setDocumentModal(prev => ({ ...prev, isOriginal: !prev.isOriginal }));
  };

  const handleCloseDocumentModal = () => {
    setDocumentModal({ isOpen: false, type: '', applicant: null, isOriginal: false, similarityData: null, isLoadingSimilarity: false, documentData: null });
    setPortfolioView('select');
    setPortfolioData(null);
  };

  // 포트폴리오 데이터 가져오기
  const loadPortfolioData = async (applicantId) => {
    try {
      setIsLoadingPortfolio(true);
      console.log('포트폴리오 데이터를 불러오는 중...', applicantId);
      
      if (!applicantId) {
        console.error('지원자 ID가 없습니다');
        setPortfolioData(null);
        return;
      }
      
      const portfolio = await api.getPortfolioByApplicantId(applicantId);
      console.log('포트폴리오 데이터:', portfolio);
      
      setPortfolioData(portfolio);
    } catch (error) {
      console.error('포트폴리오 데이터 로드 오류:', error);
      setPortfolioData(null);
    } finally {
      setIsLoadingPortfolio(false);
    }
  };

  const handleSimilarApplicantClick = async (similarData) => {
    try {
      // 유사한 지원자의 ID를 사용해서 전체 지원자 정보를 가져옴
      const response = await fetch(`${API_BASE_URL}/api/applicants/${similarData.resume_id}`);
      if (response.ok) {
        const applicantData = await response.json();
        
        // 현재 모달의 타입을 기억해둠 (자소서에서 클릭했으면 자소서를, 이력서에서 클릭했으면 이력서를)
        const currentModalType = documentModal.type;
        
        // 현재 모달을 닫고 새로운 모달을 열기
        setDocumentModal({ isOpen: false, type: '', applicant: null, isOriginal: false, similarityData: null, isLoadingSimilarity: false });
        
        // 약간의 딜레이 후에 새로운 모달 열기 (부드러운 전환을 위해)
        setTimeout(() => {
          setDocumentModal({
            isOpen: true,
            type: currentModalType, // 현재 모달의 타입을 유지
            applicant: applicantData,
            isOriginal: true,
            similarityData: null,
            isLoadingSimilarity: false
          });
        }, 100);
      } else {
        console.error('지원자 정보를 가져오는 데 실패했습니다.');
      }
    } catch (error) {
      console.error('지원자 정보 요청 중 오류:', error);
    }
  };

  // 유사 인재 추천 핸들러
  const handleSimilarCandidatesAnalysis = async (applicant) => {
    setSimilarCandidates({
      isLoading: true,
      data: null,
      error: null
    });

    try {
      console.log('🔍 유사 인재 분석 시작:', applicant.id);
      const response = await fetch(`${API_BASE_URL}/api/applicants/similar-recommendation/${applicant.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();
      
      if (result.success && result.data?.results) {
        console.log('✅ 하이브리드 유사 인재 분석 완료:', result.data.results.length, '명');
        console.log('📊 검색 방법별 결과: 벡터', result.data.vector_count, '개, 키워드', result.data.keyword_count, '개');
        setSimilarCandidates({
          isLoading: false,
          data: result.data.results,
          error: null
        });
      } else {
        console.log('⚠️ 유사 인재를 찾지 못함:', result.message);
        setSimilarCandidates({
          isLoading: false,
          data: [],
          error: result.message || '유사 인재를 찾을 수 없습니다.'
        });
      }
    } catch (error) {
      console.error('❌ 유사 인재 분석 실패:', error);
      setSimilarCandidates({
        isLoading: false,
        data: null,
        error: '네트워크 오류가 발생했습니다.'
      });
    }
  };

  const handleViewSimilarCandidate = (candidateResume) => {
    // 유사 인재의 상세 정보를 모달로 표시
    setSelectedApplicant(candidateResume);
    // 새로운 지원자에 대해 유사 인재 분석 시작
    handleSimilarCandidatesAnalysis(candidateResume);
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

  // 지원자 삭제 핸들러
  const handleDeleteApplicant = async (applicantId) => {
    if (!window.confirm('정말로 이 지원자를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        console.log('✅ 지원자 삭제 성공');
        
        // 모달 닫기
        handleCloseModal();
        
        // 지원자 목록 새로고침
        setCurrentPage(0);
        loadApplicants(0, false);
        
        // 통계 업데이트
        loadStats();
        
        alert('지원자가 성공적으로 삭제되었습니다.');
      } else {
        const errorData = await response.json();
        console.error('❌ 지원자 삭제 실패:', errorData);
        alert(`지원자 삭제 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('❌ 지원자 삭제 오류:', error);
      alert('지원자 삭제 중 오류가 발생했습니다.');
    }
  };

  // 체크박스 관련 핸들러들
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedApplicants([]);
      setSelectAll(false);
    } else {
      setSelectedApplicants((paginatedApplicants || []).map(applicant => applicant.id));
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
    if ((selectedJobs || []).length > 0) filters.push(`직무: ${(selectedJobs || []).join(', ')}`);
    if ((selectedExperience || []).length > 0) filters.push(`경력: ${(selectedExperience || []).join(', ')}`);
    return filters.join(' | ');
  };

  // 새 이력서 등록 핸들러들
  const handleResumeModalOpen = () => {
    setIsResumeModalOpen(true);
  };

  const handleResumeModalClose = () => {
    setIsResumeModalOpen(false);
    setResumeFile(null);
    setCoverLetterFile(null);
    setPortfolioFile(null);
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
        // 파일명으로 이력서인지 자기소개서인지 포트폴리오인지 판단
        const fileName = file.name.toLowerCase();
        if (fileName.includes('자기소개서') || fileName.includes('cover') || fileName.includes('coverletter')) {
          setCoverLetterFile(file);
          console.log('드래그 앤 드롭으로 자기소개서 파일이 업로드되었습니다:', file.name);
        } else if (fileName.includes('포트폴리오') || fileName.includes('portfolio')) {
          setPortfolioFile(file);
          console.log('드래그 앤 드롭으로 포트폴리오 파일이 업로드되었습니다:', file.name);
        } else {
          setResumeFile(file);
          console.log('드래그 앤 드롭으로 이력서 파일이 업로드되었습니다:', file.name);
        }
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

  const handleCoverFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setCoverLetterFile(file);
      // 파일명에서 기본 정보 추출 시도
      const fileName = file.name.toLowerCase();
      if (fileName.includes('자기소개서') || fileName.includes('cover') || fileName.includes('coverletter')) {
        // 파일명에서 정보 추출 로직
        console.log('자기소개서 파일이 선택되었습니다:', file.name);
      }
    }
  };

  const handlePortfolioFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setPortfolioFile(file);
      console.log('포트폴리오 파일이 선택되었습니다:', file.name);
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
      console.log('🚀 통합 문서 업로드 시작');
      console.log('📁 선택된 파일들:', { resumeFile, coverLetterFile, portfolioFile });
      
      // 최소 하나의 파일은 필요
      if (!resumeFile && !coverLetterFile && !portfolioFile) {
        alert('이력서, 자기소개서, 또는 포트폴리오 파일 중 하나는 선택해주세요.');
        return;
      }

      // 파일 내용 미리보기 (디버깅용)
      if (resumeFile) {
        console.log('📄 이력서 파일 정보:', {
          name: resumeFile.name,
          size: resumeFile.size,
          type: resumeFile.type,
          lastModified: new Date(resumeFile.lastModified).toLocaleString()
        });
      }
      
      if (coverLetterFile) {
        console.log('📝 자기소개서 파일 정보:', {
          name: coverLetterFile.name,
          size: coverLetterFile.size,
          type: coverLetterFile.type,
          lastModified: new Date(coverLetterFile.lastModified).toLocaleString()
        });
      }

      if (portfolioFile) {
        console.log('📁 포트폴리오 파일 정보:', {
          name: portfolioFile.name,
          size: portfolioFile.size,
          type: portfolioFile.type,
          lastModified: new Date(portfolioFile.lastModified).toLocaleString()
        });
      }

      // 파일 유효성 검사 강화
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
              const maxSize = 50 * 1024 * 1024; // 50MB
      
      if (resumeFile) {
        if (!allowedTypes.includes(resumeFile.type) && !resumeFile.name.match(/\.(pdf|doc|docx|txt)$/i)) {
          alert('이력서 파일 형식이 지원되지 않습니다. PDF, DOC, DOCX, TXT 파일만 업로드 가능합니다.');
          return;
        }
        if (resumeFile.size > maxSize) {
                      alert('이력서 파일 크기가 50MB를 초과합니다.');
          return;
        }
      }
      
      if (coverLetterFile) {
        if (!allowedTypes.includes(coverLetterFile.type) && !coverLetterFile.name.match(/\.(pdf|doc|docx|txt)$/i)) {
          alert('자기소개서 파일 형식이 지원되지 않습니다. PDF, DOC, DOCX, TXT 파일만 업로드 가능합니다.');
          return;
        }
        if (coverLetterFile.size > maxSize) {
                      alert('자기소개서 파일 크기가 50MB를 초과합니다.');
          return;
        }
      }

      if (portfolioFile) {
        if (!portfolioFile.type.includes('pdf') && !portfolioFile.name.match(/\.pdf$/i)) {
          alert('포트폴리오 파일은 PDF 형식만 지원됩니다.');
          return;
        }
        if (portfolioFile.size > maxSize) {
                      alert('포트폴리오 파일 크기가 50MB를 초과합니다.');
          return;
        }
      }

      // 분석 시작
      setIsAnalyzing(true);
      setAnalysisResult(null);

      // 통합 업로드 API 호출
      console.log('📤 통합 업로드 API 호출 시작');
      console.log('⏱️ 타임아웃 설정: 10분 (600초)');
      
      const formData = new FormData();
      
      if (resumeFile) {
        console.log('📄 이력서 파일 전송:', {
          name: resumeFile.name,
          size: resumeFile.size,
          type: resumeFile.type
        });
        formData.append('resume_file', resumeFile);
      }
      if (coverLetterFile) {
        console.log('📝 자기소개서 파일 전송:', {
          name: coverLetterFile.name,
          size: coverLetterFile.size,
          type: coverLetterFile.type
        });
        formData.append('cover_letter_file', coverLetterFile);
      }
      if (portfolioFile) {
        console.log('📁 포트폴리오 파일 전송:', {
          name: portfolioFile.name,
          size: portfolioFile.size,
          type: portfolioFile.type
        });
        formData.append('portfolio_file', portfolioFile);
      }

      const response = await fetch(`${API_BASE_URL}/api/integrated-ocr/upload-multiple-documents`, {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(600000) // 10분 타임아웃으로 증가
      });

      if (!response.ok) {
        console.log('❌ 서버 응답 에러:', {
          status: response.status,
          statusText: response.statusText,
          url: response.url
        });
        
        let errorData;
        try {
          errorData = await response.json();
          console.log('📋 에러 응답 데이터:', errorData);
        } catch (parseError) {
          console.log('📋 에러 응답 파싱 실패:', parseError);
          const errorText = await response.text();
          console.log('📋 원본 에러 텍스트:', errorText);
          errorData = { detail: errorText || '알 수 없는 오류' };
        }
        
        throw new Error(`통합 업로드 실패: ${errorData.detail || errorData.message || '알 수 없는 오류'}`);
      }

      const result = await response.json();
      console.log('✅ 통합 업로드 성공:', result);

      // 분석 결과 생성
      const analysisResult = {
        documentType: result.data.uploaded_documents.join(' + '),
        fileName: [resumeFile?.name, coverLetterFile?.name, portfolioFile?.name].filter(Boolean).join(', '),
        analysisDate: new Date().toLocaleString(),
        processingTime: 0,
        extractedTextLength: 0,
        analysisResult: result.data.results,
        uploadResults: Object.entries(result.data.results).map(([type, data]) => ({
          type: type === 'resume' ? 'resume' : type === 'cover_letter' ? 'cover_letter' : 'portfolio',
          result: data
        })),
        applicant: result.data.results.resume?.applicant || result.data.results.cover_letter?.applicant || result.data.results.portfolio?.applicant || null
      };

      setAnalysisResult(analysisResult);
      setIsAnalyzing(false);

      // 성공 메시지
      const uploadedDocs = result.data.uploaded_documents;
      const successMessage = uploadedDocs.length > 1 
        ? `${uploadedDocs.join(', ')} 문서들이 성공적으로 업로드되었습니다!\n\n지원자: ${analysisResult.applicant?.name || 'N/A'}`
        : `${uploadedDocs[0] === 'resume' ? '이력서' : uploadedDocs[0] === 'cover_letter' ? '자기소개서' : '포트폴리오'}가 성공적으로 업로드되었습니다!\n\n지원자: ${analysisResult.applicant?.name || 'N/A'}`;
      
      alert(successMessage);
      
      // 지원자 목록 새로고침
      loadApplicants();
      
    } catch (error) {
      console.error('❌ 통합 문서 업로드 실패:', error);
      
      // 에러 타입별 상세 메시지
      let errorMessage = '문서 업로드에 실패했습니다.';
      
      if (error.name === 'AbortError') {
        errorMessage = '요청 시간이 초과되었습니다. (10분 제한)\n\n대용량 파일이나 여러 파일을 동시에 업로드할 때 시간이 오래 걸릴 수 있습니다.\n\n해결 방법:\n1. 파일 크기를 줄여보세요 (각 파일 10MB 이하 권장)\n2. 한 번에 하나씩 파일을 업로드해보세요\n3. 다시 시도해보세요';
      } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = '네트워크 연결에 실패했습니다.\n\n서버 상태를 확인해주세요.';
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage = '서버에 연결할 수 없습니다.\n\n백엔드 서버가 실행 중인지 확인해주세요.';
      } else {
        errorMessage = `문서 업로드에 실패했습니다:\n${error.message}`;
      }
      
      console.error('🔍 에러 상세 정보:', {
        name: error.name,
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      });
      
      alert(errorMessage);
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
              새 지원자 등록
            </NewResumeButton>
            <NewResumeButton onClick={() => window.open('/pdf-ocr', '_blank')} style={{ marginLeft: '10px', backgroundColor: '#8B5CF6' }}>
              <FiCamera size={16} />
              PDF OCR
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
                key={applicant.id}
                applicant={applicant}
                onCardClick={handleCardClick}
                onStatusUpdate={handleUpdateStatus}
                getStatusText={getStatusText}
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
                  key={applicant.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05, duration: 0.1 }}
                  onClick={() => handleCardClick(applicant)}
                  onMouseEnter={() => setHoveredApplicant(applicant.id)}
                  onMouseLeave={() => setHoveredApplicant(null)}
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
                      {(applicant.skills || '').split(',').slice(0, 3).map((skill, skillIndex) => (
                        <SkillTagBoard key={skillIndex}>
                          {skill.trim()}
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
                        {getStatusText(applicant.status)}
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
                </ProfileGrid>
              </ProfileSection>

              <SkillsSection>
                <SkillsTitle>
                  <FiCode size={20} />
                  기술스택
                </SkillsTitle>
                <SkillsGrid>
                  {(selectedApplicant.skills || '').split(',').map((skill, index) => (
                    <SkillTag key={index}>
                      {skill.trim()}
                    </SkillTag>
                  ))}
                </SkillsGrid>
              </SkillsSection>

              <SummarySection>
                <SummaryTitle>
                  <FiFile size={20} />
                  AI 분석 요약
                </SummaryTitle>
                
                {selectedApplicant.analysisScore && (
                  <AnalysisScoreDisplay>
                    <AnalysisScoreCircle>
                      {selectedApplicant.analysisScore}
                    </AnalysisScoreCircle>
                    <AnalysisScoreInfo>
                      <AnalysisScoreLabel>AI 분석 점수</AnalysisScoreLabel>
                      <AnalysisScoreValue>{selectedApplicant.analysisScore}점</AnalysisScoreValue>
                    </AnalysisScoreInfo>
                  </AnalysisScoreDisplay>
                )}
                
                <SummaryText>
                  {selectedApplicant.summary}
                </SummaryText>
              </SummarySection>

              {/* 유사 인재 추천 섹션 */}
              <SimilarCandidatesSection>
                <SimilarCandidatesTitle>
                  <FiUsers size={20} />
                  유사 인재 추천
                </SimilarCandidatesTitle>
                
                {similarCandidates.isLoading && (
                  <SimilarCandidatesLoading>
                    <SimilarCandidatesSpinner />
                    <div>유사 인재 분석 중입니다...</div>
                  </SimilarCandidatesLoading>
                )}

                {similarCandidates.data && similarCandidates.data.length > 0 && (
                  <SimilarCandidatesList>
                    {similarCandidates.data.map((candidate, index) => (
                      <SimilarCandidateItem key={candidate.applicant?.id || index}>
                        <SimilarCandidateInfo>
                          <SimilarCandidateName>{candidate.applicant?.name || '이름 없음'}</SimilarCandidateName>
                          <SimilarCandidateDetails>
                            {candidate.applicant?.position} | {candidate.applicant?.experience}
                          </SimilarCandidateDetails>
                          <SimilarCandidateScore>
                            유사도: {(candidate.final_score * 100).toFixed(1)}%
                            <SimilarCandidateScoreDetail>
                              (벡터: {(candidate.vector_score * 100).toFixed(1)}%, 키워드: {(candidate.keyword_score * 100).toFixed(1)}%)
                            </SimilarCandidateScoreDetail>
                          </SimilarCandidateScore>
                          <SimilarCandidateMethod>
                            검색방법: {candidate.search_methods?.join(', ') || 'N/A'}
                          </SimilarCandidateMethod>
                        </SimilarCandidateInfo>
                        <SimilarCandidateActions>
                          <SimilarCandidateButton 
                            onClick={() => handleViewSimilarCandidate(candidate.applicant)}
                          >
                            상세보기
                          </SimilarCandidateButton>
                        </SimilarCandidateActions>
                      </SimilarCandidateItem>
                    ))}
                  </SimilarCandidatesList>
                )}

                {similarCandidates.error && (
                  <SimilarCandidatesError>
                    유사 인재 검색 중 오류가 발생했습니다: {similarCandidates.error}
                  </SimilarCandidatesError>
                )}

                {similarCandidates.data && similarCandidates.data.length === 0 && !similarCandidates.isLoading && (
                  <SimilarCandidatesEmpty>
                    유사한 인재를 찾을 수 없습니다.
                  </SimilarCandidatesEmpty>
                )}
              </SimilarCandidatesSection>

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

              <DeleteButton onClick={() => handleDeleteApplicant(selectedApplicant.id)}>
                <FiX size={16} />
                지원자 삭제
              </DeleteButton>
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
                  {documentModal.type === 'coverLetter' && '자소서'}
                  {documentModal.type === 'portfolio' && '포트폴리오'}
                  - {documentModal.applicant.name}
                </DocumentModalTitle>
                <DocumentHeaderActions>
                  <DocumentOriginalButton onClick={handleOriginalClick}>
                    {documentModal.isOriginal ? '요약보기' : '원본보기'}
                  </DocumentOriginalButton>
                  <DocumentCloseButton onClick={handleCloseDocumentModal}>&times;</DocumentCloseButton>
                </DocumentHeaderActions>
              </DocumentModalHeader>

              <DocumentContent>
                {/* 포트폴리오: 선택 화면 */}
                {documentModal.type === 'portfolio' && portfolioView === 'select' && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>포트폴리오 요약 방법 선택</DocumentSectionTitle>
                      <SelectionGrid>
                        <SelectionCard
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => setPortfolioView('github')}
                        >
                          <SelectionIcon className="github">
                            <FiGitBranch />
                          </SelectionIcon>
                          <SelectionTitle>깃헙 요약</SelectionTitle>
                          <SelectionDesc>GitHub URL/아이디로 레포 분석 요약 보기</SelectionDesc>
                        </SelectionCard>
                        <SelectionCard
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => {
                            console.log('포트폴리오 버튼 클릭:', documentModal.applicant);
                            if (documentModal.applicant && documentModal.applicant._id) {
                              setPortfolioView('portfolio');
                              loadPortfolioData(documentModal.applicant._id);
                            } else {
                              console.error('지원자 ID가 없습니다:', documentModal.applicant);
                              alert('지원자 정보를 찾을 수 없습니다.');
                            }
                          }}
                        >
                          <SelectionIcon className="portfolio">
                            <FiCode />
                          </SelectionIcon>
                          <SelectionTitle>포트폴리오 요약</SelectionTitle>
                          <SelectionDesc>등록된 포트폴리오 정보 기반 요약 보기</SelectionDesc>
                        </SelectionCard>
                      </SelectionGrid>
                    </DocumentSection>
                  </>
                )}

                {/* 포트폴리오: 깃헙 요약 화면 */}
                {documentModal.type === 'portfolio' && portfolioView === 'github' && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>
                        <button 
                          onClick={() => setPortfolioView('select')} 
                          style={{ 
                            background: 'transparent', 
                            border: 'none', 
                            cursor: 'pointer', 
                            marginRight: 8, 
                            color: 'var(--text-secondary)'
                          }}
                          aria-label="뒤로"
                        >
                          <FiArrowLeft />
                        </button>
                        깃헙 요약
                      </DocumentSectionTitle>
                      <GithubSummaryPanel />
                    </DocumentSection>
                  </>
                )}

                {/* 포트폴리오: 기존 포트폴리오 상세 */}
                {documentModal.type === 'portfolio' && portfolioView === 'portfolio' && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>
                        <button 
                          onClick={() => setPortfolioView('select')} 
                          style={{ 
                            background: 'transparent', 
                            border: 'none', 
                            cursor: 'pointer', 
                            marginRight: 8, 
                            color: 'var(--text-secondary)'
                          }}
                          aria-label="뒤로"
                        >
                          <FiArrowLeft />
                        </button>
                        포트폴리오
                      </DocumentSectionTitle>
                      {isLoadingPortfolio ? (
                        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                          <div>포트폴리오 데이터를 불러오는 중...</div>
                        </div>
                      ) : (
                        <PortfolioSummaryPanel portfolio={portfolioData} />
                      )}
                    </DocumentSection>
                  </>
                )}

                {/* 이력서 기존 로직 */}
                {documentModal.type === 'resume' && documentModal.isOriginal && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>지원자 기본정보</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>이름</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.name || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원 직무</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.position || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>부서</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.department || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>경력</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.experience || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>기술스택</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.skills || '정보 없음'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>상태</DocumentCardTitle>
                          <DocumentCardText>{getStatusText(documentModal.applicant.status)}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>평가 정보</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>성장배경</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.growthBackground || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원동기</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.motivation || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>경력사항</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.careerHistory || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>종합 점수</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.analysisScore || 0}점</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>분석 결과</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.analysisResult || '분석 결과 없음'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원일시</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.created_at ? new Date(documentModal.applicant.created_at).toLocaleString() : 'N/A'}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>
                  </>
                )}

                {/* 자소서: cover_letters 컬렉션에서 정보 가져오기 */}
                {documentModal.type === 'coverLetter' && documentModal.isOriginal && documentModal.documentData && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>지원자 기본정보</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>이름</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.name || documentModal.applicant.name || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원 직무</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.position || documentModal.applicant.position || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>부서</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.department || documentModal.applicant.department || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>경력</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.experience || documentModal.applicant.experience || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>기술스택</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.keywords?.join(', ') || documentModal.applicant.skills || '정보 없음'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>상태</DocumentCardTitle>
                          <DocumentCardText>{getStatusText(documentModal.applicant.status)}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>평가 정보</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>성장배경</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.growthBackground || documentModal.applicant.growthBackground || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원동기</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.motivation || documentModal.applicant.motivation || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>경력사항</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.careerHistory || documentModal.applicant.careerHistory || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>종합 점수</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.analysisScore || documentModal.applicant.analysisScore || 0}점</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>분석 결과</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.analysisResult || documentModal.applicant.analysisResult || '분석 결과 없음'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원일시</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.created_at ? new Date(documentModal.documentData.created_at).toLocaleString() : (documentModal.applicant.created_at ? new Date(documentModal.applicant.created_at).toLocaleString() : 'N/A')}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>
                  </>
                )}

                {documentModal.type === 'resume' && !documentModal.isOriginal && documentModal.documentData && (
                  <DocumentSection>
                    <DocumentSectionTitle>이력서 내용</DocumentSectionTitle>
                    <DocumentCard>
                      <DocumentCardText>
                        {documentModal.documentData.extracted_text || '이력서 내용을 불러올 수 없습니다.'}
                      </DocumentCardText>
                    </DocumentCard>
                  </DocumentSection>
                )}

                {documentModal.type === 'coverLetter' && !documentModal.isOriginal && documentModal.documentData && (
                  <DocumentSection>
                    <DocumentSectionTitle>자소서 내용</DocumentSectionTitle>
                    <DocumentCard>
                      <DocumentCardText>
                        {documentModal.documentData.extracted_text || documentModal.documentData.content || '자소서 내용을 불러올 수 없습니다.'}
                      </DocumentCardText>
                    </DocumentCard>
                  </DocumentSection>
                )}

                {documentModal.type === 'coverLetter' && documentModal.documentData && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>지원 동기</DocumentSectionTitle>
                      <DocumentText>{documentModal.documentData.extracted_text || documentModal.documentData.content || '자소서 내용을 불러올 수 없습니다.'}</DocumentText>
                    </DocumentSection>
                  </>
                )}

                {documentModal.type === 'portfolio' && documentModal.applicant.documents?.portfolio && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>프로젝트</DocumentSectionTitle>
                      {(documentModal.applicant.documents.portfolio.projects || []).map((project, index) => (
                        <DocumentCard key={index}>
                          <DocumentCardTitle>{project.title}</DocumentCardTitle>
                          <DocumentCardText>{project.description}</DocumentCardText>
                          <DocumentCardText><strong>기술스택:</strong> {(project.technologies || []).join(', ')}</DocumentCardText>
                          <DocumentCardText><strong>주요 기능:</strong></DocumentCardText>
                          <DocumentList>
                            {(project.features || []).map((feature, idx) => (
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
                        {(documentModal.applicant.documents.portfolio.achievements || []).map((achievement, index) => (
                          <DocumentListItem key={index}>{achievement}</DocumentListItem>
                        ))}
                      </DocumentList>
                    </DocumentSection>
                  </>
                )}

                {documentModal.type === 'coverLetter' && !documentModal.isOriginal && (
                  <>
                    {/* 유사도 체크 결과 섹션 */}
                    <DocumentSection>
                      <DocumentSectionTitle>🔍 유사도 체크 결과</DocumentSectionTitle>
                      
                      {documentModal.isLoadingSimilarity && (
                        <DocumentCard>
                          <DocumentCardText>
                            📊 다른 {documentModal.type === 'resume' ? '이력서' : '자소서'}들과의 유사도를 분석 중입니다...
                          </DocumentCardText>
                        </DocumentCard>
                      )}

                      {!documentModal.isLoadingSimilarity && documentModal.similarityData && (
                        <>
                          {/* 통계 정보 */}
                          <DocumentCard>
                            <DocumentCardTitle>📈 유사도 분석 통계</DocumentCardTitle>
                            <DocumentGrid style={{display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px'}}>
                              <div>
                                <strong>비교 대상:</strong> {documentModal.similarityData?.statistics?.total_compared || 0}명
                              </div>
                              <div>
                                <strong>평균 유사도:</strong> {((documentModal.similarityData?.statistics?.average_similarity || 0) * 100).toFixed(1)}%
                              </div>
                              <div>
                                <strong>높은 유사도:</strong> {documentModal.similarityData?.statistics?.high_similarity_count || 0}명 (70% 이상)
                              </div>
                              <div>
                                <strong>중간 유사도:</strong> {documentModal.similarityData?.statistics?.moderate_similarity_count || 0}명 (40-70%)
                              </div>
                            </DocumentGrid>
                          </DocumentCard>

                          {/* 표절 위험도 분석 */}
                          {documentModal.similarityData?.plagiarism_analysis && documentModal.similarityData.plagiarism_analysis.success && (
                            <DocumentCard>
                              <DocumentCardTitle>⚠️ 표절 위험도 분석</DocumentCardTitle>
                              <div style={{
                                padding: '12px',
                                borderRadius: '8px',
                                backgroundColor: documentModal.similarityData?.plagiarism_analysis?.risk_level === 'HIGH' ? '#fff5f5' : 
                                                documentModal.similarityData?.plagiarism_analysis?.risk_level === 'MEDIUM' ? '#fffbf0' : '#f0fff4',
                                border: `2px solid ${documentModal.similarityData?.plagiarism_analysis?.risk_level === 'HIGH' ? '#ff4757' : 
                                                   documentModal.similarityData?.plagiarism_analysis?.risk_level === 'MEDIUM' ? '#ffa502' : '#2ed573'}`
                              }}>
                                <div style={{
                                  fontWeight: 'bold',
                                  marginBottom: '8px',
                                  color: documentModal.similarityData?.plagiarism_analysis?.risk_level === 'HIGH' ? '#ff4757' : 
                                        documentModal.similarityData?.plagiarism_analysis?.risk_level === 'MEDIUM' ? '#ffa502' : '#2ed573'
                                }}>
                                  위험도: {documentModal.similarityData?.plagiarism_analysis?.risk_level || 'N/A'} 
                                  ({((documentModal.similarityData?.plagiarism_analysis?.risk_score || 0) * 100).toFixed(1)}%)
                                </div>
                                <div style={{fontSize: '14px', color: '#333', marginBottom: '8px', whiteSpace: 'pre-line'}}>
                                  {documentModal.similarityData?.plagiarism_analysis?.analysis || '분석 결과가 없습니다.'}
                                </div>
                                
                                {documentModal.similarityData?.plagiarism_analysis?.recommendations && 
                                 documentModal.similarityData.plagiarism_analysis.recommendations.length > 0 && (
                                  <div>
                                    <div style={{fontSize: '12px', fontWeight: 'bold', color: '#666', marginBottom: '4px'}}>
                                      권장사항:
                                    </div>
                                    <ul style={{margin: '0', paddingLeft: '16px'}}>
                                      {documentModal.similarityData?.plagiarism_analysis?.recommendations?.map((rec, idx) => (
                                        <li key={idx} style={{fontSize: '12px', color: '#666', marginBottom: '2px'}}>
                                          {rec}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            </DocumentCard>
                          )}

                          {/* 상위 유사 이력서들 */}
                          {documentModal.similarityData?.top_similar?.length > 0 && (
                            <DocumentCard>
                              <DocumentCardTitle>🎯 가장 유사한 자소서 TOP 5</DocumentCardTitle>
                              {documentModal.similarityData?.top_similar?.map((similar, index) => (
                                <div key={similar.resume_id} style={{
                                  padding: '12px',
                                  margin: '8px 0',
                                  border: `2px solid ${similar.is_high_similarity ? '#ff4757' : similar.is_moderate_similarity ? '#ffa502' : '#2ed573'}`,
                                  borderRadius: '8px',
                                  backgroundColor: similar.is_high_similarity ? '#fff5f5' : similar.is_moderate_similarity ? '#fffbf0' : '#f0fff4',
                                  cursor: 'pointer',
                                  transition: 'all 0.2s ease'
                                }}
                                onClick={() => handleSimilarApplicantClick(similar)}
                                onMouseEnter={(e) => {
                                  e.target.style.transform = 'translateY(-2px)';
                                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                                }}
                                onMouseLeave={(e) => {
                                  e.target.style.transform = 'translateY(0)';
                                  e.target.style.boxShadow = 'none';
                                }}>
                                  <div style={{fontWeight: 'bold', marginBottom: '4px'}}>
                                    #{index + 1}. {similar.applicant_name} ({similar.position})
                                  </div>
                                  <div style={{fontSize: '14px', color: '#666'}}>
                                    전체 유사도: <strong style={{color: similar.is_high_similarity ? '#ff4757' : similar.is_moderate_similarity ? '#ffa502' : '#2ed573'}}>
                                      {(similar.overall_similarity * 100).toFixed(1)}%
                                    </strong>
                                  </div>
                                  <div style={{fontSize: '12px', color: '#888', marginTop: '4px'}}>
                                    전체 유사도: {(similar.overall_similarity * 100).toFixed(1)}%
                                  </div>
                                  
                                  {/* LLM 분석 결과 추가 */}
                                  {similar.llm_analysis && similar.llm_analysis.success && (
                                    <div style={{
                                      marginTop: '8px',
                                      padding: '8px',
                                      backgroundColor: '#f0f8ff',
                                      borderLeft: '4px solid #4a90e2',
                                      borderRadius: '4px'
                                    }}>
                                      <div style={{fontSize: '11px', fontWeight: 'bold', color: '#4a90e2', marginBottom: '4px'}}>
                                        🤖 AI 분석
                                      </div>
                                      <div style={{fontSize: '12px', color: '#333', lineHeight: '1.4', whiteSpace: 'pre-line'}}>
                                        {similar.llm_analysis.analysis}
                                      </div>
                                    </div>
                                  )}
                                  
                                  {similar.llm_analysis && !similar.llm_analysis.success && (
                                    <div style={{
                                      marginTop: '8px',
                                      padding: '8px',
                                      backgroundColor: '#fff0f0',
                                      borderLeft: '4px solid #e74c3c',
                                      borderRadius: '4px'
                                    }}>
                                      <div style={{fontSize: '11px', color: '#e74c3c'}}>
                                        AI 분석 실패: {similar.llm_analysis.error || 'Unknown error'}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </DocumentCard>
                          )}
                        </>
                      )}

                      {!documentModal.isLoadingSimilarity && !documentModal.similarityData && (
                        <DocumentCard>
                          <DocumentCardText>
                            유사도 체크 중 오류가 발생했습니다. 다시 시도해주세요.
                          </DocumentCardText>
                        </DocumentCard>
                      )}
                    </DocumentSection>

                    {/* 기존 자소서 요약 섹션 */}
                    {!documentModal.applicant.documents?.resume && (
                      <DocumentSection>
                        <DocumentSectionTitle>자소서 요약</DocumentSectionTitle>
                        <DocumentCard>
                          <DocumentCardText>
                            현재 이 지원자의 상세 자소서 정보는 등록되지 않았습니다.<br/>
                            <strong>원본보기</strong> 버튼을 클릭하면 DB에 저장된 지원자의 모든 정보를 확인할 수 있습니다.
                          </DocumentCardText>
                        </DocumentCard>
                      </DocumentSection>
                    )}
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
                <ResumeModalTitle>새 지원자 등록</ResumeModalTitle>
                <ResumeModalCloseButton onClick={handleResumeModalClose}>&times;</ResumeModalCloseButton>
              </ResumeModalHeader>

              <ResumeModalBody>
                <ResumeFormSection>
                  <ResumeFormTitle>이력서 업로드</ResumeFormTitle>
                  <DocumentUploadContainer>
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
                                : '이력서 파일을 선택하거나 드래그하세요'
                              }
                            </span>
                            <small>PDF, DOC, DOCX, TXT 파일 지원</small>
                          </FileUploadPlaceholder>
                        )}
                      </FileUploadLabel>
                    </FileUploadArea>
                  </DocumentUploadContainer>
                </ResumeFormSection>

                <ResumeFormSection>
                  <ResumeFormTitle>자기소개서 업로드</ResumeFormTitle>
                  <DocumentUploadContainer>
                    <FileUploadArea
                      isDragOver={isDragOver}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                    >
                      <FileUploadInput
                        type="file"
                        accept=".pdf,.doc,.docx,.txt"
                        onChange={handleCoverFileChange}
                        id="cover-file"
                      />
                      <FileUploadLabel htmlFor="cover-file">
                        {coverLetterFile ? (
                          <FileSelected>
                            <FiFile size={20} />
                            <span>{coverLetterFile.name}</span>
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
                                : '자기소개서 파일을 선택하거나 드래그하세요'
                              }
                            </span>
                            <small>PDF, DOC, DOCX, TXT 파일 지원</small>
                          </FileUploadPlaceholder>
                        )}
                      </FileUploadLabel>
                    </FileUploadArea>
                  </DocumentUploadContainer>
                </ResumeFormSection>

                <ResumeFormSection>
                  <ResumeFormTitle>포트폴리오 업로드</ResumeFormTitle>
                  <DocumentUploadContainer>
                    <FileUploadArea
                      isDragOver={isDragOver}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                    >
                      <FileUploadInput
                        type="file"
                        accept=".pdf"
                        onChange={handlePortfolioFileChange}
                        id="portfolio-file"
                      />
                      <FileUploadLabel htmlFor="portfolio-file">
                        {portfolioFile ? (
                          <FileSelected>
                            <FiFile size={20} />
                            <span>{portfolioFile.name}</span>
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
                                : '포트폴리오 파일을 선택하거나 드래그하세요'
                              }
                            </span>
                            <small>PDF 파일만 지원</small>
                          </FileUploadPlaceholder>
                        )}
                      </FileUploadLabel>
                    </FileUploadArea>
                  </DocumentUploadContainer>
                </ResumeFormSection>

                <ResumeFormActions>
                  <ResumeSubmitButton 
                    onClick={handleResumeSubmit}
                    disabled={(!resumeFile && !coverLetterFile && !portfolioFile) || isAnalyzing}
                  >
                    {isAnalyzing ? '처리 중...' : '업로드 및 저장'}
                  </ResumeSubmitButton>
                </ResumeFormActions>
              </ResumeModalBody>

              {isAnalyzing && (
                <ResumeAnalysisSection>
                  <ResumeAnalysisTitle>문서 업로드 및 분석 중입니다...</ResumeAnalysisTitle>
                  <ResumeAnalysisSpinner>
                    <div className="spinner"></div>
                    <span>AI가 문서를 분석하고 있습니다 (최대 5분 소요)</span>
                    <small style={{ marginTop: '8px', color: 'var(--text-secondary)' }}>
                      대용량 파일이나 여러 파일을 동시에 처리할 때 시간이 오래 걸릴 수 있습니다.
                    </small>
                  </ResumeAnalysisSpinner>
                </ResumeAnalysisSection>
              )}

              {analysisResult && (
                <ResumeAnalysisSection>
                  <ResumeAnalysisTitle>업로드 결과</ResumeAnalysisTitle>
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
                      <ResumeAnalysisLabel>업로드 일시:</ResumeAnalysisLabel>
                      <ResumeAnalysisValue>{analysisResult.analysisDate}</ResumeAnalysisValue>
                    </ResumeAnalysisItem>
                    {analysisResult.applicant && (
                      <>
                        <ResumeAnalysisItem>
                          <ResumeAnalysisLabel>지원자 이름:</ResumeAnalysisLabel>
                          <ResumeAnalysisValue>{analysisResult.applicant.name || 'N/A'}</ResumeAnalysisValue>
                        </ResumeAnalysisItem>
                        <ResumeAnalysisItem>
                          <ResumeAnalysisLabel>지원자 이메일:</ResumeAnalysisLabel>
                          <ResumeAnalysisValue>{analysisResult.applicant.email || 'N/A'}</ResumeAnalysisValue>
                        </ResumeAnalysisItem>
                        <ResumeAnalysisItem>
                          <ResumeAnalysisLabel>지원자 전화번호:</ResumeAnalysisLabel>
                          <ResumeAnalysisValue>{analysisResult.applicant.phone || 'N/A'}</ResumeAnalysisValue>
                        </ResumeAnalysisItem>
                        <ResumeAnalysisItem>
                          <ResumeAnalysisLabel>지원 직무:</ResumeAnalysisLabel>
                          <ResumeAnalysisValue>{analysisResult.applicant.position || 'N/A'}</ResumeAnalysisValue>
                        </ResumeAnalysisItem>
                        <ResumeAnalysisItem>
                          <ResumeAnalysisLabel>기술 스택:</ResumeAnalysisLabel>
                          <ResumeAnalysisSkills>
                            {(analysisResult.applicant.skills || '').split(',').map((skill, index) => (
                              <ResumeSkillTag key={index}>{skill.trim()}</ResumeSkillTag>
                            ))}
                          </ResumeAnalysisSkills>
                        </ResumeAnalysisItem>
                      </>
                    )}
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>업로드 결과:</ResumeAnalysisLabel>
                      <ResumeAnalysisRecommendations>
                        {analysisResult.uploadResults?.map((result, index) => (
                          <ResumeRecommendationItem key={index}>
                            ✅ {result.type === 'resume' ? '이력서' : result.type === 'cover_letter' ? '자기소개서' : '포트폴리오'} 업로드 성공
                          </ResumeRecommendationItem>
                        ))}
                        {analysisResult.analysisResult && Object.keys(analysisResult.analysisResult).map((docType, index) => (
                          <ResumeRecommendationItem key={`doc-${index}`}>
                            ✅ {docType === 'resume' ? '이력서' : docType === 'cover_letter' ? '자기소개서' : '포트폴리오'} OCR 처리 완료
                          </ResumeRecommendationItem>
                        ))}
                      </ResumeAnalysisRecommendations>
                    </ResumeAnalysisItem>
                    <ResumeAnalysisItem>
                      <ResumeAnalysisLabel>상태:</ResumeAnalysisLabel>
                      <ResumeAnalysisValue style={{ color: '#28a745', fontWeight: 'bold' }}>
                        ✅ 성공적으로 DB에 저장되었습니다
                      </ResumeAnalysisValue>
                    </ResumeAnalysisItem>
                  </ResumeAnalysisContent>
                </ResumeAnalysisSection>
              )}

              <ResumeModalFooter>
                <ResumeModalButton onClick={handleResumeModalClose}>
                  {analysisResult ? '닫기' : '취소'}
                </ResumeModalButton>
              </ResumeModalFooter>
            </ResumeModalContent>
          </ResumeModalOverlay>
        )}
      </AnimatePresence>

      {/* 상세 분석 모달 */}
      <DetailedAnalysisModal
        isOpen={showDetailedAnalysis}
        onClose={() => setShowDetailedAnalysis(false)}
        analysisData={{
          ...analysisResult,
          analysisScore: selectedApplicant?.analysisScore
        }}
      />
    </Container>
  );
};

// 새로운 스타일 컴포넌트들
const ApplicantInfoContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
`;

const InfoField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const InfoLabel = styled.label`
  font-size: 0.9rem;
  font-weight: 600;
  color: #2d3748;
`;

const InfoInput = styled.input`
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #4299e1;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
  }

  &::placeholder {
    color: #a0aec0;
  }
`;

const ResumeFormActions = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
`;

const ResumeSubmitButton = styled.button`
  background-color: #48bb78;
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 160px;

  &:hover:not(:disabled) {
    background-color: #38a169;
    transform: translateY(-1px);
  }

  &:disabled {
    background-color: #cbd5e0;
    cursor: not-allowed;
    transform: none;
  }
`;

const DeleteButton = styled.button`
  background-color: #e53e3e;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  width: 100%;
  justify-content: center;

  &:hover {
    background-color: #c53030;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

// 유사 인재 추천 스타일 컴포넌트들
const SimilarCandidatesSection = styled.div`
  margin: 24px 0;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
`;

const SimilarCandidatesTitle = styled.h3`
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
`;

const SimilarCandidatesButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 16px;

  &:hover {
    background: #3182ce;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const SimilarCandidatesLoading = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #718096;
  font-size: 0.9rem;
  gap: 16px;
`;

const SimilarCandidatesSpinner = styled.div`
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const SimilarCandidatesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const SimilarCandidateItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;

  &:hover {
    border-color: #4299e1;
    box-shadow: 0 2px 8px rgba(66, 153, 225, 0.1);
  }
`;

const SimilarCandidateInfo = styled.div`
  flex: 1;
`;

const SimilarCandidateName = styled.div`
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
`;

const SimilarCandidateDetails = styled.div`
  font-size: 0.9rem;
  color: #718096;
  margin-bottom: 4px;
`;

const SimilarCandidateScore = styled.div`
  font-size: 0.8rem;
  color: #4299e1;
  font-weight: 500;
`;

const SimilarCandidateScoreDetail = styled.div`
  font-size: 0.7rem;
  color: #718096;
  font-weight: 400;
  margin-top: 2px;
`;

const SimilarCandidateMethod = styled.div`
  font-size: 0.7rem;
  color: #38a169;
  margin-top: 4px;
  font-style: italic;
`;

const SimilarCandidateActions = styled.div`
  display: flex;
  gap: 8px;
`;

const SimilarCandidateButton = styled.button`
  padding: 8px 16px;
  background: #f7fafc;
  color: #4299e1;
  border: 1px solid #4299e1;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #4299e1;
    color: white;
  }
`;

const SimilarCandidatesError = styled.div`
  text-align: center;
  padding: 20px;
  color: #e53e3e;
  background: #fed7d7;
  border-radius: 8px;
  font-size: 0.9rem;
`;

const SimilarCandidatesEmpty = styled.div`
  text-align: center;
  padding: 20px;
  color: #718096;
  font-style: italic;
`;

export default ApplicantManagement; 
