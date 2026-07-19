import { useState } from 'react';
import { api } from '../api';

const DEFAULT_PHASE3_REQUEST = 'Need a Python FastAPI backend developer with high availability for a new service';
const DEFAULT_PHASE4_REQUIREMENTS = 'Need senior backend developers for a FinTech microservices project using Java, Spring Boot, and Kafka';
const DEFAULT_PHASE4_SKILLS = 'Java, Spring Boot, Microservices, Kafka, PostgreSQL';

function parseSkills(text) {
  return (text || '')
    .split(',')
    .map(skill => skill.trim())
    .filter(Boolean);
}

function formatJson(value) {
  return JSON.stringify(value, null, 2);
}

function PhaseCard({ title, phase, description, status, error, onRun, running, children }) {
  return (
    <section className="phase-card">
      <div className="phase-card-header">
        <div>
          <div className="phase-kicker">{phase}</div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
        <button className="btn btn-primary" onClick={onRun} disabled={running}>
          {running ? 'Running...' : 'Run phase'}
        </button>
      </div>
      {status && <div className="phase-status">{status}</div>}
      {error && <div className="phase-error">{error}</div>}
      {children}
    </section>
  );
}

function SummaryMetric({ label, value, sublabel }) {
  return (
    <div className="phase-metric">
      <div className="phase-metric-label">{label}</div>
      <div className="phase-metric-value">{value}</div>
      <div className="phase-metric-sub">{sublabel}</div>
    </div>
  );
}

