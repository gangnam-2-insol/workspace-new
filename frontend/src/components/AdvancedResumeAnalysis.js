import React, { useState, useRef } from 'react';
import RadarChart from './RadarChart';
import './AdvancedResumeAnalysis.css';

const AdvancedResumeAnalysis = () => {
  const [formData, setFormData] = useState({
    applicantName: '',
    applicantEmail: '',
    jobPosition: '개발자',
    jobDescription: '',
    resumeFile: null,
    coverLetterFile: null
  });
  
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  
  const fileInputRef = useRef();
  const coverLetterInputRef = useRef();
  const resultRef = useRef();

  const jobPositions = [
    { value: '개발자', label: '개발자 (개발/프로그래밍)' },
    { value: '기획자', label: '기획자 (서비스/제품 기획)' },
    { value: '디자이너', label: '디자이너 (UI/UX/그래픽)' },
    { value: '마케터', label: '마케터 (마케팅/홍보)' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e, fileType) => {
    const file = e.target.files[0];
    if (file) {
      setFormData(prev => ({
        ...prev,
        [fileType]: file
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.applicantName || !formData.applicantEmail || !formData.resumeFile) {
      setError('필수 항목을 모두 입력해주세요.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('applicant_name', formData.applicantName);
      formDataToSend.append('applicant_email', formData.applicantEmail);
      formDataToSend.append('job_position', formData.jobPosition);
      formDataToSend.append('job_description', formData.jobDescription);
      formDataToSend.append('resume_file', formData.resumeFile);
      
      if (formData.coverLetterFile) {
        formDataToSend.append('cover_letter_file', formData.coverLetterFile);
      }

      const response = await fetch('http://localhost:8000/api/advanced-analysis/analyze-resume', {
        method: 'POST',
        body: formDataToSend,
      });

      if (!response.ok) {
        throw new Error(`분석 실패: ${response.status}`);
      }

      const result = await response.json();
      setAnalysisResult(result.data);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetForm = () => {
    setFormData({
      applicantName: '',
      applicantEmail: '',
      jobPosition: '개발자',
      jobDescription: '',
      resumeFile: null,
      coverLetterFile: null
    });
    setAnalysisResult(null);
    setError(null);
    
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (coverLetterInputRef.current) coverLetterInputRef.current.value = '';
  };

  const handleRadarChartClick = (sectionIndex) => {
    if (!resultRef.current) return;
    
    // 섹션별 스크롤 위치 계산
    const sections = [
      'job-fit-section',
      'tech-stack-section', 
      'project-relevance-section',
      'tech-competency-section',
      'experience-impact-section',
      'problem-solving-section',
      'collaboration-section',
      'growth-potential-section',
      'clarity-grammar-section'
    ];
    
    const targetSection = sections[sectionIndex];
    const element = document.getElementById(targetSection);
    
    if (element) {
      element.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
      });
      
      // 클릭된 섹션 하이라이트 효과
      element.style.backgroundColor = 'rgba(54, 162, 235, 0.1)';
      element.style.border = '2px solid rgba(54, 162, 235, 0.5)';
      
      setTimeout(() => {
        element.style.backgroundColor = '';
        element.style.border = '';
      }, 2000);
    }
  };

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    const { stage1, stage2, final_score, analysis_timestamp } = analysisResult;
    const summary = analysisResult;

    return (
      <div className="analysis-result" ref={resultRef}>
        <h3>📊 분석 결과</h3>
        
        {/* 레이더 차트 추가 */}
        <RadarChart 
          analysisData={analysisResult} 
          onSectionClick={handleRadarChartClick}
        />
        
        {/* 최종 점수 */}
        <div className="final-score">
          <h4>🏆 최종 종합 점수</h4>
          <div className="score-display">
            <span className="score-number">{final_score?.toFixed(1) || 'N/A'}</span>
            <span className="score-label">점</span>
          </div>
        </div>

        {/* 1단계: Hugging Face 분석 결과 */}
        <div className="stage-results">
          <h4>🤖 1단계: Hugging Face 기계적 평가</h4>
          
          <div id="job-fit-section" className="evaluation-section">
            <h5>🎯 직무 적합성 (Job Fit)</h5>
            <div className="evaluation">
              <label>직무 적합성 점수</label>
              <p>{stage1?.job_fit_score?.toFixed(1) || 'N/A'}점</p>
            </div>
          </div>

          <div id="tech-stack-section" className="evaluation-section">
            <h5>🔧 기술 스택 일치 여부</h5>
            <div className="evaluation">
              <label>기술 스택 점수</label>
              <p>{stage1?.skill_scores ? Object.values(stage1.skill_scores).reduce((a, b) => a + b, 0) / Object.keys(stage1.skill_scores).length : 'N/A'}점</p>
            </div>
          </div>

          <div id="project-relevance-section" className="evaluation-section">
            <h5>📋 경험한 프로젝트 관련성</h5>
            <div className="evaluation">
              <label>프로젝트 관련성</label>
              <p>{stage1?.job_fit_score?.toFixed(1) || 'N/A'}점</p>
            </div>
          </div>

          <div id="tech-competency-section" className="evaluation-section">
            <h5>⚡ 핵심 기술 역량 (Tech Competency)</h5>
            <div className="evaluation">
              <label>기술 역량 점수</label>
              <p>{stage1?.skill_scores ? Object.values(stage1.skill_scores).reduce((a, b) => a + b, 0) / Object.keys(stage1.skill_scores).length : 'N/A'}점</p>
            </div>
            {stage1?.skill_scores && (
              <div className="skill-breakdown">
                <h6>세부 스킬 점수:</h6>
                <div className="skill-grid">
                  {Object.entries(stage1.skill_scores).map(([skill, score]) => (
                    <div key={skill} className="skill-item">
                      <span className="skill-name">{skill}</span>
                      <span className="skill-score">{score.toFixed(1)}점</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div id="experience-impact-section" className="evaluation-section">
            <h5>💼 경력 및 성과 (Experience & Impact)</h5>
            <div className="evaluation">
              <label>경력 성과 점수</label>
              <p>{stage1?.text_quality_score?.toFixed(1) || 'N/A'}점</p>
            </div>
          </div>

          <div id="problem-solving-section" className="evaluation-section">
            <h5>🔍 문제 해결 능력 (Problem-Solving)</h5>
            <div className="evaluation">
              <label>문제 해결 점수</label>
              <p>{stage1?.text_quality_score?.toFixed(1) || 'N/A'}점</p>
            </div>
          </div>

          <div id="collaboration-section" className="evaluation-section">
            <h5>🤝 커뮤니케이션/협업 (Collaboration)</h5>
            <div className="evaluation">
              <label>협업 능력 점수</label>
              <p>{stage1?.text_quality_score?.toFixed(1) || 'N/A'}점</p>
            </div>
          </div>

          <div id="growth-potential-section" className="evaluation-section">
            <h5>📈 성장 가능성/학습 능력 (Growth Potential)</h5>
            <div className="evaluation">
              <label>성장 가능성 점수</label>
              <p>{stage1?.text_quality_score?.toFixed(1) || 'N/A'}점</p>
            </div>
          </div>

          <div id="clarity-grammar-section" className="evaluation-section">
            <h5>✍️ 자소서 표현력/논리성 (Clarity & Grammar)</h5>
            <div className="evaluation">
              <label>문법 점수</label>
              <p>{stage1?.grammar_score?.toFixed(1) || 'N/A'}점</p>
            </div>
            <div className="evaluation">
              <label>텍스트 품질 점수</label>
              <p>{stage1?.text_quality_score?.toFixed(1) || 'N/A'}점</p>
            </div>
          </div>

          {stage1?.summary && (
            <div className="evaluation">
              <label>AI 생성 요약</label>
              <p>{stage1.summary}</p>
            </div>
          )}
        </div>

        {/* 2단계: GPT-4o 분석 결과 */}
        {stage2 && (
          <div className="stage-results">
            <h4>🧠 2단계: GPT-4o 종합 평가</h4>
            
            <div className="evaluation">
              <label>직무 적합성</label>
              <p>{stage2.직무_적합성}점</p>
            </div>
            <div className="evaluation">
              <label>핵심 기술 역량</label>
              <p>{stage2.핵심_기술_역량}점</p>
            </div>
            <div className="evaluation">
              <label>경력 및 성과</label>
              <p>{stage2.경력_및_성과}점</p>
            </div>
            <div className="evaluation">
              <label>문제 해결 능력</label>
              <p>{stage2.문제_해결_능력}점</p>
            </div>
            <div className="evaluation">
              <label>협업/커뮤니케이션</label>
              <p>{stage2.협업}점</p>
            </div>
            <div className="evaluation">
              <label>성장 가능성</label>
              <p>{stage2.성장_가능성}점</p>
            </div>
            <div className="evaluation">
              <label>표현력/문법</label>
              <p>{stage2.표현력}점</p>
            </div>
            {stage2.종합_평가 && (
              <div className="evaluation">
                <label>종합 평가</label>
                <p>{stage2.종합_평가}</p>
              </div>
            )}
          </div>
        )}

        {/* 분석 시간 */}
        <div className="analysis-timestamp">
          <p>분석 완료 시간: {summary.analysis_timestamp}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="advanced-resume-analysis">
      <div className="container">
        <h2>🚀 고급 이력서 분석 시스템</h2>
        <p className="subtitle">
          2단계 분석: Hugging Face (빠른 기계적 평가) + GPT-4o (사람다운 종합 평가)
        </p>

        {/* 분석 폼 */}
        <form onSubmit={handleSubmit} className="analysis-form">
          <div className="form-section">
            <h3>👤 지원자 정보</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="applicantName">이름 *</label>
                <input
                  type="text"
                  id="applicantName"
                  name="applicantName"
                  value={formData.applicantName}
                  onChange={handleInputChange}
                  placeholder="지원자 이름을 입력하세요"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="applicantEmail">이메일 *</label>
                <input
                  type="email"
                  id="applicantEmail"
                  name="applicantEmail"
                  value={formData.applicantEmail}
                  onChange={handleInputChange}
                  placeholder="이메일을 입력하세요"
                  required
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>💼 직무 정보</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="jobPosition">지원 직무 *</label>
                <select
                  id="jobPosition"
                  name="jobPosition"
                  value={formData.jobPosition}
                  onChange={handleInputChange}
                >
                  {jobPositions.map(pos => (
                    <option key={pos.value} value={pos.value}>
                      {pos.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="jobDescription">직무 설명 (선택사항)</label>
              <textarea
                id="jobDescription"
                name="jobDescription"
                value={formData.jobDescription}
                onChange={handleInputChange}
                placeholder="지원 직무에 대한 상세 설명을 입력하세요. 직무 적합성 분석에 활용됩니다."
                rows="4"
              />
            </div>
          </div>

          <div className="form-section">
            <h3>📄 문서 업로드</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="resumeFile">이력서 *</label>
                <input
                  type="file"
                  id="resumeFile"
                  ref={fileInputRef}
                  onChange={(e) => handleFileChange(e, 'resumeFile')}
                  accept=".pdf,.docx,.doc,.txt"
                  required
                />
                <small>지원 형식: PDF, DOCX, DOC, TXT</small>
              </div>
              <div className="form-group">
                <label htmlFor="coverLetterFile">자기소개서 (선택사항)</label>
                <input
                  type="file"
                  id="coverLetterFile"
                  ref={coverLetterInputRef}
                  onChange={(e) => handleFileChange(e, 'coverLetterFile')}
                  accept=".pdf,.docx,.doc,.txt"
                />
                <small>지원 형식: PDF, DOCX, DOC, TXT</small>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="btn-analyze"
              disabled={isAnalyzing}
            >
              {isAnalyzing ? '🔍 분석 중...' : '🚀 분석 시작'}
            </button>
            <button
              type="button"
              className="btn-reset"
              onClick={resetForm}
            >
              🔄 초기화
            </button>
          </div>
        </form>

        {/* 에러 메시지 */}
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {/* 분석 결과 */}
        {renderAnalysisResult()}
      </div>
    </div>
  );
};

export default AdvancedResumeAnalysis;
