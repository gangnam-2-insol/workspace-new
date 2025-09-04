import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiMessageCircle,
  FiX,
  FiSend,
  FiMinimize2,
  FiMaximize2,
  FiTrash2,
  FiRefreshCw,
  FiHelpCircle,
  FiArrowRight,
  FiExternalLink,
  FiMessageSquare
} from 'react-icons/fi';
import pickChatbotApi from '../services/pickChatbotApi';
import dynamicMessageService from '../services/dynamicMessageService';

// 리액트 에이전트 관련 import
import agentApiService from '../services/agentApiService';
import {
  AgentState,
  MessageType,
  analyzeAgentResponse,
  getNextActionsByState,
  formatAgentResponse,
  createAgentSession,
  transitionAgentState,
  monitorAgentPerformance
} from '../utils/agentUtils';
import AgentMessage from './AgentComponents/AgentMessage';
import AgentQuickActions from './AgentComponents/AgentQuickActions';
import AgentSuggestions from './AgentComponents/AgentSuggestions';
import AgentLoadingDots from './AgentComponents/AgentLoadingDots';

const ChatbotContainer = styled(motion.div)`
  position: fixed;
  bottom: 0px;
  height: 100%;
  right: 25px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
`;

// 배경 오버레이 제거됨 - 픽톡 활성화 시에도 다른 페이지 조작 가능하도록

const ChatWindow = styled(motion.div)`
  width: 400px;
  height: 100%;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 15px;

  @media (max-width: 480px) {
    width: 350px;
    height: 500px;
  }
`;

const ChatHeader = styled.div`
  background: linear-gradient(135deg, #2dd4bf 0%, #38bdf8 60%, #60a5fa 100%);
  color: #ffffff;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
`;

const HeaderInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const AgentIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
`;

const HeaderText = styled.div`
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }
  p {
    margin: 0;
    font-size: 12px;
    opacity: 0.8;
  }
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const IconButton = styled.button`
  background: none;
  border: none;
  color: #ffffff;
  padding: 6px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.22);
  }
`;

const ChatBody = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MessageContainer = styled.div`
  display: flex;
  justify-content: ${props => props.$isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: 8px;
`;

const Message = styled(motion.div)`
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;
  white-space: pre-wrap;
  overflow-wrap: anywhere;

  ${props => props.$isUser ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 4px;
  ` : `
    background: #f8f9fa;
    color: #333;
    border-bottom-left-radius: 4px;
  `}
`;



const SuggestionsContainer = styled.div`
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const SuggestionButton = styled.button`
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  color: #0ea5e9;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;

  &:hover {
    background: #0ea5e9;
    color: white;
  }
`;

const QuickActionsContainer = styled.div`
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const QuickActionButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
`;

const ChatInput = styled.div`
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #eee;
  border-radius: 25px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;

  &:focus {
    border-color: #667eea;
  }
`;

const SendButton = styled.button`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: visible;
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

// 기존 로딩 컴포넌트 - AgentLoadingDots로 대체됨
// const LoadingDots = styled.div`
//   display: flex;
//   gap: 4px;
//   padding: 12px 16px;
//   background: #f8f9fa;
//   border-radius: 18px;
//   border-bottom-left-radius: 4px;
//   width: fit-content;
// `;

// const Dot = styled(motion.div)`
//   width: 8px;
//   height: 8px;
//   border-radius: 50%;
//   background: #667eea;
// `;

const FloatingButton = styled(motion.button)`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2dd4bf 0%, #38bdf8 60%, #60a5fa 100%);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
  }
`;

