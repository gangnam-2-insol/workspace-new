from typing import Dict, Any, Optional, List
from openai import OpenAI
import os
from datetime import datetime

class LLMService:
    def __init__(self):
        """
        LLM 서비스 초기화
        """
        print(f"[LLMService] === LLM 서비스 초기화 시작 ===")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"[LLMService] 경고: OPENAI_API_KEY 환경변수가 설정되지 않았습니다!")
        else:
            print(f"[LLMService] OPENAI_API_KEY 확인됨 (길이: {len(api_key)})")
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = 'gpt-4o-mini'
        print(f"[LLMService] OpenAI 클라이언트 초기화 완료: {self.model_name}")
        print(f"[LLMService] === LLM 서비스 초기화 완료 ===")
        
    async def analyze_similarity_reasoning(self, 
                                         original_resume: Dict[str, Any], 
                                         similar_resume: Dict[str, Any],
                                         similarity_score: float,
                                         chunk_details: Optional[Dict] = None,
                                         document_type: str = "이력서") -> Dict[str, Any]:
        """
        두 문서 간의 유사성을 분석하고 어떤 부분이 유사한지 설명합니다.
        
        Args:
            original_resume (Dict[str, Any]): 원본 문서
            similar_resume (Dict[str, Any]): 유사한 문서
            similarity_score (float): 유사도 점수
            chunk_details (Optional[Dict]): 청크별 세부 정보
            document_type (str): 문서 타입 ("이력서" 또는 "자소서")
            
        Returns:
            Dict[str, Any]: 유사성 분석 결과
        """
        try:
            print(f"[LLMService] === 유사성 분석 시작 ===")
            print(f"[LLMService] 원본 {document_type}: {original_resume.get('name', 'Unknown')}")
            print(f"[LLMService] 유사 {document_type}: {similar_resume.get('name', 'Unknown')}")
            print(f"[LLMService] 유사도 점수: {similarity_score:.3f}")
            
            # 이력서에서 주요 정보 추출
            original_info = self._extract_resume_info(original_resume)
            similar_info = self._extract_resume_info(similar_resume)
            print(f"[LLMService] {document_type} 정보 추출 완료")
            
            # 프롬프트 구성
            prompt = self._build_similarity_analysis_prompt(
                original_info, 
                similar_info, 
                similarity_score,
                chunk_details
            )
            print(f"[LLMService] 프롬프트 생성 완료 (길이: {len(prompt)})")
            
            # OpenAI API 호출
            system_prompt = f"당신은 {document_type} 유사성 분석 전문가입니다. 두 {document_type}를 비교하여 구체적으로 어떤 부분이 유사한지 간결하고 명확하게 설명해주세요."
            print(f"[LLMService] OpenAI API 호출 시작...")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            print(f"[LLMService] OpenAI API 응답 수신 완료")
            analysis_result = response.choices[0].message.content
            print(f"[LLMService] 분석 결과 길이: {len(analysis_result) if analysis_result else 0}")
            print(f"[LLMService] 분석 결과 미리보기: {analysis_result[:100] if analysis_result else 'None'}...")
            
            # 응답 파싱하여 구조화된 데이터 추출
            parsed_analysis = self._parse_analysis_response(analysis_result)
            
            print(f"[LLMService] === 유사성 분석 완료 ===")
            return {
                "success": True,
                "analysis": analysis_result,
                "parsed_analysis": parsed_analysis,
                "similarity_score": similarity_score,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[LLMService] === 유사성 분석 중 오류 발생 ===")
            print(f"[LLMService] 오류 타입: {type(e).__name__}")
            print(f"[LLMService] 오류 메시지: {str(e)}")
            import traceback
            print(f"[LLMService] 스택 트레이스: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "analysis": "유사성 분석에 실패했습니다.",
                "similarity_score": similarity_score,
                "analyzed_at": datetime.now().isoformat()
            }
    
    def _extract_resume_info(self, resume: Dict[str, Any]) -> Dict[str, str]:
        """
        이력서에서 주요 정보를 추출합니다.
        
        Args:
            resume (Dict[str, Any]): 이력서 데이터
            
        Returns:
            Dict[str, str]: 추출된 정보
        """
        return {
            "name": resume.get("name", "Unknown"),
            "position": resume.get("position", ""),
            "department": resume.get("department", ""),
            "growth_background": resume.get("growthBackground", ""),
            "motivation": resume.get("motivation", ""),
            "career_history": resume.get("careerHistory", ""),
            "experience": resume.get("experience", ""),
            "skills": resume.get("skills", "")
        }
    
    def _build_similarity_analysis_prompt(self, 
                                        original_info: Dict[str, str], 
                                        similar_info: Dict[str, str],
                                        similarity_score: float,
                                        chunk_details: Optional[Dict] = None) -> str:
        """
        유사성 분석을 위한 프롬프트를 구성합니다.
        
        Args:
            original_info (Dict[str, str]): 원본 이력서 정보
            similar_info (Dict[str, str]): 유사한 이력서 정보
            similarity_score (float): 유사도 점수
            chunk_details (Optional[Dict]): 청크별 세부 정보
            
        Returns:
            str: 구성된 프롬프트
        """
        
        # 청크 매칭 정보 구성
        chunk_info = ""
        if chunk_details:
            chunk_matches = []
            for key, detail in chunk_details.items():
                chunk_matches.append(f"- {detail['query_chunk']} → {detail['match_chunk']} ({detail['score']:.1%})")
            chunk_info = "\n".join(chunk_matches)
        else:
            chunk_info = "청크 매칭 정보 없음"
        
        # 섹션별 키워드 추출을 위해 텍스트 길이 제한을 늘리고 더 명확한 지시사항 추가
        prompt = f"""역할: 너는 자소서/이력서 유사성 분석 전문가다.
임무: 두 문서의 각 섹션에서 핵심 키워드를 정확히 추출하고 유사성을 분석해라.

엄격한 규칙:
- 주어진 텍스트에 실제로 존재하는 단어만 사용
- 각 섹션별로 핵심 키워드를 반드시 추출
- 키워드는 명사, 동사, 형용사 위주로 추출
- 섹션에 내용이 없으면 '없음'으로 표시

## 조회이력서 ({original_info['name']})
### 성장배경 섹션:
{original_info['growth_background'][:400]}

### 지원동기 섹션:
{original_info['motivation'][:400]}

### 경력사항 섹션:
{original_info['career_history'][:400]}

## 유사이력서 ({similar_info['name']})
### 성장배경 섹션:
{similar_info['growth_background'][:400]}

### 지원동기 섹션:
{similar_info['motivation'][:400]}

### 경력사항 섹션:
{similar_info['career_history'][:400]}

출력 형식 (각 항목을 정확히 구분):

1) 전체키워드: {{두 문서에서 공통으로 나타나는 핵심 단어 최대 5개}}

2) 유사섹션: {{가장 유사한 섹션 이름과 이유}}

3) 섹션별키워드분석:
- 성장배경: 조회이력서={{최대5개키워드}} | 유사이력서={{최대5개키워드}} | 공통키워드={{최대5개키워드}}
- 지원동기: 조회이력서={{최대5개키워드}} | 유사이력서={{최대5개키워드}} | 공통키워드={{최대5개키워드}}
- 경력사항: 조회이력서={{최대5개키워드}} | 유사이력서={{최대5개키워드}} | 공통키워드={{최대5개키워드}}

4) 요약: {{유사도 {similarity_score:.1%} 기준으로 핵심 유사점}}

**중요: 각 섹션에서 최대 5개의 핵심 키워드를 추출하되, 텍스트에 없는 단어는 절대 사용금지**"""
        
        return prompt
    
    def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """
        LLM 응답을 파싱하여 구조화된 데이터로 변환합니다.
        
        Args:
            analysis_text (str): LLM 응답 텍스트
            
        Returns:
            Dict[str, Any]: 파싱된 구조화 데이터
        """
        try:
            if not analysis_text:
                return {}
            
            parsed_data = {
                "전체키워드": [],
                "유사섹션": "",
                "섹션별키워드": {
                    "성장배경": {"조회이력서": [], "유사이력서": [], "공통": []},
                    "지원동기": {"조회이력서": [], "유사이력서": [], "공통": []},
                    "경력사항": {"조회이력서": [], "유사이력서": [], "공통": []}
                },
                "요약": ""
            }
            
            lines = analysis_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 1) 전체키워드 파싱
                if line.startswith('1)') and '전체키워드' in line:
                    keywords = line.split(':', 1)[1].strip() if ':' in line else ""
                    all_keywords = [k.strip() for k in keywords.split(',') if k.strip()]
                    parsed_data["전체키워드"] = all_keywords[:5]  # 최대 5개로 제한
                
                # 2) 유사섹션 파싱
                elif line.startswith('2)') and '유사섹션' in line:
                    parsed_data["유사섹션"] = line.split(':', 1)[1].strip() if ':' in line else ""
                
                # 3) 섹션별키워드분석 파싱
                elif line.startswith('3)') and '섹션별키워드' in line:
                    current_section = "섹션별키워드"
                
                elif current_section == "섹션별키워드" and line.startswith('-'):
                    # 예: - 성장배경: A문서키워드={word1,word2} | B문서키워드={word3,word4} | 공통키워드={word5}
                    self._parse_section_keywords(line, parsed_data["섹션별키워드"])
                
                # 4) 요약 파싱
                elif line.startswith('4)') and '요약' in line:
                    parsed_data["요약"] = line.split(':', 1)[1].strip() if ':' in line else ""
            
            print(f"[LLMService] 응답 파싱 완료: {len(parsed_data['전체키워드'])}개 전체키워드, "
                  f"섹션별키워드 {len([k for section in parsed_data['섹션별키워드'].values() for k in section['공통']])}개")
            
            return parsed_data
            
        except Exception as e:
            print(f"[LLMService] 응답 파싱 중 오류: {str(e)}")
            return {}
    
    def _parse_section_keywords(self, line: str, section_data: Dict[str, Dict[str, List[str]]]):
        """
        섹션별 키워드 라인을 파싱합니다.
        
        Args:
            line (str): 파싱할 라인
            section_data (Dict): 섹션 데이터를 저장할 딕셔너리
        """
        try:
            # 섹션명 추출 (성장배경, 지원동기, 경력사항)
            section_name = None
            for name in ["성장배경", "지원동기", "경력사항"]:
                if name in line:
                    section_name = name
                    break
            
            if not section_name:
                return
            
            # 키워드 추출
            parts = line.split('|')
            for part in parts:
                part = part.strip()
                
                if '조회이력서' in part and '=' in part:
                    keywords_str = part.split('=', 1)[1].strip()
                    keywords = self._extract_keywords_from_braces(keywords_str)
                    section_data[section_name]["조회이력서"] = keywords
                
                elif '유사이력서' in part and '=' in part:
                    keywords_str = part.split('=', 1)[1].strip()
                    keywords = self._extract_keywords_from_braces(keywords_str)
                    section_data[section_name]["유사이력서"] = keywords
                
                elif '공통키워드' in part and '=' in part:
                    keywords_str = part.split('=', 1)[1].strip()
                    keywords = self._extract_keywords_from_braces(keywords_str)
                    section_data[section_name]["공통"] = keywords
            
        except Exception as e:
            print(f"[LLMService] 섹션 키워드 파싱 오류: {str(e)}")
    
    def _extract_keywords_from_braces(self, text: str) -> List[str]:
        """
        중괄호 안의 키워드들을 추출합니다. 중괄호가 없으면 직접 파싱합니다.
        
        Args:
            text (str): 키워드가 포함된 텍스트
            
        Returns:
            List[str]: 추출된 키워드 리스트
        """
        try:
            import re
            keywords = []
            
            # 먼저 중괄호 안의 내용 추출 시도
            matches = re.findall(r'\{([^}]*)\}', text)
            
            if matches:
                # 중괄호가 있는 경우
                for match in matches:
                    words = [w.strip() for w in match.split(',') if w.strip() and w.strip() != '없음']
                    keywords.extend(words[:5])
            else:
                # 중괄호가 없는 경우, 콜론 뒤의 내용을 직접 파싱
                if ':' in text:
                    content = text.split(':', 1)[1].strip()
                    words = [w.strip() for w in content.split(',') if w.strip() and w.strip() != '없음']
                    keywords.extend(words[:5])
            
            return keywords
            
        except Exception as e:
            print(f"[LLMService] 키워드 추출 오류: {str(e)}")
            return []
    
    async def analyze_plagiarism_risk(self, 
                                    original_resume: Dict[str, Any], 
                                    similar_resumes: List[Dict[str, Any]],
                                    document_type: str = "이력서") -> Dict[str, Any]:
        """
        표절 위험도를 분석합니다.
        
        Args:
            original_resume (Dict[str, Any]): 원본 문서
            similar_resumes (List[Dict[str, Any]]): 유사한 문서들
            document_type (str): 문서 타입 ("이력서" 또는 "자소서")
            
        Returns:
            Dict[str, Any]: 표절 위험도 분석 결과
        """
        try:
            print(f"[LLMService] === 표절 위험도 분석 시작 ===")
            print(f"[LLMService] 원본 {document_type}: {original_resume.get('name', 'Unknown')}")
            print(f"[LLMService] 유사한 {document_type} 수: {len(similar_resumes)}")
            
            if not similar_resumes:
                print(f"[LLMService] 유사한 {document_type}가 없음 - LOW 위험도 반환")
                return {
                    "success": True,
                    "risk_level": "LOW",
                    "risk_score": 0.0,
                    "analysis": f"유사한 {document_type}가 발견되지 않았습니다.",
                    "recommendations": []
                }
            
            # 최고 유사도 점수 확인 (API 응답 구조에 맞게 수정)
            similarities = []
            for resume in similar_resumes:
                if "similarity_score" in resume:
                    similarities.append(resume["similarity_score"])
                elif "overall_similarity" in resume:
                    similarities.append(resume["overall_similarity"])
                else:
                    print(f"[LLMService] 경고: 유사도 점수를 찾을 수 없음 - {resume.keys()}")
                    similarities.append(0.0)
            
            max_similarity = max(similarities) if similarities else 0.0
            print(f"[LLMService] 최고 유사도 점수: {max_similarity:.3f}")
            
            # 위험도 레벨 결정
            if max_similarity >= 0.8:
                risk_level = "HIGH"
                risk_score = max_similarity
                analysis = f"매우 높은 유사도({max_similarity:.1%})의 {document_type}가 발견되었습니다. 표절 가능성이 높습니다."
                recommendations = []
            elif max_similarity >= 0.6:
                risk_level = "MEDIUM"
                risk_score = max_similarity
                analysis = f"높은 유사도({max_similarity:.1%})의 {document_type}가 발견되었습니다. 주의가 필요합니다."
                recommendations = []
            else:
                risk_level = "LOW"
                risk_score = max_similarity
                analysis = f"적정 수준의 유사도({max_similarity:.1%})입니다. 표절 위험은 낮습니다."
                recommendations = []
            
            print(f"[LLMService] 위험도 결정 완료: {risk_level} (점수: {risk_score:.3f})")
            print(f"[LLMService] === 표절 위험도 분석 완료 ===")
            
            return {
                "success": True,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "analysis": analysis,
                "recommendations": recommendations,
                "similar_count": len(similar_resumes),
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[LLMService] === 표절 위험도 분석 중 오류 발생 ===")
            print(f"[LLMService] 오류 타입: {type(e).__name__}")
            print(f"[LLMService] 오류 메시지: {str(e)}")
            import traceback
            print(f"[LLMService] 스택 트레이스: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "risk_level": "UNKNOWN",
                "risk_score": 0.0,
                "analysis": "표절 위험도 분석에 실패했습니다.",
                "analyzed_at": datetime.now().isoformat()
            }