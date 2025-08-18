from typing import List, Dict, Any
import re

class ChunkingService:
    def __init__(self):
        """청킹 서비스 초기화"""
        print("청킹 서비스 초기화 완료")
    
    def chunk_resume_text(self, resume: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        이력서를 청킹 단위로 분할합니다.
        
        Args:
            resume (Dict[str, Any]): 이력서 데이터
            
        Returns:
            List[Dict[str, Any]]: 청크 리스트
        """
        chunks = []
        resume_id = str(resume.get("_id", ""))
        
        print(f"[ChunkingService] === 이력서 청킹 시작 ===")
        print(f"[ChunkingService] 이력서 ID: {resume_id}")
        
        # 1. 요약/개요 청크 (summary)
        summary_chunk = self._create_summary_chunk(resume, resume_id)
        if summary_chunk:
            chunks.append(summary_chunk)
        
        # 2. 기술스택/스킬 청크 (skills) - 전체적으로 하나의 청크
        skills_chunk = self._create_skills_chunk(resume, resume_id)
        if skills_chunk:
            chunks.append(skills_chunk)
        
        # 3. 경험 항목별 청크 (experience items)
        experience_chunks = self._create_experience_chunks(resume, resume_id)
        chunks.extend(experience_chunks)
        
        # 4. 교육 항목별 청크 (education items)
        education_chunks = self._create_education_chunks(resume, resume_id)
        chunks.extend(education_chunks)
        
        # 5. 성장배경 청크
        growth_chunk = self._create_growth_background_chunk(resume, resume_id)
        if growth_chunk:
            chunks.append(growth_chunk)
        
        # 6. 지원동기 청크
        motivation_chunk = self._create_motivation_chunk(resume, resume_id)
        if motivation_chunk:
            chunks.append(motivation_chunk)
        
        # 7. 경력사항 청크
        career_chunk = self._create_career_history_chunk(resume, resume_id)
        if career_chunk:
            chunks.append(career_chunk)
        
        print(f"[ChunkingService] 총 {len(chunks)}개 청크 생성 완료")
        for i, chunk in enumerate(chunks):
            print(f"[ChunkingService] 청크 {i+1}: {chunk['chunk_type']} - {len(chunk['text'])} 문자")
        print(f"[ChunkingService] === 이력서 청킹 완료 ===")
        
        return chunks
    
    def _create_summary_chunk(self, resume: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """요약/개요 청크 생성"""
        # resume_text가 있는 경우 첫 부분을 요약으로 사용
        resume_text = resume.get("resume_text", "").strip()
        if resume_text:
            # 첫 200자 정도를 요약으로 간주
            summary_text = resume_text[:200]
        else:
            # 기본 정보들을 요약으로 구성
            name = resume.get("name", "")
            position = resume.get("position", "")
            department = resume.get("department", "")
            
            summary_parts = []
            if name:
                summary_parts.append(f"이름: {name}")
            if position:
                summary_parts.append(f"지원직무: {position}")
            if department:
                summary_parts.append(f"희망부서: {department}")
            
            summary_text = " ".join(summary_parts)
        
        if summary_text:
            return {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_summary",
                "chunk_type": "summary",
                "text": summary_text.strip(),
                "metadata": {
                    "section": "summary",
                    "original_field": "summary"
                }
            }
        return None
    
    def _create_skills_chunk(self, resume: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """기술스택/스킬 청크 생성"""
        skills = resume.get("skills", "").strip()
        
        if skills:
            return {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_skills",
                "chunk_type": "skills",
                "text": f"기술스택: {skills}",
                "metadata": {
                    "section": "skills",
                    "original_field": "skills"
                }
            }
        return None
    
    def _create_experience_chunks(self, resume: Dict[str, Any], resume_id: str) -> List[Dict[str, Any]]:
        """경험 항목별 청크 생성"""
        chunks = []
        
        # experience 필드에서 경험 추출
        experience = resume.get("experience", "").strip()
        if experience:
            # 경험을 개별 항목으로 분할 (줄바꿈, 숫자., - 등으로 구분)
            experience_items = self._split_into_items(experience)
            
            for i, item in enumerate(experience_items):
                if item.strip():
                    chunks.append({
                        "resume_id": resume_id,
                        "chunk_id": f"{resume_id}_experience_{i+1}",
                        "chunk_type": "experience",
                        "text": f"경험: {item.strip()}",
                        "metadata": {
                            "section": "experience",
                            "item_index": i+1,
                            "original_field": "experience"
                        }
                    })
        
        return chunks
    
    def _create_education_chunks(self, resume: Dict[str, Any], resume_id: str) -> List[Dict[str, Any]]:
        """교육 항목별 청크 생성"""
        chunks = []
        
        # education 필드가 있다면 사용
        education = resume.get("education", "").strip()
        if education:
            education_items = self._split_into_items(education)
            
            for i, item in enumerate(education_items):
                if item.strip():
                    chunks.append({
                        "resume_id": resume_id,
                        "chunk_id": f"{resume_id}_education_{i+1}",
                        "chunk_type": "education",
                        "text": f"교육: {item.strip()}",
                        "metadata": {
                            "section": "education",
                            "item_index": i+1,
                            "original_field": "education"
                        }
                    })
        
        return chunks
    
    def _create_growth_background_chunk(self, resume: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """성장배경 청크 생성"""
        growth_background = resume.get("growthBackground", "").strip()
        
        if growth_background:
            return {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_growth_background",
                "chunk_type": "growth_background",
                "text": f"성장배경: {growth_background}",
                "metadata": {
                    "section": "growth_background",
                    "original_field": "growthBackground"
                }
            }
        return None
    
    def _create_motivation_chunk(self, resume: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """지원동기 청크 생성"""
        motivation = resume.get("motivation", "").strip()
        
        if motivation:
            return {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_motivation",
                "chunk_type": "motivation",
                "text": f"지원동기: {motivation}",
                "metadata": {
                    "section": "motivation",
                    "original_field": "motivation"
                }
            }
        return None
    
    def _create_career_history_chunk(self, resume: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """경력사항 청크 생성"""
        career_history = resume.get("careerHistory", "").strip()
        
        if career_history:
            return {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_career_history",
                "chunk_type": "career_history",
                "text": f"경력사항: {career_history}",
                "metadata": {
                    "section": "career_history",
                    "original_field": "careerHistory"
                }
            }
        return None
    
    def _split_into_items(self, text: str) -> List[str]:
        """텍스트를 개별 항목으로 분할"""
        if not text:
            return []
        
        # 다양한 구분자로 분할
        # 1. 숫자와 점 (1. 2. 3.)
        # 2. 대시 (-, •, -, ●)
        # 3. 줄바꿈으로 구분된 항목
        
        # 먼저 명확한 구분자들로 분할
        items = re.split(r'(?:\d+\.|[-•●▪▫]|\n\s*[-•●▪▫]?|\n\s*\d+\.)', text)
        
        # 빈 항목 제거 및 정리
        cleaned_items = []
        for item in items:
            item = item.strip()
            if item and len(item) > 10:  # 너무 짧은 항목은 제외
                cleaned_items.append(item)
        
        # 분할된 항목이 없으면 원본 텍스트를 하나의 항목으로 반환
        if not cleaned_items and text.strip():
            cleaned_items = [text.strip()]
        
        return cleaned_items