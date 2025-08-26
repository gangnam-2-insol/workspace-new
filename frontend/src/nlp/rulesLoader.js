export async function loadRules(urlOrStatic) {
  try {
    if (typeof urlOrStatic === 'string') {
      const res = await fetch(urlOrStatic, { headers: { 'Content-Type': 'application/json' } });
      if (!res.ok) throw new Error(`Failed to load rules: ${res.status}`);
      return await res.json();
    }
    // 객체 직접 주입도 허용
    return urlOrStatic;
  } catch (e) {
    console.error('[rulesLoader] 룰셋 로딩 실패:', e);
    return {};
  }
}

export function getRulesForContext(rules, context) {
  if (!rules || !context) return null;
  return rules[context] || null;
}


