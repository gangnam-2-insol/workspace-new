import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './JobPostingAgent.css';

const JobPostingAgent = () => {
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [currentState, setCurrentState] = useState('initial');
    const [extractedKeywords, setExtractedKeywords] = useState([]);
    const [recommendedTemplates, setRecommendedTemplates] = useState([]);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    const [generatedContent, setGeneratedContent] = useState(null);
    const [finalContent, setFinalContent] = useState(null);
    const [jobPostingId, setJobPostingId] = useState(null);

    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // 스크롤을 맨 아래로
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // 세션 시작
    const startSession = async () => {
        try {
            setIsLoading(true);
            const response = await axios.post('/api/job-posting-agent/start-session', {
                user_id: 'user_123', // 실제로는 로그인된 사용자 ID
                company_info: {
                    name: '테스트 회사',
                    location: '서울'
                }
            });

            setSessionId(response.data.session_id);
            addMessage('agent', response.data.message);
            addMessage('agent', response.data.next_action);
            setCurrentState('initial');
        } catch (error) {
            console.error('세션 시작 실패:', error);
            addMessage('error', '세션 시작에 실패했습니다.');
        } finally {
            setIsLoading(false);
        }
    };

    // 사용자 입력 처리
    const processUserInput = async (input) => {
        if (!sessionId || !input.trim()) return;

        try {
            setIsLoading(true);
            addMessage('user', input);

            const response = await axios.post('/api/job-posting-agent/process-input', {
                session_id: sessionId,
                user_input: input
            });

            const data = response.data;
            setCurrentState(data.state);

            // 에이전트 응답 추가
            addMessage('agent', data.message);
            if (data.next_action) {
                addMessage('agent', data.next_action);
            }

            // 상태별 데이터 업데이트
            if (data.extracted_keywords) {
                setExtractedKeywords(data.extracted_keywords);
            }
            if (data.recommended_templates) {
                setRecommendedTemplates(data.recommended_templates);
            }
            if (data.selected_template) {
                setSelectedTemplate(data.selected_template);
            }
            if (data.generated_content) {
                setGeneratedContent(data.generated_content);
            }
            if (data.final_content) {
                setFinalContent(data.final_content);
            }
            if (data.job_posting_id) {
                setJobPostingId(data.job_posting_id);
            }

        } catch (error) {
            console.error('입력 처리 실패:', error);
            addMessage('error', '입력 처리에 실패했습니다.');
        } finally {
            setIsLoading(false);
            setUserInput('');
        }
    };

    // 메시지 추가
    const addMessage = (type, content) => {
        const newMessage = {
            id: Date.now(),
            type,
            content,
            timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, newMessage]);
    };

    // 입력 제출
    const handleSubmit = (e) => {
        e.preventDefault();
        if (userInput.trim() && !isLoading) {
            processUserInput(userInput);
        }
    };

    // 템플릿 선택
    const selectTemplate = (template) => {
        setSelectedTemplate(template);
        processUserInput(`템플릿 선택: ${template.name}`);
    };

    // 새 템플릿 생성
    const generateNewTemplate = () => {
        processUserInput('새로운 템플릿을 생성해주세요');
    };

    // 공고 내용 수정
    const modifyContent = (field, value) => {
        if (generatedContent) {
            const updatedContent = { ...generatedContent };
            if (field === 'title') {
                updatedContent.title = value;
            } else if (field === 'description') {
                updatedContent.description = value;
            } else if (field === 'requirements') {
                updatedContent.requirements = value.split('\n').filter(item => item.trim());
            } else if (field === 'preferred') {
                updatedContent.preferred = value.split('\n').filter(item => item.trim());
            }
            setGeneratedContent(updatedContent);
        }
    };

    // 공고 등록
    const registerJobPosting = () => {
        processUserInput('등록');
    };

    // 새 공고 시작
    const startNewJobPosting = () => {
        setSessionId(null);
        setMessages([]);
        setUserInput('');
        setCurrentState('initial');
        setExtractedKeywords([]);
        setRecommendedTemplates([]);
        setSelectedTemplate(null);
        setGeneratedContent(null);
        setFinalContent(null);
        setJobPostingId(null);
        startSession();
    };

    return (
        <div className="job-posting-agent">
            <div className="agent-header">
                <h2>🤖 채용공고 에이전트</h2>
                <p>AI가 도와주는 스마트한 채용공고 작성</p>
            </div>

            <div className="agent-container">
                {/* 채팅 영역 */}
                <div className="chat-area">
                    <div className="messages">
                        {messages.length === 0 ? (
                            <div className="welcome-message">
                                <h3>채용공고 작성을 시작해보세요!</h3>
                                <p>원하는 직무나 기술 스택을 알려주시면 AI가 최적의 공고를 만들어드립니다.</p>
                                <button
                                    className="start-button"
                                    onClick={startSession}
                                    disabled={isLoading}
                                >
                                    {isLoading ? '시작 중...' : '채용공고 작성 시작'}
                                </button>
                            </div>
                        ) : (
                            messages.map((message) => (
                                <div key={message.id} className={`message ${message.type}`}>
                                    <div className="message-content">
                                        {message.type === 'agent' && <span className="agent-icon">🤖</span>}
                                        {message.type === 'user' && <span className="user-icon">👤</span>}
                                        {message.type === 'error' && <span className="error-icon">⚠️</span>}
                                        <span className="message-text">{message.content}</span>
                                    </div>
                                    <div className="message-time">{message.timestamp}</div>
                                </div>
                            ))
                        )}
                        {isLoading && (
                            <div className="message agent">
                                <div className="message-content">
                                    <span className="agent-icon">🤖</span>
                                    <span className="message-text">
                                        <div className="loading-dots">
                                            <span></span>
                                            <span></span>
                                            <span></span>
                                        </div>
                                    </span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* 입력 영역 */}
                    <form onSubmit={handleSubmit} className="input-area">
                        <input
                            ref={inputRef}
                            type="text"
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            placeholder="메시지를 입력하세요..."
                            disabled={isLoading || !sessionId}
                            className="message-input"
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !userInput.trim() || !sessionId}
                            className="send-button"
                        >
                            전송
                        </button>
                    </form>
                </div>

                {/* 사이드바 - 상태별 정보 표시 */}
                <div className="sidebar">
                    {/* 키워드 표시 */}
                    {extractedKeywords.length > 0 && (
                        <div className="sidebar-section">
                            <h4>🔍 추출된 키워드</h4>
                            <div className="keywords">
                                {extractedKeywords.map((keyword, index) => (
                                    <span key={index} className="keyword-tag">{keyword}</span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* 추천 템플릿 */}
                    {recommendedTemplates.length > 0 && (
                        <div className="sidebar-section">
                            <h4>📋 추천 템플릿</h4>
                            <div className="templates">
                                {recommendedTemplates.map((template, index) => (
                                    <div key={index} className="template-card">
                                        <h5>{template.name}</h5>
                                        <p className="template-source">{template.source}</p>
                                        <div className="template-stats">
                                            <span>사용: {template.metadata.usage_count}</span>
                                            <span>성공률: {Math.round(template.metadata.success_rate * 100)}%</span>
                                        </div>
                                        <button
                                            onClick={() => selectTemplate(template)}
                                            className="select-template-btn"
                                        >
                                            선택
                                        </button>
                                    </div>
                                ))}
                                <button
                                    onClick={generateNewTemplate}
                                    className="generate-template-btn"
                                >
                                    🆕 새 템플릿 생성
                                </button>
                            </div>
                        </div>
                    )}

                    {/* 생성된 공고 내용 */}
                    {generatedContent && (
                        <div className="sidebar-section">
                            <h4>📝 생성된 공고</h4>
                            <div className="generated-content">
                                <div className="content-field">
                                    <label>제목</label>
                                    <input
                                        type="text"
                                        value={generatedContent.title}
                                        onChange={(e) => modifyContent('title', e.target.value)}
                                        className="content-input"
                                    />
                                </div>
                                <div className="content-field">
                                    <label>설명</label>
                                    <textarea
                                        value={generatedContent.description}
                                        onChange={(e) => modifyContent('description', e.target.value)}
                                        className="content-textarea"
                                        rows="3"
                                    />
                                </div>
                                <div className="content-field">
                                    <label>자격 요건</label>
                                    <textarea
                                        value={generatedContent.requirements.join('\n')}
                                        onChange={(e) => modifyContent('requirements', e.target.value)}
                                        className="content-textarea"
                                        rows="3"
                                    />
                                </div>
                                <div className="content-field">
                                    <label>우대 사항</label>
                                    <textarea
                                        value={generatedContent.preferred.join('\n')}
                                        onChange={(e) => modifyContent('preferred', e.target.value)}
                                        className="content-textarea"
                                        rows="3"
                                    />
                                </div>
                                <div className="content-actions">
                                    <button
                                        onClick={() => processUserInput('수정')}
                                        className="modify-btn"
                                    >
                                        수정 완료
                                    </button>
                                    <button
                                        onClick={() => processUserInput('확인')}
                                        className="confirm-btn"
                                    >
                                        확인
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 최종 확인 */}
                    {finalContent && (
                        <div className="sidebar-section">
                            <h4>✅ 최종 확인</h4>
                            <div className="final-content">
                                <h5>{finalContent.title}</h5>
                                <p>{finalContent.description}</p>
                                <div className="final-actions">
                                    <button
                                        onClick={registerJobPosting}
                                        className="register-btn"
                                    >
                                        공고 등록
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 등록 완료 */}
                    {jobPostingId && (
                        <div className="sidebar-section">
                            <h4>🎉 등록 완료!</h4>
                            <div className="completion-message">
                                <p>공고가 성공적으로 등록되었습니다.</p>
                                <p>ID: {jobPostingId}</p>
                                <button
                                    onClick={startNewJobPosting}
                                    className="new-job-btn"
                                >
                                    새 공고 작성
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default JobPostingAgent;
