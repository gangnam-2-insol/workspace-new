# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
from chatbot_router import router as chatbot_router

# FastAPI ???�성
app = FastAPI(
    title="HireMe API",
    description="HireMe ?�로?�트 백엔??API",
    version="1.0.0"
)

# CORS ?�정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 챗봇 ?�우??추�?
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["chatbot"])

# MongoDB ?�결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://admin:password@localhost:27017/hireme?authSource=admin")

# MongoDB ?�결 ?�도 (?�패?�도 ?�버???�작)
try:
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.hireme
    print("MongoDB ?�결 ?�공")
except Exception as e:
    print(f"MongoDB ?�결 ?�패: {e}")
    print("MongoDB ?�이 ?�버�??�작?�니??")
    client = None
    db = None

# Pydantic 모델??class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    role: str = "user"
    created_at: Optional[datetime] = None

class Resume(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    content: str
    status: str = "pending"
    created_at: Optional[datetime] = None

class Interview(BaseModel):
    id: Optional[str] = None
    user_id: str
    company: str
    position: str
    date: datetime
    status: str = "scheduled"
    type: Optional[str] = "1�?면접"  # 면접 ?�형 (1�? 2�? 최종 ??
    hrManager: Optional[str] = "면접관"  # 면접관 ?�름
    location: Optional[str] = "?�의??  # 면접 ?�소
    notes: Optional[str] = ""  # 면접 ?�트
    created_at: Optional[datetime] = None

# 지?�서 관리용 ?�로??모델
class Application(BaseModel):
    id: Optional[str] = None
    name: str
    type: str  # resume, coverletter, portfolio
    title: str
    status: str  # pending, reviewed, approved, rejected
    date: str
    experience: str
    skills: List[str]
    summary: str
    created_at: Optional[datetime] = None

class ApplicationStats(BaseModel):
    total: int
    pending: int
    reviewed: int
    approved: int
    rejected: int

# ?�플 ?�이??SAMPLE_APPLICATIONS = [
    # 2024??1???�이??(25�?
    {
        "name": "김개발",
        "type": "resume",
        "title": "?�론?�엔??개발???�력??,
        "status": "reviewed",
        "date": "2024-01-15",
        "experience": "3??,
        "skills": ["React", "TypeScript", "Node.js"],
        "summary": "??개발 경험 3?? React?� TypeScript ?�문가로서 ?�용??경험??중시?�는 개발??추구?�니??"
    },
    {
        "name": "?�디?�인",
        "type": "coverletter",
        "title": "UI/UX ?�자?�너 ?�소??,
        "status": "pending",
        "date": "2024-01-14",
        "experience": "2??,
        "skills": ["Figma", "Adobe XD", "Photoshop"],
        "summary": "?�용??중심 ?�자??경험, ?�로?�트 20�??�료?�며 창의?�인 ?�루?�을 ?�공?�니??"
    },
    {
        "name": "박백?�드",
        "type": "portfolio",
        "title": "백엔??개발???�트?�리??,
        "status": "approved",
        "date": "2024-01-13",
        "experience": "5??,
        "skills": ["Java", "Spring", "MySQL"],
        "summary": "?�규모 ?�스???�계 경험, 마이?�로?�비???�문가로서 ?�정?�인 ?�비?��? 구축?�니??"
    },
    {
        "name": "최마케??,
        "type": "resume",
        "title": "?��???마�????�력??,
        "status": "reviewed",
        "date": "2024-01-12",
        "experience": "4??,
        "skills": ["Google Ads", "Facebook Ads", "Analytics"],
        "summary": "ROAS 300% ?�성, 고객 ?�과 최적???�문가로서 ?�이??기반 마�??�을 ?�현?�니??"
    },
    {
        "name": "?�데?�터",
        "type": "coverletter",
        "title": "?�이???�이?�티?�트 ?�소??,
        "status": "rejected",
        "date": "2024-01-11",
        "experience": "6??,
        "skills": ["Python", "TensorFlow", "SQL"],
        "summary": "머신?�닝 모델 개발, 빅데?�터 분석 ?�문가로서 ?�사?�트�??�출?�는 분석???�행?�니??"
    },
    {
        "name": "?��??�택",
        "type": "portfolio",
        "title": "?�?�택 개발???�트?�리??,
        "status": "approved",
        "date": "2024-01-10",
        "experience": "4??,
        "skills": ["React", "Node.js", "MongoDB"],
        "summary": "?�?�택 개발 경험, MERN ?�택 ?�문가로서 ?�전?????�플리�??�션??구축?�니??"
    },
    {
        "name": "?�디?�인",
        "type": "resume",
        "title": "그래???�자?�너 ?�력??,
        "status": "pending",
        "date": "2024-01-09",
        "experience": "3??,
        "skills": ["Illustrator", "Photoshop", "InDesign"],
        "summary": "브랜???�이?�티???�자???�문가, 50�??�상??브랜???�로?�트�??�공?�으�??�료?�습?�다."
    },
    {
        "name": "?�모바일",
        "type": "coverletter",
        "title": "모바????개발???�소??,
        "status": "reviewed",
        "date": "2024-01-08",
        "experience": "5??,
        "skills": ["Swift", "Kotlin", "Flutter"],
        "summary": "iOS/Android ??개발 ?�문가, 30�??�상???�을 출시?�고 100�??�운로드�??�성?�습?�다."
    },
    {
        "name": "강보??,
        "type": "resume",
        "title": "보안 ?��??�어 ?�력??,
        "status": "approved",
        "date": "2024-01-07",
        "experience": "7??,
        "skills": ["Penetration Testing", "SIEM", "Firewall"],
        "summary": "?�보보안 ?�문가, ?�기업 보안 ?�스??구축 �?침해?�고 ?�??경험??보유?�니??"
    },
    {
        "name": "조클?�우??,
        "type": "portfolio",
        "title": "?�라?�드 ?�키?�트 ?�트?�리??,
        "status": "reviewed",
        "date": "2024-01-06",
        "experience": "6??,
        "skills": ["AWS", "Azure", "Kubernetes"],
        "summary": "?�라?�드 ?�프???�계 ?�문가, 마이?�로?�비???�키?�처 구축 �??�영 경험??보유?�니??"
    },
    {
        "name": "백AI",
        "type": "coverletter",
        "title": "AI ?��??�어 ?�소??,
        "status": "pending",
        "date": "2024-01-05",
        "experience": "4??,
        "skills": ["Deep Learning", "NLP", "Computer Vision"],
        "summary": "?�공지??모델 개발 ?�문가, ?�연??처리 �?컴퓨??비전 분야?�서 ?�신?�인 ?�루?�을 ?�공?�니??"
    },
    {
        "name": "?�DevOps",
        "type": "resume",
        "title": "DevOps ?��??�어 ?�력??,
        "status": "approved",
        "date": "2024-01-04",
        "experience": "5??,
        "skills": ["Docker", "Jenkins", "Terraform"],
        "summary": "CI/CD ?�이?�라??구축 ?�문가, ?�동?�된 배포 ?�스?�으�?개발 ?�산?�을 극�??�합?�다."
    },
    {
        "name": "?�QA",
        "type": "coverletter",
        "title": "QA ?��??�어 ?�소??,
        "status": "reviewed",
        "date": "2024-01-03",
        "experience": "3??,
        "skills": ["Selenium", "JUnit", "Test Automation"],
        "summary": "?�질 보증 ?�문가, ?�동?�된 ?�스???�스?�으�??�프?�웨???�질??보장?�니??"
    },
    {
        "name": "구블록체??,
        "type": "portfolio",
        "title": "블록체인 개발???�트?�리??,
        "status": "pending",
        "date": "2024-01-02",
        "experience": "4??,
        "skills": ["Solidity", "Ethereum", "Smart Contracts"],
        "summary": "블록체인 기술 ?�문가, ?�마??컨트?�트 개발 �?DApp 구축 경험??보유?�니??"
    },
    {
        "name": "?�게??,
        "type": "resume",
        "title": "게임 개발???�력??,
        "status": "approved",
        "date": "2024-01-01",
        "experience": "6??,
        "skills": ["Unity", "C#", "Unreal Engine"],
        "summary": "게임 개발 ?�문가, 모바??�?PC 게임 개발 경험?�로 ?��??�는 게임???�작?�니??"
    },
    {
        "name": "김?�개�?,
        "type": "resume",
        "title": "??개발???�력??,
        "status": "reviewed",
        "date": "2024-01-16",
        "experience": "4??,
        "skills": ["Vue.js", "Laravel", "PostgreSQL"],
        "summary": "?�?�택 ??개발 ?�문가, ?�용??친화?�인 ???�플리�??�션??구축?�니??"
    },
    {
        "name": "?�모바일",
        "type": "coverletter",
        "title": "모바??개발???�소??,
        "status": "pending",
        "date": "2024-01-17",
        "experience": "3??,
        "skills": ["React Native", "Firebase", "Redux"],
        "summary": "?�로???�랫??모바????개발 ?�문가, ?�율?�인 개발 ?�로?�스�?추구?�니??"
    },
    {
        "name": "박데?�터",
        "type": "portfolio",
        "title": "?�이???��??�어 ?�트?�리??,
        "status": "approved",
        "date": "2024-01-18",
        "experience": "5??,
        "skills": ["Apache Spark", "Hadoop", "Kafka"],
        "summary": "빅데?�터 처리 ?�문가, ?�?�량 ?�이???�이?�라??구축 �??�영 경험??보유?�니??"
    },
    {
        "name": "최디?�인",
        "type": "resume",
        "title": "UI ?�자?�너 ?�력??,
        "status": "reviewed",
        "date": "2024-01-19",
        "experience": "2??,
        "skills": ["Sketch", "Principle", "Zeplin"],
        "summary": "?�용??경험 ?�자???�문가, 직�??�이�??�름?�운 ?�터?�이?��? ?�계?�니??"
    },
    {
        "name": "?�백?�드",
        "type": "coverletter",
        "title": "백엔??개발???�소??,
        "status": "rejected",
        "date": "2024-01-20",
        "experience": "6??,
        "skills": ["Python", "Django", "Redis"],
        "summary": "고성??백엔???�스??구축 ?�문가, ?�장 가?�한 ?�키?�처�??�계?�니??"
    },
    {
        "name": "?�프론트",
        "type": "portfolio",
        "title": "?�론?�엔??개발???�트?�리??,
        "status": "approved",
        "date": "2024-01-21",
        "experience": "3??,
        "skills": ["Angular", "RxJS", "TypeScript"],
        "summary": "모던 ?�론?�엔??개발 ?�문가, 반응?????�플리�??�션??구축?�니??"
    },
    {
        "name": "?�DevOps",
        "type": "resume",
        "title": "DevOps ?��??�어 ?�력??,
        "status": "pending",
        "date": "2024-01-22",
        "experience": "4??,
        "skills": ["Kubernetes", "Helm", "Prometheus"],
        "summary": "?�라?�드 ?�이?�브 ?�경 구축 ?�문가, ?�동?�된 ?�영 ?�스?�을 구축?�니??"
    },
    {
        "name": "?�AI",
        "type": "coverletter",
        "title": "AI ?�구???�소??,
        "status": "reviewed",
        "date": "2024-01-23",
        "experience": "5??,
        "skills": ["PyTorch", "Scikit-learn", "OpenCV"],
        "summary": "머신?�닝 ?�구 ?�문가, 최신 AI 기술???�용???�신?�인 ?�루?�을 개발?�니??"
    },
    {
        "name": "강보??,
        "type": "resume",
        "title": "보안 분석가 ?�력??,
        "status": "approved",
        "date": "2024-01-24",
        "experience": "7??,
        "skills": ["Wireshark", "Metasploit", "Nmap"],
        "summary": "?�트?�크 보안 ?�문가, 침해?�고 ?�??�?보안 취약??분석???�행?�니??"
    },
    {
        "name": "조클?�우??,
        "type": "portfolio",
        "title": "?�라?�드 ?��??�어 ?�트?�리??,
        "status": "reviewed",
        "date": "2024-01-25",
        "experience": "6??,
        "skills": ["GCP", "Terraform", "Ansible"],
        "summary": "멀???�라?�드 ?�경 구축 ?�문가, ?�프???�동??�?최적?��? ?�행?�니??"
    },
    
    # 2024??2???�이??(25�?
    {
        "name": "김?�?�택",
        "type": "resume",
        "title": "?�?�택 개발???�력??,
        "status": "reviewed",
        "date": "2024-02-15",
        "experience": "5??,
        "skills": ["MERN Stack", "GraphQL", "Docker"],
        "summary": "?�?�택 개발 ?�문가, ?��??�인 ???�플리�??�션???�율?�으�?구축?�니??"
    },
    {
        "name": "?�데?�터",
        "type": "coverletter",
        "title": "?�이??분석가 ?�소??,
        "status": "pending",
        "date": "2024-02-14",
        "experience": "4??,
        "skills": ["R", "Tableau", "Power BI"],
        "summary": "?�이???�각???�문가, 복잡???�이?��? ?�해?�기 ?�운 ?�사?�트�?변?�합?�다."
    },
    {
        "name": "박모바일",
        "type": "portfolio",
        "title": "모바????개발???�트?�리??,
        "status": "approved",
        "date": "2024-02-13",
        "experience": "3??,
        "skills": ["Swift", "Core Data", "ARKit"],
        "summary": "iOS ??개발 ?�문가, ?�용??경험??중시?�는 모바???�플리�??�션??개발?�니??"
    },
    {
        "name": "최프론트",
        "type": "resume",
        "title": "?�론?�엔??개발???�력??,
        "status": "reviewed",
        "date": "2024-02-12",
        "experience": "4??,
        "skills": ["Svelte", "Vite", "Tailwind CSS"],
        "summary": "모던 ?�론?�엔??개발 ?�문가, 빠르�?반응?????�플리�??�션??구축?�니??"
    },
    {
        "name": "?�백?�드",
        "type": "coverletter",
        "title": "백엔??개발???�소??,
        "status": "rejected",
        "date": "2024-02-11",
        "experience": "6??,
        "skills": ["Go", "Gin", "PostgreSQL"],
        "summary": "고성??백엔???�스??개발 ?�문가, 마이?�로?�비???�키?�처�?구축?�니??"
    },
    {
        "name": "?�디?�인",
        "type": "portfolio",
        "title": "UX ?�자?�너 ?�트?�리??,
        "status": "approved",
        "date": "2024-02-10",
        "experience": "3??,
        "skills": ["Framer", "Protopie", "Miro"],
        "summary": "?�용??경험 ?�자???�문가, 직�??�이�??�용?�기 ?�운 ?�터?�이?��? ?�계?�니??"
    },
    {
        "name": "?�DevOps",
        "type": "resume",
        "title": "DevOps ?��??�어 ?�력??,
        "status": "pending",
        "date": "2024-02-09",
        "experience": "5??,
        "skills": ["GitLab CI", "ArgoCD", "Istio"],
        "summary": "GitOps ?�문가, ?�동?�된 배포 �??�영 ?�스?�을 구축?�니??"
    },
    {
        "name": "?�AI",
        "type": "coverletter",
        "title": "AI ?��??�어 ?�소??,
        "status": "reviewed",
        "date": "2024-02-08",
        "experience": "4??,
        "skills": ["TensorFlow", "Keras", "MLflow"],
        "summary": "?�러??모델 개발 ?�문가, 최신 AI 기술???�용???�신?�인 ?�루?�을 ?�공?�니??"
    },
    {
        "name": "강보??,
        "type": "resume",
        "title": "보안 ?��??�어 ?�력??,
        "status": "approved",
        "date": "2024-02-07",
        "experience": "8??,
        "skills": ["Burp Suite", "OWASP ZAP", "Nessus"],
        "summary": "???�플리�??�션 보안 ?�문가, 취약??분석 �?보안 강화�??�행?�니??"
    },
    {
        "name": "조클?�우??,
        "type": "portfolio",
        "title": "?�라?�드 ?��??�어 ?�트?�리??,
        "status": "reviewed",
        "date": "2024-02-06",
        "experience": "6??,
        "skills": ["Azure", "ARM Templates", "Azure DevOps"],
        "summary": "Microsoft Azure ?�문가, ?�라?�드 ?�이?�브 ?�플리�??�션??구축?�니??"
    },
    {
        "name": "김?�?�택",
        "type": "resume",
        "title": "?�?�택 개발???�력??,
        "status": "reviewed",
        "date": "2024-02-05",
        "experience": "5??,
        "skills": ["React", "Node.js", "PostgreSQL"],
        "summary": "?�?�택 개발 ?�문가, ?��??�인 ???�플리�??�션???�율?�으�?구축?�니??"
    },
    {
        "name": "?�데?�터",
        "type": "coverletter",
        "title": "?�이??분석가 ?�소??,
        "status": "pending",
        "date": "2024-02-04",
        "experience": "4??,
        "skills": ["Python", "Pandas", "Matplotlib"],
        "summary": "?�이??분석 ?�문가, 복잡???�이?��? ?�해?�기 ?�운 ?�사?�트�?변?�합?�다."
    },
    {
        "name": "박모바일",
        "type": "portfolio",
        "title": "모바????개발???�트?�리??,
        "status": "approved",
        "date": "2024-02-03",
        "experience": "3??,
        "skills": ["React Native", "Expo", "Firebase"],
        "summary": "?�로???�랫??모바????개발 ?�문가, ?�율?�인 개발 ?�로?�스�?추구?�니??"
    },
    {
        "name": "최프론트",
        "type": "resume",
        "title": "?�론?�엔??개발???�력??,
        "status": "reviewed",
        "date": "2024-02-02",
        "experience": "4??,
        "skills": ["Angular", "RxJS", "NgRx"],
        "summary": "모던 ?�론?�엔??개발 ?�문가, 반응?????�플리�??�션??구축?�니??"
    },
    {
        "name": "?�백?�드",
        "type": "coverletter",
        "title": "백엔??개발???�소??,
        "status": "rejected",
        "date": "2024-02-01",
        "experience": "6??,
        "skills": ["Java", "Spring Boot", "MySQL"],
        "summary": "고성??백엔???�스??개발 ?�문가, 마이?�로?�비???�키?�처�?구축?�니??"
    }
]

