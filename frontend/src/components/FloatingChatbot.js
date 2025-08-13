import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const FloatingChatbot = ({ page, onFieldUpdate, onComplete, onPageAction }) => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uiElements, setUiElements] = useState([]);
  // const [sessionId, setSessionId] = useState(null); // 세션 ID 상태 제거
  
  // AI 채용공고 작성 도우미 관련 상태
  const [aiMode, setAiMode] = useState(false);
  const [aiStep, setAiStep] = useState(1);
  const [aiFormData, setAiFormData] = useState({
    department: '',
    experience: '',
    experienceYears: '',
    headcount: '',
    mainDuties: '',
    workHours: '',
    workDays: '',
    locationCity: '',
    locationDistrict: '',
    salary: '',
    contactEmail: '',
    deadline: ''
  });

  // RAG: 사용자 상호작용 학습을 위한 상태
  const [userInteractionHistory, setUserInteractionHistory] = useState([]);
  const [learnedPatterns, setLearnedPatterns] = useState({});

  // RAG: 사용자 상호작용 기록 함수
  const recordUserInteraction = (userInput, matchedElement, score, similarity) => {
    const interaction = {
      timestamp: new Date(),
      userInput: userInput,
      matchedElement: matchedElement ? {
        text: matchedElement.text,
        type: matchedElement.type,
        metadata: matchedElement.metadata
      } : null,
      score: score,
      similarity: similarity,
      page: page
    };

    setUserInteractionHistory(prev => [...prev, interaction]);
    
    // 최근 50개만 유지
    if (userInteractionHistory.length > 50) {
      setUserInteractionHistory(prev => prev.slice(-50));
    }
  };

  // RAG: 사용자 패턴 학습 함수
  const learnUserPatterns = () => {
    const patterns = {};
    
    userInteractionHistory.forEach(interaction => {
      const key = `${interaction.userInput.toLowerCase()}_${interaction.page}`;
      if (!patterns[key]) {
        patterns[key] = {
          count: 0,
          avgScore: 0,
          elements: new Set()
        };
      }
      
      patterns[key].count++;
      patterns[key].avgScore = (patterns[key].avgScore * (patterns[key].count - 1) + interaction.score) / patterns[key].count;
      
      if (interaction.matchedElement) {
        patterns[key].elements.add(interaction.matchedElement.text);
      }
    });

    setLearnedPatterns(patterns);
    console.log('RAG: 학습된 패턴:', patterns);
  };
  
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // 디버깅용 로그
  console.log('FloatingChatbot 렌더링됨, page:', page);

  // 챗봇 닫기 함수
  const closeChat = () => {
    setIsOpen(false);
    sessionStorage.setItem('chatbotWasOpen', 'false');
    console.log('챗봇이 자동으로 닫혔습니다.');
  };

  // 세션 초기화 로직 제거 (이제 불필요)
  useEffect(() => {
    // 페이지가 변경되면 채팅창을 닫고 메시지를 초기화
    setIsOpen(false);
    setMessages([]);
    setInputValue('');
    setIsLoading(false);
    setAiMode(false);
    setAiStep(1);
    setAiFormData({
      department: '',
      experience: '',
      experienceYears: '',
      headcount: '',
      mainDuties: '',
      workHours: '',
      workDays: '',
      locationCity: '',
      locationDistrict: '',
      salary: '',
      contactEmail: '',
      deadline: ''
    });
    
    console.log('페이지 변경으로 인한 채팅창 초기화:', page);
  }, [page]); // page 변경 시에만 실행

  // 챗봇이 열린 상태에서 페이지 이동 시 자동으로 다시 열기
  useEffect(() => {
    // 이전 페이지에서 챗봇이 열려있었다면 새 페이지에서도 열기
    const wasChatbotOpen = sessionStorage.getItem('chatbotWasOpen');
    if (wasChatbotOpen === 'true') {
      const timer = setTimeout(() => {
        setIsOpen(true);
        console.log('챗봇이 열린 상태에서 페이지 이동 후 자동 열기:', page);
        sessionStorage.removeItem('chatbotWasOpen'); // 사용 후 제거
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [page]);

  // 환영 메시지 설정을 위한 별도 useEffect
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage = {
        type: 'bot',
        content: getWelcomeMessage(page),
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [page, messages.length]);

  // RAG: 주기적으로 사용자 패턴 학습
  useEffect(() => {
    if (userInteractionHistory.length > 0) {
      const interval = setInterval(() => {
        learnUserPatterns();
      }, 30000); // 30초마다 학습

      return () => clearInterval(interval);
    }
  }, [userInteractionHistory]);

  // 챗봇 닫기 이벤트 리스너
  useEffect(() => {
    const handleCloseChatbot = () => {
      closeChat();
    };

    const handleHideFloatingChatbot = () => {
      setIsOpen(false);
      console.log('플로팅 챗봇이 숨겨졌습니다.');
    };

    const handleShowFloatingChatbot = () => {
      console.log('플로팅 챗봇이 다시 보입니다.');
    };

    const handleStartFreeTextMode = () => {
      console.log('자유 텍스트 모드 시작');
      sessionStorage.setItem('freeTextMode', 'true');
      setIsOpen(true);
      // 자유 텍스트 모드 안내 메시지
      const welcomeMessage = {
        type: 'bot',
        content: '자유 텍스트 모드로 시작합니다! 🎯\n\n채용 정보를 자유롭게 입력해주세요. AI가 자동으로 정보를 추출하여 폼에 입력해드리겠습니다.\n\n예시: "인천에서 디자인팀 1명을 뽑으려고 해. 9 to 6 근무이고 주말보장이야. 신입이라서 연봉은 2000만원 정도로 생각하고 있어."',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    };

    window.addEventListener('closeChatbot', handleCloseChatbot);
    window.addEventListener('hideFloatingChatbot', handleHideFloatingChatbot);
    window.addEventListener('showFloatingChatbot', handleShowFloatingChatbot);
    window.addEventListener('startFreeTextMode', handleStartFreeTextMode);

    return () => {
      window.removeEventListener('closeChatbot', handleCloseChatbot);
      window.removeEventListener('hideFloatingChatbot', handleHideFloatingChatbot);
      window.removeEventListener('showFloatingChatbot', handleShowFloatingChatbot);
      window.removeEventListener('startFreeTextMode', handleStartFreeTextMode);
    };
  }, []);

  // 세션 초기화 함수 제거
  // const initializeSession = async () => { /* ... */ };

  // 챗봇이 처음 열릴 때 환영 메시지 추가 (이 함수는 그대로 유지)
  const handleOpenChat = async () => {
    if (!isOpen && messages.length === 0) {
      // 환영 메시지 추가는 useEffect에서 처리하거나, 초기화 시점에 한 번만 실행되도록 조정
      // 현재는 useEffect에 메시지 초기화 로직이 있으므로 여기서는 제거
    }
    setIsOpen(true);
    sessionStorage.setItem('chatbotWasOpen', 'true');
    
    // 챗봇이 열린 후 입력창에 포커스
    setTimeout(() => {
      focusInput();
    }, 300);
  };

  // 메뉴 도움말 생성 함수
  const generateMenuHelp = () => {
    let helpText = '🎯 **사용 가능한 메뉴 키워드**:\n\n';
    
    for (const [categoryKey, category] of Object.entries(menuNavigationConfig.categories)) {
      helpText += `📂 **${category.title}**\n`;
      helpText += `└ ${category.description}\n\n`;
      
      for (const [menuName, menuInfo] of Object.entries(category.items)) {
        helpText += `• **${menuName}**: ${menuInfo.keywords.slice(0, 5).join(', ')}${menuInfo.keywords.length > 5 ? '...' : ''}\n`;
      }
      helpText += '\n';
    }
    
    return helpText;
  };

  const getWelcomeMessage = (currentPage) => {
    const welcomeMessages = {
      'dashboard': `안녕하세요! 대시보드에 대해 도움 드리겠습니다! 📊

📈 **대시보드 특징**:
• 전체 채용 현황을 한눈에 확인할 수 있는 메인 페이지
• 실시간 통계와 차트로 채용 진행 상황 파악
• 주요 지표와 알림을 통합 관리

🎯 **챗봇 조작 키워드**:
• "대시보드", "메인", "홈", "메인페이지", "홈페이지"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "채용공고 등록", "이력서 관리", "면접 관리", "지원자 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'job-posting': `안녕하세요! 채용공고 등록에 대해 도움 드리겠습니다! 🎯

📝 **채용공고 등록 특징**:
• 새로운 채용공고를 등록하고 관리하는 페이지
• 텍스트 기반과 이미지 기반 등록 방식 지원
• AI 도우미를 통한 스마트한 채용공고 작성

🎯 **챗봇 조작 키워드**:
• "채용공고", "공고", "채용", "구인", "채용공고등록", "공고등록", "채용등록"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "이력서 관리", "면접 관리", "지원자 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'resume': `안녕하세요! 이력서 관리에 대해 도움 드리겠습니다! 📄

📋 **이력서 관리 특징**:
• 지원자들의 이력서를 검토하고 관리하는 페이지
• 이력서 필터링, 검색, 평가 기능 제공
• 지원자 현황과 이력서 상태를 한눈에 확인

🎯 **챗봇 조작 키워드**:
• "이력서", "이력서관리", "이력서관리", "이력서보기", "이력서확인", "이력서검토"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "채용공고 등록", "지원자 관리", "면접 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'applicants': `안녕하세요! 지원자 관리에 대해 도움 드리겠습니다! 👥

👥 **지원자 관리 특징**:
• 지원자들의 정보와 상태를 관리하는 페이지
• 지원자 현황, 통계, 상세 정보 확인
• 지원자별 이력서와 포트폴리오 연동 관리

🎯 **챗봇 조작 키워드**:
• "지원자", "지원자관리", "지원자목록", "지원자보기", "지원자확인", "지원자검토"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "채용공고 등록", "이력서 관리", "면접 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'interview': `안녕하세요! 면접 관리에 대해 도움 드리겠습니다! 🎤

🎤 **면접 관리 특징**:
• 면접 일정과 평가를 관리하는 페이지
• 면접 일정 등록, 수정, 확인 기능
• 면접 평가 시스템과 결과 관리

🎯 **챗봇 조작 키워드**:
• "면접", "면접관리", "면접일정", "면접스케줄", "면접보기", "면접확인"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "채용공고 등록", "이력서 관리", "지원자 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'interview-calendar': `안녕하세요! 면접 캘린더에 대해 도움 드리겠습니다! 📅

📅 **면접 캘린더 특징**:
• 면접 일정을 캘린더 형태로 관리하는 페이지
• 월별, 주별 면접 일정 확인 및 관리
• 면접 일정 등록, 수정, 삭제 기능

🎯 **챗봇 조작 키워드**:
• "캘린더", "달력", "일정", "스케줄", "면접캘린더", "면접달력"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "채용공고 등록", "이력서 관리", "지원자 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'portfolio': `안녕하세요! 포트폴리오 분석에 대해 도움 드리겠습니다! 💼

💼 **포트폴리오 분석 특징**:
• 지원자들의 포트폴리오를 분석하고 평가하는 페이지
• 포트폴리오 검토, 평가, 비교 기능
• 지원자 역량과 경험을 종합적으로 분석

🎯 **챗봇 조작 키워드**:
• "포트폴리오", "포트폴리오분석", "포트폴리오보기", "포트폴리오확인", "분석"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "채용공고 등록", "이력서 관리", "지원자 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'cover-letter': `안녕하세요! 자소서 검증에 대해 도움 드리겠습니다! ✍️

✍️ **자소서 검증 특징**:
• 지원자들의 자기소개서를 검토하고 평가하는 페이지
• 자소서 내용 분석, 평가, 피드백 기능
• 지원자 의도와 표현력을 종합적으로 검토

🎯 **챗봇 조작 키워드**:
• "자소서", "자소서검증", "자소서보기", "자소서확인", "자기소개서"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "채용공고 등록", "이력서 관리", "지원자 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'talent': `안녕하세요! 인재 추천에 대해 도움 드리겠습니다! 👥

👥 **인재 추천 특징**:
• 적합한 인재를 추천하고 매칭하는 페이지
• 지원자 분석을 통한 인재 추천 시스템
• 채용 요구사항과 지원자 역량 매칭

🎯 **챗봇 조작 키워드**:
• "인재", "인재추천", "추천", "인재추천", "인재보기", "인재확인"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "채용공고 등록", "이력서 관리", "지원자 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'users': `안녕하세요! 사용자 관리에 대해 도움 드리겠습니다! 👤

👤 **사용자 관리 특징**:
• 시스템 사용자들의 계정과 권한을 관리하는 페이지
• 사용자 등록, 수정, 삭제 및 권한 설정
• 시스템 접근 권한과 보안 관리

🎯 **챗봇 조작 키워드**:
• "사용자", "사용자관리", "사용자목록", "사용자보기", "사용자확인"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "채용공고 등록", "이력서 관리", "지원자 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`,
      
      'settings': `안녕하세요! 설정에 대해 도움 드리겠습니다! ⚙️

⚙️ **설정 특징**:
• 시스템 설정과 환경을 관리하는 페이지
• 알림 설정, 보안 설정, 시스템 환경 설정
• 사용자 개인화 설정과 기본값 관리

🎯 **챗봇 조작 키워드**:
• "설정", "설정보기", "설정확인", "환경설정", "시스템설정"

🚀 **메뉴 이동**: 메뉴명을 말씀하시면 해당 페이지로 이동해드려요!
• "대시보드", "채용공고 등록", "이력서 관리", "지원자 관리" 등

🤖 **AI 챗봇은 사용자와의 채용 관련 자율대화가 가능하며, 메뉴명을 말씀하시면 해당 페이지로 이동할 수 있습니다.**`
        };
    
    return welcomeMessages[currentPage] || '안녕하세요! 어떤 도움이 필요하신가요?';
  };

  // 자동 스크롤 함수
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 메시지가 추가될 때마다 자동 스크롤
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 페이지가 변경될 때마다 UI 요소 스캔
  useEffect(() => {
    console.log('페이지 변경됨:', page);
    const scannedElements = scanUIElements();
    setUiElements(scannedElements);
    console.log('스캔된 UI 요소들:', scannedElements);
  }, [page]);

  // 입력창 포커스 함수
  const focusInput = () => {
    inputRef.current?.focus();
  };

  // UI 구조를 읽어서 동적 키워드 생성 (RAG 스타일 개선)
  const scanUIElements = () => {
    const uiElements = [];
    // 모달이 열려 있으면 모달 내부만, 아니면 전체 document에서 스캔
    let root = null;
    if (isOpen) {
      root = document.querySelector('.floating-chatbot-modal');
    }
    const base = root || document;
    
    // 버튼 요소들 스캔 (더 포괄적으로)
    const buttons = base.querySelectorAll('button, [role="button"], .btn, .button');
    buttons.forEach(button => {
      const text = button.textContent?.trim();
      if (text) {
        uiElements.push({
          type: 'button',
          text: text,
          element: button,
          keywords: generateKeywords(text),
          embedding: generateSimpleEmbedding(text), // RAG: 임베딩 추가
          metadata: {
            tagName: button.tagName,
            className: button.className,
            id: button.id
          }
        });
      }
    });
    
    // 링크 요소들 스캔
    const links = base.querySelectorAll('a, [role="link"]');
    links.forEach(link => {
      const text = link.textContent?.trim();
      if (text) {
        uiElements.push({
          type: 'link',
          text: text,
          element: link,
          keywords: generateKeywords(text),
          embedding: generateSimpleEmbedding(text), // RAG: 임베딩 추가
          metadata: {
            tagName: link.tagName,
            className: link.className,
            id: link.id,
            href: link.href
          }
        });
      }
    });
    
    // 클릭 가능한 요소들 스캔 (확장)
    const clickableSelectors = [
      '[onclick]', 
      '[data-action]', 
      '[data-click]', 
      '.clickable', 
      '.interactive',
      '[tabindex]',
      '.card',
      '.menu-item',
      '.nav-item'
    ];
    const clickableElements = base.querySelectorAll(clickableSelectors.join(', '));
    clickableElements.forEach(element => {
      const text = element.textContent?.trim();
      if (text && !element.closest('button, a')) { // 중복 방지
        uiElements.push({
          type: 'clickable',
          text: text,
          element: element,
          keywords: generateKeywords(text),
          embedding: generateSimpleEmbedding(text), // RAG: 임베딩 추가
          metadata: {
            tagName: element.tagName,
            className: element.className,
            id: element.id
          }
        });
      }
    });
    
    // 입력 필드들도 스캔 (레이블 포함)
    const inputs = base.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      // 입력 필드의 레이블 찾기
      let label = '';
      const id = input.getAttribute('id');
      if (id) {
        const labelElement = base.querySelector(`label[for="${id}"]`);
        if (labelElement) {
          label = labelElement.textContent?.trim();
        }
      }
      
      // placeholder도 키워드로 추가
      const placeholder = input.getAttribute('placeholder') || '';
      
      if (label || placeholder) {
        const fullText = label + ' ' + placeholder;
        uiElements.push({
          type: 'input',
          text: label || placeholder,
          element: input,
          keywords: generateKeywords(fullText),
          embedding: generateSimpleEmbedding(fullText), // RAG: 임베딩 추가
          metadata: {
            tagName: input.tagName,
            className: input.className,
            id: input.id,
            type: input.type,
            placeholder: placeholder
          }
        });
      }
    });
    
    // 제목 요소들 스캔
    const headings = base.querySelectorAll('h1, h2, h3, h4, h5, h6, .title, .heading');
    headings.forEach(heading => {
      const text = heading.textContent?.trim();
      if (text) {
        uiElements.push({
          type: 'heading',
          text: text,
          element: heading,
          keywords: generateKeywords(text),
          embedding: generateSimpleEmbedding(text), // RAG: 임베딩 추가
          metadata: {
            tagName: heading.tagName,
            className: heading.className,
            id: heading.id
          }
        });
      }
    });
    
    return uiElements;
  };

    // 텍스트에서 키워드 생성 (개선된 버전)
  const generateKeywords = (text) => {
    const keywords = [];
    const lowerText = text.toLowerCase();
    
    // 원본 텍스트
    keywords.push(lowerText);
    
    // 단어별 분리 (더 정교한 분리)
    const words = lowerText.split(/[\s,\.\-_]+/).filter(word => word.length > 1);
    keywords.push(...words);
    
    // 확장된 유사 표현들
    const synonyms = {
      '새로운': ['새', '신규', '새로', '신설', '첫', '처음'],
      '채용공고': ['공고', '채용', '구인', '모집', '채용정보', '구인정보', '채용안내'],
      '등록': ['작성', '만들기', '생성', '추가', '입력', '기재', '등록하기', '작성하기'],
      '텍스트': ['직접', '입력', '작성', '글자', '문자'],
      '이미지': ['그림', '사진', 'AI', '시각', '그래픽', '디자인'],
      '템플릿': ['양식', '서식', '폼', '틀', '형식', '템플릿'],
      '조직도': ['부서', '조직', '구조', '팀', '조직구조', '부서구조'],
      '관리': ['설정', '편집', '수정', '관리하기', '설정하기', '편집하기'],
      '지원자': ['지원', '지원자관리', '지원자현황', '지원자목록'],
      '면접': ['면접관리', '면접일정', '면접평가', '면접관리'],
      '포트폴리오': ['포트폴리오분석', '포트폴리오관리', '포트폴리오'],
      '자기소개서': ['자기소개서검증', '자기소개서관리', '자기소개서'],
      '인재추천': ['인재추천', '추천시스템', '인재추천시스템'],
      '통계': ['채용통계', '통계관리', '통계보기'],
      '대시보드': ['메인', '홈', '메인화면', '홈화면', '대시보드'],
      '설정': ['환경설정', '시스템설정', '설정관리'],
      '도움말': ['도움', '가이드', '매뉴얼', '사용법']
    };
    
    // 유사어 추가
    words.forEach(word => {
      if (synonyms[word]) {
        keywords.push(...synonyms[word]);
      }
    });
    
    // 부분 일치 키워드 추가 (더 유연한 매칭)
    const partialMatches = [];
    words.forEach(word => {
      if (word.length > 2) {
        // 3글자 이상인 단어의 부분 일치 추가
        for (let i = 3; i <= word.length; i++) {
          partialMatches.push(word.substring(0, i));
        }
      }
    });
    keywords.push(...partialMatches);
    
    // 특수 문자 제거 후 키워드 추가
    const cleanWords = words.map(word => word.replace(/[^\w가-힣]/g, ''));
    keywords.push(...cleanWords.filter(word => word.length > 1));
    
    return [...new Set(keywords)]; // 중복 제거
  };

   // 수정 명령에서 새로운 값 추출하는 함수들
   const extractNewValue = (message) => {
     // "부서를 마케팅으로 바꿔줘" → "마케팅" 추출
     const match = message.match(/를\s*([가-힣a-zA-Z]+)\s*로/);
     return match ? match[1] : null;
   };

   const extractNumber = (message) => {
     // "인원을 5명으로 바꿔줘" → 5 추출
     const match = message.match(/(\d+)명/);
     return match ? parseInt(match[1]) : null;
   };

   const extractSalary = (message) => {
     // "급여를 4000만원으로 바꿔줘" → "4000만원" 추출
     const match = message.match(/를\s*([0-9]+만원|[0-9]+천만원)\s*로/);
     return match ? match[1] : null;
   };

   const extractWorkContent = (message) => {
     // "업무를 웹개발로 바꿔줘" → "웹개발" 추출
     const match = message.match(/를\s*([가-힣a-zA-Z]+)\s*로/);
     return match ? match[1] : null;
   };

  // 메뉴 기반 페이지 이동 매핑
  // Enhanced menu navigation mapping with categories and comprehensive keywords
  const menuNavigationConfig = {
    categories: {
      '메인': {
        title: '메인',
        description: '시스템의 메인 페이지와 대시보드',
        items: {
          '대시보드': {
            path: '/',
            keywords: [
              '대시보드', '메인', '홈', '메인페이지', '홈페이지', '메인화면',
              'dashboard', 'main', 'home', '메인 대시보드', '홈 대시보드',
              '시작페이지', '첫페이지', '메인메뉴', '홈메뉴'
            ],
            synonyms: ['메인화면', '시작화면', '첫화면', '대시보드화면']
          }
        }
      },
      '채용 관리': {
        title: '채용 관리',
        description: '채용 과정의 모든 단계를 관리하는 기능들',
        items: {
          '채용공고 등록': {
            path: '/job-posting',
            keywords: [
              '채용공고', '공고', '채용', '구인', '채용공고등록', '공고등록', '채용등록',
              'job posting', 'recruitment', 'job', '구인공고', '채용공고작성',
              '공고작성', '채용공고관리', '공고관리', '채용관리', '구인관리',
              '채용공고등록', '공고등록', '채용등록', '구인등록'
            ],
            synonyms: ['구인공고', '채용공고작성', '공고작성', '채용공고관리']
          },
          '이력서 관리': {
            path: '/resume',
            keywords: [
              '이력서', '이력서관리', '이력서보기', '이력서확인', '이력서검토',
              'resume', 'cv', 'curriculum vitae', '이력서목록', '이력서리스트',
              '이력서검색', '이력서필터', '이력서평가', '이력서분석',
              '지원자이력서', '이력서관리', '이력서시스템'
            ],
            synonyms: ['CV', '커리큘럼', '이력서목록', '이력서리스트']
          },
          '지원자 관리': {
            path: '/applicants',
            keywords: [
              '지원자', '지원자관리', '지원자목록', '지원자보기', '지원자확인', '지원자검토',
              'applicant', 'candidate', '지원자리스트', '지원자명단', '지원자현황',
              '지원자통계', '지원자분석', '지원자평가', '지원자검색',
              '지원자필터', '지원자상태', '지원자관리시스템'
            ],
            synonyms: ['후보자', '지원자리스트', '지원자명단', '지원자현황']
          },
          '면접 관리': {
            path: '/interview',
            keywords: [
              '면접', '면접관리', '면접일정', '면접스케줄', '면접보기', '면접확인',
              'interview', '면접시스템', '면접관리시스템', '면접일정관리',
              '면접스케줄관리', '면접평가', '면접결과', '면접통계',
              '면접관리', '면접시스템', '면접관리시스템'
            ],
            synonyms: ['면접시스템', '면접관리시스템', '면접일정관리']
          },
          '캘린더': {
            path: '/interview-calendar',
            keywords: [
              '캘린더', '달력', '일정', '스케줄', '면접캘린더', '면접달력',
              'calendar', 'schedule', '면접일정', '면접스케줄', '면접캘린더',
              '면접달력', '면접일정관리', '면접스케줄관리', '면접캘린더관리',
              '면접달력관리', '면접일정보기', '면접스케줄보기'
            ],
            synonyms: ['면접일정', '면접스케줄', '면접캘린더', '면접달력']
          },
          '포트폴리오 분석': {
            path: '/portfolio',
            keywords: [
              '포트폴리오', '포트폴리오분석', '포트폴리오보기', '포트폴리오확인', '분석',
              'portfolio', '포트폴리오관리', '포트폴리오시스템', '포트폴리오평가',
              '포트폴리오검토', '포트폴리오분석', '포트폴리오비교', '포트폴리오통계',
              '포트폴리오관리시스템', '포트폴리오분석시스템'
            ],
            synonyms: ['포트폴리오관리', '포트폴리오시스템', '포트폴리오평가']
          },
          '자소서 검증': {
            path: '/cover-letter',
            keywords: [
              '자소서', '자소서검증', '자소서보기', '자소서확인', '자기소개서',
              'cover letter', '자기소개서', '자소서관리', '자소서시스템',
              '자소서평가', '자소서검토', '자소서분석', '자소서통계',
              '자소서관리시스템', '자소서검증시스템', '자기소개서관리'
            ],
            synonyms: ['자기소개서', '자소서관리', '자소서시스템', '자소서평가']
          },
          '인재 추천': {
            path: '/talent',
            keywords: [
              '인재', '인재추천', '추천', '인재추천', '인재보기', '인재확인',
              'talent', 'recommendation', '인재관리', '인재시스템', '인재추천시스템',
              '인재매칭', '인재검색', '인재분석', '인재평가', '인재통계',
              '인재관리시스템', '인재추천관리', '인재매칭시스템'
            ],
            synonyms: ['인재관리', '인재시스템', '인재추천시스템', '인재매칭']
          }
        }
      },
      '시스템': {
        title: '시스템',
        description: '시스템 관리 및 설정 기능들',
        items: {
          '사용자 관리': {
            path: '/users',
            keywords: [
              '사용자', '사용자관리', '사용자목록', '사용자보기', '사용자확인',
              'user', 'user management', '사용자리스트', '사용자명단', '사용자현황',
              '사용자통계', '사용자분석', '사용자평가', '사용자검색',
              '사용자필터', '사용자상태', '사용자관리시스템', '사용자권한'
            ],
            synonyms: ['사용자리스트', '사용자명단', '사용자현황', '사용자권한']
          },
          '설정': {
            path: '/settings',
            keywords: [
              '설정', '설정보기', '설정확인', '환경설정', '시스템설정',
              'settings', 'configuration', '환경설정', '시스템설정', '설정관리',
              '설정변경', '설정수정', '설정확인', '설정보기', '설정관리시스템',
              '환경설정관리', '시스템설정관리', '설정시스템'
            ],
            synonyms: ['환경설정', '시스템설정', '설정관리', '설정변경']
          }
        }
      }
    }
  };

  // 메뉴 기반 페이지 이동 처리
  // Enhanced menu navigation handling with categories and comprehensive keyword matching
  const handleMenuNavigation = (message) => {
    const lowerMessage = message.toLowerCase();
    let bestMatch = null;
    let highestScore = 0;

    // 모든 카테고리와 메뉴를 순회하며 키워드 매칭
    for (const [categoryKey, category] of Object.entries(menuNavigationConfig.categories)) {
      for (const [menuName, menuInfo] of Object.entries(category.items)) {
        // 키워드 매칭 점수 계산
        let score = 0;
        let matchedKeywords = [];

        // 정확한 키워드 매칭
        for (const keyword of menuInfo.keywords) {
          const lowerKeyword = keyword.toLowerCase();
          if (lowerMessage.includes(lowerKeyword)) {
            score += 10; // 정확한 키워드는 높은 점수
            matchedKeywords.push(keyword);
          }
        }

        // 유사어 매칭
        for (const synonym of menuInfo.synonyms) {
          const lowerSynonym = synonym.toLowerCase();
          if (lowerMessage.includes(lowerSynonym)) {
            score += 8; // 유사어는 중간 점수
            matchedKeywords.push(synonym);
          }
        }

        // 카테고리 키워드 매칭
        if (lowerMessage.includes(category.title.toLowerCase())) {
          score += 5; // 카테고리 키워드는 낮은 점수
        }

        // 가장 높은 점수의 매치 저장
        if (score > highestScore) {
          highestScore = score;
          bestMatch = {
            menuName,
            menuInfo,
            category,
            score,
            matchedKeywords
          };
        }
      }
    }

    // 매칭 결과가 있고 점수가 충분히 높으면 페이지 이동
    if (bestMatch && bestMatch.score >= 5) {
      console.log(`메뉴 매칭됨: ${bestMatch.menuName} → ${bestMatch.menuInfo.path} (점수: ${bestMatch.score})`);
      console.log(`매칭된 키워드: ${bestMatch.matchedKeywords.join(', ')}`);

      if (onPageAction) {
        console.log(`onPageAction 호출: changePage:${bestMatch.menuInfo.path.replace('/', '')}`);
        onPageAction(`changePage:${bestMatch.menuInfo.path.replace('/', '')}`);
      } else {
        console.log('onPageAction이 정의되지 않음');
      }

      // 폴백: 라우터 훅을 통한 직접 네비게이션 (환경 문제 시 보조)
      try {
        if (navigate) {
          navigate(bestMatch.menuInfo.path);
          console.log('[FloatingChatbot] navigate 호출:', bestMatch.menuInfo.path);
        }
      } catch (e) {
        console.warn('[FloatingChatbot] navigate 폴백 실패:', e);
      }

      // 카테고리 정보를 포함한 응답 메시지 생성
      const categoryInfo = bestMatch.category.title !== '메인' ? `\n📂 카테고리: ${bestMatch.category.title}` : '';
      const keywordInfo = bestMatch.matchedKeywords.length > 0 ? `\n🔍 인식된 키워드: ${bestMatch.matchedKeywords.slice(0, 3).join(', ')}` : '';

      return {
        message: `**${bestMatch.menuName}** 페이지로 이동할게요! 🚀\n\n📍 이동할 페이지: ${bestMatch.menuName}${categoryInfo}${keywordInfo}\n⏰ 잠시 후 페이지가 변경됩니다.`
      };
    }

    return null; // 매칭되는 메뉴가 없음
  };

  // 페이지별 액션 처리 함수 (UI 구조 기반)
  // 간단한 텍스트 임베딩 생성 함수 (RAG 스타일)
  const generateSimpleEmbedding = (text) => {
    const lowerText = text.toLowerCase();
    const words = lowerText.split(/[\s,\.\-_]+/).filter(word => word.length > 1);
    
    // 단어 빈도 기반 벡터 생성
    const vector = {};
    words.forEach(word => {
      vector[word] = (vector[word] || 0) + 1;
    });
    
    return vector;
  };

  // 코사인 유사도 계산 (RAG 스타일)
  const calculateCosineSimilarity = (vec1, vec2) => {
    const allKeys = new Set([...Object.keys(vec1), ...Object.keys(vec2)]);
    
    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;
    
    allKeys.forEach(key => {
      const val1 = vec1[key] || 0;
      const val2 = vec2[key] || 0;
      dotProduct += val1 * val2;
      norm1 += val1 * val1;
      norm2 += val2 * val2;
    });
    
    const denominator = Math.sqrt(norm1) * Math.sqrt(norm2);
    return denominator === 0 ? 0 : dotProduct / denominator;
  };

  // 문자열 유사도 계산 함수 (편집 거리 기반)
  const calculateSimilarity = (str1, str2) => {
    const matrix = [];
    const len1 = str1.length;
    const len2 = str2.length;

    // 초기화
    for (let i = 0; i <= len1; i++) {
      matrix[i] = [i];
    }
    for (let j = 0; j <= len2; j++) {
      matrix[0][j] = j;
    }

    // 편집 거리 계산
    for (let i = 1; i <= len1; i++) {
      for (let j = 1; j <= len2; j++) {
        if (str1[i - 1] === str2[j - 1]) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j] + 1,     // 삭제
            matrix[i][j - 1] + 1,     // 삽입
            matrix[i - 1][j - 1] + 1  // 교체
          );
        }
      }
    }

    // 유사도 계산 (0~1 사이 값)
    const maxLen = Math.max(len1, len2);
    return maxLen === 0 ? 1 : (maxLen - matrix[len1][len2]) / maxLen;
  };

  const handlePageAction = (message) => {
    const lowerMessage = message.toLowerCase();
    console.log('=== 디버깅 시작 ===');
    console.log('handlePageAction 호출됨:', message);
    console.log('소문자 변환된 메시지:', lowerMessage);
    console.log('현재 페이지:', page);

    // 도움말 요청 처리
    if (lowerMessage.includes('도움말') || lowerMessage.includes('help') || 
        lowerMessage.includes('메뉴') || lowerMessage.includes('키워드') ||
        lowerMessage.includes('사용법') || lowerMessage.includes('가이드')) {
      return {
        message: generateMenuHelp()
      };
    }

    // 먼저 메뉴 기반 페이지 이동 확인
    const menuNavigationResult = handleMenuNavigation(message);
    if (menuNavigationResult) {
      return menuNavigationResult;
    }

    const jobPostingKeywords = ['채용공고', '공고', '채용', '새공고', '등록', '작성', '구인', '새 공고', '새로운 공고', '신규 공고', '채용 공고', '채용공고 등록', '채용공고 작성', '채용공고 관리', '채용공고 목록', '채용공고 보기', '채용공고 확인', '채용공고 검색', '채용공고 수정', '채용공고 삭제', '채용공고 등록하기', '채용공고 작성하기', '채용공고 만들기', '채용공고 추가', '채용공고 입력', '채용공고 업로드', '채용공고 생성', '채용공고 제작', '채용공고 발행', '채용공고 게시', '채용공고 공개', '채용공고 등록하', '채용공고 작성하', '채용공고 만들', '채용공고 추가하', '채용공고 입력하', '채용공고 업로드하', '채용공고 생성하', '채용공고 제작하', '채용공고 발행하', '채용공고 게시하', '채용공고 공개하'];
    const isJobPostingRelated = jobPostingKeywords.some(keyword => lowerMessage.includes(keyword));
    
    // 새공고 관련 키워드 특별 처리
    const newJobPostingKeywords = ['새공고', '새 공고', '새로운 공고', '신규 공고', '새로운 채용', '신규 채용', '새로운 채용공고', '신규 채용공고', '새 채용공고', '새로운 채용 공고', '신규 채용 공고', '새 채용 공고', '새로운 채용공고 등록', '신규 채용공고 등록', '새 채용공고 등록', '새로운 채용공고 작성', '신규 채용공고 작성', '새 채용공고 작성', '새로운 채용공고 만들기', '신규 채용공고 만들기', '새 채용공고 만들기', '새로운 채용공고 추가', '신규 채용공고 추가', '새 채용공고 추가'];
    const isNewJobPostingRequest = newJobPostingKeywords.some(keyword => lowerMessage.includes(keyword));

    if (isJobPostingRelated && page !== 'job-posting') {
        if (onPageAction) {
            console.log('페이지 이동 요청: job-posting');
            onPageAction('changePage:job-posting'); // 페이지 이동 액션 호출
            
            // 페이지 이동 후 자동으로 등록 방법 선택 모달 표시
            setTimeout(() => {
                console.log('페이지 이동 후 자동으로 등록 방법 선택 모달 표시');
                onPageAction('openRegistrationMethod');
            }, 1000); // 1초 후 자동 실행
        }

        // 폴백: 직접 네비게이션
        try {
          if (navigate) {
            navigate('/job-posting');
            console.log('[FloatingChatbot] navigate 호출: /job-posting');
          }
        } catch (e) {
          console.warn('[FloatingChatbot] navigate 폴백 실패 (/job-posting):', e);
        }
        
        // 모든 채용공고 관련 키워드에 대해 동일한 메시지 제공
        return {
            message: `**채용공고** 관련 기능을 위해 해당 페이지로 이동할게요! 🚀\n\n⏰ 1초 후 자동으로 등록 방법을 선택할 수 있는 창이 나타납니다.\n\n📋 **등록 방법**:\n• 텍스트 기반: AI가 단계별로 질문하여 직접 입력\n• 이미지 기반: 채용공고 이미지를 업로드하여 자동 인식`
        };
    }

    if (isJobPostingRelated && page === 'job-posting') {
        // job-posting 페이지에서 채용공고 관련 키워드 입력 시 AI 어시스턴트 자동 시작
        console.log('job-posting 페이지에서 채용공고 키워드 감지 - AI 어시스턴트 자동 시작');
        startAIChatbot();
        
        return {
            message: `🤖 AI 채용공고 작성 도우미를 시작하겠습니다!\n\n단계별로 질문하여 자동으로 입력해드릴게요.\n\n⏰ 2초 후 자동으로 텍스트 기반 등록을 시작합니다...`
        };
    }

    if (page === 'job-posting') {
      // AI 채용공고 작성 도우미 시작 요청 감지
      if (lowerMessage.includes('ai 도우미') || lowerMessage.includes('채용공고 작성 도우미') || 
          lowerMessage.includes('도우미') || lowerMessage.includes('ai 작성') || 
          lowerMessage.includes('단계별') || lowerMessage.includes('질문') ||
          lowerMessage.includes('ai가 도와') || lowerMessage.includes('ai가 작성')) {
        
        // AI 도우미 모드 시작
        startAIChatbot();
        
        return {
          message: `🤖 AI 채용공고 작성 도우미를 시작하겠습니다!\n\n단계별로 질문하여 자동으로 입력해드릴게요.\n\n⏰ 2초 후 자동으로 텍스트 기반 등록을 시작합니다...`
        };
      }
      
      // 미리 스캔된 UI 요소들 사용 (RAG 스타일 매칭)
      console.log('현재 저장된 UI 요소들:', uiElements);
      
      // 사용자 입력에 대한 임베딩 생성
      const userEmbedding = generateSimpleEmbedding(lowerMessage);
      
      // 메시지와 UI 요소 매칭 (RAG 스타일 알고리즘)
      let bestMatch = null;
      let highestScore = 0;
      let retrievalResults = []; // RAG: 검색 결과 저장

      for (const element of uiElements) {
        let score = 0;
        let matchedKeywords = [];
        let retrievalScore = 0;

        // 1. 키워드 기반 매칭 (기존 방식)
        for (const keyword of element.keywords) {
          const lowerKeyword = keyword.toLowerCase();
          
          // 정확한 일치 (가장 높은 점수)
          if (lowerMessage.includes(lowerKeyword)) {
            score += 15;
            matchedKeywords.push(keyword);
          }
          // 부분 일치 (키워드가 메시지에 포함)
          else if (lowerKeyword.length > 2 && lowerMessage.includes(lowerKeyword)) {
            score += 8;
            matchedKeywords.push(keyword);
          }
          // 메시지가 키워드에 포함 (더 유연한 매칭)
          else if (lowerKeyword.length > 2 && lowerKeyword.includes(lowerMessage)) {
            score += 5;
            matchedKeywords.push(keyword);
          }
          // 유사도 기반 매칭
          else if (lowerKeyword.length > 3) {
            const similarity = calculateSimilarity(lowerMessage, lowerKeyword);
            if (similarity > 0.6) {
              score += Math.floor(similarity * 10);
              matchedKeywords.push(keyword);
            }
          }
        }

        // 2. RAG: 임베딩 기반 유사도 검색
        if (element.embedding) {
          const cosineSimilarity = calculateCosineSimilarity(userEmbedding, element.embedding);
          retrievalScore = cosineSimilarity * 20; // 코사인 유사도 점수
          
          // RAG: 검색 결과에 추가
          if (cosineSimilarity > 0.1) {
            retrievalResults.push({
              element: element,
              similarity: cosineSimilarity,
              score: retrievalScore
            });
          }
        }

        // 3. 요소 타입별 보너스 점수
        if (element.type === 'button') {
          score += 3; // 버튼은 클릭 가능하므로 높은 우선순위
        } else if (element.type === 'input') {
          score += 1; // 입력 필드는 중간 우선순위
        }

        // 4. 최종 점수 계산 (키워드 + 임베딩)
        const finalScore = score + retrievalScore;

        if (finalScore > highestScore) {
          highestScore = finalScore;
          bestMatch = {
            element: element,
            score: finalScore,
            matchedKeywords: matchedKeywords,
            retrievalScore: retrievalScore,
            cosineSimilarity: element.embedding ? calculateCosineSimilarity(userEmbedding, element.embedding) : 0
          };
        }
      }

      // RAG: 검색 결과 정렬 및 로깅
      retrievalResults.sort((a, b) => b.similarity - a.similarity);
      console.log('RAG 검색 결과 (상위 3개):', retrievalResults.slice(0, 3));

      // RAG: 매칭 결과 처리 (검색 기반 액션 생성)
      if (bestMatch && bestMatch.score >= 3) {
        console.log(`RAG UI 요소 매칭됨: "${bestMatch.element.text}"`);
        console.log(`- 총 점수: ${bestMatch.score}`);
        console.log(`- 키워드 점수: ${bestMatch.score - bestMatch.retrievalScore}`);
        console.log(`- 임베딩 점수: ${bestMatch.retrievalScore}`);
        console.log(`- 코사인 유사도: ${bestMatch.cosineSimilarity.toFixed(3)}`);
        console.log(`- 매칭된 키워드:`, bestMatch.matchedKeywords);

        // RAG: 사용자 상호작용 기록
        recordUserInteraction(lowerMessage, bestMatch.element, bestMatch.score, bestMatch.cosineSimilarity);

        // RAG: 컨텍스트 강화를 위한 메타데이터 활용
        const contextInfo = [];
        if (bestMatch.element.metadata) {
          if (bestMatch.element.metadata.tagName) {
            contextInfo.push(`태그: ${bestMatch.element.metadata.tagName}`);
          }
          if (bestMatch.element.metadata.className) {
            contextInfo.push(`클래스: ${bestMatch.element.metadata.className}`);
          }
        }

        // RAG: 학습된 패턴 활용
        const patternKey = `${lowerMessage}_${page}`;
        const learnedPattern = learnedPatterns[patternKey];
        const patternInfo = learnedPattern && learnedPattern.count > 1 ? 
          `\n🧠 학습된 패턴: ${learnedPattern.count}번 사용됨 (평균 점수: ${learnedPattern.avgScore.toFixed(1)})` : '';

        // 요소 클릭 시뮬레이션
        if (bestMatch.element.element && bestMatch.element.element.click) {
          try {
            bestMatch.element.element.click();
            console.log('RAG: 요소 클릭 성공');
            
            // RAG: 강화된 응답 메시지 생성
            const similarityInfo = bestMatch.cosineSimilarity > 0.3 ? 
              `\n🔍 의미적 유사도: ${(bestMatch.cosineSimilarity * 100).toFixed(1)}%` : '';
            const contextInfoText = contextInfo.length > 0 ? 
              `\n📋 요소 정보: ${contextInfo.join(', ')}` : '';

            // 새 공고 등록/채용공고 작성 관련이면 바로 AI 어시스턴트 시작
            const btnTextLower = String(bestMatch.element.text || '').replace(/\s+/g, '').toLowerCase();
            const isNewPosting = btnTextLower.includes('새공고') || btnTextLower.includes('새공고등록') || btnTextLower.includes('채용공고') || btnTextLower.includes('공고');
            try {
              if (isNewPosting && typeof startAIChatbot === 'function') {
                console.log('[FloatingChatbot] 새 공고 등록 - 바로 AI 어시스턴트 열기');
                startAIChatbot();
                return {
                  message: `🤖 AI 채용공고 작성 도우미를 시작합니다!\n${contextInfoText}${similarityInfo}`
                };
              }
            } catch (e) {
              console.warn('[FloatingChatbot] AI 어시스턴트 자동 시작 실패:', e);
            }

            // 기본 메시지 (간소화)
            return {
              message: `**${bestMatch.element.text}** 버튼을 클릭했어요! 🎯${contextInfoText}${similarityInfo}`
            };
          } catch (error) {
            console.error('RAG: 요소 클릭 실패:', error);
            return {
              message: `"${bestMatch.element.text}" 요소를 찾았지만 클릭할 수 없어요. 직접 클릭해주세요.`
            };
          }
        }
      }
      
      // 새공고 등록 요청 감지
      if (lowerMessage.includes('새공고') || lowerMessage.includes('새로운') || lowerMessage.includes('새 ') || 
          lowerMessage.includes('신규') || lowerMessage.includes('등록') || lowerMessage.includes('작성') || 
          lowerMessage.includes('만들')) {
        if (lowerMessage.includes('채용') || lowerMessage.includes('공고') || lowerMessage.includes('채용공고') || 
            lowerMessage.includes('새공고')) {
          
          // AI 어시스턴트 자동 시작
          console.log('새공고/채용공고 키워드 감지 - AI 어시스턴트 자동 시작');
          startAIChatbot();
          
          return {
            message: `🤖 AI 채용공고 작성 도우미를 시작하겠습니다!\n\n단계별로 질문하여 자동으로 입력해드릴게요.\n\n⏰ 2초 후 자동으로 텍스트 기반 등록을 시작합니다...`
          };
          
          // 텍스트 관련 키워드 감지
          const textKeywords = [
            '텍스트', '텍스트기반', '직접', '입력', '작성', '타이핑', '키보드', '문자', '수동', '손으로', 
            '하나씩', '단계별', '질문', '대화', '채팅', '말로', '음성', '음성인식', '글자', '문서',
            'word', '문서작성', '직접입력', '수동입력', '단계별입력', '대화형', '채팅형', '말로', '음성으로'
          ];
          const imageKeywords = [
            '이미지', '그림', '사진', 'AI', '스캔', '카메라', '업로드', '파일', 'OCR', 
            '자동', '인식', '분석', '추출', '업로드', '드래그', '드롭', '첨부', '업로드',
            '사진촬영', '스캔', '이미지인식', '자동인식', '파일업로드', '이미지분석', '그림으로', '사진으로'
          ];
          
          // 키워드 매칭 점수 계산
          let textScore = 0;
          let imageScore = 0;
          
          textKeywords.forEach(keyword => {
            if (lowerMessage.includes(keyword)) {
              textScore += 1;
            }
          });
          
          imageKeywords.forEach(keyword => {
            if (lowerMessage.includes(keyword)) {
              imageScore += 1;
            }
          });
          
          // 우선순위 키워드 (더 높은 가중치)
          const priorityTextKeywords = ['텍스트', '직접', '수동', '단계별', '대화', '채팅', '말로'];
          const priorityImageKeywords = ['이미지', '사진', '스캔', 'OCR', '업로드', '카메라', '그림'];
          
          priorityTextKeywords.forEach(keyword => {
            if (lowerMessage.includes(keyword)) {
              textScore += 3; // 우선순위 키워드는 더 높은 점수
            }
          });
          
          priorityImageKeywords.forEach(keyword => {
            if (lowerMessage.includes(keyword)) {
              imageScore += 3; // 우선순위 키워드는 더 높은 점수
            }
          });
          
          console.log('텍스트 점수:', textScore, '이미지 점수:', imageScore);
          
          // 키워드가 없으면 선택 메시지 표시
          if (textScore === 0 && imageScore === 0) {
            return {
              message: '새로운 채용공고를 등록하시는군요! 🎯\n\n어떤 방식으로 등록하시겠습니까?\n\n📝 **텍스트 기반**: AI가 단계별로 질문하여 직접 입력\n🖼️ **이미지 기반**: 채용공고 이미지를 업로드하여 자동 인식\n\n"텍스트" 또는 "이미지"로 답변해주세요!'
            };
          } else if (textScore > imageScore && textScore > 0) {
            // 텍스트 기반 등록 선택
            if (onPageAction) {
              onPageAction('openTextBasedRegistration');
            }
            
            // 자동으로 다음 단계 진행을 위한 타이머 설정 (즉시 실행)
            setTimeout(() => {
              console.log('자동 진행: startTextBasedFlow 실행');
              if (onPageAction) {
                onPageAction('startTextBasedFlow');
              }
            }, 1000); // 1초 후 자동 진행
            
            // 챗봇 자동 닫기 (1초 후)
            setTimeout(() => {
              if (onPageAction) {
                onPageAction('closeChatbot');
              }
            }, 1000); // 1초 후 챗봇 닫기
            
            return {
              message: '텍스트 기반 채용공고 등록을 시작하겠습니다! 📝\n\nAI가 단계별로 질문하여 자동으로 입력해드릴게요.\n\n⏰ 1초 후 자동으로 다음 단계로 진행됩니다...\n\n💬 챗봇은 1초 후 자동으로 닫힙니다.'
            };
          } else if (imageScore > textScore && imageScore > 0) {
            // 이미지 기반 등록 선택
            if (onPageAction) {
              onPageAction('openImageBasedRegistration');
            }
            
            // 자동으로 다음 단계 진행을 위한 타이머 설정 (즉시 실행)
            setTimeout(() => {
              console.log('자동 진행: startImageBasedFlow 실행');
              if (onPageAction) {
                onPageAction('startImageBasedFlow');
              }
            }, 1000); // 1초 후 자동 진행
            
            // 챗봇 자동 닫기 (1초 후)
            setTimeout(() => {
              if (onPageAction) {
                onPageAction('closeChatbot');
              }
            }, 1000); // 1초 후 챗봇 닫기
            
            return {
              message: '이미지 기반 채용공고 등록을 시작하겠습니다! 🖼️\n\n채용공고 이미지를 업로드해주시면 AI가 자동으로 분석하여 입력해드릴게요.\n\n⏰ 1초 후 자동으로 다음 단계로 진행됩니다...\n\n💬 챗봇은 1초 후 자동으로 닫힙니다.'
            };
          } else {
            // 키워드가 없거나 동점이면 기본 모달 열기
            if (onPageAction) {
              onPageAction('openRegistrationMethod');
            }
            return {
              message: '새로운 채용공고 등록을 시작하겠습니다! 📝\n\n등록 방법을 선택해주세요:\n• 텍스트 기반 등록\n• 이미지 기반 등록'
            };
          }
        }
      }
      
      // 텍스트/이미지 키워드 직접 감지 (새공고 없이)
      const textKeywords = ['텍스트', '텍스트기반', '직접', '수동', '단계별', '대화', '채팅', '말로', '음성으로', '타이핑', '키보드', 'text'];
      const imageKeywords = ['이미지', '사진', '그림', '스캔', 'OCR', '업로드', '카메라', '파일', 'image'];
      
      console.log('=== 텍스트/이미지 키워드 감지 디버깅 ===');
      console.log('텍스트 키워드 배열:', textKeywords);
      console.log('이미지 키워드 배열:', imageKeywords);
      
      let hasTextKeyword = textKeywords.some(keyword => lowerMessage.includes(keyword));
      let hasImageKeyword = imageKeywords.some(keyword => lowerMessage.includes(keyword));
      
      // 매칭된 키워드들 찾기
      const matchedTextKeywords = textKeywords.filter(keyword => lowerMessage.includes(keyword));
      const matchedImageKeywords = imageKeywords.filter(keyword => lowerMessage.includes(keyword));
      
      console.log('매칭된 텍스트 키워드들:', matchedTextKeywords);
      console.log('매칭된 이미지 키워드들:', matchedImageKeywords);
      console.log('키워드 감지 결과:', { hasTextKeyword, hasImageKeyword, message: lowerMessage });
      
      if (hasTextKeyword && !hasImageKeyword) {
        console.log('=== 텍스트 기반 등록 선택됨 ===');
        console.log('조건: hasTextKeyword =', hasTextKeyword, ', hasImageKeyword =', hasImageKeyword);
        
        // 텍스트 관련 키워드만 있으면 텍스트 기반 등록 선택
        if (onPageAction) {
          console.log('onPageAction 호출: openTextBasedRegistration');
          onPageAction('openTextBasedRegistration');
        }
        
        // 자동으로 다음 단계 진행을 위한 타이머 설정 (즉시 실행)
        setTimeout(() => {
          console.log('자동 진행: startTextBasedFlow 실행');
          if (onPageAction) {
            onPageAction('startTextBasedFlow');
          }
        }, 1000);
        
        // 챗봇 자동 닫기 (1초 후)
        setTimeout(() => {
          if (onPageAction) {
            onPageAction('closeChatbot');
          }
        }, 1000); // 1초 후 챗봇 닫기
        
        return {
          message: '텍스트 기반 채용공고 등록을 시작하겠습니다! 📝\n\nAI가 단계별로 질문하여 자동으로 입력해드릴게요.\n\n⏰ 1초 후 자동으로 다음 단계로 진행됩니다...\n\n💬 챗봇은 1초 후 자동으로 닫힙니다.'
        };
      } else if (hasImageKeyword && !hasTextKeyword) {
        console.log('=== 이미지 기반 등록 선택됨 ===');
        console.log('조건: hasTextKeyword =', hasTextKeyword, ', hasImageKeyword =', hasImageKeyword);
        
        // 이미지 관련 키워드만 있으면 이미지 기반 등록 선택
        if (onPageAction) {
          console.log('onPageAction 호출: openImageBasedRegistration');
          onPageAction('openImageBasedRegistration');
        }
        
        // 자동으로 다음 단계 진행을 위한 타이머 설정 (즉시 실행)
        setTimeout(() => {
          console.log('자동 진행: startImageBasedFlow 실행');
          if (onPageAction) {
            onPageAction('startImageBasedFlow');
          }
        }, 2000);
        
        // 챗봇 자동 닫기 (1초 후)
        setTimeout(() => {
          if (onPageAction) {
            onPageAction('closeChatbot');
          }
        }, 1000); // 1초 후 챗봇 닫기
        
        return {
          message: '이미지 기반 채용공고 등록을 시작하겠습니다! 🖼️\n\n채용공고 이미지를 업로드해주시면 AI가 자동으로 분석하여 입력해드릴게요.\n\n⏰ 2초 후 자동으로 다음 단계로 진행됩니다...\n\n💬 챗봇은 1초 후 자동으로 닫힙니다.'
        };
      } else {
        console.log('=== 키워드 매칭 실패 또는 조건 불만족 ===');
        console.log('조건: hasTextKeyword =', hasTextKeyword, ', hasImageKeyword =', hasImageKeyword);
      }
      
      // 모달 내부에서의 AI 챗봇 응답 처리
      if (lowerMessage.includes('개발') || lowerMessage.includes('마케팅') || lowerMessage.includes('영업') || 
          lowerMessage.includes('디자인') || lowerMessage.includes('기획') || lowerMessage.includes('신입') || 
          lowerMessage.includes('경력') || lowerMessage.includes('명') || lowerMessage.includes('업무') ||
          lowerMessage.includes('시간') || lowerMessage.includes('요일') || lowerMessage.includes('위치') ||
          lowerMessage.includes('연봉') || lowerMessage.includes('급여') || lowerMessage.includes('이메일') ||
          lowerMessage.includes('마감') || lowerMessage.includes('마감일')) {
        
        // AI 챗봇 응답 처리
        handleAIResponse(inputValue);
        
        return {
          message: '답변이 등록되었습니다! 다음 질문에 답변해주세요. 🤖'
        };
      }
      
      // 자동 진행 취소 키워드 처리
      if (lowerMessage.includes('취소') || lowerMessage.includes('중지') || lowerMessage.includes('멈춰') ||
          lowerMessage.includes('stop') || lowerMessage.includes('cancel')) {
        
        if (onPageAction) {
          onPageAction('cancelAutoProgress');
        }
        
        return {
          message: '자동 진행을 취소했습니다! ⏹️\n\n수동으로 진행하실 수 있습니다.'
        };
      }
      
      // 이미지 업로드 관련 키워드 처리
      if (lowerMessage.includes('이미지') || lowerMessage.includes('사진') || lowerMessage.includes('파일') ||
          lowerMessage.includes('업로드') || lowerMessage.includes('드래그') || lowerMessage.includes('드롭') ||
          lowerMessage.includes('첨부') || lowerMessage.includes('스캔') || lowerMessage.includes('OCR')) {
        
        // 이미지 업로드 자동 진행 (즉시 실행)
        const autoProgressTimer = setTimeout(() => {
          console.log('자동 진행: autoUploadImage 실행');
          if (onPageAction) {
            onPageAction('autoUploadImage');
          }
        }, 1000); // 1초 후 자동 진행
        
        return {
          message: '이미지 업로드를 자동으로 진행하겠습니다! 🖼️\n\n⏰ 1초 후 자동으로 이미지 분석을 시작합니다...\n\n💡 "취소"라고 입력하면 자동 진행을 중지할 수 있습니다.',
          timer: autoProgressTimer
        };
      }
      
      // 수정 관련 키워드 감지
      if (lowerMessage.includes('바꿔') || lowerMessage.includes('변경') || 
          lowerMessage.includes('수정') || lowerMessage.includes('바꾸') ||
          lowerMessage.includes('로 바꿔') || lowerMessage.includes('으로 변경') ||
          lowerMessage.includes('로 수정') || lowerMessage.includes('으로 바꿔')) {
        
        console.log('=== 수정 명령 감지 ===');
        console.log('수정 메시지:', lowerMessage);
        
        // 부서 수정
        if (lowerMessage.includes('부서') || lowerMessage.includes('팀') || lowerMessage.includes('직무')) {
          const newDepartment = extractNewValue(lowerMessage);
          if (newDepartment) {
            if (onPageAction) {
              onPageAction(`updateDepartment:${newDepartment}`);
            }
            return {
              message: `부서를 ${newDepartment}로 변경하겠습니다! ✅`
            };
          }
        }
        
        // 인원 수정
        if (lowerMessage.includes('인원') || lowerMessage.includes('명') || lowerMessage.includes('명수')) {
          const newHeadcount = extractNumber(lowerMessage);
          if (newHeadcount) {
            if (onPageAction) {
              onPageAction(`updateHeadcount:${newHeadcount}`);
            }
            return {
              message: `채용 인원을 ${newHeadcount}명으로 변경하겠습니다! ✅`
            };
          }
        }
        
        // 급여 수정
        if (lowerMessage.includes('급여') || lowerMessage.includes('연봉') || lowerMessage.includes('월급')) {
          const newSalary = extractSalary(lowerMessage);
          if (newSalary) {
            if (onPageAction) {
              onPageAction(`updateSalary:${newSalary}`);
            }
            return {
              message: `급여를 ${newSalary}로 변경하겠습니다! ✅`
            };
          }
        }
        
        // 업무 내용 수정
        if (lowerMessage.includes('업무') || lowerMessage.includes('일') || lowerMessage.includes('담당')) {
          const newWork = extractWorkContent(lowerMessage);
          if (newWork) {
            if (onPageAction) {
              onPageAction(`updateWorkContent:${newWork}`);
            }
            return {
              message: `업무 내용을 ${newWork}로 변경하겠습니다! ✅`
            };
          }
        }
      }
      
      if (lowerMessage.includes('도움') || lowerMessage.includes('help')) {
        const availableFeatures = uiElements.map(el => `• "${el.text}"`).join('\n');
        
        return {
          message: `현재 페이지에서 사용 가능한 기능들입니다! 🎯\n\n${availableFeatures}\n\n이 중에서 원하는 기능을 말씀해주세요!`
        };
      }
    }
    
    console.log('=== 디버깅 종료 ===');
    return null; // 액션이 없으면 null 반환
  };

  // AI 도우미 시작 함수
  const startAIChatbot = () => {
    console.log('=== startAIChatbot 함수 호출됨 ===');
    
    setAiMode(true);
    setAiStep(1);
    setAiFormData({
      department: '',
      experience: '',
      experienceYears: '',
      headcount: '',
      mainDuties: '',
      workHours: '',
      workDays: '',
      locationCity: '',
      locationDistrict: '',
      salary: '',
      contactEmail: '',
      deadline: ''
    });
    
    console.log('AI 모드 상태 초기화 완료');
    
    // AI 도우미 시작 메시지 추가
    const aiStartMessage = {
      type: 'bot',
      content: '🤖 AI 채용공고 작성 도우미를 시작합니다!\n\n먼저 구인 부서를 알려주세요. (예: 개발, 마케팅, 영업, 디자인 등)',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, aiStartMessage]);
    
    console.log('AI 시작 메시지 추가 완료');
    
    // 자동 진행 활성화 - 1초 후 텍스트 기반 등록 시작
    setTimeout(() => {
      console.log('=== 1초 타이머 완료 - 자동 진행 시작 ===');
      console.log('onPageAction 존재 여부:', !!onPageAction);
      
      if (onPageAction) {
        console.log('openTextBasedRegistration 액션 호출');
        onPageAction('openTextBasedRegistration');
        
        // 추가로 0.5초 후 AI 챗봇 시작
        setTimeout(() => {
          console.log('startTextBasedFlow 액션 호출');
          if (onPageAction) {
            onPageAction('startTextBasedFlow');
          }
        }, 500);
      } else {
        console.log('onPageAction이 없어서 자동 진행 불가');
      }
    }, 1000);
  };

  // AI 응답 처리 함수
  const handleAIResponse = (userInput) => {
    const currentField = getCurrentField(aiStep);
    
    // 사용자 입력을 현재 필드에 저장
    setAiFormData(prev => ({
      ...prev,
      [currentField.key]: userInput
    }));
    
    // 다음 단계로 이동
    const nextStep = aiStep + 1;
    setAiStep(nextStep);
    
    if (nextStep <= 8) { // 총 8단계
      const nextField = getCurrentField(nextStep);
      const nextMessage = {
        type: 'bot',
        content: `좋습니다! 이제 ${nextField.label}에 대해 알려주세요.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, nextMessage]);
    } else {
      // 모든 단계 완료
      const completeMessage = {
        type: 'bot',
        content: '🎉 모든 정보 입력이 완료되었습니다! 채용공고 등록을 진행하겠습니다.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, completeMessage]);
      
      // AI 모드 종료
      setAiMode(false);
      
      // 페이지 액션으로 텍스트 기반 등록 시작
      if (onPageAction) {
        onPageAction('openTextBasedRegistration');
      }
    }
  };

  // 현재 단계에 따른 필드 정보 반환
  const getCurrentField = (step) => {
    const fields = [
      { key: 'department', label: '구인 부서' },
      { key: 'headcount', label: '채용 인원' },
      { key: 'mainDuties', label: '업무 내용' },
      { key: 'workHours', label: '근무 시간' },
      { key: 'locationCity', label: '근무 위치' },
      { key: 'salary', label: '급여 조건' },
      { key: 'deadline', label: '마감일' },
      { key: 'contactEmail', label: '연락처 이메일' }
    ];
    return fields[step - 1] || fields[0];
  };

  const toggleChat = () => {
    console.log('챗봇 토글 클릭됨, 현재 상태:', isOpen);
    if (!isOpen) {
      handleOpenChat();
    } else {
      setIsOpen(false);
      sessionStorage.setItem('chatbotWasOpen', 'false');
    }
    console.log('챗봇 상태 변경됨:', !isOpen);
  };

  const sendMessage = async (customInput = null) => {
    console.log('[FloatingChatbot] sendMessage 호출됨');
    console.log('[FloatingChatbot] customInput:', customInput, '타입:', typeof customInput);
    console.log('[FloatingChatbot] inputValue:', inputValue, '타입:', typeof inputValue);
    
    const messageToSend = customInput || inputValue;
    console.log('[FloatingChatbot] messageToSend:', messageToSend, '타입:', typeof messageToSend);
    
    // messageToSend가 문자열이 아닌 경우 문자열로 변환
    const messageString = String(messageToSend || '');
    console.log('[FloatingChatbot] messageString:', messageString, '타입:', typeof messageString);
    
    if (!messageString.trim()) {
      console.log('[FloatingChatbot] 빈 메시지로 인해 전송 취소');
      return;
    }

    // 등록 관련 키워드 감지 시 페이지 이동 처리
    const registrationKeywords = ['등록', '채용공고', '채용', '공고', '작성', '만들어줘', '작성해줘', '등록해줘'];
    const hasRegistrationKeyword = registrationKeywords.some(keyword => 
      messageString.toLowerCase().includes(keyword.toLowerCase())
    );
    
    if (hasRegistrationKeyword) {
      console.log('[FloatingChatbot] 등록 관련 키워드 감지됨:', messageString);
      
      // 먼저 메뉴 기반 페이지 이동 확인
      const menuNavigationResult = handleMenuNavigation(messageString);
      if (menuNavigationResult) {
        console.log('[FloatingChatbot] 메뉴 네비게이션 결과:', menuNavigationResult);
        
        // 페이지 이동 후 키워드에 따른 추가 액션 실행
        setTimeout(() => {
          console.log('[FloatingChatbot] 페이지 이동 후 추가 액션 실행');
          
          // 키워드에 따른 추가 액션 처리
          if (messageString.toLowerCase().includes('새공고') || 
              messageString.toLowerCase().includes('새로운') ||
              messageString.toLowerCase().includes('신규') ||
              messageString.toLowerCase().includes('등록')) {
            // 바로 AI 어시스턴트 열기 (등록 방법 선택 모달 건너뛰기)
            console.log('[FloatingChatbot] 새 공고 등록 - 바로 AI 어시스턴트 열기');
            const event = new CustomEvent('startAIAssistant');
            window.dispatchEvent(event);
            console.log('[FloatingChatbot] AI 어시스턴트 열기 이벤트 발생');
          } else if (messageString.toLowerCase().includes('ai') ||
                     messageString.toLowerCase().includes('어시스턴트') ||
                     messageString.toLowerCase().includes('도우미')) {
            // AI 어시스턴트 열기
            const event = new CustomEvent('startAIAssistant');
            window.dispatchEvent(event);
            console.log('[FloatingChatbot] AI 어시스턴트 열기 이벤트 발생');
          }
        }, 1000); // 페이지 이동 후 1초 뒤에 실행 (페이지 로딩 시간 고려)
        
        const actionMessage = {
          type: 'bot',
          content: menuNavigationResult.message,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, actionMessage]);
        setIsLoading(false);
        setTimeout(() => {
          focusInput();
        }, 100);
        return;
      }
      
      // 메뉴 매칭이 안 되면 AI 어시스턴트 호출
      console.log('[FloatingChatbot] 메뉴 매칭 실패, AI 어시스턴트 호출');
      const event = new CustomEvent('openAIAssistant', {
        detail: {
          trigger: 'registration_keyword',
          message: messageString
        }
      });
      window.dispatchEvent(event);
      
      // 사용자에게 안내 메시지
      const guideMessage = {
        type: 'bot',
        content: '채용공고 등록을 위해 AI 어시스턴트를 열어드리겠습니다! 🚀',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, guideMessage]);
      setIsLoading(false);
      setTimeout(() => {
        focusInput();
      }, 100);
      return;
    }

    // (순서 변경) 일상대화/페이지 키워드는 페이지 액션 시도 이후로 이동

    console.log('[FloatingChatbot] sendMessage 시작:', messageString);
    console.log('[FloatingChatbot] 현재 상태 - isOpen:', isOpen, 'isLoading:', isLoading, 'aiMode:', aiMode);

    const userMessage = {
      type: 'user',
      content: messageString,
      timestamp: new Date()
    };

    console.log('[FloatingChatbot] 사용자 메시지 추가:', userMessage);
    setMessages(prev => {
      const newMessages = [...prev, userMessage];
      console.log('[FloatingChatbot] 전체 메시지:', newMessages);
      // 메시지 추가 후 스크롤 다운
      setTimeout(() => scrollToBottom(), 100);
      return newMessages;
    });
    setInputValue('');
    setIsLoading(true);

    // AI 모드인 경우 AI 응답 처리
    if (aiMode) {
      console.log('[FloatingChatbot] AI 모드에서 응답 처리');
      handleAIResponse(userMessage.content);
      setIsLoading(false);
      setTimeout(() => {
        focusInput();
      }, 100);
      return;
    }

    // 페이지별 액션 처리
    console.log('[FloatingChatbot] 페이지 액션 처리 시도');
    const pageAction = handlePageAction(messageString);
    if (pageAction) {
      console.log('[FloatingChatbot] 페이지 액션 실행됨:', pageAction);
      const actionMessage = {
        type: 'bot',
        content: pageAction.message,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, actionMessage]);
      setIsLoading(false);
      
      // 자동 진행 로그
      console.log('페이지 액션 실행됨:', pageAction.message);
      
      setTimeout(() => {
        focusInput();
      }, 100);
      return;
    }

    // 페이지 매칭이 없을 때만 일상대화/페이지 키워드 처리 (이동 등의 키워드 포함)
    const casualKeywords = ['안녕', '반가워', '도움', '도와줘', '이동', '페이지', '메뉴', '메인', '홈'];
    const hasCasualKeyword = casualKeywords.some(keyword => 
      messageString.toLowerCase().includes(keyword.toLowerCase())
    );
    if (hasCasualKeyword) {
      console.log('[FloatingChatbot] 일상대화/페이지이동 키워드 감지됨:', messageString);
      const casualResponse = {
        type: 'bot',
        content: '안녕하세요! 무엇을 도와드릴까요? 페이지 이동이나 메뉴 안내가 필요하시면 말씀해주세요! 😊',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, casualResponse]);
      setIsLoading(false);
      setTimeout(() => {
        focusInput();
      }, 100);
      return;
    }

    // 백엔드 API 호출 (Gemini 연동용)
    console.log('[FloatingChatbot] 백엔드 API 호출 시작');
    
    // 자유 텍스트 모드 감지 (sessionStorage에서 확인)
    const isFreeTextMode = sessionStorage.getItem('freeTextMode') === 'true';
    
    const requestBody = {
      user_input: messageString,
      conversation_history: messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      })),
      current_page: page,
      context: {},
      mode: isFreeTextMode ? 'free_text' : 'normal'
    };

    console.log('[FloatingChatbot] API 요청 데이터:', requestBody);

    // 인코딩 문제 해결을 위한 강력한 처리
    const requestBodyString = JSON.stringify(requestBody);
    const encoder = new TextEncoder();
    const encodedBody = encoder.encode(requestBodyString);

   const response = await fetch((process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/api/chatbot/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json; charset=utf-8',
        'Accept-Charset': 'utf-8'
      },
      body: encodedBody
    });

    console.log('[FloatingChatbot] API 응답 상태:', response.status, response.ok);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('API 에러 응답:', errorData);
      throw new Error(`API 에러: ${response.status} - ${JSON.stringify(errorData)}`);
    }

    const data = await response.json();
    
    console.log('[FloatingChatbot] 백엔드 응답:', data);
    console.log('[FloatingChatbot] 응답 message:', data.message);
    console.log('[FloatingChatbot] 응답 response:', data.response);
    console.log('[FloatingChatbot] 응답 type:', data.type);
    
    // autonomous_collection 타입 응답 처리
    if (data.type === 'autonomous_collection') {
      console.log('[FloatingChatbot] 자율모드 응답 감지 - 자동등록 처리 시작');
      console.log('[FloatingChatbot] 추출된 데이터:', data.extracted_data);
      
      // 추출된 데이터가 있으면 폼에 자동 입력
      if (data.extracted_data) {
        console.log('[FloatingChatbot] 추출된 데이터를 폼에 자동 입력');
        
        // 추출된 데이터를 폼 필드에 매핑하여 자동 입력
        const fieldMappings = {
          '부서': 'department',
          '인원': 'headcount', 
          '근무시간': 'workHours',
          '근무요일': 'workDays',
          '연봉': 'salary',
          '업무': 'mainDuties',
          '지역': 'locationCity'
        };
        
        // 각 추출된 필드를 해당 폼 필드에 입력
        Object.entries(data.extracted_data).forEach(([key, value]) => {
          const fieldKey = fieldMappings[key];
          if (fieldKey && onFieldUpdate) {
            console.log(`[FloatingChatbot] 필드 자동 입력: ${fieldKey} = ${value}`);
            onFieldUpdate(fieldKey, value);
          }
        });
      }
      
      // 자동등록 처리를 위한 이벤트 발생
      if (onPageAction) {
        console.log('[FloatingChatbot] 자동등록 액션 실행');
        
        // 1초 후 자동등록 시작
        setTimeout(() => {
          onPageAction('openTextBasedRegistration');
          
          // 추가로 0.5초 후 AI 챗봇 시작
          setTimeout(() => {
            onPageAction('startTextBasedFlow');
          }, 500);
        }, 1000);
      }
    }
    
    const botMessage = {
      type: 'bot',
      content: data.message || data.response || data.content || '응답을 받지 못했습니다.',
      timestamp: new Date(),
      suggestions: data.suggestions || []
    };

    console.log('[FloatingChatbot] 봇 메시지 생성:', botMessage);
    setMessages(prev => {
      const newMessages = [...prev, botMessage];
      // 봇 메시지 추가 후 스크롤 다운
      setTimeout(() => scrollToBottom(), 100);
      return newMessages;
    });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };





  return (
    <>
      {/* 플로팅 버튼 */}
      <div
        className="floating-chatbot"
        onClick={toggleChat}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '64px',
          height: '64px',
          backgroundColor: '#ff4444',
          borderRadius: '50%',
          boxShadow: '0 10px 25px rgba(255, 68, 68, 0.4)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 999,
          transition: 'all 0.3s ease',
          border: '3px solid white'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#ff0000';
          e.currentTarget.style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = '#ff4444';
          e.currentTarget.style.transform = 'scale(1)';
        }}
      >
        <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
          {isOpen ? '✕' : '💬'}
        </div>
      </div>

      {/* 모달 채팅창 */}
      <div
        className="floating-chatbot-modal" // [추가] 모달 구분용 클래스
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'flex-end',
          zIndex: 9998,
          padding: '16px',
          opacity: isOpen ? 1 : 0,
          pointerEvents: isOpen ? 'auto' : 'none',
          transition: 'opacity 0.3s ease'
        }}
      >
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
          width: '400px',
          height: '90%',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          marginTop: '20px',
          position: 'relative'
        }}>

          
          {/* 헤더 */}
          <div style={{
            padding: '16px',
            borderBottom: '1px solid #e5e7eb',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexShrink: 0,
            position: 'relative',
            zIndex: 2
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', margin: 0 }}>
              AI 챗봇
            </h3>
            <button
              onClick={toggleChat}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '18px',
                color: '#6b7280',
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              ✕
            </button>
          </div>
          
          {/* 채팅 인터페이스 */}
          <div style={{ 
            flex: 1, 
            overflow: 'hidden',
            position: 'relative',
            zIndex: 2
          }}>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              height: '100%',
              position: 'relative',
              zIndex: 2
            }}>
              {/* 채팅 메시지 영역 */}
              <div style={{ 
                flex: 1, 
                overflowY: 'auto', 
                padding: '16px', 
                display: 'flex', 
                flexDirection: 'column', 
                gap: '16px',
                minHeight: 0,
                position: 'relative',
                zIndex: 2
              }}>
                {messages.map((message, index) => {
                  console.log(`[FloatingChatbot] 메시지 렌더링 ${index}:`, message);
                  return (
                    <div
                      key={index}
                      style={{ 
                        display: 'flex', 
                        flexDirection: 'column',
                        alignItems: message.type === 'user' ? 'flex-end' : 'flex-start',
                        marginBottom: '8px'
                      }}
                    >
                      <div style={{
                        maxWidth: '280px',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        backgroundColor: message.type === 'user' ? '#2563eb' : '#f3f4f6',
                        color: message.type === 'user' ? 'white' : '#1f2937',
                        wordBreak: 'break-word'
                      }}>
                        <div style={{ fontSize: '14px', whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>
                          {message.content}
                        </div>
                        <div style={{ fontSize: '12px', opacity: 0.7, marginTop: '4px' }}>
                          {message.timestamp ? message.timestamp.toLocaleTimeString() : new Date().toLocaleTimeString()}
                        </div>
                      </div>
                      
                      {/* 추천 리스트 표시 */}
                      {message.type === 'bot' && message.suggestions && message.suggestions.length > 0 && (
                        <div style={{
                          marginTop: '8px',
                          display: 'flex',
                          flexWrap: 'wrap',
                          gap: '4px',
                          maxWidth: '280px'
                        }}>
                          {message.suggestions.map((suggestion, suggestionIndex) => (
                            <button
                              key={suggestionIndex}
                              onClick={() => {
                                console.log(`[FloatingChatbot] 추천 선택: ${suggestion}`);
                                setInputValue(suggestion);
                                // 선택된 추천을 즉시 전송
                                setTimeout(() => {
                                  sendMessage(suggestion);
                                }, 100);
                              }}
                              style={{
                                padding: '4px 8px',
                                fontSize: '12px',
                                backgroundColor: '#e5e7eb',
                                color: '#374151',
                                border: '1px solid #d1d5db',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                whiteSpace: 'nowrap',
                                maxWidth: '100px',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis'
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = '#d1d5db';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = '#e5e7eb';
                              }}
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}

                {isLoading && (
                  <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                    <div style={{
                      backgroundColor: '#f3f4f6',
                      color: '#1f2937',
                      padding: '8px 16px',
                      borderRadius: '8px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{
                          width: '16px',
                          height: '16px',
                          border: '2px solid #d1d5db',
                          borderTop: '2px solid #4b5563',
                          borderRadius: '50%',
                          animation: 'spin 1s linear infinite'
                        }}></div>
                        <span style={{ fontSize: '14px' }}>입력 중...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* 자동 스크롤을 위한 빈 div */}
                <div ref={messagesEndRef} />
              </div>

              {/* 입력 영역 */}
              <div style={{ 
                borderTop: '1px solid #e5e7eb', 
                padding: '16px', 
                flexShrink: 0 
              }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <textarea
                    ref={inputRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="메시지를 입력하세요..."
                    style={{
                      width: '100%',
                      padding: '8px 16px',
                      border: '1px solid #d1d5db',
                      borderRadius: '8px',
                      fontSize: '14px',
                      resize: 'none',
                      outline: 'none'
                    }}
                    rows={3}
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !inputValue.trim()}
                    style={{
                      padding: '8px 24px',
                      backgroundColor: '#2563eb',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      alignSelf: 'flex-end',
                      opacity: (isLoading || !inputValue.trim()) ? 0.5 : 1
                    }}
                  >
                    전송
                  </button>

                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default FloatingChatbot;