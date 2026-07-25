import { useState } from 'react';
import { clearChatHistory, loadChatHistory, removeChatHistoryEntry } from '../chatHistory';

function formatDate(value) {
  if (!value) return 'Unknown';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Unknown' : date.toLocaleString();
}

export default function ConversationHistory() {
  const [history, setHistory] = useState(() => loadChatHistory());

  function clearAll() {
    clearChatHistory();
    setHistory([]);
  }

  function removeOne(entryId) {
    setHistory(removeChatHistoryEntry(entryId));
  }

  return (
    <div>
      <div className="section-header">
        <h1>🕘 Conversation History</h1>
        <button className="btn btn-outline" onClick={clearAll} disabled={history.length === 0}>Clear History</button>
      </div>

      {history.length === 0 ? (
        <div className="card">
          <p className="empty-state" style={{ padding: '1rem' }}>No conversation history yet. Use AI Assistant to generate entries.</p>
        </div>
      ) : (
        <div className="conversation-list">
          {history.map((item, idx) => (
            <article key={item.id || idx} className="conversation-card">
              <div className="conversation-header">
                <div>
                  <strong>Q{history.length - idx}.</strong> {item.question}
                </div>
                <button className="btn btn-outline" onClick={() => removeOne(item.id)}>Remove</button>
              </div>
              <p>{item.answer_preview || 'No answer preview available.'}</p>
              <small>
                {formatDate(item.timestamp)} · provider {item.llm_provider || 'unknown'} · context {item.context_used ?? 0}
              </small>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
