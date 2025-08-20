// MongoDB에서 직접 실행할 수 있는 JavaScript 코드
// mongo shell이나 MongoDB Compass에서 실행

use hireme;

// 지원자 정보 가져오기
var applicants = db.applicants.find({}).toArray();

// 포트폴리오 생성 함수
function createPortfolio(applicant) {
    var applicantId = applicant._id.toString();
    var name = applicant.name;
    var position = applicant.position;
    var skills = applicant.skills || [];
    
    var portfolio = {
        applicant_id: applicantId,
        application_id: "app_" + applicantId + "_" + Math.floor(Math.random() * 9000 + 1000),
        extracted_text: name + "의 " + position + " 포트폴리오입니다. " + skills.join(", ") + "를 활용한 다양한 프로젝트를 수행했습니다.",
        summary: name + "의 " + position + " 포트폴리오 - 웹 애플리케이션과 모바일 앱 개발 경험",
        keywords: skills,
        document_type: "portfolio",
        basic_info: {
            emails: [name.toLowerCase().replace(/\s/g, '') + "@email.com"],
            phones: ["010-" + Math.floor(Math.random() * 9000 + 1000) + "-" + Math.floor(Math.random() * 9000 + 1000)],
            names: [name],
            urls: ["https://portfolio." + name.toLowerCase().replace(/\s/g, '') + ".com"]
        },
        file_metadata: {
            filename: name + "_포트폴리오.pdf",
            size: 2048000,
            mime: "application/pdf",
            hash: "hash_" + name + "_portfolio_" + Math.floor(Math.random() * 9000 + 1000),
            created_at: new Date(),
            modified_at: new Date()
        },
        items: [
            {
                title: name + " - 웹 애플리케이션 프로젝트",
                description: "사용자 친화적인 웹 애플리케이션을 개발하여 기존 시스템의 사용성을 크게 개선한 프로젝트입니다.",
                tech_stack: skills.slice(0, 3),
                role: position + " 개발 및 설계",
                duration: "6개월",
                team_size: 5,
                achievements: [
                    "사용자 만족도 20% 향상",
                    "시스템 응답 속도 30% 개선",
                    "코드 품질 향상으로 유지보수성 증대"
                ],
                artifacts: [
                    {
                        kind: "file",
                        filename: name + "_프로젝트A_스크린샷.png",
                        mime: "image/png",
                        size: 1024000,
                        hash: "hash_" + name + "_projectA_" + Math.floor(Math.random() * 9000 + 1000)
                    }
                ]
            },
            {
                title: name + " - 모바일 앱 프로젝트",
                description: "모바일 환경에 최적화된 애플리케이션을 개발하여 사용자 접근성을 향상시킨 프로젝트입니다.",
                tech_stack: skills.slice(1, 4),
                role: position + " 담당",
                duration: "4개월",
                team_size: 3,
                achievements: [
                    "앱스토어 평점 4.5/5.0 달성",
                    "다운로드 수 10,000+ 달성",
                    "사용자 이탈률 15% 감소"
                ],
                artifacts: [
                    {
                        kind: "url",
                        filename: name + "_모바일앱_데모",
                        url: "https://demo.example.com/" + name.toLowerCase().replace(/\s/g, '') + "_mobile_app"
                    }
                ]
            }
        ],
        analysis_score: Math.random() * 20 + 75, // 75-95 사이의 점수
        status: "active",
        version: 1,
        created_at: new Date(),
        updated_at: new Date()
    };
    
    return portfolio;
}

// 모든 지원자에 대해 포트폴리오 생성
var portfolios = [];
applicants.forEach(function(applicant) {
    var portfolio = createPortfolio(applicant);
    portfolios.push(portfolio);
    print("포트폴리오 생성: " + applicant.name);
});

// 포트폴리오 삽입
if (portfolios.length > 0) {
    var result = db.portfolios.insertMany(portfolios);
    print("포트폴리오 " + result.insertedIds.length + "개 생성 완료");
} else {
    print("생성할 포트폴리오가 없습니다.");
}

// 결과 확인
print("전체 포트폴리오 수: " + db.portfolios.countDocuments({}));
