import { useMemo } from 'react';
import { loadChatHistory } from '../chatHistory';

function formatDate(value) {
  if (!value) return 'Unknown';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Unknown' : date.toLocaleString();
}

export default function ChatAnalytics() {
  const history = loadChatHistory();

  const analytics = useMemo(() => {
    const providerCounts = {};
    let totalContextDocs = 0;

    history.forEach(item => {
      const provider = item.llm_provider || 'unknown';
      providerCounts[provider] = (providerCounts[provider] || 0) + 1;
      totalContextDocs += Number(item.context_used || 0);
    });

    const averageContext = history.length ? (totalContextDocs / history.length).toFixed(1) : '0.0';

    return {
      totalQuestions: history.length,
      averageContext,
      providerCounts,
      latestQuestionAt: history[0]?.timestamp || null,
    };
  }, [history]);

  return (
    <div>
      <div className="section-header">
        <h1>📈 Chat Assistant Analytics</h1>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Questions asked</div>
          <div className="stat-value">{analytics.totalQuestions}</div>
          <div className="stat-sub">Across this browser session history</div>
        </div>
        <div className="stat-card allocation">
          <div className="stat-label">Avg context docs</div>
          <div className="stat-value">{analytics.averageContext}</div>
          <div className="stat-sub">Retrieved per RAG answer</div>
        </div>
        <div className="stat-card project">
          <div className="stat-label">Latest question</div>
          <div className="stat-value" style={{ fontSize: '1rem' }}>{formatDate(analytics.latestQuestionAt)}</div>
          <div className="stat-sub">Most recent interaction</div>
        </div>
      </div>

      <div className="card">
        <h3>Provider usage</h3>
        {Object.keys(analytics.providerCounts).length === 0 ? (
          <p className="empty-state" style={{ padding: '1rem' }}>No chat history yet. Ask in AI Assistant to populate analytics.</p>
        ) : (
          <div className="simple-list">
            {Object.entries(analytics.providerCounts).map(([provider, count]) => (
              <div key={provider} className="simple-list-item">
                <strong>{provider}</strong>
                <span>{count} queries</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h3>Recent questions</h3>
        {history.length === 0 ? (
          <p className="empty-state" style={{ padding: '1rem' }}>No recent questions available.</p>
        ) : (
          <div className="simple-list">
            {history.slice(0, 10).map(item => (
              <div key={item.id} className="simple-list-item vertical">
                <strong>{item.question}</strong>
                <small>{formatDate(item.timestamp)} · {item.llm_provider} · context {item.context_used}</small>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
