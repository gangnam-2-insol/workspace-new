// MongoDB Compass에서 실행할 수 있는 스크립트
// 현재 데이터베이스 상태 확인

use hireme;

print("=== 현재 데이터베이스 상태 확인 ===");

// 각 컬렉션별 데이터 수 확인
var applicantsCount = db.applicants.countDocuments({});
var resumesCount = db.resumes.countDocuments({});
var coverLettersCount = db.cover_letters.countDocuments({});
var portfoliosCount = db.portfolios.countDocuments({});

print("📊 데이터 현황:");
print("  지원자: " + applicantsCount + "명");
print("  이력서: " + resumesCount + "개");
print("  자소서: " + coverLettersCount + "개");
print("  포트폴리오: " + portfoliosCount + "개");

// 지원자 목록 확인
print("\n👥 지원자 목록:");
var applicants = db.applicants.find({}, {name: 1, position: 1, email: 1}).toArray();
applicants.forEach(function(applicant, index) {
  var name = applicant.name || "이름 없음";
  var position = applicant.position || "직무 없음";
  var email = applicant.email || "이메일 없음";
  print("  " + (index + 1) + ". " + name + " (" + position + ") - " + email);
});

// 각 지원자별 문서 연결 상태 확인
print("\n📋 지원자별 문서 연결 상태:");
var completedApplicants = 0;

applicants.forEach(function(applicant) {
  var applicantId = applicant._id.toString();
  var name = applicant.name || "이름 없음";
  
  // 각 문서 타입별 개수 확인
  var resumeCount = db.resumes.countDocuments({applicant_id: applicantId});
  var coverLetterCount = db.cover_letters.countDocuments({applicant_id: applicantId});
  var portfolioCount = db.portfolios.countDocuments({applicant_id: applicantId});
  
  print("  " + name + ":");
  print("    - 이력서: " + resumeCount + "개");
  print("    - 자소서: " + coverLetterCount + "개");
  print("    - 포트폴리오: " + portfolioCount + "개");
  
  // 완성도 확인
  if (resumeCount > 0 && coverLetterCount > 0 && portfolioCount > 0) {
    completedApplicants++;
    print("    ✅ 완성 (이력서✓, 자소서✓, 포트폴리오✓)");
  } else {
    var missingDocs = [];
    if (resumeCount === 0) missingDocs.push("이력서");
    if (coverLetterCount === 0) missingDocs.push("자소서");
    if (portfolioCount === 0) missingDocs.push("포트폴리오");
    print("    ❌ 미완성 (누락: " + missingDocs.join(", ") + ")");
  }
});

// 전체 완성도 계산
var completionRate = applicantsCount > 0 ? (completedApplicants / applicantsCount * 100) : 0;
print("\n📈 전체 완성도: " + completionRate.toFixed(1) + "% (" + completedApplicants + "/" + applicantsCount + ")");

if (completionRate === 100) {
  print("🎉 모든 지원자의 문서가 완성되었습니다!");
} else if (completionRate >= 80) {
  print("👍 대부분의 문서가 완성되었습니다.");
} else {
  print("⚠️ 아직 많은 문서가 누락되었습니다.");
}

// 상세 분석
print("\n🔍 상세 분석:");
print("이력서 누락: " + (applicantsCount - resumesCount) + "명");
print("자소서 누락: " + (applicantsCount - coverLettersCount) + "명");
print("포트폴리오 누락: " + (applicantsCount - portfoliosCount) + "명");

print("\n📝 다음 단계:");
if (completionRate < 100) {
  print("1. 누락된 문서들을 생성해야 합니다.");
  if (resumesCount < applicantsCount) {
    print("   - 이력서 생성 필요");
  }
  if (coverLettersCount < applicantsCount) {
    print("   - 자소서 생성 필요");
  }
  if (portfoliosCount < applicantsCount) {
    print("   - 포트폴리오 생성 필요");
  }
} else {
  print("✅ 모든 데이터가 완성되었습니다!");
  print("이제 PDF 업로드 기능을 테스트할 수 있습니다.");
}