# 면접 관�??�플 ?�이??(100�? - 지?�서 ?�이?��? 매칭
SAMPLE_INTERVIEWS = [
    # 2024??1??면접 ?�이??(25�?
    {
        "user_id": "user001",
        "company": "?�이�?,
        "position": "?�론?�엔??개발??,
        "date": "2024-01-20T10:00:00",
        "status": "scheduled",
        "type": "1�?면접",
        "hrManager": "김?�사",
        "location": "?�의??A",
        "notes": "React, TypeScript 경험 ?�인"
    },
    {
        "user_id": "user002",
        "company": "카카??,
        "position": "UI/UX ?�자?�너",
        "date": "2024-01-21T14:00:00",
        "status": "scheduled",
        "type": "1�?면접",
        "hrManager": "?�채??,
        "location": "?�의??B",
        "notes": "Figma, Adobe XD 경험 ?�인"
    },
    {
        "user_id": "user003",
        "company": "구�?",
        "position": "백엔??개발??,
        "date": "2024-01-22T09:30:00",
        "status": "completed",
        "type": "2�?면접",
        "hrManager": "박인??,
        "location": "?�의??C",
        "notes": "Java, Spring 경험 ?�인"
    },
    {
        "user_id": "user004",
        "company": "마이?�로?�프??,
        "position": "?�이???�이?�티?�트",
        "date": "2024-01-23T15:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user005",
        "company": "?�플",
        "position": "iOS 개발??,
        "date": "2024-01-24T11:00:00",
        "status": "cancelled"
    },
    {
        "user_id": "user006",
        "company": "메�?",
        "position": "AI ?��??�어",
        "date": "2024-01-25T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user007",
        "company": "?�플�?��",
        "position": "DevOps ?��??�어",
        "date": "2024-01-26T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user008",
        "company": "?�포?�파??,
        "position": "?�?�택 개발??,
        "date": "2024-01-27T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user009",
        "company": "?�버",
        "position": "보안 ?��??�어",
        "date": "2024-01-28T16:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user010",
        "company": "?�어비앤�?,
        "position": "?�라?�드 ?�키?�트",
        "date": "2024-01-29T09:00:00",
        "status": "completed"
    },
    {
        "user_id": "user011",
        "company": "?�위??,
        "position": "백엔??개발??,
        "date": "2024-01-30T11:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user012",
        "company": "링크?�인",
        "position": "?�이???��??�어",
        "date": "2024-01-31T13:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user013",
        "company": "?�퀘어",
        "position": "모바??개발??,
        "date": "2025-08-01T15:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user014",
        "company": "?�랙",
        "position": "?�론?�엔??개발??,
        "date": "2024-01-14T10:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user015",
        "company": "?�롭박스",
        "position": "QA ?��??�어",
        "date": "2024-01-15T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user016",
        "company": "?�성?�자",
        "position": "Android 개발??,
        "date": "2024-01-16T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user017",
        "company": "LG?�자",
        "position": "?�베?�드 개발??,
        "date": "2024-01-17T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user018",
        "company": "?��??�동�?,
        "position": "?�율주행 ?��??�어",
        "date": "2024-01-18T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user019",
        "company": "SK?�이?�스",
        "position": "반도�??��??�어",
        "date": "2024-01-19T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user020",
        "company": "KT",
        "position": "?�트?�크 ?��??�어",
        "date": "2024-01-20T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user021",
        "company": "SK?�레�?,
        "position": "5G ?��??�어",
        "date": "2024-01-21T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user022",
        "company": "LG?�플?�스",
        "position": "?�라?�드 ?��??�어",
        "date": "2024-01-22T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user023",
        "company": "CJ?�?�통??,
        "position": "로봇공학 ?��??�어",
        "date": "2024-01-23T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user024",
        "company": "?�스�?,
        "position": "?�마?�팩?�리 ?��??�어",
        "date": "2024-01-24T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user025",
        "company": "?�산?�너빌리??,
        "position": "IoT ?��??�어",
        "date": "2024-01-25T15:00:00",
        "status": "completed"
    },
    
    # 2024??2??면접 ?�이??(25�?
    {
        "user_id": "user026",
        "company": "쿠팡",
        "position": "?�?�택 개발??,
        "date": "2024-02-01T10:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user027",
        "company": "배달?��?�?,
        "position": "백엔??개발??,
        "date": "2024-02-16T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user028",
        "company": "?�스",
        "position": "?�론?�엔??개발??,
        "date": "2024-02-17T09:30:00",
        "status": "completed"
    },
    {
        "user_id": "user029",
        "company": "?�근마켓",
        "position": "모바??개발??,
        "date": "2024-02-18T15:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user030",
        "company": "무신??,
        "position": "UI/UX ?�자?�너",
        "date": "2024-02-19T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user031",
        "company": "?��???,
        "position": "?�이???�이?�티?�트",
        "date": "2024-02-20T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user032",
        "company": "?�빙",
        "position": "DevOps ?��??�어",
        "date": "2024-02-21T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user033",
        "company": "?�이�?,
        "position": "보안 ?��??�어",
        "date": "2024-02-22T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user034",
        "company": "?�슨",
        "position": "게임 개발??,
        "date": "2024-02-23T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user035",
        "company": "?�어비스",
        "position": "3D 그래???��??�어",
        "date": "2024-02-24T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user036",
        "company": "?�마?�게?�트",
        "position": "?�버 개발??,
        "date": "2024-02-25T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user037",
        "company": "?�마�?,
        "position": "?�라?�언??개발??,
        "date": "2024-02-26T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user038",
        "company": "컴투??,
        "position": "게임 기획??,
        "date": "2024-02-27T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user039",
        "company": "NC?�프??,
        "position": "?�트?�크 ?�로그래�?,
        "date": "2024-02-28T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user040",
        "company": "?�인",
        "position": "AI ?��??�어",
        "date": "2024-02-29T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user041",
        "company": "?��??�쉐??,
        "position": "?�?�택 개발??,
        "date": "2024-02-01T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user042",
        "company": "29CM",
        "position": "백엔??개발??,
        "date": "2024-02-02T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user043",
        "company": "지그재�?,
        "position": "?�론?�엔??개발??,
        "date": "2024-02-03T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user044",
        "company": "브랜??,
        "position": "모바??개발??,
        "date": "2024-02-04T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user045",
        "company": "마켓컬리",
        "position": "UI/UX ?�자?�너",
        "date": "2024-02-05T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user046",
        "company": "?�늘?�집",
        "position": "?�이???�이?�티?�트",
        "date": "2024-02-06T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user047",
        "company": "버킷?�레?�스",
        "position": "DevOps ?��??�어",
        "date": "2024-02-07T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user048",
        "company": "?�윗?�래�?,
        "position": "보안 ?��??�어",
        "date": "2024-02-08T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user049",
        "company": "뱅크?�러??,
        "position": "?�?�크 개발??,
        "date": "2024-02-09T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user050",
        "company": "카카?�뱅??,
        "position": "블록체인 ?��??�어",
        "date": "2024-02-10T10:00:00",
        "status": "completed"
    },
    
    # 2025??10??면접 ?�이??(25�?
    {
        "user_id": "user051",
        "company": "카카?�페??,
        "position": "결제 ?�스???��??�어",
        "date": "2025-10-15T10:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user052",
        "company": "?�이버파?�낸??,
        "position": "?�?�크 개발??,
        "date": "2025-10-16T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user053",
        "company": "?�스증권",
        "position": "?�??개발??,
        "date": "2025-10-17T09:30:00",
        "status": "completed"
    },
    {
        "user_id": "user054",
        "company": "KB�???�??,
        "position": "?��???뱅킹 ?��??�어",
        "date": "2025-10-18T15:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user055",
        "company": "?�한?�??,
        "position": "블록체인 개발??,
        "date": "2025-10-19T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user056",
        "company": "?�나?�??,
        "position": "AI 금융 ?��??�어",
        "date": "2025-10-20T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user057",
        "company": "?�리?�??,
        "position": "?�라?�드 ?��??�어",
        "date": "2025-10-21T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user058",
        "company": "IBK기업?�??,
        "position": "보안 ?��??�어",
        "date": "2025-10-22T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user059",
        "company": "NH?�협?�??,
        "position": "?�이???��??�어",
        "date": "2025-10-23T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user060",
        "company": "SC?�일?�??,
        "position": "모바??뱅킹 개발??,
        "date": "2025-10-24T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user061",
        "company": "케?�뱅??,
        "position": "?�?�택 개발??,
        "date": "2025-10-25T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user062",
        "company": "카카?�모빌리??,
        "position": "?�율주행 ?��??�어",
        "date": "2025-10-26T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user063",
        "company": "?�이버클로바",
        "position": "AI ?��??�어",
        "date": "2025-10-27T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user064",
        "company": "카카?�엔?�테?�먼??,
        "position": "콘텐�?추천 ?��??�어",
        "date": "2025-10-28T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user065",
        "company": "?�이버웹??,
        "position": "?�툰 ?�랫??개발??,
        "date": "2025-10-29T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user066",
        "company": "카카?�게?�즈",
        "position": "게임 ?�버 개발??,
        "date": "2025-10-30T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user067",
        "company": "?�이버클?�우??,
        "position": "?�라?�드 ?�키?�트",
        "date": "2025-10-31T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user068",
        "company": "카카?�엔?�프?�이�?,
        "position": "?�터?�라?�즈 ?�루??개발??,
        "date": "2025-11-01T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user069",
        "company": "?�이버파?�낸??,
        "position": "?�?�크 개발??,
        "date": "2025-11-02T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user070",
        "company": "카카?�뱅??,
        "position": "?��???뱅킹 ?��??�어",
        "date": "2025-11-03T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user071",
        "company": "?�스증권",
        "position": "?�??개발??,
        "date": "2025-11-04T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user072",
        "company": "KB�???�??,
        "position": "블록체인 개발??,
        "date": "2025-11-05T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user073",
        "company": "?�한?�??,
        "position": "AI 금융 ?��??�어",
        "date": "2025-11-06T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user074",
        "company": "?�나?�??,
        "position": "?�라?�드 ?��??�어",
        "date": "2025-11-07T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user075",
        "company": "?�리?�??,
        "position": "보안 ?��??�어",
        "date": "2025-11-08T10:00:00",
        "status": "completed"
    },
    
    # 2025??11??면접 ?�이??(25�?
    {
        "user_id": "user076",
        "company": "IBK기업?�??,
        "position": "?�이???��??�어",
        "date": "2025-11-15T10:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user077",
        "company": "NH?�협?�??,
        "position": "모바??뱅킹 개발??,
        "date": "2025-11-16T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user078",
        "company": "SC?�일?�??,
        "position": "?�?�택 개발??,
        "date": "2025-11-17T09:30:00",
        "status": "completed"
    },
    {
        "user_id": "user079",
        "company": "케?�뱅??,
        "position": "?�율주행 ?��??�어",
        "date": "2025-11-18T15:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user080",
        "company": "카카?�모빌리??,
        "position": "AI ?��??�어",
        "date": "2025-11-19T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user081",
        "company": "?�이버클로바",
        "position": "콘텐�?추천 ?��??�어",
        "date": "2025-11-20T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user082",
        "company": "카카?�엔?�테?�먼??,
        "position": "?�툰 ?�랫??개발??,
        "date": "2025-11-21T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user083",
        "company": "?�이버웹??,
        "position": "게임 ?�버 개발??,
        "date": "2025-11-22T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user084",
        "company": "카카?�게?�즈",
        "position": "?�라?�드 ?�키?�트",
        "date": "2025-11-23T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user085",
        "company": "?�이버클?�우??,
        "position": "?�터?�라?�즈 ?�루??개발??,
        "date": "2025-11-24T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user086",
        "company": "카카?�엔?�프?�이�?,
        "position": "?�?�크 개발??,
        "date": "2025-11-25T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user087",
        "company": "?�이버파?�낸??,
        "position": "?��???뱅킹 ?��??�어",
        "date": "2025-11-26T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user088",
        "company": "카카?�뱅??,
        "position": "?�??개발??,
        "date": "2025-11-27T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user089",
        "company": "?�스증권",
        "position": "블록체인 개발??,
        "date": "2025-11-28T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user090",
        "company": "KB�???�??,
        "position": "AI 금융 ?��??�어",
        "date": "2025-11-29T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user091",
        "company": "?�한?�??,
        "position": "?�라?�드 ?��??�어",
        "date": "2025-11-30T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user092",
        "company": "?�나?�??,
        "position": "보안 ?��??�어",
        "date": "2025-12-01T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user093",
        "company": "?�리?�??,
        "position": "?�이???��??�어",
        "date": "2025-12-02T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user094",
        "company": "IBK기업?�??,
        "position": "모바??뱅킹 개발??,
        "date": "2025-12-03T10:00:00",
        "status": "completed"
    },
    {
        "user_id": "user095",
        "company": "NH?�협?�??,
        "position": "?�?�택 개발??,
        "date": "2025-12-04T14:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user096",
        "company": "SC?�일?�??,
        "position": "?�율주행 ?��??�어",
        "date": "2025-12-05T09:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user097",
        "company": "케?�뱅??,
        "position": "AI ?��??�어",
        "date": "2025-12-06T15:00:00",
        "status": "completed"
    },
    {
        "user_id": "user098",
        "company": "카카?�모빌리??,
        "position": "콘텐�?추천 ?��??�어",
        "date": "2025-12-07T11:00:00",
        "status": "scheduled"
    },
    {
        "user_id": "user099",
        "company": "?�이버클로바",
        "position": "?�툰 ?�랫??개발??,
        "date": "2025-12-08T13:30:00",
        "status": "scheduled"
    },
    {
        "user_id": "user100",
        "company": "카카?�엔?�테?�먼??,
        "position": "게임 ?�버 개발??,
        "date": "2025-12-09T10:00:00",
        "status": "completed"
    }
]