const NewPickChatbot = ({ isOpen, onOpenChange }) => {
  // 리액트 에이전트 상태 추가
  const [agentSession, setAgentSession] = useState(null);
  const [currentAgentState, setCurrentAgentState] = useState(AgentState.INITIAL);
  const [isAgentMode, setIsAgentMode] = useState(false);

  // sessionStorage에서 상태 복원
  const getInitialMessages = async () => {
    const savedMessages = sessionStorage.getItem('pickChatbotMessages');
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages);
        // timestamp를 Date 객체로 변환
        return parsed.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
      } catch (e) {
        console.log('저장된 메시지 파싱 실패, 기본 메시지 사용');
      }
    }

    // 동적 메시지 생성
    try {
      const context = dynamicMessageService.createUserContext();
      const dynamicMessage = await dynamicMessageService.generateContextualMessage(context);

      return [
        {
          id: 1,
          text: dynamicMessage.message,
          isUser: false,
          timestamp: new Date(),
          quickActions: [
            { title: "채용공고 등록", action: "navigate", target: "/job-posting", icon: "📝" },
            { title: "지원자 관리", action: "navigate", target: "/applicants", icon: "👥" },
            { title: "채용공고 조회", action: "chat", message: "채용공고 목록을 보여주세요", icon: "📋" },
            { title: "지원자 통계", action: "chat", message: "지원자 통계를 보여주세요", icon: "📊" },
            { title: "메일 발송", action: "chat", message: "메일 템플릿을 보여주세요", icon: "📧" },
            // 리액트 에이전트 모드 추가
            { title: "🤖 AI 에이전트 모드", action: "agent_mode", target: "agent", icon: "🤖" }
          ]
        }
      ];
    } catch (error) {
      console.error('동적 메시지 생성 실패:', error);
      // 기본 메시지 반환
      return [
        {
          id: 1,
          text: "안녕하세요! AI 채용 관리 시스템의 픽톡입니다. 무엇을 도와드릴까요?",
          isUser: false,
          timestamp: new Date(),
          quickActions: [
            { title: "채용공고 등록", action: "navigate", target: "/job-posting", icon: "📝" },
            { title: "지원자 관리", action: "navigate", target: "/applicants", icon: "👥" },
            { title: "채용공고 조회", action: "chat", message: "채용공고 목록을 보여주세요", icon: "📋" },
            { title: "지원자 통계", action: "chat", message: "지원자 통계를 보여주세요", icon: "📊" },
            { title: "메일 발송", action: "chat", message: "메일 템플릿을 보여주세요", icon: "📧" },
            // 리액트 에이전트 모드 추가
            { title: "🤖 AI 에이전트 모드", action: "agent_mode", target: "agent", icon: "🤖" }
          ]
        }
      ];
    }
  };

  const [messages, setMessages] = useState([]);

  // 초기 메시지 로드
  useEffect(() => {
    const loadInitialMessages = async () => {
      const initialMessages = await getInitialMessages();
      setMessages(initialMessages);
    };
    loadInitialMessages();
  }, []);
  const [inputValue, setInputValue] = useState(sessionStorage.getItem('pickChatbotInput') || '');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // 입력폼 포커스 함수
  const focusInput = () => {
    inputRef.current?.focus();
  };

  // sessionStorage에 상태 저장
  useEffect(() => {
    sessionStorage.setItem('pickChatbotMessages', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    sessionStorage.setItem('pickChatbotInput', inputValue);
  }, [inputValue]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

    // 리액트 에이전트 모드 시작
  const startAgentMode = async () => {
    const startTime = Date.now();
    console.group('🤖 [AGENT MODE] 에이전트 모드 시작');
    console.log('⏰ 시작 시간:', new Date().toISOString());

    try {
      setIsLoading(true);
      const session = createAgentSession();
      setAgentSession(session);
      setCurrentAgentState(AgentState.INITIAL);
      setIsAgentMode(true);

      console.log('🔧 에이전트 세션 생성:', session);
      console.log('📊 초기 상태:', AgentState.INITIAL);

      // 에이전트 세션 시작
      const agentResponse = await agentApiService.startSession();

      const processingTime = Date.now() - startTime;
      console.log('⚡ 처리 시간:', `${processingTime}ms`);
      console.log('📥 LLM 응답:', agentResponse);

      if (agentResponse.success) {
        // LLM 피드백 디버깅 정보 업데이트
        setLlmDebugInfo(prev => ({
          ...prev,
          lastRequest: { type: 'start_session', timestamp: new Date() },
          lastResponse: agentResponse,
          processingTime: processingTime,
          confidence: agentResponse.confidence || 0,
          nextActions: agentResponse.quick_actions || []
        }));

        // 세션 ID 저장
        if (agentResponse.session_id) {
          setAgentSession(prev => ({
            ...prev,
            id: agentResponse.session_id
          }));
          console.log('🆔 세션 ID 할당:', agentResponse.session_id);
        }

        const agentMessage = {
          id: Date.now(),
          text: agentResponse.message + "\n\n" + agentResponse.next_action,
          isUser: false,
          timestamp: new Date(),
          isAgentMessage: true,
          agentState: agentResponse.state || AgentState.INITIAL,
          quickActions: agentResponse.quick_actions || getNextActionsByState(AgentState.INITIAL, {})
        };

        setMessages(prev => [...prev, agentMessage]);
        setCurrentAgentState(agentResponse.state || AgentState.INITIAL);

        console.log('✅ 에이전트 모드 시작 성공');
        console.log('🎯 현재 상태:', agentResponse.state || AgentState.INITIAL);
        console.log('💬 응답 메시지:', agentResponse.message);
        console.log('🔄 다음 액션:', agentResponse.next_action);
      } else {
        throw new Error(agentResponse.message || '에이전트 세션 시작에 실패했습니다.');
      }
    } catch (error) {
      console.error('❌ 에이전트 모드 시작 실패:', error);
      setIsAgentMode(false);

      const errorMessage = {
        id: Date.now(),
        text: "죄송합니다. 에이전트 모드 시작에 실패했습니다. 다시 시도해주세요.",
        isUser: false,
        timestamp: new Date(),
        isAgentMessage: true,
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      console.groupEnd();
    }
  };

    // 리액트 에이전트 입력 처리
  const handleAgentInput = async (userInput) => {
    try {
      setIsLoading(true);

      // 에이전트 입력 처리
      const agentResponse = await agentApiService.processInput(userInput, agentSession?.id);

      if (agentResponse.success) {
        // 상태 전환
        const newState = agentResponse.state || currentAgentState;
        setCurrentAgentState(newState);

        // 에이전트 응답 메시지 생성 (툴 실행 결과와 상세 정보 숨김)
        const agentMessage = {
          id: Date.now(),
          text: agentResponse.response,
          isUser: false,
          timestamp: new Date(),
          isAgentMessage: true,
          agentState: newState,
          quickActions: agentResponse.quick_actions || getNextActionsByState(newState, agentResponse),
          extractedData: agentResponse.extracted_fields || {},
          generatedContent: agentResponse.generated_content || null,
          autoNavigation: agentResponse.tool_result?.auto_navigation || null
        };

        setMessages(prev => [...prev, agentMessage]);

        // 세션 업데이트
        if (agentSession) {
          setAgentSession(prev => ({
            ...prev,
            state: newState,
            extractedData: { ...prev.extractedData, ...agentResponse.extracted_fields },
            messages: [...prev.messages, { user: userInput, agent: agentResponse.response }]
          }));
        }

        // 자동 네비게이션 처리 (픽톡 방식 그대로)
        if (agentResponse.tool_result?.auto_navigation?.enabled) {
          const autoNav = agentResponse.tool_result.auto_navigation;
          console.log('🚀 [자동 네비게이션] 시작:', autoNav);

          // 3초 후 자동 이동 (픽톡과 동일)
          setTimeout(() => {
            console.log('🚀 [자동 네비게이션] 페이지 이동 실행:', autoNav.target);

            // 페이지 이동
            window.handlePageAction(`changePage:${autoNav.target.replace('/', '')}`);

            // 픽톡 모달 직접 열기 (페이지 이동 후 지연시간을 두고 실행)
            if (autoNav.action === 'open_job_modal') {
              console.log('🚀 [픽톡 모달 직접 열기] 추출된 데이터:', autoNav.extracted_data);

              // 페이지 이동 후 1초 지연하여 openPickTalkModal 함수 등록 대기
              setTimeout(() => {
                if (window.openPickTalkModal) {
                  console.log('✅ [픽톡 모달] openPickTalkModal 함수 호출 성공');
                  window.openPickTalkModal(autoNav.extracted_data);
                } else {
                  console.error('❌ [픽톡 모달] openPickTalkModal 함수를 찾을 수 없습니다');
                  console.log('🔄 [재시도] 2초 후 다시 시도합니다...');

                  // 2초 후 재시도
                  setTimeout(() => {
                    if (window.openPickTalkModal) {
                      console.log('✅ [픽톡 모달] 재시도 성공 - openPickTalkModal 함수 호출');
                      window.openPickTalkModal(autoNav.extracted_data);
                    } else {
                      console.error('❌ [픽톡 모달] 최종 실패 - openPickTalkModal 함수를 찾을 수 없습니다');
                    }
                  }, 2000);
                }
              }, 1000); // 페이지 이동 후 1초 대기
            }
          }, autoNav.delay);
        }
      } else {
        throw new Error(agentResponse.message || '에이전트 응답 처리에 실패했습니다.');
      }

    } catch (error) {
      console.error('에이전트 입력 처리 실패:', error);

      const errorMessage = {
        id: Date.now(),
        text: "죄송합니다. 에이전트 처리 중 오류가 발생했습니다. 다시 시도해주세요.",
        isUser: false,
        timestamp: new Date(),
        isAgentMessage: true,
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };



  const handleSendMessage = async (messageText = null) => {
    const startTime = Date.now();
    const textToSend = messageText || inputValue.trim();
    if (!textToSend || isLoading) return;

    // 에이전트 모드인 경우 에이전트 처리
    if (isAgentMode) {
      const userMessage = {
        id: Date.now(),
        text: textToSend,
        isUser: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, userMessage]);
      setInputValue('');

      await handleAgentInput(textToSend);
      return;
    }

    console.group('🚀 [PICK-TALK FRONTEND] 메시지 전송 프로세스');
    console.log('📝 전송 메시지:', textToSend);

    const userMessage = {
      id: Date.now(),
      text: textToSend,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await pickChatbotApi.chat(textToSend);
      const responseTime = Date.now() - startTime;

      console.log('✅ API 응답 수신 완료');
      console.log('📊 [응답 분석]:', {
        응답시간: `${responseTime}ms`,
        응답길이: response.response?.length || 0,
        세션ID: response.session_id,
        신뢰도: response.confidence,
        툴사용: response.tool_results ? '있음' : '없음',
        페이지액션: response.page_action ? '있음' : '없음',
        제안개수: response.suggestions?.length || 0,
        빠른액션: response.quick_actions?.length || 0
      });

      // 응답 품질 분석
      if (responseTime > 5000) {
        console.warn('⚠️ [성능] 응답 시간이 5초를 초과했습니다:', responseTime + 'ms');
      }

      if (response.response && response.response.length < 10) {
        console.warn('⚠️ [품질] 응답이 너무 짧습니다:', response.response);
      }

      // 툴 결과 상세 분석
      if (response.tool_results) {
        console.log('🔧 [툴 결과 상세]:', {
          툴이름: response.tool_results.tool || 'N/A',
          액션: response.tool_results.action || 'N/A',
          성공여부: response.tool_results.result?.status || 'N/A',
          데이터크기: JSON.stringify(response.tool_results.result?.data || {}).length
        });
      }

      const botMessage = {
        id: Date.now() + 1,
        text: response.response,
        isUser: false,
        timestamp: new Date(),
        suggestions: response.suggestions || [],
        quickActions: response.quick_actions || [],
        pageAction: response.page_action || null
      };

      setMessages(prev => [...prev, botMessage]);

      // 페이지 액션이 있으면 자동 처리
      if (botMessage.pageAction) {
        console.log('🔍 [DEBUG] 페이지 액션 감지:', botMessage.pageAction);

        // 페이지 액션 상세 분석
        console.log('🎬 [페이지 액션 상세 분석]:', {
          액션타입: botMessage.pageAction.action,
          대상경로: botMessage.pageAction.path || botMessage.pageAction.target_url,
          메시지: botMessage.pageAction.message,
          자동입력데이터: botMessage.pageAction.auto_fill_data ? '있음' : '없음',
          자동액션: botMessage.pageAction.auto_action || 'N/A'
        });

        if (botMessage.pageAction.auto_fill_data) {
          console.log('📝 [자동 입력 데이터]:', botMessage.pageAction.auto_fill_data);
        }

        const handlePageAction = () => {
          if (botMessage.pageAction.action === 'navigate') {
            const pageAction = botMessage.pageAction;
            console.log('🎯 [페이지 네비게이션] 부드러운 이동 시작:', pageAction);

            // 현재 페이지가 이미 목적지 페이지인지 확인
            const currentPath = window.location.pathname;
            const targetPath = pageAction.path;

            if (currentPath === targetPath ||
                (targetPath === '/ai-job-registration' && currentPath === '/job-posting')) {
              console.log('🎯 [자동 입력] 현재 페이지에서 직접 자동 입력 실행');

              // 페이지 이동 없이 자동 입력 데이터만 적용
            if (pageAction.auto_fill_data) {
              sessionStorage.setItem('autoFillJobPostingData', JSON.stringify(pageAction.auto_fill_data));

                // 페이지에 자동 입력 이벤트 발생
                window.dispatchEvent(new CustomEvent('autoFillJobPosting', {
                  detail: pageAction.auto_fill_data
                }));
              }
              return;
            }

            if (pageAction.auto_fill_data) {
              sessionStorage.setItem('autoFillJobPostingData', JSON.stringify(pageAction.auto_fill_data));
            }
            sessionStorage.setItem('pickChatbotIsOpen', 'true');

              if (window.handlePageAction && pageAction.path) {
                window.handlePageAction(`changePage:${pageAction.path.replace('/', '')}`);
              } else if (pageAction.path) {
                window.location.href = pageAction.path;
            }
          } else if (botMessage.pageAction.action === 'openAIJobRegistration') {
            sessionStorage.setItem('pickChatbotIsOpen', 'true');
            if (botMessage.pageAction.auto_fill_data) {
              const autoFillParam = encodeURIComponent(JSON.stringify(botMessage.pageAction.auto_fill_data));
              window.location.href = `/job-posting?autoFill=${autoFillParam}`;
            } else {
              window.location.href = '/job-posting';
            }
          }
        };

        // 페이지 액션이 있으면 사용자에게 부드러운 안내
        if (botMessage.pageAction.message || botMessage.pageAction.action === 'navigate') {
          console.log('🎯 [페이지 이동] 조건 충족 - 자동 이동 시작');
          const actionMessage = botMessage.pageAction.message || "페이지로 이동합니다";
          const navigationMessage = {
            id: Date.now() + 2,
            text: `✨ ${actionMessage}\n\n🌟 **2초 후 자동으로 페이지 이동됩니다**`,
            isUser: false,
            timestamp: new Date(),
            isNavigationPrompt: true,
            pageAction: botMessage.pageAction,
            suggestions: [
              "🚀 지금 바로 이동하기"
            ],
            quickActions: [
              { title: "🚀 지금 이동", action: "navigate_smooth", target: botMessage.pageAction.path, icon: "🚀" }
            ]
          };

          setMessages(prev => [...prev, navigationMessage]);

          // 카운트다운 표시
          let countdown = 3;
          const countdownInterval = setInterval(() => {
            if (countdown > 0) {
              setMessages(prev => prev.map(msg =>
                msg.id === navigationMessage.id
                  ? { ...msg, text: `✨ ${actionMessage}\n\n🌟 **${countdown}초 후 자동으로 페이지 이동됩니다**` }
                  : msg
              ));
              countdown--;
            } else {
              clearInterval(countdownInterval);
              handlePageAction();
            }
          }, 1000);
        } else {
          setTimeout(handlePageAction, 2000);
        }
      }
    } catch (error) {
      const errorTime = Date.now() - startTime;

      console.error('❌ 에러 발생:', error);

      // 오류 상세 분석
      console.error('🚨 [오류 상세 분석]:', {
        오류타입: error.name || 'Unknown',
        오류메시지: error.message || '알 수 없는 오류',
        응답시간: `${errorTime}ms`,
        상태코드: error.status || 'N/A',
        네트워크오류: error.code === 'NETWORK_ERROR' ? '예' : '아니오',
        타임아웃: errorTime > 30000 ? '예' : '아니오'
      });

      // 스택 트레이스 출력 (개발 환경에서만)
      if (process.env.NODE_ENV === 'development') {
        console.error('📊 [스택 트레이스]:', error.stack);
      }

      // 오류 타입별 메시지 생성
      let errorText = '죄송합니다. 일시적인 오류가 발생했습니다.';

      if (errorTime > 30000) {
        errorText = '⏰ 요청 시간이 초과되었습니다. 네트워크 상태를 확인해주세요.';
      } else if (error.message && error.message.includes('fetch')) {
        errorText = '🌐 서버 연결에 실패했습니다. 백엔드 서버 상태를 확인해주세요.';
      } else if (error.status >= 500) {
        errorText = '🔧 서버 내부 오류가 발생했습니다. 관리자에게 문의해주세요.';
      } else if (error.status >= 400) {
        errorText = '📝 요청 형식에 문제가 있습니다. 다시 시도해주세요.';
      }

      const errorMessage = {
        id: Date.now() + 1,
        text: errorText,
        isUser: false,
        timestamp: new Date(),
        suggestions: ["다시 시도하기", "다른 질문하기"],
        quickActions: [],
        isError: true,
        errorDetails: {
          type: error.name,
          message: error.message,
          responseTime: errorTime,
          status: error.status
        }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      console.log(`⏱️ [처리 완료] 총 소요시간: ${Date.now() - startTime}ms`);
      console.groupEnd();
      setTimeout(() => {
        focusInput();
      }, 100);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    console.log('🎯 [SUGGESTION CLICK] 클릭된 제안:', suggestion);

    if (suggestion === "🚀 지금 바로 이동하기" || suggestion === "페이지로 이동하기") {
      console.log('✨ [부드러운 이동] 사용자가 즉시 이동 선택');
      const currentMessage = messages[messages.length - 1];
      if (currentMessage && currentMessage.isNavigationPrompt && currentMessage.pageAction) {
        const pageAction = currentMessage.pageAction;
        if (pageAction.action === 'navigate') {
          if (pageAction.auto_fill_data) {
            sessionStorage.setItem('autoFillJobPostingData', JSON.stringify(pageAction.auto_fill_data));
          }
          sessionStorage.setItem('pickChatbotIsOpen', 'true');

            if (window.handlePageAction && pageAction.path) {
              window.handlePageAction(`changePage:${pageAction.path.replace('/', '')}`);
            } else {
              window.location.href = pageAction.path;
            }
        } else if (pageAction.action === 'openAIJobRegistration') {
          sessionStorage.setItem('pickChatbotIsOpen', 'true');
          if (pageAction.auto_fill_data) {
            const autoFillParam = encodeURIComponent(JSON.stringify(pageAction.auto_fill_data));
            window.location.href = `/job-posting?autoFill=${autoFillParam}`;
          } else {
            window.location.href = '/job-posting';
          }
        }
        return;
      }
    }

    // 기존 제안 처리 로직
    handleSendMessage(suggestion);
  };

  const handleQuickActionClick = (action) => {
    // 에이전트 모드 액션 처리
    if (isAgentMode && action.action) {
      handleSendMessage(action.title);
      return;
    }

    if (action.action === 'navigate') {
      sessionStorage.setItem('pickChatbotIsOpen', 'true');
      window.location.href = action.target;
    } else if (action.action === 'external') {
      window.open(action.target, '_blank');
    } else if (action.action === 'openAIJobRegistration') {
      sessionStorage.setItem('pickChatbotIsOpen', 'true');
      if (action.auto_fill_data) {
        const autoFillParam = encodeURIComponent(JSON.stringify(action.auto_fill_data));
        window.location.href = `/job-posting?autoFill=${autoFillParam}`;
      } else {
        window.location.href = '/job-posting';
      }
    } else if (action.action === 'agent_mode') {
      // 에이전트 모드 시작
      startAgentMode();
      return;
    } else if (action.action === 'register_job_posting') {
      // 등록하기 버튼 클릭 시
      handleSendMessage('등록하기');
    } else if (action.action === 'cancel_job_posting') {
      // 취소 버튼 클릭 시
      handleSendMessage('취소할게요');
    } else if (action.action === 'chat') {
      // 채팅 메시지 전송
      if (action.message) {
        handleSendMessage(action.message);
      }
    }
  };

  // 텍스트 포맷팅 함수
  const formatResponseText = (text) => {
    if (!text) return text;

    const EMOJIS = ["📋", "💡", "🎯", "🔍", "📊", "🤝", "💼", "📝", "🚀", "💻"];
    const NUM_LIST_RE = /\b(\d+)\.\s+/g;
    const EMOJI_RE = new RegExp('(' + EMOJIS.map(emoji => emoji.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'g');

    let formattedText = text.trim();
    formattedText = formattedText.replace(/\*\*/g, '');
    formattedText = formattedText.replace(/([.!?。])\s+/g, '$1\n\n');
    formattedText = formattedText.replace(/• /g, '\n• ');
    formattedText = formattedText.replace(NUM_LIST_RE, '$1. ');
    formattedText = formattedText.replace(EMOJI_RE, '\n\n$1');
    formattedText = formattedText.replace(/\n{3,}/g, '\n\n');

    return formattedText;
  };

  // 강제 새로고침 감지 및 초기화
  useEffect(() => {
    const isHardRefresh = performance.navigation.type === 1 ||
                         (performance.getEntriesByType('navigation')[0] &&
                          performance.getEntriesByType('navigation')[0].type === 'reload');

    if (isHardRefresh) {
      console.log('🔍 강제 새로고침 감지됨 - 세션 초기화');
      sessionStorage.removeItem('pickChatbotMessages');
      sessionStorage.removeItem('pickChatbotInput');
      sessionStorage.removeItem('pickChatbotShouldReset');

      // 에이전트 모드도 초기화
      setIsAgentMode(false);
      setAgentSession(null);
      setCurrentAgentState(AgentState.INITIAL);

      const defaultMessage = {
        id: Date.now(),
        text: "안녕하세요! AI 채용 관리 시스템의 픽톡입니다. 무엇을 도와드릴까요?",
        isUser: false,
        timestamp: new Date(),
        quickActions: [
          { title: "채용공고 등록", action: "navigate", target: "/job-posting", icon: "📝" },
          { title: "지원자 관리", action: "navigate", target: "/applicants", icon: "👥" },
          { title: "🤖 AI 에이전트 모드", action: "agent_mode", target: "agent", icon: "🤖" }
        ]
      };
      setMessages([defaultMessage]);
      setInputValue('');
    }

    const handleBeforeUnload = () => {
      sessionStorage.setItem('pickChatbotShouldReset', 'true');
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  // 챗봇이 열릴 때 입력폼에 자동 포커스
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        focusInput();
      }, 300);
    }
  }, [isOpen]);

  const clearChat = () => {
    pickChatbotApi.resetSession();

    // 에이전트 모드 종료
    if (isAgentMode) {
      setIsAgentMode(false);
      setAgentSession(null);
      setCurrentAgentState(AgentState.INITIAL);

      // 에이전트 세션 종료
      if (agentSession?.id) {
        agentApiService.endSession(agentSession.id);
      }
    }

    const defaultMessage = {
      id: Date.now(),
      text: "안녕하세요! AI 채용 관리 시스템의 픽톡입니다. 무엇을 도와드릴까요?",
      isUser: false,
      timestamp: new Date(),
      quickActions: [
        { title: "채용공고 등록", action: "navigate", target: "/job-posting", icon: "📝" },
        { title: "지원자 관리", action: "navigate", target: "/applicants", icon: "👥" },
        { title: "🤖 AI 에이전트 모드", action: "agent_mode", target: "agent", icon: "🤖" }
      ]
    };
    setMessages([defaultMessage]);
    setInputValue('');
    sessionStorage.removeItem('pickChatbotMessages');
    sessionStorage.removeItem('pickChatbotInput');
  };

  // 배경 클릭 시 픽톡 닫기 기능 제거됨 - 픽톡 활성화 상태 유지

  // LLM 피드백 디버깅을 위한 상태 추가
  const [llmDebugInfo, setLlmDebugInfo] = useState({
    lastRequest: null,
    lastResponse: null,
    processingTime: 0,
    tokenUsage: null,
    confidence: 0,
    extractedData: {},
    suggestions: [],
    nextActions: []
  });
  const [showDebugPanel, setShowDebugPanel] = useState(false);

  return (
    <>
      {/* 플로팅 버튼 - 항상 표시 */}
      <FloatingButton
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        onClick={() => {
          onOpenChange(true);
          sessionStorage.setItem('pickChatbotIsOpen', 'true');
        }}
        title="픽톡 열기"
        style={{ display: isOpen === true ? 'none' : 'flex' }}
      >
        💬
      </FloatingButton>

      {/* 채팅창 상태 */}
      <AnimatePresence>
        {isOpen === true && (
          <>
            {/* 배경 오버레이 제거됨 - 픽톡 활성화 시에도 다른 페이지 조작 가능 */}
            <ChatbotContainer
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 20 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
            >
          <ChatWindow>
            <ChatHeader>
              <HeaderInfo>
                <AgentIcon>
                  💬
                </AgentIcon>
                <HeaderText>
                  <h3>픽톡</h3>
                  <p>{isAgentMode ? '🤖 AI 에이전트 모드' : 'AI 어시스턴트'}</p>
                  {isAgentMode && (
                    <small style={{ opacity: 0.8, fontSize: '10px' }}>
                      상태: {currentAgentState.replace('_', ' ')}
                    </small>
                  )}
                </HeaderText>
              </HeaderInfo>
              <HeaderActions>
                {/* 에이전트 모드 전환 버튼 */}
                <IconButton
                  onClick={() => {
                    if (isAgentMode) {
                      // 에이전트 모드 종료
                      setIsAgentMode(false);
                      setAgentSession(null);
                      setCurrentAgentState(AgentState.INITIAL);
                      if (agentSession?.id) {
                        agentApiService.endSession(agentSession.id);
                      }
                    } else {
                      // 에이전트 모드 시작
                      startAgentMode();
                    }
                  }}
                  title={isAgentMode ? "에이전트 모드 종료" : "에이전트 모드 시작"}
                  style={{
                    background: isAgentMode ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.18)',
                    border: isAgentMode ? '2px solid rgba(255, 255, 255, 0.5)' : 'none'
                  }}
                >
                  🤖
                </IconButton>
                <IconButton onClick={clearChat} title="대화 초기화">
                  <FiTrash2 size={16} />
                </IconButton>
                <IconButton onClick={() => {
                  onOpenChange('floating');
                  sessionStorage.setItem('pickChatbotIsOpen', 'floating');
                }} title="최소화">
                  <FiMinimize2 size={18} />
                </IconButton>
              </HeaderActions>
            </ChatHeader>

            <ChatBody>
              {messages.map((message) => (
                <div key={message.id}>
                  {/* 에이전트 메시지인 경우 AgentMessage 컴포넌트 사용 */}
                  {message.isAgentMessage ? (
                    <AgentMessage
                      message={message.text}
                      isUser={message.isUser}
                      timestamp={message.timestamp}
                    />
                  ) : (
                    <MessageContainer $isUser={message.isUser}>
                      <Message
                        $isUser={message.isUser}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        {message.isUser ? message.text : formatResponseText(message.text)}
                      </Message>
                    </MessageContainer>
                  )}



                  {/* 추천 질문 (최초 1회만 노출) */}
                  {!message.isUser && message.suggestions && message.suggestions.length > 0 && message.id === 1 && (
                    <SuggestionsContainer>
                      {message.suggestions.map((suggestion, index) => (
                        <SuggestionButton
                          key={index}
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion}
                        </SuggestionButton>
                      ))}
                    </SuggestionsContainer>
                  )}



                  {/* 에이전트 메시지의 경우 AgentQuickActions 컴포넌트 사용 */}
                  {message.isAgentMessage && message.quickActions && message.quickActions.length > 0 && (
                    <AgentQuickActions
                      actions={message.quickActions}
                      onActionClick={handleQuickActionClick}
                      disabled={isLoading}
                    />
                  )}
                </div>
              ))}

              {isLoading && (
                <MessageContainer $isUser={false}>
                  <AgentLoadingDots />
                </MessageContainer>
              )}
              <div ref={messagesEndRef} />
            </ChatBody>

            <ChatInput>
              <Input
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="메시지를 입력하세요..."
                disabled={isLoading}
              />
              <SendButton
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isLoading}
              >
                <FiSend size={18} />
              </SendButton>
            </ChatInput>
          </ChatWindow>
        </ChatbotContainer>
            </>
        )}
      </AnimatePresence>
    </>
  );
};

export default NewPickChatbot;
