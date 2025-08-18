import React, { useState, useRef, useEffect } from 'react';

const FloatingChatbot = ({ page, onFieldUpdate, onComplete, onPageAction }) => {
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
  
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // 디버깅용 로그
  console.log('FloatingChatbot 렌더링됨, page:', page);

  // 챗봇 닫기 함수
  const closeChat = () => {
    setIsOpen(false);
    console.log('챗봇이 자동으로 닫혔습니다.');
  };

  // 세션 초기화 로직 제거 (이제 불필요)
  useEffect(() => {
    // initializeSession(); // 세션 초기화 로직 제거
    // 챗봇이 처음 열릴 때 환영 메시지 추가 로직을 여기에 통합하거나 handleOpenChat에서만 실행
    if (messages.length === 0) {
      const welcomeMessage = {
        type: 'bot',
        content: getWelcomeMessage(page),
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [page]); // page 변경 시 환영 메시지 다시 설정

  // 챗봇 닫기 이벤트 리스너
  useEffect(() => {
    const handleCloseChatbot = () => {
      closeChat();
    };

    window.addEventListener('closeChatbot', handleCloseChatbot);

    return () => {
      window.removeEventListener('closeChatbot', handleCloseChatbot);
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
    
    // 챗봇이 열린 후 입력창에 포커스
    setTimeout(() => {
      focusInput();
    }, 300);
  };

  const getWelcomeMessage = (currentPage) => {
    const welcomeMessages = {
      'dashboard': `안녕하세요! 대시보드에서 어떤 도움이 필요하신가요?

📊 현재 현황을 확인하거나 다음 질문들을 해보세요:
• "현재 등록된 채용공고는 몇 개인가요?"
• "지원자 통계를 보여주세요"
• "면접 일정을 확인해주세요"`,
      
      'job-posting': `채용공고 등록을 도와드리겠습니다! 🎯

다음 질문들을 해보세요:
• "채용공고 등록 방법을 알려주세요"
• "어떤 부서에서 채용하시나요?"
• "채용공고 작성 팁을 알려주세요"
• "새로운 채용공고를 등록하고 싶어요"

💡 **스마트 등록 기능**: 
• "텍스트로 등록하고 싶어요" → 텍스트 기반 등록 (자동 진행)
• "이미지로 등록하고 싶어요" → 이미지 기반 등록 (자동 진행)

🤖 **AI 채용공고 작성 도우미**:
• "AI 도우미" 또는 "AI가 도와줘" → 단계별 질문으로 자동 입력
• "단계별로 질문해줘" → AI가 하나씩 질문하여 자동으로 입력

🚀 **자동 진행 기능**:
• 선택 후 2초 뒤 자동으로 다음 단계 진행
• 답변 입력 후 1.5초 뒤 자동으로 다음 질문 진행`,
      
      'resume': `이력서 관리에 대해 도움을 드리겠습니다! 📄

다음 질문들을 해보세요:
• "지원자 이력서를 어떻게 확인하나요?"
• "이력서 검토 방법을 알려주세요"
• "지원자 현황을 보여주세요"
• "이력서 필터링 기능이 있나요?"`,
      
      'interview': `면접 관리에 대해 문의하실 내용이 있으신가요? 🎤

다음 질문들을 해보세요:
• "면접 일정을 확인해주세요"
• "면접 평가 방법을 알려주세요"
• "면접 결과를 입력하고 싶어요"
• "면접 준비사항을 알려주세요"`,
      
      'portfolio': `포트폴리오 분석에 대해 도움을 드리겠습니다! 💼

다음 질문들을 해보세요:
• "포트폴리오 분석 기능이 뭔가요?"
• "지원자 포트폴리오를 어떻게 확인하나요?"
• "포트폴리오 평가 기준을 알려주세요"`,
      
      'cover-letter': `자기소개서 검증에 대해 문의하실 내용이 있으신가요? ✍️

다음 질문들을 해보세요:
• "자기소개서 검증 기능이 뭔가요?"
• "자소서 평가 방법을 알려주세요"
• "자소서 작성 팁을 알려주세요"`,
      
      'talent': `인재 추천에 대해 도움을 드리겠습니다! 👥

다음 질문들을 해보세요:
• "인재 추천 시스템이 어떻게 작동하나요?"
• "추천 인재를 확인하고 싶어요"
• "인재 매칭 기준을 알려주세요"`,
      
      'users': `사용자 관리에 대해 문의하실 내용이 있으신가요? 👤

다음 질문들을 해보세요:
• "사용자 목록을 확인해주세요"
• "새로운 사용자를 추가하고 싶어요"
• "사용자 권한을 변경하고 싶어요"`,
      
      'settings': `설정에 대해 도움을 드리겠습니다! ⚙️

다음 질문들을 해보세요:
• "시스템 설정을 변경하고 싶어요"
• "알림 설정을 확인해주세요"
• "백업 설정을 알려주세요"`
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

  // UI 구조를 읽어서 동적 키워드 생성
  const scanUIElements = () => {
    const uiElements = [];
    // 모달이 열려 있으면 모달 내부만, 아니면 전체 document에서 스캔
    let root = null;
    if (isOpen) {
      root = document.querySelector('.floating-chatbot-modal');
    }
    const base = root || document;
    
    // 버튼 요소들 스캔
    const buttons = base.querySelectorAll('button');
    buttons.forEach(button => {
      const text = button.textContent?.trim();
      if (text) {
        uiElements.push({
          type: 'button',
          text: text,
          element: button,
          keywords: generateKeywords(text)
        });
      }
    });
    
    // 링크 요소들 스캔
    const links = base.querySelectorAll('a');
    links.forEach(link => {
      const text = link.textContent?.trim();
      if (text) {
        uiElements.push({
          type: 'link',
          text: text,
          element: link,
          keywords: generateKeywords(text)
        });
      }
    });
    
    // 특정 클래스를 가진 요소들 스캔
    const clickableElements = base.querySelectorAll('[onclick], [data-action]');
    clickableElements.forEach(element => {
      const text = element.textContent?.trim();
      if (text) {
        uiElements.push({
          type: 'clickable',
          text: text,
          element: element,
          keywords: generateKeywords(text)
        });
      }
    });
    
    return uiElements;
  };

  // 텍스트에서 키워드 생성
  const generateKeywords = (text) => {
    const keywords = [];
    const lowerText = text.toLowerCase();
    
    // 원본 텍스트
    keywords.push(lowerText);
    
    // 단어별 분리
    const words = lowerText.split(/[\s,]+/).filter(word => word.length > 1);
    keywords.push(...words);
    
    // 유사 표현들 추가
    const synonyms = {
      '새로운': ['새', '신규', '새로'],
      '채용공고': ['공고', '채용', '구인'],
      '등록': ['작성', '만들기', '생성', '추가'],
      '텍스트': ['직접', '입력', '작성'],
      '이미지': ['그림', '사진', 'AI'],
      '템플릿': ['양식', '서식', '폼'],
      '조직도': ['부서', '조직', '구조'],
      '관리': ['설정', '편집', '수정']
    };
    
    // 유사어 추가
    words.forEach(word => {
      if (synonyms[word]) {
        keywords.push(...synonyms[word]);
      }
    });
    
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

  // 페이지별 액션 처리 함수 (UI 구조 기반)
  const handlePageAction = (message) => {
    const lowerMessage = message.toLowerCase();
    console.log('=== 디버깅 시작 ===');
    console.log('handlePageAction 호출됨:', message);
    console.log('소문자 변환된 메시지:', lowerMessage);
    console.log('현재 페이지:', page);

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
      
      // 미리 스캔된 UI 요소들 사용
      console.log('현재 저장된 UI 요소들:', uiElements);
      
      // 메시지와 UI 요소 매칭
      for (const element of uiElements) {
        for (const keyword of element.keywords) {
          if (lowerMessage.includes(keyword)) {
            // 매칭된 요소 클릭 시뮬레이션
            if (element.element && element.element.click) {
              element.element.click();
              return {
                message: `"${element.text}" 기능을 실행했습니다! ✅`
              };
            }
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
            }, 2000); // 2초 후 자동 진행
            
            // 챗봇 자동 닫기 (1초 후)
            setTimeout(() => {
              if (onPageAction) {
                onPageAction('closeChatbot');
              }
            }, 1000); // 1초 후 챗봇 닫기
            
            return {
              message: '텍스트 기반 채용공고 등록을 시작하겠습니다! 📝\n\nAI가 단계별로 질문하여 자동으로 입력해드릴게요.\n\n⏰ 2초 후 자동으로 다음 단계로 진행됩니다...\n\n💬 챗봇은 1초 후 자동으로 닫힙니다.'
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
            }, 2000); // 2초 후 자동 진행
            
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
        }, 2000);
        
        // 챗봇 자동 닫기 (1초 후)
        setTimeout(() => {
          if (onPageAction) {
            onPageAction('closeChatbot');
          }
        }, 1000); // 1초 후 챗봇 닫기
        
        return {
          message: '텍스트 기반 채용공고 등록을 시작하겠습니다! 📝\n\nAI가 단계별로 질문하여 자동으로 입력해드릴게요.\n\n⏰ 2초 후 자동으로 다음 단계로 진행됩니다...\n\n💬 챗봇은 1초 후 자동으로 닫힙니다.'
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
    
    // 자동 진행 활성화 - 2초 후 텍스트 기반 등록 시작
    setTimeout(() => {
      console.log('=== 2초 타이머 완료 - 자동 진행 시작 ===');
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
    }, 2000);
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
    }
    console.log('챗봇 상태 변경됨:', !isOpen);
  };

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // AI 모드인 경우 AI 응답 처리
    if (aiMode) {
      handleAIResponse(userMessage.content);
      setIsLoading(false);
      setTimeout(() => {
        focusInput();
      }, 100);
      return;
    }

    // 페이지별 액션 처리
    const pageAction = handlePageAction(inputValue);
    if (pageAction) {
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

    // 백엔드 API 호출 (Gemini 연동용)
    try {
      // 대화 기록을 추출하여 백엔드에 전달 (Gemini 모델에 보낼 대화 컨텍스트)
      const conversationHistory = messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'model', // Gemini API에 맞는 role로 변환
        parts: [{ text: msg.content }]
      }));

      const response = await fetch('/api/chatbot/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: inputValue,
          conversation_history: conversationHistory, // 대화 기록 전송
          current_page: page, // 현재 페이지 컨텍스트 추가
          mode: "normal" // 기존 모드 유지
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API 에러 응답:', errorData);
        throw new Error(`API 에러: ${response.status} - ${JSON.stringify(errorData)}`);
      }

      const data = await response.json();
      
      const botMessage = {
        type: 'bot',
        content: data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('챗봇 API 호출 실패:', error);
      const errorMessage = {
        type: 'bot',
        content: `죄송합니다. 일시적인 오류가 발생했습니다. (${error.message})`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // 전송 완료 후 입력창에 포커스
      setTimeout(() => {
        focusInput();
      }, 100);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* 플로팅 아이콘 */}
      <div
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
          zIndex: 99999,
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
          height: '75%',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          marginTop: '80px'
        }}>
          {/* 헤더 */}
          <div style={{
            padding: '16px',
            borderBottom: '1px solid #e5e7eb',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexShrink: 0
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
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              {/* 채팅 메시지 영역 */}
              <div style={{ 
                flex: 1, 
                overflowY: 'auto', 
                padding: '16px', 
                display: 'flex', 
                flexDirection: 'column', 
                gap: '16px',
                minHeight: 0 
              }}>
                {messages.map((message, index) => (
                  <div
                    key={index}
                    style={{ 
                      display: 'flex', 
                      justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start' 
                    }}
                  >
                    <div style={{
                      maxWidth: '280px',
                      padding: '8px 16px',
                      borderRadius: '8px',
                      backgroundColor: message.type === 'user' ? '#2563eb' : '#f3f4f6',
                      color: message.type === 'user' ? 'white' : '#1f2937'
                    }}>
                      <div style={{ fontSize: '14px', whiteSpace: 'pre-wrap' }}>
                        {message.content}
                      </div>
                      <div style={{ fontSize: '12px', opacity: 0.7, marginTop: '4px' }}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}

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