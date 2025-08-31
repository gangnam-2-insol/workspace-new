const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class JobPostingAPI {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api/job-postings`;
  }

  // 채용공고 목록 조회
  async getJobPostings(params = {}) {
    try {
      const queryParams = new URLSearchParams();

      if (params.skip !== undefined) queryParams.append('skip', params.skip);
      if (params.limit !== undefined) queryParams.append('limit', params.limit);
      if (params.status) queryParams.append('status', params.status);
      if (params.company) queryParams.append('company', params.company);

      const url = `${this.baseURL}?${queryParams.toString()}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 목록 조회 실패:', error);
      throw error;
    }
  }

  // 채용공고 상세 조회
  async getJobPosting(jobId) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 조회 실패:', error);
      throw error;
    }
  }

  // 채용공고 생성
  async createJobPosting(jobData) {
    const startTime = Date.now();

    console.group('📝 [채용공고 API] 생성 요청');
    console.log('🕐 요청 시작:', new Date().toISOString());
    console.log('🌐 API URL:', this.baseURL);

    // 요청 데이터 분석
    console.log('📊 [요청 데이터 분석]:', {
      총필드수: Object.keys(jobData).length,
      제목: jobData.title || 'N/A',
      부서: jobData.department || 'N/A',
      직무: jobData.position || 'N/A',
      데이터크기: JSON.stringify(jobData).length,
      분리된업무포함: jobData.core_responsibilities ? '예' : '아니오'
    });

    // 필수 필드 확인
    const requiredFields = ['title', 'department', 'main_duties'];
    const missingFields = requiredFields.filter(field => !jobData[field]);

    console.log('🔍 [필수 필드 검증]:', {
      필수필드: requiredFields,
      누락필드: missingFields,
      검증결과: missingFields.length === 0 ? '통과' : '실패'
    });

    if (missingFields.length > 0) {
      console.warn('⚠️ [검증 실패] 필수 필드 누락:', missingFields);
    }

    try {
      const fetchStart = Date.now();

      const response = await fetch(this.baseURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobData),
      });

      const fetchTime = Date.now() - fetchStart;

      console.log('📊 [HTTP 응답]:', {
        상태코드: response.status,
        상태텍스트: response.statusText,
        네트워크시간: `${fetchTime}ms`,
        응답헤더: Object.fromEntries(response.headers.entries())
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ [HTTP 오류]:', {
          상태: response.status,
          메시지: response.statusText,
          응답내용: errorText
        });
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const parseStart = Date.now();
      const result = await response.json();
      const parseTime = Date.now() - parseStart;
      const totalTime = Date.now() - startTime;

      console.log('📥 [응답 분석]:', {
        파싱시간: `${parseTime}ms`,
        총처리시간: `${totalTime}ms`,
        생성된ID: result.id || 'N/A',
        응답크기: JSON.stringify(result).length,
        성공여부: result.id ? '성공' : '실패'
      });

      // 성능 분석
      if (totalTime > 5000) {
        console.warn('⚠️ [성능 경고] 응답시간 5초 초과:', totalTime + 'ms');
      } else {
        console.log('✅ [성능 양호] 응답시간 정상:', totalTime + 'ms');
      }

      console.groupEnd();
      return result;

    } catch (error) {
      const errorTime = Date.now() - startTime;

      console.error('❌ [API 오류 상세]:', {
        오류타입: error.name,
        오류메시지: error.message,
        실패시간: `${errorTime}ms`,
        요청크기: JSON.stringify(jobData).length
      });

      console.groupEnd();
      throw error;
    }
  }

  // 채용공고 수정
  async updateJobPosting(jobId, updateData) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 수정 실패:', error);
      throw error;
    }
  }

  // 채용공고 삭제
  async deleteJobPosting(jobId) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 삭제 실패:', error);
      throw error;
    }
  }

  // 채용공고 발행
  async publishJobPosting(jobId) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}/publish`, {
        method: 'PATCH',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 발행 실패:', error);
      throw error;
    }
  }

  // 채용공고 마감
  async closeJobPosting(jobId) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}/close`, {
        method: 'PATCH',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 마감 실패:', error);
      throw error;
    }
  }

  // 채용공고 통계 조회
  async getJobPostingStats() {
    try {
      const response = await fetch(`${this.baseURL}/stats/overview`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 통계 조회 실패:', error);
      throw error;
    }
  }

  // 주요업무 분리 기능
  async separateMainDuties(mainDuties) {
    const startTime = Date.now();

    console.group('🔄 [주요업무 분리 API] 요청');
    console.log('📝 원본 텍스트:', mainDuties.substring(0, 100) + '...');
    console.log('📏 텍스트 길이:', mainDuties.length);
    console.log('🌐 API URL:', `${this.baseURL}/separate-duties`);

    try {
      const fetchStart = Date.now();

      const response = await fetch(`${this.baseURL}/separate-duties`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ main_duties: mainDuties }),
      });

      const fetchTime = Date.now() - fetchStart;

      console.log('📊 [HTTP 응답]:', {
        상태코드: response.status,
        상태텍스트: response.statusText,
        네트워크시간: `${fetchTime}ms`
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ [분리 API 오류]:', {
          상태: response.status,
          응답내용: errorText
        });
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const parseStart = Date.now();
      const result = await response.json();
      const parseTime = Date.now() - parseStart;
      const totalTime = Date.now() - startTime;

      console.log('📥 [분리 결과 분석]:', {
        파싱시간: `${parseTime}ms`,
        총처리시간: `${totalTime}ms`,
        성공여부: result.success,
        카테고리수: result.summary?.total_categories || 0,
        분리품질: result.summary?.separation_quality || 'N/A',
        응답크기: JSON.stringify(result).length
      });

      // 분리된 카테고리별 내용 분석
      if (result.separated_duties) {
        console.log('📋 [카테고리별 분리 결과]:');
        Object.entries(result.separated_duties).forEach(([category, content]) => {
          if (content && content.trim()) {
            console.log(`  🎯 ${category}: ${content.length}자`);
          }
        });
      }

      console.groupEnd();
      return result;

    } catch (error) {
      const errorTime = Date.now() - startTime;

      console.error('❌ [분리 API 오류]:', {
        오류타입: error.name,
        오류메시지: error.message,
        실패시간: `${errorTime}ms`,
        원본길이: mainDuties.length
      });

      console.groupEnd();
      throw error;
    }
  }

  // 스마트 주요업무 분리 기능 (가장 적합한 내용 자동 선별)
  async separateMainDutiesSmart(mainDuties) {
    const startTime = Date.now();

    console.group('🤖 [스마트 분리 API] 요청');
    console.log('📝 원본 텍스트:', mainDuties.substring(0, 100) + '...');
    console.log('📏 텍스트 길이:', mainDuties.length);
    console.log('🌐 API URL:', `${this.baseURL}/separate-duties-smart`);

    try {
      const fetchStart = Date.now();

      const response = await fetch(`${this.baseURL}/separate-duties-smart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ main_duties: mainDuties }),
      });

      const fetchTime = Date.now() - fetchStart;

      console.log('📊 [HTTP 응답]:', {
        상태코드: response.status,
        상태텍스트: response.statusText,
        네트워크시간: `${fetchTime}ms`
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ [스마트 분리 API 오류]:', {
          상태: response.status,
          응답내용: errorText
        });
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const parseStart = Date.now();
      const result = await response.json();
      const parseTime = Date.now() - parseStart;
      const totalTime = Date.now() - startTime;

      console.log('🤖 [스마트 분리 결과 분석]:', {
        파싱시간: `${parseTime}ms`,
        총처리시간: `${totalTime}ms`,
        성공여부: result.success,
        품질점수: result.smart_extraction?.quality_score || 0,
        추천내용길이: result.smart_extraction?.recommended_content?.length || 0,
        주요카테고리수: result.summary?.primary_categories || 0,
        보조카테고리수: result.summary?.secondary_categories || 0
      });

      // 스마트 추출 결과 분석
      if (result.smart_extraction) {
        console.log('🎯 [스마트 추출 상세]:');
        console.log(`  📝 추천 내용: "${result.smart_extraction.recommended_content.substring(0, 80)}..."`);
        console.log(`  📊 우선순위: [${result.smart_extraction.priority_order.slice(0, 3).join(', ')}]`);
        console.log(`  💯 품질점수: ${(result.smart_extraction.quality_score * 100).toFixed(1)}점`);

        const displaySuggestions = result.smart_extraction.display_suggestions;
        console.log('🎨 [표시 제안]:');
        console.log(`  🔝 주요 표시: ${displaySuggestions.primary_display?.length || 0}개 카테고리`);
        console.log(`  📂 보조 표시: ${displaySuggestions.secondary_display?.length || 0}개 카테고리`);
        console.log(`  🔍 숨김 내용: ${displaySuggestions.hidden_content?.length || 0}개 카테고리`);

        // 주요 카테고리 내용 미리보기
        if (displaySuggestions.primary_display?.length > 0) {
          console.log('📋 [주요 카테고리 미리보기]:');
          displaySuggestions.primary_display.forEach((item, index) => {
            console.log(`  ${index + 1}. ${item.category}: ${item.content.substring(0, 50)}... (${item.length}자, 점수: ${item.score.toFixed(2)})`);
          });
        }
      }

      console.groupEnd();
      return result;

    } catch (error) {
      const errorTime = Date.now() - startTime;

      console.error('❌ [스마트 분리 API 오류]:', {
        오류타입: error.name,
        오류메시지: error.message,
        실패시간: `${errorTime}ms`,
        원본길이: mainDuties.length
      });

      console.groupEnd();
      throw error;
    }
  }

  // 분리된 주요업무 적용
  async applySeparatedDuties(jobId, separatedDuties) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}/apply-separated-duties`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(separatedDuties),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('분리된 업무 적용 실패:', error);
      throw error;
    }
  }

  // 관련 분야 추출
  async extractJobFields(inputData) {
    try {
      const response = await fetch(`${this.baseURL}/extract-fields`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(inputData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('분야 추출 실패:', error);
      throw error;
    }
  }

  // 에러 처리 헬퍼
  handleError(error) {
    if (error.response) {
      // 서버 응답이 있는 경우
      return {
        message: error.response.data?.detail || '서버 오류가 발생했습니다.',
        status: error.response.status
      };
    } else if (error.request) {
      // 요청은 보냈지만 응답이 없는 경우
      return {
        message: '서버에 연결할 수 없습니다.',
        status: 0
      };
    } else {
      // 요청 자체에 문제가 있는 경우
      return {
        message: error.message || '알 수 없는 오류가 발생했습니다.',
        status: 0
      };
    }
  }
}

export default new JobPostingAPI();
