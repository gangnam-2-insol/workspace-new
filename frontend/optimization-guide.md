# 프론트엔드 최적화 가이드

## 1. 패키지 업그레이드 및 정리

### 현재 문제점
- `react-scripts@5.0.1` (구버전)
- `axios@0.27.2` (구버전)
- `react-query@3.39.3` (구버전)
- 불필요한 개발 의존성

### 최적화 방안

#### A. 패키지 업그레이드
```bash
# 주요 패키지 업그레이드
npm install axios@^1.7.7
npm install @tanstack/react-query@^5.59.0
npm install react-hook-form@^7.52.1
npm install styled-components@^6.1.13
npm install framer-motion@^11.11.17
```

#### B. 불필요한 패키지 제거
```bash
# 테스트 관련 패키지 (개발 시에만 필요)
npm uninstall @testing-library/jest-dom @testing-library/react @testing-library/user-event
```

## 2. 번들 크기 최적화

### A. 코드 스플리팅
```javascript
// App.js에서 라우트별 지연 로딩
import { lazy, Suspense } from 'react';

const ApplicantManagement = lazy(() => import('./pages/ApplicantManagement'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

// 사용 시
<Suspense fallback={<div>Loading...</div>}>
  <ApplicantManagement />
</Suspense>
```

### B. 이미지 최적화
```javascript
// 이미지 지연 로딩
import { LazyLoadImage } from 'react-lazy-load-image-component';

<LazyLoadImage
  src={imageSrc}
  alt="description"
  effect="blur"
  placeholderSrc="/placeholder.jpg"
/>
```

## 3. 개발 서버 최적화

### A. 환경 변수 설정 (.env.development)
```
FAST_REFRESH=true
GENERATE_SOURCEMAP=false
TSC_COMPILE_ON_ERROR=true
ESLINT_NO_DEV_ERRORS=true
CHOKIDAR_USEPOLLING=false
WATCHPACK_POLLING=false
SKIP_PREFLIGHT_CHECK=true
```

### B. Webpack 설정 최적화
```javascript
// craco.config.js (Create React App Configuration Override)
module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // 개발 모드에서 소스맵 비활성화
      if (process.env.NODE_ENV === 'development') {
        webpackConfig.devtool = false;
      }

      // 캐시 최적화
      webpackConfig.cache = {
        type: 'filesystem',
        buildDependencies: {
          config: [__filename]
        }
      };

      return webpackConfig;
    }
  }
};
```

## 4. 성능 모니터링

### A. 번들 분석
```bash
npm run build:analyze
```

### B. 성능 측정
```javascript
// 성능 측정 유틸리티
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

## 5. 실행 명령어 최적화

### A. 빠른 개발 서버 시작
```bash
npm run start:fast
```

### B. 프로덕션 빌드 최적화
```bash
npm run build:production
```

## 예상 성능 개선 효과
- **번들 크기**: 30-40% 감소
- **초기 로딩 시간**: 50-60% 단축
- **개발 서버 시작 시간**: 40-50% 단축
- **Hot Reload 속도**: 60-70% 향상