# ?�용???�플 ?�이??SAMPLE_USERS = [
    {
        "username": "김개발",
        "email": "kim.dev@example.com",
        "role": "applicant"
    },
    {
        "username": "?�디?�인",
        "email": "lee.design@example.com",
        "role": "applicant"
    },
    {
        "username": "박백?�드",
        "email": "park.backend@example.com",
        "role": "applicant"
    },
    {
        "username": "최마케??,
        "email": "choi.marketing@example.com",
        "role": "applicant"
    },
    {
        "username": "?�데?�터",
        "email": "jung.data@example.com",
        "role": "applicant"
    },
    {
        "username": "?��??�택",
        "email": "han.fullstack@example.com",
        "role": "applicant"
    },
    {
        "username": "?�디?�인",
        "email": "yoon.design@example.com",
        "role": "applicant"
    },
    {
        "username": "?�모바일",
        "email": "lim.mobile@example.com",
        "role": "applicant"
    },
    {
        "username": "강보??,
        "email": "kang.security@example.com",
        "role": "applicant"
    },
    {
        "username": "조클?�우??,
        "email": "jo.cloud@example.com",
        "role": "applicant"
    },
    {
        "username": "백AI",
        "email": "baek.ai@example.com",
        "role": "applicant"
    },
    {
        "username": "?�DevOps",
        "email": "song.devops@example.com",
        "role": "applicant"
    },
    {
        "username": "?�QA",
        "email": "nam.qa@example.com",
        "role": "applicant"
    },
    {
        "username": "구블록체??,
        "email": "gu.blockchain@example.com",
        "role": "applicant"
    },
    {
        "username": "?�게??,
        "email": "yang.game@example.com",
        "role": "applicant"
    },
    {
        "username": "HR매니?�1",
        "email": "hr1@company.com",
        "role": "hr_manager"
    },
    {
        "username": "HR매니?�2",
        "email": "hr2@company.com",
        "role": "hr_manager"
    },
    {
        "username": "HR매니?�3",
        "email": "hr3@company.com",
        "role": "hr_manager"
    },
    {
        "username": "관리자",
        "email": "admin@hireme.com",
        "role": "admin"
    }
]

