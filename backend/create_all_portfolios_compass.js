// MongoDB Compass에서 실행할 수 있는 스크립트
// 10명 지원자의 포트폴리오 데이터 생성

use hireme;

print("=== 10명 지원자 포트폴리오 생성 ===");

// 1. 스키마 검증 비활성화
print("\n1단계: 스키마 검증 비활성화");
try {
    db.runCommand({
        "collMod": "portfolios",
        "validator": {},
        "validationLevel": "off",
        "validationAction": "warn"
    });
    print("✅ 스키마 검증 비활성화 완료");
} catch (e) {
    print("⚠️ 스키마 검증 비활성화 실패: " + e.message);
}

// 2. 지원자 정보 가져오기
print("\n2단계: 지원자 정보 확인");
var applicants = db.applicants.find({}).toArray();
print("총 " + applicants.length + "명의 지원자 발견");

if (applicants.length === 0) {
    print("❌ 지원자가 없습니다.");
    exit();
}

// 3. 포트폴리오 생성 함수
function createPortfolio(applicant, index) {
    var applicantId = applicant._id.toString();
    var name = applicant.name;
    var position = applicant.position;
    var skills = applicant.skills || [];
    
    // 포지션별 맞춤형 포트폴리오 내용 생성
    var portfolioContent = generatePortfolioContent(name, position, skills);
    
    var portfolio = {
        "applicant_id": applicantId,
        "application_id": "app_" + applicantId + "_" + (1000 + index),
        "extracted_text": name + "의 " + position + " 포트폴리오입니다. " + skills.join(", ") + "를 활용한 다양한 프로젝트를 수행했습니다.",
        "summary": name + "의 " + position + " 포트폴리오 - " + getPositionDescription(position),
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
        "content": portfolioContent,
        "analysis_score": Math.round((Math.random() * 20 + 75) * 10) / 10,
        "status": "active",
        "version": 1,
        "created_at": new Date(),
        "updated_at": new Date()
    };
    
    return portfolio;
}

// 포지션별 설명 생성
function getPositionDescription(position) {
    var descriptions = {
        "프론트엔드": "웹 애플리케이션과 모바일 앱 개발 경험",
        "백엔드": "API 개발과 데이터베이스 설계 경험",
        "풀스택": "전체 개발 스택을 활용한 프로젝트 경험",
        "데이터": "데이터 분석과 머신러닝 프로젝트 경험",
        "DevOps": "인프라 구축과 CI/CD 파이프라인 경험",
        "모바일": "iOS/Android 앱 개발 경험",
        "AI": "인공지능과 딥러닝 프로젝트 경험"
    };
    return descriptions[position] || "다양한 프로젝트 개발 경험";
}

// 포트폴리오 내용 생성
function generatePortfolioContent(name, position, skills) {
    var content = "# " + name + " 포트폴리오\n\n";
    content += "## 프로필\n";
    content += "- 이름: " + name + "\n";
    content += "- 직무: " + position + "\n";
    content += "- 기술 스택: " + skills.join(", ") + "\n\n";
    
    content += "## 주요 프로젝트\n\n";
    
    // 프로젝트 1
    content += "### 1. " + getProjectTitle(position, 1) + " (2023)\n";
    content += "**기술 스택**: " + skills.slice(0, 3).join(", ") + "\n";
    content += "**역할**: " + position + " 개발 및 설계\n";
    content += "**기간**: 6개월\n";
    content += "**팀 규모**: 5명\n\n";
    content += "**프로젝트 개요**\n";
    content += getProjectDescription(position, 1) + "\n\n";
    content += "**주요 성과**\n";
    content += "- 사용자 만족도 20% 향상\n";
    content += "- 시스템 응답 속도 30% 개선\n";
    content += "- 코드 품질 향상으로 유지보수성 증대\n\n";
    
    // 프로젝트 2
    content += "### 2. " + getProjectTitle(position, 2) + " (2022)\n";
    content += "**기술 스택**: " + skills.slice(1, 4).join(", ") + "\n";
    content += "**역할**: " + position + " 담당\n";
    content += "**기간**: 4개월\n";
    content += "**팀 규모**: 3명\n\n";
    content += "**프로젝트 개요**\n";
    content += getProjectDescription(position, 2) + "\n\n";
    content += "**주요 성과**\n";
    content += "- 앱스토어 평점 4.5/5.0 달성\n";
    content += "- 다운로드 수 10,000+ 달성\n";
    content += "- 사용자 이탈률 15% 감소\n\n";
    
    content += "## 기술적 역량\n";
    content += "- 프로그래밍 언어: " + skills.join(", ") + "\n";
    content += "- 개발 도구: Git, Docker, Jenkins\n";
    content += "- 데이터베이스: MySQL, PostgreSQL, MongoDB\n";
    content += "- 클라우드 플랫폼: AWS, Azure, GCP\n\n";
    
    content += "## 수상 및 자격\n";
    content += "- 우수 개발자상 (2023)\n";
    content += "- 관련 기술 자격증 보유\n";
    content += "- 기술 컨퍼런스 발표 경험\n";
    
    return content;
}

