import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminToolsManager from './AdminToolsManager';
import { ensureUiIndexIfNeeded, resolveByQuery } from '../utils/uiIndex';
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
  FiTool,
  FiCpu
} from 'react-icons/fi';

const ChatbotContainer = styled(motion.div)`
  position: fixed;
  bottom: 80px;
  right: 25px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
`;

const ChatButton = styled(motion.button)`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 3px 14px rgba(102, 126, 234, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-size: 130% 130%;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-position 0.2s ease;

  &:before {
    content: '';
    position: absolute;
    inset: -6px;
    border-radius: 50%;
    background: radial-gradient(closest-side, rgba(118, 75, 162, 0.25), rgba(118, 75, 162, 0));
    opacity: 0;
    transition: opacity 0.2s ease;
    pointer-events: none;
  }

  &:hover {
    transform: scale(1.05) translateY(-1px);
    box-shadow: 0 6px 22px rgba(102, 126, 234, 0.5);
    background-position: 80% 20%;
    filter: invert(1);
  }

  &:hover:before {
    opacity: 0.7;
  }

  &:focus-visible {
    outline: none;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3), 0 6px 22px rgba(102, 126, 234, 0.5);
  }
`;

const ChatWindow = styled(motion.div)`
  width: 400px;
  height: 600px;
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
  white-space: pre-wrap; /* 줄바꿈 문자 보존 */
  overflow-wrap: anywhere; /* 긴 단어 줄바꿈 */
  
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

const ToolIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #667eea;
  margin-top: 4px;
  padding: 4px 8px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  width: fit-content;
`;

const ChatInput = styled.div`
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const MinimizedContent = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 22px;
  color: #333;
  transition: background 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.04);
    transform: scale(1.04);
    filter: invert(1);
  }
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

  .lgc-send-base { width: 100%; display: flex; align-items: center; justify-content: center; }
  .lgc-send-fly { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); pointer-events: none; }
  .lgc-send-trail { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); border-radius: 50%; background: rgba(255,255,255,0.9); pointer-events: none; }
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 18px;
  border-bottom-left-radius: 4px;
  width: fit-content;
`;

const Dot = styled(motion.div)`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
`;

const SHOW_PURPLE_TRIGGER_BUTTON = false; // 보라색 플로팅 트리거 버튼 숨김

