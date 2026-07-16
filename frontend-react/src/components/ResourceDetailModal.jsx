export default function ResourceDetailModal({ detail: r }) {
  if (!r) return <p className="empty-state loading">Loading...</p>;
  if (r.error) return <p className="empty-state">Error: {r.error}</p>;

  return (
    <>
      <h2 style={{ marginBottom: '0.5rem' }}>{r.name}</h2>
      <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>{r.designation} · {r.employee_id}</p>

      <div className="modal-detail-row">
        <span className="modal-label">Department</span><span>{r.department}</span>
      </div>
      <div className="modal-detail-row">
        <span className="modal-label">Email</span><span>{r.email}</span>
      </div>
      <div className="modal-detail-row">
        <span className="modal-label">Location</span><span>{r.location || 'N/A'}</span>
      </div>
      <div className="modal-detail-row">
        <span className="modal-label">Experience</span><span>{r.experience_years} years</span>
      </div>
      <div className="modal-detail-row">
        <span className="modal-label">Availability</span><span>{r.availability_percentage}%</span>
      </div>
      <div className="modal-detail-row">
        <span className="modal-label">Status</span>
        <span className={`bench-badge ${r.is_on_bench ? 'on-bench' : 'allocated'}`}>
          {r.is_on_bench ? '🪑 On Bench' : '✅ Allocated'}
        </span>
      </div>
      {r.hourly_rate && (
        <div className="modal-detail-row">
          <span className="modal-label">Hourly Rate</span><span>${r.hourly_rate}/hr</span>
        </div>
      )}

      <div style={{ marginTop: '1rem' }}>
        <strong>Skills</strong>
        <div className="skill-tags" style={{ marginTop: '0.5rem' }}>
          {(r.skills || []).map(s => <span key={s} className="skill-tag">{s}</span>)}
        </div>
      </div>

      {r.certifications?.length > 0 && (
        <div style={{ marginTop: '1rem' }}>
          <strong>Certifications</strong>
          <div className="skill-tags" style={{ marginTop: '0.5rem' }}>
            {r.certifications.map(c => (
              <span key={c} className="skill-tag" style={{ background: '#dbeafe', borderColor: '#93c5fd' }}>
                📜 {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {r.bio && (
        <div style={{ marginTop: '1rem' }}>
          <strong>Bio</strong>
          <p style={{ marginTop: '0.5rem', color: '#4b5563', fontSize: '0.9rem' }}>{r.bio}</p>
        </div>
      )}

      {r.bench_start_date && (
        <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#fef3c7', borderRadius: '8px' }}>
          <strong>Bench Since:</strong> {new Date(r.bench_start_date).toLocaleDateString()}<br />
          {r.expected_allocation_date && (
            <><strong>Expected Allocation:</strong> {new Date(r.expected_allocation_date).toLocaleDateString()}</>
          )}
        </div>
      )}
    </>
  );
}
