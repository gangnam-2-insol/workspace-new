#!/usr/bin/env python3
"""
HuggingFace 기반 이력서 분석기
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from transformers import pipeline, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
from models.resume_analysis import HuggingFaceAnalysisResult

class HuggingFaceResumeAnalyzer:
    """HuggingFace 기반 이력서 분석기"""
    
    def __init__(self, device: str = "auto"):
        """초기화"""
        # 디바이스 설정
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"🔧 HuggingFace 분석기 초기화 중... (디바이스: {self.device})")
        
        # 모델 로딩
        self._load_models()
        
        print("✅ HuggingFace 분석기 초기화 완료!")
    
    def _load_models(self):
        """AI 모델들 로딩"""
        try:
            # 1. 임베딩 모델: multi-qa-MiniLM-L6-cos-v1
            print("📥 임베딩 모델 로딩 중...")
            self.embedding_model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1', device=self.device)
            
            # 2. 요약 모델: facebook/bart-large-cnn
            print("📥 요약 모델 로딩 중...")
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=self.device)
            
            # 3. 분류 모델: facebook/bart-large-mnli
            print("📥 분류 모델 로딩 중...")
            self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=self.device)
            
            # 4. 문법검사 모델: prithivida/grammar_error_correcter_v1
            print("📥 문법검사 모델 로딩 중...")
            self.grammar_corrector = pipeline("text2text-generation", model="prithivida/grammar_error_correcter_v1", device=self.device)
            
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {str(e)}")
            raise
    
    async def analyze_resume(self, applicant_data: Dict[str, Any]) -> HuggingFaceAnalysisResult:
        """이력서 분석 실행"""
        try:
            start_time = time.time()
            
            print(f"🔍 {applicant_data.get('name', '알 수 없음')} 이력서 분석 시작...")
            
            # 이력서 내용 추출
            resume_content = self._extract_resume_content(applicant_data)
            
            # 각 항목별 분석 실행
            analysis_results = {}
            
            # 1. 학력 및 전공 분석
            analysis_results["education"] = await self._analyze_education(applicant_data, resume_content)
            
            # 2. 경력 및 직무 경험 분석
            analysis_results["experience"] = await self._analyze_experience(applicant_data, resume_content)
            
            # 3. 보유 기술 및 역량 분석
            analysis_results["skills"] = await self._analyze_skills(applicant_data, resume_content)
            
            # 4. 프로젝트 및 성과 분석
            analysis_results["projects"] = await self._analyze_projects(applicant_data, resume_content)
            
            # 5. 자기계발 및 성장 분석
            analysis_results["growth"] = await self._analyze_growth(applicant_data, resume_content)
            
            # 6. 문법 및 표현 분석
            analysis_results["grammar"] = await self._analyze_grammar(resume_content)
            
            # 7. 직무 적합성 분석
            analysis_results["job_matching"] = await self._analyze_job_matching(applicant_data, resume_content)
            
            # 종합 점수 계산
            overall_score = self._calculate_overall_score(analysis_results)
            
            # 강점 및 개선점 추출
            strengths, improvements = self._extract_feedback(analysis_results)
            
            # 권장사항 생성
            recommendations = self._generate_recommendations(analysis_results, improvements)
            
            # 종합 피드백 생성
            overall_feedback = self._generate_overall_feedback(analysis_results, overall_score)
            
            # 분석 결과 구성
            analysis_result = HuggingFaceAnalysisResult(
                overall_score=overall_score,
                education_score=analysis_results["education"]["score"],
                experience_score=analysis_results["experience"]["score"],
                skills_score=analysis_results["skills"]["score"],
                projects_score=analysis_results["projects"]["score"],
                growth_score=analysis_results["growth"]["score"],
                grammar_score=analysis_results["grammar"]["score"],
                job_matching_score=analysis_results["job_matching"]["score"],
                
                education_analysis=analysis_results["education"]["analysis"],
                experience_analysis=analysis_results["experience"]["analysis"],
                skills_analysis=analysis_results["skills"]["analysis"],
                projects_analysis=analysis_results["projects"]["analysis"],
                growth_analysis=analysis_results["growth"]["analysis"],
                grammar_analysis=analysis_results["grammar"]["analysis"],
                job_matching_analysis=analysis_results["job_matching"]["analysis"],
                
                strengths=strengths,
                improvements=improvements,
                overall_feedback=overall_feedback,
                recommendations=recommendations
            )
            
            processing_time = time.time() - start_time
            print(f"✅ 이력서 분석 완료: {applicant_data.get('name', '알 수 없음')} (처리시간: {processing_time:.2f}초)")
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ 이력서 분석 실패: {str(e)}")
            raise
    
    def _extract_resume_content(self, applicant_data: Dict[str, Any]) -> str:
        """이력서 내용 추출 및 구성"""
        content_parts = []
        
        # 기본 정보
        if applicant_data.get("name"):
            content_parts.append(f"이름: {applicant_data['name']}")
        if applicant_data.get("position"):
            content_parts.append(f"지원 직무: {applicant_data['position']}")
        if applicant_data.get("department"):
            content_parts.append(f"부서: {applicant_data['department']}")
        if applicant_data.get("experience"):
            content_parts.append(f"경력: {applicant_data['experience']}")
        if applicant_data.get("skills"):
            content_parts.append(f"기술 스택: {applicant_data['skills']}")
        
        # 상세 정보
        if applicant_data.get("growthBackground"):
            content_parts.append(f"성장 배경: {applicant_data['growthBackground']}")
        if applicant_data.get("motivation"):
            content_parts.append(f"지원 동기: {applicant_data['motivation']}")
        if applicant_data.get("careerHistory"):
            content_parts.append(f"경력 사항: {applicant_data['careerHistory']}")
        
        # 추출된 텍스트
        if applicant_data.get("extracted_text"):
            content_parts.append(f"이력서 내용:\n{applicant_data['extracted_text']}")
        
        return "\n\n".join(content_parts) if content_parts else "이력서 내용이 없습니다."
    
    async def _analyze_education(self, applicant_data: Dict[str, Any], resume_content: str) -> Dict[str, Any]:
        """학력 및 전공 분석"""
        try:
            # 학력 관련 키워드
            education_keywords = ["학력", "전공", "대학교", "학과", "학점", "졸업", "재학"]
            
            # 키워드 매칭 점수 계산
            keyword_score = self._calculate_keyword_score(resume_content, education_keywords)
            
            # 학력 정보 완성도 평가
            completeness_score = self._evaluate_completeness(applicant_data, ["education", "major"])
            
            # 직무 연관성 평가
            relevance_score = self._evaluate_job_relevance(applicant_data.get("position", ""), resume_content)
            
            # 종합 점수 계산
            score = int((keyword_score * 0.4 + completeness_score * 0.3 + relevance_score * 0.3))
            
            analysis = f"학력 정보 완성도: {completeness_score}/100, 직무 연관성: {relevance_score}/100"
            
            return {"score": score, "analysis": analysis}
            
        except Exception as e:
            print(f"❌ 학력 분석 실패: {str(e)}")
            return {"score": 50, "analysis": "학력 분석 중 오류가 발생했습니다."}
    
    async def _analyze_experience(self, applicant_data: Dict[str, Any], resume_content: str) -> Dict[str, Any]:
        """경력 및 직무 경험 분석"""
        try:
            # 경력 관련 키워드
            experience_keywords = ["경력", "경험", "업무", "담당", "개발", "프로젝트", "성과"]
            
            # 키워드 매칭 점수 계산
            keyword_score = self._calculate_keyword_score(resume_content, experience_keywords)
            
            # 경력 정보 완성도 평가
            completeness_score = self._evaluate_completeness(applicant_data, ["experience", "careerHistory"])
            
            # 경력 기간 평가
            duration_score = self._evaluate_experience_duration(applicant_data.get("experience", ""))
            
            # 종합 점수 계산
            score = int((keyword_score * 0.3 + completeness_score * 0.4 + duration_score * 0.3))
            
            analysis = f"경력 정보 완성도: {completeness_score}/100, 경력 기간: {duration_score}/100"
            
            return {"score": score, "analysis": analysis}
            
        except Exception as e:
            print(f"❌ 경력 분석 실패: {str(e)}")
            return {"score": 50, "analysis": "경력 분석 중 오류가 발생했습니다."}
    
    async def _analyze_skills(self, applicant_data: Dict[str, Any], resume_content: str) -> Dict[str, Any]:
        """보유 기술 및 역량 분석"""
        try:
            # 기술 관련 키워드
            skill_keywords = ["기술", "스택", "언어", "프레임워크", "도구", "라이브러리"]
            
            # 키워드 매칭 점수 계산
            keyword_score = self._calculate_keyword_score(resume_content, skill_keywords)
            
            # 기술 정보 완성도 평가
            completeness_score = self._evaluate_completeness(applicant_data, ["skills"])
            
            # 기술 다양성 평가
            diversity_score = self._evaluate_skill_diversity(applicant_data.get("skills", ""))
            
            # 종합 점수 계산
            score = int((keyword_score * 0.3 + completeness_score * 0.4 + diversity_score * 0.3))
            
            analysis = f"기술 정보 완성도: {completeness_score}/100, 기술 다양성: {diversity_score}/100"
            
            return {"score": score, "analysis": analysis}
            
        except Exception as e:
            print(f"❌ 기술 분석 실패: {str(e)}")
            return {"score": 50, "analysis": "기술 분석 중 오류가 발생했습니다."}
    
    async def _analyze_projects(self, applicant_data: Dict[str, Any], resume_content: str) -> Dict[str, Any]:
        """프로젝트 및 성과 분석"""
        try:
            # 프로젝트 관련 키워드
            project_keywords = ["프로젝트", "개발", "구현", "설계", "아키텍처", "성과", "결과"]
            
            # 키워드 매칭 점수 계산
            keyword_score = self._calculate_keyword_score(resume_content, project_keywords)
            
            # 프로젝트 정보 완성도 평가
            completeness_score = self._evaluate_completeness(applicant_data, ["projects", "achievements"])
            
            # 프로젝트 규모 평가
            scale_score = self._evaluate_project_scale(resume_content)
            
            # 종합 점수 계산
            score = int((keyword_score * 0.3 + completeness_score * 0.4 + scale_score * 0.3))
            
            analysis = f"프로젝트 정보 완성도: {completeness_score}/100, 프로젝트 규모: {scale_score}/100"
            
            return {"score": score, "analysis": analysis}
            
        except Exception as e:
            print(f"❌ 프로젝트 분석 실패: {str(e)}")
            return {"score": 50, "analysis": "프로젝트 분석 중 오류가 발생했습니다."}
    
    async def _analyze_growth(self, applicant_data: Dict[str, Any], resume_content: str) -> Dict[str, Any]:
        """자기계발 및 성장 분석"""
        try:
            # 성장 관련 키워드
            growth_keywords = ["성장", "학습", "자기계발", "발전", "향상", "목표", "비전"]
            
            # 키워드 매칭 점수 계산
            keyword_score = self._calculate_keyword_score(resume_content, growth_keywords)
            
            # 성장 정보 완성도 평가
            completeness_score = self._evaluate_completeness(applicant_data, ["growthBackground", "motivation"])
            
            # 학습 의지 평가
            learning_score = self._evaluate_learning_motivation(resume_content)
            
            # 종합 점수 계산
            score = int((keyword_score * 0.3 + completeness_score * 0.4 + learning_score * 0.3))
            
            analysis = f"성장 정보 완성도: {completeness_score}/100, 학습 의지: {learning_score}/100"
            
            return {"score": score, "analysis": analysis}
            
        except Exception as e:
            print(f"❌ 성장 분석 실패: {str(e)}")
            return {"score": 50, "analysis": "성장 분석 중 오류가 발생했습니다."}
    
    async def _analyze_grammar(self, resume_content: str) -> Dict[str, Any]:
        """문법 및 표현 분석"""
        try:
            # 문법 오류 검사
            corrected_text = self.grammar_corrector(resume_content, max_length=512)[0]["generated_text"]
            
            # 원본과 수정된 텍스트 비교
            grammar_score = self._calculate_grammar_score(resume_content, corrected_text)
            
            analysis = f"문법 및 표현 품질: {grammar_score}/100"
            
            return {"score": grammar_score, "analysis": analysis}
            
        except Exception as e:
            print(f"❌ 문법 분석 실패: {str(e)}")
            return {"score": 70, "analysis": "문법 분석 중 오류가 발생했습니다."}
    
    async def _analyze_job_matching(self, applicant_data: Dict[str, Any], resume_content: str) -> Dict[str, Any]:
        """직무 적합성 분석"""
        try:
            # 지원 직무
            target_job = applicant_data.get("position", "")
            
            # 직무별 요구사항 정의
            job_requirements = {
                "백엔드 개발자": ["서버", "API", "데이터베이스", "백엔드", "서버사이드"],
                "프론트엔드 개발자": ["프론트엔드", "UI", "UX", "웹", "클라이언트"],
                "풀스택 개발자": ["풀스택", "전체", "웹", "앱", "통합"],
                "데이터 사이언티스트": ["데이터", "분석", "머신러닝", "통계", "AI"],
                "DevOps 엔지니어": ["DevOps", "배포", "인프라", "클라우드", "자동화"]
            }
            
            # 직무 적합성 점수 계산
            matching_score = self._calculate_job_matching_score(target_job, resume_content, job_requirements)
            
            analysis = f"직무 적합성: {matching_score}/100"
            
            return {"score": matching_score, "analysis": analysis}
            
        except Exception as e:
            print(f"❌ 직무 적합성 분석 실패: {str(e)}")
            return {"score": 70, "analysis": "직무 적합성 분석 중 오류가 발생했습니다."}
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> int:
        """키워드 매칭 점수 계산"""
        if not text or not keywords:
            return 0
        
        text_lower = text.lower()
        matched_count = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        
        return int((matched_count / len(keywords)) * 100)
    
    def _evaluate_completeness(self, data: Dict[str, Any], fields: List[str]) -> int:
        """정보 완성도 평가"""
        if not data or not fields:
            return 0
        
        filled_count = sum(1 for field in fields if data.get(field))
        return int((filled_count / len(fields)) * 100)
    
    def _evaluate_job_relevance(self, position: str, content: str) -> int:
        """직무 연관성 평가"""
        if not position or not content:
            return 50
        
        # 직무별 관련 키워드
        relevance_keywords = {
            "개발자": ["개발", "프로그래밍", "코딩", "소프트웨어"],
            "디자이너": ["디자인", "UI", "UX", "시각", "그래픽"],
            "기획자": ["기획", "전략", "분석", "요구사항"],
            "마케터": ["마케팅", "홍보", "브랜딩", "고객"]
        }
        
        # 직무와 가장 유사한 키워드 찾기
        best_match = 0
        for job_type, keywords in relevance_keywords.items():
            if job_type in position:
                match_score = self._calculate_keyword_score(content, keywords)
                best_match = max(best_match, match_score)
        
        return best_match if best_match > 0 else 50
    
    def _evaluate_experience_duration(self, experience: str) -> int:
        """경력 기간 평가"""
        if not experience:
            return 0
        
        try:
            # 숫자 추출
            import re
            numbers = re.findall(r'\d+', experience)
            if numbers:
                years = int(numbers[0])
                if years >= 5:
                    return 100
                elif years >= 3:
                    return 80
                elif years >= 1:
                    return 60
                else:
                    return 40
        except:
            pass
        
        return 50
    
    def _evaluate_skill_diversity(self, skills: str) -> int:
        """기술 다양성 평가"""
        if not skills:
            return 0
        
        # 쉼표나 공백으로 구분된 기술 개수
        skill_list = [skill.strip() for skill in skills.replace(',', ' ').split() if skill.strip()]
        
        if len(skill_list) >= 8:
            return 100
        elif len(skill_list) >= 6:
            return 80
        elif len(skill_list) >= 4:
            return 60
        elif len(skill_list) >= 2:
            return 40
        else:
            return 20
    
    def _evaluate_project_scale(self, content: str) -> int:
        """프로젝트 규모 평가"""
        if not content:
            return 0
        
        # 프로젝트 규모 관련 키워드
        scale_keywords = ["대규모", "엔터프라이즈", "글로벌", "복잡", "통합", "시스템"]
        small_keywords = ["소규모", "간단", "기본", "단순"]
        
        large_score = self._calculate_keyword_score(content, scale_keywords)
        small_score = self._calculate_keyword_score(content, small_keywords)
        
        if large_score > small_score:
            return 80 + (large_score - small_score) * 0.2
        else:
            return 40 + (small_score - large_score) * 0.3
    
    def _evaluate_learning_motivation(self, content: str) -> int:
        """학습 의지 평가"""
        if not content:
            return 0
        
        # 학습 의지 관련 키워드
        learning_keywords = ["학습", "공부", "연구", "탐구", "도전", "새로운", "최신"]
        
        return self._calculate_keyword_score(content, learning_keywords)
    
    def _calculate_grammar_score(self, original: str, corrected: str) -> int:
        """문법 점수 계산"""
        if not original or not corrected:
            return 70
        
        # 원본과 수정된 텍스트의 길이 차이로 문법 오류 정도 추정
        length_diff = abs(len(original) - len(corrected))
        
        if length_diff == 0:
            return 100
        elif length_diff <= 10:
            return 90
        elif length_diff <= 20:
            return 80
        elif length_diff <= 50:
            return 70
        else:
            return 60
    
    def _calculate_job_matching_score(self, target_job: str, content: str, requirements: Dict[str, List[str]]) -> int:
        """직무 적합성 점수 계산"""
        if not target_job or not content:
            return 50
        
        # 가장 유사한 직무 찾기
        best_match = 0
        for job_type, keywords in requirements.items():
            if job_type in target_job:
                match_score = self._calculate_keyword_score(content, keywords)
                best_match = max(best_match, match_score)
        
        return best_match if best_match > 0 else 50
    
    def _calculate_overall_score(self, analysis_results: Dict[str, Any]) -> int:
        """종합 점수 계산"""
        scores = [
            analysis_results["education"]["score"],
            analysis_results["experience"]["score"],
            analysis_results["skills"]["score"],
            analysis_results["projects"]["score"],
            analysis_results["growth"]["score"],
            analysis_results["grammar"]["score"],
            analysis_results["job_matching"]["score"]
        ]
        
        return int(sum(scores) / len(scores))
    
    def _extract_feedback(self, analysis_results: Dict[str, Any]) -> tuple:
        """강점 및 개선점 추출"""
        strengths = []
        improvements = []
        
        # 점수별 피드백
        for category, result in analysis_results.items():
            score = result["score"]
            if score >= 80:
                strengths.append(f"{category} 영역이 우수합니다")
            elif score <= 50:
                improvements.append(f"{category} 영역을 개선해야 합니다")
        
        return strengths, improvements
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any], improvements: List[str]) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        for improvement in improvements:
            if "기술" in improvement:
                recommendations.append("기술 스택을 더 다양화하고 최신 기술을 학습하세요")
            elif "경력" in improvement:
                recommendations.append("구체적인 프로젝트 경험과 성과를 추가하세요")
            elif "학력" in improvement:
                recommendations.append("학력 정보를 더 상세하게 작성하세요")
            elif "프로젝트" in improvement:
                recommendations.append("프로젝트의 규모와 기여도를 구체적으로 기술하세요")
            elif "성장" in improvement:
                recommendations.append("자기계발 계획과 목표를 명확하게 제시하세요")
        
        return recommendations if recommendations else ["전반적으로 우수한 이력서입니다"]
    
    def _generate_overall_feedback(self, analysis_results: Dict[str, Any], overall_score: int) -> str:
        """종합 피드백 생성"""
        if overall_score >= 90:
            return "전체적으로 매우 우수한 이력서입니다. 모든 영역에서 높은 수준을 보여줍니다."
        elif overall_score >= 80:
            return "전체적으로 우수한 이력서입니다. 일부 영역에서만 개선이 필요합니다."
        elif overall_score >= 70:
            return "전체적으로 양호한 이력서입니다. 몇 가지 영역을 개선하면 더 좋아질 것입니다."
        elif overall_score >= 60:
            return "전체적으로 보통 수준의 이력서입니다. 여러 영역에서 개선이 필요합니다."
        else:
            return "전체적으로 개선이 필요한 이력서입니다. 기본적인 구성과 내용을 보완해야 합니다."
    
    async def batch_analyze(self, applicants_data: list) -> list:
        """일괄 분석"""
        results = []
        
        for i, applicant_data in enumerate(applicants_data):
            try:
                print(f"📊 일괄 분석 진행률: {i+1}/{len(applicants_data)}")
                result = await self.analyze_resume(applicant_data)
                results.append({
                    "applicant_id": applicant_data.get("_id"),
                    "name": applicant_data.get("name"),
                    "analysis_result": result,
                    "success": True
                })
            except Exception as e:
                print(f"❌ {applicant_data.get('name', '알 수 없음')} 분석 실패: {str(e)}")
                results.append({
                    "applicant_id": applicant_data.get("_id"),
                    "name": applicant_data.get("name"),
                    "error": str(e),
                    "success": False
                })
        
        return results

# 사용 예시
if __name__ == "__main__":
    import asyncio
    
    async def test_analyzer():
        analyzer = HuggingFaceResumeAnalyzer()
        
        # 테스트 데이터
        test_applicant = {
            "name": "김철수",
            "position": "백엔드 개발자",
            "department": "개발팀",
            "experience": "2년",
            "skills": "Python, Django, PostgreSQL",
            "growthBackground": "컴퓨터공학 전공",
            "motivation": "기술적 성장을 원함",
            "careerHistory": "웹 개발 2년",
            "extracted_text": "상세한 이력서 내용..."
        }
        
        try:
            result = await analyzer.analyze_resume(test_applicant)
            print("✅ 분석 완료!")
            print(f"종합 점수: {result.overall_score}/100")
            print(f"강점: {result.strengths}")
            print(f"개선점: {result.improvements}")
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
    
    # 테스트 실행
    asyncio.run(test_analyzer())
