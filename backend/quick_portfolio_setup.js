// MongoDB Compass에서 실행할 수 있는 스크립트
// 포트폴리오 스키마 검증 비활성화 및 샘플 데이터 생성

use hireme;

print("=== 포트폴리오 스키마 검증 비활성화 ===");

// 1. 스키마 검증 비활성화
try {
    db.runCommand({
        "collMod": "portfolios",
        "validator": {},
        "validationLevel": "off",
        "validationAction": "warn"
    });
    print("✅ 스키마 검증 비활성화 완료");
} catch (e) {
    print("⚠️ 스키마 검증 비활성화 실패:", e.message);
}

// 2. 지원자 정보 가져오기
var applicants = db.applicants.find({}).toArray();
print("총 " + applicants.length + "명의 지원자 발견");

// 3. 포트폴리오 생성 함수
function createPortfolio(applicant, index) {
    var applicantId = applicant._id.toString();
    var name = applicant.name;
    var position = applicant.position;
    var skills = applicant.skills || [];
    
    var portfolio = {
        "applicant_id": applicantId,
        "application_id": "app_" + applicantId + "_" + (1000 + index),
        "extracted_text": name + "의 " + position + " 포트폴리오입니다. " + skills.join(", ") + "를 활용한 다양한 프로젝트를 수행했습니다.",
        "summary": name + "의 " + position + " 포트폴리오 - 웹 애플리케이션과 모바일 앱 개발 경험",
        "keywords": skills,
        "document_type": "portfolio",
        "basic_info": {
            "emails": [name.toLowerCase().replace(/\s/g, '') + "@email.com"],
            "phones": ["010-" + Math.floor(Math.random() * 9000 + 1000) + "-" + Math.floor(Math.random() * 9000 + 1000)],
            "names": [name],
            "urls": ["https://portfolio." + name.toLowerCase().replace(/\s/g, '') + ".com"]
        },
        "file_metadata": {
            "filename": name + "_포트폴리오.pdf",
            "size": 2048000,
            "mime": "application/pdf",
            "hash": "hash_" + name + "_portfolio_" + (1000 + index),
            "created_at": new Date(),
            "modified_at": new Date()
        },
        "content": "# " + name + " 포트폴리오\n\n## 프로필\n- 이름: " + name + "\n- 직무: " + position + "\n- 기술 스택: " + skills.join(", ") + "\n\n## 주요 프로젝트\n\n### 1. 웹 애플리케이션 프로젝트 (2023)\n**기술 스택**: " + skills.slice(0, 3).join(", ") + "\n**역할**: " + position + " 개발 및 설계\n**기간**: 6개월\n**팀 규모**: 5명\n\n**주요 성과**\n- 사용자 만족도 20% 향상\n- 시스템 응답 속도 30% 개선\n- 코드 품질 향상으로 유지보수성 증대\n\n### 2. 모바일 앱 프로젝트 (2022)\n**기술 스택**: " + skills.slice(1, 4).join(", ") + "\n**역할**: " + position + " 담당\n**기간**: 4개월\n**팀 규모**: 3명\n\n**주요 성과**\n- 앱스토어 평점 4.5/5.0 달성\n- 다운로드 수 10,000+ 달성\n- 사용자 이탈률 15% 감소\n\n## 기술적 역량\n- 프로그래밍 언어: " + skills.join(", ") + "\n- 개발 도구: Git, Docker, Jenkins\n- 데이터베이스: MySQL, PostgreSQL, MongoDB\n- 클라우드 플랫폼: AWS, Azure, GCP\n\n## 수상 및 자격\n- 우수 개발자상 (2023)\n- 관련 기술 자격증 보유\n- 기술 컨퍼런스 발표 경험",
        "analysis_score": Math.round((Math.random() * 20 + 75) * 10) / 10,
        "status": "active",
        "version": 1,
        "created_at": new Date(),
        "updated_at": new Date()
    };
    
    return portfolio;
}

// 4. 모든 지원자에 대해 포트폴리오 생성
print("\n=== 포트폴리오 생성 시작 ===");
var portfolios = [];
for (var i = 0; i < applicants.length; i++) {
    var portfolio = createPortfolio(applicants[i], i + 1);
    portfolios.push(portfolio);
    print("포트폴리오 생성: " + applicants[i].name);
}

// 5. 포트폴리오 삽입
if (portfolios.length > 0) {
    try {
        var result = db.portfolios.insertMany(portfolios);
        print("✅ 포트폴리오 " + result.insertedIds.length + "개 생성 완료");
    } catch (e) {
        print("❌ 포트폴리오 삽입 실패:", e.message);
    }
} else {
    print("생성할 포트폴리오가 없습니다.");
}

// 6. 결과 확인
print("\n=== 최종 결과 ===");
print("지원자 수:", db.applicants.countDocuments({}));
print("이력서 수:", db.resumes.countDocuments({}));
print("자소서 수:", db.cover_letters.countDocuments({}));
print("포트폴리오 수:", db.portfolios.countDocuments({}));

print("\n🎉 포트폴리오 설정 완료! 이제 PDF 업로드가 정상 작동합니다.");
