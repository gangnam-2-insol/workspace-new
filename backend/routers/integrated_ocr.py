from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import os
import tempfile
from pathlib import Path
from datetime import datetime
import json

# GPT-4o-mini Vision API 기반 PDF OCR 모듈 import
from pdf_ocr_module.main import process_pdf
from pdf_ocr_module.config import Settings
from pdf_ocr_module.ai_analyzer import analyze_text
from pdf_ocr_module.mongo_saver import MongoSaver
from models.applicant import ApplicantCreate
from chunking_service import ChunkingService

router = APIRouter(tags=["integrated-ocr"])

def serialize_mongo_data(data):
    """MongoDB 데이터를 JSON 직렬화 가능한 형태로 변환합니다."""
    if data is None:
        return None
    
    try:
        # ObjectId를 문자열로 변환
        from bson import ObjectId
        if isinstance(data, ObjectId):
            return str(data)
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {key: serialize_mongo_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [serialize_mongo_data(item) for item in data]
        else:
            return data
    except ImportError:
        # bson이 없는 경우 datetime만 처리
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {key: serialize_mongo_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [serialize_mongo_data(item) for item in data]
        else:
            return data

# MongoDB 서비스 의존성
def get_mongo_saver():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    return MongoSaver(mongo_uri)


def _extract_contact_from_text(text: str) -> Dict[str, Optional[str]]:
    """텍스트에서 이메일/전화번호/이름 후보를 단순 추출합니다."""
    import re
    
    # 이메일 추출
    email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
    first_email = email_matches[0] if email_matches else None
    
    # 전화번호 추출 (더 다양한 형식 지원)
    phone_patterns = [
        r'\b\d{2,3}[-\.\s]?\d{3,4}[-\.\s]?\d{4}\b',  # 010-1234-5678
        r'\b\d{3}[-\.\s]?\d{4}[-\.\s]?\d{4}\b',      # 010-1234-5678
        r'\b\d{10,11}\b'                              # 01012345678
    ]
    first_phone = None
    for pattern in phone_patterns:
        phone_matches = re.findall(pattern, text)
        if phone_matches:
            first_phone = phone_matches[0]
            break
    
    # 이름 추출 (더 정교한 패턴)
    name_patterns = [
        r'(?:이름|성명|Name|name)\s*[:\-]?\s*([가-힣]{2,4})',  # 이름: 김철수
        r'(?:개인정보|Personal Information)\s*[:\-]?\s*([가-힣]{2,4})',  # 개인정보: 김철수
        r'([가-힣]{2,4})\s*(?:님|씨|군|양)',  # 김철수님
        r'([가-힣]{2,4})\s*[,，]',  # 김철수,
        r'^([가-힣]{2,4})\n',  # 문서 맨 위 독립적인 이름
        r'(?:그래픽디자이너|디자이너|개발자|프로그래머|엔지니어|기획자|마케터|영업|인사|회계)\s*[,，]\s*([가-힣]{2,4})',  # 직책과 함께
    ]
    
    guessed_name = None
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            guessed_name = match.group(1)
            break
    
    # 이메일에서 이름 추출 (백업)
    if not guessed_name and first_email:
        local = first_email.split('@')[0]
        # 숫자나 특수문자가 많은 경우 제외
        if len(re.findall(r'[0-9_]', local)) < len(local) * 0.3:
            guessed_name = local.replace('.', ' ').replace('_', ' ').strip()
    
    return {"email": first_email, "phone": first_phone, "name": guessed_name}


def _build_applicant_data(name: Optional[str], email: Optional[str], phone: Optional[str], ocr_result: Dict[str, Any], job_posting_id: Optional[str] = None) -> ApplicantCreate:
    """OCR 결과와 AI 분석 결과를 종합하여 지원자 데이터를 생성합니다."""
    
    # 1. Vision API 분석 결과 우선 확인 (가장 정확함)
    vision_analysis = ocr_result.get("vision_analysis", {})
    vision_name = vision_analysis.get("name", "")
    vision_email = vision_analysis.get("email", "")
    vision_phone = vision_analysis.get("phone", "")
    vision_position = vision_analysis.get("position", "")
    vision_company = vision_analysis.get("company", "")
    vision_education = vision_analysis.get("education", "")
    vision_skills = vision_analysis.get("skills", "")
    
    # 2. AI 분석 결과에서 기본 정보 추출 (두 가지 구조 모두 확인)
    # 구조 1: ocr_result.basic_info (배열 형태)
    ai_basic_info = ocr_result.get("basic_info", {})
    ai_names = ai_basic_info.get("names", [])
    ai_emails = ai_basic_info.get("emails", [])
    ai_phones = ai_basic_info.get("phones", [])
    
    # 구조 2: ocr_result.structured_data.basic_info (단일 값 형태)
    structured_data = ocr_result.get("structured_data", {})
    structured_basic_info = structured_data.get("basic_info", {})
    
    ai_single_name = structured_basic_info.get("name", "")
    ai_single_email = structured_basic_info.get("email", "")
    ai_single_phone = structured_basic_info.get("phone", "")
    ai_position = structured_basic_info.get("position", "")
    
    # 2. 텍스트에서 직접 추출 (백업용)
    text = ocr_result.get("extracted_text", "") or ocr_result.get("full_text", "") or ""
    extracted = _extract_contact_from_text(text)
    
    # 4. 우선순위에 따라 최종 값 결정
    # 이름: Vision API > Form 입력 > AI 단일 값 > AI 배열 첫 번째 > 텍스트 추출 > 기본값
    final_name = (
        vision_name or
        name or 
        ai_single_name or
        (ai_names[0] if ai_names else None) or 
        extracted.get("name") or 
        "이름미상"
    )
    
    # 이메일: Vision API > Form 입력 > AI 단일 값 > AI 배열 첫 번째 > 텍스트 추출 > 기본값
    final_email = (
        vision_email or
        email or 
        ai_single_email or
        (ai_emails[0] if ai_emails else None) or 
        extracted.get("email") or 
        f"unknown_{int(datetime.utcnow().timestamp())}@noemail.local"
    )
    
    # 전화번호: Vision API > Form 입력 > AI 단일 값 > AI 배열 첫 번째 > 텍스트 추출
    final_phone = (
        vision_phone or
        phone or 
        ai_single_phone or
        (ai_phones[0] if ai_phones else None) or 
        extracted.get("phone")
    )
    
    # 5. 추가 정보 추출 (Vision API 우선, AI 분석 결과 백업)
    # 직무/포지션
    final_position = vision_position or ai_position or _extract_position_from_text(text)
    
    # 기술 스택 (Vision API에서 추출된 스킬 우선)
    if vision_skills:
        final_skills = vision_skills
    else:
        final_skills = _extract_skills_from_text(text)
    
    # 경력 정보
    final_experience = _extract_experience_from_text(text)
    
    # 부서 (기본값)
    final_department = "개발"  # 기본값
    
    # 성장 배경 (Vision API 요약 우선)
    vision_summary = vision_analysis.get("summary", "")
    if vision_summary:
        final_growth_background = vision_summary[:200] + "..." if len(vision_summary) > 200 else vision_summary
    else:
        final_growth_background = ocr_result.get("summary", "")[:200] + "..." if ocr_result.get("summary") else ""
    
    # 지원 동기 (기본값)
    final_motivation = "이력서를 통해 지원자의 역량과 경험을 확인했습니다."
    
    # 경력 사항 (Vision API 요약 우선)
    if vision_summary:
        final_career_history = vision_summary[:300] + "..." if len(vision_summary) > 300 else vision_summary
    else:
        final_career_history = ocr_result.get("summary", "")[:300] + "..." if ocr_result.get("summary") else ""
    
    # 분석 점수 (기본값)
    final_analysis_score = 65  # 기본값
    
    # 분석 결과 (Vision API 요약 우선)
    if vision_summary:
        final_analysis_result = vision_summary[:100] + "..." if len(vision_summary) > 100 else vision_summary
    else:
        final_analysis_result = ocr_result.get("summary", "")[:100] + "..." if ocr_result.get("summary") else ""
    
    # 6. 디버깅을 위한 로그 (개발 중에만 사용)
    print(f"🔍 지원자 정보 추출 결과:")
    print(f"  - OCR 결과 구조: {list(ocr_result.keys())}")
    print(f"  - Vision API 결과: name={vision_name}, email={vision_email}, phone={vision_phone}, position={vision_position}")
    print(f"  - AI 분석 결과 (배열): names={ai_names}, emails={ai_emails}, phones={ai_phones}")
    print(f"  - AI 분석 결과 (단일): name={ai_single_name}, email={ai_single_email}, phone={ai_single_phone}, position={ai_position}")
    print(f"  - structured_data 구조: {list(structured_data.keys()) if structured_data else 'None'}")
    print(f"  - 텍스트 추출 결과: {extracted}")
    print(f"  - 최종 결정: name={final_name}, email={final_email}, phone={final_phone}, position={final_position}")
    
    # 경력 정보를 숫자로 변환 (머지용 프로젝트 구조에 맞춤)
    experience_years = 0
    if final_experience:
        # "3년", "1-3년", "신입" 등의 패턴에서 숫자 추출
        import re
        numbers = re.findall(r'\d+', final_experience)
        if numbers:
            experience_years = int(numbers[0])
        elif "신입" in final_experience:
            experience_years = 0
    
    # 스킬을 배열로 변환 (머지용 프로젝트 구조에 맞춤)
    skills_list = []
    if final_skills:
        if isinstance(final_skills, str):
            # 콤마, 슬래시, 공백으로 구분된 스킬을 배열로 변환
            skills_list = [skill.strip() for skill in re.split(r'[,/\s]+', final_skills) if skill.strip()]
        elif isinstance(final_skills, list):
            skills_list = final_skills
    
    # 스킬을 문자열로 변환 (현재 프로젝트 모델에 맞춤)
    if skills_list:
        final_skills_str = ", ".join(str(skill) for skill in skills_list if skill)
    else:
        final_skills_str = ""
    
    return ApplicantCreate(
        name=final_name,
        email=final_email,
        phone=final_phone,
        position=final_position,
        department=final_department,
        experience=final_experience,
        skills=final_skills_str,
        growthBackground=final_growth_background,
        motivation=final_motivation,
        careerHistory=final_career_history,
        analysisScore=final_analysis_score,
        analysisResult=final_analysis_result,
        status="pending",
        job_posting_id=job_posting_id if job_posting_id else None
    )


def _extract_position_from_text(text: str) -> str:
    """텍스트에서 직무/포지션을 추출합니다."""
    import re
    
    position_patterns = [
        r'(?:직무|포지션|직책|담당|역할)\s*[:\-]?\s*([가-힣A-Za-z\s]+)',
        r'(프론트엔드|백엔드|풀스택|데이터|DevOps|모바일|AI|UI/UX|디자이너|기획자|마케터|영업|인사|회계)',
        r'(개발자|엔지니어|프로그래머|디자이너|기획자|마케터|영업|인사|회계)',
    ]
    
    for pattern in position_patterns:
        match = re.search(pattern, text)
        if match:
            position = match.group(1).strip()
            if position:
                return position
    
    return "개발자"  # 기본값


def _extract_skills_from_text(text: str) -> str:
    """텍스트에서 기술 스택을 추출합니다."""
    import re
    
    # 기술 스택 키워드
    skill_keywords = [
        # 프로그래밍 언어
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Kotlin", "Swift",
        # 프레임워크/라이브러리
        "React", "Vue", "Angular", "Node.js", "Express", "Django", "Flask", "Spring", "Spring Boot",
        # 데이터베이스
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQLite",
        # 클라우드/인프라
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Git",
        # 기타
        "HTML", "CSS", "Sass", "Less", "Webpack", "Babel", "GraphQL", "REST API"
    ]
    
    found_skills = []
    for skill in skill_keywords:
        if skill.lower() in text.lower() or skill in text:
            found_skills.append(skill)
    
    if found_skills:
        return ", ".join(found_skills[:5])  # 최대 5개까지만
    
    return "기술 스택 정보 없음"


def _extract_experience_from_text(text: str) -> str:
    """텍스트에서 경력 정보를 추출합니다."""
    import re
    
    experience_patterns = [
        r'(\d+)\s*년\s*경력',
        r'경력\s*(\d+)\s*년',
        r'(\d+)\s*년\s*차',
        r'신입|주니어|미드레벨|시니어|리드',
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, text)
        if match:
            if pattern == r'신입|주니어|미드레벨|시니어|리드':
                return match.group(0)
            else:
                years = int(match.group(1))
                if years == 0:
                    return "신입"
                elif years <= 2:
                    return "1-3년"
                elif years <= 5:
                    return "3-5년"
                else:
                    return "5년 이상"
    
    return "경력 정보 없음"


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """PDF 파일을 업로드하고 OCR 처리를 수행합니다."""
    try:
        # 파일 유효성 검사
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)
        
        try:
            # PDF 처리
            result = process_pdf(tmp_path)
            
            # 연락처 정보 추출
            contact_info = _extract_contact_from_text(result.get("full_text", ""))
            
            # Vision 분석 결과가 있으면 우선 사용
            vision_analysis = result.get("vision_analysis", {})
            if vision_analysis and isinstance(vision_analysis, dict):
                contact_info.update({
                    "name": vision_analysis.get("name", contact_info.get("name")),
                    "email": vision_analysis.get("email", contact_info.get("email")),
                    "phone": vision_analysis.get("phone", contact_info.get("phone")),
                    "position": vision_analysis.get("position", ""),
                    "company": vision_analysis.get("company", ""),
                    "education": vision_analysis.get("education", ""),
                    "skills": vision_analysis.get("skills", ""),
                    "address": vision_analysis.get("address", "")
                })
            
            # 응답 데이터 구성
            response_data = {
                "success": True,
                "message": "PDF 처리 완료",
                "data": {
                    "mongo_id": result.get("mongo_id"),
                    "file_name": result.get("file_name"),
                    "num_pages": result.get("num_pages"),
                    "summary": result.get("summary"),
                    "keywords": result.get("keywords", []),
                    "contact_info": contact_info,
                    "vision_analysis": vision_analysis,
                    "processing_info": {
                        "used_ocr": result.get("processing_info", {}).get("used_ocr", False),
                        "embedded_text_length": result.get("processing_info", {}).get("embedded_text_length", 0),
                        "total_text_length": result.get("processing_info", {}).get("total_text_length", 0)
                    }
                }
            }
            
            return JSONResponse(content=response_data)
            
        finally:
            # 임시 파일 삭제
            if tmp_path.exists():
                tmp_path.unlink()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 처리 중 오류가 발생했습니다: {str(e)}")


@router.post("/analyze-text")
async def analyze_text_endpoint(
    text: str = Form(...),
    settings: Settings = Depends(lambda: Settings())
):
    """텍스트 분석을 수행합니다."""
    try:
        analysis = analyze_text(text, settings)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "summary": analysis.get("summary", ""),
                "keywords": analysis.get("keywords", []),
                "basic_info": analysis.get("basic_info", {}),
                "structured_data": analysis.get("structured_data", {})
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/documents/{mongo_id}")
async def get_document(
    mongo_id: str,
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """MongoDB에서 문서를 조회합니다."""
    try:
        document = mongo_saver.get_document_by_id(mongo_id)
        if not document:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
        
        # JSON 직렬화 가능한 형태로 변환
        serialized_doc = serialize_mongo_data(document)
        
        return JSONResponse(content={
            "success": True,
            "data": serialized_doc
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """문서 목록을 조회합니다."""
    try:
        documents = mongo_saver.get_documents(skip=skip, limit=limit)
        
        # JSON 직렬화 가능한 형태로 변환
        serialized_docs = [serialize_mongo_data(doc) for doc in documents]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "documents": serialized_docs,
                "total": len(serialized_docs),
                "skip": skip,
                "limit": limit
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 목록 조회 중 오류가 발생했습니다: {str(e)}")


@router.delete("/documents/{mongo_id}")
async def delete_document(
    mongo_id: str,
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """문서를 삭제합니다."""
    try:
        result = mongo_saver.delete_document(mongo_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="삭제할 문서를 찾을 수 없습니다.")
        
        return JSONResponse(content={
            "success": True,
            "message": "문서가 성공적으로 삭제되었습니다."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 삭제 중 오류가 발생했습니다: {str(e)}")


@router.get("/health")
async def health_check():
    """서비스 상태를 확인합니다."""
    return JSONResponse(content={
        "success": True,
        "message": "OCR 서비스가 정상적으로 작동 중입니다.",
        "timestamp": datetime.now().isoformat()
    })


@router.post("/upload-multiple-documents")
async def upload_multiple_documents(
    resume_file: Optional[UploadFile] = File(None),
    cover_letter_file: Optional[UploadFile] = File(None),
    portfolio_file: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    job_posting_id: Optional[str] = Form("default_job_posting"),
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """여러 문서를 한 번에 업로드하고 OCR 처리 후 하나의 지원자 레코드로 통합 저장합니다."""
    try:
        # 최소 하나의 파일은 필요
        if not resume_file and not cover_letter_file and not portfolio_file:
            raise HTTPException(status_code=400, detail="최소 하나의 문서 파일이 필요합니다")
        
        # job_posting_id 기본값 설정
        if not job_posting_id or job_posting_id == "default_job_posting":
            job_posting_id = "default_job_posting"
        
        results = {}
        temp_files = []
        applicant_id = None
        
        # 1. 이력서 처리 (우선순위 1)
        if resume_file:
            if not resume_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="이력서는 PDF 파일만 업로드 가능합니다")
            
            print(f"📄 이력서 처리 시작: {resume_file.filename}")
            print(f"📄 이력서 파일 크기: {resume_file.size} bytes")
            print(f"📄 이력서 파일 타입: {resume_file.content_type}")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await resume_file.read()
                temp_file.write(content)
                temp_file_path = Path(temp_file.name)
                temp_files.append(temp_file_path)
            
            try:
                # OCR 처리
                print(f"🔍 이력서 OCR 처리 중...")
                ocr_result = process_pdf(str(temp_file_path))
                
                # AI 분석 결과 가져오기 (Vision API 포함)
                print(f"🤖 이력서 AI 분석 중...")
                settings = Settings()
                
                # OCR에서 이미지 경로가 있는지 확인하고 Vision API 사용
                if ocr_result.get("used_ocr") and ocr_result.get("image_paths"):
                    from pdf_ocr_module.ai_analyzer import analyze_text_with_vision
                    ai_analysis = analyze_text_with_vision(
                        ocr_result.get("image_paths", []), 
                        ocr_result.get("full_text", ""), 
                        settings
                    )
                else:
                    ai_analysis = analyze_text(ocr_result.get("full_text", ""), settings)
                
                # 임시로 지원자 기본 정보 미리 추출 (ChunkingService용)
                temp_ocr_result = {
                    "extracted_text": ocr_result.get("full_text", ""),
                    "summary": ai_analysis.get("summary", ""),
                    "keywords": ai_analysis.get("keywords", []),
                    "basic_info": ai_analysis.get("basic_info", {}),
                    "structured_data": ai_analysis.get("structured_data", {}),
                    "vision_analysis": ai_analysis.get("vision_analysis", {}),
                }
                temp_applicant = _build_applicant_data(name, email, phone, temp_ocr_result, job_posting_id)
                
                # OCR 결과에 AI 분석 결과 추가
                enhanced_ocr_result = {
                    "extracted_text": ocr_result.get("full_text", ""),
                    "resume_text": ocr_result.get("full_text", ""),  # ChunkingService에서 fallback용
                    "summary": ai_analysis.get("summary", "") or "이력서 분석 결과",
                    "keywords": ai_analysis.get("keywords", []) or ["이력서"],
                    "basic_info": ai_analysis.get("basic_info", {}) or {
                        "names": [temp_applicant.name] if temp_applicant.name and temp_applicant.name != "이름미상" else [],
                        "emails": [temp_applicant.email] if temp_applicant.email and "@" in temp_applicant.email else [],
                        "phones": [temp_applicant.phone] if temp_applicant.phone else [],
                        "name": temp_applicant.name,
                        "email": temp_applicant.email,
                        "phone": temp_applicant.phone
                    },
                    "structured_data": ai_analysis.get("structured_data", {}),
                    "vision_analysis": ai_analysis.get("vision_analysis", {}),
                    "document_type": "resume",
                    "pages": ocr_result.get("num_pages", 0),
                    "used_ocr": ocr_result.get("used_ocr", False)
                }
                
                # 지원자 데이터 생성
                applicant_data = _build_applicant_data(name, email, phone, enhanced_ocr_result, job_posting_id)
                
                # 디버깅을 위한 지원자 데이터 출력
                print(f"🔍 생성된 지원자 데이터: name={applicant_data.name}, email={applicant_data.email}, phone={applicant_data.phone}")
                
                # MongoDB에 저장
                result = await mongo_saver.save_resume_with_ocr(
                    ocr_result=enhanced_ocr_result,
                    applicant_data=applicant_data,
                    job_posting_id=job_posting_id,
                    file_path=temp_file_path
                )
                
                results["resume"] = result
                applicant_id = result.get("applicant", {}).get("id")
                
                # 결과 구조 디버깅
                print(f"🔍 MongoDB 저장 결과 구조: {list(result.keys())}")
                print(f"🔍 applicant 키 내용: {result.get('applicant', 'None')}")
                
                print(f"✅ 이력서 처리 완료: {applicant_id}")
                print(f"📊 이력서 결과: {result.get('message', 'N/A')}")
                # 올바른 구조로 지원자 정보 접근
                applicant_info = result.get('applicant', {}).get('applicant', {})
                print(f"👤 지원자 정보: {applicant_info.get('name', 'N/A')} ({applicant_info.get('email', 'N/A')})")
                
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                print(f"❌ 이력서 처리 실패: {e}")
                print(f"🔍 이력서 에러 상세 정보:")
                print(error_traceback)
                
                error_message = f"이력서 처리 실패: {str(e)}"
                if hasattr(e, '__traceback__'):
                    error_message += f"\n\n상세 정보: {error_traceback}"
                
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": "이력서 처리 실패",
                        "detail": error_message,
                        "timestamp": datetime.now().isoformat()
                    }
                )
        
        # 2. 자기소개서 처리 (기존 지원자에 연결)
        if cover_letter_file:
            if not cover_letter_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="자기소개서는 PDF 파일만 업로드 가능합니다")
            
            print(f"📝 자기소개서 처리 시작: {cover_letter_file.filename}")
            print(f"📝 자기소개서 파일 크기: {cover_letter_file.size} bytes")
            print(f"📝 자기소개서 파일 타입: {cover_letter_file.content_type}")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await cover_letter_file.read()
                temp_file.write(content)
                temp_file_path = Path(temp_file.name)
                temp_files.append(temp_file_path)
            
            try:
                # OCR 처리
                print(f"🔍 자기소개서 OCR 처리 중...")
                ocr_result = process_pdf(str(temp_file_path))
                
                # AI 분석 결과 가져오기
                print(f"🤖 자기소개서 AI 분석 중...")
                settings = Settings()
                ai_analysis = analyze_text(ocr_result.get("full_text", ""), settings)
                
                # OCR 결과에 AI 분석 결과 추가
                enhanced_ocr_result = {
                    "extracted_text": ocr_result.get("full_text", ""),
                    "summary": ai_analysis.get("summary", ""),
                    "keywords": ai_analysis.get("keywords", []),
                    "basic_info": ai_analysis.get("basic_info", {}),
                    "structured_data": ai_analysis.get("structured_data", {}),
                    "document_type": "cover_letter",
                    "pages": ocr_result.get("num_pages", 0)
                }
                
                # 기존 지원자 데이터 사용 또는 새로 생성
                if applicant_id:
                    # 기존 지원자 정보 가져오기
                    existing_applicant = mongo_saver.mongo_service.get_applicant_by_id_sync(applicant_id)
                    if existing_applicant:
                        applicant_data = ApplicantCreate(
                            name=existing_applicant.get("name", name),
                            email=existing_applicant.get("email", email),
                            phone=existing_applicant.get("phone", phone),
                            position=existing_applicant.get("position", ""),
                            department=existing_applicant.get("department", ""),
                            experience=existing_applicant.get("experience", ""),
                            skills=existing_applicant.get("skills", ""),
                            growthBackground=existing_applicant.get("growthBackground", ""),
                            motivation=existing_applicant.get("motivation", ""),
                            careerHistory=existing_applicant.get("careerHistory", ""),
                            analysisScore=existing_applicant.get("analysisScore", 0),
                            analysisResult=existing_applicant.get("analysisResult", ""),
                            status=existing_applicant.get("status", "pending"),
                            job_posting_id=job_posting_id
                        )
                    else:
                        applicant_data = _build_applicant_data(name, email, phone, enhanced_ocr_result, job_posting_id)
                else:
                    applicant_data = _build_applicant_data(name, email, phone, enhanced_ocr_result, job_posting_id)
                
                # MongoDB에 저장
                result = await mongo_saver.save_cover_letter_with_ocr(
                    ocr_result=enhanced_ocr_result,
                    applicant_data=applicant_data,
                    job_posting_id=job_posting_id,
                    file_path=temp_file_path
                )
                
                results["cover_letter"] = result
                if not applicant_id:
                    applicant_id = result.get("applicant", {}).get("id")
                
                print(f"✅ 자기소개서 처리 완료: {applicant_id}")
                print(f"📊 자기소개서 결과: {result.get('message', 'N/A')}")
                # 올바른 구조로 지원자 정보 접근
                applicant_info = result.get('applicant', {}).get('applicant', {})
                print(f"👤 지원자 정보: {applicant_info.get('name', 'N/A')} ({applicant_info.get('email', 'N/A')})")
                
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                print(f"❌ 자기소개서 처리 실패: {e}")
                print(f"🔍 자기소개서 에러 상세 정보:")
                print(error_traceback)
                raise HTTPException(status_code=500, detail=f"자기소개서 처리 실패: {str(e)}\n\n상세 정보: {error_traceback}")
        
        # 3. 포트폴리오 처리 (기존 지원자에 연결)
        if portfolio_file:
            if not portfolio_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="포트폴리오는 PDF 파일만 업로드 가능합니다")
            
            print(f"📁 포트폴리오 처리 시작: {portfolio_file.filename}")
            print(f"📁 포트폴리오 파일 크기: {portfolio_file.size} bytes")
            print(f"📁 포트폴리오 파일 타입: {portfolio_file.content_type}")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await portfolio_file.read()
                temp_file.write(content)
                temp_file_path = Path(temp_file.name)
                temp_files.append(temp_file_path)
            
            try:
                # OCR 처리
                print(f"🔍 포트폴리오 OCR 처리 중...")
                ocr_result = process_pdf(str(temp_file_path))
                
                # AI 분석 결과 가져오기
                print(f"🤖 포트폴리오 AI 분석 중...")
                settings = Settings()
                ai_analysis = analyze_text(ocr_result.get("full_text", ""), settings)
                
                # OCR 결과에 AI 분석 결과 추가
                enhanced_ocr_result = {
                    "extracted_text": ocr_result.get("full_text", ""),
                    "summary": ai_analysis.get("summary", ""),
                    "keywords": ai_analysis.get("keywords", []),
                    "basic_info": ai_analysis.get("basic_info", {}),
                    "structured_data": ai_analysis.get("structured_data", {}),
                    "document_type": "portfolio",
                    "pages": ocr_result.get("num_pages", 0)
                }
                
                # 기존 지원자 데이터 사용 또는 새로 생성
                if applicant_id:
                    # 기존 지원자 정보 가져오기
                    existing_applicant = mongo_saver.mongo_service.get_applicant_by_id_sync(applicant_id)
                    if existing_applicant:
                        applicant_data = ApplicantCreate(
                            name=existing_applicant.get("name", name),
                            email=existing_applicant.get("email", email),
                            phone=existing_applicant.get("phone", phone),
                            position=existing_applicant.get("position", ""),
                            department=existing_applicant.get("department", ""),
                            experience=existing_applicant.get("experience", ""),
                            skills=existing_applicant.get("skills", ""),
                            growthBackground=existing_applicant.get("growthBackground", ""),
                            motivation=existing_applicant.get("motivation", ""),
                            careerHistory=existing_applicant.get("careerHistory", ""),
                            analysisScore=existing_applicant.get("analysisScore", 0),
                            analysisResult=existing_applicant.get("analysisResult", ""),
                            status=existing_applicant.get("status", "pending"),
                            job_posting_id=job_posting_id
                        )
                    else:
                        applicant_data = _build_applicant_data(name, email, phone, enhanced_ocr_result, job_posting_id)
                else:
                    applicant_data = _build_applicant_data(name, email, phone, enhanced_ocr_result, job_posting_id)
                
                # MongoDB에 저장
                result = await mongo_saver.save_portfolio_with_ocr(
                    ocr_result=enhanced_ocr_result,
                    applicant_data=applicant_data,
                    job_posting_id=job_posting_id,
                    file_path=temp_file_path
                )
                
                results["portfolio"] = result
                if not applicant_id:
                    applicant_id = result.get("applicant", {}).get("id")
                
                print(f"✅ 포트폴리오 처리 완료: {applicant_id}")
                print(f"📊 포트폴리오 결과: {result.get('message', 'N/A')}")
                # 올바른 구조로 지원자 정보 접근
                applicant_info = result.get('applicant', {}).get('applicant', {})
                print(f"👤 지원자 정보: {applicant_info.get('name', 'N/A')} ({applicant_info.get('email', 'N/A')})")
                
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                print(f"❌ 포트폴리오 처리 실패: {e}")
                print(f"🔍 포트폴리오 에러 상세 정보:")
                print(error_traceback)
                raise HTTPException(status_code=500, detail=f"포트폴리오 처리 실패: {str(e)}\n\n상세 정보: {error_traceback}")
        
        # 임시 파일들 정리
        print(f"🧹 임시 파일 정리 중... ({len(temp_files)}개 파일)")
        for temp_file_path in temp_files:
            if temp_file_path.exists():
                temp_file_path.unlink()
        
        print(f"✅ 모든 문서 처리 완료! 지원자 ID: {applicant_id}")
        print(f"📊 업로드된 문서: {list(results.keys())}")
        
        # 최종 지원자 정보 가져오기
        final_applicant_info = None
        if applicant_id:
            final_applicant_info = mongo_saver.mongo_service.get_applicant_by_id_sync(applicant_id)
            # ObjectId를 문자열로 직렬화
            final_applicant_info = serialize_mongo_data(final_applicant_info)
        
        # 프론트엔드 호환성을 위한 결과 구조 변경
        processed_results = {}
        for doc_type, result_data in results.items():
            processed_results[doc_type] = {
                **result_data,
                # 중첩된 applicant 구조를 평면화
                "applicant": result_data.get("applicant", {}).get("applicant", {})
            }
        
        # 최종 결과 반환
        return JSONResponse(content={
            "success": True,
            "message": "모든 문서 OCR 처리 및 저장 완료",
            "data": {
                "applicant_id": applicant_id,
                "applicant_info": final_applicant_info,
                "results": serialize_mongo_data(processed_results),
                "uploaded_documents": list(results.keys())
            }
        })
        
    except Exception as e:
        # 임시 파일들 정리
        for temp_file_path in temp_files:
            if temp_file_path.exists():
                temp_file_path.unlink()
        
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ 통합 문서 처리 실패: {e}")
        print(f"🔍 에러 상세 정보:")
        print(error_traceback)
        
        # 더 명확한 에러 메시지 생성
        error_message = f"문서 처리 실패: {str(e)}"
        if hasattr(e, '__traceback__'):
            error_message += f"\n\n상세 정보: {error_traceback}"
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "문서 처리 실패",
                "detail": error_message,
                "timestamp": datetime.now().isoformat()
            }
        )
    finally:
        mongo_saver.close()
