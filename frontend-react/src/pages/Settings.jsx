import { applyTheme, loadTheme, saveTheme } from '../settingsStore';

export default function Settings({ theme, onThemeChange }) {
  const selected = theme || loadTheme();

  function updateTheme(nextTheme) {
    const normalized = saveTheme(nextTheme);
    applyTheme(normalized);
    onThemeChange?.(normalized);
  }

  return (
    <div>
      <div className="section-header">
        <h1>⚙️ Settings</h1>
      </div>

      <div className="card">
        <h3>Appearance</h3>
        <div className="simple-list-item">
          <div>
            <strong>Theme</strong>
            <p style={{ marginTop: '0.35rem', color: 'var(--gray-600)' }}>
              Switch between light and dark mode for better readability.
            </p>
          </div>
          <select
            className="filter-select"
            value={selected}
            onChange={e => updateTheme(e.target.value)}
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>
      </div>

      <div className="card">
        <h3>Notes</h3>
        <ul style={{ paddingLeft: '1.2rem', color: 'var(--gray-600)' }}>
          <li>Theme preference is saved in browser local storage.</li>
          <li>Conversation history and feedback are also local to this browser.</li>
          <li>Use admin role to access phase validation pages.</li>
        </ul>
      </div>
    </div>
  );
}