# API ?�우?�들
@app.get("/")
async def root():
    return {"message": "HireMe API ?�버가 ?�행 중입?�다!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# ?�용??관??API
@app.get("/api/users", response_model=List[User])
async def get_users():
    if db is None:
        return []
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]

@app.post("/api/users", response_model=User)
async def create_user(user: User):
    if db is None:
        return user
    user_dict = user.dict()
    user_dict["created_at"] = datetime.now()
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return User(**user_dict)

# ?�력??관??API
@app.get("/api/resumes", response_model=List[Resume])
async def get_resumes():
    if db is None:
        return []
    resumes = await db.resumes.find().to_list(1000)
    return [Resume(**resume) for resume in resumes]

@app.post("/api/resumes", response_model=Resume)
async def create_resume(resume: Resume):
    if db is None:
        return resume
    resume_dict = resume.dict()
    resume_dict["created_at"] = datetime.now()
    result = await db.resumes.insert_one(resume_dict)
    resume_dict["id"] = str(result.inserted_id)
    return Resume(**resume_dict)

# 면접 관??API
@app.get("/api/interviews", response_model=List[Interview])
async def get_interviews():
    if db is None:
        return []
    try:
        interviews = await db.interviews.find().to_list(1000)
        # MongoDB _id�?id�?변??        for interview in interviews:
            if "_id" in interview:
                interview["id"] = str(interview["_id"])
                del interview["_id"]
        return [Interview(**interview) for interview in interviews]
    except Exception as e:
        print(f"면접 목록 조회 ?�류: {str(e)}")
        return []

