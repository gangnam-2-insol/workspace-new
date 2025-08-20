# 포트폴리오 스키마 검증 비활성화 가이드

## 문제 상황
현재 포트폴리오 컬렉션에 복잡한 JSON 스키마 검증이 설정되어 있어서 PDF 업로드 시 포트폴리오 저장이 실패하고 있습니다.

## 해결 방법

### 1. MongoDB Compass 사용 (추천)

1. MongoDB Compass 실행
2. `localhost:27017` 연결
3. `hireme` 데이터베이스 선택
4. MongoDB Shell 탭 클릭
5. 다음 명령어 실행:

```javascript
// 포트폴리오 컬렉션의 스키마 검증 비활성화
db.runCommand({
  "collMod": "portfolios",
  "validator": {},
  "validationLevel": "off",
  "validationAction": "warn"
})
```

### 2. 터미널에서 mongosh 사용

```bash
mongosh
use hireme
db.runCommand({
  "collMod": "portfolios",
  "validator": {},
  "validationLevel": "off",
  "validationAction": "warn"
})
```

### 3. 확인 명령어

```javascript
// 스키마 검증이 비활성화되었는지 확인
db.getCollectionInfos({name: "portfolios"})
```

## 결과
스키마 검증이 비활성화되면:
- ✅ PDF 업로드 시 포트폴리오 저장 가능
- ✅ 기존 이력서/자소서 기능 정상 작동
- ✅ 프론트엔드에서 포트폴리오 표시 가능

## 주의사항
- 스키마 검증을 비활성화하면 데이터 무결성 검증이 약해집니다
- 나중에 필요시 다시 스키마 검증을 활성화할 수 있습니다
