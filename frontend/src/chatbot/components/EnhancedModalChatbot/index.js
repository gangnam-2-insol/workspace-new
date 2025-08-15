import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import AIModeSelector from './AIModeSelector';
import ChatbotRestartButton from './ChatbotRestartButton';
import jsonFieldMapper from '../../utils/JsonFieldMapper';
import { classifyContext } from '../../nlp/contextClassifier';
import { loadRules, getRulesForContext } from '../../nlp/rulesLoader';
import { matchKeywords } from '../../nlp/keywordMatcher';
import rulesConfig from '../../config/rules/recruitRules.json';
import { getInitialField, getNextField, getPrompt } from '../../nlp/formFlow';
import ChatbotApiService from '../../services/chatbotApi';
import LangGraphApiService from '../../services/langgraphApi';

const EnhancedModalChatbot = ({
  isOpen,
  onClose,
  onFieldUpdate,
  onComplete,
  onTitleRecommendation,  // 새로운 prop: 제목 추천 모달 열기
  onPageAction,  // 새로운 prop: 페이지 액션 처리
  formData = {},
  pageId = 'recruit_form',
  initialAIMode = null,  // 초기 AI 모드 설정
  closeOnBackdropClick = false  // 배경 클릭 시 닫기 여부 (기본값: false)
}) => {
  // API URL 설정 - 환경 변수 또는 기본값 사용
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8010';
  
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // 세션 기반 히스토리를 위한 세션 ID (sessionStorage 사용하여 새로고침 시 자동 초기화)
  const [sessionId] = useState(() => {
    const existingSessionId = sessionStorage.getItem('aiChatbot_sessionId');
    if (existingSessionId) {
      return existingSessionId;
    }
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('aiChatbot_sessionId', newSessionId);
    return newSessionId;
  });
  const [showDirectionChoice, setShowDirectionChoice] = useState(true);
  const [selectedDirection, setSelectedDirection] = useState(null);

  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showEndChat, setShowEndChat] = useState(false);
  const [endChatTimer, setEndChatTimer] = useState(null);
  const [countdown, setCountdown] = useState(3);
  const [suggestions, setSuggestions] = useState([]);

  // 대화 순서 관리 상태
  const [conversationOrder, setConversationOrder] = useState({
    currentStep: 0,
    totalSteps: 8,
    completedFields: new Set(),
    isOrderBroken: false
  });

  // 필드 순서 정의
  const FIELD_ORDER = [
    { key: 'department', label: '구인 부서', step: 1 },
    { key: 'headcount', label: '채용 인원', step: 2 },
    { key: 'mainDuties', label: '주요 업무', step: 3 },
    { key: 'workHours', label: '근무 시간', step: 4 },
    { key: 'locationCity', label: '근무 위치', step: 5 },
    { key: 'salary', label: '급여 조건', step: 6 },
    { key: 'experience', label: '경력 요건', step: 7 },
    { key: 'contactEmail', label: '연락처 이메일', step: 8 }
  ];
  const [isFinalizing, setIsFinalizing] = useState(false);

  // 대화 재시작 함수
  const handleRestartConversation = useCallback(() => {
    console.log('[EnhancedModalChatbot] 대화 재시작');
    
    // 상태 초기화
    setMessages([]);
    setInputValue('');
    setIsLoading(false);
    setIsFinalizing(false);
    setShowModeSelector(true);
    setSelectedAIMode(null);
    setSelectedDirection(null);
    setShowDirectionChoice(true);
    
    // 순서 상태 초기화
    setConversationOrder({
      currentStep: 0,
      totalSteps: 8,
      completedFields: new Set(),
      isOrderBroken: false
    });
    
    // 세션 히스토리 클리어
    clearSessionHistory();
    
    // 초기 메시지 추가
    setTimeout(() => {
      setMessages([{
        type: 'bot',
        content: '안녕하세요! 채용공고 작성을 도와드리겠습니다. 어떤 방식으로 진행하시겠어요?',
        timestamp: new Date(),
        id: 'welcome-restart'
      }]);
    }, 100);
  }, []);

  // 현재 단계 업데이트 함수
  const updateCurrentStep = useCallback((fieldKey, value) => {
    const fieldInfo = FIELD_ORDER.find(f => f.key === fieldKey);
    if (!fieldInfo) return;

    setConversationOrder(prev => {
      const newCompleted = new Set(prev.completedFields);
      
      if (value && value.toString().trim()) {
        newCompleted.add(fieldKey);
      } else {
        newCompleted.delete(fieldKey);
      }

      // 다음 단계 계산
      let nextStep = 0;
      for (let i = 0; i < FIELD_ORDER.length; i++) {
        if (!newCompleted.has(FIELD_ORDER[i].key)) {
          nextStep = i + 1;
          break;
        }
        if (i === FIELD_ORDER.length - 1) {
          nextStep = FIELD_ORDER.length; // 모든 필드 완료
        }
      }

      return {
        ...prev,
        currentStep: nextStep,
        completedFields: newCompleted,
        isOrderBroken: false // 정상 진행으로 표시
      };
    });
  }, [FIELD_ORDER]);

  // 안전한 메시지 생성 헬퍼 함수
  const createMessage = useCallback((type, content, additionalProps = {}) => {
    return {
      type,
      content,
      timestamp: new Date(),
      id: `${type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      ...additionalProps
    };
  }, []);

  // AI 모드 관련 상태 추가
  const [selectedAIMode, setSelectedAIMode] = useState(null);
  const [showModeSelector, setShowModeSelector] = useState(true);
  
  // 필드 관련 상태 추가
  const [filledFields, setFilledFields] = useState({});
  const [currentField, setCurrentField] = useState(null);
  const [lastExtractedJson, setLastExtractedJson] = useState(null);
  const [rules, setRules] = useState(null);
  const [currentContext, setCurrentContext] = useState('job_posting');

  // 동적 UI 스캔 기반 필드 목록 (현재 페이지 UI에 존재하는 항목만 질문)
  const [dynamicFields, setDynamicFields] = useState([]);

  // 동적 프롬프트 생성 (동적 필드 정의보다 먼저 참조되므로 상단에 위치)
  const getDynamicPromptFor = useCallback((fieldName) => {
    const f = dynamicFields.find((x) => x.name === fieldName);
    if (!f) return null;
    const base = f.label || f.name;
    // 간단한 조사 처리
    const needsRl = /[가-힣]$/.test(base) && !/[가-힣]$/.test(base.replace(/.*([가-힣])$/, '$1')) ? '를' : '을';
    return `${base}${needsRl} 알려주세요.`;
  }, [dynamicFields]);

  const scanFormFieldsFromPage = useCallback(() => {
    try {
      const results = [];
      const chatContainer = document.querySelector('.enhanced-modal-chatbot-container');

      // 1) 우선 순위: 화면상의 폼 그룹 순서를 그대로 따름
      const formGroups = Array.from(document.querySelectorAll('.custom-form-group'));
      if (formGroups.length > 0) {
        formGroups.forEach((grp) => {
          if (chatContainer && chatContainer.contains(grp)) return; // 챗봇 내부 제외
          const el = grp.querySelector('input, textarea, select');
          if (!el) return;
          const style = window.getComputedStyle(el);
          if (style.display === 'none' || style.visibility === 'hidden') return;
          if (el.type === 'hidden' || el.type === 'button' || el.type === 'submit' || el.disabled) return;

          const id = el.getAttribute('id');
          const name = el.getAttribute('name') || id;
          if (!name) return;
          let label = '';
          const labelEl = grp.querySelector('label');
          if (labelEl) label = labelEl.textContent?.trim() || '';
          if (!label && id) {
            const forLabel = document.querySelector(`label[for="${id}"]`);
            if (forLabel) label = forLabel.textContent?.trim() || '';
          }
          if (!label) label = el.getAttribute('placeholder') || name;

          if (!results.some((r) => r.name === name)) {
            results.push({ name, label: (label || name).replace(/\*|:|\s+\*$/g, '').trim(), tag: el.tagName.toLowerCase(), type: el.type || 'text' });
          }
        });
      }

      // 2) 폴백: 페이지 전체 입력을 순차 스캔
      if (results.length === 0) {
        const allInputs = Array.from(document.querySelectorAll('input, textarea, select'));
        allInputs.forEach((el) => {
          if (!el || (chatContainer && chatContainer.contains(el))) return;
          const style = window.getComputedStyle(el);
          if (style.display === 'none' || style.visibility === 'hidden') return;
          if (el.type === 'hidden' || el.type === 'button' || el.type === 'submit' || el.disabled) return;
          const id = el.getAttribute('id');
          const name = el.getAttribute('name') || id;
          if (!name) return;
          let label = '';
          if (id) {
            const forLabel = document.querySelector(`label[for="${id}"]`);
            if (forLabel) label = forLabel.textContent?.trim() || '';
          }
          if (!label) {
            const parentLabel = el.closest('label');
            if (parentLabel) label = parentLabel.textContent?.trim() || '';
          }
          if (!label) {
            const grp = el.closest('.custom-form-group');
            if (grp) {
              const l = grp.querySelector('label');
              if (l) label = l.textContent?.trim() || '';
            }
          }
          if (!label) label = el.getAttribute('placeholder') || name;
          if (!results.some((r) => r.name === name)) {
            results.push({ name, label: (label || name).replace(/\*|:|\s+\*$/g, '').trim(), tag: el.tagName.toLowerCase(), type: el.type || 'text' });
          }
        });
      }
      return results;
    } catch (e) {
      console.warn('[EnhancedModalChatbot] UI 스캔 실패:', e);
      return [];
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      const fields = scanFormFieldsFromPage();
      setDynamicFields(fields);
    }
  }, [isOpen, scanFormFieldsFromPage]);

  // 동적 필드 로드 이후 개별입력 초기 프롬프트 재설정 (최적화된 버전)
  useEffect(() => {
    if (isOpen && selectedAIMode === 'individual_input' && !currentField && dynamicFields.length > 0) {
      const first = dynamicFields[0]?.name;
      if (first) {
        setSelectedAIMode('individual_input');
        setShowModeSelector(false);
        setCurrentField(first);
        const prompt = getDynamicPromptFor(first) || getPrompt(pageId, first) || '먼저 필요한 항목부터 알려주세요.';
        setMessages(prev => [...prev, { type: 'bot', content: prompt, timestamp: new Date(), id: `bot-nextprompt-${Date.now()}` }]);
        
        // 최적화된 스크롤 로직 (한 번만 시도)
        const scrollToFirstField = () => {
          const selectors = [
            `input[name="${first}"]:not([type="hidden"]):not([disabled])`,
            `textarea[name="${first}"]:not([disabled])`,
            `select[name="${first}"]:not([disabled])`,
            `.custom-form-group input[name="${first}"]:not([type="hidden"]):not([disabled])`,
            `.custom-form-group textarea[name="${first}"]:not([disabled])`,
            `#${first}:not([type="hidden"]):not([disabled])`
          ];
          
          for (const sel of selectors) {
            const elements = document.querySelectorAll(sel);
            for (const el of elements) {
              const isVisible = el.offsetParent !== null && 
                               window.getComputedStyle(el).display !== 'none' && 
                               window.getComputedStyle(el).visibility !== 'hidden';
              
              if (el && isVisible) {
                console.log(`[EnhancedModalChatbot] 개별입력 모드 시작 - 첫 번째 필드 스크롤 성공: ${first}`);
                
                // 즉시 스크롤 (부드러운 스크롤 제거로 성능 향상)
                el.scrollIntoView({ 
                  behavior: 'auto', 
                  block: 'center',
                  inline: 'nearest'
                });
                
                // 시각적 강조 (포커싱 없이)
                const originalBorder = el.style.border;
                const originalBoxShadow = el.style.boxShadow;
                el.style.border = '2px solid #10b981';
                el.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.2)';
                
                setTimeout(() => {
                  el.style.border = originalBorder;
                  el.style.boxShadow = originalBoxShadow;
                }, 2000);
                
                return;
              }
            }
          }
        };
        
        // 지연 시간 단축
        setTimeout(scrollToFirstField, 300);
      }
    }
  }, [isOpen, selectedAIMode, currentField, dynamicFields.length, getDynamicPromptFor, pageId, getPrompt]);

  // 공통 폼 플로우 유틸 사용 (다른 페이지에서도 재사용)
  const getNextFieldKey = useCallback((currentKey) => getNextField(pageId, currentKey), [pageId]);
  
  // 적용/입력 명령 감지 및 필드 추론 유틸
  const fieldDisplayNames = {
    department: '부서',
    position: '직무',
    headcount: '인원',
    experience: '경력',
    workType: '형태',
    workHours: '시간',
    workDays: '요일',
    salary: '연봉',
    locationCity: '근무지',
    mainDuties: '업무',
    contactEmail: '이메일',
    deadline: '마감일',
    additionalInfo: '기타 항목'
  };

  // 입력 유효성 검사기
  const exampleForField = {
    department: '예: 개발, 마케팅, 영업, 디자인',
    headcount: '예: 1명, 3명',
    workHours: '예: 09:00 ~ 18:00',
    workDays: '예: 월~금, 월~토',
    salary: '예: 4,000만원, 3,000 ~ 5,000만원, 협의',
    locationCity: '예: 서울, 인천, 부산',
    mainDuties: '예: 웹 서비스 백엔드 개발 및 운영',
    contactEmail: '예: hr@example.com',
    deadline: '예: 2025-12-31',
    experience: '예: 신입, 3년 이상'
  };

  const knownDepartments = ['개발', '마케팅', '영업', '디자인', '기획', '인사', '재무', '운영', '데이터', '백엔드', '프론트엔드', 'QA', '품질', '생산', 'CS'];

  const validateFieldValue = useCallback((fieldKey, rawValue) => {
    const value = String(rawValue || '').trim();
    const fail = (msg) => ({ isValid: false, normalizedValue: null, errorMessage: msg });
    const ok = (v) => ({ isValid: true, normalizedValue: v, errorMessage: null });

    if (!value) return fail('값이 비어 있습니다.');

    switch (fieldKey) {
      case 'department': {
        const onlyKorean = /^[가-힣A-Za-z\s]{2,20}$/;
        const containsKnown = knownDepartments.some((kw) => value.includes(kw));
        if (!onlyKorean.test(value) && !containsKnown) {
          return fail(`${exampleForField.department}`);
        }
        // 팀/실/본부 접미사 자동 보정
        const normalized = value.replace(/\s+/g, '').endsWith('팀') ? value : value;
        return ok(normalized);
      }
      case 'headcount': {
        const m = value.match(/(\d{1,3})/);
        if (!m) return fail(`${exampleForField.headcount}`);
        const n = Math.max(0, Math.min(999, parseInt(m[1], 10)));
        return ok(`${n}명`);
      }
      case 'contactEmail': {
        const re = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
        if (!re.test(value)) return fail(`${exampleForField.contactEmail}`);
        return ok(value);
      }
      case 'workHours': {
        const text = value;
        const ampm = (h, ap) => {
          let hh = parseInt(h, 10);
          if (/오후|pm/i.test(ap || '')) hh = (hh % 12) + 12;
          if (/오전|am/i.test(ap || '')) hh = (hh % 12);
          return hh;
        };
        // 오전10시~오후8시, 10:00~20:00, 9~18, 9-6(=18), 9 to 6, 9시부터 6시까지
        const apRe = /(오전|오후|am|pm)?\s*(\d{1,2})(?::?(\d{2}))?\s*[시:]?/i;
        const rangeRe = new RegExp(`${apRe.source}\s*[~\-]\s*${apRe.source}`);
        const rangeTo = new RegExp(`${apRe.source}\s*(?:to|TO)\s*${apRe.source}`);
        const rangeKor = new RegExp(`${apRe.source}\s*부터\s*${apRe.source}\s*까지`);
        // 9시부터 5시 (까지 생략)도 허용
        const rangeKor2 = new RegExp(`${apRe.source}\s*부터\s*${apRe.source}(?:\s*까지)?`);
        let m = value.match(rangeKor) || value.match(rangeKor2) || value.match(rangeTo) || value.match(rangeRe);
        // 키워드 입력: 유연근무/자율근무/재택 등
        if (/유연근무|자율근무|플렉스|재택|원격/i.test(text)) {
          return ok('유연근무');
        }
        let sH, sM, eH, eM;
        if (m) {
          const sh = ampm(m[2], m[1]);
          const sm = m[3] || '00';
          const ehRaw = parseInt(m[5], 10);
          let eh = ampm(m[5], m[4]);
          const em = m[6] || '00';
          // 9-6 형태 보정: 종료가 1~12 사이이고 AM/PM 미지정이며 시작보다 작으면 +12 혹은 18으로 간주
          if (!m[4] && sh !== undefined && ehRaw <= 12 && eh <= 12 && eh < sh) {
            eh = eh + 12;
          }
          sH = String(sh).padStart(2, '0');
          sM = String(sm).padStart(2, '0');
          eH = String(eh).padStart(2, '0');
          eM = String(em).padStart(2, '0');
          return ok(`${sH}:${sM} ~ ${eH}:${eM}`);
        }
        // 1000~2000
        const hhmm = /(\d{3,4})\s*[~\-]\s*(\d{3,4})/;
        const m2 = text.match(hhmm);
        if (m2) {
          const a = m2[1].padStart(4, '0');
          const b = m2[2].padStart(4, '0');
          return ok(`${a.slice(0,2)}:${a.slice(2)} ~ ${b.slice(0,2)}:${b.slice(2)}`);
        }
        return fail(`${exampleForField.workHours}`);
      }
      case 'workDays': {
        let v = value.replace(/\s+/g, '');
        if (/주중|평일/.test(v)) return ok('월~금');
        if (/주말/.test(v)) return ok('토~일');
        if (/주5일|주오일/.test(v)) return ok('월~금');
        if (/주6일|주소육일/.test(v)) return ok('월~토');
        const re = /(월|화|수|목|금|토|일)[~\-](월|화|수|목|금|토|일)/;
        if (re.test(v)) return ok(v.replace('-', '~'));
        return fail(`${exampleForField.workDays}`);
      }
      case 'salary': {
        if (/협의/.test(value)) return ok('협의');
        const nums = value.replace(/[,\s]/g, '').match(/\d+/g);
        if (!nums) return fail(`${exampleForField.salary}`);
        if (nums.length === 1) return ok(`${nums[0]}만원`);
        return ok(`${nums[0]} ~ ${nums[1]}만원`);
      }
      case 'locationCity': {
        const re = /^[가-힣A-Za-z\s]{2,20}$/;
        if (!re.test(value)) return fail(`${exampleForField.locationCity}`);
        return ok(value.replace(/\s+/g, ''));
      }
      case 'deadline': {
        const t = value.trim();
        const norm = (d) => {
          const y = d.getFullYear();
          const m = String(d.getMonth()+1).padStart(2,'0');
          const da = String(d.getDate()).padStart(2,'0');
          return `${y}-${m}-${da}`;
        };
        // yyyy-mm-dd / yyyy.mm.dd / yyyy/mm/dd
        let m = t.match(/^(\d{4})[\-\/.](\d{1,2})[\-\/.](\d{1,2})$/);
        if (m) {
          const d = new Date(parseInt(m[1],10), parseInt(m[2],10)-1, parseInt(m[3],10));
          return ok(norm(d));
        }
        // mm-dd / mm.dd / mm/dd (올해)
        m = t.match(/^(\d{1,2})[\-\/.](\d{1,2})$/);
        if (m) {
          const today = new Date();
          const d = new Date(today.getFullYear(), parseInt(m[1],10)-1, parseInt(m[2],10));
          return ok(norm(d));
        }
        // 12월31일 / 9월 21일까지
        m = t.match(/^(\d{1,2})\s*월\s*(\d{1,2})\s*일(?:\s*까지)?$/);
        if (m) {
          const today = new Date();
          const d = new Date(today.getFullYear(), parseInt(m[1],10)-1, parseInt(m[2],10));
          return ok(norm(d));
        }
        // 오늘/내일/모레
        if (/오늘/.test(t)) return ok(norm(new Date()));
        if (/내일/.test(t)) { const d = new Date(); d.setDate(d.getDate()+1); return ok(norm(d)); }
        if (/모레/.test(t)) { const d = new Date(); d.setDate(d.getDate()+2); return ok(norm(d)); }
        return fail(`${exampleForField.deadline}`);
      }
      case 'experience': {
        const re = /(신입|무관|\d+\s*년)/;
        if (!re.test(value)) return fail(`${exampleForField.experience}`);
        return ok(value.replace(/\s+/g, ''));
      }
      case 'mainDuties': {
        if (value.length < 5) return fail(`${exampleForField.mainDuties}`);
        return ok(value);
      }
      default:
        // 알 수 없는 필드는 비어있지만 않으면 통과
        if (value.length < 2) return fail('두 글자 이상 입력해주세요.');
        return ok(value);
    }
  }, []);

  // 필드 별 한국어/동의어 키워드
  const fieldSynonyms = {
    mainDuties: ['주요업무', '담당업무', '업무', '업무내용', 'job', 'duties'],
    workHours: ['근무시간', '근무 시각', '근무시각', '근무시간대', 'work hours'],
    workDays: ['근무요일', '근무 요일', '주간 근무', 'work days', '주중', '주말'],
    salary: ['연봉', '급여', '연봉수준', '급여수준', '연봉액', '연봉(만원)'],
    department: ['부서', '팀', '소속'],
    experience: ['경력', '신입/경력', '경력사항'],
    locationCity: ['지역', '근무지', '근무지역', '근무장소', '위치', '근무 위치'],
    headcount: ['인원', '채용인원', 'TO', '명채용', '명', '모집인원', '인원수'],
    workType: ['근무형태', '고용형태', '근무 형태'],
    contactEmail: ['이메일', '메일', '연락처', '연락처 이메일', 'contact email', 'contactEmail'],
    deadline: ['마감일', '접수마감', '지원마감', '마감 날짜', '마감일자', 'deadline'],
    location: ['근무지', '근무지역', '지역', '근무 위치', 'location'],
    position: ['직무', '직무명', '포지션', '직책', '채용포지션', 'position']
  };

  const detectFieldFromText = useCallback((text) => {
    if (!text) return null;
    const normalized = String(text).replace(/\s+/g, '').toLowerCase();
    for (const [field, synonyms] of Object.entries(fieldSynonyms)) {
      if (synonyms.some((kw) => normalized.includes(kw.replace(/\s+/g, '').toLowerCase()))) {
        return field;
      }
    }
    return null;
  }, []);

  const extractTargetFieldFromCommand = useCallback((text) => {
    if (!text) return null;
    // "연봉 적용", "주요업무 반영" 같은 패턴 우선 탐지
    for (const [field, synonyms] of Object.entries(fieldSynonyms)) {
      for (const syn of synonyms) {
        const pattern = new RegExp(`${syn.replace(/[-/\\^$*+?.()|[\]{}]/g, '')}\s*(을|를|로)?\s*(적용|반영|입력|넣|써)`, 'i');
        if (pattern.test(text)) return field;
      }
    }
    return detectFieldFromText(text);
  }, [detectFieldFromText]);

  const isApplyCommand = useCallback((text) => {
    if (!text) return false;
    const t = String(text).replace(/\s+/g, '');
    const patterns = [
      // 기본
      '적용', '적용해줘', '적용해', '적용바람', '모두적용', '전부적용', '전체적용', '다적용', '싱크', '동기화',
      // 입력/반영/넣기/쓰기
      '입력', '입력해줘', '반영', '반영해줘', '넣어줘', '다넣어줘', '폼에넣어줘', '써줘', '그대로써줘', '이대로써줘', '기입', '업데이트', '업뎃', '등록', '저장', '삽입', '붙여넣기', '붙여넣어줘', '페이스트',
      // 그대로/이대로
      '그대로적용', '이대로적용', '그대로반영', '이대로반영', '그대로입력', '이대로입력', '그대로넣어줘', '이대로넣어줘',
      // 전체/모두/전부
      '전체', '모두', '전부',
      // 선택 채택류
      '채택', '이걸로', '이내용으로', '위내용으로', '방금걸로', '방금내용대로'
    ];
    return patterns.some((p) => t.includes(p));
  }, []);

  // 리스트 항목 선택 파서 (예: "1번", "1,3", "1~3", "상위 3개", "3개만", "첫 번째")
  const parseSelectionSpec = useCallback((text, maxLen) => {
    if (!text) return null;
    const result = new Set();
    const t = String(text);

    // 숫자 범위 1~N
    const rangeMatch = t.match(/(\d+)\s*[~\-]\s*(\d+)/);
    if (rangeMatch) {
      const start = Math.max(1, parseInt(rangeMatch[1], 10));
      const end = Math.min(maxLen || Infinity, parseInt(rangeMatch[2], 10));
      for (let i = start; i <= end; i += 1) result.add(i);
    }

    // 콤마 구분 숫자들
    const listMatch = t.match(/\b(\d+(?:\s*,\s*\d+)+)\b/);
    if (listMatch) {
      listMatch[1].split(/\s*,\s*/).forEach((n) => {
        const v = parseInt(n, 10);
        if (!Number.isNaN(v)) result.add(v);
      });
    }

    // "1번", "2번만"
    const singleNumMatch = t.match(/\b(\d+)\s*번/);
    if (singleNumMatch) {
      const v = parseInt(singleNumMatch[1], 10);
      if (!Number.isNaN(v)) result.add(v);
    }

    // 상위/앞/처음 N개, N개만
    const topNMatch = t.match(/(?:상위|앞|처음)\s*(\d+)\s*개|\b(\d+)\s*개만/);
    if (topNMatch) {
      const n = parseInt(topNMatch[1] || topNMatch[2], 10);
      for (let i = 1; i <= Math.min(n, maxLen || n); i += 1) result.add(i);
    }

    // 한글 서수: 첫/두/세/네/다섯
    const ordinalMap = { '첫': 1, '두': 2, '둘': 2, '세': 3, '셋': 3, '네': 4, '다섯': 5 };
    for (const [ord, idx] of Object.entries(ordinalMap)) {
      if (t.includes(`${ord}번째`) || t.includes(`${ord}번째만`) || t.includes(`${ord}째`)) {
        result.add(idx);
      }
    }

    if (result.size === 0) return null;
    return Array.from(result).sort((a, b) => a - b);
  }, []);

  const findLastNonApplyUserMessage = useCallback(() => {
    for (let i = messagesRef.current.length - 1; i >= 0; i -= 1) {
      const msg = messagesRef.current[i];
      if (msg?.type === 'user' && !isApplyCommand(msg.content)) {
        return msg;
      }
    }
    return null;
  }, [isApplyCommand]);

  const findLastBotMessage = useCallback(() => {
    for (let i = messagesRef.current.length - 1; i >= 0; i -= 1) {
      const msg = messagesRef.current[i];
      if (msg?.type === 'bot' && msg?.content) {
        return msg;
      }
    }
    return null;
  }, []);

  // 텍스트 생성 필드 자동 감지 함수
  const detectTextGenerationFields = useCallback(() => {
    const fields = [];
    
    // 동적으로 스캔된 필드들 중에서 텍스트 생성이 필요한 필드 감지
    dynamicFields.forEach(field => {
      const { name, label, placeholder, type } = field;
      
      // 1. textarea 타입은 무조건 텍스트 생성 필드
      if (type === 'textarea') {
        fields.push(name);
        return;
      }
      
      // 2. 라벨/플레이스홀더에서 텍스트 생성 필드 키워드 감지
      const textToCheck = `${label || ''} ${placeholder || ''}`.toLowerCase();
      const generationIndicators = [
        '주요업무', '담당업무', '업무내용', '직무내용', '업무',
        '기타', '추가사항', '복리후생', '복지', '혜택', '부가혜택',
        '자격요건', '우대사항', '경력요건', '지원자격',
        '소개', '설명', '상세내용', '세부사항', '비고',
        '내용', '기타사항', '특이사항', '참고사항'
      ];
      
      if (generationIndicators.some(indicator => textToCheck.includes(indicator))) {
        fields.push(name);
      }
      
      // 3. 필드명 자체에서 감지 (camelCase 고려)
      const fieldNameLower = name.toLowerCase();
      const fieldNamePatterns = [
        'duties', 'duty', 'task', 'job', 'work', 'responsibility',
        'additional', 'extra', 'benefit', 'welfare', 'perk',
        'requirement', 'qualification', 'skill', 'experience',
        'description', 'detail', 'content', 'info', 'note'
      ];
      
      if (fieldNamePatterns.some(pattern => fieldNameLower.includes(pattern))) {
        fields.push(name);
      }
    });
    
    return [...new Set(fields)]; // 중복 제거
  }, [dynamicFields]);

  // 현재 페이지의 텍스트 생성 필드 목록 (동적으로 감지)
  const TEXT_GENERATION_FIELDS = useMemo(() => detectTextGenerationFields(), [detectTextGenerationFields]);
  
  // 텍스트 생성 요청 키워드
  const TEXT_GENERATION_KEYWORDS = [
    '추천', '추천해줘', '추천해', '알려줘', '제안해줘', '만들어줘',
    '정리해줘', '정리해', '다듬어줘', '다듬어', '정제해줘', '개선해줘',
    '수정해줘', '편집해줘', '보완해줘', '완성해줘', '작성해줘',
    '예시', '샘플', '템플릿', '가이드', '도움말'
  ];

  // 텍스트 생성 필드 요청 감지 (동적 필드 기반)
  const isTextGenerationRequest = useCallback((text, targetField = null) => {
    if (!text) return false;
    const t = String(text).replace(/\s+/g, '').toLowerCase();
    
    // 키워드 포함 여부 확인
    const hasGenerationKeyword = TEXT_GENERATION_KEYWORDS.some(keyword => t.includes(keyword));
    if (!hasGenerationKeyword) return false;
    
    // 특정 필드 지정되었을 때
    if (targetField && TEXT_GENERATION_FIELDS.includes(targetField)) {
      return true;
    }
    
    // 동적으로 스캔된 필드들의 라벨과 매칭 확인
    const mentionedField = dynamicFields.find(field => {
      const { label, placeholder, name } = field;
      const fieldTexts = [label, placeholder, name].filter(Boolean);
      
      return fieldTexts.some(fieldText => {
        const fieldTextLower = String(fieldText).toLowerCase();
        // 부분 매칭 (예: "주요업무" in "주요업무를 알려줘")
        return t.includes(fieldTextLower) || fieldTextLower.includes(t.split(/[을를이가]/)[0]);
      });
    });
    
    // 언급된 필드가 텍스트 생성 필드인지 확인
    return mentionedField && TEXT_GENERATION_FIELDS.includes(mentionedField.name);
  }, [TEXT_GENERATION_KEYWORDS, TEXT_GENERATION_FIELDS, dynamicFields]);

  // 주요업무 추천 의도 감지 (자율모드 보완용) - 기존 호환성 유지
  const isDutiesRecommendationRequest = useCallback((text) => {
    if (!text) return false;
    const t = String(text).replace(/\s+/g, '').toLowerCase();
    return (t.includes('주요업무') || t.includes('담당업무') || t.includes('업무')) && (t.includes('추천') || t.includes('추천해줘'));
  }, []);

  // 대화 기록에서 부서명 추출
  const extractDepartmentFromHistory = useCallback(() => {
    // formData에서 먼저 확인
    if (formData?.department) return formData.department;
    
    // 메시지 기록에서 부서명 추출 시도
    for (let i = messagesRef.current.length - 1; i >= 0; i--) {
      const msg = messagesRef.current[i];
      if (msg?.type === 'user') {
        const text = String(msg.content || '').trim();
        // 부서명 패턴 매칭 (기획팀, 개발팀, 영업팀, 마케팅팀 등)
        const deptMatch = text.match(/(기획|개발|영업|마케팅|인사|재무|총무|디자인|운영|고객|품질|생산|연구|전략|사업|기술|서비스|콘텐츠|데이터|AI|보안|법무)팀?/);
        if (deptMatch) return deptMatch[0];
      }
    }
    return null;
  }, [formData]);

  // 텍스트 생성 의도 추출 (추천/정리/다듬기 등)
  const extractGenerationIntent = useCallback((text) => {
    const t = String(text).replace(/\s+/g, '').toLowerCase();
    
    if (t.includes('추천') || t.includes('제안')) return 'recommendation';
    if (t.includes('정리') || t.includes('정제')) return 'organize';
    if (t.includes('다듬') || t.includes('개선') || t.includes('보완')) return 'improve';
    if (t.includes('수정') || t.includes('편집')) return 'edit';
    if (t.includes('완성') || t.includes('작성')) return 'complete';
    if (t.includes('예시') || t.includes('샘플') || t.includes('템플릿')) return 'example';
    
    return 'general';
  }, []);

  // 생성 요청 타입 결정 (동적 필드 기반)
  const getGenerationRequestType = useCallback((fieldName) => {
    if (!fieldName) return 'text_generation';
    
    // 동적 필드에서 해당 필드 찾기
    const field = dynamicFields.find(f => f.name === fieldName);
    if (!field) return 'text_generation';
    
    const { label, placeholder, name } = field;
    const combinedText = `${label || ''} ${placeholder || ''} ${name}`.toLowerCase();
    
    // 필드 타입에 따른 생성 요청 타입 결정
    if (combinedText.includes('주요업무') || combinedText.includes('담당업무') || combinedText.includes('duties')) {
      return 'main_duties_generation';
    }
    if (combinedText.includes('기타') || combinedText.includes('복리후생') || combinedText.includes('additional')) {
      return 'additional_info_generation';
    }
    if (combinedText.includes('자격요건') || combinedText.includes('경력') || combinedText.includes('requirement')) {
      return 'requirement_generation';
    }
    if (combinedText.includes('소개') || combinedText.includes('설명') || combinedText.includes('description')) {
      return 'description_generation';
    }
    
    return 'text_generation';
  }, [dynamicFields]);

  // 업데이트(변경/수정/설정) 명령 감지 및 파싱
  const isUpdateCommand = useCallback((text) => {
    if (!text) return false;
    const raw = String(text);
    const t = raw.replace(/\s+/g, '');
    const verbs = ['변경', '수정', '바꿔', '바꾸', '업데이트', '설정', '세팅'];
    const hasAssign = /[:=]/.test(raw);
    const hasVerb = verbs.some(v => t.includes(v));
    if (hasAssign || hasVerb) return true;
    // "<필드>는 값" / "<필드>은 값" 형태도 업데이트로 간주
    const allSynonyms = Object.entries(fieldSynonyms).flatMap(([k, arr]) => arr.map(s => ({ key: k, syn: s })));
    const simpleAssign = allSynonyms.some(({ syn }) => new RegExp(`${syn.replace(/[-/\\^$*+?.()|[\]{}]/g, '')}\s*(?:은|는)\s+.+`).test(raw));
    // 이메일 단서: 이메일 주소가 있고 연락처/이메일 키워드가 포함되면 업데이트로 간주
    const looksLikeEmail = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/.test(raw);
    const mentionsEmail = /이메일|메일|연락처|contact\s*email|contactEmail/i.test(raw);
    return simpleAssign || (looksLikeEmail && mentionsEmail);
  }, [fieldSynonyms]);

  const extractValueForField = useCallback((text, fieldKey) => {
    if (!text) return null;
    const quoted = text.match(/["']([\s\S]+?)["']/);
    if (quoted) return quoted[1].trim();

    const t = String(text);
    // 이메일 전용
    if (fieldKey === 'contactEmail') {
      const email = t.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/);
      if (email) return email[0];
    }
    if (fieldKey === 'headcount') {
      const m = t.match(/(\d+)\s*명/);
      if (m) return `${m[1]}명`;
      const m2 = t.match(/(?:인원|인원수|채용인원)\s*[:=]?\s*(\d+)/);
      if (m2) return `${m2[1]}명`;
    }
    if (fieldKey === 'salary') {
      const m = t.match(/([0-9][0-9,]*)\s*(만원|원|억)?/);
      if (m) return m[2] ? `${m[1]}${m[2]}` : m[1];
    }
    // 일반: 필드 동의어 다음부터 변경/수정 동사 전까지 추출
    const synonyms = fieldSynonyms[fieldKey] || [];
    for (const syn of synonyms) {
      const synEsc = syn.replace(/[-/\\^$*+?.()|[\]{}]/g, '');
      const re = new RegExp(`${synEsc}\s*(?:은|는|를|을|의)?\s*([\uAC00-\uD7A3A-Za-z0-9:;,.\-_/\s]+?)\s*(?:으로|로)?\s*(?:변경|수정|바꿔|바꾸|업데이트|설정|세팅)`, 'i');
      const m = t.match(re);
      if (m && m[1]) return m[1].trim();
      // 동사가 없는 단순 할당: "<동의어>는 값" / "<동의어>: 값" / "<동의어>=값"
      const reSimple = new RegExp(`${synEsc}\s*(?:은|는|:|=)\s*([\uAC00-\uD7A3A-Za-z0-9@.:;,.\-_/\s]+)`, 'i');
      const ms = t.match(reSimple);
      if (ms && ms[1]) return ms[1].trim();
    }
    // 할당식 키:값
    const fieldName = Object.keys(fieldSynonyms).find(k => k === fieldKey);
    if (fieldName) {
      const re2 = new RegExp(`${fieldName}\s*[:=]\s*([\uAC00-\uD7A3A-Za-z0-9:;,.\-_/\s]+)`, 'i');
      const m = t.match(re2);
      if (m && m[1]) return m[1].trim();
    }
    return null;
  }, [fieldSynonyms]);

  // 추천 메시지 설정
  useEffect(() => {
    setSuggestions([
      '회사 소개를 입력해주세요',
      '채용 포지션을 알려주세요',
      '근무 조건을 설명해주세요',
      '자격 요건을 알려주세요',
      '복리후생을 설명해주세요',
      '지원 방법을 알려주세요'
    ]);
  }, []);

  // 룰셋 로딩 (채용세트 기준) - 번들에 포함된 JSON 사용
  useEffect(() => {
    (async () => {
      const loaded = await loadRules(rulesConfig);
      setRules(loaded);
    })();
  }, []);
  const messagesEndRef = useRef(null);
  const messagesRef = useRef([]);
  const inputRef = useRef(null);
  
  // 세션 기반 히스토리 관리 함수들
  const saveMessagesToSession = useCallback((messagesToSave) => {
    try {
      const sessionKey = `aiChatbot_messages_${sessionId}`;
      const dataToSave = {
        messages: messagesToSave,
        timestamp: Date.now(),
        pageId: pageId,
        sessionId: sessionId
      };
      sessionStorage.setItem(sessionKey, JSON.stringify(dataToSave));
      console.log(`[EnhancedModalChatbot] 메시지 저장 완료: ${messagesToSave.length}개 메시지`);
    } catch (error) {
      console.warn('[EnhancedModalChatbot] 메시지 저장 실패:', error);
    }
  }, [sessionId, pageId]);
  
  const loadMessagesFromSession = useCallback(() => {
    try {
      const sessionKey = `aiChatbot_messages_${sessionId}`;
      const savedData = sessionStorage.getItem(sessionKey);
      
      if (savedData) {
        const parsedData = JSON.parse(savedData);
        
        // 24시간 이내의 메시지만 복원 (86400000ms = 24시간)
        const isRecent = (Date.now() - parsedData.timestamp) < 86400000;
        const isSamePage = parsedData.pageId === pageId;
        
        if (isRecent && isSamePage && parsedData.messages) {
          console.log(`[EnhancedModalChatbot] 세션 메시지 복원: ${parsedData.messages.length}개 메시지`);
          
          // timestamp를 Date 객체로 변환
          const messagesWithDateTimestamp = parsedData.messages.map(msg => ({
            ...msg,
            timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
          }));
          
          return messagesWithDateTimestamp;
        } else {
          console.log('[EnhancedModalChatbot] 세션 메시지가 만료되었거나 다른 페이지입니다');
          // 만료된 데이터 제거
          sessionStorage.removeItem(sessionKey);
        }
      }
      
      return [];
    } catch (error) {
      console.warn('[EnhancedModalChatbot] 메시지 복원 실패:', error);
      return [];
    }
  }, [sessionId, pageId]);
  
  const clearSessionHistory = useCallback(() => {
    try {
      // 현재 세션의 메시지 삭제
      const sessionKey = `aiChatbot_messages_${sessionId}`;
      sessionStorage.removeItem(sessionKey);
      
      // 세션 ID도 삭제하여 완전히 초기화
      sessionStorage.removeItem('aiChatbot_sessionId');
      
      console.log('[EnhancedModalChatbot] 세션 히스토리 및 세션 ID 완전 삭제 완료');
    } catch (error) {
      console.warn('[EnhancedModalChatbot] 세션 히스토리 클리어 실패:', error);
    }
  }, [sessionId]);

  // messages 상태가 변경될 때마다 ref 업데이트 및 세션 저장
  useEffect(() => {
    messagesRef.current = messages;
    
    // 메시지가 있고 AI 어시스턴트가 열려있을 때만 저장
    if (messages.length > 0 && isOpen) {
      saveMessagesToSession(messages);
    }
  }, [messages, isOpen, saveMessagesToSession]);

  const scrollToBottom = useCallback(() => {
    // AI 어시스턴트 내부의 메시지 컨테이너에서만 스크롤 처리
    const messagesContainer = document.querySelector('.enhanced-modal-chatbot-messages-container');
    if (messagesContainer) {
      // 즉시 스크롤 (부드러운 스크롤 제거로 성능 향상)
      messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'auto'
      });
    }
  }, []);

  useEffect(() => {
    // 새로운 메시지가 추가될 때만 스크롤 처리 (디바운싱 적용)
    if (messages.length > 0) {
      const timer = setTimeout(() => scrollToBottom(), 100); // 지연 시간 단축
      return () => clearTimeout(timer);
    }
  }, [messages.length, scrollToBottom]); // messages 전체 대신 length만 감지

  // AI 응답 후 자동으로 입력 영역에 포커스 (최적화된 버전)
  useEffect(() => {
    if (!isLoading && messages.length > 0) {
      // 마지막 메시지가 AI 응답인 경우에만 포커스
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.type === 'bot') {
        // 단순화된 포커스 로직 (한 번만 시도)
        setTimeout(() => {
          if (inputRef.current) {
            try {
              inputRef.current.focus();
              console.log('[EnhancedModalChatbot] 입력창 포커스 성공');
            } catch (e) {
              console.warn('[EnhancedModalChatbot] 입력창 포커스 실패:', e);
            }
          }
        }, 100); // 지연 시간 단축
      }
    }
  }, [messages.length, isLoading]); // messages 전체 대신 length만 감지

  // AI 어시스턴트 자동 호출 이벤트 리스너
  useEffect(() => {
    const handleOpenAIAssistant = (event) => {
      console.log('[EnhancedModalChatbot] AI 어시스턴트 자동 호출 이벤트 수신:', event.detail);
      
      if (event.detail.trigger === 'registration_keyword') {
        // 등록 관련 키워드로 호출된 경우
        setShowModeSelector(true);
        setSelectedAIMode(null);
        setMessages([]);
        setFilledFields({});
        setCurrentField(null);
        
        // 초기 메시지 설정
        const initialMessage = {
          type: 'bot',
          content: '채용공고 등록을 위해 AI 어시스턴트를 시작합니다! 🚀\n\n어떤 방식으로 진행하시겠어요?',
          timestamp: new Date()
        };
        setMessages([initialMessage]);
      }
    };

    const handleCloseEnhancedModalChatbot = () => {
      console.log('[EnhancedModalChatbot] 강제 닫기 이벤트 수신');
      
      // 모든 상태 완전 초기화
      setMessages([]);
      setInputValue('');
      setIsLoading(false);
      setIsFinalizing(false);
      setShowModeSelector(true);
      setSelectedAIMode(null);
      setSelectedDirection(null);
      setShowDirectionChoice(true);
      setFilledFields({});
      setCurrentField(null);
      
      // 대화 순서 상태 초기화
      setConversationOrder({
        currentStep: 0,
        totalSteps: 8,
        completedFields: new Set(),
        isOrderBroken: false
      });
      
      // 세션 히스토리 완전 삭제
      clearSessionHistory();
      
      // 랭그래프 모드일 때는 채용공고 등록 도우미도 함께 닫기
      if (selectedAIMode === 'langgraph' || pageId === 'langgraph_recruit_form') {
        console.log('[EnhancedModalChatbot] 랭그래프 모드 감지 - 채용공고 등록 도우미도 함께 닫기');
        // 랭그래프 채용공고 등록 도우미 닫기 이벤트 발생
        window.dispatchEvent(new CustomEvent('closeLangGraphRegistration'));
      }
      
      // 모달 닫기
      onClose();
      
      console.log('[EnhancedModalChatbot] 강제 닫기 완료');
    };

    const handleForceLangGraphMode = () => {
      console.log('[EnhancedModalChatbot] 랭그래프 모드 강제 설정 이벤트 수신');
      
      // 랭그래프 모드 강제 설정
      setSelectedAIMode('langgraph');
      setShowModeSelector(false);
      
      const langGraphMessage = {
        type: 'bot',
        content: '🧪 LangGraph 모드가 강제로 설정되었습니다!\n\nLangGraph 기반 Agent 시스템으로 다양한 도구를 자동으로 선택하여 답변합니다.\n\n다음과 같은 요청을 해보세요:\n• "최신 개발 트렌드 알려줘" (검색)\n• "연봉 4000만원의 월급" (계산)\n• "저장된 채용공고 보여줘" (DB 조회)\n• "안녕하세요" (일반 대화)',
        timestamp: new Date(),
        id: `mode-langgraph-force-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      };
      
      setMessages([langGraphMessage]);
      
      console.log('[EnhancedModalChatbot] 랭그래프 모드 강제 설정 완료');
    };

    window.addEventListener('openAIAssistant', handleOpenAIAssistant);
    window.addEventListener('closeEnhancedModalChatbot', handleCloseEnhancedModalChatbot);
    window.addEventListener('forceLangGraphMode', handleForceLangGraphMode);
    
    return () => {
      window.removeEventListener('openAIAssistant', handleOpenAIAssistant);
      window.removeEventListener('closeEnhancedModalChatbot', handleCloseEnhancedModalChatbot);
      window.removeEventListener('forceLangGraphMode', handleForceLangGraphMode);
    };
  }, [onClose, clearSessionHistory]);

  // 초기 AI 모드 설정
  useEffect(() => {
    if (isOpen && initialAIMode && !selectedAIMode) {
      console.log('[EnhancedModalChatbot] 초기 AI 모드 설정:', initialAIMode);
      
      // 랭그래프 모드인 경우 특별 처리
      if (initialAIMode === 'langgraph') {
        console.log('[EnhancedModalChatbot] 랭그래프 모드 자동 설정');
        setSelectedAIMode('langgraph');
        setShowModeSelector(false);
        
        const langGraphMessage = {
          type: 'bot',
          content: '🧪 LangGraph 모드가 자동으로 시작되었습니다!\n\nLangGraph 기반 Agent 시스템으로 다양한 도구를 자동으로 선택하여 답변합니다.\n\n다음과 같은 요청을 해보세요:\n• "최신 개발 트렌드 알려줘" (검색)\n• "연봉 4000만원의 월급" (계산)\n• "저장된 채용공고 보여줘" (DB 조회)\n• "안녕하세요" (일반 대화)',
          timestamp: new Date(),
          id: `mode-langgraph-auto-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        };
        
        setMessages([langGraphMessage]);
        return;
      }
      
      // 다른 모드들도 자동 설정
      setSelectedAIMode(initialAIMode);
      setShowModeSelector(false);
      
      const modeMessages = {
        'individual_input': {
          type: 'bot',
          content: '📝 개별입력모드가 자동으로 시작되었습니다!\n\n각 필드를 하나씩 순서대로 입력받겠습니다.\n\n먼저 구인 부서를 알려주세요.',
          timestamp: new Date(),
          id: `mode-individual_input-auto-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        },
        'autonomous': {
          type: 'bot', 
          content: '🤖 자율모드가 자동으로 시작되었습니다!\n\n채용공고에 필요한 모든 정보를 한 번에 말씀해주세요.\n\n예: "인천에서 개발팀 2명을 뽑으려고 해요. 9시부터 6시까지 근무하고 연봉은 4000만원이에요"',
          timestamp: new Date(),
          id: `mode-autonomous-auto-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        },
        'ai_assistant': {
          type: 'bot',
          content: '💬 AI 어시스턴트 모드가 자동으로 시작되었습니다!\n\n채용공고 작성에 대해 자유롭게 대화하세요.\n\n어떤 도움이 필요하신가요?',
          timestamp: new Date(),
          id: `mode-ai_assistant-auto-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        },
        'test_mode': {
          type: 'bot',
          content: '🧪 테스트중 모드가 자동으로 시작되었습니다!\n\nLangGraph 기반 Agent 시스템으로 다양한 도구를 자동으로 선택하여 답변합니다.\n\n다음과 같은 요청을 해보세요:\n• "최신 개발 트렌드 알려줘" (검색)\n• "연봉 4000만원의 월급" (계산)\n• "저장된 채용공고 보여줘" (DB 조회)\n• "안녕하세요" (일반 대화)',
          timestamp: new Date(),
          id: `mode-test_mode-auto-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        }
      };
      
      if (modeMessages[initialAIMode]) {
        setMessages([modeMessages[initialAIMode]]);
      }
    }
  }, [isOpen, initialAIMode, selectedAIMode]);

  // 초기 메시지 설정 (세션 복원이 없을 때만)
  useEffect(() => {
    if (isOpen && messages.length === 0 && showModeSelector && !initialAIMode) {
      const welcomeMessages = {
        'recruit_form': '안녕하세요! 채용 공고 작성을 도와드리겠습니다. 어떤 방식으로 진행하시겠어요?',
        'resume_analysis': '안녕하세요! 이력서 분석을 도와드리겠습니다. 어떤 방식으로 진행하시겠어요?',
        'interview_management': '안녕하세요! 면접 관리를 도와드리겠습니다. 어떤 방식으로 진행하시겠어요?',
        'portfolio_analysis': '안녕하세요! 포트폴리오 분석을 도와드리겠습니다. 어떤 방식으로 진행하시겠어요?',
        'cover_letter_validation': '안녕하세요! 자기소개서 검증을 도와드리겠습니다. 어떤 방식으로 진행하시겠어요?',
        'applicant_management': '안녕하세요! 지원자 관리를 도와드리겠습니다. 어떤 방식으로 진행하시겠어요?'
      };

      setMessages([
        {
          type: 'bot',
          content: welcomeMessages[pageId] || '안녕하세요! AI 어시스턴트가 도와드리겠습니다. 어떤 방식으로 진행하시겠어요?',
          timestamp: new Date(),
          id: 'welcome'
        }
      ]);
      setShowDirectionChoice(true);
      setSelectedDirection(null);
    }
  }, [isOpen, messages.length, pageId, showModeSelector, initialAIMode]);

  // 방향 선택 처리
  const handleDirectionChoice = useCallback((direction) => {
    setSelectedDirection(direction);
    setShowDirectionChoice(false);
    
    const guidedMessages = {
      'recruit_form': '안녕하세요! AI 어시스턴트입니다. 채용공고 작성에 대해 자유롭게 대화해보세요. 단계별로 질문드릴 수도 있고, 자유롭게 대화할 수도 있습니다. 어떤 것이든 물어보세요!',
      'resume_analysis': '안녕하세요! AI 어시스턴트입니다. 이력서 분석에 대해 자유롭게 대화해보세요. 단계별로 질문드릴 수도 있고, 자유롭게 대화할 수도 있습니다. 어떤 것이든 물어보세요!',
      'interview_management': '안녕하세요! AI 어시스턴트입니다. 면접 관리에 대해 자유롭게 대화해보세요. 단계별로 질문드릴 수도 있고, 자유롭게 대화할 수도 있습니다. 어떤 것이든 물어보세요!',
      'portfolio_analysis': '안녕하세요! AI 어시스턴트입니다. 포트폴리오 분석에 대해 자유롭게 대화해보세요. 단계별로 질문드릴 수도 있고, 자유롭게 대화할 수도 있습니다. 어떤 것이든 물어보세요!',
      'cover_letter_validation': '안녕하세요! AI 어시스턴트입니다. 자기소개서 검증에 대해 자유롭게 대화해보세요. 단계별로 질문드릴 수도 있고, 자유롭게 대화할 수도 있습니다. 어떤 것이든 물어보세요!',
      'applicant_management': '안녕하세요! AI 어시스턴트입니다. 지원자 관리에 대해 자유롭게 대화해보세요. 단계별로 질문드릴 수도 있고, 자유롭게 대화할 수도 있습니다. 어떤 것이든 물어보세요!'
    };

    const freeMessages = {
      'recruit_form': '안녕하세요! AI 어시스턴트입니다. 채용공고 작성에 대해 자유롭게 대화해보세요. 자유롭게 입력하시면 AI가 분석하여 폼에 자동으로 입력해드리겠습니다. 어떤 것이든 물어보세요!',
      'resume_analysis': '안녕하세요! AI 어시스턴트입니다. 이력서 분석에 대해 자유롭게 대화해보세요. 자유롭게 입력하시면 AI가 분석하여 결과를 제공해드리겠습니다. 어떤 것이든 물어보세요!',
      'interview_management': '안녕하세요! AI 어시스턴트입니다. 면접 관리에 대해 자유롭게 대화해보세요. 자유롭게 입력하시면 AI가 분석하여 관리 도구에 자동으로 입력해드리겠습니다. 어떤 것이든 물어보세요!',
      'portfolio_analysis': '안녕하세요! AI 어시스턴트입니다. 포트폴리오 분석에 대해 자유롭게 대화해보세요. 자유롭게 입력하시면 AI가 분석하여 결과를 제공해드리겠습니다. 어떤 것이든 물어보세요!',
      'cover_letter_validation': '안녕하세요! AI 어시스턴트입니다. 자기소개서 검증에 대해 자유롭게 대화해보세요. 자유롭게 입력하시면 AI가 분석하여 검증 결과를 제공해드리겠습니다. 어떤 것이든 물어보세요!',
      'applicant_management': '안녕하세요! AI 어시스턴트입니다. 지원자 관리에 대해 자유롭게 대화해보세요. 자유롭게 입력하시면 AI가 분석하여 관리 도구에 자동으로 입력해드리겠습니다. 어떤 것이든 물어보세요!'
    };
    
    let initialMessage = '';
    if (direction === 'guided') {
      initialMessage = guidedMessages[pageId] || '안녕하세요! AI 어시스턴트입니다. 자유롭게 대화해보세요.';
    } else if (direction === 'free') {
      initialMessage = freeMessages[pageId] || '안녕하세요! AI 어시스턴트입니다. 자유롭게 대화해보세요.';
    }
    
    setMessages(prev => [...prev, {
      type: 'bot',
      content: initialMessage,
      timestamp: new Date(),
      id: `direction-${direction}`
    }]);
  }, [pageId]);

  // 모달이 열릴 때 플로팅 챗봇 숨기기
  useEffect(() => {
    if (isOpen) {
      // 플로팅 챗봇 숨기기
      const floatingChatbot = document.querySelector('.floating-chatbot');
      if (floatingChatbot) {
        floatingChatbot.style.display = 'none';
      }

      // 커스텀 이벤트로 플로팅 챗봇에 알림
      window.dispatchEvent(new CustomEvent('hideFloatingChatbot'));
    } else {
      // 모달이 닫힐 때 완전한 상태 초기화
      console.log('=== 모달 닫힘: 완전한 상태 초기화 시작 ===');
      
      // 모든 상태를 확실히 초기화
      setMessages([]);
      setInputValue('');
      setIsLoading(false);
      setIsFinalizing(false);
      setShowModeSelector(true);  // 모드 선택기 다시 보이게
      setSelectedAIMode(null);
      setSelectedDirection(null);
      setShowDirectionChoice(true);
      setFilledFields({});
      setCurrentField(null);
      
      // 대화 순서 상태 초기화
      setConversationOrder({
        currentStep: 0,
        totalSteps: 8,
        completedFields: new Set(),
        isOrderBroken: false
      });
      
      // 세션 히스토리 완전 삭제
      clearSessionHistory();
      
      console.log('=== 모달 닫힘: 완전한 상태 초기화 완료 ===');
      
      // 플로팅 챗봇 다시 보이기
      const floatingChatbot = document.querySelector('.floating-chatbot');
      if (floatingChatbot) {
        floatingChatbot.style.display = 'flex';
      }

      // 커스텀 이벤트로 플로팅 챗봇에 알림
      window.dispatchEvent(new CustomEvent('showFloatingChatbot'));
    }
  }, [isOpen, clearSessionHistory]);

  // 대화종료 타이머 정리
  useEffect(() => {
    return () => {
      if (endChatTimer) {
        clearTimeout(endChatTimer);
      }
    };
  }, [endChatTimer]);

  const handleAIResponse = useCallback(async (userInput) => {
    if (!userInput.trim()) return;

    // 최종 등록 처리 중에는 입력을 큐에 넣지 않고 안내만 표기
    if (isFinalizing) {
      setMessages(prev => [...prev, {
        type: 'bot',
        content: '현재 등록 처리 중입니다. 완료 후 계속 이용해 주세요. ⏳',
        timestamp: new Date(),
        id: `bot-finalizing-warn-${Date.now()}`,
        isInfo: true
      }]);
      return;
    }

    // LangGraph 모드에서 정보 추출 시 LangGraphJobRegistration으로 전달
    console.log('[EnhancedModalChatbot] LangGraph 모드 체크:', selectedAIMode, userInput);
    console.log('[EnhancedModalChatbot] selectedAIMode 타입:', typeof selectedAIMode);
    console.log('[EnhancedModalChatbot] selectedAIMode 값:', JSON.stringify(selectedAIMode));
    console.log('[EnhancedModalChatbot] 조건 확인:', selectedAIMode === 'langgraph');
    if (selectedAIMode === 'langgraph') {
      // LangGraph 모드에서 채용공고 관련 정보 추출 시
      console.log('[EnhancedModalChatbot] LangGraph 모드에서 채용공고 정보 추출 감지');
      
      // 추출된 정보를 LangGraphJobRegistration으로 전달하는 이벤트 발생
      const extractedData = {
        department: '',
        position: '',
        headcount: '',
        experience: '',
        workType: '',
        workHours: '',
        locationCity: '',
        locationDistrict: '',
        salary: '',
        mainDuties: '',
        requirements: '',
        benefits: '',
        contactEmail: '',
        deadline: ''
      };
      
      // AI가 사용자 입력에서 정보를 추출하는 함수
      const extractInfo = (text) => {
        const info = {};
        
        // 직무명 추출
        const positionPatterns = [
          /(프론트엔드\s*개발자|백엔드\s*개발자|풀스택\s*개발자|웹\s*개발자|앱\s*개발자|모바일\s*개발자|시스템\s*개발자|데이터\s*엔지니어|DevOps\s*엔지니어|QA\s*엔지니어|UI\/UX\s*디자이너|그래픽\s*디자이너|기획자|마케터|영업사원|인사담당자|회계담당자|운영담당자)/i,
          /(개발자|프로그래머|엔지니어|매니저|대리|과장|차장|부장|사원|인턴|디자이너|기획자|마케터|영업사원)/i
        ];
        
        for (const pattern of positionPatterns) {
          const match = text.match(pattern);
          if (match) {
            info.position = match[1];
            break;
          }
        }
        
        // 모집인원 추출
        const headcountPatterns = [
          /모집인원[:\s]*(\d+)명/i,
          /채용인원[:\s]*(\d+)명/i,
          /인원[:\s]*(\d+)명/i,
          /(\d+)명\s*(?:모집|채용)/i,
          /(\d+)명/i
        ];
        
        for (const pattern of headcountPatterns) {
          const match = text.match(pattern);
          if (match) {
            info.headcount = match[1] + '명';
            break;
          }
        }
        
        // 경력요건 추출
        if (text.includes('신입/경력') || text.includes('신입 또는 경력')) {
          info.experience = '신입/경력';
        } else if (text.includes('신입')) {
          info.experience = '신입';
        } else if (text.includes('경력')) {
          info.experience = '경력';
        }
        
        // 경력연차 추출
        const experienceYearPatterns = [
          /경력\s*(\d+)\s*년\s*이상/i,
          /(\d+)\s*년\s*이상\s*경력/i,
          /경력\s*(\d+)\s*년/i
        ];
        
        for (const pattern of experienceYearPatterns) {
          const match = text.match(pattern);
          if (match) {
            info.experienceYears = match[1] + '년 이상';
            break;
          }
        }
        
        // 근무형태 추출
        if (text.includes('정규직')) info.workType = '정규직';
        else if (text.includes('계약직')) info.workType = '계약직';
        else if (text.includes('인턴')) info.workType = '인턴';
        else if (text.includes('파트타임')) info.workType = '파트타임';
        
        // 근무시간 추출
        const workHoursPatterns = [
          /(\d{1,2}):(\d{2})\s*~\s*(\d{1,2}):(\d{2})/,
          /(\d{1,2})시\s*~\s*(\d{1,2})시/,
          /근무시간[:\s]*(\d{1,2}):(\d{2})\s*~\s*(\d{1,2}):(\d{2})/i
        ];
        
        for (const pattern of workHoursPatterns) {
          const match = text.match(pattern);
          if (match) {
            if (match[3]) {
              info.workHours = `${match[1]}:${match[2]} ~ ${match[3]}:${match[4]}`;
            } else {
              info.workHours = `${match[1]}시 ~ ${match[2]}시`;
            }
            break;
          }
        }
        
        // 근무요일 추출
        if (text.includes('월~금') || text.includes('월-금') || text.includes('월요일~금요일')) {
          info.workDays = '월~금';
        } else if (text.includes('월~토') || text.includes('월-토') || text.includes('월요일~토요일')) {
          info.workDays = '월~토';
        } else if (text.includes('평일')) {
          info.workDays = '월~금';
        }
        
        // 근무위치 추출
        const locationPatterns = [
          /위치[:\s]*(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)\s*([가-힣]+구?)/i,
          /(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)\s*([가-힣]+구?)/i,
          /(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)/i
        ];
        
        for (const pattern of locationPatterns) {
          const match = text.match(pattern);
          if (match) {
            info.locationCity = match[1];
            if (match[2]) {
              info.locationDistrict = match[2];
            }
            break;
          }
        }
        
        // 급여/연봉 추출
        const salaryPatterns = [
          /연봉[:\s]*(\d+)[천만]원/i,
          /급여[:\s]*(\d+)[천만]원/i,
          /(\d+)[천만]원\s*(?:연봉|급여)/i,
          /(\d+)[천만]원/i
        ];
        
        for (const pattern of salaryPatterns) {
          const match = text.match(pattern);
          if (match) {
            info.salary = match[1] + '만원';
            break;
          }
        }
        
        // 주요업무 추출
        const mainDutiesMatch = text.match(/주요업무[:\s]*([\s\S]*?)(?=\n\n|\n###|\n🎯|\n### 🎯|자격요건|🎯 자격요건)/i);
        if (mainDutiesMatch) {
          info.mainDuties = mainDutiesMatch[1].trim().replace(/^[•\-\*]\s*/gm, '').replace(/\n/g, ' ');
        }
        
        // 자격요건 추출
        const requirementsMatch = text.match(/자격요건[:\s]*([\s\S]*?)(?=\n\n|\n###|\n🌟|\n### 🌟|우대조건|🌟 우대조건)/i);
        if (requirementsMatch) {
          info.requirements = requirementsMatch[1].trim().replace(/^[•\-\*]\s*/gm, '').replace(/\n/g, ' ');
        }
        
        // 복리후생 추출
        const benefitsMatch = text.match(/복리후생[:\s]*([\s\S]*?)(?=\n\n|\n###|\n📞|\n### 📞|지원방법|📞 지원방법)/i);
        if (benefitsMatch) {
          info.benefits = benefitsMatch[1].trim().replace(/^[•\-\*]\s*/gm, '').replace(/\n/g, ' ');
        }
        
        // 연락처 이메일 추출
        const emailMatch = text.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
        if (emailMatch) {
          info.contactEmail = emailMatch[1];
        }
        
        // 마감일 추출
        const deadlinePatterns = [
          /마감일[:\s]*([0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2})/i,
          /마감[:\s]*([0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2})/i,
          /지원마감[:\s]*([0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2})/i
        ];
        
        for (const pattern of deadlinePatterns) {
          const match = text.match(pattern);
          if (match) {
            info.deadline = match[1].replace(/\//g, '-');
            break;
          }
        }
        
        return info;
      };
      
      const extractedInfo = extractInfo(userInput);
      
      // 추출된 정보가 있으면 1초 후 LangGraphJobRegistration으로 전달
      if (Object.keys(extractedInfo).length > 0) {
        console.log('[EnhancedModalChatbot] AI가 추출한 정보:', extractedInfo);
        
        // AI 분석 완료 모달창 표시 (디버깅 포함)
        console.log('[EnhancedModalChatbot] 모달창 생성 시작');
        
        try {
          const analysisModal = document.createElement('div');
          analysisModal.id = 'ai-analysis-modal';
          analysisModal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
          `;
          
          analysisModal.innerHTML = `
            <div style="
              background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
              color: white;
              padding: 40px;
              border-radius: 20px;
              text-align: center;
              max-width: 500px;
              box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            ">
              <div style="font-size: 48px; margin-bottom: 20px;">🤖</div>
              <h2 style="margin: 0 0 20px 0; font-size: 24px; font-weight: 600;">AI 분석 완료</h2>
              <div style="margin-bottom: 20px; font-size: 16px; line-height: 1.6;">
                입력하신 정보에서 다음 항목들을 추출했습니다:
              </div>
              <div style="
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                text-align: left;
                font-size: 14px;
                line-height: 1.5;
              ">
                ${Object.entries(extractedInfo).map(([key, value]) => `• ${key}: ${value}`).join('\n')}
              </div>
              <div style="font-size: 14px; opacity: 0.9;">
                2초 후 채용공고 등록 도우미에 전달됩니다...
              </div>
            </div>
          `;
          
          console.log('[EnhancedModalChatbot] 모달창 요소 생성됨:', analysisModal);
          console.log('[EnhancedModalChatbot] document.body 존재:', !!document.body);
          
          // 모달창을 DOM에 추가
          document.body.appendChild(analysisModal);
          console.log('[EnhancedModalChatbot] 모달창 DOM에 추가됨');
          
          // 모달창이 실제로 표시되는지 확인
          setTimeout(() => {
            const modalElement = document.getElementById('ai-analysis-modal');
            console.log('[EnhancedModalChatbot] 모달창 DOM 확인:', modalElement);
            console.log('[EnhancedModalChatbot] 모달창 스타일:', modalElement ? modalElement.style.cssText : '없음');
            console.log('[EnhancedModalChatbot] 모달창 표시 여부:', modalElement ? window.getComputedStyle(modalElement).display : '없음');
          }, 100);
          
        } catch (error) {
          console.error('[EnhancedModalChatbot] 모달창 생성 중 오류:', error);
          
          // 대안: 간단한 alert로 대체
          alert(`AI 분석 완료!\n\n추출된 정보:\n${Object.entries(extractedInfo).map(([key, value]) => `• ${key}: ${value}`).join('\n')}\n\n2초 후 전달됩니다.`);
        }
        
        // 2초 후 모달창 제거 및 데이터 전달
        setTimeout(() => {
          console.log('[EnhancedModalChatbot] 2초 후 모달창 제거 시작');
          
          // 모달창 제거
          try {
            const modalElement = document.getElementById('ai-analysis-modal');
            console.log('[EnhancedModalChatbot] 제거할 모달창 찾음:', modalElement);
            
            if (modalElement && modalElement.parentNode) {
              modalElement.parentNode.removeChild(modalElement);
              console.log('[EnhancedModalChatbot] 모달창 제거 완료');
            } else {
              console.log('[EnhancedModalChatbot] 모달창이 이미 제거되었거나 찾을 수 없음');
            }
          } catch (error) {
            console.error('[EnhancedModalChatbot] 모달창 제거 중 오류:', error);
          }
          
          console.log('[EnhancedModalChatbot] 2초 후 추출된 정보를 랭그래프 채용공고 등록 도우미에 전달:', extractedInfo);
          
          // 추출된 정보를 LangGraphJobRegistration으로 전달 (준비중 영역을 동적 폼으로 변경)
          const event = new CustomEvent('langGraphDataUpdate', {
            detail: {
              action: 'updateLangGraphData',
              data: extractedInfo  // 추출된 객체 전달
            }
          });
          window.dispatchEvent(event);
          
          // 전달 완료 메시지
          setMessages(prev => [...prev, {
            type: 'bot',
            content: `✅ 추출된 정보가 랭그래프 모드의 채용공고 등록 도우미에 전달되었습니다!\n\n준비중 영역이 동적으로 생성된 제목과 인풋으로 변경되어 각 항목에 자동으로 입력됩니다.`,
            timestamp: new Date(),
            id: `transfer-complete-${Date.now()}`,
            isSuccess: true
          }]);
        }, 2000);
        
        // 정보 추출이 완료되었으므로 여기서 return하여 AI API 요청을 하지 않음
        console.log('[EnhancedModalChatbot] 정보 추출 완료, AI API 요청 건너뛰기');
        return; // 함수 전체 종료
      }
    }
    
    // 여기서부터는 일반적인 AI 응답 처리 (정보 추출이 감지되지 않은 경우)
    console.log('[EnhancedModalChatbot] 일반적인 AI 응답 처리 시작');

    // 사용자 메시지를 먼저 추가
    const userMessage = createMessage('user', userInput);

    // 사용자 메시지를 즉시 UI에 추가
    setMessages(prev => [...prev, userMessage]);

    // 입력값을 클리어하고 로딩 상태 설정
    setInputValue('');
    setIsLoading(true);
    setShowSuggestions(false); // 추천 리스트 닫기

    // 0) 최종 등록 강제 트리거: '작성 완료/작성완료/최종 등록/등록 완료'
    try {
      const finalizeRe = /(작성\s*완료|작성완료|최종\s*등록|등록\s*완료|완료|등록해줘|등록|제출|저장|끝)/i;
      if (finalizeRe.test(userInput)) {
        setMessages(prev => [...prev, createMessage('bot', 
          'AI 어시스턴트를 종료하고 등록완료 버튼을 자동으로 클릭합니다... ✅',
          { isSuccess: true }
        )]);
        setIsLoading(false);
        setIsFinalizing(true);
        
        // 작성완료 시 세션 히스토리 삭제
        clearSessionHistory();
        
        // 1초 후 AI 어시스턴트 모달 닫기
        setTimeout(() => {
          try { 
            onClose(); 
            console.log('[EnhancedModalChatbot] AI 어시스턴트 모달 종료 완료');
          } catch (e) {
            console.error('[EnhancedModalChatbot] AI 어시스턴트 모달 종료 실패:', e);
          }
          
          // AI 어시스턴트 모달이 닫힌 후 등록완료 버튼 자동 클릭
          setTimeout(() => {
            // DOM 상태 디버깅
            console.log('[EnhancedModalChatbot] DOM 상태 디버깅 시작');
            console.log('[EnhancedModalChatbot] 현재 URL:', window.location.href);
            console.log('[EnhancedModalChatbot] 문서 제목:', document.title);
            console.log('[EnhancedModalChatbot] 모든 모달 요소:', document.querySelectorAll('[class*="modal"], [class*="Modal"]').length);
            
            const clickRegistrationButton = (attempt = 1) => {
              if (attempt > 8) {
                console.error('[EnhancedModalChatbot] 등록완료 버튼을 찾을 수 없습니다');
                alert('등록완료 버튼을 찾을 수 없습니다. 수동으로 등록완료 버튼을 클릭해주세요.');
                return;
              }
              
              console.log(`[EnhancedModalChatbot] 등록완료 버튼 클릭 시도 ${attempt}`);
              
              // 모든 버튼 스캔하여 정확한 등록완료 버튼 찾기
              const findRegistrationButton = () => {
                console.log('[EnhancedModalChatbot] 페이지의 모든 버튼 스캔 시작');
                
                // 1. 모든 button 요소 스캔
                const allButtons = document.querySelectorAll('button');
                console.log(`[EnhancedModalChatbot] 총 ${allButtons.length}개의 button 요소 발견`);
                
                for (let i = 0; i < allButtons.length; i++) {
                  const button = allButtons[i];
                  const buttonText = button.textContent?.trim() || '';
                  const className = button.className || '';
                  
                  console.log(`[EnhancedModalChatbot] 버튼 ${i + 1}: 텍스트="${buttonText}", 클래스="${className}"`);
                  
                  // 등록완료 버튼 조건 확인
                  const isRegistrationButton = (
                    buttonText.includes('등록 완료') ||
                    buttonText.includes('등록완료') ||
                    (buttonText.includes('완료') && className.includes('primary')) ||
                    (buttonText.includes('등록') && className.includes('primary'))
                  );
                  
                  if (isRegistrationButton) {
                    console.log(`[EnhancedModalChatbot] 등록완료 버튼 후보 발견: "${buttonText}" (클래스: ${className})`);
                    
                    // 가시성 및 활성화 상태 확인
                    const isVisible = button.offsetParent !== null && 
                                     window.getComputedStyle(button).display !== 'none' && 
                                     window.getComputedStyle(button).visibility !== 'hidden';
                    
                    const isEnabled = !button.disabled;
                    
                    console.log(`[EnhancedModalChatbot] 버튼 상태 - 보임: ${isVisible}, 활성화: ${isEnabled}`);
                    
                    if (isVisible && isEnabled) {
                      return button;
                    }
                  }
                }
                
                // 2. styled-components로 생성된 버튼 찾기 (클래스명이 해시된 경우)
                const styledButtons = document.querySelectorAll('[class*="Button"]');
                console.log(`[EnhancedModalChatbot] styled-components 버튼 ${styledButtons.length}개 추가 스캔`);
                
                for (const button of styledButtons) {
                  const buttonText = button.textContent?.trim() || '';
                  const className = button.className || '';
                  
                  if (buttonText.includes('등록') && buttonText.includes('완료')) {
                    console.log(`[EnhancedModalChatbot] styled-components 등록완료 버튼 발견: "${buttonText}"`);
                    
                    const isVisible = button.offsetParent !== null && 
                                     window.getComputedStyle(button).display !== 'none' && 
                                     window.getComputedStyle(button).visibility !== 'hidden';
                    
                    if (isVisible && !button.disabled) {
                      return button;
                    }
                  }
                }
                
                return null;
              };
              
              const targetButton = findRegistrationButton();
              
              if (targetButton) {
                console.log('[EnhancedModalChatbot] 등록완료 버튼 발견! 클릭 실행:', targetButton);
                
                // 시각적 피드백
                const originalStyle = {
                  background: targetButton.style.background,
                  transform: targetButton.style.transform,
                  boxShadow: targetButton.style.boxShadow
                };
                
                targetButton.style.background = '#10b981';
                targetButton.style.transform = 'scale(1.05)';
                targetButton.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.3)';
                
                setTimeout(() => {
                  targetButton.style.background = originalStyle.background;
                  targetButton.style.transform = originalStyle.transform;
                  targetButton.style.boxShadow = originalStyle.boxShadow;
                }, 300);
                
                // 여러 방법으로 클릭 시도
                try {
                  // 1. 일반 클릭
                  targetButton.click();
                  console.log('[EnhancedModalChatbot] 일반 클릭 완료');
                } catch (e) {
                  console.warn('[EnhancedModalChatbot] 일반 클릭 실패, 이벤트 디스패치 시도:', e);
                  
                  // 2. 마우스 이벤트 시뮬레이션
                  const clickEvent = new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                  });
                  targetButton.dispatchEvent(clickEvent);
                  console.log('[EnhancedModalChatbot] 마우스 이벤트 디스패치 완료');
                }
                
                setIsFinalizing(false);
                return;
              } else {
                console.warn(`[EnhancedModalChatbot] 등록완료 버튼을 찾지 못함 (시도 ${attempt}/${8})`);
                
                // 5번째 시도부터는 대안 방법 사용
                if (attempt >= 5) {
                  console.log('[EnhancedModalChatbot] 대안 방법 시도: onComplete 직접 호출');
                  
                  // formData를 가져와서 onComplete 함수 직접 호출
                  try {
                    // TextBasedRegistration의 formData 상태를 찾아서 가져오기
                    const getAllFormData = () => {
                      // 1. 페이지의 모든 input, textarea, select 요소에서 데이터 수집
                      const formElements = document.querySelectorAll('input, textarea, select');
                      const collectedData = {};
                      
                      formElements.forEach(element => {
                        const name = element.name || element.id;
                        const value = element.value?.trim();
                        
                        if (name && value) {
                          collectedData[name] = value;
                          console.log(`[EnhancedModalChatbot] 수집된 데이터: ${name} = ${value}`);
                        }
                      });
                      
                      return collectedData;
                    };
                    
                    const currentFormData = getAllFormData();
                    console.log('[EnhancedModalChatbot] 수집된 formData:', currentFormData);
                    
                    // onTitleRecommendation이 있으면 제목 추천 모달 열기, 없으면 기존 onComplete 호출
                    if (onTitleRecommendation && typeof onTitleRecommendation === 'function') {
                      console.log('[EnhancedModalChatbot] 제목 추천 모달 열기');
                      onTitleRecommendation(currentFormData);
                      setIsFinalizing(false);
                      return;
                    } else if (onComplete && typeof onComplete === 'function') {
                      console.log('[EnhancedModalChatbot] onComplete 함수 직접 호출');
                      onComplete(currentFormData);
                      setIsFinalizing(false);
                      return;
                    } else {
                      console.warn('[EnhancedModalChatbot] onTitleRecommendation 또는 onComplete 함수를 찾을 수 없음');
                    }
                  } catch (error) {
                    console.error('[EnhancedModalChatbot] onComplete 직접 호출 실패:', error);
                  }
                }
              }
              
              // 재시도 (더 긴 대기 시간)
              setTimeout(() => clickRegistrationButton(attempt + 1), 1000);
            };
            
            clickRegistrationButton();
          }, 500);
        }, 1000);
        
        return;
      }
    } catch (e) {
      console.error('[EnhancedModalChatbot] 작성완료 처리 중 오류:', e);
    }

    // 적용/입력 명령은 서버 호출 없이 로컬에서 처리
    try {
      if (isApplyCommand(userInput)) {
        const lastUserMsg = findLastNonApplyUserMessage();
        const lastBotMsg = findLastBotMessage();

        // 대상 필드 추론: 최근 사용자 메시지 → 최근 봇 메시지 → currentField
        let targetField = extractTargetFieldFromCommand(userInput) ||
          detectFieldFromText(lastUserMsg?.content) ||
          detectFieldFromText(lastBotMsg?.content) ||
          currentField;

        // 현재 단계 잠금(Strict) 모드: '수정/변경/바꿔' 등 명시적 업데이트 동사가 없으면
        // 반드시 현재 질문 중인 필드에만 적용
        const hasUpdateVerb = /(수정|수정해줘|변경|변경해줘|바꿔|바꿔줘|바꾸|바꿔주세요|업데이트|설정|세팅)/.test(userInput);
        const strictLock = selectedAIMode === 'individual_input' && currentField && !hasUpdateVerb;
        if (strictLock) {
          targetField = currentField;
        }

        // 업무 추천 맥락 기본값
        if (!targetField && lastUserMsg && /업무|추천/.test(lastUserMsg.content)) {
          targetField = 'mainDuties';
        }

        // 최근 봇 메시지가 복리후생/기타항목 추천이면 대상 필드를 강제로 additionalInfo로 설정
        if (!strictLock && lastBotMsg && /복리후생|기타\s*항목|benefit|welfare/i.test(String(lastBotMsg.content))) {
          targetField = 'additionalInfo';
        }

        if (!targetField) {
          const failMessage = {
            type: 'bot',
            content: '어떤 항목에 적용할지 알 수 없습니다. 예: "주요업무 적용"처럼 말씀해 주세요.',
            timestamp: new Date(),
            id: `bot-applyfail-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
          };
          setMessages(prev => [...prev, failMessage]);
          setIsLoading(false);
          return;
        }

        // 마지막 봇 응답에서 리스트/섹션 내용 추출
        const extractListFromText = (text) => {
          if (!text) return '';
          const lines = String(text).split('\n');
          const listLines = lines.filter((ln) => /^(\s*[0-9]+\.\s+|\s*[-*•]\s+)/.test(ln.trim()));
          if (listLines.length > 0) return listLines.join('\n');
          const idx = lines.findIndex((ln) => /담당업무|주요업무|복리후생|기타\s*항목/.test(ln));
          if (idx >= 0) return lines.slice(idx + 1).join('\n').trim();
          return text.trim();
        };

        // 따옴표 지정 값 우선 적용 (예: "..." 또는 '...')
        const quotedMatch = userInput.match(/["']([\s\S]+?)["']/);
        let valueToApply = quotedMatch ? quotedMatch[1].trim() : null;

        // 1) 우선 직전에 매핑된 JSON이 있으면 해당 필드 값 활용 (정확도↑)
        if (!valueToApply) {
          if (lastExtractedJson && targetField in lastExtractedJson) {
            valueToApply = lastExtractedJson[targetField];
          } else {
            // 2) 없으면 마지막 봇 메시지에서 텍스트 추출
            valueToApply = extractListFromText(lastBotMsg?.content || '');
          }
        }

        // 부분 선택/제외 적용 (예: "1,3번만 적용", "2번 제외하고 적용", "상위 3개 적용").
        // 결과는 번호를 1부터 순차 재번호(renumbering)하여 저장
        const listLines = String(valueToApply || '').split('\n').filter((ln) => ln.trim());
        const selection = parseSelectionSpec(userInput, listLines.length);
        const isExcludeMode = /제외|빼고|빼서|제하고/.test(userInput);
        if (selection && listLines.length > 0) {
          if (isExcludeMode) {
            const excludeSet = new Set(selection);
            const picked = listLines.filter((_, i) => !excludeSet.has(i + 1));
          if (picked.length > 0) {
              const renumbered = picked.map((ln, idx) => ln.replace(/^\s*\d+\.\s*/, `${idx+1}. `));
              valueToApply = renumbered.join('\n');
            }
          } else {
            const picked = selection.map((idx) => listLines[idx - 1]).filter(Boolean);
            if (picked.length > 0) {
              const renumbered = picked.map((ln, idx) => ln.replace(/^\s*\d+\.\s*/, `${idx+1}. `));
              valueToApply = renumbered.join('\n');
            }
          }
        }

        if (!valueToApply) {
          const emptyMessage = {
            type: 'bot',
            content: '적용할 내용이 비어 있습니다. 먼저 AI의 제안을 받아주세요.',
            timestamp: new Date(),
            id: `bot-applyempty-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
          };
          setMessages(prev => [...prev, emptyMessage]);
          setIsLoading(false);
          return;
        }

        // 기타항목은 “추천” 표현이 포함되면 라벨을 제거하고 통일된 정리 텍스트로 저장
        let valueForApply = valueToApply;
        if (targetField === 'additionalInfo') {
          const lines = String(valueToApply).split('\n').map((ln) => ln.replace(/^[-*•]\s*/, '').trim());
          const filtered = lines.filter((ln) => ln && !/추천|제안|예시/i.test(ln));
          if (filtered.length > 0) {
            valueForApply = filtered.join('\n');
          }
        }

        if (onFieldUpdate) {
          onFieldUpdate(targetField, valueForApply);
          // 단계 추적 업데이트
          updateCurrentStep(targetField, valueForApply);
        }

        const successMessage = {
          type: 'bot',
          content: `✅ ${fieldDisplayNames[targetField] || targetField} 항목에 적용했습니다.`,
          timestamp: new Date(),
          id: `bot-applied-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          isSuccess: true
        };
        setMessages(prev => [...prev, successMessage]);
        
        // 개별입력 모드라면 다음 필드로 진행 (동적 UI 순서 기준)
        if (selectedAIMode === 'individual_input') {
          const idx = dynamicFields.findIndex((f) => f.name === targetField);
          const nextDynamic = idx >= 0 ? dynamicFields[idx + 1]?.name : null;
          if (nextDynamic) {
            setCurrentField(nextDynamic);
            const prompt = getDynamicPromptFor(nextDynamic) || getPrompt(pageId, nextDynamic);
            if (prompt) {
              setMessages(prev => [...prev, { type: 'bot', content: prompt, timestamp: new Date(), id: `bot-nextprompt-${Date.now()}` }]);
              
              // 다음 질문 필드로 자동 스크롤
              setTimeout(() => {
                const scrollToNextField = (attempt = 1) => {
                  if (attempt > 3) return;
                  
                  const selectors = [
                    `input[name="${nextDynamic}"]:not([type="hidden"]):not([disabled])`,
                    `textarea[name="${nextDynamic}"]:not([disabled])`,
                    `select[name="${nextDynamic}"]:not([disabled])`,
                    `.custom-form-group input[name="${nextDynamic}"]:not([type="hidden"]):not([disabled])`,
                    `.custom-form-group textarea[name="${nextDynamic}"]:not([disabled])`,
                    `#${nextDynamic}:not([type="hidden"]):not([disabled])`
                  ];
                  
                  for (const sel of selectors) {
                    const elements = document.querySelectorAll(sel);
                    for (const el of elements) {
                      const isVisible = el.offsetParent !== null && 
                                       window.getComputedStyle(el).display !== 'none' && 
                                       window.getComputedStyle(el).visibility !== 'hidden';
                      
                      if (el && isVisible) {
                        console.log(`[EnhancedModalChatbot] 다음 질문 필드 스크롤: ${nextDynamic}`);
                        
                        // 부드러운 스크롤로 해당 필드로 이동
                        el.scrollIntoView({ 
                          behavior: 'smooth', 
                          block: 'center',
                          inline: 'nearest'
                        });
                        
                        // 시각적 강조 (포커싱 없이)
                        const originalBorder = el.style.border;
                        const originalBoxShadow = el.style.boxShadow;
                        el.style.border = '2px solid #10b981';
                        el.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.2)';
                        
                        setTimeout(() => {
                          el.style.border = originalBorder;
                          el.style.boxShadow = originalBoxShadow;
                        }, 2000);
                        
                        return true;
                      }
                    }
                  }
                  
                  // 재시도
                  setTimeout(() => scrollToNextField(attempt + 1), 200 * attempt);
                  return false;
                };
                
                scrollToNextField();
              }, 600); // 메시지가 추가된 후 스크롤
            }
          } else {
            // 더 물을 항목이 없으면 마무리 안내
            setMessages(prev => [...prev, { type: 'bot', content: '필수 항목 입력이 완료되었습니다. 필요한 항목을 더 말씀해 주세요.', timestamp: new Date(), id: `bot-finish-${Date.now()}`, isInfo: true }]);
          }
        }
        setIsLoading(false);
        return;
      }

      // 키:값 업데이트 명령 처리 (개별/자율 공통)
      if (isUpdateCommand(userInput) || /(수정|수정해줘|변경|변경해줘|바꿔|바꿔줘|바꾸|바꿔주세요)/.test(userInput)) {
        // 1) 어떤 필드를 말하는지 추정
        const mentionedField = extractTargetFieldFromCommand(userInput) || detectFieldFromText(userInput);
        if (mentionedField && onFieldUpdate) {
          let newValue = extractValueForField(userInput, mentionedField);
          // '<필드> <값>으로 (수정|변경|바꿔)' 패턴 보강
          if (!newValue) {
            const synonyms = fieldSynonyms[mentionedField] || [mentionedField];
            const synGroup = synonyms.map(s => s.replace(/[-/\\^$*+?.()|[\]{}]/g, '')).join('|');
            const m = userInput.match(new RegExp(`(?:${synGroup})\s*(?:을|를)?\s*([\uAC00-\uD7A3A-Za-z0-9\s]+?)\s*으로\s*(?:수정|변경|바꿔|바꾸)`, 'i'));
            if (m && m[1]) newValue = m[1].trim();
          }
          if (newValue) {
            onFieldUpdate(mentionedField, newValue);
            // 단계 추적 업데이트
            updateCurrentStep(mentionedField, newValue);
            // 업데이트된 필드로 스크롤 이동
            setTimeout(() => {
              const nameToScroll = mentionedField;
              const tryScroll = (attempt = 1) => {
                console.log(`[EnhancedModalChatbot] 스크롤 시도 ${attempt}: ${nameToScroll}`);
                
                // 더 포괄적인 셀렉터 목록 (우선순위 순)
                const selectors = [
                  // 정확한 name 속성
                  `input[name="${nameToScroll}"]:not([type="hidden"]):not([disabled])`,
                  `textarea[name="${nameToScroll}"]:not([disabled])`,
                  `select[name="${nameToScroll}"]:not([disabled])`,
                  // 폼 그룹 내 name 속성
                  `.custom-form-group input[name="${nameToScroll}"]:not([type="hidden"]):not([disabled])`,
                  `.custom-form-group textarea[name="${nameToScroll}"]:not([disabled])`,
                  `.custom-form-group select[name="${nameToScroll}"]:not([disabled])`,
                  `.form-group input[name="${nameToScroll}"]:not([type="hidden"]):not([disabled])`,
                  `.form-group textarea[name="${nameToScroll}"]:not([disabled])`,
                  // ID 기반
                  `#${nameToScroll}:not([type="hidden"]):not([disabled])`,
                  // 클래스 기반
                  `.${nameToScroll}:not([type="hidden"]):not([disabled])`,
                  // data 속성 기반
                  `[data-field="${nameToScroll}"]:not([type="hidden"]):not([disabled])`,
                  `[data-name="${nameToScroll}"]:not([type="hidden"]):not([disabled])`,
                  // 플레이스홀더 기반 (부분 매칭)
                  `input[placeholder*="${nameToScroll}"]:not([type="hidden"]):not([disabled])`,
                  `textarea[placeholder*="${nameToScroll}"]:not([disabled])`
                ];
                
                for (const sel of selectors) {
                  try {
                    const elements = document.querySelectorAll(sel);
                    console.log(`[EnhancedModalChatbot] 셀렉터 "${sel}": ${elements.length}개 요소 발견`);
                    
                    for (const el of elements) {
                      // 요소가 화면에 보이는지 확인
                      const isVisible = el.offsetParent !== null && 
                                       window.getComputedStyle(el).display !== 'none' && 
                                       window.getComputedStyle(el).visibility !== 'hidden';
                      
                      if (el && isVisible) {
                        console.log(`[EnhancedModalChatbot] 스크롤 성공: "${sel}"`, el);
                        
                        // 화면 스크롤 (포커싱 없이)
                        el.scrollIntoView({ 
                          behavior: 'smooth', 
                          block: 'center',
                          inline: 'nearest'
                        });
                        
                        // 시각적 하이라이트 효과
                        const originalBorder = el.style.border;
                        const originalBoxShadow = el.style.boxShadow;
                        const originalTransition = el.style.transition;
                        
                        el.style.transition = 'all 0.3s ease';
                        el.style.border = '2px solid #667eea';
                        el.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.2)';
                        
                        setTimeout(() => {
                          el.style.border = originalBorder;
                          el.style.boxShadow = originalBoxShadow;
                          el.style.transition = originalTransition;
                        }, 2000);
                        
                        return true;
                      }
                    }
                  } catch (error) {
                    console.warn(`[EnhancedModalChatbot] 셀렉터 "${sel}" 처리 중 오류:`, error);
                  }
                }
                return false;
              };
              
              // 다중 시도로 안정성 향상
              const maxAttempts = 3;
              const attemptWithRetry = (currentAttempt = 1) => {
                if (currentAttempt > maxAttempts) {
                  console.warn(`[EnhancedModalChatbot] ${maxAttempts}번의 스크롤 시도 모두 실패: ${nameToScroll}`);
                  return;
                }
                
                if (!tryScroll(currentAttempt)) {
                  const delay = currentAttempt * 150; // 점진적 지연
                  console.log(`[EnhancedModalChatbot] 스크롤 실패, ${delay}ms 후 재시도 (${currentAttempt + 1}/${maxAttempts})`);
                  setTimeout(() => attemptWithRetry(currentAttempt + 1), delay);
                }
              };
              
              attemptWithRetry();
            }, 150);
            setMessages(prev => [...prev, {
              type: 'bot',
              content: `✅ ${fieldDisplayNames[mentionedField] || mentionedField} 값을 업데이트했습니다.`,
              timestamp: new Date(),
              id: `bot-updated-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              isSuccess: true
            }]);

            // 개별입력모드라면 다음 프롬프트 이어가기
            if (selectedAIMode === 'individual_input') {
              const idx = dynamicFields.findIndex((f) => f.name === mentionedField);
              const nextDynamic = idx >= 0 ? dynamicFields[idx + 1]?.name : null;
              if (nextDynamic) {
                setCurrentField(nextDynamic);
                const prompt = getDynamicPromptFor(nextDynamic) || getPrompt(pageId, nextDynamic);
                if (prompt) {
                  setMessages(prev => [...prev, { type: 'bot', content: prompt, timestamp: new Date(), id: `bot-nextprompt-${Date.now()}` }]);
                  
                  // 다음 질문 필드로 자동 스크롤
                  setTimeout(() => {
                    const scrollToNextField = (attempt = 1) => {
                      if (attempt > 3) return;
                      
                      const selectors = [
                        `input[name="${nextDynamic}"]:not([type="hidden"]):not([disabled])`,
                        `textarea[name="${nextDynamic}"]:not([disabled])`,
                        `select[name="${nextDynamic}"]:not([disabled])`,
                        `.custom-form-group input[name="${nextDynamic}"]:not([type="hidden"]):not([disabled])`,
                        `.custom-form-group textarea[name="${nextDynamic}"]:not([disabled])`,
                        `#${nextDynamic}:not([type="hidden"]):not([disabled])`
                      ];
                      
                      for (const sel of selectors) {
                        const elements = document.querySelectorAll(sel);
                        for (const el of elements) {
                          const isVisible = el.offsetParent !== null && 
                                           window.getComputedStyle(el).display !== 'none' && 
                                           window.getComputedStyle(el).visibility !== 'hidden';
                          
                          if (el && isVisible) {
                            console.log(`[EnhancedModalChatbot] 업데이트 후 다음 질문 필드 스크롤: ${nextDynamic}`);
                            
                            // 부드러운 스크롤로 해당 필드로 이동
                            el.scrollIntoView({ 
                              behavior: 'smooth', 
                              block: 'center',
                              inline: 'nearest'
                            });
                            
                            // 시각적 강조 (포커싱 없이)
                            const originalBorder = el.style.border;
                            const originalBoxShadow = el.style.boxShadow;
                            el.style.border = '2px solid #10b981';
                            el.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.2)';
                            
                            setTimeout(() => {
                              el.style.border = originalBorder;
                              el.style.boxShadow = originalBoxShadow;
                            }, 2000);
                            
                            return true;
                          }
                        }
                      }
                      
                      // 재시도
                      setTimeout(() => scrollToNextField(attempt + 1), 200 * attempt);
                      return false;
                    };
                    
                    scrollToNextField();
                  }, 500);
                }
              }
            }

            setIsLoading(false);
            return;
          }
        }
      }

      // 맥락 분류 → 룰셋 키워드 매칭 → 액션 힌트
      try {
        const ctx = await classifyContext(userInput);
        setCurrentContext(ctx);
        const ctxRules = getRulesForContext(rules, ctx);
        if (ctxRules && matchKeywords(userInput, ctxRules.keywords)) {
          // 필요 시 ctxRules.action 분기 처리 가능
          // 현 단계에서는 job_posting 맥락이면 폼 입력 보조 강화 등에 활용 가능
        }
      } catch (e) {
        console.warn('[EnhancedModalChatbot] 맥락 분류 실패:', e);
      }

      // 개별입력모드: 현재 요청된 필드가 있고 입력이 질문형이 아니면 바로 반영 (서버 호출과 병행)
      const questionLike = (() => {
        const t = String(userInput).trim();
        if (t.endsWith('?')) return true;
        const qPatterns = ['뭐야', '무엇', '어떻게', '어떤', '알려줘', '설명해줘', '추천해줘', '예시', '어디', '언제', '왜', '몇', '가능해', '가능한가', '궁금'];
        const nt = t.replace(/\s+/g, '');
        return qPatterns.some((p) => nt.includes(p));
      })();

      if (
        selectedAIMode === 'individual_input' &&
        currentField &&
        onFieldUpdate &&
        !questionLike &&
        // 요청/추천/추가 지시 문구가 포함되면 값 적용을 보류하고 답변 모드로 전환
        !/(추천|추천해|알려줘|보여줘|제안|예시|리스트|목록|골라줘|뽑아줘|추려줘|추가해줘|추가해|추가|더해줘|더넣어줘|두개만|몇개|적당한|수정|수정해줘|변경|변경해줘|바꿔|바꿔줘|바꾸|바꿔주세요)/.test(userInput)
      ) {
        // 유효성 검사
        const validation = validateFieldValue(currentField, userInput.trim());
        if (process.env.NODE_ENV !== 'production') {
          // eslint-disable-next-line no-console
          console.debug('[EnhancedModalChatbot] validation', { field: currentField, value: userInput.trim(), validation });
        }

        if (!validation.isValid) {
          setMessages(prev => [...prev, { type: 'bot', content: `입력값이 올바르지 않습니다. ${validation.errorMessage}`, timestamp: new Date(), id: `bot-validate-fail-${Date.now()}`, isInfo: true }]);
          setIsLoading(false);
          return;
        }

        onFieldUpdate(currentField, validation.normalizedValue || userInput.trim());
        setFilledFields(prev => ({ ...prev, [currentField]: userInput.trim() }));
        setMessages(prev => [...prev, { type: 'bot', content: `✅ ${(fieldDisplayNames[currentField] || currentField)}에 입력했습니다.`, timestamp: new Date(), id: `bot-individual-applied-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`, isSuccess: true }]);

        // 다음 필드로 진행: 현재 페이지에서 스캔된 UI 기반 목록 사용
        const idx = dynamicFields.findIndex((f) => f.name === currentField);
        const nextDynamic = idx >= 0 ? dynamicFields[idx + 1]?.name : null;
        if (nextDynamic) {
          setCurrentField(nextDynamic);
          const prompt = getDynamicPromptFor(nextDynamic) || getPrompt(pageId, nextDynamic);
          if (prompt) {
            setMessages(prev => [...prev, { type: 'bot', content: prompt, timestamp: new Date(), id: `bot-nextprompt-${Date.now()}` }]);
            
            // 다음 질문 필드로 자동 스크롤
            setTimeout(() => {
              const scrollToNextField = (attempt = 1) => {
                if (attempt > 3) return;
                
                console.log(`[EnhancedModalChatbot] 개별입력 모드 - 다음 필드 스크롤 시도 ${attempt}: ${nextDynamic}`);
                
                const selectors = [
                  `input[name="${nextDynamic}"]:not([type="hidden"]):not([disabled])`,
                  `textarea[name="${nextDynamic}"]:not([disabled])`,
                  `select[name="${nextDynamic}"]:not([disabled])`,
                  `.custom-form-group input[name="${nextDynamic}"]:not([type="hidden"]):not([disabled])`,
                  `.custom-form-group textarea[name="${nextDynamic}"]:not([disabled])`,
                  `#${nextDynamic}:not([type="hidden"]):not([disabled])`
                ];
                
                for (const sel of selectors) {
                  const elements = document.querySelectorAll(sel);
                  for (const el of elements) {
                    const isVisible = el.offsetParent !== null && 
                                     window.getComputedStyle(el).display !== 'none' && 
                                     window.getComputedStyle(el).visibility !== 'hidden';
                    
                    if (el && isVisible) {
                      console.log(`[EnhancedModalChatbot] 개별입력 모드 - 다음 필드 스크롤 성공: ${nextDynamic}`);
                      
                      // 부드러운 스크롤로 해당 필드로 이동
                      el.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center',
                        inline: 'nearest'
                      });
                      
                      // 시각적 강조 (포커싱 없이)
                      const originalBorder = el.style.border;
                      const originalBoxShadow = el.style.boxShadow;
                      el.style.border = '2px solid #10b981';
                      el.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.2)';
                      
                      setTimeout(() => {
                        el.style.border = originalBorder;
                        el.style.boxShadow = originalBoxShadow;
                      }, 2000);
                      
                      return true;
                    }
                  }
                }
                
                // 재시도
                setTimeout(() => scrollToNextField(attempt + 1), 200 * attempt);
                return false;
              };
              
              scrollToNextField();
            }, 500);
          }
        } else {
          // 더 물을 항목이 없으면 안내만 남기고 종료
          setMessages(prev => [...prev, { type: 'bot', content: '필수 항목 입력이 완료되었습니다. 계속 입력하시려면 항목을 말씀해주세요.', timestamp: new Date(), id: `bot-finish-${Date.now()}`, isInfo: true }]);
        }
        // 서버 호출로 인한 추가 질문 충돌 방지: 여기서 종료
        setIsLoading(false);
        return;
      }
    } catch (applyError) {
      console.error('[EnhancedModalChatbot] 적용 명령 처리 중 오류:', applyError);
      const errorResponse = {
        type: 'bot',
        content: '적용 처리 중 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date(),
        id: `error-apply-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      };
      setMessages(prev => [...prev, errorResponse]);
      setIsLoading(false);
      return;
    }

    try {
      // 개별입력 모드에서 현재 필드 입력 중에는 서버 호출로 인한 불필요한 추가 질문을 막는다
      const isQuestionLike = (() => {
        const t = String(userInput).trim();
        if (t.endsWith('?')) return true;
        const qPatterns = [
          '뭐야','무엇','어떻게','어떤','알려줘','설명해줘','추천','추천해줘','예시','보여줘','리스트','목록','골라줘','뽑아줘','추려줘',
          '추가','추가해줘','추가해','더해줘','더넣어줘','두개','몇개','적당한','원해','필요'
        ];
        const nt = t.replace(/\s+/g, '');
        return qPatterns.some((p) => nt.includes(p));
      })();
      if (selectedAIMode === 'individual_input' && currentField && !isQuestionLike) {
        return; // 프론트 시퀀스만 사용
      }

      // LangGraph 모드인 경우 새로운 API 서비스 사용
      let data;
      
      if (selectedAIMode === 'langgraph') {
        console.log('[EnhancedModalChatbot] LangGraph 모드 API 호출 시작');
        try {
          const response = await LangGraphApiService.callLangGraphAgent(
            userInput,
            messagesRef.current.map(msg => ({
              role: msg.type === 'user' ? 'user' : 'assistant',
              content: msg.content
            })),
            sessionId
          );
          
          data = {
            type: 'langgraph_response',
            content: response.response,
            intent: response.intent,
            confidence: response.confidence,
            extracted_fields: response.extracted_fields || {}
          };
          
          console.log('[EnhancedModalChatbot] LangGraph 응답:', data);
        } catch (error) {
          console.error('[EnhancedModalChatbot] LangGraph API 오류:', error);
          throw error;
        }
      } else if (selectedAIMode === 'test_mode') {
        if (process.env.NODE_ENV !== 'production') {
          console.log('[EnhancedModalChatbot] 테스트 모드 API 요청 시작:', `${API_BASE_URL}/api/chatbot/test-mode-chat`);
        }
        
        const testResponse = await fetch(`${API_BASE_URL}/api/chatbot/test-mode-chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_input: userInput,
            conversation_history: messagesRef.current.map(msg => ({
              role: msg.type === 'user' ? 'user' : 'assistant',
              content: msg.content
            }))
          })
        });

        if (!testResponse.ok) {
          const errorText = await testResponse.text();
          console.error('[EnhancedModalChatbot] 테스트중 모드 서버 응답 오류:', testResponse.status, errorText);
          throw new Error(`테스트중 모드 서버 오류: ${testResponse.status} - ${errorText}`);
        }

        data = await testResponse.json();
        console.log('[EnhancedModalChatbot] 테스트중 모드 AI 응답:', data);
      } else {
        if (process.env.NODE_ENV !== 'production') {
          console.log('[EnhancedModalChatbot] 일반 모드 API 요청 시작:', `${API_BASE_URL}/api/chatbot/chat`);
        }
        
        const response = await fetch(`${API_BASE_URL}/api/chatbot/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json; charset=utf-8',
          },
          body: JSON.stringify({
            user_input: userInput,
            conversation_history: messagesRef.current.map(msg => ({
              role: msg.type === 'user' ? 'user' : 'assistant',
              content: msg.content
            })),
            selected_direction: selectedDirection,
            form_data: formData,
            page: pageId,
            mode: selectedAIMode || 'normal',  // 선택된 AI 모드 사용
            // 텍스트 생성 요청 시 부서 정보 및 필드 타입 명시적 전달
            context_hints: isTextGenerationRequest(userInput, currentField) ? {
              department: formData?.department || extractDepartmentFromHistory(),
              current_field: currentField,
              field_type: TEXT_GENERATION_FIELDS.includes(currentField) ? 'text_generation' : 'normal',
              request_type: getGenerationRequestType(currentField),
              generation_intent: extractGenerationIntent(userInput)
            } : undefined
          })
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error('[EnhancedModalChatbot] 서버 응답 오류:', response.status, errorText);
          throw new Error(`서버 오류: ${response.status} - ${errorText}`);
        }

        data = await response.json();
        console.log('[EnhancedModalChatbot] 일반 모드 AI 응답:', data);
      }
      
      console.log('[EnhancedModalChatbot] AI 응답:', data);

      // 텍스트 생성 요청 시 타깃 필드별 처리 강화
      if ((selectedAIMode === 'autonomous' || selectedAIMode === 'ai_assistant') && isTextGenerationRequest(userInput, currentField)) {
        data.type = data.type || 'ai_assistant';  // autonomous_collection 대신 ai_assistant 사용
        
        // 동적 필드에 따른 타깃 데이터 설정
        const targetField = dynamicFields.find(f => f.name === currentField);
        if (targetField) {
          const { label, name } = targetField;
          const fieldKey = label || name || currentField;
          
          data.extracted_data = {
            ...(data.extracted_data || {}),
            [fieldKey]: data.extracted_data?.[fieldKey] || 
                       data.extracted_data?.[name] || 
                       data.content || 
                       `생성된 ${label || name}을(를) 적용해보세요`
          };
        }
      }

      // 랭그래프 모드 응답 처리
      if (selectedAIMode === 'langgraph' && data.type === 'langgraph_response') {
        console.log('[EnhancedModalChatbot] 랭그래프 모드 응답 처리:', data);
        // 랭그래프 응답은 그대로 표시
      }

      // AI 응답 메시지 구성
      const contentText = data.content || data.message || (data.type === 'langgraph_response' ? data.content : '');
      // 임시 미리보기(샘플) 판단 휴리스틱: 섹션/불릿이 포함된 가이드성 텍스트
      const looksLikePreview = (() => {
        const t = String(contentText || '');
        const norm = t.replace(/\s+/g, '');
        const hasSections = /(주요업무|담당업무|자격요건|우대조건|채용공고|작성가이드|요약)/.test(norm);
        const hasBullets = /(\n\s*[-*•]\s+)|(^|\n)\s*\d+\.\s+/.test(t);
        return hasSections && hasBullets;
      })();

      const aiMessage = {
        type: 'bot',
        content: contentText,
        timestamp: new Date(),
        id: `bot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        responseType: data.response_type || 'conversation',
        selectableItems: data.selectable_items || [],
        suggestions: data.suggestions || [],
        // 미리보기 플래그: 가이드성 텍스트로 보이는 경우 시각적으로 '임시 미리보기'로 표시
        isPreview: looksLikePreview
      };

      // 개별입력모드: 중복/군더더기 메시지 억제 후 일반 메시지 스타일로 표시
        const normalize = (s) => String(s || '').replace(/\s+/g, '').toLowerCase();
      const nContent = normalize(aiMessage.content);

      // 1) 의미 없는 채우기/광범위 안내 문구 제거
      const isFiller = /(?:채용|지원|공고)[^\n]{0,40}?(?:관련|내용|부분)?[^\n]{0,40}?(?:궁금|질문|문의|알고싶)/.test(aiMessage.content || '')
        || /어떤\s*방식으로\s*진행하시겠/ .test(aiMessage.content || '')
        || /어떤\s*도움이\s*필요하신가요/ .test(aiMessage.content || '');
      if (isFiller) {
        // 메시지 추가 없이 무시
      } else {
        // 2) 직전(혹은 최근) 프롬프트와 의미상 동일하면 숨김
        const recentPrompt = (() => {
          for (let i = messagesRef.current.length - 1; i >= 0; i -= 1) {
            const m = messagesRef.current[i];
            if (m?.type === 'bot' && typeof m.id === 'string' && m.id.startsWith('bot-nextprompt-')) {
              return m;
            }
          }
          return null;
        })();

        let isSemanticallyDuplicate = false;
        if (recentPrompt?.content) {
          const np = normalize(recentPrompt.content);
          const keywordPairs = [
            ['직무', '알려'],
            ['포지션', '알려'],
            ['부서', '알려'],
          ];
          const pairHit = keywordPairs.some(([a, b]) => np.includes(a) && np.includes(b) && nContent.includes(a) && nContent.includes(b));
          const exactLike = np === nContent;
          isSemanticallyDuplicate = pairHit || exactLike;
        }

        if (!isSemanticallyDuplicate) {
        setMessages(prevMsgs => [...prevMsgs, aiMessage]);
        }
      }

      // 개별입력모드: 서버 응답으로는 currentField를 바꾸지 않고, 프론트의 시퀀스만 사용

      // autonomous_collection 타입 특별 처리
      if (data.type === 'autonomous_collection') {
        console.log('[EnhancedModalChatbot] 자율모드 응답 감지 - 자동등록 처리 시작');
        console.log('[EnhancedModalChatbot] 추출된 데이터:', data.extracted_data);
        
        // 추출된 데이터가 있으면 폼에 자동 입력
        if (data.extracted_data && onFieldUpdate) {
          console.log('[EnhancedModalChatbot] 추출된 데이터를 폼에 자동 입력');
          
          // 추출된 데이터를 폼 필드에 매핑하여 자동 입력
          const fieldMappings = {
            '부서': 'department',
            '인원': 'headcount', 
            '근무시간': 'workHours',
            '근무요일': 'workDays',
            '연봉': 'salary',
            '업무': 'mainDuties',
            '지역': 'locationCity',
            '경력': 'experience'
          };
          
          // 각 추출된 필드를 해당 폼 필드에 입력
          Object.entries(data.extracted_data).forEach(([key, value]) => {
            const fieldKey = fieldMappings[key];
            if (fieldKey) {
              console.log(`[EnhancedModalChatbot] 필드 자동 입력: ${fieldKey} = ${value}`);
              onFieldUpdate(fieldKey, value);
            }
          });
        }
      }

      // LangGraph 모드에서 추출된 필드 정보 처리
      if (selectedAIMode === 'langgraph' && data.extracted_fields) {
        console.log('[EnhancedModalChatbot] LangGraph 모드에서 추출된 필드 정보 처리:', data.extracted_fields);
        console.log('[EnhancedModalChatbot] extracted_fields 타입:', typeof data.extracted_fields);
        console.log('[EnhancedModalChatbot] extracted_fields 키 개수:', Object.keys(data.extracted_fields).length);
        
        // 추출된 필드 정보를 폼에 자동 입력
        if (onFieldUpdate) {
          Object.entries(data.extracted_fields).forEach(([field, value]) => {
            if (value && value !== '') {
              console.log(`[EnhancedModalChatbot] LangGraph 필드 자동 입력: ${field} = ${value}`);
              onFieldUpdate(field, value);
            }
          });
        }
        
        // LangGraph API 서비스를 통해 필드 업데이트 이벤트 발생 (빈 객체일 경우 텍스트로 폴백 전달)
        console.log('[EnhancedModalChatbot] dispatchFieldUpdate 호출 전:', data.extracted_fields);
        console.log('[EnhancedModalChatbot] 전체 응답 데이터:', data);
        console.log('[EnhancedModalChatbot] extracted_fields 상세:', JSON.stringify(data.extracted_fields, null, 2));
        const hasFields = data.extracted_fields && Object.keys(data.extracted_fields).length > 0;
        if (hasFields) {
          LangGraphApiService.dispatchFieldUpdate(data.extracted_fields);
        } else {
          // 폴백: 문자열 데이터로 전달하면 LangGraphJobRegistration에서 텍스트 분석 후 동적 폼 생성
          const event = new CustomEvent('langGraphDataUpdate', {
            detail: {
              action: 'updateLangGraphData',
              data: userInput
            }
          });
          window.dispatchEvent(event);
          console.log('[EnhancedModalChatbot] 빈 필드 → 사용자 입력 텍스트로 폴백 이벤트 전달');
        }
      } else {
        console.log('[EnhancedModalChatbot] LangGraph 모드가 아니거나 extracted_fields가 없음');
        console.log('[EnhancedModalChatbot] selectedAIMode:', selectedAIMode);
        console.log('[EnhancedModalChatbot] data.extracted_fields:', data.extracted_fields);
        
        // 일반 모드에서의 JSON 필드 매핑 처리
        console.log('[EnhancedModalChatbot] AI 응답 데이터:', data);
        
        // JsonFieldMapper를 사용하여 응답 처리
        const mappingResult = jsonFieldMapper.processChatResponse(
          data, 
          pageId, 
          null, // container는 필요시 추가
          onFieldUpdate
        );
        
        if (mappingResult.success) {
          console.log('[EnhancedModalChatbot] JSON 매핑 성공:', mappingResult.mappedFields);
          if (mappingResult.warnings.length > 0) {
            console.warn('[EnhancedModalChatbot] 매핑 경고:', mappingResult.warnings);
          }
        } else {
          console.log('[EnhancedModalChatbot] JSON 매핑 실패:', mappingResult.message);
        }
      }

      // 마지막 추출 JSON 저장 (적용 명령 시 활용)
      try {
        if (data) {
          const jsonData = jsonFieldMapper.extractJsonFromResponse(data);
          if (jsonData && typeof jsonData === 'object') {
            setLastExtractedJson(jsonData);
          }
        }
      } catch (e) {
        // 무시 (진단 로그만)
        console.warn('[EnhancedModalChatbot] 마지막 JSON 저장 실패:', e);
      }
      
      // 기존 개별 필드 처리 (하위 호환성을 위해 유지)
      if (data.value && data.field && onFieldUpdate) {
        console.log(`[EnhancedModalChatbot] 개별 필드 입력: ${data.field} = ${data.value}`);
        onFieldUpdate(data.field, data.value);
      }
      
      // 추가 질문이 필요한 경우 처리
      if (data.next_question && selectedDirection === 'guided') {
        setTimeout(() => {
          setMessages(prev => [...prev, {
            type: 'bot',
            content: data.next_question,
            timestamp: new Date(),
            id: `next-question-${Date.now()}`
          }]);
        }, 1000);
      }

    } catch (error) {
      console.error('[EnhancedModalChatbot] AI 응답 처리 중 오류:', error);

      // 더 구체적인 오류 메시지 제공
      let errorMessage = '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.';
      
      if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        errorMessage = '서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.';
      } else if (error.message.includes('서버 오류')) {
        errorMessage = `서버 오류가 발생했습니다: ${error.message}`;
      }

      const errorResponse = {
        type: 'bot',
        content: errorMessage,
        timestamp: new Date(),
        id: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      };

      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  }, [onFieldUpdate, selectedDirection, formData, pageId, selectedAIMode, API_BASE_URL]);

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      handleAIResponse(inputValue);
    }
  }, [inputValue, isLoading, handleAIResponse]);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  const handleSuggestionClick = useCallback((suggestion) => {
    setInputValue(suggestion);
    handleAIResponse(suggestion);
  }, [handleAIResponse]);

  const handleItemSelect = useCallback((item) => {
    console.log('[EnhancedModalChatbot] 항목 선택:', item);
    handleAIResponse(item.value || item.label);
  }, [handleAIResponse]);

  const handleQuickSuggestionClick = useCallback((suggestion) => {
    setInputValue(suggestion);
    setShowSuggestions(false);
  }, []);

  const toggleSuggestions = useCallback(() => {
    setShowSuggestions(prev => !prev);
  }, []);

  const handleEndChat = useCallback(() => {
    setShowEndChat(true);
    setCountdown(3);
    
    // 1초마다 카운트다운 (최적화된 버전)
    const countdownInterval = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(countdownInterval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    // 3초 후 자동으로 종료
    const timer = setTimeout(() => {
      // 타이머 정리
      clearInterval(countdownInterval);
      
      // 세션 히스토리 클리어
      clearSessionHistory();
      
      setMessages([]);
      setInputValue('');
      setShowSuggestions(false);
      setShowEndChat(false);
      setCountdown(3);
      setShowDirectionChoice(true);
      setSelectedDirection(null);
      setShowModeSelector(true);
      setSelectedAIMode(null);
      
      // 랭그래프 모드일 때는 채용공고 등록 도우미도 함께 닫기
      if (selectedAIMode === 'langgraph' || pageId === 'langgraph_recruit_form') {
        console.log('[EnhancedModalChatbot] 랭그래프 모드 대화 종료 - 채용공고 등록 도우미도 함께 닫기');
        window.dispatchEvent(new CustomEvent('closeLangGraphRegistration'));
      } else {
        // 플로팅 챗봇 다시 보이기 (기존 모드일 때만)
        const floatingChatbot = document.querySelector('.floating-chatbot');
        if (floatingChatbot) {
          floatingChatbot.style.display = 'flex';
        }
      }
      
      onClose();
    }, 3000);
    
    setEndChatTimer(timer);
  }, [onClose, clearSessionHistory]);

  const handleCancelEndChat = useCallback(() => {
    setShowEndChat(false);
    setCountdown(3);
    if (endChatTimer) {
      clearTimeout(endChatTimer);
      setEndChatTimer(null);
    }
  }, [endChatTimer]);

  // 테스트중 모드 클릭 핸들러
  const handleTestModeClick = () => {
    setSelectedAIMode('test_mode');
    setShowModeSelector(false);
    
    const testModeMessage = {
      type: 'bot',
      content: '🧪 테스트중 모드를 시작합니다!\n\nLangGraph 기반 Agent 시스템으로 다양한 도구를 자동으로 선택하여 답변합니다.\n\n다음과 같은 요청을 해보세요:\n• "최신 개발 트렌드 알려줘" (검색)\n• "연봉 4000만원의 월급" (계산)\n• "저장된 채용공고 보여줘" (DB 조회)\n• "안녕하세요" (일반 대화)',
      timestamp: new Date(),
      id: `mode-test_mode-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
    
    setMessages([testModeMessage]);
    
    // 테스트중 모드 선택 후 입력창에 포커스 (최적화된 버전)
    setTimeout(() => {
      if (inputRef.current) {
        try {
          inputRef.current.focus();
          console.log('[EnhancedModalChatbot] 테스트중 모드 선택 후 입력창 포커스 성공');
        } catch (e) {
          console.warn('[EnhancedModalChatbot] 테스트중 모드 선택 후 입력창 포커스 실패:', e);
        }
      }
    }, 100); // 지연 시간 단축
  };

  // AI 모드 선택 핸들러
  const handleAIModeSelect = (mode) => {
    console.log('[EnhancedModalChatbot] handleAIModeSelect 호출됨, mode:', mode);
    console.log('[EnhancedModalChatbot] onPageAction 존재 여부:', !!onPageAction);
    
    // langgraph 모드는 새로운 LangGraph 등록 창을 열어야 함
    if (mode === 'langgraph') {
      console.log('[EnhancedModalChatbot] LangGraph 모드 선택 - 새로운 창 열기');
      console.log('[EnhancedModalChatbot] onPageAction 타입:', typeof onPageAction);
      
      // 기존 상태 완전 초기화
      setMessages([]);
      setInputValue('');
      setIsLoading(false);
      setIsFinalizing(false);
      setFilledFields({});
      setCurrentField(null);
      setShowDirectionChoice(true);
      setSelectedDirection(null);
      
      // 대화 순서 상태 초기화
      setConversationOrder({
        currentStep: 0,
        totalSteps: 8,
        completedFields: new Set(),
        isOrderBroken: false
      });
      
      // 세션 히스토리 완전 삭제
      clearSessionHistory();
      
      // 플로팅 챗봇에 랭그래프 모드 시작 이벤트 발생
      window.dispatchEvent(new CustomEvent('startLangGraphMode'));
      
      if (onPageAction) {
        console.log('[EnhancedModalChatbot] onPageAction 호출: openLangGraphRegistration');
        onPageAction('openLangGraphRegistration');
      } else {
        console.log('[EnhancedModalChatbot] onPageAction이 정의되지 않음!');
        // Fallback: 직접 이벤트 발생
        console.log('[EnhancedModalChatbot] Fallback: 직접 이벤트 발생');
        const event = new CustomEvent('openLangGraphRegistration');
        window.dispatchEvent(event);
      }
      
      // LangGraph 모드로 설정하고 모달은 그대로 유지
      setSelectedAIMode('langgraph');
      setShowModeSelector(false);
      
      const langGraphMessage = {
        type: 'bot',
        content: '🧪 LangGraph 모드를 시작합니다!\n\n새로운 AI 채용공고 등록 도우미 창이 열렸습니다.\n\n기존 입력값이 모두 초기화되었습니다.\n\nLangGraph 기반 Agent 시스템으로 다양한 도구를 자동으로 선택하여 답변합니다.\n\n다음과 같은 요청을 해보세요:\n• "최신 개발 트렌드 알려줘" (검색)\n• "연봉 4000만원의 월급" (계산)\n• "저장된 채용공고 보여줘" (DB 조회)\n• "안녕하세요" (일반 대화)',
        timestamp: new Date(),
        id: `mode-langgraph-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      };
      
      setMessages([langGraphMessage]);
      
      // LangGraph 모드 선택 후 입력창에 포커스 (최적화된 버전)
      setTimeout(() => {
        if (inputRef.current) {
          try {
            inputRef.current.focus();
            console.log('[EnhancedModalChatbot] LangGraph 모드 선택 후 입력창 포커스 성공');
          } catch (e) {
            console.warn('[EnhancedModalChatbot] LangGraph 모드 선택 후 입력창 포커스 실패:', e);
          }
        }
      }, 100); // 지연 시간 단축
      
      console.log('[EnhancedModalChatbot] LangGraph 모드 처리 완료 - 기존 상태 초기화됨');
      return;
    }
    setSelectedAIMode(mode);
    setShowModeSelector(false);
    
    // 선택된 모드에 따른 초기 메시지 추가
    const modeMessages = {
      'individual_input': {
        type: 'bot',
          content: '📝 개별입력모드를 시작합니다!\n\n각 필드를 하나씩 순서대로 입력받겠습니다.\n\n먼저 구인 부서를 알려주세요.',
        timestamp: new Date(),
        id: `mode-individual_input-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      },
      'autonomous': {
        type: 'bot', 
        content: '🤖 자율모드를 시작합니다!\n\n채용공고에 필요한 모든 정보를 한 번에 말씀해주세요.\n\n예: "인천에서 개발팀 2명을 뽑으려고 해요. 9시부터 6시까지 근무하고 연봉은 4000만원이에요"',
        timestamp: new Date(),
        id: `mode-autonomous-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      },
      'ai_assistant': {
        type: 'bot',
        content: '💬 AI 어시스턴트 모드를 시작합니다!\n\n채용공고 작성에 대해 자유롭게 대화하세요.\n\n어떤 도움이 필요하신가요?',
        timestamp: new Date(),
        id: `mode-ai_assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      },
      'langgraph': {
        type: 'bot',
        content: '💬 LangGraph 모드를 시작합니다!\n\nLangGraph 템플릿에 맞춰 단계별로 질문하여 채용공고를 작성해드리겠습니다.\n\n먼저 구인 부서를 알려주세요.',
        timestamp: new Date(),
        id: `mode-langgraph-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      }
    };
    
    setMessages([modeMessages[mode]]);

    // 개별입력모드 또는 LangGraph 모드 초기 타깃 필드 설정 (폼 시퀀스 기반)
    if (mode === 'individual_input' || mode === 'langgraph') {
      // 동적 필드 우선: 현재 페이지에서 스캔된 필드만 묻기
      const dynamicFirst = dynamicFields[0]?.name;
      if (dynamicFirst) {
        setCurrentField(dynamicFirst);
        const prompt = getDynamicPromptFor(dynamicFirst) || getPrompt(pageId, dynamicFirst) || '먼저 필요한 항목부터 알려주세요.';
        setMessages(prev => [{ type: 'bot', content: prompt, timestamp: new Date(), id: `mode-individual-prompt-${Date.now()}` }]);
      } else {
        // 폴백: 기존 정의 사용
        const first = getInitialField(pageId) || null;
        if (first) {
      setCurrentField(first);
          const firstPrompt = getPrompt(pageId, first) || '먼저 필요한 항목부터 알려주세요.';
        setMessages(prev => [{ type: 'bot', content: firstPrompt, timestamp: new Date(), id: `mode-individual-prompt-${Date.now()}` }]);
        }
      }
    }
    
    // 모드 선택 후 입력창에 포커스
    setTimeout(() => {
      if (inputRef.current) {
        try {
          inputRef.current.focus();
          console.log(`[EnhancedModalChatbot] ${mode} 모드 선택 후 입력창 포커스 성공`);
        } catch (e) {
          console.warn(`[EnhancedModalChatbot] ${mode} 모드 선택 후 입력창 포커스 실패:`, e);
        }
      }
    }, 200);
  };

  // AI 어시스턴트가 열릴 때 상태 초기화 및 세션 복원
  useEffect(() => {
    if (isOpen) {
      // 세션에서 메시지 복원 시도
      const savedMessages = loadMessagesFromSession();
      
      if (savedMessages.length > 0) {
        // 저장된 메시지가 있으면 복원
        console.log('[EnhancedModalChatbot] 세션 메시지 복원 중...', savedMessages.length);
        setMessages(savedMessages);
        
        // 복원된 메시지에서 AI 모드와 현재 필드 추론
        const lastBotMessage = [...savedMessages].reverse().find(msg => msg.type === 'bot');
        if (lastBotMessage) {
          // AI 모드 selector를 건너뛰고 바로 대화 재개
          setShowModeSelector(false);
          
          // 메시지 내용을 분석해서 AI 모드 추론
          if (lastBotMessage.content?.includes('개별입력') || lastBotMessage.content?.includes('순서대로')) {
            setSelectedAIMode('individual_input');
          } else if (lastBotMessage.content?.includes('자율모드') || lastBotMessage.content?.includes('한 번에')) {
            setSelectedAIMode('autonomous');
          } else {
            setSelectedAIMode('ai_assistant');
          }
        }
      } else {
        // 저장된 메시지가 없으면 초기화
        console.log('[EnhancedModalChatbot] 새로운 세션 시작');
        
        // initialAIMode가 설정되어 있으면 자동으로 해당 모드로 시작
        if (initialAIMode) {
          console.log('[EnhancedModalChatbot] initialAIMode로 자동 시작:', initialAIMode);
          setShowModeSelector(false);
          setSelectedAIMode(initialAIMode);
          handleAIModeSelect(initialAIMode);
        } else {
          setShowModeSelector(true);
          setSelectedAIMode(null);
          setMessages([]);
        }
      }
      
      // 공통 상태 초기화
      setFilledFields({});
      setCurrentField(null);
      setInputValue('');
      setIsLoading(false);
      
      // 모달이 완전히 열린 후 입력창에 포커스
      setTimeout(() => {
        if (inputRef.current) {
          try {
            inputRef.current.focus();
            console.log('[EnhancedModalChatbot] 모달 열림 시 입력창 포커스 성공');
          } catch (e) {
            console.warn('[EnhancedModalChatbot] 모달 열림 시 입력창 포커스 실패:', e);
          }
        }
      }, 300);
    }
  }, [isOpen, loadMessagesFromSession]);

  // 모드 선택기로 돌아가기
  const handleBackToModeSelector = () => {
    setShowModeSelector(true);
    setSelectedAIMode(null);
    setMessages([]);
    setFilledFields({});
    setCurrentField(null);
  };

  // 배경 클릭 이벤트 처리
  const handleBackdropClick = (e) => {
    // 배경 클릭 시 닫기가 활성화된 경우에만 처리
    if (closeOnBackdropClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="enhanced-modal-chatbot-overlay"
      onClick={handleBackdropClick}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'transparent',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        zIndex: 1000,
        pointerEvents: closeOnBackdropClick ? 'auto' : 'none' // 배경 클릭 설정에 따라 조정
      }}
    >
      <div
        className="enhanced-modal-chatbot-container"
        style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          position: 'fixed',
          top: '50%',
          right: '24px',
          transform: 'translateY(-50%)', // 화면 중간에 고정
          width: '480px',
          height: '95vh', // 화면 높이의 95%로 고정
          maxWidth: '500px',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
          zIndex: 1001,
          transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
          pointerEvents: 'auto' // AI 어시스턴트 내부는 클릭 가능
        }}
      >

        
        <div
          className="enhanced-modal-chatbot-header"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '24px 32px',
            borderBottom: '1px solid #e2e8f0',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '16px 16px 0 0',
            position: 'relative',
            zIndex: 2
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <h3 className="enhanced-modal-chatbot-title" style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
              AI 어시스턴트
            </h3>
            {/* {messages.length > 0 && (
              <div style={{ fontSize: '12px', opacity: 0.8, marginTop: '2px' }}>
                💾 세션 자동 저장됨 ({messages.length}개 메시지)
              </div>
            )} */}
          </div>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            {/* 모드 선택기로 돌아가기 버튼 (AI 모드가 선택된 경우에만 표시) */}
            {selectedAIMode && !showModeSelector && (
              <button
                onClick={handleBackToModeSelector}
                style={{
                  background: 'rgba(255, 255, 255, 0.2)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  color: 'white',
                  fontSize: '12px',
                  cursor: 'pointer',
                  padding: '6px 12px',
                  borderRadius: '16px',
                  transition: 'all 0.3s ease',
                  fontWeight: '500'
                }}
                onMouseEnter={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.3)'}
                onMouseLeave={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.2)'}
              >
                모드변경
              </button>
            )}
            <button
              className="enhanced-modal-chatbot-end-chat-btn"
              onClick={handleEndChat}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: 'white',
                fontSize: '12px',
                cursor: 'pointer',
                padding: '6px 12px',
                borderRadius: '16px',
                transition: 'all 0.3s ease',
                fontWeight: '500'
              }}
              onMouseEnter={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.3)'}
              onMouseLeave={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.2)'}
            >
              대화종료
            </button>
            <button
              className="enhanced-modal-chatbot-close-btn"
              onClick={() => {
                // 플로팅 챗봇 다시 표시
                const floatingChatbot = document.querySelector('.floating-chatbot');
                if (floatingChatbot) {
                  floatingChatbot.style.display = 'flex';
                }
                // 커스텀 이벤트로 플로팅 챗봇에 알림
                window.dispatchEvent(new CustomEvent('showFloatingChatbot'));
                // 원래 onClose 콜백 호출
                onClose();
              }}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                fontSize: '24px',
                cursor: 'pointer',
                padding: '0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.2)'}
              onMouseLeave={(e) => e.target.style.background = 'none'}
            >
              ×
            </button>
          </div>
        </div>

        <div
          className="enhanced-modal-chatbot-body"
          style={{
            flex: 1,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            zIndex: 2
          }}
        >
          {/* 헤더와 메시지 사이 고정 공지 영역 */}
          <div
            className="enhanced-modal-chatbot-sticky-notice"
            style={{
              position: 'sticky',
              top: 0,
              zIndex: 3,
              background: '#f8fafc',
              borderBottom: '1px solid #e2e8f0',
              color: '#334155',
              padding: '8px 16px',
              fontSize: '12px'
            }}
          >
            {/* Tip: 추천/알려줘/추가 같은 요청 문장은 값으로 저장되지 않습니다. 적용하려면 "1번 적용"처럼 말씀해 주세요. */}
            💡 <strong>유용한 팁:</strong><br></br>
            • 수정이 필요할 경우 예시: "구인 부서 ooo으로 바꿔줘"<br></br>
            • 특정 항목을 선택하고 싶을 때 예시: "구인 부서만 알려줘"<br></br>
            • 최종 등록: "작성완료"를 입력해주세요
            </div>
          {/* 재시작 버튼 및 진행률 표시 */}
          {!showModeSelector && !showDirectionChoice && (
            <ChatbotRestartButton
              onRestart={handleRestartConversation}
              currentStep={conversationOrder.currentStep}
              totalSteps={conversationOrder.totalSteps}
              disabled={isLoading || isFinalizing}
            />
          )}

          <div
            className="enhanced-modal-chatbot-messages-container"
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '20px',
              maxHeight: 'calc(80vh - 100px)', // 헤더와 입력창 높이를 제외한 높이
              position: 'relative',
              zIndex: 2,
              scrollBehavior: 'smooth' // 부드러운 스크롤
            }}
          >
            {/* AI 모드 선택기 표시 */}
            {showModeSelector && (
              <div style={{ marginBottom: '20px' }}>
                <AIModeSelector 
                  onModeSelect={handleAIModeSelect}
                  selectedMode={selectedAIMode}
                  onTestModeClick={handleTestModeClick}
                />
              </div>
            )}
            
            {messages.map((message) => (
              <div
                key={message.id}
                className={`enhanced-modal-chatbot-message enhanced-modal-chatbot-message-${message.type}`}
                style={{
                  marginBottom: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: message.type === 'user' ? 'flex-end' : 'flex-start',
                  position: 'relative',
                  zIndex: 2
                }}
              >
                <div
                  className={`enhanced-modal-chatbot-message-content enhanced-modal-chatbot-message-content-${message.type}`}
                  style={{
                    maxWidth: message.isSuccess || message.isInfo ? '100%' : '70%',
                    padding: message.isSuccess || message.isInfo ? '4px 8px' : '12px 16px',
                    borderRadius: message.isSuccess || message.isInfo ? '0' : '12px',
                    backgroundColor: (message.isSuccess || message.isInfo)
                      ? 'transparent'
                      : (message.type === 'user' ? '#667eea' : '#f3f4f6'),
                    color: (message.isSuccess || message.isInfo)
                      ? '#6b7280'
                      : (message.type === 'user' ? 'white' : '#374151'),
                    fontSize: message.isSuccess || message.isInfo ? '12px' : '14px',
                    lineHeight: message.isSuccess || message.isInfo ? '1.4' : '1.5',
                    position: 'relative',
                    zIndex: 2,
                    whiteSpace: 'pre-line',
                    border: 'none',
                    boxShadow: 'none',
                    // 미리보기는 약한 흐림/워터마크, 일반 답변/사용자 질문 대응은 선명 유지
                    filter: message.isPreview ? 'blur(0.2px)' : 'none',
                    opacity: message.isPreview ? 0.95 : (message.isSuccess || message.isInfo ? 0.9 : 1)
                  }}
                >
                  {/* 워터마크 */}
                  {message.isPreview && (
                    <div style={{
                      position: 'absolute',
                      top: 8,
                      right: 12,
                      fontSize: 11,
                      color: '#9ca3af',
                      textTransform: 'uppercase',
                      letterSpacing: 1,
                      pointerEvents: 'none'
                    }}>
                      임시 미리보기
                    </div>
                  )}
                  {message.content}
                </div>

                {/* 모드 선택 버튼 제거 - AIModeSelector에서 이미 선택함 */}

                {/* 제안사항 표시 */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="enhanced-modal-chatbot-suggestions">
                    {message.suggestions.map((suggestion, index) => (
                      <button
                        key={`${message.id || 'msg'}-suggestion-${index}-${String(suggestion)}`}
                        className={`enhanced-modal-chatbot-suggestion-btn enhanced-modal-chatbot-suggestion-btn-${index}`}
                        onClick={() => handleSuggestionClick(suggestion)}
                        style={{
                          background: '#667eea',
                          color: 'white',
                          border: 'none',
                          padding: '8px 12px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => e.target.style.background = '#5a67d8'}
                        onMouseLeave={(e) => e.target.style.background = '#667eea'}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}

                {/* 선택 가능한 항목들 표시 */}
                {message.selectableItems && message.selectableItems.length > 0 && (
                  <div className="enhanced-modal-chatbot-selectable-items">
                    {message.selectableItems.map((item, index) => (
                      <button
                        key={`${message.id || 'msg'}-item-${index}-${String(item.label || item.value || '')}`}
                        className={`enhanced-modal-chatbot-item-btn enhanced-modal-chatbot-item-btn-${index}`}
                        onClick={() => handleItemSelect(item)}
                        style={{
                          background: '#f3f4f6',
                          color: '#374151',
                          border: '1px solid #d1d5db',
                          padding: '8px 12px',
                          borderRadius: '8px',
                          fontSize: '12px',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          textAlign: 'left'
                        }}
                        onMouseEnter={(e) => e.target.style.background = '#e5e7eb'}
                        onMouseLeave={(e) => e.target.style.background = '#f3f4f6'}
                      >
                        {item.label || item.value}
                      </button>
                    ))}
                  </div>
                )}

                <div
                  className={`enhanced-modal-chatbot-message-timestamp enhanced-modal-chatbot-message-timestamp-${message.type}`}
                  style={{
                    fontSize: '10px',
                    color: '#9ca3af',
                    marginTop: '4px',
                    textAlign: message.type === 'user' ? 'right' : 'left',
                    display: message.isSuccess ? 'none' : 'block'
                  }}
                >
                  {message.timestamp ? (
                    message.timestamp instanceof Date 
                      ? message.timestamp.toLocaleTimeString()
                      : new Date(message.timestamp).toLocaleTimeString()
                  ) : new Date().toLocaleTimeString()}
                </div>
              </div>
            ))}

            {/* 대화종료 메시지 */}
            {showEndChat && (
              <div
                className="enhanced-modal-chatbot-end-chat-message"
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  zIndex: 10000,
                  width: '100%',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center'
                }}
              >
                <div
                  className="enhanced-modal-chatbot-end-chat-content"
                  style={{
                    maxWidth: '400px',
                    width: '90%',
                    padding: '24px 28px',
                    borderRadius: '20px',
                    background: 'linear-gradient(145deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    fontSize: '16px',
                    lineHeight: '1.6',
                    textAlign: 'center',
                    fontWeight: '600',
                    boxShadow: '0 12px 32px rgba(102, 126, 234, 0.25)',
                    position: 'relative',
                    overflow: 'hidden',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}
                >
                  {/* 배경 장식 요소 */}
                  <div style={{
                    position: 'absolute',
                    top: '-20px',
                    right: '-20px',
                    width: '80px',
                    height: '80px',
                    background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
                    borderRadius: '50%',
                    animation: 'pulse 2s infinite'
                  }} />
                  <div style={{
                    position: 'absolute',
                    bottom: '-30px',
                    left: '-30px',
                    width: '60px',
                    height: '60px',
                    background: 'radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%)',
                    borderRadius: '50%',
                    animation: 'pulse 2.5s infinite'
                  }} />
                  
                  <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '12px',
                      marginBottom: '16px'
                    }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'rgba(255, 255, 255, 0.2)',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(255, 255, 255, 0.3)'
                      }}>
                        <span style={{
                          fontSize: '24px',
                          fontWeight: 'bold'
                        }}>⏰</span>
                      </div>
                      <div>
                        <div style={{
                          fontSize: '18px',
                          fontWeight: '700',
                          marginBottom: '4px'
                        }}>
                          대화를 종료합니다
                        </div>
                        <div style={{
                          fontSize: '14px',
                          opacity: '0.9',
                          fontWeight: '400'
                        }}>
                          {countdown}초 후 자동으로 종료됩니다
                        </div>
                      </div>
                    </div>
                    
                    <div style={{
                      display: 'flex',
                      justifyContent: 'center',
                      gap: '16px',
                      marginTop: '20px'
                    }}>
                      <button
                        onClick={handleCancelEndChat}
                        style={{
                          background: 'rgba(255, 255, 255, 0.2)',
                          color: 'white',
                          border: '1px solid rgba(255, 255, 255, 0.3)',
                          padding: '12px 24px',
                          borderRadius: '30px',
                          fontSize: '14px',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          fontWeight: '600',
                          backdropFilter: 'blur(10px)',
                          minWidth: '100px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = 'rgba(255, 255, 255, 0.3)';
                          e.target.style.transform = 'translateY(-2px)';
                          e.target.style.boxShadow = '0 8px 20px rgba(255, 255, 255, 0.2)';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = 'rgba(255, 255, 255, 0.2)';
                          e.target.style.transform = 'translateY(0)';
                          e.target.style.boxShadow = 'none';
                        }}
                      >
                        <span style={{ fontSize: '16px' }}>✋</span>
                        취소
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {isLoading && (
              <div className="enhanced-modal-chatbot-loading-message">
                <div className="enhanced-modal-chatbot-loading-content">
                  <div className="enhanced-modal-chatbot-typing-indicator">
                    <span className="enhanced-modal-chatbot-typing-dot enhanced-modal-chatbot-typing-dot-1"></span>
                    <span className="enhanced-modal-chatbot-typing-dot enhanced-modal-chatbot-typing-dot-2"></span>
                    <span className="enhanced-modal-chatbot-typing-dot enhanced-modal-chatbot-typing-dot-3"></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} className="enhanced-modal-chatbot-messages-end" />
          </div>
        </div>

        {/* 추천 리스트 */}
        {showSuggestions && (
          <div
            className="enhanced-modal-chatbot-quick-suggestions"
            style={{
              padding: '16px 20px',
              borderTop: '1px solid #e2e8f0',
              backgroundColor: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
              maxHeight: '140px',
              overflowY: 'auto',
              transform: 'translateY(0)',
              transition: 'all 0.3s ease',
              boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.1)'
            }}
          >
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '10px'
            }}>
              {suggestions.map((suggestion, index) => (
                <button
                  key={`quick-suggestion-${index}-${String(suggestion)}`}
                  className="enhanced-modal-chatbot-quick-suggestion-btn"
                  onClick={() => handleQuickSuggestionClick(suggestion)}
                  style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: 'none',
                    padding: '12px 16px',
                    borderRadius: '12px',
                    fontSize: '13px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    whiteSpace: 'nowrap',
                    textAlign: 'left',
                    position: 'relative',
                    overflow: 'hidden',
                    boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)',
                    fontWeight: '500',
                    lineHeight: '1.4'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.3)';
                  }}
                >
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
                    pointerEvents: 'none'
                  }} />
                  <span style={{ position: 'relative', zIndex: 1 }}>
                    {suggestion}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        <form
          className="enhanced-modal-chatbot-form"
          onSubmit={handleSubmit}
          style={{
            padding: '20px',
            borderTop: '1px solid #e2e8f0',
            display: 'flex',
            gap: '12px',
            alignItems: 'center'
          }}
        >
          <textarea
            className="enhanced-modal-chatbot-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요..."
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '2px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '14px',
              resize: 'none',
              minHeight: '85px',
              maxHeight: '120px',
              fontFamily: 'inherit'
            }}
            rows="1"
            ref={inputRef}
          />
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
            <button
              type="button"
              onClick={toggleSuggestions}
              style={{
                background: showSuggestions ? '#667eea' : '#f8fafc',
                border: showSuggestions ? 'none' : '1px solid #e2e8f0',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 12px',
                borderRadius: '20px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                color: showSuggestions ? '#ffffff' : '#64748b',
                fontSize: '12px',
                fontWeight: '500',
                boxShadow: showSuggestions ? '0 2px 8px rgba(102, 126, 234, 0.3)' : 'none',
                minWidth: '75px',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => {
                if (!showSuggestions) {
                  e.target.style.background = '#f1f5f9';
                  e.target.style.borderColor = '#cbd5e1';
                }
              }}
              onMouseLeave={(e) => {
                if (!showSuggestions) {
                  e.target.style.background = '#f8fafc';
                  e.target.style.borderColor = '#e2e8f0';
                }
              }}
            >
              <span style={{
                transform: showSuggestions ? 'rotate(0deg)' : 'rotate(180deg)',
                transition: 'transform 0.3s ease',
                fontSize: '10px',
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center'
              }}>
                ▼
              </span>
              <span>
                {showSuggestions ? '닫기' : '추천'}
              </span>
            </button>
            
            <button
              type="submit"
              className="enhanced-modal-chatbot-send-btn"
              disabled={!inputValue.trim() || isLoading}
              style={{
                padding: '12px 25px',
                background: inputValue.trim() && !isLoading ? '#667eea' : '#9ca3af',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: inputValue.trim() && !isLoading ? 'pointer' : 'not-allowed',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                if (inputValue.trim() && !isLoading) {
                  e.target.style.background = '#5a67d8';
                }
              }}
              onMouseLeave={(e) => {
                if (inputValue.trim() && !isLoading) {
                  e.target.style.background = '#667eea';
                }
              }}
            >
              전송
            </button>
          </div>
        </form>
      </div>

      <style>{`
        .enhanced-modal-chatbot-typing-indicator {
          display: flex;
          gap: 4px;
          align-items: center;
        }
        
        .enhanced-modal-chatbot-typing-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #667eea;
        }
        
        .enhanced-modal-chatbot-typing-dot-1 {
          animation: typing 1.4s infinite ease-in-out;
        }
        
        .enhanced-modal-chatbot-typing-dot-2 {
          animation: typing 1.4s infinite ease-in-out 0.2s;
        }
        
        .enhanced-modal-chatbot-typing-dot-3 {
          animation: typing 1.4s infinite ease-in-out 0.4s;
        }
        
        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.4;
          }
          30% {
            transform: translateY(-10px);
            opacity: 1;
          }
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 0.6;
            transform: scale(1.1);
          }
        }
      `}</style>
    </div>
  );
};

export default EnhancedModalChatbot;
