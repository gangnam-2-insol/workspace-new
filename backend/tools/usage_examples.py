"""
툴 래핑 사용 예시
"""

import asyncio
import logging
from typing import Dict, Any
from api_wrapper import HireMeAPIWrapper

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_applicant_management():
    """지원자 관리 예시"""
    print("=== 지원자 관리 예시 ===")

    async with HireMeAPIWrapper() as api:
        # 1. 지원자 생성
        applicant_data = {
            "name": "김개발",
            "email": "kim@example.com",
            "phone": "010-1234-5678",
            "position": "프론트엔드 개발자",
            "experience": "3년",
            "skills": ["React", "TypeScript", "Node.js"],
            "job_posting_id": "job_123"
        }

        try:
            result = await api.applicant.create_applicant(applicant_data)
            print(f"✅ 지원자 생성 성공: {result['name']}")
            applicant_id = result['id']
        except Exception as e:
            print(f"❌ 지원자 생성 실패: {e}")
            return

        # 2. 지원자 목록 조회
        try:
            applicants = await api.applicant.get_applicants(
                skip=0,
                limit=10,
                status="pending",
                position="개발자"
            )
            print(f"✅ 지원자 목록 조회 성공: {len(applicants['applicants'])}명")
        except Exception as e:
            print(f"❌ 지원자 목록 조회 실패: {e}")

        # 3. 지원자 상태 업데이트
        try:
            result = await api.applicant.update_applicant_status(applicant_id, "서류합격")
            print(f"✅ 지원자 상태 업데이트 성공: {result['status']}")
        except Exception as e:
            print(f"❌ 지원자 상태 업데이트 실패: {e}")

async def example_chatbot():
    """채팅봇 예시"""
    print("\n=== 채팅봇 예시 ===")

    async with HireMeAPIWrapper() as api:
        # 1. AI 어시스턴트 채팅
        try:
            response = await api.chatbot.ai_assistant_chat(
                user_input="프론트엔드 개발자 채용공고를 작성해주세요",
                session_id="session_123"
            )
            print(f"✅ AI 어시스턴트 응답: {response['message'][:100]}...")
        except Exception as e:
            print(f"❌ AI 어시스턴트 채팅 실패: {e}")

        # 2. AI 제목 추천
        try:
            response = await api.chatbot.generate_title(
                job_description="React, TypeScript 경험자 모집",
                company_name="테크스타트업",
                concept="신입친화형"
            )
            print(f"✅ 제목 추천: {response['title']}")
        except Exception as e:
            print(f"❌ 제목 추천 실패: {e}")

async def example_pdf_ocr():
    """PDF OCR 예시"""
    print("\n=== PDF OCR 예시 ===")

    async with HireMeAPIWrapper() as api:
        # 1. 이력서 업로드 및 OCR 처리
        try:
            result = await api.pdf_ocr.upload_resume(
                file_path="resume.pdf",
                name="김개발",
                email="kim@example.com",
                phone="010-1234-5678",
                job_posting_id="job_123"
            )
            print(f"✅ 이력서 업로드 성공: {result['message']}")
        except Exception as e:
            print(f"❌ 이력서 업로드 실패: {e}")

        # 2. 자기소개서 업로드 및 OCR 처리
        try:
            result = await api.pdf_ocr.upload_cover_letter(
                file_path="cover_letter.pdf",
                job_posting_id="job_123"
            )
            print(f"✅ 자기소개서 업로드 성공: {result['message']}")
        except Exception as e:
            print(f"❌ 자기소개서 업로드 실패: {e}")

async def example_github_analysis():
    """GitHub 분석 예시"""
    print("\n=== GitHub 분석 예시 ===")

    async with HireMeAPIWrapper() as api:
        # 1. GitHub 사용자 분석
        try:
            result = await api.github.analyze_user(
                username="github_username",
                force_reanalysis=False
            )
            print(f"✅ GitHub 사용자 분석 성공: {result['username']}")
            print(f"   총 저장소: {result['total_repos']}개")
            print(f"   주요 언어: {', '.join(result['main_languages'][:3])}")
        except Exception as e:
            print(f"❌ GitHub 사용자 분석 실패: {e}")

        # 2. GitHub 저장소 분석
        try:
            result = await api.github.analyze_repository(
                username="github_username",
                repo_name="project_name"
            )
            print(f"✅ GitHub 저장소 분석 성공: {result['repo_name']}")
        except Exception as e:
            print(f"❌ GitHub 저장소 분석 실패: {e}")

