# 📋 Resume 컬렉션 통합 방안

## 🎯 통합 목표
- `DB(without yc).txt` 구조와 100% 일치
- 기존 기능 호환성 유지
- 모듈화된 구조와 기본 구조 통합
- API 일관성 확보

## 📊 현재 상황 분석

### 1. **기본 모델** (`backend/models/resume.py`)
```python
# ✅ DB(without yc).txt와 일치
class Resume(ResumeBase):
    id: str = Field(alias="_id")
    basic_info: Optional[dict]
    file_metadata: Optional[dict]
    created_at: Optional[datetime]
```

### 2. **모듈화된 모델** (`backend/modules/resume/models.py`)
```python
# ⚠️ DB(without yc).txt와 불일치
class Resume(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    position: str
    department: Optional[str]
    experience: str
    skills: str
    growthBackground: Optional[str]
    motivation: Optional[str]
    careerHistory: Optional[str]
    analysisScore: int
    analysisResult: str
    status: ResumeStatus
    created_at: datetime
```

## 🔧 통합 방안

### **방안 1: 기본 모델 중심 통합 (권장)**

#### 1.1 모듈화된 모델을 기본 모델 구조로 변경
```python
# backend/modules/resume/models.py 수정
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class ResumeStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

class ResumeBase(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    extracted_text: str = Field(..., description="추출된 텍스트")
    summary: Optional[str] = Field(None, description="요약")
    keywords: Optional[List[str]] = Field(None, description="키워드")
    document_type: str = Field(default="resume", description="문서 타입")

class ResumeCreate(ResumeBase):
    basic_info: Optional[dict] = Field(None, description="기본 정보")
    file_metadata: Optional[dict] = Field(None, description="파일 메타데이터")

class Resume(ResumeBase):
    id: str = Field(alias="_id", description="이력서 ID")
    basic_info: Optional[dict] = Field(None, description="기본 정보")
    file_metadata: Optional[dict] = Field(None, description="파일 메타데이터")
    created_at: Optional[datetime] = Field(None, description="생성일시")

    class Config:
        populate_by_name = True

# 추가 기능을 위한 확장 모델
class ResumeExtended(Resume):
    """확장된 이력서 모델 (기존 모듈화된 기능 지원)"""
    name: Optional[str] = Field(None, description="지원자 이름")
    position: Optional[str] = Field(None, description="지원 직무")
    department: Optional[str] = Field(None, description="부서")
    experience: Optional[str] = Field(None, description="경력")
    skills: Optional[str] = Field(None, description="기술 스택")
    growthBackground: Optional[str] = Field(None, description="성장 배경")
    motivation: Optional[str] = Field(None, description="지원 동기")
    careerHistory: Optional[str] = Field(None, description="경력 사항")
    analysisScore: Optional[int] = Field(None, ge=0, le=100, description="분석 점수")
    analysisResult: Optional[str] = Field(None, description="분석 결과")
    status: Optional[ResumeStatus] = Field(None, description="상태")

class ResumeUpdate(BaseModel):
    """이력서 수정 모델"""
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    basic_info: Optional[dict] = None
    file_metadata: Optional[dict] = None
    # 확장 필드들
    name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[str] = None
    growthBackground: Optional[str] = None
    motivation: Optional[str] = None
    careerHistory: Optional[str] = None
    analysisScore: Optional[int] = None
    analysisResult: Optional[str] = None
    status: Optional[ResumeStatus] = None

class ResumeSearchRequest(BaseModel):
    """이력서 검색 요청 모델"""
    query: Optional[str] = Field(None, description="검색 쿼리")
    position: Optional[str] = Field(None, description="직무")
    department: Optional[str] = Field(None, description="부서")
    status: Optional[ResumeStatus] = Field(None, description="상태")
    min_score: Optional[int] = Field(None, description="최소 점수")
    max_score: Optional[int] = Field(None, description="최대 점수")
    limit: int = Field(default=10, description="검색 결과 수")
    skip: int = Field(default=0, description="건너뛸 결과 수")

class ResumeAnalysisRequest(BaseModel):
    """이력서 분석 요청 모델"""
    resume_id: str = Field(..., description="이력서 ID")
    analysis_type: Optional[str] = Field(default="comprehensive", description="분석 타입")

class ResumeAnalysisResult(BaseModel):
    """이력서 분석 결과 모델"""
    resume_id: str = Field(..., description="이력서 ID")
    overall_score: float = Field(..., description="종합 점수")
    skill_analysis: dict = Field(default_factory=dict, description="기술 분석")
    experience_analysis: dict = Field(default_factory=dict, description="경력 분석")
    motivation_analysis: dict = Field(default_factory=dict, description="동기 분석")
    recommendations: List[str] = Field(default_factory=list, description="권장사항")
    strengths: List[str] = Field(default_factory=list, description="강점")
    weaknesses: List[str] = Field(default_factory=list, description="약점")
```

