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
  FiArrowLeft
} from 'react-icons/fi';
import DetailedAnalysisModal from '../components/DetailedAnalysisModal';
import ResumeModal from '../components/ResumeModal';
import CoverLetterSummary from '../components/CoverLetterSummary';
import CoverLetterAnalysis from '../components/CoverLetterAnalysis';
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
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }
`;

const StatCard = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: ${props => {
      switch (props.$variant) {
        case 'total':
          return 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)';
        case 'passed':
          return 'linear-gradient(90deg, #48bb78 0%, #38a169 100%)';
        case 'waiting':
          return 'linear-gradient(90deg, #ed8936 0%, #dd6b20 100%)';
        case 'rejected':
          return 'linear-gradient(90deg, #e53e3e 0%, #c53030 100%)';
        default:
          return 'linear-gradient(90deg, #e2e8f0 0%, #cbd5e0 100%)';
      }
    }};
  }
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }
`;

const StatValue = styled(motion.div)`
  font-size: 36px;
  font-weight: 800;
  color: #2d3748;
  margin-bottom: 8px;
  line-height: 1;
`;

const StatLabel = styled.div`
  color: #4a5568;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
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

const ExistingApplicantInfo = styled.div`
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 1px solid #2196f3;
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
`;

const ExistingApplicantTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: #1976d2;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ExistingApplicantDetails = styled.div`
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  
  ul {
    margin: 8px 0;
    padding-left: 20px;
  }
  
  li {
    margin: 4px 0;
  }
`;



const ReplaceOptionSection = styled.div`
  margin-top: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  border: 1px solid #e0e0e0;
`;

const ReplaceOptionLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1976d2;
  cursor: pointer;
  
  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #1976d2;
  }
  
  span {
    font-size: 15px;
  }
`;

