export default function ResourceCard({ resource: r, onClick }) {
  return (
    <div
      className={`resource-card ${r.is_on_bench ? 'bench' : 'allocated'}`}
      onClick={onClick}
    >
      <span className={`bench-badge ${r.is_on_bench ? 'on-bench' : 'allocated'}`}>
        {r.is_on_bench ? '🪑 On Bench' : '✅ Allocated'}
      </span>
      <div className="resource-name">{r.name}</div>
      <div className="resource-designation">{r.designation}</div>
      <div className="resource-meta">
        <span className="meta-badge dept">{r.department}</span>
        {r.location && <span className="meta-badge location">📍 {r.location}</span>}
        <span className="meta-badge exp">⭐ {r.experience_years}y</span>
      </div>
      <div className="skill-tags">
        {(r.skills || []).slice(0, 5).map(s => (
          <span key={s} className="skill-tag">{s}</span>
        ))}
        {(r.skills?.length || 0) > 5 && (
          <span className="skill-tag">+{r.skills.length - 5}</span>
        )}
      </div>
    </div>
  );
}
