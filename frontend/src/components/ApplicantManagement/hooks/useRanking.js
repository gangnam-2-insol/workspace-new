import { useState, useCallback } from 'react';
import { filterApplicants } from '../utils';

/* 간단 랭킹 로직 (키워드/채용공고 기반) */
export default function useRanking(applicants, { search }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const calculateRanking = useCallback(async () => {
    setLoading(true);
    try {
      const filtered = filterApplicants(applicants, { search, jobs: [], experience: [], status: [], job: '' });
      const ranked = filtered
        .map(a => ({ ...a, score: 50 }))          // 예시: 임의 점수
        .sort((a,b)=>b.score - a.score)
        .map((a,i)=>({ ...a, rank:i+1 }));
      setResults(ranked);
    } catch(e){
      console.error('랭킹 계산 오류:', e);
    } finally {
      setLoading(false);
    }
  }, [applicants, search]);

  return { results, loading, calculateRanking };
}
