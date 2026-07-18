export default function ProjectDetailModal({ detail }) {
  if (!detail || detail.loading) return <p className="empty-state loading">Loading...</p>;
  if (detail.error) return <p className="empty-state">Error: {detail.error}</p>;

  const { project: p, team } = detail;

  return (
    <>
      <h2 style={{ marginBottom: '0.5rem' }}>{p.name}</h2>
      <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>{p.project_code} · {p.client}</p>

      <div className="modal-detail-row">
        <span className="modal-label">Status</span>
        <span className={`status-badge ${p.status}`}>{p.status}</span>
      </div>
      <div className="modal-detail-row">
        <span className="modal-label">Priority</span>
        <span className={`priority-badge ${p.priority}`}>{p.priority}</span>
      </div>
      <div className="modal-detail-row">
        <span className="modal-label">Domain</span><span>{p.domain || 'N/A'}</span>
      </div>
      <div className="modal-detail-row">
        <span className="modal-label">Location</span><span>{p.location || 'Remote'}</span>
      </div>
      <div className="modal-detail-row">
        <span className="modal-label">Team Size</span>
        <span>{p.current_team_size}/{p.team_size_required}</span>
      </div>
      {p.budget && (
        <div className="modal-detail-row">
          <span className="modal-label">Budget</span>
          <span>${p.budget.toLocaleString()}</span>
        </div>
      )}
      {p.start_date && (
        <div className="modal-detail-row">
          <span className="modal-label">Start Date</span>
          <span>{new Date(p.start_date).toLocaleDateString()}</span>
        </div>
      )}
      {p.end_date && (
        <div className="modal-detail-row">
          <span className="modal-label">End Date</span>
          <span>{new Date(p.end_date).toLocaleDateString()}</span>
        </div>
      )}
      {p.manager_name && (
        <div className="modal-detail-row">
          <span className="modal-label">Manager</span><span>{p.manager_name}</span>
        </div>
      )}

      <div style={{ marginTop: '1rem' }}>
        <strong>Required Skills</strong>
        <div className="skill-tags" style={{ marginTop: '0.5rem' }}>
          {(p.required_skills || []).map(s => <span key={s} className="skill-tag">{s}</span>)}
        </div>
      </div>

      {p.description && (
        <div style={{ marginTop: '1rem' }}>
          <strong>Description</strong>
          <p style={{ marginTop: '0.5rem', color: '#4b5563', fontSize: '0.9rem' }}>{p.description}</p>
        </div>
      )}

      <div style={{ marginTop: '1.25rem' }}>
        <strong>Current Team ({team?.length || 0})</strong>
        {team?.length > 0 ? (
          <table className="data-table" style={{ marginTop: '0.5rem' }}>
            <thead>
              <tr><th>Resource</th><th>Role</th><th>Allocation</th></tr>
            </thead>
            <tbody>
              {team.map((m, i) => (
                <tr key={i}>
                  <td>{m.resource_name}</td>
                  <td>{m.role}</td>
                  <td>{m.allocation_percentage}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.5rem' }}>
            No team members assigned yet
          </p>
        )}
      </div>
    </>
  );
}