export default function Phases() {
  const [phase1Result, setPhase1Result] = useState(null);
  const [phase2Result, setPhase2Result] = useState(null);
  const [phase3Request, setPhase3Request] = useState(DEFAULT_PHASE3_REQUEST);
  const [phase3TopK, setPhase3TopK] = useState(5);
  const [phase3MinAvailability, setPhase3MinAvailability] = useState(50);
  const [phase3MaxUtilization, setPhase3MaxUtilization] = useState(50);
  const [phase3Result, setPhase3Result] = useState(null);
  const [phase4Requirements, setPhase4Requirements] = useState(DEFAULT_PHASE4_REQUIREMENTS);
  const [phase4Skills, setPhase4Skills] = useState(DEFAULT_PHASE4_SKILLS);
  const [phase4TeamSize, setPhase4TeamSize] = useState(3);
  const [phase4TopK, setPhase4TopK] = useState(10);
  const [phase4Result, setPhase4Result] = useState(null);
  const [phase5Result, setPhase5Result] = useState(null);
  const [running, setRunning] = useState({});
  const [error, setError] = useState({});
  const [runAllStatus, setRunAllStatus] = useState('');

  function setPhaseState(phase, value) {
    setRunning(prev => ({ ...prev, [phase]: value }));
  }

  function setPhaseError(phase, value) {
    setError(prev => ({ ...prev, [phase]: value }));
  }

  async function runPhase1() {
    setPhaseState('phase1', true);
    setPhaseError('phase1', '');
    try {
      const data = await api('/admin/phase1/prepare-data', { method: 'POST' });
      setPhase1Result(data);
      return data;
    } catch (e) {
      setPhaseError('phase1', e.message);
      throw e;
    } finally {
      setPhaseState('phase1', false);
    }
  }

  async function runPhase2() {
    setPhaseState('phase2', true);
    setPhaseError('phase2', '');
    try {
      const data = await api('/admin/phase2/build-rag', { method: 'POST' });
      setPhase2Result(data);
      return data;
    } catch (e) {
      setPhaseError('phase2', e.message);
      throw e;
    } finally {
      setPhaseState('phase2', false);
    }
  }

  async function runPhase3() {
    setPhaseState('phase3', true);
    setPhaseError('phase3', '');
    try {
      const data = await api('/admin/phase3/retrieve', {
        method: 'POST',
        body: JSON.stringify({
          staffing_request: phase3Request.trim(),
          top_k: Number(phase3TopK) || 5,
          min_availability: Number(phase3MinAvailability) || 0,
          max_utilization: Number(phase3MaxUtilization) || 100,
        }),
      });
      setPhase3Result(data);
      return data;
    } catch (e) {
      setPhaseError('phase3', e.message);
      throw e;
    } finally {
      setPhaseState('phase3', false);
    }
  }

  async function runPhase4() {
    setPhaseState('phase4', true);
    setPhaseError('phase4', '');
    try {
      const data = await api('/admin/phase4/recommend', {
        method: 'POST',
        body: JSON.stringify({
          project_requirements: phase4Requirements.trim(),
          required_skills: parseSkills(phase4Skills),
          team_size: Number(phase4TeamSize) || 1,
          top_k: Number(phase4TopK) || 10,
        }),
      });
      setPhase4Result(data);
      return data;
    } catch (e) {
      setPhaseError('phase4', e.message);
      throw e;
    } finally {
      setPhaseState('phase4', false);
    }
  }

  async function runPhase5() {
    setPhaseState('phase5', true);
    setPhaseError('phase5', '');
    try {
      const data = await api('/admin/phase5/dashboard');
      setPhase5Result(data);
      return data;
    } catch (e) {
      setPhaseError('phase5', e.message);
      throw e;
    } finally {
      setPhaseState('phase5', false);
    }
  }

  async function runAllPhases() {
    setRunAllStatus('');
    try {
      await runPhase1();
      await runPhase2();
      await runPhase3();
      await runPhase4();
      await runPhase5();
      setRunAllStatus('All phases completed successfully.');
    } catch {
      setRunAllStatus('Phase run stopped at the first error.');
    }
  }

  return (
    <div className="phase-shell">
      <div className="phase-hero card">
        <div>
          <div className="phase-kicker">Browser validation</div>
          <h1>Phase output console</h1>
          <p>
            Run each backend phase from the browser, inspect the returned JSON, and verify the
            full data pipeline without leaving the UI.
          </p>
        </div>
        <div className="phase-hero-actions">
          <button className="btn btn-success btn-lg" onClick={runAllPhases} disabled={Object.values(running).some(Boolean)}>
            {Object.values(running).some(Boolean) ? 'Running...' : 'Run all phases'}
          </button>
          {runAllStatus && <div className="phase-status phase-status-inline">{runAllStatus}</div>}
        </div>
      </div>

      <div className="phase-summary-grid">
        <SummaryMetric label="Phase 1" value={phase1Result?.employees_count ?? '—'} sublabel="Employees prepared" />
        <SummaryMetric label="Phase 2" value={phase2Result?.documents_indexed ?? '—'} sublabel="Documents indexed" />
        <SummaryMetric label="Phase 3" value={phase3Result?.total_matches ?? '—'} sublabel="Matches returned" />
        <SummaryMetric label="Phase 4" value={phase4Result?.recommended_employees?.length ?? '—'} sublabel="Recommended employees" />
        <SummaryMetric label="Phase 5" value={phase5Result?.resources?.available ?? '—'} sublabel="Available resources" />
      </div>

      <div className="phase-grid">
        <PhaseCard
          phase="Phase 1"
          title="Prepare standardized data"
          description="Collect sample employees and projects, normalize skills, and persist the JSON artifacts used by later phases."
          status={phase1Result ? `Prepared ${phase1Result.employees_count} employees and ${phase1Result.projects_count} projects.` : ''}
          error={error.phase1}
          running={running.phase1}
          onRun={runPhase1}
        >
          {phase1Result && (
            <div className="phase-output-stack">
              <div className="phase-pill-row">
                <span className="phase-pill">Taxonomy domains: {phase1Result.taxonomy_domains}</span>
                <span className="phase-pill">Employees: {phase1Result.employees_count}</span>
                <span className="phase-pill">Projects: {phase1Result.projects_count}</span>
              </div>
              <pre className="json-output">{formatJson(phase1Result)}</pre>
            </div>
          )}
        </PhaseCard>

        <PhaseCard
          phase="Phase 2"
          title="Build the FAISS RAG pipeline"
          description="Embed employee and project documents, store the index, and generate the phase 2 artifacts."
          status={phase2Result ? `${phase2Result.documents_indexed} documents indexed.` : ''}
          error={error.phase2}
          running={running.phase2}
          onRun={runPhase2}
        >
          {phase2Result && (
            <div className="phase-output-stack">
              <div className="phase-pill-row">
                <span className="phase-pill">FAISS: {phase2Result.faiss_available ? 'available' : 'unavailable'}</span>
                <span className="phase-pill">Resource docs: {phase2Result.resource_documents}</span>
                <span className="phase-pill">Project docs: {phase2Result.project_documents}</span>
              </div>
              <div className="phase-artifact-list">
                {Object.entries(phase2Result.artifacts || {}).map(([label, value]) => (
                  <div key={label} className="phase-artifact-item">
                    <strong>{label}</strong>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
              <pre className="json-output">{formatJson(phase2Result)}</pre>
            </div>
          )}
        </PhaseCard>

        <PhaseCard
          phase="Phase 3"
          title="Retrieve staffing matches"
          description="Turn a natural-language staffing request into embeddings and inspect the filtered matches."
          status={phase3Result ? `${phase3Result.total_matches} matching resources found.` : ''}
          error={error.phase3}
          running={running.phase3}
          onRun={runPhase3}
        >
          <div className="phase-form-grid">
            <label className="form-group">
              <span>Staffing request</span>
              <textarea className="query-textarea" rows={4} value={phase3Request} onChange={e => setPhase3Request(e.target.value)} />
            </label>
            <div className="phase-input-grid">
              <label className="form-group">
                <span>Top K</span>
                <input className="form-input" type="number" min={1} max={20} value={phase3TopK} onChange={e => setPhase3TopK(e.target.value)} />
              </label>
              <label className="form-group">
                <span>Min availability %</span>
                <input className="form-input" type="number" min={0} max={100} value={phase3MinAvailability} onChange={e => setPhase3MinAvailability(e.target.value)} />
              </label>
              <label className="form-group">
                <span>Max utilization %</span>
                <input className="form-input" type="number" min={0} max={100} value={phase3MaxUtilization} onChange={e => setPhase3MaxUtilization(e.target.value)} />
              </label>
            </div>
          </div>
          {phase3Result && (
            <div className="phase-output-stack">
              <div className="phase-pill-row">
                <span className="phase-pill">Min availability: {phase3Result.filters?.min_availability}%</span>
                <span className="phase-pill">Max utilization: {phase3Result.filters?.max_utilization}%</span>
                <span className="phase-pill">Matches: {phase3Result.total_matches}</span>
              </div>
              <div className="phase-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Resource</th>
                      <th>Department</th>
                      <th>Match</th>
                      <th>Availability</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(phase3Result.top_matches || []).map((match, index) => (
                      <tr key={`${match.id || index}-${match.name || 'match'}`}>
                        <td>
                          <strong>{match.name}</strong><br />
                          <small>{(match.skills || []).slice(0, 4).join(', ')}</small>
                        </td>
                        <td>{match.department || '—'}</td>
                        <td>{Math.round((match.match_score || 0) * 100)}%</td>
                        <td>{match.availability_percentage ?? 0}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <pre className="json-output">{formatJson(phase3Result)}</pre>
            </div>
          )}
        </PhaseCard>

        <PhaseCard
          phase="Phase 4"
          title="Generate recommendations"
          description="Rank candidate resources for a project, surface skill overlap, and show the explanation behind each pick."
          status={phase4Result ? `${phase4Result.recommended_employees?.length || 0} recommended employees selected.` : ''}
          error={error.phase4}
          running={running.phase4}
          onRun={runPhase4}
        >
          <div className="phase-form-grid">
            <label className="form-group">
              <span>Project requirements</span>
              <textarea className="query-textarea" rows={4} value={phase4Requirements} onChange={e => setPhase4Requirements(e.target.value)} />
            </label>
            <div className="phase-input-grid phase-input-grid-wide">
              <label className="form-group">
                <span>Required skills</span>
                <input className="form-input" type="text" value={phase4Skills} onChange={e => setPhase4Skills(e.target.value)} />
              </label>
              <label className="form-group">
                <span>Team size</span>
                <input className="form-input" type="number" min={1} max={20} value={phase4TeamSize} onChange={e => setPhase4TeamSize(e.target.value)} />
              </label>
              <label className="form-group">
                <span>Top K</span>
                <input className="form-input" type="number" min={1} max={20} value={phase4TopK} onChange={e => setPhase4TopK(e.target.value)} />
              </label>
            </div>
          </div>
          {phase4Result && (
            <div className="phase-output-stack">
              <div className="phase-pill-row">
                <span className="phase-pill">Team size: {phase4Result.team_size}</span>
                <span className="phase-pill">Skill gaps: {(phase4Result.skill_gaps || []).length}</span>
                <span className="phase-pill">Upskilling ideas: {(phase4Result.upskilling_suggestions || []).length}</span>
              </div>
              <div className="phase-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Employee</th>
                      <th>Department</th>
                      <th>Score</th>
                      <th>Justification</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(phase4Result.recommended_employees || []).map((employee, index) => (
                      <tr key={`${employee.resource_id || index}-${employee.name || 'employee'}`}>
                        <td>
                          <strong>{employee.name}</strong><br />
                          <small>{(employee.skills || []).slice(0, 4).join(', ')}</small>
                        </td>
                        <td>{employee.department || '—'}</td>
                        <td>{Math.round((employee.match_score || 0) * 100)}%</td>
                        <td>{employee.justification}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <pre className="json-output">{formatJson(phase4Result)}</pre>
            </div>
          )}
        </PhaseCard>

        <PhaseCard
          phase="Phase 5"
          title="Review dashboard intelligence"
          description="Summarize capacity, skill demand, open project gaps, and staffing suggestions generated from the pipeline."
          status={phase5Result ? `${phase5Result.resources?.available ?? 0} resources available.` : ''}
          error={error.phase5}
          running={running.phase5}
          onRun={runPhase5}
        >
          {phase5Result && (
            <div className="phase-output-stack">
              <div className="phase-summary-grid phase-summary-grid-tight">
                <SummaryMetric label="Total resources" value={phase5Result.resources?.total ?? '—'} sublabel="Organization size" />
                <SummaryMetric label="Available" value={phase5Result.resources?.available ?? '—'} sublabel="Ready for assignment" />
                <SummaryMetric label="Bench" value={phase5Result.resources?.bench ?? '—'} sublabel="On the bench" />
                <SummaryMetric label="Bench %" value={phase5Result.resources?.bench_percentage ?? '—'} sublabel="Current capacity mix" />
              </div>
              <div className="phase-side-by-side">
                <div className="phase-mini-card">
                  <h3>Skill demand gaps</h3>
                  <div className="phase-pill-row">
                    {(phase5Result.skill_demand_insights || []).slice(0, 6).map(item => (
                      <span key={item.skill} className="phase-pill">
                        {item.skill}: +{item.gap}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="phase-mini-card">
                  <h3>Open projects</h3>
                  <div className="phase-pill-row">
                    {(phase5Result.project_gaps || []).slice(0, 6).map(project => (
                      <span key={project.project_code} className="phase-pill">
                        {project.project_code}: +{project.gap}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <pre className="json-output">{formatJson(phase5Result)}</pre>
            </div>
          )}
        </PhaseCard>
      </div>
    </div>
  );
}