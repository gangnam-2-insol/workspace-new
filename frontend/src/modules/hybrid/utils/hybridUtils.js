/**
 * 하이브리드 분석 유틸리티
 * 
 * 하이브리드 분석 관련 유틸리티 함수들을 제공합니다.
 */

import { getScoreColor, formatDate } from '../../shared/utils';

/**
 * 분석 타입별 라벨 반환
 * @param {string} analysisType - 분석 타입
 * @returns {string} 분석 타입 라벨
 */
export const getAnalysisTypeLabel = (analysisType) => {
    const labels = {
        'comprehensive': '종합 분석',
        'cross_reference': '교차 참조 분석',
        'integrated_evaluation': '통합 평가'
    };
    return labels[analysisType] || analysisType;
};

/**
 * 분석 상태별 라벨 반환
 * @param {string} status - 분석 상태
 * @returns {string} 상태 라벨
 */
export const getAnalysisStatusLabel = (status) => {
    const labels = {
        'pending': '대기 중',
        'processing': '분석 중',
        'completed': '완료',
        'failed': '실패'
    };
    return labels[status] || status;
};

/**
 * 분석 상태별 색상 반환
 * @param {string} status - 분석 상태
 * @returns {string} 색상 클래스
 */
export const getAnalysisStatusColor = (status) => {
    const colors = {
        'pending': 'text-yellow-600 bg-yellow-100',
        'processing': 'text-blue-600 bg-blue-100',
        'completed': 'text-green-600 bg-green-100',
        'failed': 'text-red-600 bg-red-100'
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
};

/**
 * 종합 점수 등급 반환
 * @param {number} score - 종합 점수
 * @returns {string} 등급
 */
export const getScoreGrade = (score) => {
    if (score >= 90) return 'A+';
    if (score >= 85) return 'A';
    if (score >= 80) return 'A-';
    if (score >= 75) return 'B+';
    if (score >= 70) return 'B';
    if (score >= 65) return 'B-';
    if (score >= 60) return 'C+';
    if (score >= 55) return 'C';
    if (score >= 50) return 'C-';
    return 'D';
};

/**
 * 종합 점수 등급별 색상 반환
 * @param {number} score - 종합 점수
 * @returns {string} 색상 클래스
 */
export const getScoreGradeColor = (score) => {
    const grade = getScoreGrade(score);
    const colors = {
        'A+': 'text-green-800 bg-green-100',
        'A': 'text-green-700 bg-green-50',
        'A-': 'text-green-600 bg-green-50',
        'B+': 'text-blue-800 bg-blue-100',
        'B': 'text-blue-700 bg-blue-50',
        'B-': 'text-blue-600 bg-blue-50',
        'C+': 'text-yellow-800 bg-yellow-100',
        'C': 'text-yellow-700 bg-yellow-50',
        'C-': 'text-yellow-600 bg-yellow-50',
        'D': 'text-red-800 bg-red-100'
    };
    return colors[grade] || 'text-gray-800 bg-gray-100';
};

/**
 * 문서 타입별 아이콘 반환
 * @param {string} documentType - 문서 타입
 * @returns {string} 아이콘 클래스
 */
export const getDocumentTypeIcon = (documentType) => {
    const icons = {
        'resume': '📄',
        'cover_letter': '✉️',
        'portfolio': '💼'
    };
    return icons[documentType] || '📋';
};

/**
 * 문서 타입별 라벨 반환
 * @param {string} documentType - 문서 타입
 * @returns {string} 문서 타입 라벨
 */
export const getDocumentTypeLabel = (documentType) => {
    const labels = {
        'resume': '이력서',
        'cover_letter': '자기소개서',
        'portfolio': '포트폴리오'
    };
    return labels[documentType] || documentType;
};

/**
 * 가중치 계산
 * @param {number} resumeScore - 이력서 점수
 * @param {number} coverLetterScore - 자기소개서 점수
 * @param {number} portfolioScore - 포트폴리오 점수
 * @returns {Object} 가중치별 점수
 */
export const calculateWeightedScores = (resumeScore, coverLetterScore, portfolioScore) => {
    const weights = {
        resume: 0.4,
        coverLetter: 0.3,
        portfolio: 0.3
    };

    const weightedScores = {
        resume: resumeScore ? resumeScore * weights.resume : 0,
        coverLetter: coverLetterScore ? coverLetterScore * weights.coverLetter : 0,
        portfolio: portfolioScore ? portfolioScore * weights.portfolio : 0
    };

    const totalWeight = Object.values(weights).reduce((sum, weight) => {
        if (resumeScore && weight === weights.resume) return sum + weight;
        if (coverLetterScore && weight === weights.coverLetter) return sum + weight;
        if (portfolioScore && weight === weights.portfolio) return sum + weight;
        return sum;
    }, 0);

    const comprehensiveScore = totalWeight > 0 
        ? Object.values(weightedScores).reduce((sum, score) => sum + score, 0) / totalWeight
        : 0;

    return {
        weightedScores,
        comprehensiveScore: Math.round(comprehensiveScore * 10) / 10
    };
};

/**
 * 교차 참조 분석 결과 요약 생성
 * @param {Object} crossReference - 교차 참조 분석 결과
 * @returns {Object} 요약 정보
 */
export const generateCrossReferenceSummary = (crossReference) => {
    const { consistency_score, completeness_score, logical_consistency } = crossReference;
    
    const averageScore = (consistency_score + completeness_score + logical_consistency) / 3;
    
    let level = '낮음';
    if (averageScore >= 80) level = '매우 높음';
    else if (averageScore >= 70) level = '높음';
    else if (averageScore >= 60) level = '보통';
    
    return {
        averageScore: Math.round(averageScore * 10) / 10,
        level,
        consistency: consistency_score,
        completeness: completeness_score,
        logicalConsistency: logical_consistency
    };
};

/**
 * 통합 평가 결과 요약 생성
 * @param {Object} evaluation - 통합 평가 결과
 * @returns {Object} 요약 정보
 */
export const generateEvaluationSummary = (evaluation) => {
    const {
        technical_competency,
        communication_skills,
        problem_solving,
        teamwork,
        leadership,
        adaptability
    } = evaluation;

    const scores = [
        technical_competency,
        communication_skills,
        problem_solving,
        teamwork,
        leadership,
        adaptability
    ];

    const averageScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    
    const strengths = [];
    const weaknesses = [];
    
    if (technical_competency >= 80) strengths.push('기술 역량');
    else if (technical_competency < 60) weaknesses.push('기술 역량');
    
    if (communication_skills >= 80) strengths.push('의사소통 능력');
    else if (communication_skills < 60) weaknesses.push('의사소통 능력');
    
    if (problem_solving >= 80) strengths.push('문제 해결 능력');
    else if (problem_solving < 60) weaknesses.push('문제 해결 능력');
    
    if (teamwork >= 80) strengths.push('팀워크');
    else if (teamwork < 60) weaknesses.push('팀워크');
    
    if (leadership >= 80) strengths.push('리더십');
    else if (leadership < 60) weaknesses.push('리더십');
    
    if (adaptability >= 80) strengths.push('적응력');
    else if (adaptability < 60) weaknesses.push('적응력');

    return {
        averageScore: Math.round(averageScore * 10) / 10,
        strengths,
        weaknesses,
        scores: {
            technical: technical_competency,
            communication: communication_skills,
            problemSolving: problem_solving,
            teamwork,
            leadership,
            adaptability
        }
    };
};

/**
 * 분석 결과 차트 데이터 생성
 * @param {Object} analysis - 분석 결과
 * @returns {Object} 차트 데이터
 */
export const generateChartData = (analysis) => {
    const { resume_score, cover_letter_score, portfolio_score, comprehensive_score } = analysis;
    
    const documentScores = [
        { name: '이력서', score: resume_score || 0, color: getScoreColor(resume_score || 0) },
        { name: '자기소개서', score: cover_letter_score || 0, color: getScoreColor(cover_letter_score || 0) },
        { name: '포트폴리오', score: portfolio_score || 0, color: getScoreColor(portfolio_score || 0) }
    ];

    const radarData = [
        { name: '기술 역량', score: analysis.detailed_analysis?.resume_analysis?.score || 0 },
        { name: '의사소통', score: analysis.detailed_analysis?.cover_letter_analysis?.score || 0 },
        { name: '프로젝트', score: analysis.detailed_analysis?.portfolio_analysis?.score || 0 },
        { name: '종합 점수', score: comprehensive_score || 0 }
    ];

    return {
        documentScores,
        radarData,
        comprehensiveScore: comprehensive_score || 0
    };
};

/**
 * 파일 업로드 검증
 * @param {File} file - 업로드할 파일
 * @param {string} documentType - 문서 타입
 * @returns {Object} 검증 결과
 */
export const validateFileUpload = (file, documentType) => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = {
        resume: ['.pdf', '.doc', '.docx', '.txt'],
        cover_letter: ['.pdf', '.doc', '.docx', '.txt'],
        portfolio: ['.pdf', '.zip', '.rar', '.doc', '.docx']
    };

    const errors = [];

    // 파일 크기 검증
    if (file.size > maxSize) {
        errors.push(`파일 크기가 10MB를 초과합니다. (현재: ${(file.size / 1024 / 1024).toFixed(2)}MB)`);
    }

    // 파일 확장자 검증
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes[documentType].includes(fileExtension)) {
        errors.push(`지원하지 않는 파일 형식입니다. 허용된 형식: ${allowedTypes[documentType].join(', ')}`);
    }

    return {
        isValid: errors.length === 0,
        errors
    };
};