@app.post("/api/interviews", response_model=Interview)
async def create_interview(interview: Interview):
    if db is None:
        return interview
    interview_dict = interview.dict()
    interview_dict["created_at"] = datetime.now()
    result = await db.interviews.insert_one(interview_dict)
    interview_dict["id"] = str(result.inserted_id)
    return Interview(**interview_dict)

# 지?�서 관�?API
@app.get("/api/applications", response_model=List[Application])
async def get_applications():
    try:
        if db is None:
            return []
        
        # 컬렉?�이 존재?�는지 ?�인
        collections = await db.list_collection_names()
        if "applications" not in collections:
            return []
        
        applications = await db.applications.find().to_list(1000)
        return [Application(**app) for app in applications]
    except Exception as e:
        print(f"지?�서 목록 조회 ?�류: {str(e)}")
        return []

@app.get("/api/applications/stats", response_model=ApplicationStats)
async def get_application_stats():
    try:
        if db is None:
            return ApplicationStats(total=0, pending=0, reviewed=0, approved=0, rejected=0)
        
        # 컬렉?�이 존재?�는지 ?�인
        collections = await db.list_collection_names()
        if "applications" not in collections:
            return ApplicationStats(total=0, pending=0, reviewed=0, approved=0, rejected=0)
        
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        stats_result = await db.applications.aggregate(pipeline).to_list(None)
        
        stats = {
            "total": 0,
            "pending": 0,
            "reviewed": 0,
            "approved": 0,
            "rejected": 0
        }
        
        for stat in stats_result:
            status = stat["_id"]
            count = stat["count"]
            if status in stats:
                stats[status] = count
        
        # ?�체 개수 계산
        total_count = await db.applications.count_documents({})
        stats["total"] = total_count
        
        return ApplicationStats(**stats)
    except Exception as e:
        print(f"?�계 조회 ?�류: {str(e)}")
        # ?�류 발생 ??기본�?반환
        return ApplicationStats(total=0, pending=0, reviewed=0, approved=0, rejected=0)

