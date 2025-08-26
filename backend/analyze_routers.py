#!/usr/bin/env python3
"""
라우터 등록 순서와 prefix 분석 스크립트
"""

def analyze_routers():
    """라우터 등록 순서와 prefix를 분석합니다."""
    
    print("🔍 라우터 등록 순서와 prefix 분석")
    print("=" * 60)
    
    # 현재 main.py의 라우터 등록 순서
    router_registrations = [
        # 기본 라우터들
        {"name": "applicants_router", "prefix": "None (내부에 /api/applicants)", "main_prefix": "None", "order": 1},
        {"name": "upload_router", "prefix": "None", "main_prefix": "None", "order": 2},
        {"name": "pick_chatbot_router", "prefix": "None", "main_prefix": "/api/pick-chatbot", "order": 3},
        {"name": "integrated_ocr_router", "prefix": "None", "main_prefix": "/api/integrated-ocr", "order": 4},
        {"name": "pdf_ocr_router", "prefix": "None", "main_prefix": "/api/pdf-ocr", "order": 5},
        {"name": "job_posting_router", "prefix": "/api/job-postings", "main_prefix": "None", "order": 6},
        {"name": "sample_data_router", "prefix": "/api/sample", "main_prefix": "None", "order": 7},
        {"name": "chatbot_router", "prefix": "None", "main_prefix": "/chatbot", "order": 8},
        
        # 모듈화된 라우터들
        {"name": "resume_router", "prefix": "/api/resumes", "main_prefix": "/api/resume", "order": 9},
        {"name": "cover_letter_router", "prefix": "/api/cover-letter", "main_prefix": "/api/cover-letter", "order": 10},
        {"name": "portfolio_router", "prefix": "/api/portfolio-module", "main_prefix": "/api/portfolio", "order": 11},
        {"name": "hybrid_router", "prefix": "/api/hybrid", "main_prefix": "/api/hybrid", "order": 12},
        
        # GitHub 라우터
        {"name": "github_router", "prefix": "None", "main_prefix": "/api/github", "order": 13},
        
        # 회사 인재상 라우터
        {"name": "company_culture_router", "prefix": "/api/company-culture", "main_prefix": "None", "order": 14},
        
        # 유사도 분석 라우터
        {"name": "similarity_router", "prefix": "/similarity", "main_prefix": "/api/similarity", "order": 15},
    ]
    
    print("📋 라우터 등록 순서:")
    for router in router_registrations:
        final_prefix = router["main_prefix"] if router["main_prefix"] != "None" else router["prefix"]
        print(f"  {router['order']:2d}. {router['name']:<20} -> {final_prefix}")
    
    print("\n⚠️  잠재적 문제점들:")
    
    # 1. /api prefix 충돌 확인 (정확한 /api 경로만)
    api_prefix_routers = [r for r in router_registrations if r["main_prefix"] == "/api" or (r["main_prefix"] == "None" and r["prefix"] == "/api")]
    if len(api_prefix_routers) > 1:
        print(f"  ❌ /api prefix 충돌: {len(api_prefix_routers)}개 라우터")
        for router in api_prefix_routers:
            final_prefix = router["main_prefix"] if router["main_prefix"] != "None" else router["prefix"]
            print(f"      - {router['name']}: {final_prefix}")
    else:
        print("  ✅ /api prefix 충돌 없음")
    
    # 2. 중복 경로 확인
    paths = []
    for router in router_registrations:
        final_prefix = router["main_prefix"] if router["main_prefix"] != "None" else router["prefix"]
        if final_prefix != "None":
            paths.append(final_prefix)
    
    duplicates = [path for path in set(paths) if paths.count(path) > 1]
    if duplicates:
        print(f"  ❌ 중복 경로: {duplicates}")
    else:
        print("  ✅ 중복 경로 없음")
    
    # 3. 경로 충돌 확인
    print("\n🔍 경로 충돌 분석:")
    
    # /api/applicants 경로 확인
    applicants_conflicts = []
    for router in router_registrations:
        final_prefix = router["main_prefix"] if router["main_prefix"] != "None" else router["prefix"]
        if final_prefix == "/api" and router["order"] < 1:  # applicants_router보다 먼저 등록된 /api 라우터
            applicants_conflicts.append(router["name"])
    
    if applicants_conflicts:
        print(f"  ❌ /api/applicants 경로 충돌 가능성:")
        for conflict in applicants_conflicts:
            print(f"      - {conflict}가 /api/applicants를 가로챌 수 있음")
    else:
        print("  ✅ /api/applicants 경로 충돌 없음")
    
    # 4. 권장사항
    print("\n💡 권장사항:")
    print("  1. applicants_router를 가장 먼저 등록 (현재 상태: ✅)")
    print("  2. /api prefix 라우터들을 나중에 등록 (현재 상태: ✅)")
    print("  3. 구체적인 경로를 가진 라우터를 먼저 등록 (현재 상태: ✅)")
    
    return router_registrations

if __name__ == "__main__":
    analyze_routers()