/**
 * 분석 진행률 계산
 * @param {Object} hybridDoc - 하이브리드 문서
 * @returns {number} 진행률 (0-100)
 */
export const calculateAnalysisProgress = (hybridDoc) => {
    const { resume_id, cover_letter_id, portfolio_id, analysis_status } = hybridDoc;
    
    let progress = 0;
    
    // 문서 업로드 진행률 (60%)
    const totalDocuments = 3;
    const uploadedDocuments = [resume_id, cover_letter_id, portfolio_id].filter(id => id).length;
    progress += (uploadedDocuments / totalDocuments) * 60;
    
    // 분석 진행률 (40%)
    if (analysis_status === 'completed') {
        progress += 40;
    } else if (analysis_status === 'processing') {
        progress += 20;
    }
    
    return Math.round(progress);
};

/**
 * 분석 결과 필터링
 * @param {Array} analyses - 분석 결과 목록
 * @param {Object} filters - 필터 조건
 * @returns {Array} 필터링된 결과
 */
export const filterAnalyses = (analyses, filters) => {
    return analyses.filter(analysis => {
        // 점수 필터
        if (filters.minScore && analysis.comprehensive_score < filters.minScore) return false;
        if (filters.maxScore && analysis.comprehensive_score > filters.maxScore) return false;
        
        // 상태 필터
        if (filters.status && analysis.analysis_status !== filters.status) return false;
        
        // 태그 필터
        if (filters.tags && filters.tags.length > 0) {
            const hasMatchingTag = filters.tags.some(tag => 
                analysis.tags && analysis.tags.includes(tag)
            );
            if (!hasMatchingTag) return false;
        }
        
        // 날짜 필터
        if (filters.dateFrom) {
            const analysisDate = new Date(analysis.analysis_date);
            const fromDate = new Date(filters.dateFrom);
            if (analysisDate < fromDate) return false;
        }
        
        if (filters.dateTo) {
            const analysisDate = new Date(analysis.analysis_date);
            const toDate = new Date(filters.dateTo);
            if (analysisDate > toDate) return false;
        }
        
        return true;
    });
};

