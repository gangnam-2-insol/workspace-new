import React, { useState } from 'react';

const TestGithubSummary = () => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    if (!username.trim()) {
      setError('GitHub 아이디 또는 GitHub URL을 입력하세요');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/github/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim() })
      });
      const data = await res.json();
      if (!res.ok) {
        // 백엔드에서 detail만 내려올 수도 있으니 보강
        const msg = data?.message || data?.detail || '요약 요청 실패';
        throw new Error(msg);
      }
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 720, margin: '0 auto' }}>
      <h2>GitHub 요약 테스트</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input
          placeholder="GitHub 아이디 또는 GitHub URL (예: https://github.com/test/test_project)"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ flex: 1, padding: 10, borderRadius: 8, border: '1px solid #ddd' }}
        />
        <button type="submit" disabled={loading} style={{ padding: '10px 16px' }}>
          {loading ? '요약 중...' : '요약하기'}
        </button>
      </form>

      {error && (
        <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>
      )}

      {result && (
        <div style={{ background: '#fff', border: '1px solid #eee', borderRadius: 8, padding: 16 }}>
          <div style={{ marginBottom: 8 }}>
            <strong>프로필:</strong> <a href={result.profileUrl} target="_blank" rel="noreferrer">{result.profileUrl}</a>
          </div>
          <div style={{ marginBottom: 8 }}>
            <strong>소스:</strong> {result.source}
          </div>
          <div>
            <strong>분석 결과:</strong>
            {(() => {
              try {
                const summaries = JSON.parse(result.summary);
                return (
                  <div>
                    {Array.isArray(summaries) ? summaries.map((summary, index) => (
                      <div key={index} style={{ marginBottom: 16, padding: 12, border: '1px solid #ddd', borderRadius: 4 }}>
                        {summary.name && <h4 style={{ margin: '0 0 8px 0' }}>{summary.name}</h4>}
                        <div style={{ marginBottom: 4 }}>
                          <strong>주제:</strong> {summary.주제}
                        </div>
                        <div style={{ marginBottom: 4 }}>
                          <strong>기술 스택:</strong> {Array.isArray(summary['기술 스택']) ? summary['기술 스택'].join(', ') : summary['기술 스택']}
                        </div>
                        <div style={{ marginBottom: 4 }}>
                          <strong>주요 기능:</strong> {Array.isArray(summary['주요 기능']) ? summary['주요 기능'].join(', ') : summary['주요 기능']}
                        </div>
                        <div>
                          <strong>레포 주소:</strong> <a href={summary['레포 주소']} target="_blank" rel="noreferrer">{summary['레포 주소']}</a>
                        </div>
                      </div>
                    )) : (
                      <div style={{ padding: 12, border: '1px solid #ddd', borderRadius: 4 }}>
                        <div style={{ marginBottom: 4 }}>
                          <strong>주제:</strong> {summaries.주제}
                        </div>
                        <div style={{ marginBottom: 4 }}>
                          <strong>기술 스택:</strong> {Array.isArray(summaries['기술 스택']) ? summaries['기술 스택'].join(', ') : summaries['기술 스택']}
                        </div>
                        <div style={{ marginBottom: 4 }}>
                          <strong>주요 기능:</strong> {Array.isArray(summaries['주요 기능']) ? summaries['주요 기능'].join(', ') : summaries['주요 기능']}
                        </div>
                        <div>
                          <strong>레포 주소:</strong> <a href={summaries['레포 주소']} target="_blank" rel="noreferrer">{summaries['레포 주소']}</a>
                        </div>
                      </div>
                    )}
                  </div>
                );
              } catch (e) {
                // JSON 파싱 실패 시 기존 텍스트 형태로 표시
                return <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{result.summary}</pre>;
              }
            })()}
          </div>
        </div>
      )}
    </div>
  );
};

export default TestGithubSummary;


