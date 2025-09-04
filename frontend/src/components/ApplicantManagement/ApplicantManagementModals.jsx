import React, { useState, useCallback, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import ApplicantDetailModal from './ApplicantDetailModal';
import DocumentModal from './DocumentModal';
import NewApplicantModal from './NewApplicantModal';

const ApplicantManagementModals = ({
  // 모달 상태
  detailModal,
  resumeModal,
  documentModal,
  newApplicantModal,

  // 모달 핸들러
  onDetailModalOpen,
  onDetailModalClose,
  onResumeModalOpen,
  onResumeModalClose,
  onDocumentModalOpen,
  onDocumentModalClose,
  onNewApplicantModalOpen,
  onNewApplicantModalClose,

  // 데이터 핸들러
  onResumeSubmit,
  onPortfolioViewChange,

  // API 관련
  API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'
}) => {
  // 포트폴리오 관련 상태
  const [portfolioView, setPortfolioView] = useState('select');
  const [portfolioData, setPortfolioData] = useState(null);
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false);

  // 문서 데이터 상태
  const [documentData, setDocumentData] = useState(null);
  const [similarityData, setSimilarityData] = useState(null);
  const [isLoadingSimilarity, setIsLoadingSimilarity] = useState(false);

  // 포트폴리오 뷰 변경 핸들러
  const handlePortfolioViewChange = useCallback((view) => {
    setPortfolioView(view);
    if (onPortfolioViewChange) {
      onPortfolioViewChange(view);
    }

    // 포트폴리오 데이터 로드
    if (view !== 'select' && documentModal.applicant) {
      loadPortfolioData(view, documentModal.applicant);
    }
  }, [onPortfolioViewChange, documentModal.applicant]);

  // 포트폴리오 데이터 로드
  const loadPortfolioData = useCallback(async (view, applicant) => {
    if (!applicant) return;

    setIsLoadingPortfolio(true);
    try {
      let endpoint = '';
      if (view === 'github') {
        endpoint = `${API_BASE_URL}/api/applicants/${applicant.id}/portfolio/github`;
      } else {
        endpoint = `${API_BASE_URL}/api/applicants/${applicant.id}/portfolio`;
      }

      const response = await fetch(endpoint);
      if (response.ok) {
        const data = await response.json();
        setPortfolioData(data);
      } else {
        console.error('포트폴리오 데이터 로드 실패:', response.statusText);
        setPortfolioData(null);
      }
    } catch (error) {
      console.error('포트폴리오 데이터 로드 오류:', error);
      setPortfolioData(null);
    } finally {
      setIsLoadingPortfolio(false);
    }
  }, [API_BASE_URL]);

  // 문서 모달 열기 시 데이터 로드
  const handleDocumentModalOpen = useCallback(async (type, applicant) => {
    if (!applicant) return;

    // 문서 데이터 로드
    try {
      let endpoint = '';
      switch (type) {
        case 'resume':
          endpoint = `${API_BASE_URL}/api/applicants/${applicant.id}/resume`;
          break;
        case 'coverLetter':
          endpoint = `${API_BASE_URL}/api/applicants/${applicant.id}/cover-letter`;
          break;
        case 'portfolio':
          endpoint = `${API_BASE_URL}/api/applicants/${applicant.id}/portfolio`;
          break;
        default:
          break;
      }

      if (endpoint) {
        const response = await fetch(endpoint);
        if (response.ok) {
          const data = await response.json();
          setDocumentData(data);
        } else {
          console.error('문서 데이터 로드 실패:', response.statusText);
          setDocumentData(null);
        }
      }

      // 자소서인 경우 유사도 체크
      if (type === 'coverLetter') {
        await checkSimilarity(applicant.id);
      }

      // 포트폴리오인 경우 뷰 초기화
      if (type === 'portfolio') {
        setPortfolioView('select');
        setPortfolioData(null);
      }

    } catch (error) {
      console.error('문서 데이터 로드 오류:', error);
      setDocumentData(null);
    }

    // 모달 열기
    if (onDocumentModalOpen) {
      onDocumentModalOpen(type, applicant);
    }
  }, [API_BASE_URL, onDocumentModalOpen]);

  // 유사도 체크
  const checkSimilarity = useCallback(async (applicantId) => {
    setIsLoadingSimilarity(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/cover-letters/similarity-check/${applicantId}`);
      if (response.ok) {
        const data = await response.json();
        setSimilarityData(data);
      } else {
        console.error('유사도 체크 실패:', response.statusText);
        setSimilarityData(null);
      }
    } catch (error) {
      console.error('유사도 체크 오류:', error);
      setSimilarityData(null);
    } finally {
      setIsLoadingSimilarity(false);
    }
  }, [API_BASE_URL]);

  // 문서 모달 닫기
  const handleDocumentModalClose = useCallback(() => {
    setDocumentData(null);
    setSimilarityData(null);
    setPortfolioData(null);
    setPortfolioView('select');
    if (onDocumentModalClose) {
      onDocumentModalClose();
    }
  }, [onDocumentModalClose]);

  // 새 지원자 등록 제출
  const handleNewApplicantSubmit = useCallback(async (formData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        console.log('새 지원자 등록 성공:', result);

        // 성공 시 모달 닫기 및 콜백 실행
        if (onNewApplicantModalClose) {
          onNewApplicantModalClose();
        }

        // 부모 컴포넌트에 새로고침 요청
        if (onResumeSubmit) {
          onResumeSubmit(result);
        }
      } else {
        const error = await response.json();
        console.error('새 지원자 등록 실패:', error);
        alert('지원자 등록에 실패했습니다: ' + (error.message || '알 수 없는 오류'));
      }
    } catch (error) {
      console.error('새 지원자 등록 오류:', error);
      alert('지원자 등록 중 오류가 발생했습니다.');
    }
  }, [API_BASE_URL, onNewApplicantModalClose, onResumeSubmit]);

  // 지원자 상세정보에서 이력서 보기
  const handleResumeClick = useCallback((applicant) => {
    handleDocumentModalOpen('resume', applicant);
  }, [handleDocumentModalOpen]);

  // 지원자 상세정보에서 자소서 보기
  const handleDocumentClick = useCallback((type, applicant) => {
    handleDocumentModalOpen(type, applicant);
  }, [handleDocumentModalOpen]);

  // 지원자 상세정보에서 포트폴리오 보기
  const handlePortfolioClick = useCallback((applicant) => {
    handleDocumentModalOpen('portfolio', applicant);
  }, [handleDocumentModalOpen]);

  // 모달 닫기 시 상태 초기화
  const handleDetailModalClose = useCallback(() => {
    if (onDetailModalClose) {
      onDetailModalClose();
    }
  }, [onDetailModalClose]);

  const handleResumeModalClose = useCallback(() => {
    if (onResumeModalClose) {
      onResumeModalClose();
    }
  }, [onResumeModalClose]);

  const handleNewApplicantModalClose = useCallback(() => {
    if (onNewApplicantModalClose) {
      onNewApplicantModalClose();
    }
  }, [onNewApplicantModalClose]);

  return (
    <AnimatePresence>
      {/* 지원자 상세정보 모달 */}
      {detailModal.isOpen && detailModal.applicant && (
        <ApplicantDetailModal
          isOpen={detailModal.isOpen}
          applicant={detailModal.applicant}
          onClose={handleDetailModalClose}
          onResumeClick={handleResumeClick}
          onDocumentClick={handleDocumentClick}
          onPortfolioClick={handlePortfolioClick}
        />
      )}

      {/* 문서 보기 모달 */}
      {documentModal.isOpen && documentModal.applicant && (
        <DocumentModal
          isOpen={documentModal.isOpen}
          type={documentModal.type}
          applicant={documentModal.applicant}
          documentData={documentData}
          similarityData={similarityData}
          isLoadingSimilarity={isLoadingSimilarity}
          onClose={handleDocumentModalClose}
          onPortfolioViewChange={handlePortfolioViewChange}
        />
      )}

      {/* 새 지원자 등록 모달 */}
      {newApplicantModal.isOpen && (
        <NewApplicantModal
          isOpen={newApplicantModal.isOpen}
          onClose={handleNewApplicantModalClose}
          onSubmit={handleNewApplicantSubmit}
          existingApplicant={newApplicantModal.existingApplicant}
          isCheckingDuplicate={newApplicantModal.isCheckingDuplicate}
          onReplaceExisting={newApplicantModal.onReplaceExisting}
        />
      )}
    </AnimatePresence>
  );
};

export default ApplicantManagementModals;