const LangGraphChatbot = ({ isOpen: isOpenProp, onOpenChange }) => {
  const [isOpenInternal, setIsOpenInternal] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [agentStatus, setAgentStatus] = useState('idle');
  const [isAdminMode, setIsAdminMode] = useState(false);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [isSendAnimating, setIsSendAnimating] = useState(false);
  const wsRef = useRef(null);
	const navigate = useNavigate();
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // 제어/비제어 겸용: 외부 isOpen이 boolean이면 제어 모드로 동작
  const isControlled = typeof isOpenProp === 'boolean';
  const isOpen = isControlled ? isOpenProp : isOpenInternal;

  // 스크롤을 맨 아래로 이동
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 에이전트 상태 확인
  useEffect(() => {
    checkAgentHealth();
  }, []);

  // 자동 오픈 제거: 페이지 로드시 챗봇이 자동으로 열리지 않도록 함

  // WebSocket 연결 (있으면 사용, 실패하면 무시하고 REST로 폴백)
  // WebSocket 완전 제거: REST만 사용

	// 메시지가 추가될 때마다 입력창에 포커스
	useEffect(() => {
		if (isOpen && !isMinimized) {
			setTimeout(() => {
				inputRef.current?.focus();
			}, 0);
		}
	}, [messages, isOpen, isMinimized]);

  const checkAgentHealth = async () => {
    try {
      const response = await fetch('/api/langgraph-agent/health');
      const data = await response.json();
      setAgentStatus(data.status);
    } catch (error) {
      console.error('에이전트 상태 확인 실패:', error);
      setAgentStatus('error');
    }
  };

  // 간단한 네비게이션 의도 감지 및 경로 매핑
  const resolveNavigationPath = (text) => {
    const lower = String(text || '').toLowerCase();

    const moveVerbs = [
      '이동', '넘어가', '넘어 가', '가 ', '가자', '열어', '열기', '열어줘', '보여', '페이지', '메뉴',
      'move', 'go', 'open', 'navigate'
    ];

    const hasMoveVerb = moveVerbs.some(v => lower.includes(v));

    // 메뉴 키워드 매핑
    const routes = [
      { path: '/', keywords: ['대시보드', '메인', '홈', 'dashboard', 'home'] },
      { path: '/job-posting', keywords: ['채용공고', '공고', '채용', 'job posting'] },
      { path: '/resume', keywords: ['이력서 관리', '이력서관리', '이력서', 'resume', 'cv'] },
      { path: '/applicants', keywords: ['지원자 관리', '지원자관리', '지원자', 'applicant', 'candidate'] },
      { path: '/interview', keywords: ['면접 관리', '면접관리', '면접', 'interview'] },
      { path: '/interview-calendar', keywords: ['캘린더', '달력', '일정', 'calendar'] },
      { path: '/portfolio', keywords: ['포트폴리오 분석', '포트폴리오', 'portfolio'] },
      { path: '/cover-letter', keywords: ['자소서 검증', '자소서', 'cover letter'] },
      { path: '/talent', keywords: ['인재 추천', '인재추천', '인재', 'talent'] },
      { path: '/users', keywords: ['사용자 관리', '사용자관리', '사용자', 'user'] },
      { path: '/settings', keywords: ['설정', '세팅', 'settings'] },
    ];

    for (const r of routes) {
      if (r.keywords.some(k => lower.includes(k.toLowerCase()))) {
        // 이동 의도가 명시된 경우 우선 처리, 없더라도 정확 매칭이면 허용
        if (hasMoveVerb || lower.trim() === r.keywords[0].toLowerCase()) {
          return r.path;
        }
      }
    }
    return null;
  };

  const labelForPath = (path) => {
    const map = {
      '/': '대시보드',
      '/job-posting': '채용공고 등록',
      '/resume': '이력서 관리',
      '/applicants': '지원자 관리',
      '/interview': '면접 관리',
      '/interview-calendar': '면접 캘린더',
      '/portfolio': '포트폴리오 분석',
      '/cover-letter': '자소서 검증',
      '/talent': '인재 추천',
      '/users': '사용자 관리',
      '/settings': '설정'
    };
    return map[path] || path;
  };

  // 관리자 모드 상태 추정: 서버가 명시 API를 제공하지 않으므로 메시지 기반 추정 또는 추후 전용 API 연동
  useEffect(() => {
    const handler = (e) => {
      // 단순 표시용 훅: 특정 시스템 메시지를 감지해 토글 (향후 백엔드 API로 대체 가능)
      const text = String(e.detail || '').toLowerCase();
      if (text.includes('관리자 모드가 활성화되었습니다')) setIsAdminMode(true);
      if (text.includes('관리자 모드가 비활성화되었습니다')) setIsAdminMode(false);
    };
    window.addEventListener('chatbot-system', handler);
    return () => window.removeEventListener('chatbot-system', handler);
  }, []);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      content: inputValue,
      isUser: true,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // 1) 로컬 우선 실행: 현재 페이지에 버튼이 있는데도 답변만 하는 문제를 회피
    try {
      const text = userMessage.content.toLowerCase();
      const isActionLike = /(클릭|눌러|누르|열어|열기|상세|보기|삭제|제거|open|view|detail|delete|remove)/.test(text);
      if (isActionLike) {
        const page = await ensureUiIndexIfNeeded(window.location.href, true);
        const target = resolveByQuery(userMessage.content, 'click', page);
        if (target && target.selector) {
          const el = document.querySelector(target.selector);
          if (el) {
            try { window.HireMeUI?.highlightOnce?.(el); } catch(_) {}
            el.scrollIntoView?.({ behavior: 'smooth', block: 'center' });
            setTimeout(() => el.click(), 120);
            const botNotice = {
              id: Date.now() + 2,
              content: `요청하신 동작을 현재 페이지에서 바로 실행했습니다. (대상: ${target.text || target.selector})`,
              isUser: false,
              timestamp: new Date().toISOString(),
            };
            setMessages(prev => [...prev, botNotice]);
            setIsLoading(false);
            // 백엔드 호출 없이 로컬 실행 완료
            return;
          }
        }
      }
    } catch(_) {}

    // 1-b) 로컬 네비게이션 의도 감지 (예: "지원자 관리 이동")
    try {
      const navPath = resolveNavigationPath(userMessage.content);
      if (navPath) {
        navigate(navPath);
        const label = labelForPath(navPath);
        const botNotice = {
          id: Date.now() + 3,
          content: `${label} 페이지로 이동합니다. (navigate 툴 적용) 🚀`,
          isUser: false,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, botNotice]);
        setIsLoading(false);
        // 페이지 이동 후 UI 인덱스 수집 시도
        setTimeout(() => { try { ensureUiIndexIfNeeded(window.location.href, true); } catch(_) {} }, 400);
        return;
      }
    } catch(_) {}

    try {
      console.debug('[Chat][request.user]', userMessage.content);
      // WebSocket 우선 사용
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send(JSON.stringify({
            user_input: userMessage.content,
            session_id: sessionId,
            context: {
              current_page: window.location.pathname,
              user_agent: navigator.userAgent
            }
          }));
          return; // WS 모드에선 서버 응답 onmessage에서 처리
        } catch(_) {}
      }

      // 폴백: REST 호출
      const payload = {
        user_input: userMessage.content,
        session_id: sessionId,
        context: {
          current_page: window.location.pathname,
          user_agent: navigator.userAgent
        }
      };
      console.log('[DEBUG] POST /api/langgraph-agent/chat payload:', payload);
      console.debug('[Chat][request.payload]', payload);

      const response = await fetch('/api/langgraph-agent/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      console.log('[DEBUG] /chat status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

    	const data = await response.json();
      console.log('[DEBUG] /chat json:', data);
      console.debug('[Chat][response.raw]', { message: data.message, mode: data.mode, tool_used: data.tool_used });

		if (data.success) {
            let displayContent = data.message;
            let pageAction = null;
            try {
				const parsed = JSON.parse(data.message);
				console.log('[DEBUG] parsed message:', parsed);
				if (parsed && parsed.type === 'react_agent_response') {
					displayContent = parsed.response || data.message;
					pageAction = parsed.page_action || null;
				}
			} catch (e) {
				// message가 JSON이 아니면 그대로 사용
				console.warn('[DEBUG] message is not JSON, raw message used.');
			}

			const botMessage = {
				id: Date.now() + 1,
				content: displayContent,
				isUser: false,
				timestamp: data.timestamp,
				mode: data.mode,
				toolUsed: data.tool_used,
				confidence: data.confidence
			};

			setMessages(prev => [...prev, botMessage]);
            console.debug('[Chat][response.assistant]', displayContent);

			// 세션 ID 저장
			if (!sessionId) {
				setSessionId(data.session_id);
			}

			// React Agent page_action 처리
            if (pageAction && pageAction.action === 'navigate' && pageAction.target) {
				console.log('[DEBUG] navigate action:', pageAction.target);
				setTimeout(() => {
					navigate(pageAction.target);
                    // 페이지 이동 후 최초 1회 UI 인덱스 수집
                    setTimeout(() => {
                      try { ensureUiIndexIfNeeded(window.location.href, true); } catch(_) {}
                    }, 400);
                }, 100);
            } else if (pageAction && pageAction.action === 'dom' && pageAction.dom_action) {
              // DOM 액션 실행 (기본 구현)
              try {
                const a = pageAction.dom_action;
                const args = pageAction.args || {};
                console.log('[DEBUG] dom action:', a, 'args:', args);
                console.debug('[Action][dom.request]', { action: a, args });
                if (a === 'dumpUI') {
                  const href = window.location.href;
                  const page = await ensureUiIndexIfNeeded(href, true);
                  const list = page.elements.slice(0, 200).map((e, i) => `${i+1}. [${e.role}] ${e.text || e.attributes?.['aria-label'] || e.selector}`);
                  const content = `현재 페이지 UI 요소 ${page.elements.length}개 중 상위 200개:\n\n` + list.join('\n');
                  setMessages(prev => [...prev, { id: Date.now()+2, content, isUser: false, timestamp: new Date().toISOString() }]);
                  return;
                }
                // selector가 비어 있고 자연어 질의가 있을 경우 UI 인덱스에서 해석 시도
                if (!args.selector && args.query) {
                  try {
                    const page = await ensureUiIndexIfNeeded(window.location.href, true);
                    const kind = a === 'typeText' ? 'type' : 'click';
                    const target = resolveByQuery(args.query, kind, page);
                    if (target) args.selector = target.selector;
                    console.debug('[Action][dom.resolve]', { query: args.query, resolvedSelector: args.selector });
                  } catch(_) {}
                }
                // 현재 페이지에서 대상이 해석되지 않으면 범위 확장 요청 메시지 안내
                if (!args.selector && args.query) {
                  const ask = `현재 페이지에서 "${args.query}"을(를) 찾지 못했습니다.\n범위를 확장해 계속할까요?\n- 이 페이지 전체 재스캔: "이 페이지 다시 스캔"\n- 사이트 전역 검색: "사이트 전역에서 ${args.query} 찾기"\n- 다른 페이지로 이동: "채용공고 페이지로 이동" 등`;
                  setMessages(prev => [
                    ...prev,
                    { id: Date.now()+3, content: ask, isUser: false, timestamp: new Date().toISOString() }
                  ]);
                  console.debug('[Action][dom.unresolved]', { query: args.query, scope: 'page', suggested: true });
                  return; // 범위 확장 응답을 사용자에게 요청하고 종료
                }
                if (a === 'click') {
                  const el = document.querySelector(args.selector);
                  if (el) {
                    try { window.HireMeUI?.highlightOnce?.(el); } catch(_) {}
                    el.scrollIntoView?.({ behavior: 'smooth', block: 'center' });
                    setTimeout(() => el.click(), 150);
                  }
                } else if (a === 'typeText') {
                  const el = document.querySelector(args.selector);
                  if (el) el.value = args.text ?? '';
                } else if (a === 'submitForm') {
                  const el = document.querySelector(args.selector);
                  if (el && typeof el.submit === 'function') el.submit();
                } else if (a === 'check') {
                  const el = document.querySelector(args.selector);
                  if (el) el.checked = true;
                } else if (a === 'selectOption') {
                  const el = document.querySelector(args.selector);
                  if (el) el.value = args.value ?? '';
                } else if (a === 'scrollToElement') {
                  const el = document.querySelector(args.selector);
                  if (el) el.scrollIntoView({ behavior: 'smooth' });
                } else if (a === 'scrollToBottom') {
                  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                } else if (a === 'copyText') {
                  const el = document.querySelector(args.selector);
                  if (el) navigator.clipboard?.writeText?.(el.innerText || '');
                } else if (a === 'pasteText') {
                  const el = document.querySelector(args.selector);
                  if (el && navigator.clipboard?.readText) {
                    navigator.clipboard.readText().then(t => { el.value = t; }).catch(()=>{});
                  }
                } else if (a === 'getText') {
                  const el = document.querySelector(args.selector);
                  // 결과를 메시지로 표시만 함
                  const text = el ? (el.innerText || el.value || '') : '';
                  setMessages(prev => [...prev, { id: Date.now()+2, content: `값: ${text}`, isUser: false, timestamp: new Date().toISOString() }]);
                } else if (a === 'exists') {
                  const el = document.querySelector(args.selector);
                  const exists = !!el;
                  setMessages(prev => [...prev, { id: Date.now()+2, content: `존재 여부: ${exists}`, isUser: false, timestamp: new Date().toISOString() }]);
                }
                console.debug('[Action][dom.done]', { action: a, selectorTried: args.selector });
              } catch (err) {
                console.error('DOM 액션 실패:', err);
              }
			}
		} else {
        throw new Error(data.message || '응답 처리 실패');
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
      const errorMessage = {
        id: Date.now() + 1,
        content: '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.',
        isUser: false,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
		// 전송 후에도 입력창 포커스 유지
		setTimeout(() => {
			inputRef.current?.focus();
		}, 0);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && inputValue.trim()) {
        setIsSendAnimating(true);
        setTimeout(() => setIsSendAnimating(false), 1000);
      }
      sendMessage();
    }
  };

  const clearChat = async () => {
    if (sessionId) {
      try {
        await fetch(`/api/langgraph-agent/sessions/${sessionId}/clear`, {
          method: 'POST'
        });
      } catch (error) {
        console.error('채팅 기록 삭제 실패:', error);
      }
    }
    setMessages([]);
    setSessionId(null);
	// 기록 삭제 후 입력창 포커스
	setTimeout(() => {
		inputRef.current?.focus();
	}, 0);
  };

  const toggleChat = () => {
    const next = !isOpen;
    if (isControlled) {
      onOpenChange && onOpenChange(next);
    } else {
      setIsOpenInternal(next);
    }
    if (next) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 300);
    }
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const getStatusColor = () => {
    switch (agentStatus) {
      case 'healthy': return '#00c851';
      case 'unhealthy': return '#ff4444';
      case 'error': return '#ff8800';
      default: return '#999';
    }
  };

  return (
    <ChatbotContainer className="lgc-container">
      <AnimatePresence>
        {isOpen && (
          <ChatWindow
            className="lgc-window"
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ 
              opacity: 1, 
              y: 0, 
              scale: 1,
              height: isMinimized ? '64px' : '600px',
              width: isMinimized ? '64px' : '400px',
              borderRadius: isMinimized ? '50%' : '20px',
              padding: isMinimized ? '0px' : undefined
            }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            transition={{ duration: 0.25 }}
            style={{ overflow: 'hidden' }}
          >
            <ChatHeader className="lgc-header" style={{ display: isMinimized ? 'none' : undefined }}>
              <HeaderInfo className="lgc-header-info">
                <AgentIcon className="lgc-agent-icon">
                  <FiCpu />
                </AgentIcon>
                <HeaderText className="lgc-header-text">
                  <h3>에이전트 챗봇</h3>
                  <p>랭그래프 기반 리액트 에이전트 챗봇 {isAdminMode && '· 관리자'}</p>
                </HeaderText>
              </HeaderInfo>
              <HeaderActions className="lgc-header-actions">
                <div className="lgc-status-dot" style={{ 
                  width: '8px', 
                  height: '8px', 
                  borderRadius: '50%', 
                  backgroundColor: getStatusColor(),
                  marginRight: '8px'
                }} />
                <IconButton className="lgc-btn lgc-btn-minimize" onClick={toggleMinimize}>
                  {isMinimized ? <FiMaximize2 size={16} /> : <FiMinimize2 size={16} />}
                </IconButton>
                <IconButton className="lgc-btn lgc-btn-clear" onClick={clearChat}>
                  <FiRefreshCw size={16} />
                </IconButton>
                {isAdminMode && (
                  <IconButton className="lgc-btn lgc-btn-admin" onClick={() => setShowAdminPanel(true)} title="관리자 툴 관리">
                    <FiTool size={16} />
                  </IconButton>
                )}
                <IconButton className="lgc-btn lgc-btn-close" onClick={toggleChat}>
                  <FiX size={16} />
                </IconButton>
              </HeaderActions>
            </ChatHeader>

            {isMinimized ? (
              <MinimizedContent className="lgc-minimized" title="확대" onClick={toggleMinimize} aria-label="채팅창 확대">
                💬
              </MinimizedContent>
            ) : (
              <>
                <ChatBody className="lgc-body">
                  {messages.length === 0 && (
                    <WelcomeMessage className="lgc-welcome">
                      안녕하세요!<br /> 
                      저는 HireMe AI 어시스턴트입니다. 🤖<br />
                      채용 관련 질문이나 도움이 필요할 경우 말씀해주세요.
                    </WelcomeMessage>
                  )}
                  
                  {messages.map((message) => (
                    <MessageContainer key={message.id} $isUser={message.isUser} className={`lgc-message-container ${message.isUser ? 'lgc--user' : 'lgc--bot'}`}>
                      <Message
                        className="lgc-message"
                        $isUser={message.isUser}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        {message.content}
                        {message.toolUsed && (
                          <ToolIndicator className="lgc-tool-indicator">
                            <FiTool size={12} />
                            {message.toolUsed} 툴 사용
                          </ToolIndicator>
                        )}
                      </Message>
                    </MessageContainer>
                  ))}
                  
                  {isLoading && (
                    <MessageContainer className="lgc-message-container lgc--bot" isUser={false}>
                      <LoadingDots className="lgc-loading-dots">
                        <Dot className="lgc-loading-dot"
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                        />
                        <Dot className="lgc-loading-dot"
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                        />
                        <Dot className="lgc-loading-dot"
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                        />
                      </LoadingDots>
                    </MessageContainer>
                  )}
                  <div ref={messagesEndRef} />
                </ChatBody>

                <ChatInput className="lgc-input">
                  <Input
                    className="lgc-text-input"
                    ref={inputRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="메시지를 입력하세요..."
                    disabled={isLoading}
                  />
                  <SendButton
                    className="lgc-send-button"
                    onClick={() => {
                      if (!isLoading && inputValue.trim()) {
                        setIsSendAnimating(true);
                        setTimeout(() => setIsSendAnimating(false), 1000);
                      }
                      sendMessage();
                    }}
                    disabled={isLoading || !inputValue.trim()}
                  >
                    {/* 기본 아이콘 */}
                    <span className="lgc-send-base" style={{ opacity: isSendAnimating ? 0 : 1 }}>
                      <FiSend size={20} />
                    </span>
                    {/* 날아가는 복제 아이콘 */}
                    {isSendAnimating && (
                      <>
                        <motion.div
                          className="lgc-send-fly"
                          initial={{ x: 0, y: 0, scale: 1, opacity: 1, rotate: 0 }}
                          animate={{
                            x: [0, 12, 28, 52, 78],
                            y: [0, -10, -24, -36, -46],
                            scale: [1, 1.05, 1, 0.95, 0.9],
                            opacity: [1, 1, 0.9, 0.75, 0],
                            rotate: [0, 12, 20, 28, 36]
                          }}
                          transition={{ duration: 0.95, ease: 'easeOut' }}
                        >
                          <FiSend size={22} />
                        </motion.div>
                        {/* 트레일 2개 */}
                        <motion.div
                          className="lgc-send-trail"
                          style={{ width: 8, height: 8 }}
                          initial={{ x: 0, y: 0, opacity: 0.7, scale: 0.8 }}
                          animate={{ x: [0, 10, 30], y: [0, -8, -22], opacity: [0.7, 0.4, 0], scale: [0.8, 1.2, 1.6] }}
                          transition={{ duration: 0.9, ease: 'easeOut' }}
                        />
                        <motion.div
                          className="lgc-send-trail"
                          style={{ width: 6, height: 6 }}
                          initial={{ x: 0, y: 0, opacity: 0.6, scale: 0.7 }}
                          animate={{ x: [0, 6, 18], y: [0, -6, -16], opacity: [0.6, 0.35, 0], scale: [0.7, 1.1, 1.4] }}
                          transition={{ duration: 0.9, ease: 'easeOut', delay: 0.05 }}
                        />
                      </>
                    )}
                  </SendButton>
                </ChatInput>
              </>
            )}
          </ChatWindow>
        )}
      </AnimatePresence>

      {SHOW_PURPLE_TRIGGER_BUTTON && (
        <ChatButton
          className="lgc-trigger"
          onClick={toggleChat}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <FiMessageCircle />
        </ChatButton>
      )}

      {showAdminPanel && isAdminMode && (
        <AdminToolsManager className="lgc-admin-panel" sessionId={sessionId} onClose={() => setShowAdminPanel(false)} />
      )}
    </ChatbotContainer>
  );
};

export default LangGraphChatbot;