// 포지션별 프로젝트 제목 생성
function getProjectTitle(position, projectNum) {
    var titles = {
        "프론트엔드": projectNum === 1 ? "반응형 웹 애플리케이션" : "모바일 최적화 웹앱",
        "백엔드": projectNum === 1 ? "REST API 시스템" : "마이크로서비스 아키텍처",
        "풀스택": projectNum === 1 ? "전체 스택 웹 플랫폼" : "실시간 협업 도구",
        "데이터": projectNum === 1 ? "데이터 분석 대시보드" : "머신러닝 예측 모델",
        "DevOps": projectNum === 1 ? "CI/CD 파이프라인 구축" : "클라우드 인프라 자동화",
        "모바일": projectNum === 1 ? "크로스 플랫폼 앱" : "네이티브 모바일 앱",
        "AI": projectNum === 1 ? "AI 챗봇 시스템" : "이미지 인식 서비스"
    };
    return titles[position] || "웹 애플리케이션 프로젝트";
}

// 포지션별 프로젝트 설명 생성
function getProjectDescription(position, projectNum) {
    var descriptions = {
        "프론트엔드": projectNum === 1 ? 
            "사용자 친화적인 반응형 웹 애플리케이션을 개발하여 기존 시스템의 사용성을 크게 개선했습니다." :
            "모바일 환경에 최적화된 웹 애플리케이션을 개발하여 사용자 접근성을 향상시켰습니다.",
        "백엔드": projectNum === 1 ?
            "안정적이고 확장 가능한 REST API 시스템을 구축하여 다양한 클라이언트의 요청을 효율적으로 처리했습니다." :
            "마이크로서비스 아키텍처를 도입하여 시스템의 유연성과 확장성을 크게 향상시켰습니다.",
        "풀스택": projectNum === 1 ?
            "프론트엔드부터 백엔드까지 전체 스택을 활용하여 완전한 웹 플랫폼을 구축했습니다." :
            "실시간 협업이 가능한 웹 도구를 개발하여 팀 생산성을 향상시켰습니다.",
        "데이터": projectNum === 1 ?
            "대용량 데이터를 분석하고 시각화하는 대시보드를 구축하여 비즈니스 인사이트를 제공했습니다." :
            "머신러닝 알고리즘을 활용하여 예측 모델을 개발하고 정확도를 향상시켰습니다.",
        "DevOps": projectNum === 1 ?
            "자동화된 CI/CD 파이프라인을 구축하여 배포 프로세스를 효율화했습니다." :
            "클라우드 인프라를 자동화하여 운영 효율성을 크게 향상시켰습니다.",
        "모바일": projectNum === 1 ?
            "iOS와 Android를 모두 지원하는 크로스 플랫폼 모바일 앱을 개발했습니다." :
            "네이티브 성능을 활용한 고성능 모바일 애플리케이션을 개발했습니다.",
        "AI": projectNum === 1 ?
            "자연어 처리를 활용한 AI 챗봇 시스템을 개발하여 고객 서비스를 개선했습니다." :
            "컴퓨터 비전 기술을 활용한 이미지 인식 서비스를 구축했습니다."
    };
    return descriptions[position] || "사용자 친화적인 웹 애플리케이션을 개발하여 기존 시스템의 사용성을 크게 개선했습니다.";
}

// 4. 모든 지원자에 대해 포트폴리오 생성
print("\n3단계: 포트폴리오 생성 시작");
var portfolios = [];

for (var i = 0; i < applicants.length; i++) {
    var portfolio = createPortfolio(applicants[i], i + 1);
    portfolios.push(portfolio);
    print("포트폴리오 생성: " + applicants[i].name + " (" + applicants[i].position + ")");
}

// 5. 포트폴리오 삽입
print("\n4단계: 포트폴리오 데이터베이스 저장");
if (portfolios.length > 0) {
    try {
        var result = db.portfolios.insertMany(portfolios);
        print("✅ 포트폴리오 " + result.insertedIds.length + "개 생성 완료");
    } catch (e) {
        print("❌ 포트폴리오 삽입 실패: " + e.message);
    }
} else {
    print("생성할 포트폴리오가 없습니다.");
}

// 6. 결과 확인
print("\n5단계: 최종 결과 확인");
print("지원자 수:", db.applicants.countDocuments({}));
print("이력서 수:", db.resumes.countDocuments({}));
print("자소서 수:", db.cover_letters.countDocuments({}));
print("포트폴리오 수:", db.portfolios.countDocuments({}));

// 완성도 확인
var completedApplicants = 0;
applicants.forEach(function(applicant) {
    var applicantId = applicant._id.toString();
    var resumeCount = db.resumes.countDocuments({applicant_id: applicantId});
    var coverLetterCount = db.cover_letters.countDocuments({applicant_id: applicantId});
    var portfolioCount = db.portfolios.countDocuments({applicant_id: applicantId});
    
    if (resumeCount > 0 && coverLetterCount > 0 && portfolioCount > 0) {
        completedApplicants++;
    }
});

var completionRate = (completedApplicants / applicants.length * 100);
print("\n📈 전체 완성도: " + completionRate.toFixed(1) + "% (" + completedApplicants + "/" + applicants.length + ")");

if (completionRate === 100) {
    print("🎉 모든 지원자의 문서가 완성되었습니다!");
} else {
    print("⚠️ 아직 일부 문서가 누락되었습니다.");
}

print("\n🎉 포트폴리오 생성 작업 완료!");
