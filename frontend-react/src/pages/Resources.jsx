import { useState, useEffect } from 'react';
import { api } from '../api';
import Modal from '../components/Modal';
import ResourceCard from '../components/ResourceCard';
import ResourceDetailModal from '../components/ResourceDetailModal';

export default function Resources() {
  const [resources, setResources] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);

  async function loadResources(skill = '') {
    setLoading(true);
    setError('');
    try {
      let url = '/resources/?limit=50';
      if (skill) url += `&skill=${encodeURIComponent(skill)}`;
      const data = await api(url);
      setResources(data.resources);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadResources(); }, []);

  async function openDetail(id) {
    setSelectedId(id);
    try {
      const r = await api(`/resources/${id}`);
      setDetail(r);
    } catch (e) {
      setDetail({ error: e.message });
    }
  }

  function closeModal() { setSelectedId(null); setDetail(null); }

  return (
    <div>
      <div className="section-header">
        <h1>🧑‍💼 Resources</h1>
        <div className="header-actions">
          <input
            type="text"
            className="search-input"
            placeholder="Search by skill, dept..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && loadResources(search)}
          />
          <button className="btn btn-primary" onClick={() => loadResources(search)}>Search</button>
        </div>
      </div>

      {loading && <p className="empty-state loading">Loading resources...</p>}
      {error && <p className="empty-state">Error: {error}</p>}
      {!loading && !error && resources.length === 0 && (
        <p className="empty-state">No resources found</p>
      )}
      {!loading && !error && resources.length > 0 && (
        <div className="resource-grid">
          {resources.map(r => (
            <ResourceCard key={r.id} resource={r} onClick={() => openDetail(r.id)} />
          ))}
        </div>
      )}

      {selectedId && (
        <Modal onClose={closeModal}>
          <ResourceDetailModal detail={detail} />
        </Modal>
      )}
    </div>
  );
}
