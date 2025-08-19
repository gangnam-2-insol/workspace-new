// MongoDB Compass에서 실행할 수 있는 스크립트
// 새로운 포트폴리오 스키마 적용

use hireme;

print("=== 새로운 포트폴리오 스키마 적용 ===");

// 새로운 스키마 정의
var newSchema = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["applicant_id", "application_id", "extracted_text", "summary", "document_type", "status"],
    "properties": {
      "applicant_id": {
        "bsonType": "string",
        "description": "지원자 ID (필수)"
      },
      "application_id": {
        "bsonType": "string",
        "description": "지원서 ID (필수)"
      },
      "extracted_text": {
        "bsonType": "string",
        "description": "OCR로 추출된 텍스트 (필수)"
      },
      "summary": {
        "bsonType": "string",
        "description": "포트폴리오 요약 (필수)"
      },
      "keywords": {
        "bsonType": "array",
        "items": {
          "bsonType": "string"
        },
        "description": "키워드 목록 (선택)"
      },
      "document_type": {
        "bsonType": "string",
        "enum": ["portfolio"],
        "description": "문서 타입 (필수)"
      },
      "basic_info": {
        "bsonType": "object",
        "properties": {
          "emails": {
            "bsonType": "array",
            "items": {
              "bsonType": "string"
            }
          },
          "phones": {
            "bsonType": "array",
            "items": {
              "bsonType": "string"
            }
          },
          "names": {
            "bsonType": "array",
            "items": {
              "bsonType": "string"
            }
          },
          "urls": {
            "bsonType": "array",
            "items": {
              "bsonType": "string"
            }
          }
        }
      },
      "file_metadata": {
        "bsonType": "object",
        "properties": {
          "filename": {
            "bsonType": "string"
          },
          "size": {
            "bsonType": "int"
          },
          "mime": {
            "bsonType": "string"
          },
          "hash": {
            "bsonType": "string"
          },
          "created_at": {
            "bsonType": "date"
          },
          "modified_at": {
            "bsonType": "date"
          }
        }
      },
      "content": {
        "bsonType": "string",
        "description": "포트폴리오 내용 (선택)"
      },
      "analysis_score": {
        "bsonType": "double",
        "minimum": 0,
        "maximum": 100,
        "description": "분석 점수 (0-100, 선택)"
      },
      "status": {
        "bsonType": "string",
        "enum": ["active", "inactive", "archived"],
        "description": "포트폴리오 상태 (필수)"
      },
      "version": {
        "bsonType": "int",
        "minimum": 1,
        "description": "버전 번호 (선택)"
      },
      "created_at": {
        "bsonType": "date",
        "description": "생성일시 (선택)"
      },
      "updated_at": {
        "bsonType": "date",
        "description": "수정일시 (선택)"
      }
    }
  }
};

// 현재 데이터 검증
print("\n=== 현재 데이터 검증 ===");
var portfolios = db.portfolios.find({}).toArray();
print("총 " + portfolios.length + "개의 포트폴리오 데이터 검증 중...");

var validCount = 0;
var invalidCount = 0;

portfolios.forEach(function(portfolio, index) {
  var requiredFields = ["applicant_id", "application_id", "extracted_text", "summary", "document_type", "status"];
  var missingFields = requiredFields.filter(function(field) {
    return !portfolio.hasOwnProperty(field) || portfolio[field] === null || portfolio[field] === undefined;
  });
  
  if (missingFields.length > 0) {
    print("❌ 포트폴리오 " + (index + 1) + ": 필수 필드 누락 - " + missingFields.join(", "));
    invalidCount++;
  } else {
    print("✅ 포트폴리오 " + (index + 1) + ": 검증 통과");
    validCount++;
  }
});

print("\n검증 결과: " + validCount + "개 통과, " + invalidCount + "개 실패");

// 새로운 스키마 적용
if (invalidCount === 0) {
  print("\n=== 새로운 스키마 적용 ===");
  try {
    var result = db.runCommand({
      "collMod": "portfolios",
      "validator": newSchema,
      "validationLevel": "moderate",
      "validationAction": "error"
    });
    print("✅ 새로운 스키마 적용 완료");
    print("결과: " + JSON.stringify(result, null, 2));
    
    // 확인
    var collectionInfo = db.getCollectionInfos({name: "portfolios"});
    if (collectionInfo.length > 0) {
      var options = collectionInfo[0].options || {};
      print("검증 레벨: " + (options.validationLevel || "N/A"));
      print("검증 액션: " + (options.validationAction || "N/A"));
    }
    
  } catch (e) {
    print("❌ 스키마 적용 실패: " + e.message);
  }
} else {
  print("\n⚠️ 일부 데이터가 검증을 통과하지 못했습니다.");
  print("데이터를 수정한 후 다시 시도해주세요.");
}

print("\n🎉 스키마 적용 작업 완료!");
