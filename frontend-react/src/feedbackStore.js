const FEEDBACK_KEY = 'arm_feedback_history';
const MAX_FEEDBACK_ITEMS = 100;

export function loadFeedback() {
  try {
    const raw = localStorage.getItem(FEEDBACK_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function addFeedback(entry) {
  const next = [entry, ...loadFeedback()].slice(0, MAX_FEEDBACK_ITEMS);
  localStorage.setItem(FEEDBACK_KEY, JSON.stringify(next));
  return next;
}

export function clearFeedback() {
  localStorage.removeItem(FEEDBACK_KEY);
}