@app.get("/api/applications/{application_id}", response_model=Application)
async def get_application(application_id: str):
    if db is None:
        raise HTTPException(status_code=404, detail="MongoDB가 ?�결?��? ?�았?�니??")
    
    try:
        from bson import ObjectId
        application = await db.applications.find_one({"_id": ObjectId(application_id)})
        if application is None:
            raise HTTPException(status_code=404, detail="지?�서�?찾을 ???�습?�다.")
        
        application["id"] = str(application["_id"])
        return Application(**application)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지?�서 조회 ?�패: {str(e)}")

@app.get("/api/interviews/{interview_id}")
async def get_interview(interview_id: str):
    if db is None:
        raise HTTPException(status_code=404, detail="MongoDB가 ?�결?��? ?�았?�니??")
    
    try:
        from bson import ObjectId
        interview = await db.interviews.find_one({"_id": ObjectId(interview_id)})
        if interview is None:
            raise HTTPException(status_code=404, detail="면접 ?�보�?찾을 ???�습?�다.")
        
        interview["id"] = str(interview["_id"])
        return interview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"면접 ?�보 조회 ?�패: {str(e)}")

@app.get("/api/portfolios/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    if db is None:
        raise HTTPException(status_code=404, detail="MongoDB가 ?�결?��? ?�았?�니??")
    
    try:
        from bson import ObjectId
        portfolio = await db.portfolios.find_one({"_id": ObjectId(portfolio_id)})
        if portfolio is None:
            raise HTTPException(status_code=404, detail="?�트?�리???�보�?찾을 ???�습?�다.")
        
        portfolio["id"] = str(portfolio["_id"])
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"?�트?�리???�보 조회 ?�패: {str(e)}")

