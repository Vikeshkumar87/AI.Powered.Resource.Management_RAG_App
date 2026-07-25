import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';

export default function SkillDashboard() {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function loadResources() {
      setLoading(true);
      setError('');
      try {
        const data = await api('/resources/?limit=200');
        if (!cancelled) {
          setResources(data.resources || []);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadResources();
    return () => { cancelled = true; };
  }, []);

  const skillRows = useMemo(() => {
    const skillMap = new Map();

    resources.forEach(resource => {
      (resource.skills || []).forEach(rawSkill => {
        const skill = rawSkill.trim();
        if (!skill) return;

        if (!skillMap.has(skill)) {
          skillMap.set(skill, {
            skill,
            resources: 0,
            bench: 0,
            totalAvailability: 0,
          });
        }

        const row = skillMap.get(skill);
        row.resources += 1;
        row.totalAvailability += Number(resource.availability_percentage || 0);
        if (resource.is_on_bench) {
          row.bench += 1;
        }
      });
    });

    return Array.from(skillMap.values())
      .map(item => ({
        ...item,
        avgAvailability: item.resources ? (item.totalAvailability / item.resources).toFixed(1) : '0.0',
      }))
      .sort((a, b) => b.resources - a.resources);
  }, [resources]);

  return (
    <div>
      <div className="section-header">
        <h1>🧠 Skill Dashboard</h1>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Unique skills</div>
          <div className="stat-value">{skillRows.length}</div>
          <div className="stat-sub">Distinct capabilities in workforce</div>
        </div>
        <div className="stat-card bench">
          <div className="stat-label">Resources analyzed</div>
          <div className="stat-value">{resources.length}</div>
          <div className="stat-sub">Used for skill breakdown</div>
        </div>
      </div>

      <div className="card">
        <h3>Top skills distribution</h3>
        {loading && <p className="empty-state loading" style={{ padding: '1rem' }}>Loading skills...</p>}
        {error && <p className="empty-state" style={{ padding: '1rem' }}>Error: {error}</p>}
        {!loading && !error && skillRows.length === 0 && (
          <p className="empty-state" style={{ padding: '1rem' }}>No skill data found.</p>
        )}
        {!loading && !error && skillRows.length > 0 && (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Skill</th>
                  <th>Resources</th>
                  <th>On Bench</th>
                  <th>Avg Availability</th>
                </tr>
              </thead>
              <tbody>
                {skillRows.slice(0, 30).map(row => (
                  <tr key={row.skill}>
                    <td><strong>{row.skill}</strong></td>
                    <td>{row.resources}</td>
                    <td>{row.bench}</td>
                    <td>{row.avgAvailability}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
