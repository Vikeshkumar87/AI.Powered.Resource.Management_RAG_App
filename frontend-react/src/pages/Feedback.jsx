import { useMemo, useState } from 'react';
import { addFeedback, clearFeedback, loadFeedback } from '../feedbackStore';

const CATEGORIES = ['General', 'AI Assistant', 'Dashboard', 'Performance', 'Bug'];

export default function Feedback() {
  const [entries, setEntries] = useState(() => loadFeedback());
  const [category, setCategory] = useState('General');
  const [rating, setRating] = useState(4);
  const [message, setMessage] = useState('');

  const averageRating = useMemo(() => {
    if (!entries.length) return '0.0';
    const total = entries.reduce((acc, item) => acc + Number(item.rating || 0), 0);
    return (total / entries.length).toFixed(1);
  }, [entries]);

  function submitFeedback(event) {
    event.preventDefault();
    if (!message.trim()) {
      return;
    }

    const next = addFeedback({
      id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
      category,
      rating: Number(rating),
      message: message.trim(),
      timestamp: new Date().toISOString(),
    });

    setEntries(next);
    setMessage('');
    setRating(4);
    setCategory('General');
  }

  function clearAllFeedback() {
    clearFeedback();
    setEntries([]);
  }

  return (
    <div>
      <div className="section-header">
        <h1>🗣 Feedback</h1>
        <button className="btn btn-outline" onClick={clearAllFeedback} disabled={entries.length === 0}>Clear Feedback</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total feedback</div>
          <div className="stat-value">{entries.length}</div>
          <div className="stat-sub">Stored in local browser</div>
        </div>
        <div className="stat-card allocation">
          <div className="stat-label">Average rating</div>
          <div className="stat-value">{averageRating}</div>
          <div className="stat-sub">Across all submissions</div>
        </div>
      </div>

      <div className="card">
        <h3>Submit feedback</h3>
        <form className="recommend-form" onSubmit={submitFeedback}>
          <div className="phase-input-grid">
            <label className="form-group">
              <span>Category</span>
              <select className="form-input" value={category} onChange={e => setCategory(e.target.value)}>
                {CATEGORIES.map(item => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>
            <label className="form-group">
              <span>Rating (1 to 5)</span>
              <input
                className="form-input"
                type="number"
                min={1}
                max={5}
                value={rating}
                onChange={e => setRating(e.target.value)}
              />
            </label>
          </div>
          <label className="form-group">
            <span>Your feedback</span>
            <textarea
              className="query-textarea"
              rows={4}
              value={message}
              onChange={e => setMessage(e.target.value)}
              placeholder="Share what works and what should improve"
            />
          </label>
          <button className="btn btn-primary" type="submit">Submit Feedback</button>
        </form>
      </div>

      <div className="card">
        <h3>Recent feedback</h3>
        {entries.length === 0 ? (
          <p className="empty-state" style={{ padding: '1rem' }}>No feedback submitted yet.</p>
        ) : (
          <div className="simple-list">
            {entries.slice(0, 20).map(item => (
              <div key={item.id} className="simple-list-item vertical">
                <strong>{item.category} · {item.rating}/5</strong>
                <span>{item.message}</span>
                <small>{new Date(item.timestamp).toLocaleString()}</small>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
