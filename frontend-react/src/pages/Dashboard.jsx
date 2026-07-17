import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [aging, setAging] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seedStatus, setSeedStatus] = useState('');
  const [seeding, setSeeding] = useState(false);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const [s, g, a] = await Promise.all([
        api('/dashboard/stats'),
        api('/dashboard/project-gaps'),
        api('/dashboard/bench-aging'),
      ]);
      setStats(s);
      setGaps(g);
      setAging(a);
    } catch {
      setStats(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  async function seedDatabase() {
    setSeeding(true);
    setSeedStatus('');
    try {
      const result = await api('/admin/seed?clear_existing=false', { method: 'POST' });
      setSeedStatus(`✅ ${result.message}`);
      await loadDashboard();
    } catch (e) {
      setSeedStatus(`❌ Error: ${e.message}`);
    } finally {
      setSeeding(false);
    }
  }

  return (
    <div>
      <div className="section-header">
        <h1>📊 Dashboard</h1>
        <button className="btn btn-primary" onClick={loadDashboard}>Refresh</button>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {loading ? (
          <div className="stat-card loading">Loading...</div>
        ) : stats ? (
          <>
            <div className="stat-card">
              <div className="stat-label">Total Resources</div>
              <div className="stat-value">{stats.resources.total}</div>
              <div className="stat-sub">In the organization</div>
            </div>
            <div className="stat-card bench">
              <div className="stat-label">On Bench</div>
              <div className="stat-value">{stats.resources.on_bench}</div>
              <div className="stat-sub">{stats.resources.bench_percentage}% of total</div>
            </div>
            <div className="stat-card allocation">
              <div className="stat-label">Allocated</div>
              <div className="stat-value">{stats.resources.allocated}</div>
              <div className="stat-sub">Active assignments</div>
            </div>
            <div className="stat-card project">
              <div className="stat-label">Active Projects</div>
              <div className="stat-value">{stats.projects.active}</div>
              <div className="stat-sub">{stats.projects.planning} in planning</div>
            </div>
          </>
        ) : (
          <div className="stat-card">
            <div className="stat-value">—</div>
            <div className="stat-label">No data yet. Seed the database!</div>
          </div>
        )}
      </div>

      {/* Dashboard grid */}
      <div className="dashboard-grid">
        <div className="card">
          <h3>🎯 Project Gaps (Open Positions)</h3>
          {loading ? (
            <p className="empty-state loading" style={{ padding: '1rem' }}>Loading...</p>
          ) : gaps.length === 0 ? (
            <p className="empty-state" style={{ padding: '1rem' }}>All projects are fully staffed! 🎉</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Project</th><th>Client</th><th>Gap</th><th>Priority</th>
                </tr>
              </thead>
              <tbody>
                {gaps.map((g, i) => (
                  <tr key={i}>
                    <td><strong>{g.project_name}</strong><br /><small>{g.project_code}</small></td>
                    <td>{g.client}</td>
                    <td>
                      <span className="gap-badge">+{g.gap} needed</span><br />
                      <small>{g.current_team_size}/{g.team_size_required}</small>
                    </td>
                    <td><span className={`priority-badge ${g.priority}`}>{g.priority}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <h3>⏳ Bench Aging Report</h3>
          {loading ? (
            <p className="empty-state loading" style={{ padding: '1rem' }}>Loading...</p>
          ) : aging.length === 0 ? (
            <p className="empty-state" style={{ padding: '1rem' }}>No resources on bench 🎉</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Resource</th><th>Dept</th><th>Days on Bench</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                {aging.map((r, i) => (
                  <tr key={i}>
                    <td><strong>{r.name}</strong><br /><small>{r.designation}</small></td>
                    <td>{r.department}</td>
                    <td>{r.days_on_bench !== null ? `${r.days_on_bench} days` : 'Unknown'}</td>
                    <td><span className={`aging-${r.aging_category}`}>{r.aging_category.toUpperCase()}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Quick Setup */}
      <div className="card setup-card">
        <h3>🚀 Quick Setup</h3>
        <p>Initialize the application with sample data to explore all features.</p>
        <button className="btn btn-success" onClick={seedDatabase} disabled={seeding}>
          {seeding ? 'Seeding...' : 'Seed Sample Data'}
        </button>
        {seedStatus && (
          <span
            className="seed-status"
            style={{ color: seedStatus.startsWith('✅') ? '#065f46' : '#991b1b' }}
          >
            {seedStatus}
          </span>
        )}
      </div>
    </div>
  );
}
