import { useState } from 'react';
import { api } from '../api';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await api('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          username: username.trim(),
          password,
        }),
      });
      onLogin(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="phase-kicker">Secure Access</div>
        <h1>Sign in</h1>
        <p>Log in as admin to access phase validation. Standard users will see all other tabs.</p>

        <form className="login-form" onSubmit={submit}>
          <label className="form-group">
            <span>Username</span>
            <input
              type="text"
              className="form-input"
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoComplete="username"
            />
          </label>

          <label className="form-group">
            <span>Password</span>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </label>

          <button className="btn btn-primary btn-lg" type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        {error && <div className="phase-error">{error}</div>}

        <div className="login-hint">
          <div><strong>Admin:</strong> admin / admin123</div>
          <div><strong>User:</strong> user / user123</div>
        </div>
      </div>
    </div>
  );
}