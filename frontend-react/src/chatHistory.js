const CHAT_HISTORY_KEY = 'arm_chat_history';
const MAX_CHAT_HISTORY = 40;

export function loadChatHistory() {
  try {
    const raw = localStorage.getItem(CHAT_HISTORY_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveChatHistory(entries) {
  const safeEntries = Array.isArray(entries) ? entries.slice(0, MAX_CHAT_HISTORY) : [];
  localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(safeEntries));
}

export function addChatHistory(entry) {
  const next = [entry, ...loadChatHistory()].slice(0, MAX_CHAT_HISTORY);
  saveChatHistory(next);
  return next;
}

export function clearChatHistory() {
  localStorage.removeItem(CHAT_HISTORY_KEY);
}

export function removeChatHistoryEntry(entryId) {
  const filtered = loadChatHistory().filter(item => item.id !== entryId);
  saveChatHistory(filtered);
  return filtered;
}
