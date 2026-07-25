import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';

export default function EmployeeProfile() {
  const [resources, setResources] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function loadResources() {
      setLoading(true);
      setError('');
      try {
        const data = await api('/resources/?limit=100');
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

  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return resources;

    return resources.filter(item => {
      const haystack = [
        item.name,
        item.employee_id,
        item.designation,
        item.department,
        item.location,
        ...(item.skills || []),
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return haystack.includes(term);
    });
  }, [resources, query]);

  return (
    <div>
      <div className="section-header">
        <h1>👤 Employee Profile</h1>
        <div className="header-actions">
          <input
            className="search-input"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search by name, skill, department..."
          />
        </div>
      </div>

      {loading && <p className="empty-state loading">Loading employee profiles...</p>}
      {error && <p className="empty-state">Error: {error}</p>}

      {!loading && !error && (
        <div className="profile-grid">
          {filtered.map(resource => (
            <article key={resource.id} className="profile-card">
              <div className="profile-head">
                <div>
                  <h3>{resource.name}</h3>
                  <p>{resource.designation}</p>
                </div>
                <span className={`bench-badge ${resource.is_on_bench ? 'on-bench' : 'allocated'}`}>
                  {resource.is_on_bench ? 'On Bench' : 'Allocated'}
                </span>
              </div>
              <div className="profile-meta">
                <span>{resource.employee_id}</span>
                <span>{resource.department}</span>
                <span>{resource.location || 'NA'}</span>
                <span>{resource.experience_years} yrs exp</span>
                <span>{resource.availability_percentage}% availability</span>
              </div>
              <div className="skill-tags">
                {(resource.skills || []).slice(0, 10).map(skill => (
                  <span key={skill} className="skill-tag">{skill}</span>
                ))}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
