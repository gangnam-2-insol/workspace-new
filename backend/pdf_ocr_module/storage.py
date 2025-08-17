from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId

from pymongo import MongoClient
from pymongo.collection import Collection

from .config import Settings


def _get_collections(client: MongoClient, settings: Settings) -> tuple[Collection, Collection]:
    db = client[settings.mongodb_db]
    return db[settings.mongodb_col_documents], db[settings.mongodb_col_pages]


def save_document_to_mongo(document: Dict[str, Any], settings: Settings) -> str:
    client = MongoClient(settings.mongodb_uri)
    try:
        col_docs, _ = _get_collections(client, settings)
        payload = {
            **document,
            "created_at": document.get("created_at", datetime.utcnow()),
        }
        result = col_docs.insert_one(payload)
        return str(result.inserted_id)
    finally:
        client.close()


# MongoDB에 원본 텍스트, 요약, 키워드, 메타데이터 저장
def save_to_db(
    pdf_filename: str,
    page_number: int,
    text: str,
    db_conn: MongoClient | None,
    summary: str | None,
    keywords: list[str] | None,
    *,
    doc_hash: Optional[str] = None,
) -> str:
    settings = Settings()
    client = db_conn or MongoClient(settings.mongodb_uri)
    created_client = db_conn is None
    try:
        _, col_pages = _get_collections(client, settings)
        payload: Dict[str, Any] = {
            "file_name": pdf_filename,
            "page": page_number,
            "text": text,
            "summary": summary,
            "keywords": keywords or [],
            "created_at": datetime.utcnow(),
        }
        if doc_hash:
            payload["doc_hash"] = doc_hash
        result = col_pages.insert_one(payload)
        return str(result.inserted_id)
    finally:
        if created_client:
            client.close()


def save_to_hireme_applicants(document: Dict[str, Any], settings: Settings) -> str:
    """추출된 정보를 hireme DB의 applicants 컬렉션에 저장합니다."""
    client = MongoClient(settings.mongodb_uri)
    try:
        # hireme DB의 applicants 컬렉션에 연결
        db = client["Hireme"]
        applicants_collection = db["applicants"]
        
        # 스킬 데이터 처리 (쉼표로 구분된 문자열을 개별 항목으로 분리)
        raw_skills = document.get("fields", {}).get("skills", [])
        processed_skills = []
        for skill_group in raw_skills:
            if isinstance(skill_group, str):
                # 쉼표로 구분된 스킬들을 개별 항목으로 분리
                individual_skills = [skill.strip() for skill in skill_group.split(',')]
                processed_skills.extend(individual_skills)
            else:
                processed_skills.append(str(skill_group))
        
        # 기존 Hireme DB 구조에 맞게 데이터 변환
        applicant_data = {
            "id": str(document.get("doc_id", "")),  # doc_id를 id로 사용
            "name": document.get("fields", {}).get("names", [""])[0] if document.get("fields", {}).get("names") else "",
            "email": document.get("fields", {}).get("emails", [""])[0] if document.get("fields", {}).get("emails") else "",
            "phone": document.get("fields", {}).get("phones", [""])[0] if document.get("fields", {}).get("phones") else "",
            "position": document.get("fields", {}).get("positions", [""])[0] if document.get("fields", {}).get("positions") else "",
            "experience": "",  # 경력 정보는 추출되지 않으므로 빈 문자열
            "education": document.get("fields", {}).get("education", [""])[0] if document.get("fields", {}).get("education") else "",
            "status": "서류검토",  # 기본 상태
            "appliedDate": datetime.utcnow().strftime("%Y-%m-%d"),  # 현재 날짜
            "aiScores": {
                "resume": 0,  # 기본값
                "coverLetter": 0,
                "portfolio": 0
            },
            "aiSuitability": 0,  # aiSuitability는 별도 필드
            "documents": {
                "resume": {
                    "exists": True,
                    "summary": document.get("summary", ""),
                    "keywords": document.get("keywords", []),
                    "content": document.get("text", "")  # 전체 이력서 텍스트
                },
                "portfolio": {
                    "exists": False,  # 포트폴리오는 별도 업로드 필요
                    "summary": "",
                    "keywords": [],
                    "content": ""
                },
                "coverLetter": {
                    "exists": False,  # 자기소개서는 별도 업로드 필요
                    "summary": "",
                    "keywords": [],
                    "content": ""
                }
            },
            "interview": {
                "scheduled": False,
                "date": "",
                "time": "",
                "type": "",
                "location": "",
                "status": ""
            },
            "created_at": document.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "source": "pdf_ocr"  # 데이터 출처 표시
        }
        
        # 중복 체크 (이메일이나 전화번호로)
        existing_applicant = None
        if applicant_data["email"]:
            existing_applicant = applicants_collection.find_one({"email": applicant_data["email"]})
        elif applicant_data["phone"]:
            existing_applicant = applicants_collection.find_one({"phone": applicant_data["phone"]})
        
        if existing_applicant:
            # 기존 데이터 업데이트 - documents.resume 부분만 업데이트
            applicants_collection.update_one(
                {"_id": existing_applicant["_id"]},
                {"$set": {
                    "name": applicant_data["name"] or existing_applicant.get("name", ""),
                    "phone": applicant_data["phone"] or existing_applicant.get("phone", ""),
                    "position": applicant_data["position"] or existing_applicant.get("position", ""),
                    "education": applicant_data["education"] or existing_applicant.get("education", ""),
                    "documents.resume": applicant_data["documents"]["resume"],
                    "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "source": "pdf_ocr"
                }}
            )
            return str(existing_applicant["_id"])
        else:
            # 새 데이터 삽입
            result = applicants_collection.insert_one(applicant_data)
            return str(result.inserted_id)
    finally:
        client.close()



