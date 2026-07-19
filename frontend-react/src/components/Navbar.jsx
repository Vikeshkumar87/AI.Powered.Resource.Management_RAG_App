export default function Navbar({ activeSection, onNavigate, links, role, displayName, onLogout }) {
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <span className="logo">⚡</span>
        <span className="brand-text">AI Resource Management</span>
        <span className="badge-rag">RAG Powered</span>
      </div>
      <div className="nav-right">
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
        <div className="nav-user">
          <span className="role-pill">{role}</span>
          <span className="user-name">{displayName}</span>
          <button className="btn btn-outline nav-logout" onClick={onLogout}>Logout</button>
        </div>
      </div>
    </nav>
  );
}
