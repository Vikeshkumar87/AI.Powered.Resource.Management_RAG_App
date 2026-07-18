export default function Navbar({ activeSection, onNavigate }) {
  const links = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'resources', label: 'Resources' },
    { id: 'bench', label: 'Bench' },
    { id: 'projects', label: 'Projects' },
    { id: 'ai-query', label: 'AI Query' },
    { id: 'recommendations', label: 'Recommendations' },
  ];

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <span className="logo">⚡</span>
        <span className="brand-text">AI Resource Management</span>
        <span className="badge-rag">RAG Powered</span>
      </div>
      <div className="nav-links">
        {links.map(({ id, label }) => (
          <button
            key={id}
            className={`nav-link${activeSection === id ? ' active' : ''}`}
            onClick={() => onNavigate(id)}
          >
            {label}
          </button>
        ))}
      </div>
    </nav>
  );
}
