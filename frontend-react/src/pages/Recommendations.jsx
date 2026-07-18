import { useState } from 'react';
import { api } from '../api';

function escapeHtml(text) {
  return (text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

export default function Recommendations() {
  const [requirements, setRequirements] = useState(
    'Senior backend developer needed for a 6-month FinTech microservices project using Java, Spring Boot, and Kafka'
  );
  const [skillsStr, setSkillsStr] = useState('Java, Spring Boot, Microservices, Kafka');
  const [teamSize, setTeamSize] = useState(2);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function getRecommendations() {
    if (!requirements.trim()) { alert('Please describe the project requirements'); return; }
    const skills = skillsStr ? skillsStr.split(',').map(s => s.trim()).filter(Boolean) : [];
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await api('/rag/recommend', {
        method: 'POST',
        body: JSON.stringify({
          project_requirements: requirements.trim(),
          required_skills: skills,
          team_size: parseInt(teamSize) || 1,
          n_candidates: 10,
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
        <h1>💡 Resource Recommendations</h1>
      </div>
      <div className="card ai-card">
        <p className="ai-description">
          Describe your project requirements and get AI-powered recommendations
          for the best matching resources from the bench.
        </p>
        <div className="recommend-form">
          <div className="form-group">
            <label>Project Requirements</label>
            <textarea
              className="query-textarea"
              placeholder="Describe the project: technology stack, domain, duration, team structure..."
              rows={4}
              value={requirements}
              onChange={e => setRequirements(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Required Skills (comma-separated)</label>
            <input
              type="text"
              className="form-input"
              placeholder="Python, Docker, AWS, React..."
              value={skillsStr}
              onChange={e => setSkillsStr(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Team Size Needed</label>
            <input
              type="number"
              className="form-input-sm"
              value={teamSize}
              min={1}
              max={20}
              onChange={e => setTeamSize(e.target.value)}
            />
          </div>
          <button
            className="btn btn-primary btn-lg"
            onClick={getRecommendations}
            disabled={loading}
            style={{ alignSelf: 'flex-start' }}
          >
            {loading ? '🎯 Analyzing...' : '🎯 Get Recommendations'}
          </button>
        </div>

        {loading && (
          <div className="query-result">🎯 Analyzing requirements and finding best matches...</div>
        )}

        {error && <div className="query-result">❌ Error: {error}</div>}

        {result && !loading && (
          <>
            <div
              className="query-result"
              dangerouslySetInnerHTML={{
                __html: `<strong>AI Recommendation:</strong><br/><br/>${escapeHtml(result.recommendation).replace(/\n/g, '<br/>')}
                  <br/><br/><small style="color:#6b7280">Team size requested: ${result.team_size_requested} · Provider: ${result.llm_provider}</small>`,
              }}
            />
            {(result.bench_candidates || result.all_candidates || []).length > 0 && (
              <div className="query-sources">
                <h4>👥 Top Candidates from Vector Search ({(result.bench_candidates || result.all_candidates).length})</h4>
                {(result.bench_candidates || result.all_candidates).map((c, i) => (
                  <div key={i} className="source-item">
                    <strong>#{i + 1}</strong> 🧑 <em>{c.metadata?.name || 'Resource'}</em>{' '}
                    [Match: {(c.score * 100).toFixed(0)}%]{' '}
                    {c.metadata?.is_on_bench === 'True' && (
                      <span className="bench-badge on-bench" style={{ fontSize: '0.65rem', padding: '1px 6px' }}>
                        On Bench
                      </span>
                    )}<br />
                    <span style={{ color: '#9ca3af', fontSize: '0.75rem' }}>
                      {c.content?.substring(0, 200)}...
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
