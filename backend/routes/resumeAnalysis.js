const express = require('express');
const router = express.Router();

// 예시: 분석 요청 처리
router.post('/analysis', async (req, res) => {
  // 실제 분석 로직은 추후 구현
  res.json({ me+ssage: '분석 결과 저장됨 (예시)' });
});

module.exports = router;