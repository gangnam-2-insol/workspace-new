from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import os
import tempfile
from pathlib import Path
from datetime import datetime

# GPT-4o-mini Vision API 기반 PDF OCR 모듈 import
from pdf_ocr_module.main import process_pdf
from pdf_ocr_module.config import Settings
from pdf_ocr_module.ai_analyzer import analyze_text
from pdf_ocr_module.mongo_saver import MongoSaver
from models.applicant import ApplicantCreate

router = APIRouter(prefix="/api/integrated-ocr", tags=["integrated-ocr"])

# MongoDB 서비스 의존성
def get_mongo_saver():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    return MongoSaver(mongo_uri)


@router.post("/check-duplicate")
async def check_duplicate_applicant(
    resume_file: UploadFile = File(...),
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """
    이력서 파일을 분석하여 기존 지원자와 중복되는지 확인합니다.
    """
    try:
        print(f"🔍 중복 체크 시작: {resume_file.filename}")
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await resume_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            print(f"📄 PDF 처리 시작: {temp_file_path}")
            
            # PDF 처리 및 텍스트 추출
            ocr_result = process_pdf(temp_file_path)
            print(f"📝 OCR 결과: {len(ocr_result.get('extracted_text', ''))} 문자")
            
            # AI 분석으로 기본 정보 추출
            analysis_result = analyze_text(ocr_result.get("extracted_text", ""))
            print(f"🤖 AI 분석 결과: {analysis_result}")
            
            # 기본 정보 추출
            basic_info = analysis_result.get("basic_info", {})
            names = basic_info.get("names", [])
            emails = basic_info.get("emails", [])
            phones = basic_info.get("phones", [])
            
            print(f"👤 추출된 정보 - 이름: {names}, 이메일: {emails}, 전화번호: {phones}")
            
            # 이름이나 이메일로 기존 지원자 검색
            existing_applicant = None
            
            if names:
                # 이름으로 검색
                for name in names:
                    if name and len(name.strip()) > 1:
                        print(f"🔍 이름으로 검색: '{name.strip()}'")
                        existing = mongo_saver.mongo_service.find_applicant_by_name(name.strip())
                        if existing:
                            print(f"✅ 이름으로 기존 지원자 발견: {existing}")
                            existing_applicant = existing
                            break
            
            if not existing_applicant and emails:
                # 이메일로 검색
                for email in emails:
                    if email and '@' in email:
                        print(f"🔍 이메일로 검색: '{email.strip()}'")
                        existing = mongo_saver.mongo_service.find_applicant_by_email(email.strip())
                        if existing:
                            print(f"✅ 이메일로 기존 지원자 발견: {existing}")
                            existing_applicant = existing
                            break
            
            if not existing_applicant and phones:
                # 전화번호로 검색
                for phone in phones:
                    if phone and len(phone.strip()) >= 10:
                        print(f"🔍 전화번호로 검색: '{phone.strip()}'")
                        existing = mongo_saver.mongo_service.find_applicant_by_phone(phone.strip())
                        if existing:
                            print(f"✅ 전화번호로 기존 지원자 발견: {existing}")
                            existing_applicant = existing
                            break
            
            # 기존 지원자 정보 반환
            if existing_applicant:
                print(f"🔄 기존 지원자 발견 - ID: {existing_applicant['_id']}")
                
                # 각 문서 타입별 존재 여부 확인
                applicant_id = str(existing_applicant["_id"])
                resume_exists = mongo_saver.mongo_service.check_document_exists(applicant_id, "resume")
                cover_letter_exists = mongo_saver.mongo_service.check_document_exists(applicant_id, "cover_letter")
                portfolio_exists = mongo_saver.mongo_service.check_document_exists(applicant_id, "portfolio")
                
                print(f"📋 문서 존재 여부 - 이력서: {resume_exists}, 자기소개서: {cover_letter_exists}, 포트폴리오: {portfolio_exists}")
                
                result = {
                    "existing_applicant": {
                        "_id": applicant_id,
                        "name": existing_applicant.get("name", ""),
                        "email": existing_applicant.get("email", ""),
                        "phone": existing_applicant.get("phone", ""),
                        "resume": resume_exists,
                        "cover_letter": cover_letter_exists,
                        "portfolio": portfolio_exists
                    },
                    "message": "기존 지원자를 발견했습니다."
                }
                
                print(f"📤 응답 반환: {result}")
                return result
            else:
                print("✅ 새로운 지원자 - 중복 없음")
                return {
                    "existing_applicant": None,
                    "message": "새로운 지원자입니다."
                }
                
        finally:
            # 임시 파일 정리
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                print(f"🗑️ 임시 파일 정리: {temp_file_path}")
                
    except Exception as e:
        print(f"❌ 중복 체크 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"중복 체크 실패: {str(e)}")


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
    
    # 1. AI 분석 결과에서 기본 정보 추출
    ai_basic_info = ocr_result.get("basic_info", {})
    
    # AI 분석 결과에서 배열 형태로 저장된 정보 추출
    ai_names = ai_basic_info.get("names", [])
    ai_emails = ai_basic_info.get("emails", [])
    ai_phones = ai_basic_info.get("phones", [])
    
    # AI 분석 결과에서 단일 값으로 저장된 정보 추출 (structured_data에서)
    structured_data = ocr_result.get("structured_data", {})
    structured_basic_info = structured_data.get("basic_info", {})
    
    ai_single_name = structured_basic_info.get("name", "")
    ai_single_email = structured_basic_info.get("email", "")
    ai_single_phone = structured_basic_info.get("phone", "")
    ai_position = structured_basic_info.get("position", "")
    
    # 2. 텍스트에서 직접 추출 (백업용)
    text = ocr_result.get("extracted_text", "") or ocr_result.get("full_text", "") or ""
    extracted = _extract_contact_from_text(text)
    
    # 3. 우선순위에 따라 최종 값 결정
    # 이름: Form 입력 > AI 단일 값 > AI 배열 첫 번째 > 텍스트 추출 > 기본값
    final_name = (
        name or 
        ai_single_name or
        (ai_names[0] if ai_names else None) or 
        extracted.get("name") or 
        "이름미상"
    )
    
    # 이메일: Form 입력 > AI 단일 값 > AI 배열 첫 번째 > 텍스트 추출 > 기본값
    final_email = (
        email or 
        ai_single_email or
        (ai_emails[0] if ai_emails else None) or 
        extracted.get("email") or 
        f"unknown_{int(datetime.utcnow().timestamp())}@noemail.local"
    )
    
    # 전화번호: Form 입력 > AI 단일 값 > AI 배열 첫 번째 > 텍스트 추출
    final_phone = (
        phone or 
        ai_single_phone or
        (ai_phones[0] if ai_phones else None) or 
        extracted.get("phone")
    )
    
    # 4. 추가 정보 추출 (AI 분석 결과에서)
    # 직무/포지션
    final_position = ai_position or _extract_position_from_text(text)
    
    # 기술 스택
    final_skills = _extract_skills_from_text(text)
    
    # 경력 정보
    final_experience = _extract_experience_from_text(text)
    
    # 부서 (기본값)
    final_department = "개발"  # 기본값
    
    # 성장 배경 (요약에서 추출)
    final_growth_background = ocr_result.get("summary", "")[:200] + "..." if ocr_result.get("summary") else ""
    
    # 지원 동기 (기본값)
    final_motivation = "이력서를 통해 지원자의 역량과 경험을 확인했습니다."
    
    # 경력 사항 (요약에서 추출)
    final_career_history = ocr_result.get("summary", "")[:300] + "..." if ocr_result.get("summary") else ""
    
    # 분석 점수 (기본값)
    final_analysis_score = 65  # 기본값
    
    # 분석 결과 (요약에서 추출)
    final_analysis_result = ocr_result.get("summary", "")[:100] + "..." if ocr_result.get("summary") else ""
    
    # 5. 디버깅을 위한 로그 (개발 중에만 사용)
    print(f"🔍 지원자 정보 추출 결과:")
    print(f"  - AI 분석 결과 (배열): names={ai_names}, emails={ai_emails}, phones={ai_phones}")
    print(f"  - AI 분석 결과 (단일): name={ai_single_name}, email={ai_single_email}, phone={ai_single_phone}, position={ai_position}")
    print(f"  - 텍스트 추출 결과: {extracted}")
    print(f"  - 최종 결정: name={final_name}, email={final_email}, phone={final_phone}, position={final_position}")
    
    return ApplicantCreate(
        name=final_name,
        email=final_email,
        phone=final_phone,
        position=final_position,
        department=final_department,
        experience=final_experience,
        skills=final_skills,
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

@router.post("/upload-resume")
async def upload_resume_with_ocr(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    job_posting_id: str = Form(...),
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """이력서를 업로드하고 OCR 처리 후 DB에 저장합니다."""
    try:
        # 파일 검증
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다")
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)
        
        try:
            # GPT-4o-mini Vision API를 사용한 PDF OCR 처리
            ocr_result = process_pdf(str(temp_file_path))
            
            # AI 분석 결과 가져오기
            settings = Settings()
            ai_analysis = analyze_text(ocr_result.get("full_text", ""), settings)
            
            # OCR 결과에 AI 분석 결과 추가
            enhanced_ocr_result = {
                "extracted_text": ocr_result.get("full_text", ""),
                "summary": ai_analysis.get("summary", ""),
                "keywords": ai_analysis.get("keywords", []),
                "basic_info": ai_analysis.get("basic_info", {}),
                "document_type": ai_analysis.get("structured_data", {}).get("document_type", "resume"),
                "pages": ocr_result.get("num_pages", 0)
            }
            
            # 지원자 데이터 생성 (OCR 기반 자동 추출)
            applicant_data = _build_applicant_data(name, email, phone, enhanced_ocr_result, job_posting_id)
            
            # MongoDB에 저장
            result = mongo_saver.save_resume_with_ocr(
                ocr_result=enhanced_ocr_result,
                applicant_data=applicant_data,
                job_posting_id=job_posting_id,
                file_path=temp_file_path
            )
            
            return JSONResponse(content={
                "success": True,
                "message": "이력서 OCR 처리 및 저장 완료",
                "data": result,
                "ocr_result": enhanced_ocr_result
            })
            
        finally:
            # 임시 파일 삭제
            if temp_file_path.exists():
                temp_file_path.unlink()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력서 처리 실패: {str(e)}")
    finally:
        mongo_saver.close()

@router.post("/upload-cover-letter")
async def upload_cover_letter_with_ocr(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    job_posting_id: str = Form(...),
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """자기소개서를 업로드하고 OCR 처리 후 DB에 저장합니다."""
    try:
        # 파일 검증
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다")
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)
        
        try:
            # GPT-4o-mini Vision API를 사용한 PDF OCR 처리
            ocr_result = process_pdf(str(temp_file_path))
            
            # AI 분석 결과 가져오기
            settings = Settings()
            ai_analysis = analyze_text(ocr_result.get("full_text", ""), settings)
            
            # OCR 결과에 AI 분석 결과 추가
            enhanced_ocr_result = {
                "extracted_text": ocr_result.get("full_text", ""),
                "summary": ai_analysis.get("summary", ""),
                "keywords": ai_analysis.get("keywords", []),
                "basic_info": ai_analysis.get("basic_info", {}),
                "document_type": ai_analysis.get("structured_data", {}).get("document_type", "cover_letter"),
                "pages": ocr_result.get("num_pages", 0)
            }
            
            # 지원자 데이터 생성 (OCR 기반 자동 추출)
            applicant_data = _build_applicant_data(name, email, phone, enhanced_ocr_result, job_posting_id)
            
            # MongoDB에 저장
            result = mongo_saver.save_cover_letter_with_ocr(
                ocr_result=enhanced_ocr_result,
                applicant_data=applicant_data,
                job_posting_id=job_posting_id,
                file_path=temp_file_path
            )
            
            return JSONResponse(content={
                "success": True,
                "message": "자기소개서 OCR 처리 및 저장 완료",
                "data": result,
                "ocr_result": enhanced_ocr_result
            })
            
        finally:
            # 임시 파일 삭제
            if temp_file_path.exists():
                temp_file_path.unlink()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자기소개서 처리 실패: {str(e)}")
    finally:
        mongo_saver.close()

@router.post("/upload-portfolio")
async def upload_portfolio_with_ocr(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    job_posting_id: str = Form(...),
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """포트폴리오를 업로드하고 OCR 처리 후 DB에 저장합니다."""
    try:
        # 파일 검증
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다")
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)
        
        try:
            # GPT-4o-mini Vision API를 사용한 PDF OCR 처리
            ocr_result = process_pdf(str(temp_file_path))
            
            # AI 분석 결과 가져오기
            settings = Settings()
            ai_analysis = analyze_text(ocr_result.get("full_text", ""), settings)
            
            # OCR 결과에 AI 분석 결과 추가
            enhanced_ocr_result = {
                "extracted_text": ocr_result.get("full_text", ""),
                "summary": ai_analysis.get("summary", ""),
                "keywords": ai_analysis.get("keywords", []),
                "basic_info": ai_analysis.get("basic_info", {}),
                "document_type": ai_analysis.get("structured_data", {}).get("document_type", "portfolio"),
                "pages": ocr_result.get("num_pages", 0)
            }
            
            # 지원자 데이터 생성 (OCR 기반 자동 추출)
            applicant_data = _build_applicant_data(name, email, phone, enhanced_ocr_result, job_posting_id)
            
            # MongoDB에 저장
            result = mongo_saver.save_portfolio_with_ocr(
                ocr_result=enhanced_ocr_result,
                applicant_data=applicant_data,
                job_posting_id=job_posting_id,
                file_path=temp_file_path
            )
            
            return JSONResponse(content={
                "success": True,
                "message": "포트폴리오 OCR 처리 및 저장 완료",
                "data": result,
                "ocr_result": enhanced_ocr_result
            })
            
        finally:
            # 임시 파일 삭제
            if temp_file_path.exists():
                temp_file_path.unlink()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포트폴리오 처리 실패: {str(e)}")
    finally:
        mongo_saver.close()

@router.post("/upload-multiple")
async def upload_multiple_documents(
    resume_file: Optional[UploadFile] = File(None),
    cover_letter_file: Optional[UploadFile] = File(None),
    portfolio_file: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    job_posting_id: str = Form(...),
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """여러 문서를 한 번에 업로드하고 OCR 처리 후 DB에 저장합니다."""
    try:
        results = {}
        temp_files = []
        
        # 지원자 데이터 생성은 첫 번째 처리된 문서의 OCR 결과로 자동 추출
        applicant_data: Optional[ApplicantCreate] = None
        
        # 이력서 처리
        if resume_file:
            if not resume_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="이력서는 PDF 파일만 업로드 가능합니다")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await resume_file.read()
                temp_file.write(content)
                temp_file_path = Path(temp_file.name)
                temp_files.append(temp_file_path)
            
            ocr_result = process_pdf(str(temp_file_path))
            if not applicant_data:
                applicant_data = _build_applicant_data(name, email, phone, ocr_result, job_posting_id)
            result = mongo_saver.save_resume_with_ocr(
                ocr_result=ocr_result,
                applicant_data=applicant_data,
                job_posting_id=job_posting_id,
                file_path=temp_file_path
            )
            results["resume"] = result
        
        # 자기소개서 처리
        if cover_letter_file:
            if not cover_letter_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="자기소개서는 PDF 파일만 업로드 가능합니다")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await cover_letter_file.read()
                temp_file.write(content)
                temp_file_path = Path(temp_file.name)
                temp_files.append(temp_file_path)
            
            ocr_result = process_pdf(str(temp_file_path))
            if not applicant_data:
                applicant_data = _build_applicant_data(name, email, phone, ocr_result, job_posting_id)
            result = mongo_saver.save_cover_letter_with_ocr(
                ocr_result=ocr_result,
                applicant_data=applicant_data,
                job_posting_id=job_posting_id,
                file_path=temp_file_path
            )
            results["cover_letter"] = result
        
        # 포트폴리오 처리
        if portfolio_file:
            if not portfolio_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="포트폴리오는 PDF 파일만 업로드 가능합니다")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await portfolio_file.read()
                temp_file.write(content)
                temp_file_path = Path(temp_file.name)
                temp_files.append(temp_file_path)
            
            ocr_result = process_pdf(str(temp_file_path))
            if not applicant_data:
                applicant_data = _build_applicant_data(name, email, phone, ocr_result, job_posting_id)
            result = mongo_saver.save_portfolio_with_ocr(
                ocr_result=ocr_result,
                applicant_data=applicant_data,
                job_posting_id=job_posting_id,
                file_path=temp_file_path
            )
            results["portfolio"] = result
        
        # 임시 파일들 정리
        for temp_file_path in temp_files:
            if temp_file_path.exists():
                temp_file_path.unlink()
        
        return JSONResponse(content={
            "success": True,
            "message": "문서들 OCR 처리 및 저장 완료",
            "data": results
        })
        
    except Exception as e:
        # 임시 파일들 정리
        for temp_file_path in temp_files:
            if temp_file_path.exists():
                temp_file_path.unlink()
        
        raise HTTPException(status_code=500, detail=f"문서 처리 실패: {str(e)}")
    finally:
        mongo_saver.close()

@router.post("/upload-multiple-documents")
async def upload_multiple_documents(
    resume_file: Optional[UploadFile] = File(None),
    cover_letter_file: Optional[UploadFile] = File(None),
    portfolio_file: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    job_posting_id: Optional[str] = Form("default_job_posting"),
    existing_applicant_id: Optional[str] = Form(None),
    replace_existing: Optional[bool] = Form(False),
    mongo_saver: MongoSaver = Depends(get_mongo_saver)
):
    """여러 문서를 한 번에 업로드하고 OCR 처리 후 하나의 지원자 레코드로 통합 저장합니다."""
    print(f"🚀 통합 문서 업로드 시작")
    print(f"📁 파일 정보: resume={resume_file.filename if resume_file else 'None'}, cover_letter={cover_letter_file.filename if cover_letter_file else 'None'}, portfolio={portfolio_file.filename if portfolio_file else 'None'}")
    print(f"🔄 교체 옵션: {replace_existing}")
    print(f"👤 기존 지원자 ID: {existing_applicant_id}")
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
        
        # 기존 지원자 ID가 있는 경우 처리
        if existing_applicant_id:
            print(f"🔄 기존 지원자 ID로 처리: {existing_applicant_id}")
            # 기존 지원자 정보 조회
            from bson import ObjectId
            try:
                existing_applicant = mongo_saver.db.applicants.find_one({"_id": ObjectId(existing_applicant_id)})
                if existing_applicant:
                    applicant_id = str(existing_applicant["_id"])
                    print(f"✅ 기존 지원자 발견: {existing_applicant.get('name', 'N/A')} ({existing_applicant.get('email', 'N/A')})")
                    
                    # 기존 지원자의 문서 등록 상태 확인
                    if resume_file:
                        resume_exists = mongo_saver.mongo_service.check_document_exists(applicant_id, "resume")
                        if resume_exists and not replace_existing:
                            raise HTTPException(
                                status_code=409, 
                                detail=f"지원자 '{existing_applicant.get('name', 'N/A')}'의 이력서가 이미 등록되어 있습니다. 교체하려면 replace_existing=true로 설정하세요."
                            )
                    
                    if cover_letter_file:
                        cover_letter_exists = mongo_saver.mongo_service.check_document_exists(applicant_id, "cover_letter")
                        if cover_letter_exists and not replace_existing:
                            raise HTTPException(
                                status_code=409, 
                                detail=f"지원자 '{existing_applicant.get('name', 'N/A')}'의 자기소개서가 이미 등록되어 있습니다. 교체하려면 replace_existing=true로 설정하세요."
                            )
                    
                    if portfolio_file:
                        portfolio_exists = mongo_saver.mongo_service.check_document_exists(applicant_id, "portfolio")
                        if portfolio_exists and not replace_existing:
                            raise HTTPException(
                                status_code=409, 
                                detail=f"지원자 '{existing_applicant.get('name', 'N/A')}'의 포트폴리오가 이미 등록되어 있습니다. 교체하려면 replace_existing=true로 설정하세요."
                            )
                    
                    print(f"✅ 문서 중복 검사 완료 - 교체 옵션: {replace_existing}")
                else:
                    print(f"⚠️ 기존 지원자 ID를 찾을 수 없음: {existing_applicant_id}")
                    existing_applicant_id = None
            except Exception as e:
                print(f"⚠️ 기존 지원자 조회 실패: {e}")
                existing_applicant_id = None
        
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
                
                # AI 분석 결과 가져오기
                print(f"🤖 이력서 AI 분석 중...")
                settings = Settings()
                ai_analysis = analyze_text(ocr_result.get("full_text", ""), settings)
                
                # OCR 결과에 AI 분석 결과 추가
                enhanced_ocr_result = {
                    "extracted_text": ocr_result.get("full_text", ""),
                    "summary": ai_analysis.get("summary", ""),
                    "keywords": ai_analysis.get("keywords", []),
                    "basic_info": ai_analysis.get("basic_info", {}),
                    "structured_data": ai_analysis.get("structured_data", {}),
                    "document_type": "resume",
                    "pages": ocr_result.get("num_pages", 0)
                }
                
                # 문서 중복 검사
                print(f"🔍 이력서 중복 검사 중...")
                duplicate_check = mongo_saver.mongo_service.check_content_duplicate(
                    enhanced_ocr_result["extracted_text"], 
                    "resume", 
                    applicant_id if existing_applicant_id else None
                )
                
                if duplicate_check["is_duplicate"]:
                    # 100% 일치하는 문서가 있는 경우
                    exact_match = duplicate_check["exact_matches"][0]
                    existing_doc = exact_match["document"]
                    existing_applicant_name = "알 수 없음"
                    
                    # 기존 문서의 지원자 정보 조회
                    if existing_doc.get("applicant_id"):
                        existing_applicant_info = mongo_saver.mongo_service.get_applicant_by_id(existing_doc["applicant_id"])
                        if existing_applicant_info:
                            existing_applicant_name = existing_applicant_info.get("name", "알 수 없음")
                    
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "type": "exact_duplicate",
                            "message": f"동일한 이력서가 이미 등록되어 있습니다",
                            "subtitle": f"지원자: {existing_applicant_name}",
                            "description": "이미 등록된 이력서와 100% 동일한 내용입니다.",
                            "existing_applicant": existing_applicant_name,
                            "similarity": exact_match["similarity"],
                            "changes": exact_match["changes"]
                        }
                    )
                
                elif duplicate_check["has_similar_content"]:
                    # 90% 이상 유사한 문서가 있는 경우
                    similar_matches = duplicate_check["similar_matches"]
                    similar_docs_info = []
                    
                    for match in similar_matches:
                        doc = match["document"]
                        existing_applicant_name = "알 수 없음"
                        
                        if doc.get("applicant_id"):
                            existing_applicant_info = mongo_saver.mongo_service.get_applicant_by_id(doc["applicant_id"])
                            if existing_applicant_info:
                                existing_applicant_name = existing_applicant_info.get("name", "알 수 없음")
                        
                        similar_docs_info.append({
                            "applicant_name": existing_applicant_name,
                            "similarity": match["similarity"],
                            "changes": match["changes"]
                        })
                    
                    # 사용자 승인이 필요한 경우
                    if not replace_existing:
                        raise HTTPException(
                            status_code=409,
                            detail={
                                "type": "similar_content",
                                "message": "유사한 이력서가 발견되었습니다",
                                "subtitle": "기존 이력서와 90% 이상 유사합니다",
                                "description": "이미 등록된 이력서와 매우 유사한 내용이 감지되었습니다.",
                                "similar_documents": similar_docs_info,
                                "requires_approval": True
                            }
                        )
                    
                    print(f"⚠️ 유사한 이력서 발견 - 교체 옵션으로 진행: {len(similar_docs_info)}개")
                
                else:
                    print(f"✅ 중복 검사 완료 - 새로운 이력서로 등록 가능")
                
                # 기존 지원자가 있는 경우 기존 정보 사용, 없는 경우 새로 생성
                if existing_applicant_id and applicant_id:
                    # 기존 지원자 정보 사용
                    applicant_data = ApplicantCreate(
                        name=existing_applicant.get("name", ""),
                        email=existing_applicant.get("email", ""),
                        phone=existing_applicant.get("phone", ""),
                        position=existing_applicant.get("position", ""),
                        department=existing_applicant.get("department", ""),
                        experience=existing_applicant.get("experience", ""),
                        skills=existing_applicant.get("skills", ""),
                        growthBackground=existing_applicant.get("growthBackground", ""),
                        motivation=existing_applicant.get("motivation", ""),
                        careerHistory=existing_applicant.get("careerHistory", ""),
                        analysisScore=existing_applicant.get("analysisScore", 65),
                        analysisResult=existing_applicant.get("analysisResult", ""),
                        status=existing_applicant.get("status", "pending"),
                        job_posting_id=job_posting_id
                    )
                else:
                    # 새 지원자 데이터 생성
                    applicant_data = _build_applicant_data(name, email, phone, enhanced_ocr_result, job_posting_id)
                    
                    # 새 지원자 등록 시 이메일 중복 체크
                    if email:
                        existing_applicant_by_email = mongo_saver.mongo_service.find_applicant_by_email(email)
                        if existing_applicant_by_email:
                            raise HTTPException(
                                status_code=409,
                                detail={
                                    "type": "duplicate_email",
                                    "message": "이미 등록된 이메일입니다",
                                    "subtitle": f"'{email}'로 등록된 지원자가 존재합니다",
                                    "description": "동일한 이메일로 이미 지원자가 등록되어 있습니다.",
                                    "email": email
                                }
                            )
                
                # MongoDB에 저장 (기존 지원자 ID가 있으면 사용)
                print(f"📄 이력서 저장 시작 - 교체 옵션: {replace_existing}")
                result = mongo_saver.save_resume_with_ocr(
                    ocr_result=enhanced_ocr_result,
                    applicant_data=applicant_data,
                    job_posting_id=job_posting_id,
                    file_path=temp_file_path,
                    existing_applicant_id=applicant_id if existing_applicant_id else None,
                    replace_existing=replace_existing
                )
                
                results["resume"] = result
                applicant_id = result.get("applicant", {}).get("id")
                
                print(f"✅ 이력서 처리 완료: {applicant_id}")
                print(f"📊 이력서 결과: {result.get('message', 'N/A')}")
                print(f"👤 지원자 정보: {result.get('applicant', {}).get('name', 'N/A')} ({result.get('applicant', {}).get('email', 'N/A')})")
                
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
                
                # 문서 중복 검사
                print(f"🔍 자기소개서 중복 검사 중...")
                duplicate_check = mongo_saver.mongo_service.check_content_duplicate(
                    enhanced_ocr_result["extracted_text"], 
                    "cover_letter", 
                    applicant_id if applicant_id else None
                )
                
                if duplicate_check["is_duplicate"]:
                    # 100% 일치하는 문서가 있는 경우
                    exact_match = duplicate_check["exact_matches"][0]
                    existing_doc = exact_match["document"]
                    existing_applicant_name = "알 수 없음"
                    
                    # 기존 문서의 지원자 정보 조회
                    if existing_doc.get("applicant_id"):
                        existing_applicant_info = mongo_saver.mongo_service.get_applicant_by_id(existing_doc["applicant_id"])
                        if existing_applicant_info:
                            existing_applicant_name = existing_applicant_info.get("name", "알 수 없음")
                    
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "type": "exact_duplicate",
                            "message": f"동일한 자기소개서가 이미 등록되어 있습니다",
                            "subtitle": f"지원자: {existing_applicant_name}",
                            "description": "이미 등록된 자기소개서와 100% 동일한 내용입니다.",
                            "existing_applicant": existing_applicant_name,
                            "similarity": exact_match["similarity"],
                            "changes": exact_match["changes"]
                        }
                    )
                
                elif duplicate_check["has_similar_content"]:
                    # 90% 이상 유사한 문서가 있는 경우
                    similar_matches = duplicate_check["similar_matches"]
                    similar_docs_info = []
                    
                    for match in similar_matches:
                        doc = match["document"]
                        existing_applicant_name = "알 수 없음"
                        
                        if doc.get("applicant_id"):
                            existing_applicant_info = mongo_saver.mongo_service.get_applicant_by_id(doc["applicant_id"])
                            if existing_applicant_info:
                                existing_applicant_name = existing_applicant_info.get("name", "알 수 없음")
                        
                        similar_docs_info.append({
                            "applicant_name": existing_applicant_name,
                            "similarity": match["similarity"],
                            "changes": match["changes"]
                        })
                    
                    # 사용자 승인이 필요한 경우
                    if not replace_existing:
                        raise HTTPException(
                            status_code=409,
                            detail={
                                "type": "similar_content",
                                "message": "유사한 자기소개서가 발견되었습니다",
                                "subtitle": "기존 자기소개서와 90% 이상 유사합니다",
                                "description": "이미 등록된 자기소개서와 매우 유사한 내용이 감지되었습니다.",
                                "similar_docs_info": similar_docs_info,
                                "requires_approval": True
                            }
                        )
                    
                    print(f"⚠️ 유사한 자기소개서 발견 - 교체 옵션으로 진행: {len(similar_docs_info)}개")
                
                else:
                    print(f"✅ 중복 검사 완료 - 새로운 자기소개서로 등록 가능")
                
                # 기존 지원자 데이터 사용 또는 새로 생성
                if applicant_id:
                    # 기존 지원자 정보 가져오기
                    existing_applicant = mongo_saver.mongo_service.get_applicant_by_id(applicant_id)
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
                    
                    # 새 지원자 등록 시 이메일 중복 체크
                    if email:
                        existing_applicant_by_email = mongo_saver.mongo_service.find_applicant_by_email(email)
                        if existing_applicant_by_email:
                            raise HTTPException(
                                status_code=409,
                                detail=f"이메일 '{email}'로 등록된 지원자가 이미 존재합니다. 기존 지원자 ID를 사용하거나 다른 이메일을 입력하세요."
                            )
                
                # MongoDB에 저장 (기존 지원자 ID가 있으면 사용)
                print(f"📝 자기소개서 저장 시작 - 교체 옵션: {replace_existing}")
                result = mongo_saver.save_cover_letter_with_ocr(
                    ocr_result=enhanced_ocr_result,
                    applicant_data=applicant_data,
                    job_posting_id=job_posting_id,
                    file_path=temp_file_path,
                    existing_applicant_id=applicant_id if applicant_id else None,
                    replace_existing=replace_existing
                )
                
                results["cover_letter"] = result
                if not applicant_id:
                    applicant_id = result.get("applicant", {}).get("id")
                
                print(f"✅ 자기소개서 처리 완료: {applicant_id}")
                print(f"📊 자기소개서 결과: {result.get('message', 'N/A')}")
                print(f"👤 지원자 정보: {result.get('applicant', {}).get('name', 'N/A')} ({result.get('applicant', {}).get('email', 'N/A')})")
                
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
                    existing_applicant = mongo_saver.mongo_service.get_applicant_by_id(applicant_id)
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
                
                # MongoDB에 저장 (기존 지원자 ID가 있으면 사용)
                print(f"📁 포트폴리오 저장 시작 - 교체 옵션: {replace_existing}")
                result = mongo_saver.save_portfolio_with_ocr(
                    ocr_result=enhanced_ocr_result,
                    applicant_data=applicant_data,
                    job_posting_id=job_posting_id,
                    file_path=temp_file_path,
                    existing_applicant_id=applicant_id if applicant_id else None,
                    replace_existing=replace_existing
                )
                
                results["portfolio"] = result
                if not applicant_id:
                    applicant_id = result.get("applicant", {}).get("id")
                
                print(f"✅ 포트폴리오 처리 완료: {applicant_id}")
                print(f"📊 포트폴리오 결과: {result.get('message', 'N/A')}")
                print(f"👤 지원자 정보: {result.get('applicant', {}).get('name', 'N/A')} ({result.get('applicant', {}).get('email', 'N/A')})")
                
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
        
        # 최종 결과 반환
        return JSONResponse(content={
            "success": True,
            "message": "모든 문서 OCR 처리 및 저장 완료",
            "data": {
                "applicant_id": applicant_id,
                "results": results,
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
