import React, { useState } from 'react';
import { FiUpload, FiFileText, FiStar, FiClock, FiCheckCircle } from 'react-icons/fi';

const ResumeAnalysis = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [documentType, setDocumentType] = useState('resume');

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // 파일 크기 검증 (10MB 제한)
      if (file.size > 10 * 1024 * 1024) {
        setError('파일 크기가 10MB를 초과합니다.');
        return;
      }
      
      // 파일 형식 검증
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      if (!allowedTypes.includes(file.type)) {
        setError('지원하지 않는 파일 형식입니다. PDF, DOC, DOCX, TXT 파일만 업로드 가능합니다.');
        return;
      }
      
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleAnalysis = async () => {
    if (!selectedFile) {
      setError('분석할 파일을 선택해주세요.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('document_type', documentType);

      const response = await fetch('http://localhost:8000/api/upload/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '파일 분석에 실패했습니다.');
      }

      const result = await response.json();
      
      // 분석 결과 처리
      const analysisData = result.analysis_result;
      
      const analysisResult = {
        documentType: documentType,
        fileName: result.filename,
        analysisDate: new Date().toLocaleString(),
        summary: `AI 상세 분석 완료 - 총점: ${analysisData.overall_summary.total_score}/10`,
        score: analysisData.overall_summary.total_score * 10, // 0-100 점수로 변환
        processingTime: result.processing_time || 0,
        extractedTextLength: result.extracted_text_length,
        detailedAnalysis: analysisData
      };

      setAnalysisResult(analysisResult);
      
    } catch (error) {
      console.error('이력서 분석 실패:', error);
      setError(`이력서 분석에 실패했습니다: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    const { detailedAnalysis } = analysisResult;
    const analysisKey = `${documentType}_analysis`;
    const analysisData = detailedAnalysis[analysisKey] || {};

    return (
      <div className="bg-white rounded-lg shadow-md p-6 mt-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
          <FiCheckCircle className="text-green-500 mr-2" />
          분석 결과
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 기본 정보 */}
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-700 mb-2">파일 정보</h4>
              <p className="text-sm text-gray-600">파일명: {analysisResult.fileName}</p>
              <p className="text-sm text-gray-600">분석 일시: {analysisResult.analysisDate}</p>
              <p className="text-sm text-gray-600">처리 시간: {analysisResult.processingTime.toFixed(2)}초</p>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-700 mb-2">종합 평가</h4>
              <div className="flex items-center">
                <div className="text-3xl font-bold text-blue-600 mr-3">
                  {analysisResult.score}
                </div>
                <div className="text-sm text-blue-600">/ 100점</div>
              </div>
              <p className="text-sm text-blue-600 mt-1">
                {detailedAnalysis.overall_summary?.recommendation || '권장사항이 없습니다.'}
              </p>
            </div>
          </div>

          {/* 상세 분석 */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-700">상세 분석</h4>
            <div className="space-y-3">
              {Object.entries(analysisData).map(([key, value]) => (
                <div key={key} className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {key.replace(/_/g, ' ')}
                    </span>
                    <span className="text-sm font-bold text-gray-800">
                      {value.score}/10
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">{value.feedback}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">이력서 분석</h1>
          <p className="text-gray-600">AI가 이력서를 분석하여 종합적인 평가를 제공합니다</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          {/* 문서 타입 선택 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              문서 타입
            </label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="resume">이력서</option>
              <option value="cover_letter">자기소개서</option>
              <option value="portfolio">포트폴리오</option>
            </select>
          </div>

          {/* 파일 업로드 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              파일 선택
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileSelect}
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <FiUpload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <div className="text-gray-600">
                  <span className="font-medium text-blue-600 hover:text-blue-500">
                    파일을 클릭하여 업로드
                  </span>
                  <p className="text-sm text-gray-500 mt-1">
                    PDF, DOC, DOCX, TXT 파일 (최대 10MB)
                  </p>
                </div>
              </label>
            </div>
            
            {selectedFile && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center">
                  <FiFileText className="text-blue-500 mr-2" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-blue-900">{selectedFile.name}</p>
                    <p className="text-xs text-blue-700">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 분석 버튼 */}
          <div className="text-center">
            <button
              onClick={handleAnalysis}
              disabled={!selectedFile || isAnalyzing}
              className={`px-6 py-3 rounded-lg font-medium text-white ${
                !selectedFile || isAnalyzing
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isAnalyzing ? (
                <div className="flex items-center">
                  <FiClock className="animate-spin mr-2" />
                  분석 중...
                </div>
              ) : (
                <div className="flex items-center">
                  <FiStar className="mr-2" />
                  분석 시작
                </div>
              )}
            </button>
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {/* 분석 결과 */}
          {renderAnalysisResult()}
        </div>
      </div>
    </div>
  );
};

export default ResumeAnalysis;