const ReplaceOptionDescription = styled.div`
  margin-top: 8px;
  font-size: 13px;
  color: #666;
  line-height: 1.4;
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
  grid-template-columns: ${props => props.viewMode === 'grid' ? 'repeat(3, 1fr)' : '1fr'};
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
  gap: 0;
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

const ResumeViewButton = styled(ActionButton)`
  background: #667eea;
  color: white;
  border-color: #667eea;
  
  &:hover {
    background: #5a67d8;
    border-color: #5a67d8;
    color: white;
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
  z-index: 2000;
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

// 이력서 버튼 특별 스타일
const ResumeButton = styled(DocumentButton)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-weight: 600;
  font-size: 15px;
  padding: 14px 28px;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
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
        
        {/* 자소서 요약 섹션 */}
        {applicant.cover_letter_analysis && (
          <CoverLetterSummary
            coverLetterData={applicant.cover_letter}
            analysisData={applicant.cover_letter_analysis}
          />
        )}
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
      'reviewed': '검토완료',
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

  // 페이지네이션 상태
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12); // 한 페이지당 12개 (3x4)
  const [hasMore, setHasMore] = useState(true);

  // 새 이력서 등록 모달 상태
  const [isResumeModalOpen, setIsResumeModalOpen] = useState(false);
  const [selectedResumeApplicant, setSelectedResumeApplicant] = useState(null);
  const [resumeFile, setResumeFile] = useState(null);
  const [coverLetterFile, setCoverLetterFile] = useState(null);
  const [portfolioFile, setPortfolioFile] = useState(null);
  const [documentType, setDocumentType] = useState('이력서');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [existingApplicant, setExistingApplicant] = useState(null);
  const [isCheckingDuplicate, setIsCheckingDuplicate] = useState(false);
  const [replaceExisting, setReplaceExisting] = useState(false);
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
  const [previewDocument, setPreviewDocument] = useState(null);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);

  // 키워드 랭킹 관련 상태 추가
  const [isCalculatingRanking, setIsCalculatingRanking] = useState(false);
  const [rankingResults, setRankingResults] = useState(null);



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

  // 필터나 검색이 변경될 때 랭킹 결과 초기화
  useEffect(() => {
    if (rankingResults) {
      setRankingResults(null);
      console.log('🔄 필터/검색 변경으로 랭킹 결과 초기화');
    }
  }, [searchTerm, filterStatus, selectedJobs, selectedExperience]);

  // 키워드 매칭 점수 계산 함수
  const calculateKeywordMatchingScore = useCallback((applicant, keyword) => {
    const keywordLower = keyword.toLowerCase();
    let score = 0;
    let matches = 0;

    // 이름에서 키워드 매칭
    if (applicant.name && applicant.name.toLowerCase().includes(keywordLower)) {
      score += 3;
      matches++;
    }

    // 직무에서 키워드 매칭
    if (applicant.position && applicant.position.toLowerCase().includes(keywordLower)) {
      score += 4;
      matches++;
    }

    // 기술스택에서 키워드 매칭
    if (applicant.skills) {
      const skills = Array.isArray(applicant.skills) ? applicant.skills : applicant.skills.split(',');
      skills.forEach(skill => {
        if (skill.trim().toLowerCase().includes(keywordLower)) {
          score += 5;
          matches++;
        }
      });
    }

    // 이력서 분석 피드백에서 키워드 매칭
    if (applicant.resume_analysis) {
      Object.values(applicant.resume_analysis).forEach(item => {
        if (item && item.feedback && item.feedback.toLowerCase().includes(keywordLower)) {
          score += 2;
          matches++;
        }
      });
    }

    // 자소서 분석 피드백에서 키워드 매칭
    if (applicant.cover_letter_analysis) {
      Object.values(applicant.cover_letter_analysis).forEach(item => {
        if (item && item.feedback && item.feedback.toLowerCase().includes(keywordLower)) {
          score += 2;
          matches++;
        }
      });
    }

    // 포트폴리오 분석 피드백에서 키워드 매칭
    if (applicant.portfolio_analysis) {
      Object.values(applicant.portfolio_analysis).forEach(item => {
        if (item && item.feedback && item.feedback.toLowerCase().includes(keywordLower)) {
          score += 2;
          matches++;
        }
      });
    }

    // 최대 10점으로 정규화
    return Math.min(score, 10);
  }, []);

  // 등수 텍스트 생성 함수
  const getRankText = useCallback((rank, total) => {
    if (rank === 1) return '🥇 1등';
    if (rank === 2) return '🥈 2등';
    if (rank === 3) return '🥉 3등';
    if (rank <= Math.ceil(total * 0.1)) return `🏅 ${rank}등 (상위 10%)`;
    if (rank <= Math.ceil(total * 0.3)) return `⭐ ${rank}등 (상위 30%)`;
    if (rank <= Math.ceil(total * 0.5)) return `✨ ${rank}등 (상위 50%)`;
    return `${rank}등`;
  }, []);

  // 키워드 랭킹 계산 함수
  const calculateKeywordRanking = useCallback(async () => {
    if (!searchTerm.trim()) {
      alert('검색어를 입력해주세요.');
      return;
    }

    if (filteredApplicants.length === 0) {
      alert('검색 결과가 없습니다. 다른 검색어나 필터 조건을 시도해보세요.');
      return;
    }

    try {
      setIsCalculatingRanking(true);
      console.log('🔍 키워드 랭킹 계산 시작:', searchTerm);
      console.log('📊 대상 지원자 수:', filteredApplicants.length);

      // 키워드와 관련된 점수 계산
      const rankingData = filteredApplicants.map(applicant => {
        let totalScore = 0;
        let keywordMatches = 0;
        let maxPossibleScore = 0;

        // 이력서 분석 점수 (30%)
        if (applicant.resume_analysis) {
          const resumeScore = calculateAverageScore(applicant.resume_analysis) * 0.3;
          totalScore += resumeScore;
          maxPossibleScore += 10 * 0.3;
        }

        // 자소서 분석 점수 (30%)
        if (applicant.cover_letter_analysis) {
          const coverLetterScore = calculateAverageScore(applicant.cover_letter_analysis) * 0.3;
          totalScore += coverLetterScore;
          maxPossibleScore += 10 * 0.3;
        }

        // 포트폴리오 분석 점수 (20%)
        if (applicant.portfolio_analysis) {
          const portfolioScore = calculateAverageScore(applicant.portfolio_analysis) * 0.2;
          totalScore += portfolioScore;
          maxPossibleScore += 10 * 0.2;
        }

        // 키워드 매칭 점수 (20%)
        const keywordScore = calculateKeywordMatchingScore(applicant, searchTerm) * 0.2;
        totalScore += keywordScore;
        maxPossibleScore += 10 * 0.2;

        // 최종 점수 (100점 만점)
        const finalScore = maxPossibleScore > 0 ? (totalScore / maxPossibleScore) * 100 : 0;

        return {
          applicant,
          totalScore: Math.round(finalScore * 10) / 10,
          keywordMatches,
          breakdown: {
            resume: applicant.resume_analysis ? Math.round(calculateAverageScore(applicant.resume_analysis) * 10) / 10 : 0,
            coverLetter: applicant.cover_letter_analysis ? Math.round(calculateAverageScore(applicant.cover_letter_analysis) * 10) / 10 : 0,
            portfolio: applicant.portfolio_analysis ? Math.round(calculateAverageScore(applicant.portfolio_analysis) * 10) / 10 : 0,
            keywordMatching: Math.round(keywordScore * 5) // 0.2 * 10 * 5 = 10점 만점
          }
        };
      });

      // 점수별 내림차순 정렬
      rankingData.sort((a, b) => b.totalScore - a.totalScore);

      // 등수 추가
      const rankedData = rankingData.map((item, index) => ({
        ...item,
        rank: index + 1,
        rankText: getRankText(index + 1, rankingData.length)
      }));

      setRankingResults(rankedData);
      console.log('✅ 랭킹 계산 완료:', rankedData.length + '명');
      
      // 성공 메시지 표시
      const topRank = rankedData[0];
      if (topRank) {
        alert(`랭킹 계산이 완료되었습니다!\n\n🥇 1등: ${topRank.applicant.name} (${topRank.totalScore}점)\n📊 총 ${rankedData.length}명의 지원자에 대해 랭킹이 계산되었습니다.`);
      }

    } catch (error) {
      console.error('❌ 랭킹 계산 오류:', error);
      alert('랭킹 계산 중 오류가 발생했습니다.');
    } finally {
      setIsCalculatingRanking(false);
    }
  }, [searchTerm, filteredApplicants, calculateKeywordMatchingScore, getRankText]);

  // 메모이제이션된 페이지네이션된 지원자 목록 (최신순 정렬)
  const paginatedApplicants = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    // 최신 지원자가 먼저 오도록 정렬 (created_at 기준 내림차순)
    const sortedApplicants = [...filteredApplicants].sort((a, b) => {
      // created_at이 없으면 현재 시간을 기본값으로 사용
      const dateA = new Date(a.created_at || a.appliedDate || new Date());
      const dateB = new Date(b.created_at || b.appliedDate || new Date());
      
      // 날짜가 유효하지 않은 경우 현재 시간으로 설정
      if (isNaN(dateA.getTime())) dateA.setTime(Date.now());
      if (isNaN(dateB.getTime())) dateB.setTime(Date.now());
      
      return dateB - dateA; // 최신순 (내림차순)
    });
    return sortedApplicants.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredApplicants, currentPage, itemsPerPage]);

  // 최적화된 통계 계산 (useMemo 사용)
  const optimizedStats = useMemo(() => {
    if (!applicants || applicants.length === 0) {
      return { total: 0, passed: 0, waiting: 0, rejected: 0 };
    }
    
    const stats = applicants.reduce((acc, applicant) => {
      acc.total++;
      
      switch (applicant.status) {
        case '서류합격':
        case '최종합격':
          acc.passed++;
          break;
        case '보류':
          acc.waiting++;
          break;
        case '서류불합격':
          acc.rejected++;
          break;
        default:
          acc.waiting++; // 기본값은 보류로 처리
          break;
      }
      
      return acc;
    }, { total: 0, passed: 0, waiting: 0, rejected: 0 });
    
    return stats;
  }, [applicants]);

  // 초기 데이터 로드
  useEffect(() => {
    // 세션 스토리지에서 저장된 데이터 확인
    const savedApplicants = sessionStorage.getItem('applicants');
    const savedStats = sessionStorage.getItem('applicantStats');
    
    if (savedApplicants) {
      try {
        const parsedApplicants = JSON.parse(savedApplicants);
        setApplicants(parsedApplicants);
        console.log('✅ 세션 스토리지에서 지원자 데이터 복원됨:', parsedApplicants.length + '명');
        
        // 저장된 통계도 복원
        if (savedStats) {
          try {
            const parsedStats = JSON.parse(savedStats);
            setStats(parsedStats);
            console.log('✅ 세션 스토리지에서 통계 데이터 복원됨');
          } catch (error) {
            console.error('통계 데이터 파싱 오류:', error);
            loadStats(); // 실패 시 API에서 로드
          }
        }
      } catch (error) {
        console.error('지원자 데이터 파싱 오류:', error);
        console.log('🔄 API에서 데이터를 새로 로드합니다.');
        loadApplicants();
        loadStats();
      }
    } else {
      // 저장된 데이터가 없으면 API에서 로드
      console.log('🔄 세션 스토리지에 데이터가 없어 API에서 로드합니다.');
      loadApplicants();
      loadStats();
    }
  }, []);

  // 최적화된 통계를 stats 상태에 반영
  useEffect(() => {
    if (optimizedStats) {
      setStats(optimizedStats);
    }
  }, [optimizedStats]);

  // 지원자 데이터 로드 (페이지네이션 지원)
  const loadApplicants = useCallback(async () => {
    try {
      setIsLoading(true);
      console.log('지원자 데이터를 불러오는 중...');
      
      // 모든 지원자 데이터를 한 번에 가져오기 (페이지네이션은 클라이언트에서 처리)
      const apiApplicants = await api.getAllApplicants(0, 1000); // 최대 1000명까지 가져오기
      
      if (apiApplicants && apiApplicants.length > 0) {
        console.log(`✅ API에서 ${apiApplicants.length}명의 지원자 데이터를 성공적으로 로드했습니다.`);
        setApplicants(apiApplicants);
        setHasMore(false); // 모든 데이터를 가져왔으므로 더 이상 로드할 필요 없음
        
        // 세션 스토리지에 지원자 데이터 저장
        try {
          sessionStorage.setItem('applicants', JSON.stringify(apiApplicants));
          console.log('💾 세션 스토리지에 지원자 데이터 저장됨');
        } catch (error) {
          console.error('지원자 데이터 세션 스토리지 저장 실패:', error);
        }
      } else {
        console.log('⚠️ API에서 데이터를 찾을 수 없습니다.');
        setApplicants([]);
        setHasMore(false);
        
        // 빈 배열도 세션 스토리지에 저장
        try {
          sessionStorage.setItem('applicants', JSON.stringify([]));
        } catch (error) {
          console.error('빈 배열 세션 스토리지 저장 실패:', error);
        }
      }
    } catch (error) {
      console.error('❌ API 연결 실패:', error);
      console.log('🔄 백엔드 서버 연결을 확인해주세요.');
      setApplicants([]);
      setHasMore(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 통계 데이터 로드
  const loadStats = useCallback(async () => {
    try {
      const apiStats = await api.getApplicantStats();
      setStats(apiStats);
      
      // 세션 스토리지에 통계 데이터 저장
      try {
        sessionStorage.setItem('applicantStats', JSON.stringify(apiStats));
        console.log('💾 세션 스토리지에 통계 데이터 저장됨');
      } catch (error) {
        console.error('통계 데이터 세션 스토리지 저장 실패:', error);
      }
    } catch (error) {
      console.error('통계 데이터 로드 실패:', error);
      // 기본 통계 계산
      updateLocalStats();
    }
  }, []);

  // 로컬 통계 업데이트
  const updateLocalStats = useCallback(() => {
    setStats(optimizedStats);
  }, [optimizedStats]);

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
        
        console.log(`📊 상태 업데이트:`, {
          이전상태: previousStatus,
          새상태: newStatus,
          지원자ID: applicantId
        });
        
        // 세션 스토리지에 업데이트된 데이터 저장
        try {
          sessionStorage.setItem('applicants', JSON.stringify(updatedApplicants));
          console.log('💾 세션 스토리지에 지원자 데이터 저장됨');
        } catch (error) {
          console.error('세션 스토리지 저장 실패:', error);
        }
        
        return updatedApplicants;
      });
      
      console.log(`✅ 지원자 ${applicantId}의 상태가 ${newStatus}로 업데이트되었습니다.`);
    } catch (error) {
      console.error('지원자 상태 업데이트 실패:', error);
    }
  }, [applicants]);



  const handleCardClick = (applicant) => {
    setSelectedApplicant(applicant);
    setIsModalOpen(true);
  };

  const handleResumeModalOpen = (applicant) => {
    setSelectedResumeApplicant(applicant);
    setIsResumeModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedApplicant(null);
    // 이력서 모달이 열려있으면 닫지 않음
  };

  const handleResumeModalClose = () => {
    setIsResumeModalOpen(false);
    setSelectedResumeApplicant(null);
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
        setCurrentPage(1);
        loadApplicants();
        
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
  const handleNewResumeModalOpen = () => {
    setIsResumeModalOpen(true);
  };

  const handleNewResumeModalClose = () => {
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
      
      // 이력서 파일이 선택되면 자동으로 중복 체크 수행
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        setTimeout(() => checkExistingApplicant(), 500); // 0.5초 후 중복 체크
      }
      
      // 새로운 파일이 선택되면 교체 옵션 초기화
      setReplaceExisting(false);
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
      
      // 다른 파일이 선택되면 기존 지원자 정보 초기화
      setExistingApplicant(null);
      // 교체 옵션도 초기화
      setReplaceExisting(false);
    }
  };

  const handlePortfolioFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setPortfolioFile(file);
      console.log('포트폴리오 파일이 선택되었습니다:', file.name);
      
      // 다른 파일이 선택되면 기존 지원자 정보 초기화
      setExistingApplicant(null);
      // 교체 옵션도 초기화
      setReplaceExisting(false);
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

  // 기존 지원자 검색 함수
  const checkExistingApplicant = async (files) => {
    try {
      console.log('🔍 중복 체크 시작...');
      setIsCheckingDuplicate(true);
      setExistingApplicant(null);
      
      // 파일에서 기본 정보 추출 시도
      let applicantInfo = {};
      
      if (resumeFile) {
        console.log('📄 이력서 파일로 중복 체크 수행:', resumeFile.name);
        const formData = new FormData();
        formData.append('resume_file', resumeFile);
        
        console.log('🌐 API 요청 전송:', `${API_BASE_URL}/api/integrated-ocr/check-duplicate`);
        
        const response = await fetch(`${API_BASE_URL}/api/integrated-ocr/check-duplicate`, {
          method: 'POST',
          body: formData
        });
        
        console.log('📡 API 응답 상태:', response.status, response.statusText);
        
        if (response.ok) {
          const result = await response.json();
          console.log('📋 API 응답 결과:', result);
          
          if (result.existing_applicant) {
            console.log('🔄 기존 지원자 발견:', result.existing_applicant);
            setExistingApplicant(result.existing_applicant);
            return result.existing_applicant;
          } else {
            console.log('✅ 새로운 지원자 - 중복 없음');
          }
        } else {
          console.error('❌ API 요청 실패:', response.status, response.statusText);
          const errorText = await response.text();
          console.error('❌ 에러 상세:', errorText);
        }
      } else {
        console.log('⚠️ 이력서 파일이 없어서 중복 체크 건너뜀');
      }
      
      return null;
    } catch (error) {
      console.error('❌ 중복 체크 중 오류:', error);
      return null;
    } finally {
      setIsCheckingDuplicate(false);
    }
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

      // 기존 지원자가 이미 발견된 경우 확인
      if (existingApplicant) {
        let message = `기존 지원자 "${existingApplicant.name}"님을 발견했습니다.\n\n`;
        message += `현재 보유 서류:\n`;
        message += `이력서: ${existingApplicant.resume ? '✅ 있음' : '❌ 없음'}\n`;
        message += `자기소개서: ${existingApplicant.cover_letter ? '✅ 있음' : '❌ 없음'}\n`;
        message += `포트폴리오: ${existingApplicant.portfolio ? '✅ 있음' : '❌ 없음'}\n\n`;
        
        // 업로드하려는 서류와 기존 서류 비교
        const duplicateDocuments = [];
        if (resumeFile && existingApplicant.resume) duplicateDocuments.push('이력서');
        if (coverLetterFile && existingApplicant.cover_letter) duplicateDocuments.push('자기소개서');
        if (portfolioFile && existingApplicant.portfolio) duplicateDocuments.push('포트폴리오');
        
        if (duplicateDocuments.length > 0) {
          message += `⚠️ 다음 서류는 이미 존재합니다:\n`;
          message += `${duplicateDocuments.join(', ')}\n\n`;
          message += `기존 파일을 새 파일로 교체하시겠습니까?\n`;
          message += `(교체하지 않으면 해당 서류는 업로드되지 않습니다)`;
          
          const shouldReplace = window.confirm(message);
          if (shouldReplace) {
            setReplaceExisting(true);
            console.log('🔄 교체 모드 활성화:', duplicateDocuments);
          } else {
            console.log('⏭️ 교체 모드 비활성화 - 중복 서류는 업로드되지 않음');
          }
        } else {
          message += `새로운 서류만 추가됩니다.`;
          const shouldContinue = window.confirm(message);
          if (!shouldContinue) {
            return;
          }
        }
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
      
      // 기존 지원자가 있는 경우 ID와 교체 옵션 포함
      if (existingApplicant) {
        formData.append('existing_applicant_id', existingApplicant._id);
        formData.append('replace_existing', replaceExisting.toString());
        console.log('🔄 기존 지원자 ID 포함:', existingApplicant._id);
        console.log('🔄 교체 옵션:', replaceExisting);
        
        // 교체 옵션에 따른 로그
        if (replaceExisting) {
          console.log('🔄 교체 모드 활성화 - 기존 서류를 새 서류로 교체');
        } else {
          console.log('⏭️ 교체 모드 비활성화 - 중복 서류는 업로드되지 않음');
        }
      }
      
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



  // 기존 문서 미리보기 함수
  const handlePreviewDocument = async (documentType) => {
    if (!existingApplicant) return;
    
    try {
      let documentId;
      let documentData;
      
      switch (documentType) {
        case 'resume':
          if (existingApplicant.resume) {
            documentId = existingApplicant.resume;
            // 이력서 데이터 가져오기
            const resumeResponse = await fetch(`${API_BASE_URL}/api/applicants/${existingApplicant._id}/resume`);
            if (resumeResponse.ok) {
              documentData = await resumeResponse.json();
            }
          }
          break;
        case 'cover_letter':
          if (existingApplicant.cover_letter) {
            documentId = existingApplicant.cover_letter;
            // 자기소개서 데이터 가져오기
            const coverLetterResponse = await fetch(`${API_BASE_URL}/api/applicants/${existingApplicant._id}/cover-letter`);
            if (coverLetterResponse.ok) {
              documentData = await coverLetterResponse.json();
            }
          }
          break;
        case 'portfolio':
          if (existingApplicant.portfolio) {
            documentId = existingApplicant.portfolio;
            // 포트폴리오 데이터 가져오기
            const portfolioResponse = await fetch(`${API_BASE_URL}/api/applicants/${existingApplicant._id}/portfolio`);
            if (portfolioResponse.ok) {
              documentData = await portfolioResponse.json();
            }
          }
          break;
        default:
          return;
      }
      
      if (documentData) {
        setPreviewDocument({
          type: documentType,
          data: documentData,
          applicantName: existingApplicant.name
        });
        setIsPreviewModalOpen(true);
      }
    } catch (error) {
      console.error('문서 미리보기 중 오류:', error);
      alert('문서를 불러올 수 없습니다.');
    }
  };

  // 문서 미리보기 모달 닫기
  const closePreviewModal = () => {
    setIsPreviewModalOpen(false);
    setPreviewDocument(null);
  };

  // 페이지네이션 함수들
  const totalPages = Math.ceil(filteredApplicants.length / itemsPerPage);
  
  // 디버깅 로그
  console.log('🔍 페이지네이션 디버깅:', {
    totalApplicants: applicants?.length || 0,
    filteredApplicants: filteredApplicants?.length || 0,
    itemsPerPage,
    totalPages,
    currentPage
  });
  
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    // 페이지 상단으로 스크롤
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  
  const goToPreviousPage = () => {
    if (currentPage > 1) {
      handlePageChange(currentPage - 1);
    }
  };
  
  const goToNextPage = () => {
    if (currentPage < totalPages) {
      handlePageChange(currentPage + 1);
    }
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
            <NewResumeButton onClick={handleNewResumeModalOpen}>
              <FiFileText size={16} />
              새 지원자 등록
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
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ delay: 0.05, duration: 0.3, ease: "easeOut" }}
          $variant="total"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <StatIcon>
            <FiUser size={24} />
          </StatIcon>
          <StatContent>
            <StatValue
              key={stats.total}
              initial={{ scale: 1 }}
              animate={{ scale: [1, 1.02, 1] }}
              transition={{ duration: 0.1 }}
            >
              {stats.total}
            </StatValue>
            <StatLabel>총 지원자</StatLabel>
            <StatPercentage>
              {stats.total > 0 ? '100%' : '0%'}
            </StatPercentage>
          </StatContent>
        </StatCard>
        
        <StatCard
          key={`passed-${stats.passed}`}
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ delay: 0.1, duration: 0.3, ease: "easeOut" }}
          $variant="passed"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <StatIcon>
            <FiCheck size={24} />
          </StatIcon>
          <StatContent>
            <StatValue
              key={stats.passed}
              initial={{ scale: 1 }}
              animate={{ scale: [1, 1.02, 1] }}
              transition={{ duration: 0.1 }}
            >
              {stats.passed}
            </StatValue>
            <StatLabel>합격</StatLabel>
            <StatPercentage>
              {stats.total > 0 ? `${Math.round((stats.passed / stats.total) * 100)}%` : '0%'}
            </StatPercentage>
          </StatContent>
        </StatCard>
        
                 <StatCard
           key={`waiting-${stats.waiting}`}
           initial={{ opacity: 0, y: 20, scale: 0.9 }}
           animate={{ opacity: 1, y: 0, scale: 1 }}
           transition={{ delay: 0.15, duration: 0.3, ease: "easeOut" }}
           $variant="waiting"
           whileHover={{ scale: 1.02 }}
           whileTap={{ scale: 0.98 }}
         >
          <StatIcon>
            <FiClock size={24} />
          </StatIcon>
          <StatContent>
            <StatValue
              key={stats.waiting}
              initial={{ scale: 1 }}
              animate={{ scale: [1, 1.02, 1] }}
              transition={{ duration: 0.1 }}
            >
              {stats.waiting}
            </StatValue>
            <StatLabel>보류</StatLabel>
            <StatPercentage>
              {stats.total > 0 ? `${Math.round((stats.waiting / stats.total) * 100)}%` : '0%'}
            </StatPercentage>
          </StatContent>
        </StatCard>
        
        <StatCard
          key={`rejected-${stats.rejected}`}
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.3, ease: "easeOut" }}
          $variant="rejected"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <StatIcon>
            <FiX size={24} />
          </StatIcon>
          <StatContent>
            <StatValue
              key={stats.rejected}
              initial={{ scale: 1 }}
              animate={{ scale: [1, 1.02, 1] }}
              transition={{ duration: 0.1 }}
            >
              {stats.rejected}
            </StatValue>
            <StatLabel>불합격</StatLabel>
            <StatPercentage>
              {stats.total > 0 ? `${Math.round((stats.rejected / stats.total) * 100)}%` : '0%'}
            </StatPercentage>
          </StatContent>
        </StatCard>
      </StatsGrid>

      <SearchBar>
        <SearchSection>
          <SearchInput
            type="text"
            placeholder={hasActiveFilters ? getFilterStatusText() : "지원자 이름,직무,기술스택을 입력하세요"}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && searchTerm.trim() && !isCalculatingRanking) {
                calculateKeywordRanking();
              }
            }}
          />
          <FilterButton onClick={handleFilterClick} hasActiveFilters={hasActiveFilters}>
            <FiFilter size={16} />
            필터 {hasActiveFilters && <FilterBadge>{selectedJobs.length + selectedExperience.length + (filterStatus !== '전체' ? 1 : 0)}</FilterBadge>}
          </FilterButton>
          <FilterButton 
            onClick={calculateKeywordRanking}
            disabled={isCalculatingRanking || !searchTerm.trim()}
            style={{ 
              background: searchTerm.trim() ? 'var(--primary-color)' : 'var(--border-color)',
              color: searchTerm.trim() ? 'white' : 'var(--text-secondary)',
              cursor: searchTerm.trim() ? 'pointer' : 'not-allowed'
            }}
          >
            {isCalculatingRanking ? (
              <>
                <div className="spinner" style={{ width: '14px', height: '14px', border: '2px solid transparent', borderTop: '2px solid currentColor', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                계산중...
              </>
            ) : (
              <>
                <FiBarChart2 size={16} />
                랭킹 계산
              </>
            )}
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

      {/* 키워드 랭킹 결과 표시 */}
      {rankingResults && rankingResults.length > 0 && (
        <RankingResultsSection>
          <RankingHeader>
            <RankingTitle>
              <FiBarChart2 size={20} />
              검색어 "{searchTerm}" 랭킹 결과
            </RankingTitle>
                      <RankingStats>
            총 {rankingResults.length}명 중 상위 5명 표시
          </RankingStats>
            <RankingClearButton onClick={() => {
              setRankingResults(null);
              setSearchTerm('');
            }}>
              <FiX size={16} />
              초기화
            </RankingClearButton>
          </RankingHeader>
          
          <RankingTable>
            <RankingTableHeader>
              <RankingTableHeaderCell>순위</RankingTableHeaderCell>
              <RankingTableHeaderCell>지원자</RankingTableHeaderCell>
              <RankingTableHeaderCell>직무</RankingTableHeaderCell>
              <RankingTableHeaderCell>총점</RankingTableHeaderCell>
              <RankingTableHeaderCell>세부 점수</RankingTableHeaderCell>
              <RankingTableHeaderCell>상태</RankingTableHeaderCell>
            </RankingTableHeader>
            
            {/* 첫 화면에 보이는 상위 5명 */}
            <RankingTableBody>
              {rankingResults.slice(0, 5).map((result, index) => (
                <RankingTableRow key={result.applicant.id}>
                  <RankingTableCell>
                    <RankBadge rank={result.rank}>
                      {result.rankText}
                    </RankBadge>
                  </RankingTableCell>
                  <RankingTableCell>
                    <ApplicantInfo>
                      <div>
                        <div style={{ fontWeight: '600', fontSize: '14px' }}>{result.applicant.name}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{result.applicant.email}</div>
                      </div>
                    </ApplicantInfo>
                  </RankingTableCell>
                  <RankingTableCell>
                    <div style={{ fontSize: '13px' }}>{result.applicant.position}</div>
                  </RankingTableCell>
                  <RankingTableCell>
                    <TotalScore>
                      {result.totalScore}점
                    </TotalScore>
                  </RankingTableCell>
                  <RankingTableCell>
                    <ScoreBreakdown>
                      <ScoreItem>
                        <span>이력서:</span>
                        <span style={{ color: result.breakdown.resume >= 7 ? '#10b981' : result.breakdown.resume >= 5 ? '#f59e0b' : '#ef4444' }}>
                          {result.breakdown.resume}점
                        </span>
                      </ScoreItem>
                      <ScoreItem>
                        <span>자소서:</span>
                        <span style={{ color: result.breakdown.coverLetter >= 7 ? '#10b981' : result.breakdown.coverLetter >= 5 ? '#f59e0b' : '#ef4444' }}>
                          {result.breakdown.coverLetter}점
                        </span>
                      </ScoreItem>
                      <ScoreItem>
                        <span>포트폴리오:</span>
                        <span style={{ color: result.breakdown.portfolio >= 7 ? '#10b981' : result.breakdown.portfolio >= 5 ? '#f59e0b' : '#ef4444' }}>
                          {result.breakdown.portfolio}점
                        </span>
                      </ScoreItem>
                      <ScoreItem>
                        <span>키워드:</span>
                        <span style={{ color: result.breakdown.keywordMatching >= 7 ? '#10b981' : result.breakdown.keywordMatching >= 5 ? '#f59e0b' : '#ef4444' }}>
                          {result.breakdown.keywordMatching}점
                        </span>
                      </ScoreItem>
                    </ScoreBreakdown>
                  </RankingTableCell>
                  <RankingTableCell>
                    <StatusBadge status={result.applicant.status}>
                      {getStatusText(result.applicant.status)}
                    </StatusBadge>
                  </RankingTableCell>
                </RankingTableRow>
              ))}
            </RankingTableBody>
            
            {/* 스크롤해서 볼 수 있는 나머지 결과들 */}
            {rankingResults.length > 5 && (
              <RankingTableBody style={{ maxHeight: '400px', marginTop: '16px' }}>
                {rankingResults.slice(5).map((result, index) => (
                  <RankingTableRow key={result.applicant.id}>
                    <RankingTableCell>
                      <RankBadge rank={result.rank}>
                        {result.rankText}
                      </RankBadge>
                    </RankingTableCell>
                    <RankingTableCell>
                      <ApplicantInfo>
                        <div>
                          <div style={{ fontWeight: '600', fontSize: '14px' }}>{result.applicant.name}</div>
                          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{result.applicant.email}</div>
                        </div>
                      </ApplicantInfo>
                    </RankingTableCell>
                    <RankingTableCell>
                      <div style={{ fontSize: '13px' }}>{result.applicant.position}</div>
                    </RankingTableCell>
                    <RankingTableCell>
                      <TotalScore>
                        {result.totalScore}점
                      </TotalScore>
                    </RankingTableCell>
                    <RankingTableCell>
                      <ScoreBreakdown>
                        <ScoreItem>
                          <span>이력서:</span>
                          <span style={{ color: result.breakdown.resume >= 7 ? '#10b981' : result.breakdown.resume >= 5 ? '#f59e0b' : '#ef4444' }}>
                            {result.breakdown.resume}점
                          </span>
                        </ScoreItem>
                        <ScoreItem>
                          <span>자소서:</span>
                          <span style={{ color: result.breakdown.coverLetter >= 7 ? '#10b981' : result.breakdown.coverLetter >= 5 ? '#f59e0b' : '#ef4444' }}>
                            {result.breakdown.coverLetter}점
                          </span>
                        </ScoreItem>
                        <ScoreItem>
                          <span>포트폴리오:</span>
                          <span style={{ color: result.breakdown.portfolio >= 7 ? '#10b981' : result.breakdown.portfolio >= 5 ? '#f59e0b' : '#ef4444' }}>
                            {result.breakdown.portfolio}점
                          </span>
                        </ScoreItem>
                        <ScoreItem>
                          <span>키워드:</span>
                          <span style={{ color: result.breakdown.keywordMatching >= 7 ? '#10b981' : result.breakdown.keywordMatching >= 5 ? '#f59e0b' : '#ef4444' }}>
                            {result.breakdown.keywordMatching}점
                          </span>
                        </ScoreItem>
                      </ScoreBreakdown>
                    </RankingTableCell>
                    <RankingTableCell>
                      <StatusBadge status={result.applicant.status}>
                        {getStatusText(result.applicant.status)}
                      </StatusBadge>
                    </RankingTableCell>
                  </RankingTableRow>
                ))}
              </RankingTableBody>
            )}
          </RankingTable>
          
          {rankingResults.length > 5 && (
            <RankingFooter>
              <RankingFooterText>
                전체 {rankingResults.length}명의 랭킹이 계산되었습니다. 
                상위 5명이 먼저 표시되며, 나머지는 아래로 스크롤하여 확인할 수 있습니다.
              </RankingFooterText>
            </RankingFooter>
          )}
        </RankingResultsSection>
      )}

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
        <>
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

          {/* 페이지네이션 */}
          {totalPages > 0 && (
            <PaginationContainer>
              <PaginationButton 
                onClick={goToPreviousPage}
                disabled={currentPage === 1}
              >
                ← 이전
              </PaginationButton>
              
              <PageNumbers>
                {Array.from({ length: totalPages }, (_, index) => index + 1).map((pageNumber) => (
                  <PageNumber
                    key={pageNumber}
                    onClick={() => handlePageChange(pageNumber)}
                    isActive={pageNumber === currentPage}
                  >
                    {pageNumber}
                  </PageNumber>
                ))}
              </PageNumbers>
              
              <PaginationButton 
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
              >
                다음 →
              </PaginationButton>
            </PaginationContainer>
          )}
        </>
      ) : (
        <>
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

          {/* 페이지네이션 (보드 뷰) */}
          {totalPages > 0 && (
            <PaginationContainer>
              <PaginationButton 
                onClick={goToPreviousPage}
                disabled={currentPage === 1}
              >
                ← 이전
              </PaginationButton>
              
              <PageNumbers>
                {Array.from({ length: totalPages }, (_, index) => index + 1).map((pageNumber) => (
                  <PageNumber
                    key={pageNumber}
                    onClick={() => handlePageChange(pageNumber)}
                    isActive={pageNumber === currentPage}
                  >
                    {pageNumber}
                  </PageNumber>
                ))}
              </PageNumbers>
              
              <PaginationButton 
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
              >
                다음 →
              </PaginationButton>
            </PaginationContainer>
          )}
        </>
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

              <DocumentButtons>
                <ResumeButton onClick={() => handleResumeModalOpen(selectedApplicant)}>
                  <FiFileText size={16} />
                  이력서
                </ResumeButton>
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
                    {/* 자소서 분석 결과 섹션 - 유사도 체크 결과 위에 배치 */}
                    <DocumentSection>
                      <DocumentSectionTitle>자소서 분석 결과</DocumentSectionTitle>
                      <CoverLetterAnalysis 
                        analysisData={{
                          technical_suitability: documentModal.documentData?.analysis?.technical_suitability || 75,
                          job_understanding: documentModal.documentData?.analysis?.job_understanding || 80,
                          growth_potential: documentModal.documentData?.analysis?.growth_potential || 85,
                          teamwork_communication: documentModal.documentData?.analysis?.teamwork_communication || 70,
                          motivation_company_fit: documentModal.documentData?.analysis?.motivation_company_fit || 90
                        }}
                      />
                    </DocumentSection>

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
                                <strong>비교 대상:</strong> {documentModal.similarityData.statistics.total_compared}명
                              </div>
                              <div>
                                <strong>평균 유사도:</strong> {(documentModal.similarityData.statistics.average_similarity * 100).toFixed(1)}%
                              </div>
                              <div>
                                <strong>높은 유사도:</strong> {documentModal.similarityData.statistics.high_similarity_count}명 (70% 이상)
                              </div>
                              <div>
                                <strong>중간 유사도:</strong> {documentModal.similarityData.statistics.moderate_similarity_count}명 (40-70%)
                              </div>
                            </DocumentGrid>
                          </DocumentCard>

                          {/* 표절 위험도 분석 */}
                          {documentModal.similarityData.plagiarism_analysis && documentModal.similarityData.plagiarism_analysis.success && (
                            <DocumentCard>
                              <DocumentCardTitle>⚠️ 표절 위험도 분석</DocumentCardTitle>
                              <div style={{
                                padding: '12px',
                                borderRadius: '8px',
                                backgroundColor: documentModal.similarityData.plagiarism_analysis.risk_level === 'HIGH' ? '#fff5f5' : 
                                                documentModal.similarityData.plagiarism_analysis.risk_level === 'MEDIUM' ? '#fffbf0' : '#f0fff4',
                                border: `2px solid ${documentModal.similarityData.plagiarism_analysis.risk_level === 'HIGH' ? '#ff4757' : 
                                                   documentModal.similarityData.plagiarism_analysis.risk_level === 'MEDIUM' ? '#ffa502' : '#2ed573'}`
                              }}>
                                <div style={{
                                  fontWeight: 'bold',
                                  marginBottom: '8px',
                                  color: documentModal.similarityData.plagiarism_analysis.risk_level === 'HIGH' ? '#ff4757' : 
                                        documentModal.similarityData.plagiarism_analysis.risk_level === 'MEDIUM' ? '#ffa502' : '#2ed573'
                                }}>
                                  위험도: {documentModal.similarityData.plagiarism_analysis.risk_level} 
                                  ({(documentModal.similarityData.plagiarism_analysis.risk_score * 100).toFixed(1)}%)
                                </div>
                                <div style={{fontSize: '14px', color: '#333', marginBottom: '8px', whiteSpace: 'pre-line'}}>
                                  {documentModal.similarityData.plagiarism_analysis.analysis}
                                </div>
                                
                                {documentModal.similarityData.plagiarism_analysis.recommendations && 
                                 documentModal.similarityData.plagiarism_analysis.recommendations.length > 0 && (
                                  <div>
                                    <div style={{fontSize: '12px', fontWeight: 'bold', color: '#666', marginBottom: '4px'}}>
                                      권장사항:
                                    </div>
                                    <ul style={{margin: '0', paddingLeft: '16px'}}>
                                      {documentModal.similarityData.plagiarism_analysis.recommendations.map((rec, idx) => (
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
                          {documentModal.similarityData.top_similar.length > 0 && (
                            <DocumentCard>
                              <DocumentCardTitle>🎯 가장 유사한 자소서 TOP 5</DocumentCardTitle>
                              {documentModal.similarityData.top_similar.map((similar, index) => (
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

                {/* 기존 지원자 정보 표시 */}
                {existingApplicant && (
                  <ExistingApplicantInfo>
                    <ExistingApplicantTitle>🔄 기존 지원자 발견</ExistingApplicantTitle>
                    <ExistingApplicantDetails>
                      <div><strong>이름:</strong> {existingApplicant.name}</div>
                      <div><strong>이메일:</strong> {existingApplicant.email || 'N/A'}</div>
                      <div><strong>현재 서류:</strong></div>
                      <ul>
                        <li>
                          이력서: {existingApplicant.resume ? '✅ 있음' : '❌ 없음'}
                          {existingApplicant.resume && (
                            <PreviewButton onClick={() => handlePreviewDocument('resume')}>
                              👁️ 미리보기
                            </PreviewButton>
                          )}
                        </li>
                        <li>
                          자기소개서: {existingApplicant.cover_letter ? '✅ 있음' : '❌ 없음'}
                          {existingApplicant.cover_letter && (
                            <PreviewButton onClick={() => handlePreviewDocument('cover_letter')}>
                              👁️ 미리보기
                            </PreviewButton>
                          )}
                        </li>
                        <li>
                          포트폴리오: {existingApplicant.portfolio ? '✅ 있음' : '❌ 없음'}
                          {existingApplicant.portfolio && (
                            <PreviewButton onClick={() => handlePreviewDocument('portfolio')}>
                              👁️ 미리보기
                            </PreviewButton>
                          )}
                        </li>
                      </ul>
                      
                      {/* 교체 옵션 체크박스 */}
                      <ReplaceOptionSection>
                        <ReplaceOptionLabel>
                          <input
                            type="checkbox"
                            checked={replaceExisting}
                            onChange={(e) => setReplaceExisting(e.target.checked)}
                          />
                          <span>기존 서류를 새 서류로 교체</span>
                        </ReplaceOptionLabel>
                        <ReplaceOptionDescription>
                          체크하면 기존에 있는 서류를 새로 업로드한 서류로 교체합니다.
                          체크하지 않으면 중복 서류는 업로드되지 않습니다.
                        </ReplaceOptionDescription>
                      </ReplaceOptionSection>
                    </ExistingApplicantDetails>
                  </ExistingApplicantInfo>
                )}

                <ResumeFormActions>
                  <ResumeSubmitButton 
                    onClick={handleResumeSubmit}
                    disabled={(!resumeFile && !coverLetterFile && !portfolioFile) || isAnalyzing || isCheckingDuplicate}
                  >
                    {isAnalyzing ? '처리 중...' : isCheckingDuplicate ? '중복 체크 중...' : '업로드 및 저장'}
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

      {/* 새로운 이력서 모달 */}
      <ResumeModal
        isOpen={isResumeModalOpen}
        onClose={handleResumeModalClose}
        applicant={selectedResumeApplicant}
        onViewSummary={() => {
          handleResumeModalClose();
          // 요약보기 로직 추가
        }}
      />

      {/* 문서 미리보기 모달 */}
      <AnimatePresence>
        {isPreviewModalOpen && previewDocument && (
          <DocumentPreviewModal
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            <DocumentPreviewContent>
              <DocumentPreviewHeader>
                <DocumentPreviewTitle>
                  📄 {previewDocument.applicantName}님의 {
                    previewDocument.type === 'resume' ? '이력서' :
                    previewDocument.type === 'cover_letter' ? '자기소개서' :
                    '포트폴리오'
                  } 미리보기
                </DocumentPreviewTitle>
                <CloseButton onClick={closePreviewModal}>
                  <FiX size={20} />
                </CloseButton>
              </DocumentPreviewHeader>
              
              <div style={{ flex: 1, overflow: 'hidden' }}>
                {previewDocument.type === 'resume' && (
                  <div>
                    <h4 style={{ padding: '20px 24px 0', margin: 0 }}>📋 이력서 내용</h4>
                    <DocumentText>
                      {previewDocument.data.extracted_text || '이력서 내용을 불러올 수 없습니다.'}
                    </DocumentText>
                  </div>
                )}
                
                {previewDocument.type === 'cover_letter' && (
                  <div>
                    <h4 style={{ padding: '20px 24px 0', margin: 0 }}>📝 자기소개서 내용</h4>
                    <DocumentText>
                      {previewDocument.data.extracted_text || '자기소개서 내용을 불러올 수 없습니다.'}
                    </DocumentText>
                  </div>
                )}
                
                {previewDocument.type === 'portfolio' && (
                  <div>
                    <h4 style={{ padding: '20px 24px 0', margin: 0 }}>💼 포트폴리오 내용</h4>
                    <DocumentText>
                      {previewDocument.data.extracted_text || '포트폴리오 내용을 불러올 수 없습니다.'}
                    </DocumentText>
                  </div>
                )}
              </div>
              
              <DocumentPreviewFooter>
                <PreviewCloseButton onClick={closePreviewModal}>
                  닫기
                </PreviewCloseButton>
              </DocumentPreviewFooter>
            </DocumentPreviewContent>
          </DocumentPreviewModal>
        )}
      </AnimatePresence>
    </Container>
  );
};

// 새로운 스타일 컴포넌트들
const StatIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  margin-bottom: 12px;
  
  ${props => {
    switch (props.$variant) {
      case 'total':
        return `
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        `;
      case 'passed':
        return `
          background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
          color: white;
        `;
      case 'waiting':
        return `
          background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
          color: white;
        `;
      case 'rejected':
        return `
          background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
          color: white;
        `;
      default:
        return `
          background: #e2e8f0;
          color: #4a5568;
        `;
    }
  }}
`;

const StatContent = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  flex: 1;
`;

const StatPercentage = styled.div`
  font-size: 0.875rem;
  font-weight: 500;
  color: #718096;
  margin-top: 4px;
`;

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

// 문서 미리보기 관련 스타일 컴포넌트들
const DocumentPreviewModal = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const DocumentPreviewContent = styled.div`
  background-color: white;
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
`;

const DocumentPreviewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  background-color: #f8fafc;
`;

const DocumentPreviewTitle = styled.h3`
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
`;

const DocumentPreviewFooter = styled.div`
  display: flex;
  justify-content: center;
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
`;

const PreviewCloseButton = styled.button`
  background-color: #4a5568;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background-color: #2d3748;
    transform: translateY(-1px);
  }
`;

const DocumentText = styled.div`
  padding: 20px 24px;
  max-height: 60vh;
  overflow-y: auto;
  line-height: 1.6;
  color: #2d3748;
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
  background-color: #f7fafc;
  border-radius: 8px;
  margin: 20px 24px;
  border: 1px solid #e2e8f0;
`;

const PreviewButton = styled.button`
  background-color: #4299e1;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 8px;

  &:hover {
    background-color: #3182ce;
    transform: translateY(-1px);
  }
`;

// 페이지네이션 스타일 컴포넌트들
const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 40px 0;
  gap: 16px;
`;

const PaginationButton = styled.button`
  background-color: #4a5568;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    background-color: #2d3748;
    transform: translateY(-1px);
  }

  &:disabled {
    background-color: #cbd5e0;
    cursor: not-allowed;
    transform: none;
  }
`;

const PageNumbers = styled.div`
  display: flex;
  gap: 8px;
`;

const PageNumber = styled.button`
  background-color: ${props => props.isActive ? '#4299e1' : '#e2e8f0'};
  color: ${props => props.isActive ? 'white' : '#4a5568'};
  border: none;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: ${props => props.isActive ? '700' : '500'};
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 48px;
  text-decoration: ${props => props.isActive ? 'underline' : 'none'};

  &:hover {
    background-color: ${props => props.isActive ? '#3182ce' : '#cbd5e0'};
    transform: translateY(-1px);
  }
`;

// 랭킹 결과 스타일 컴포넌트들
const RankingResultsSection = styled.div`
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
`;

const RankingHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--primary-color);
`;

const RankingTitle = styled.h3`
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
`;

const RankingStats = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--background-secondary);
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
`;

const RankingClearButton = styled.button`
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e5e7eb;
    color: #374151;
    transform: translateY(-1px);
  }
`;

const RankingTable = styled.div`
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  max-height: 600px;
`;

const RankingTableBody = styled.div`
  max-height: 500px;
  overflow-y: auto;
  
  /* 스크롤바 스타일링 */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--background-secondary);
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
    
    &:hover {
      background: var(--text-secondary);
    }
  }
`;

const RankingTableHeader = styled.div`
  display: grid;
  grid-template-columns: 80px 1fr 120px 100px 1fr 100px;
  gap: 16px;
  padding: 16px;
  background: var(--background-secondary);
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
`;

const RankingTableHeaderCell = styled.div`
  text-align: center;
  
  &:nth-child(1) { text-align: center; }
  &:nth-child(2) { text-align: left; }
  &:nth-child(3) { text-align: center; }
  &:nth-child(4) { text-align: center; }
  &:nth-child(5) { text-align: left; }
  &:nth-child(6) { text-align: center; }
`;

const RankingTableRow = styled.div`
  display: grid;
  grid-template-columns: 80px 1fr 120px 100px 1fr 100px;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--background-secondary);
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const RankingTableCell = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  
  &:nth-child(2) { justify-content: flex-start; }
  &:nth-child(3) { justify-content: center; }
  &:nth-child(4) { justify-content: center; }
  &:nth-child(5) { justify-content: flex-start; }
  &:nth-child(6) { justify-content: center; }
`;

const TotalScore = styled.div`
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-color);
  background: linear-gradient(135deg, rgba(0, 200, 81, 0.1), rgba(0, 200, 81, 0.05));
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(0, 200, 81, 0.2);
`;

const ScoreBreakdown = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
`;

const ScoreItem = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 8px;
  
  span:first-child {
    color: var(--text-secondary);
    min-width: 60px;
  }
  
  span:last-child {
    font-weight: 600;
  }
`;

const RankingFooter = styled.div`
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  text-align: center;
`;

const RankingFooterText = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--background-secondary);
  padding: 12px 24px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
`;

export default ApplicantManagement; 