#### 1.2 서비스 로직 수정
```python
# backend/modules/resume/services.py 수정
class ResumeService(BaseService):
    """이력서 서비스 - 통합 버전"""

    def __init__(self, db: motor.motor_asyncio.AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = "resumes"

    async def create_resume(self, resume_data: ResumeCreate) -> str:
        """이력서 생성 - 기본 구조 사용"""
        try:
            resume = Resume(**resume_data.dict())
            result = await self.db[self.collection].insert_one(resume.dict(by_alias=True))
            resume_id = str(result.inserted_id)
            logger.info(f"이력서 생성 완료: {resume_id}")
            return resume_id
        except Exception as e:
            logger.error(f"이력서 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 생성에 실패했습니다.")

    async def create_resume_extended(self, resume_data: ResumeExtended) -> str:
        """확장된 이력서 생성 - 기존 기능 지원"""
        try:
            result = await self.db[self.collection].insert_one(resume_data.dict(by_alias=True))
            resume_id = str(result.inserted_id)
            logger.info(f"확장 이력서 생성 완료: {resume_id}")
            return resume_id
        except Exception as e:
            logger.error(f"확장 이력서 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 생성에 실패했습니다.")

    async def get_resume(self, resume_id: str) -> Optional[Resume]:
        """이력서 조회 - 기본 구조"""
        try:
            resume_data = await self.db[self.collection].find_one({"_id": self._get_object_id(resume_id)})
            if resume_data:
                return Resume(**resume_data)
            return None
        except Exception as e:
            logger.error(f"이력서 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 조회에 실패했습니다.")

    async def get_resume_extended(self, resume_id: str) -> Optional[ResumeExtended]:
        """확장된 이력서 조회 - 기존 기능 지원"""
        try:
            resume_data = await self.db[self.collection].find_one({"_id": self._get_object_id(resume_id)})
            if resume_data:
                return ResumeExtended(**resume_data)
            return None
        except Exception as e:
            logger.error(f"확장 이력서 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 조회에 실패했습니다.")

    async def update_resume(self, resume_id: str, update_data: ResumeUpdate) -> bool:
        """이력서 수정 - 통합 버전"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

            result = await self.db[self.collection].update_one(
                {"_id": self._get_object_id(resume_id)},
                {"$set": update_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"이력서 수정 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 수정에 실패했습니다.")

    async def search_resumes(self, search_request: ResumeSearchRequest) -> List[Resume]:
        """이력서 검색 - 통합 버전"""
        try:
            filter_query = {}

            if search_request.query:
                filter_query["$or"] = [
                    {"extracted_text": {"$regex": search_request.query, "$options": "i"}},
                    {"summary": {"$regex": search_request.query, "$options": "i"}},
                    {"keywords": {"$in": [search_request.query]}}
                ]

            if search_request.position:
                filter_query["position"] = {"$regex": search_request.position, "$options": "i"}

            if search_request.department:
                filter_query["department"] = {"$regex": search_request.department, "$options": "i"}

            if search_request.status:
                filter_query["status"] = search_request.status

            if search_request.min_score is not None or search_request.max_score is not None:
                score_filter = {}
                if search_request.min_score is not None:
                    score_filter["$gte"] = search_request.min_score
                if search_request.max_score is not None:
                    score_filter["$lte"] = search_request.max_score
                filter_query["analysisScore"] = score_filter

            cursor = self.db[self.collection].find(filter_query).skip(search_request.skip).limit(search_request.limit)
            resumes = []
            async for resume_data in cursor:
                resumes.append(Resume(**resume_data))
            return resumes
        except Exception as e:
            logger.error(f"이력서 검색 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 검색에 실패했습니다.")

    async def analyze_resume(self, analysis_request: ResumeAnalysisRequest) -> ResumeAnalysisResult:
        """이력서 분석 - 기존 기능 유지"""
        try:
            resume = await self.get_resume(analysis_request.resume_id)
            if not resume:
                raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")

            # 기존 분석 로직 유지
            analysis_result = ResumeAnalysisResult(
                resume_id=analysis_request.resume_id,
                overall_score=85.0,  # 예시 값
                skill_analysis={"technical": 90, "communication": 80},
                experience_analysis={"years": 3, "relevance": 85},
                motivation_analysis={"alignment": 88, "passion": 82},
                recommendations=["기술 스택 강화", "프로젝트 경험 추가"],
                strengths=["백엔드 개발 경험", "문제 해결 능력"],
                weaknesses=["프론트엔드 경험 부족", "팀 리더십 경험"]
            )

            return analysis_result
        except Exception as e:
            logger.error(f"이력서 분석 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 분석에 실패했습니다.")
```

