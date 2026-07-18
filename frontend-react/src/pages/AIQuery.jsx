import { useState } from 'react';
import { api } from '../api';

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
                {result.sources.map((s, i) => (
                  <div key={i} className="source-item">
                    <strong>#{i + 1}</strong> [Score: {(s.score * 100).toFixed(0)}%]{' '}
                    {s.metadata?.type === 'resource' ? '🧑' : '📋'}{' '}
                    <em>{s.metadata?.name || 'Unknown'}</em><br />
                    <span style={{ color: '#9ca3af', fontSize: '0.75rem' }}>
                      {s.content?.substring(0, 150)}...
                    </span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
