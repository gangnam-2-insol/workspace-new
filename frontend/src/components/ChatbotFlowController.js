import React, { useState, useCallback, useEffect } from 'react';

/**
 * AI 챗봇의 대화 흐름을 안정적으로 관리하는 컨트롤러
 * 순서 꼬임 방지 및 상태 복구 기능 제공
 */
const ChatbotFlowController = ({ 
  sessionId, 
  onFieldUpdate, 
  onStepChange, 
  initialFormData = {} 
}) => {
  // 필드 정의 (고정된 순서)
  const FIELD_SEQUENCE = [
    { key: 'department', label: '구인 부서', type: 'text', required: true },
    { key: 'headcount', label: '채용 인원', type: 'number', required: true },
    { key: 'mainDuties', label: '주요 업무', type: 'textarea', required: true },
    { key: 'workHours', label: '근무 시간', type: 'text', required: false },
    { key: 'locationCity', label: '근무 위치', type: 'text', required: true },
    { key: 'salary', label: '급여 조건', type: 'text', required: false },
    { key: 'experience', label: '경력 요건', type: 'text', required: false },
    { key: 'contactEmail', label: '연락처 이메일', type: 'email', required: true }
  ];

  // 대화 상태 관리
  const [flowState, setFlowState] = useState({
    currentStepIndex: 0,
    completedFields: new Set(),
    pendingValue: null,
    isWaitingForConfirmation: false,
    conversationMode: 'guided', // 'guided' | 'free'
    lastUpdate: Date.now()
  });

  const [fieldValues, setFieldValues] = useState(() => {
    // 초기 데이터가 있으면 완료된 필드로 표시
    const completed = new Set();
    Object.keys(initialFormData).forEach(key => {
      if (initialFormData[key]) {
        completed.add(key);
      }
    });
    return {
      values: { ...initialFormData },
      completedFields: completed
    };
  });

  // 현재 필드 정보 가져오기
  const getCurrentField = useCallback(() => {
    if (flowState.currentStepIndex >= FIELD_SEQUENCE.length) {
      return null; // 모든 필드 완료
    }
    return FIELD_SEQUENCE[flowState.currentStepIndex];
  }, [flowState.currentStepIndex]);

  // 다음 미완성 필드 찾기
  const getNextIncompleteField = useCallback(() => {
    for (let i = flowState.currentStepIndex; i < FIELD_SEQUENCE.length; i++) {
      const field = FIELD_SEQUENCE[i];
      if (!fieldValues.completedFields.has(field.key) || !fieldValues.values[field.key]) {
        return { field, index: i };
      }
    }
    return null; // 모든 필드 완료
  }, [flowState.currentStepIndex, fieldValues]);

  // 순서 재정렬 및 복구
  const recalibrateFlow = useCallback(() => {
    console.log('[FlowController] 순서 재정렬 시작');
    
    // 현재 완료된 필드들 확인
    const actualCompleted = new Set();
    Object.entries(fieldValues.values).forEach(([key, value]) => {
      if (value && value.toString().trim()) {
        actualCompleted.add(key);
      }
    });

    // 다음 진행할 필드 인덱스 계산
    let nextIndex = 0;
    for (let i = 0; i < FIELD_SEQUENCE.length; i++) {
      const field = FIELD_SEQUENCE[i];
      if (!actualCompleted.has(field.key)) {
        nextIndex = i;
        break;
      }
      if (i === FIELD_SEQUENCE.length - 1) {
        nextIndex = FIELD_SEQUENCE.length; // 모든 필드 완료
      } else {
        nextIndex = i + 1;
      }
    }

    setFlowState(prev => ({
      ...prev,
      currentStepIndex: nextIndex,
      completedFields: actualCompleted,
      isWaitingForConfirmation: false,
      pendingValue: null,
      lastUpdate: Date.now()
    }));

    setFieldValues(prev => ({
      ...prev,
      completedFields: actualCompleted
    }));

    console.log('[FlowController] 순서 재정렬 완료 - 다음 인덱스:', nextIndex);
    return nextIndex;
  }, [fieldValues.values]);

  // 필드 값 업데이트
  const updateFieldValue = useCallback((fieldKey, value, confirmed = true) => {
    console.log('[FlowController] 필드 업데이트:', fieldKey, value);

    if (!confirmed) {
      // 확인 대기 상태로 설정
      setFlowState(prev => ({
        ...prev,
        pendingValue: { field: fieldKey, value },
        isWaitingForConfirmation: true,
        lastUpdate: Date.now()
      }));
      return false;
    }

    // 값 확정 및 저장
    setFieldValues(prev => {
      const newValues = { ...prev.values, [fieldKey]: value };
      const newCompleted = new Set(prev.completedFields);
      
      if (value && value.toString().trim()) {
        newCompleted.add(fieldKey);
      } else {
        newCompleted.delete(fieldKey);
      }

      return {
        values: newValues,
        completedFields: newCompleted
      };
    });

    // 외부 핸들러 호출
    if (onFieldUpdate) {
      onFieldUpdate(fieldKey, value);
    }

    // 다음 단계로 진행
    setTimeout(() => {
      const nextStepIndex = recalibrateFlow();
      if (onStepChange) {
        onStepChange({
          currentStepIndex: nextStepIndex,
          currentField: nextStepIndex < FIELD_SEQUENCE.length ? FIELD_SEQUENCE[nextStepIndex] : null,
          isCompleted: nextStepIndex >= FIELD_SEQUENCE.length,
          progress: Math.min(100, (nextStepIndex / FIELD_SEQUENCE.length) * 100)
        });
      }
    }, 100);

    return true;
  }, [onFieldUpdate, onStepChange, recalibrateFlow]);

  // 확인 대기 중인 값 승인
  const confirmPendingValue = useCallback(() => {
    if (!flowState.isWaitingForConfirmation || !flowState.pendingValue) {
      return false;
    }

    const { field, value } = flowState.pendingValue;
    
    setFlowState(prev => ({
      ...prev,
      isWaitingForConfirmation: false,
      pendingValue: null,
      lastUpdate: Date.now()
    }));

    return updateFieldValue(field, value, true);
  }, [flowState.isWaitingForConfirmation, flowState.pendingValue, updateFieldValue]);

  // 확인 대기 중인 값 거부
  const rejectPendingValue = useCallback(() => {
    setFlowState(prev => ({
      ...prev,
      isWaitingForConfirmation: false,
      pendingValue: null,
      lastUpdate: Date.now()
    }));
  }, []);

  // 특정 필드로 이동
  const jumpToField = useCallback((fieldKey) => {
    const fieldIndex = FIELD_SEQUENCE.findIndex(f => f.key === fieldKey);
    if (fieldIndex === -1) return false;

    setFlowState(prev => ({
      ...prev,
      currentStepIndex: fieldIndex,
      isWaitingForConfirmation: false,
      pendingValue: null,
      lastUpdate: Date.now()
    }));

    if (onStepChange) {
      onStepChange({
        currentStepIndex: fieldIndex,
        currentField: FIELD_SEQUENCE[fieldIndex],
        isCompleted: false,
        progress: (fieldIndex / FIELD_SEQUENCE.length) * 100
      });
    }

    return true;
  }, [onStepChange]);

  // 대화 모드 전환
  const switchConversationMode = useCallback((mode) => {
    setFlowState(prev => ({
      ...prev,
      conversationMode: mode,
      lastUpdate: Date.now()
    }));
  }, []);

  // 플로우 리셋
  const resetFlow = useCallback(() => {
    setFlowState({
      currentStepIndex: 0,
      completedFields: new Set(),
      pendingValue: null,
      isWaitingForConfirmation: false,
      conversationMode: 'guided',
      lastUpdate: Date.now()
    });

    setFieldValues({
      values: {},
      completedFields: new Set()
    });
  }, []);

  // 진행률 계산
  const getProgress = useCallback(() => {
    const completed = fieldValues.completedFields.size;
    const total = FIELD_SEQUENCE.length;
    return {
      completed,
      total,
      percentage: Math.round((completed / total) * 100),
      isCompleted: completed === total
    };
  }, [fieldValues.completedFields]);

  // 다음 질문 생성
  const getNextQuestion = useCallback(() => {
    const currentField = getCurrentField();
    
    if (!currentField) {
      return {
        type: 'completion',
        message: '🎉 모든 정보 입력이 완료되었습니다! 등록을 진행하시겠습니까?'
      };
    }

    if (flowState.isWaitingForConfirmation && flowState.pendingValue) {
      return {
        type: 'confirmation',
        message: `"${flowState.pendingValue.value}"로 ${currentField.label}을(를) 설정하시겠습니까?`,
        field: currentField,
        pendingValue: flowState.pendingValue.value
      };
    }

    // 기본 질문 생성
    const examples = {
      department: '예: 개발팀, 기획팀, 마케팅팀',
      headcount: '예: 1명, 2명, 3명',
      mainDuties: '예: 웹 개발, 앱 개발, 시스템 관리',
      workHours: '예: 09:00-18:00, 유연근무',
      locationCity: '예: 서울, 부산, 대구',
      salary: '예: 3000만원, 2500-3500만원',
      experience: '예: 신입, 경력 2년 이상',
      contactEmail: '예: hr@company.com'
    };

    return {
      type: 'question',
      message: `${currentField.label}을(를) 알려주세요.\n${examples[currentField.key] || ''}`,
      field: currentField,
      isRequired: currentField.required
    };
  }, [getCurrentField, flowState.isWaitingForConfirmation, flowState.pendingValue]);

  // 세션 복구
  useEffect(() => {
    if (sessionId && initialFormData && Object.keys(initialFormData).length > 0) {
      console.log('[FlowController] 세션 복구 시도:', initialFormData);
      recalibrateFlow();
    }
  }, [sessionId, initialFormData, recalibrateFlow]);

  return {
    // 상태
    flowState,
    fieldValues: fieldValues.values,
    currentField: getCurrentField(),
    progress: getProgress(),
    
    // 액션
    updateFieldValue,
    confirmPendingValue,
    rejectPendingValue,
    jumpToField,
    switchConversationMode,
    resetFlow,
    recalibrateFlow,
    
    // 헬퍼
    getNextQuestion,
    getNextIncompleteField,
    
    // 상수
    FIELD_SEQUENCE
  };
};

export default ChatbotFlowController;
