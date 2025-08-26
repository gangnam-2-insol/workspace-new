export function matchKeywords(text, keywords = []) {
  if (!text || !keywords?.length) return false;
  const normalized = String(text).toLowerCase();
  return keywords.some((kw) => normalized.includes(String(kw).toLowerCase()));
}