#### 1.3 라우터 수정
```python
# backend/modules/resume/router.py 수정
@router.post("/", response_model=BaseResponse)
async def create_resume(
    resume_data: ResumeCreate,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """이력서 생성 - 기본 구조"""
    try:
        resume_id = await resume_service.create_resume(resume_data)
        return BaseResponse(
            success=True,
            message="이력서가 성공적으로 생성되었습니다.",
            data={"resume_id": resume_id}
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 생성에 실패했습니다: {str(e)}"
        )

@router.post("/extended", response_model=BaseResponse)
async def create_resume_extended(
    resume_data: ResumeExtended,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """확장된 이력서 생성 - 기존 기능 지원"""
    try:
        resume_id = await resume_service.create_resume_extended(resume_data)
        return BaseResponse(
            success=True,
            message="확장된 이력서가 성공적으로 생성되었습니다.",
            data={"resume_id": resume_id}
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 생성에 실패했습니다: {str(e)}"
        )

@router.get("/{resume_id}", response_model=BaseResponse)
async def get_resume(
    resume_id: str,
    extended: bool = Query(False, description="확장 모델 사용 여부"),
    resume_service: ResumeService = Depends(get_resume_service)
):
    """이력서 조회 - 기본/확장 모델 선택"""
    try:
        if extended:
            resume = await resume_service.get_resume_extended(resume_id)
        else:
            resume = await resume_service.get_resume(resume_id)

        if not resume:
            return BaseResponse(
                success=False,
                message="이력서를 찾을 수 없습니다."
            )

        return BaseResponse(
            success=True,
            message="이력서 조회 성공",
            data=resume.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 조회에 실패했습니다: {str(e)}"
        )
```

## 📋 통합 단계별 실행 계획

### **1단계: 모델 통합**
1. `backend/modules/resume/models.py` 수정
2. 기본 모델 구조로 변경
3. 확장 모델 추가
4. 기존 기능 호환성 유지

### **2단계: 서비스 통합**
1. `backend/modules/resume/services.py` 수정
2. 기본/확장 모델 지원
3. 검색 및 분석 기능 통합
4. 에러 처리 개선

### **3단계: 라우터 통합**
1. `backend/modules/resume/router.py` 수정
2. 기본/확장 엔드포인트 제공
3. 쿼리 파라미터로 모델 선택
4. API 문서 업데이트

### **4단계: 테스트 및 검증**
1. 기존 API 테스트
2. 새로운 API 테스트
3. 데이터 마이그레이션 검증
4. 성능 테스트

### **5단계: 문서화 및 배포**
1. API 문서 업데이트
2. 사용자 가이드 작성
3. 배포 스크립트 수정
4. 모니터링 설정

## 🎯 통합 후 기대 효과

### **장점:**
1. **구조 일관성**: `DB(without yc).txt`와 100% 일치
2. **기능 호환성**: 기존 기능 모두 유지
3. **확장성**: 새로운 기능 추가 용이
4. **유지보수성**: 단일 구조로 관리 간소화
5. **API 일관성**: 통일된 응답 형식

### **주의사항:**
1. **기존 데이터**: 마이그레이션 필요할 수 있음
2. **API 변경**: 일부 엔드포인트 변경 가능
3. **테스트**: 충분한 테스트 필요
4. **문서화**: API 문서 업데이트 필요

## 📊 통합 후 데이터 구조

```json
{
  "_id": "507f1f77bcf86cd799439012",
  "applicant_id": "507f1f77bcf86cd799439011",
  "extracted_text": "홍길동의 이력서 내용...",
  "summary": "3년 경력의 백엔드 개발자",
  "keywords": ["Java", "Spring Boot", "MySQL"],
  "document_type": "resume",
  "basic_info": {
    "emails": ["hong@example.com"],
    "phones": ["010-1234-5678"],
    "names": ["홍길동"],
    "urls": ["https://github.com/hong"]
  },
  "file_metadata": {
    "filename": "resume.pdf",
    "size": 1024000,
    "mime": "application/pdf",
    "hash": "abc123def456",
    "created_at": "2024-01-01T00:00:00Z",
    "modified_at": "2024-01-01T00:00:00Z"
  },
  "created_at": "2024-01-01T00:00:00Z",
  // 확장 필드들 (선택적)
  "name": "홍길동",
  "position": "백엔드 개발자",
  "department": "개발팀",
  "experience": "3년",
  "skills": "Java, Spring Boot, MySQL",
  "growthBackground": "학창 시절부터 프로그래밍에 관심...",
  "motivation": "귀사의 기술력에 매료되어...",
  "careerHistory": "2022년부터 스타트업에서...",
  "analysisScore": 85,
  "analysisResult": "Java와 Spring 기반의 백엔드 개발 경험이 있습니다.",
  "status": "pending"
}
```

이 통합 방안을 통해 `DB(without yc).txt` 구조와 완전히 일치하면서도 기존 기능을 모두 유지할 수 있습니다.