/**
 * 분석 결과 정렬
 * @param {Array} analyses - 분석 결과 목록
 * @param {string} sortBy - 정렬 기준
 * @param {string} sortOrder - 정렬 순서 ('asc' 또는 'desc')
 * @returns {Array} 정렬된 결과
 */
export const sortAnalyses = (analyses, sortBy = 'analysis_date', sortOrder = 'desc') => {
    return [...analyses].sort((a, b) => {
        let aValue = a[sortBy];
        let bValue = b[sortBy];
        
        // 날짜 정렬
        if (sortBy === 'analysis_date' || sortBy === 'created_at') {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
        }
        
        // 숫자 정렬
        if (typeof aValue === 'number' && typeof bValue === 'number') {
            return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
        }
        
        // 문자열 정렬
        if (typeof aValue === 'string' && typeof bValue === 'string') {
            return sortOrder === 'asc' 
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        }
        
        // 날짜 정렬
        if (aValue instanceof Date && bValue instanceof Date) {
            return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
        }
        
        return 0;
    });
};

/**
 * 분석 결과 통계 생성
 * @param {Array} analyses - 분석 결과 목록
 * @returns {Object} 통계 정보
 */
export const generateAnalysesStatistics = (analyses) => {
    if (analyses.length === 0) {
        return {
            totalCount: 0,
            averageScore: 0,
            scoreDistribution: {},
            statusDistribution: {},
            topPerformers: []
        };
    }

    const scores = analyses.map(a => a.comprehensive_score).filter(score => score !== null && score !== undefined);
    const averageScore = scores.length > 0 ? scores.reduce((sum, score) => sum + score, 0) / scores.length : 0;

    // 점수 분포
    const scoreDistribution = {
        '90-100': 0,
        '80-89': 0,
        '70-79': 0,
        '60-69': 0,
        '50-59': 0,
        '0-49': 0
    };

    scores.forEach(score => {
        if (score >= 90) scoreDistribution['90-100']++;
        else if (score >= 80) scoreDistribution['80-89']++;
        else if (score >= 70) scoreDistribution['70-79']++;
        else if (score >= 60) scoreDistribution['60-69']++;
        else if (score >= 50) scoreDistribution['50-59']++;
        else scoreDistribution['0-49']++;
    });

    // 상태 분포
    const statusDistribution = {};
    analyses.forEach(analysis => {
        const status = analysis.analysis_status || 'unknown';
        statusDistribution[status] = (statusDistribution[status] || 0) + 1;
    });

    // 상위 성과자 (상위 10명)
    const topPerformers = analyses
        .filter(a => a.comprehensive_score !== null && a.comprehensive_score !== undefined)
        .sort((a, b) => b.comprehensive_score - a.comprehensive_score)
        .slice(0, 10);

    return {
        totalCount: analyses.length,
        averageScore: Math.round(averageScore * 10) / 10,
        scoreDistribution,
        statusDistribution,
        topPerformers
    };
};