@app.post("/api/applications", response_model=Application)
async def create_application(application: Application):
    if db is None:
        return application
    app_dict = application.dict()
    app_dict["created_at"] = datetime.now()
    result = await db.applications.insert_one(app_dict)
    app_dict["id"] = str(result.inserted_id)
    return Application(**app_dict)

@app.post("/api/applications/seed")
async def seed_applications():
    """?�플 ?�이?��? MongoDB???�입"""
    if db is None:
        return {"message": "MongoDB가 ?�결?��? ?�았?�니??"}
    
    try:
        # 기존 ?�이????��
        await db.applications.delete_many({})
        
        # ?�플 ?�이???�입
        for app_data in SAMPLE_APPLICATIONS:
            app_data["created_at"] = datetime.now()
            await db.applications.insert_one(app_data)
        
        return {"message": f"{len(SAMPLE_APPLICATIONS)}개의 ?�플 지?�서가 ?�공?�으�?추�??�었?�니??"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"?�플 ?�이???�입 ?�패: {str(e)}")

@app.post("/api/interviews/seed")
async def seed_interviews():
    """면접 관�??�플 ?�이?��? MongoDB???�입 - 지?�서 ?�이?��? 매칭"""
    if db is None:
        return {"message": "MongoDB가 ?�결?��? ?�았?�니??"}
    
    try:
        # 기존 ?�이????��
        await db.interviews.delete_many({})
        
        # 지?�서 ?�이?��? 매칭?�는 면접 ?�이???�성
        matched_interviews = []
        for i, application in enumerate(SAMPLE_APPLICATIONS):
            # 지?�서???�름�?직무�?면접 ?�이?�에 반영
            company = SAMPLE_INTERVIEWS[i]["company"] if i < len(SAMPLE_INTERVIEWS) else "기업"
            date = SAMPLE_INTERVIEWS[i]["date"] if i < len(SAMPLE_INTERVIEWS) else "2024-01-20T10:00:00"
            status = SAMPLE_INTERVIEWS[i]["status"] if i < len(SAMPLE_INTERVIEWS) else "scheduled"
            
            # ?�로 추�????�드?�에 ?�???�전?�게 ?�근
            interview_type = SAMPLE_INTERVIEWS[i].get("type", "1�?면접") if i < len(SAMPLE_INTERVIEWS) else "1�?면접"
            hr_manager = SAMPLE_INTERVIEWS[i].get("hrManager", "면접관") if i < len(SAMPLE_INTERVIEWS) else "면접관"
            location = SAMPLE_INTERVIEWS[i].get("location", "?�의??) if i < len(SAMPLE_INTERVIEWS) else "?�의??
            notes = SAMPLE_INTERVIEWS[i].get("notes", "") if i < len(SAMPLE_INTERVIEWS) else ""
            
            interview = {
                "user_id": f"user{i+1:03d}",
                "company": company,
                "position": f"{application['name']} - {application['title']}",  # 지?�자 ?�름 + 직무
                "date": date,
                "status": status,
                "type": interview_type,
                "hrManager": hr_manager,
                "location": location,
                "notes": notes,
                "created_at": datetime.now()
            }
            matched_interviews.append(interview)
        
        # ???�이???�입
        for interview in matched_interviews:
            await db.interviews.insert_one(interview)
        
        return {"message": f"{len(matched_interviews)}개의 ?�플 면접???�공?�으�?추�??�었?�니??"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"?�플 ?�이???�입 ?�패: {str(e)}")

@app.post("/api/users/seed")
async def seed_users():
    """?�용???�플 ?�이?��? MongoDB???�입"""
    if db is None:
        return {"message": "MongoDB가 ?�결?��? ?�았?�니??"}
    
    try:
        # 기존 ?�이????��
        await db.users.delete_many({})
        
        # ?�플 ?�이???�입
        for user_data in SAMPLE_USERS:
            user_data["created_at"] = datetime.now()
            await db.users.insert_one(user_data)
        
        return {"message": f"{len(SAMPLE_USERS)}개의 ?�플 ?�용?��? ?�공?�으�?추�??�었?�니??"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"?�플 ?�이???�입 ?�패: {str(e)}")

@app.post("/api/seed-all")
async def seed_all_data():
    """모든 ?�플 ?�이?��? MongoDB???�입 - 지?�서?� 면접 ?�이??매칭"""
    if db is None:
        return {"message": "MongoDB가 ?�결?��? ?�았?�니??"}
    
    try:
        # 기존 ?�이????��
        await db.applications.delete_many({})
        await db.interviews.delete_many({})
        await db.users.delete_many({})
        
        # 지?�서 ?�이???�입
        for app_data in SAMPLE_APPLICATIONS:
            app_data["created_at"] = datetime.now()
            await db.applications.insert_one(app_data)
        
        # 지?�서 ?�이?��? 매칭?�는 면접 ?�이???�성 �??�입
        matched_interviews = []
        for i, application in enumerate(SAMPLE_APPLICATIONS):
            company = SAMPLE_INTERVIEWS[i]["company"] if i < len(SAMPLE_INTERVIEWS) else "기업"
            date = SAMPLE_INTERVIEWS[i]["date"] if i < len(SAMPLE_INTERVIEWS) else "2024-01-20T10:00:00"
            status = SAMPLE_INTERVIEWS[i]["status"] if i < len(SAMPLE_INTERVIEWS) else "scheduled"
            
            # ?�로 추�????�드?�에 ?�???�전?�게 ?�근
            interview_type = SAMPLE_INTERVIEWS[i].get("type", "1�?면접") if i < len(SAMPLE_INTERVIEWS) else "1�?면접"
            hr_manager = SAMPLE_INTERVIEWS[i].get("hrManager", "면접관") if i < len(SAMPLE_INTERVIEWS) else "면접관"
            location = SAMPLE_INTERVIEWS[i].get("location", "?�의??) if i < len(SAMPLE_INTERVIEWS) else "?�의??
            notes = SAMPLE_INTERVIEWS[i].get("notes", "") if i < len(SAMPLE_INTERVIEWS) else ""
            
            interview = {
                "user_id": f"user{i+1:03d}",
                "company": company,
                "position": f"{application['name']} - {application['title']}",  # 지?�자 ?�름 + 직무
                "date": date,
                "status": status,
                "type": interview_type,
                "hrManager": hr_manager,
                "location": location,
                "notes": notes,
                "created_at": datetime.now()
            }
            matched_interviews.append(interview)
            await db.interviews.insert_one(interview)
        
        # ?�용???�이???�입
        for user_data in SAMPLE_USERS:
            user_data["created_at"] = datetime.now()
            await db.users.insert_one(user_data)
        
        total_count = len(SAMPLE_APPLICATIONS) + len(matched_interviews) + len(SAMPLE_USERS)
        return {
            "message": f"모든 ?�플 ?�이?��? ?�공?�으�?추�??�었?�니??",
            "details": {
                "applications": len(SAMPLE_APPLICATIONS),
                "interviews": len(matched_interviews),
                "users": len(SAMPLE_USERS),
                "total": total_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"?�플 ?�이???�입 ?�패: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
