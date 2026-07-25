import { useState } from 'react';
import { api } from '../api';
import { addChatHistory } from '../chatHistory';

const EXAMPLE_QUERIES = [
  'Who are the Python developers on bench?',
  'Find cloud architects with AWS experience',
  'Show resources with 5+ years experience',
  'Which projects need more team members?',
  'Find ML engineers available for a new project',
];

function escapeHtml(text) {
  return (text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function formatScorePercent(score) {
  const numericScore = Number(score);
  if (!Number.isFinite(numericScore)) {
    return '0%';
  }
  const normalized = Math.max(0, Math.min(1, numericScore));
  return `${Math.round(normalized * 100)}%`;
}

export default function AIQuery() {
  const [question, setQuestion] = useState('');
  const [benchOnly, setBenchOnly] = useState(false);
  const [filterType, setFilterType] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function runRAGQuery() {
    if (!question.trim()) { alert('Please enter a question'); return; }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await api('/rag/query', {
        method: 'POST',
        body: JSON.stringify({
          question: question.trim(),
          n_context_docs: 5,
          filter_type: filterType || null,
          filter_bench: benchOnly || null,
        }),
      });
      setResult(data);
      addChatHistory({
        id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
        timestamp: new Date().toISOString(),
        question: question.trim(),
        llm_provider: data.llm_provider,
        context_used: data.context_used,
        answer_preview: (data.answer || '').slice(0, 240),
      });
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="section-header">
        <h1>🤖 AI-Powered Query (RAG)</h1>
      </div>
      <div className="card ai-card">
        <p className="ai-description">
          Ask natural language questions about resources, skills, availability, and projects.
          The system uses RAG (Retrieval-Augmented Generation) to find relevant information
          and generate intelligent responses.
        </p>
        <div className="example-queries">
          <strong>Example queries:</strong>
          {EXAMPLE_QUERIES.map(q => (
            <span key={q} className="example-chip" onClick={() => setQuestion(q)}>{q}</span>
          ))}
        </div>
        <div className="query-form">
          <textarea
            className="query-textarea"
            placeholder="Ask anything about your resources and projects..."
            rows={3}
            value={question}
            onChange={e => setQuestion(e.target.value)}
          />
          <div className="query-options">
            <label>
              <input type="checkbox" checked={benchOnly} onChange={e => setBenchOnly(e.target.checked)} />
              {' '}Bench resources only
            </label>
            <select className="filter-select" value={filterType} onChange={e => setFilterType(e.target.value)}>
              <option value="">All (resources &amp; projects)</option>
              <option value="resource">Resources only</option>
              <option value="project">Projects only</option>
            </select>
            <button
              className="btn btn-primary btn-lg"
              onClick={runRAGQuery}
              disabled={loading}
            >
              {loading ? '🔍 Searching...' : '🔍 Ask AI'}
            </button>
          </div>
        </div>

        {loading && (
          <div className="query-result">
            🔍 Searching and generating response...
          </div>
        )}

        {error && (
          <div className="query-result">❌ Error: {error}</div>
        )}

        {result && !loading && (
          <>
            <div
              className="query-result"
              dangerouslySetInnerHTML={{
                __html: `<strong>Answer:</strong><br/><br/>${escapeHtml(result.answer).replace(/\n/g, '<br/>')}
                  <br/><br/><small style="color:#6b7280">LLM Provider: ${result.llm_provider} · Context docs used: ${result.context_used}</small>`,
              }}
            />
            {result.sources?.length > 0 && (
              <div className="query-sources">
                <h4>📚 Context Sources ({result.sources.length})</h4>
                <div className="table-wrap source-table-wrap">
                  <table className="data-table source-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Score</th>
                        <th>Resource / Project</th>
                        <th>Preview</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.sources.map((s, i) => (
                        <tr key={i}>
                          <td><strong>#{i + 1}</strong></td>
                          <td>
                            <span className="score-badge">{formatScorePercent(s.score)}</span>
                          </td>
                          <td>
                            {s.metadata?.type === 'resource' ? '🧑' : '📋'}{' '}
                            <strong>{s.metadata?.name || 'Unknown'}</strong>
                          </td>
                          <td>
                            <span className="source-preview">{s.content?.substring(0, 150)}...</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
