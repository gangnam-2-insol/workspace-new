/**
 * 범용적인 JSON 필드 매핑 유틸리티
 * 채팅으로 받은 JSON 데이터를 UI 구조에 맞게 매핑
 */

class JsonFieldMapper {
  constructor() {
    // 페이지별 필드 매핑 설정
    this.pageMappings = {
      // 채용공고 등록 페이지
      'recruit_form': {
        'department': 'department',
        'headcount': 'headcount',
        // 위치 키는 응답이 'location' 또는 'locationCity'로 올 수 있어 둘 다 지원
        'location': 'locationCity',
        'locationCity': 'locationCity',
        'workDays': 'workDays',
        'experience': 'experience',
        'salary': 'salary',
        'workType': 'workType',
        'mainDuties': 'mainDuties',
        'workHours': 'workHours',
        'contactEmail': 'contactEmail',
        'deadline': 'deadline',
        // 직무명(포지션)
        'position': 'position'
      },
      // 이력서 분석 페이지
      'resume_analysis': {
        'name': 'name',
        'email': 'email',
        'phone': 'phone',
        'education': 'education',
        'experience': 'experience',
        'skills': 'skills',
        'certificates': 'certificates'
      },
      // 포트폴리오 분석 페이지
      'portfolio_analysis': {
        'title': 'title',
        'description': 'description',
        'technologies': 'technologies',
        'url': 'url',
        'github': 'github'
      },
      // 면접 관리 페이지
      'interview_management': {
        'candidateName': 'candidateName',
        'position': 'position',
        'interviewDate': 'interviewDate',
        'interviewType': 'interviewType',
        'notes': 'notes'
      }
    };

    // 필드 타입별 처리 함수
    this.fieldProcessors = {
      'text': (value) => value,
      'number': (value) => parseInt(value) || value,
      'select': (value) => value,
      'textarea': (value) => value,
      'date': (value) => value,
      'email': (value) => value
    };
  }

  /**
   * 페이지별 필드 매핑 설정 추가/수정
   */
  setPageMapping(pageId, mapping) {
    this.pageMappings[pageId] = { ...this.pageMappings[pageId], ...mapping };
  }

  /**
   * UI 구조를 분석하여 필드 정보 추출
   */
  analyzeUIStructure(container) {
    const fields = {};
    
    // input, select, textarea 요소들 찾기
    const formElements = container.querySelectorAll('input, select, textarea');
    
    formElements.forEach(element => {
      const name = element.name || element.id;
      const type = element.type || element.tagName.toLowerCase();
      const placeholder = element.placeholder || '';
      
      if (name) {
        fields[name] = {
          type: this.determineFieldType(type),
          element: element,
          placeholder: placeholder,
          currentValue: element.value
        };
      }
    });

    return fields;
  }

  /**
   * 필드 타입 결정
   */
  determineFieldType(type) {
    if (type === 'email') return 'email';
    if (type === 'number') return 'number';
    if (type === 'date') return 'date';
    if (type === 'textarea') return 'textarea';
    if (type === 'select') return 'select';
    return 'text';
  }

  /**
   * JSON 데이터를 UI 필드에 매핑
   */
  mapJsonToFields(jsonData, pageId, container = null) {
    const mapping = this.pageMappings[pageId];
    if (!mapping) {
      console.warn(`[JsonFieldMapper] 페이지 ${pageId}에 대한 매핑이 없습니다.`);
      return { success: false, message: '페이지 매핑을 찾을 수 없습니다.' };
    }

    const results = {
      success: true,
      mappedFields: [],
      errors: [],
      warnings: []
    };

    // UI 구조 분석 (container가 제공된 경우)
    let uiFields = {};
    if (container) {
      uiFields = this.analyzeUIStructure(container);
    }

    // JSON 데이터를 매핑
    for (const [jsonKey, jsonValue] of Object.entries(jsonData)) {
      const fieldName = mapping[jsonKey];
      
      if (fieldName) {
        // 필드 타입에 따른 값 처리
        const processedValue = this.processValue(jsonValue, uiFields[fieldName]?.type || 'text');
        
        results.mappedFields.push({
          jsonKey,
          fieldName,
          value: processedValue,
          originalValue: jsonValue
        });

        console.log(`[JsonFieldMapper] 매핑: ${jsonKey} -> ${fieldName} = ${processedValue}`);
      } else {
        results.warnings.push(`매핑되지 않은 키: ${jsonKey} = ${jsonValue}`);
      }
    }

    return results;
  }

  /**
   * 값 처리 (타입별 변환)
   */
  processValue(value, fieldType) {
    const processor = this.fieldProcessors[fieldType] || this.fieldProcessors.text;
    return processor(value);
  }

  /**
   * 매핑된 필드들을 실제 UI에 적용
   */
  applyMappedFields(mappedFields, onFieldUpdate) {
    if (!onFieldUpdate) {
      console.warn('[JsonFieldMapper] onFieldUpdate 함수가 제공되지 않았습니다.');
      return;
    }

    mappedFields.forEach(field => {
      try {
        onFieldUpdate(field.fieldName, field.value);
        
        // 커스텀 이벤트 발생
        window.dispatchEvent(new CustomEvent('aiFieldUpdated', {
          detail: {
            field: field.fieldName,
            value: field.value,
            jsonKey: field.jsonKey,
            originalValue: field.originalValue
          }
        }));

        console.log(`[JsonFieldMapper] 필드 업데이트: ${field.fieldName} = ${field.value}`);
      } catch (error) {
        console.error(`[JsonFieldMapper] 필드 업데이트 오류: ${field.fieldName}`, error);
      }
    });
  }

  /**
   * 채팅 응답에서 JSON 데이터 추출
   */
  extractJsonFromResponse(response) {
    // 1. extracted_data가 있는 경우 (새로운 방식)
    if (response.extracted_data && typeof response.extracted_data === 'object') {
      return response.extracted_data;
    }

    // 2. content에서 JSON 패턴 찾기 (기존 방식)
    if (response.content) {
      const jsonMatch = response.content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        try {
          return JSON.parse(jsonMatch[0]);
        } catch (e) {
          console.warn('[JsonFieldMapper] JSON 파싱 실패:', e);
        }
      }
    }

    // 3. field와 value가 있는 경우
    if (response.field && response.value) {
      return { [response.field]: response.value };
    }

    return null;
  }

  /**
   * 통합 처리 함수
   */
  processChatResponse(response, pageId, container = null, onFieldUpdate = null) {
    const jsonData = this.extractJsonFromResponse(response);
    
    if (!jsonData) {
      console.log('[JsonFieldMapper] JSON 데이터를 찾을 수 없습니다.');
      return { success: false, message: 'JSON 데이터를 찾을 수 없습니다.' };
    }

    console.log('[JsonFieldMapper] 추출된 JSON 데이터:', jsonData);

    // JSON을 필드에 매핑
    const mappingResult = this.mapJsonToFields(jsonData, pageId, container);
    
    // 매핑된 필드들을 UI에 적용
    if (mappingResult.success && onFieldUpdate) {
      this.applyMappedFields(mappingResult.mappedFields, onFieldUpdate);
    }

    return {
      success: mappingResult.success,
      mappedFields: mappingResult.mappedFields,
      errors: mappingResult.errors,
      warnings: mappingResult.warnings
    };
  }
}

// 싱글톤 인스턴스 생성
const jsonFieldMapper = new JsonFieldMapper();

export default jsonFieldMapper;
