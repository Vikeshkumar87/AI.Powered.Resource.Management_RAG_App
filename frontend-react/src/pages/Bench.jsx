import { useState, useEffect } from 'react';
import { api } from '../api';
import Modal from '../components/Modal';
import ResourceCard from '../components/ResourceCard';
import ResourceDetailModal from '../components/ResourceDetailModal';

const DEPARTMENTS = ['Engineering', 'Data Science', 'Frontend', 'QA', 'Security', 'Product'];

export default function Bench() {
  const [resources, setResources] = useState([]);
  const [dept, setDept] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [detail, setDetail] = useState(null);

  async function loadBench(department = dept) {
    setLoading(true);
    setError('');
    try {
      let url = '/resources/bench?limit=50';
      if (department) url += `&department=${encodeURIComponent(department)}`;
      const data = await api(url);
      setResources(data.resources);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadBench(''); }, []);

  function handleDeptChange(e) {
    const val = e.target.value;
    setDept(val);
    loadBench(val);
  }

  async function openDetail(id) {
    setDetail({ loading: true });
    try {
      const r = await api(`/resources/${id}`);
      setDetail(r);
    } catch (e) {
      setDetail({ error: e.message });
    }
  }

  return (
    <div>
      <div className="section-header">
        <h1>🪑 Bench Management</h1>
        <div className="header-actions">
          <select className="filter-select" value={dept} onChange={handleDeptChange}>
            <option value="">All Departments</option>
            {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
          <button className="btn btn-primary" onClick={() => loadBench()}>Refresh</button>
        </div>
      </div>

      {loading && <p className="empty-state loading">Loading bench resources...</p>}
      {error && <p className="empty-state">Error: {error}</p>}
      {!loading && !error && resources.length === 0 && (
        <p className="empty-state">No resources on bench! Everyone is allocated. 🎉</p>
      )}
      {!loading && !error && resources.length > 0 && (
        <div className="resource-grid">
          {resources.map(r => (
            <ResourceCard key={r.id} resource={r} onClick={() => openDetail(r.id)} />
          ))}
        </div>
      )}

      {detail && (
        <Modal onClose={() => setDetail(null)}>
          <ResourceDetailModal detail={detail.loading ? null : detail} />
        </Modal>
      )}
    </div>
  );
}
