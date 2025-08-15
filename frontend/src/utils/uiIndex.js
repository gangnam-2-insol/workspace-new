// UI 인덱스(페이지 상호작용 요소 맵) 생성/캐시 유틸

function pick(obj, keys) {
  const out = {};
  keys.forEach(k => {
    const v = obj.getAttribute ? obj.getAttribute(k) : undefined;
    if (v != null) out[k] = String(v);
  });
  return out;
}

function isVisible(el) {
  try {
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    if (style.visibility === 'hidden' || style.display === 'none') return false;
    if (rect.width === 0 || rect.height === 0) return false;
    return true;
  } catch (_) {
    return false;
  }
}

function normalizeText(text) {
  return String(text || '')
    .replace(/\s+/g, ' ')
    .trim();
}

// --- 유사어/맥락 인식 보강 ---
const SYNONYM_GROUPS = [
  ['지원', '신청', 'apply', 'application', 'apply now'],
  ['제출', '등록', 'submit', 'send'],
  ['상세', '상세보기', '자세히', '보기', '열기', 'detail', 'details', 'view', 'open'],
  ['검색', '찾기', 'search', 'find', 'lookup'],
  ['삭제', '제거', '지우기', '지워', '삭제하기', 'delete', 'remove', 'trash'],
  ['확인', 'ok', '확정', 'confirm', 'yes'],
  ['취소', 'cancel', '닫기', 'close', 'back'],
  // PDF/OCR 도메인 강화
  ['pdf', 'pdfocr', 'ocr', '스캔', '스캐너', '문서인식', '문자인식', '문서', '텍스트추출', '추출', '인식'],
  ['업로드', 'upload', '파일선택', 'file', 'choose file', '파일 올리기']
];

const SYNONYM_INDEX = (() => {
  const map = new Map();
  for (const group of SYNONYM_GROUPS) {
    const lowerGroup = group.map(w => w.toLowerCase());
    for (const w of lowerGroup) {
      map.set(w, new Set(lowerGroup));
    }
  }
  return map;
})();

function normalizeWord(word) {
  let w = String(word || '').normalize('NFC').toLowerCase();
  w = w.replace(/[\p{P}\p{S}]+/gu, ''); // 문장부호 제거
  // 흔한 종결/요청 표현 제거
  w = w.replace(/(해주세요|해줘|해주|해요|하라|하기|하도록|해|하여|클릭|click)/g, '');
  // 조사/어미(간단) 제거: 을 를 이 가 은 는 의 에 에서 과 와 로 으로 도 만 까지 부터 등
  w = w.replace(/(을|를|이|가|은|는|의|에|에서|과|와|로|으로|도|만|까지|부터)$/g, '');
  return w.trim();
}

function tokenize(text) {
  const t = normalizeText(String(text || '')).normalize('NFC').toLowerCase();
  return t.split(/[\s/|,.;:()\[\]{}<>]+/).map(normalizeWord).filter(Boolean);
}

function expandWithSynonyms(terms) {
  const out = new Set();
  for (const t of terms) {
    out.add(t);
    const syn = SYNONYM_INDEX.get(t);
    if (syn) for (const s of syn) out.add(s);
  }
  return out;
}

function levenshtein(a, b) {
  const s = String(a || '');
  const t = String(b || '');
  const n = s.length, m = t.length;
  if (!n) return m; if (!m) return n;
  const dp = new Array(m + 1);
  for (let j = 0; j <= m; j++) dp[j] = j;
  for (let i = 1; i <= n; i++) {
    let prev = i - 1; // dp[i-1][j-1]
    dp[0] = i;
    for (let j = 1; j <= m; j++) {
      const tmp = dp[j];
      const cost = s[i - 1] === t[j - 1] ? 0 : 1;
      dp[j] = Math.min(
        dp[j] + 1,       // deletion
        dp[j - 1] + 1,   // insertion
        prev + cost      // substitution
      );
      prev = tmp;
    }
  }
  return dp[m];
}

