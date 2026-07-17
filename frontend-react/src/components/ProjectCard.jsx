export default function ProjectCard({ project: p, onClick }) {
  const progress = p.team_size_required > 0
    ? (p.current_team_size / p.team_size_required) * 100
    : 0;
  const progressClass = progress === 100 ? '' : progress >= 50 ? 'warn' : 'danger';
  const skills = (p.required_skills || []).slice(0, 4);

  return (
    <div
      className={`project-card ${p.status}${p.priority === 'critical' ? ' critical' : ''}`}
      onClick={onClick}
    >
      <div className="project-name">{p.name}</div>
      <div className="project-client">👥 {p.client}</div>
      <div className="project-meta">
        <span className={`status-badge ${p.status}`}>{p.status.replace('_', ' ')}</span>
        <span className={`priority-badge ${p.priority}`}>{p.priority}</span>
        {p.domain && <span className="meta-badge dept">{p.domain}</span>}
      </div>
      <div className="team-progress">
        <div className="progress-label">
          <span>Team: {p.current_team_size}/{p.team_size_required}</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="progress-bar">
          <div
            className={`progress-fill ${progressClass}`}
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      </div>
      <div className="skill-tags">
        {skills.map(s => <span key={s} className="skill-tag">{s}</span>)}
        {(p.required_skills?.length || 0) > 4 && (
          <span className="skill-tag">+{p.required_skills.length - 4}</span>
        )}
      </div>
    </div>
  );
}
