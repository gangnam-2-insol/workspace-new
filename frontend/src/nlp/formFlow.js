import recruitForm from '../config/forms/recruit_form.json';

const FORM_CONFIGS = {
  recruit_form: recruitForm
  // 다른 페이지는 동일 규격의 JSON 추가로 확장
};

export function getFormConfig(pageId) {
  return FORM_CONFIGS[pageId] || null;
}

export function getInitialField(pageId) {
  const cfg = getFormConfig(pageId);
  return cfg?.sequence?.[0] || null;
}

export function getNextField(pageId, currentKey) {
  const cfg = getFormConfig(pageId);
  if (!cfg?.sequence?.length) return null;
  if (!currentKey) return cfg.sequence[0];
  const idx = cfg.sequence.indexOf(currentKey);
  return idx >= 0 ? cfg.sequence[idx + 1] || null : cfg.sequence[0];
}

export function getPrompt(pageId, fieldKey) {
  const cfg = getFormConfig(pageId);
  return cfg?.prompts?.[fieldKey] || null;
}