async def example_resume_search():
    """이력서 검색 예시"""
    print("\n=== 이력서 검색 예시 ===")

    async with HireMeAPIWrapper() as api:
        # 1. 키워드 검색
        try:
            result = await api.resume_search.keyword_search(
                query="React TypeScript",
                limit=10
            )
            print(f"✅ 키워드 검색 성공: {len(result['results'])}개 결과")
        except Exception as e:
            print(f"❌ 키워드 검색 실패: {e}")

        # 2. 하이브리드 검색
        try:
            filters = {
                "experience_years": [3, 5],
                "skills": ["React", "TypeScript"]
            }
            result = await api.resume_search.hybrid_search(
                query="프론트엔드 개발자",
                filters=filters,
                limit=10
            )
            print(f"✅ 하이브리드 검색 성공: {len(result['results'])}개 결과")
        except Exception as e:
            print(f"❌ 하이브리드 검색 실패: {e}")

async def example_ai_analysis():
    """AI 분석 예시"""
    print("\n=== AI 분석 예시 ===")

    async with HireMeAPIWrapper() as api:
        # 1. 이력서 AI 분석
        try:
            result = await api.ai_analysis.analyze_resume(
                applicant_id="applicant_123",
                analyzer_type="openai",
                force_reanalysis=False
            )
            print(f"✅ 이력서 AI 분석 성공: {result['analysis_score']}점")
        except Exception as e:
            print(f"❌ 이력서 AI 분석 실패: {e}")

        # 2. 일괄 이력서 분석
        try:
            result = await api.ai_analysis.batch_analyze_resumes(
                applicant_ids=["applicant_123", "applicant_456"],
                analyzer_type="openai"
            )
            print(f"✅ 일괄 이력서 분석 성공: {len(result['results'])}개 완료")
        except Exception as e:
            print(f"❌ 일괄 이력서 분석 실패: {e}")

async def example_complete_workflow():
    """완전한 워크플로우 예시"""
    print("\n=== 완전한 워크플로우 예시 ===")

    async with HireMeAPIWrapper() as api:
        try:
            # 1. 채용공고 작성 (AI 어시스턴트)
            chat_response = await api.chatbot.ai_assistant_chat(
                user_input="React 개발자 채용공고를 작성해주세요. 3년 이상 경력자를 원합니다.",
                session_id="workflow_session"
            )
            print("1️⃣ 채용공고 작성 완료")

            # 2. 이력서 업로드 및 OCR
            ocr_result = await api.pdf_ocr.upload_resume(
                file_path="resume.pdf",
                job_posting_id="job_123"
            )
            applicant_id = ocr_result['applicant_id']
            print("2️⃣ 이력서 업로드 및 OCR 완료")

            # 3. AI 분석
            analysis_result = await api.ai_analysis.analyze_resume(
                applicant_id=applicant_id,
                analyzer_type="openai"
            )
            print("3️⃣ AI 분석 완료")

            # 4. 유사한 지원자 검색
            search_result = await api.resume_search.hybrid_search(
                query="React 개발자",
                filters={"experience_years": [3, 5]},
                limit=5
            )
            print("4️⃣ 유사 지원자 검색 완료")

            # 5. GitHub 분석 (선택적)
            github_result = await api.github.analyze_user(
                username="applicant_github_username"
            )
            print("5️⃣ GitHub 분석 완료")

            # 6. 지원자 상태 업데이트
            status_result = await api.applicant.update_applicant_status(
                applicant_id, "서류합격"
            )
            print("6️⃣ 지원자 상태 업데이트 완료")

            print("✅ 전체 워크플로우 완료!")

        except Exception as e:
            print(f"❌ 워크플로우 실패: {e}")

async def main():
    """메인 함수"""
    print("🚀 AI 채용 관리 시스템 툴 래핑 예시 시작\n")

    # 각 기능별 예시 실행
    await example_applicant_management()
    await example_chatbot()
    await example_pdf_ocr()
    await example_github_analysis()
    await example_resume_search()
    await example_ai_analysis()
    await example_complete_workflow()

    print("\n🎉 모든 예시 완료!")

if __name__ == "__main__":
    asyncio.run(main())
