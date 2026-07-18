import { useState, useEffect } from 'react';
import { api } from '../api';
import Modal from '../components/Modal';
import ProjectCard from '../components/ProjectCard';
import ProjectDetailModal from '../components/ProjectDetailModal';

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [detail, setDetail] = useState(null);

  async function loadProjects(s = status) {
    setLoading(true);
    setError('');
    try {
      let url = '/projects/?limit=50';
      if (s) url += `&status=${s}`;
      const data = await api(url);
      setProjects(data.projects);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadProjects(''); }, []);

  function handleStatusChange(e) {
    const val = e.target.value;
    setStatus(val);
    loadProjects(val);
  }

  async function openDetail(id) {
    setDetail({ loading: true });
    try {
      const [p, team] = await Promise.all([
        api(`/projects/${id}`),
        api(`/projects/${id}/team`),
      ]);
      setDetail({ project: p, team });
    } catch (e) {
      setDetail({ error: e.message });
    }
  }

  return (
    <div>
      <div className="section-header">
        <h1>📋 Projects</h1>
        <div className="header-actions">
          <select className="filter-select" value={status} onChange={handleStatusChange}>
            <option value="">All Status</option>
            <option value="planning">Planning</option>
            <option value="active">Active</option>
            <option value="on_hold">On Hold</option>
            <option value="completed">Completed</option>
          </select>
          <button className="btn btn-primary" onClick={() => loadProjects()}>Refresh</button>
        </div>
      </div>

      {loading && <p className="empty-state loading">Loading projects...</p>}
      {error && <p className="empty-state">Error: {error}</p>}
      {!loading && !error && projects.length === 0 && (
        <p className="empty-state">No projects found</p>
      )}
      {!loading && !error && projects.length > 0 && (
        <div className="project-grid">
          {projects.map(p => (
            <ProjectCard key={p.id} project={p} onClick={() => openDetail(p.id)} />
          ))}
        </div>
      )}

      {detail && (
        <Modal onClose={() => setDetail(null)}>
          <ProjectDetailModal detail={detail} />
        </Modal>
      )}
    </div>
  );
}