function tokenSimilarity(a, b) {
  const la = a.length || 1;
  const d = levenshtein(a, b);
  return 1 - d / Math.max(la, b.length || 1);
}

function extractReadableText(el) {
  try {
    const aria = el.getAttribute && (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby'));
    if (aria) return normalizeText(aria);
    const text = el.innerText || el.textContent || '';
    return normalizeText(text);
  } catch (_) {
    return '';
  }
}

function inferRole(el) {
  const explicit = el.getAttribute && el.getAttribute('role');
  if (explicit) return explicit;
  const tag = (el.tagName || '').toUpperCase();
  // 접근성/상호작용 힌트로 버튼 추정
  try {
    const hasOnClick = !!(el.getAttribute && el.getAttribute('onclick'));
    const tabIndex = el.getAttribute && el.getAttribute('tabindex');
    const className = (el.className || '').toString().toLowerCase();
    if (hasOnClick || tabIndex === '0' || /btn|button|clickable/.test(className)) {
      return 'button';
    }
  } catch (_) {}
  if (tag === 'A') return 'link';
  if (tag === 'BUTTON') return 'button';
  if (tag === 'INPUT') return 'input';
  if (tag === 'SELECT') return 'select';
  if (tag === 'TEXTAREA') return 'textarea';
  return 'other';
}

function stableHash(str) {
  // 간단 FNV-1a 해시
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(36);
}

export function normalizeUrlKey(url) {
  try {
    const u = typeof url === 'string' ? new URL(url, window.location.origin) : url;
    const keep = new Set(['lang', 'page']);
    const filtered = new URL(u.toString());
    Array.from(filtered.searchParams.keys()).forEach(k => { if (!keep.has(k)) filtered.searchParams.delete(k); });
    filtered.hash = '';
    return `${filtered.origin}${filtered.pathname}${filtered.search}`;
  } catch (_) {
    return String(url || window.location.href);
  }
}

export function computeLayoutFingerprint(doc = document) {
  const items = Array.from(doc.querySelectorAll('a,button,input,select,textarea,[role]'))
    .filter(isVisible)
    .slice(0, 500)
    .map(el => `${el.tagName}:${inferRole(el)}:${normalizeText(extractReadableText(el))}`);
  return stableHash(items.join('|'));
}

function buildRobustSelector(el) {
  // 1) data-testid/aria-label/id
  const dt = el.getAttribute && el.getAttribute('data-testid');
  if (dt) return `[data-testid="${CSS.escape(dt)}"]`;
  const aria = el.getAttribute && el.getAttribute('aria-label');
  if (aria) return `${el.tagName.toLowerCase()}[aria-label="${CSS.escape(aria)}"]`;
  const id = el.id;
  if (id) return `#${CSS.escape(id)}`;
  // 2) name + type
  const name = el.getAttribute && el.getAttribute('name');
  const type = el.getAttribute && el.getAttribute('type');
  if (name && type) return `${el.tagName.toLowerCase()}[name="${CSS.escape(name)}"][type="${CSS.escape(type)}"]`;
  if (name) return `${el.tagName.toLowerCase()}[name="${CSS.escape(name)}"]`;
  // 3) 경로 기반 nth-of-type
  const parts = [];
  let node = el;
  while (node && node.nodeType === 1 && node !== document.body) {
    const tag = node.tagName.toLowerCase();
    const parent = node.parentElement;
    if (!parent) break;
    const siblings = Array.from(parent.children).filter(c => c.tagName.toLowerCase() === tag);
    const idx = siblings.indexOf(node) + 1;
    parts.unshift(`${tag}:nth-of-type(${idx})`);
    node = parent;
  }
  return parts.length ? parts.join('>') : el.tagName.toLowerCase();
}

export function getUIMap(doc = document, includeHidden = false) {
  const urlKey = normalizeUrlKey(doc.location ? doc.location.href : window.location.href);
  const elements = [];
  const nodes = Array.from(doc.querySelectorAll(
    'a,button,input,select,textarea,[role=button],[role=link],[tabindex="0"],[onclick],label,span[role=button]'
  ));
  for (const el of nodes) {
    if (!includeHidden && !isVisible(el)) continue;
    const role = inferRole(el);
    const text = extractReadableText(el);
    const rect = el.getBoundingClientRect();
    elements.push({
      tag: el.tagName,
      role,
      text,
      selector: buildRobustSelector(el),
      attributes: pick(el, ['data-testid','aria-label','name','type','placeholder']),
      bounds: { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
      visible: true,
      stableId: el.dataset ? el.dataset.testid : undefined,
      fingerprintPart: `${el.tagName}:${role}:${normalizeText(text)}`,
      weight: role === 'button' ? 1.0 : 0.6
    });
  }
  return {
    urlKey,
    layoutFingerprint: computeLayoutFingerprint(doc),
    capturedAt: Date.now(),
    elements
  };
}

const memory = new Map();

export function highlightOnce(selector, duration = 800) {
  try {
    const el = typeof selector === 'string' ? document.querySelector(selector) : selector;
    if (!el) return;
    const prev = el.style.outline;
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.style.outline = '2px solid #667eea';
    setTimeout(() => { el.style.outline = prev; }, duration);
  } catch(_) {}
}

export function cacheUI(page) {
  memory.set(page.urlKey, page);
  try {
    sessionStorage.setItem(`ui:${page.urlKey}`, JSON.stringify(page));
  } catch (_) {}
}

export function getCachedUI(urlKey) {
  const m = memory.get(urlKey);
  if (m) return m;
  try {
    const s = sessionStorage.getItem(`ui:${urlKey}`);
    if (!s) return null;
    const parsed = JSON.parse(s);
    memory.set(urlKey, parsed);
    return parsed;
  } catch (_) {
    return null;
  }
}

export function diagnoseRefresh(existing, doc = document, ttlMs = 10 * 60 * 1000) {
  if (!existing) return { should: true, reason: 'miss' };
  try {
    if (Date.now() - (existing.capturedAt || 0) > ttlMs) return { should: true, reason: 'ttl' };
    const fp = computeLayoutFingerprint(doc);
    if (existing.layoutFingerprint !== fp) return { should: true, reason: 'fingerprint' };
    return { should: false, reason: 'none' };
  } catch (_) {
    return { should: false, reason: 'error' };
  }
}

export function shouldRefresh(existing, doc = document, ttlMs = 10 * 60 * 1000) {
  return diagnoseRefresh(existing, doc, ttlMs).should;
}

export function resolveByQuery(query, kind, page) {
  // 매우 단순한 텍스트/역할 매칭
  if (!page) return null;
  const q = normalizeText(String(query || '')).toLowerCase();
  const roleSet = new Set(
    kind === 'click' ? ['button','link'] :
    kind === 'type' ? ['input','textarea','select'] : ['button','link','input','textarea','select']
  );
  const queryTerms = expandWithSynonyms(tokenize(q));
  let best = null;
  let bestScore = 0;
  for (const e of page.elements) {
    if (!roleSet.has(e.role)) continue;
    const bagText = [e.text, e.attributes?.['aria-label'], e.attributes?.['name'], e.attributes?.['placeholder']]
      .filter(Boolean)
      .map(v => String(v).toLowerCase())
      .join(' ');
    const elemTerms = expandWithSynonyms(tokenize(bagText));
    // 점수: (정확 포함/토큰 유사도/동의어 일치) 혼합
    let score = 0;
    // 1) 문장 포함 가산
    if (bagText.includes(q) && q.length >= 2) score += 0.6;
    // 2) 토큰 기반 유사도 평균 상위치
    let simSum = 0; let simCnt = 0;
    for (const qt of queryTerms) {
      let bestTokSim = 0;
      for (const et of elemTerms) {
        if (qt === et) { bestTokSim = 1; break; }
        const s = tokenSimilarity(qt, et);
        if (s > bestTokSim) bestTokSim = s;
      }
      simSum += bestTokSim; simCnt += 1;
    }
    const avgSim = simCnt ? simSum / simCnt : 0;
    score += avgSim * 0.7;
    // 3) 역할 가산
    if (e.role === 'button') score += 0.1;
    if (score > bestScore) { bestScore = score; best = e; }
  }
  if (bestScore >= 0.6) return best;
  // 보강: 이름 등 앵커 텍스트 근처의 상세/보기 버튼 추정
  if (kind === 'click') {
    try {
      const fallback = findClosestActionNearText(query);
      if (fallback) return { tag: 'BUTTON', role: 'button', text: 'fallback', selector: fallback, attributes: {}, bounds: {x:0,y:0,w:0,h:0}, visible: true, fingerprintPart: '', weight: 1.0 };
    } catch(_) {}
  }
  return null;
}

// 근접 버튼(상세/보기/열기 등) 탐색: 주어진 텍스트 노드 근처에서 버튼/링크 추정
function findClosestActionNearText(rawQuery) {
  const q = normalizeText(String(rawQuery || ''));
  if (!q) return null;
  const words = q.split(' ');
  const name = words[0];
  if (!name) return null;
  // 이름 텍스트를 포함하는 요소 찾기
  const candidates = Array.from(document.querySelectorAll('body *'))
    .filter(n => n.childElementCount === 0 && /\S/.test(n.textContent || ''))
    .filter(n => (n.textContent || '').includes(name))
    .slice(0, 50);
  const actionRegex = /(상세|상세보기|자세히|보기|열기|삭제|제거|지우기|지워|삭제하기|detail|details|view|open|delete|remove|trash)/i;
  let bestSel = null;
  let bestDist = Infinity;
  for (const node of candidates) {
    const rect = node.getBoundingClientRect();
    // 주변 3단계 부모에서 버튼/링크 탐색
    let parent = node.parentElement;
    for (let d = 0; d < 3 && parent; d++) {
      const actions = parent.querySelectorAll('a,button,[role=button]');
      for (const a of actions) {
        const text = normalizeText(extractReadableText(a));
        if (!actionRegex.test(text)) continue;
        const r2 = a.getBoundingClientRect();
        const dx = (r2.x + r2.width / 2) - (rect.x + rect.width / 2);
        const dy = (r2.y + r2.height / 2) - (rect.y + rect.height / 2);
        const dist = Math.hypot(dx, dy);
        if (dist < bestDist) {
          bestDist = dist;
          bestSel = buildRobustSelector(a);
        }
      }
      parent = parent.parentElement;
    }
  }
  return bestSel;
}

export async function ensureUiIndexIfNeeded(href = window.location.href, verbose = false, options = {}) {
  const { forceRebuild = false, includeHidden = false } = options || {};
  const key = normalizeUrlKey(href);
  const cached = getCachedUI(key);
  const diag = diagnoseRefresh(cached, document);
  if (verbose) {
    console.debug('[UIIndex] urlKey:', key, 'cache?', !!cached, 'shouldRefresh?', diag.should, 'reason:', diag.reason);
  }
  if (forceRebuild || !cached || diag.should) {
    const page = getUIMap(document, includeHidden === true);
    cacheUI(page);
    if (verbose) {
      console.debug('[UIIndex] built index', { urlKey: page.urlKey, capturedAt: page.capturedAt, elements: page.elements.length });
    }
    return page;
  }
  if (verbose) {
    console.debug('[UIIndex] reused cached index', { urlKey: cached.urlKey, capturedAt: cached.capturedAt, elements: cached.elements.length });
  }
  return cached;
}

export async function rebuildUiIndex(href = window.location.href, verbose = false, options = {}) {
  const opts = { ...(options || {}), forceRebuild: true };
  return ensureUiIndexIfNeeded(href, verbose, opts);
}

export default {
  normalizeUrlKey,
  computeLayoutFingerprint,
  getUIMap,
  cacheUI,
  getCachedUI,
  shouldRefresh,
  diagnoseRefresh,
  resolveByQuery,
  ensureUiIndexIfNeeded,
  rebuildUiIndex
};


