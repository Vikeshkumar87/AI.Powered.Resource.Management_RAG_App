import { useEffect, useMemo, useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Resources from './pages/Resources';
import Bench from './pages/Bench';
import Projects from './pages/Projects';
import AIQuery from './pages/AIQuery';
import Recommendations from './pages/Recommendations';
import Phases from './pages/Phases';
import Login from './pages/Login';
import { clearSession, loadSession, saveSession } from './auth';

const SECTIONS = {
  phases: Phases,
  dashboard: Dashboard,
  resources: Resources,
  bench: Bench,
  projects: Projects,
  'ai-query': AIQuery,
  recommendations: Recommendations,
};

export default function App() {
  const [session, setSession] = useState(() => loadSession());
  const [activeSection, setActiveSection] = useState('dashboard');

  const links = useMemo(() => {
    const baseLinks = [
      { id: 'dashboard', label: 'Dashboard' },
      { id: 'resources', label: 'Resources' },
      { id: 'bench', label: 'Bench' },
      { id: 'projects', label: 'Projects' },
      { id: 'ai-query', label: 'AI Assistant' },
      { id: 'recommendations', label: 'Recommendations' },
    ];
    if (session?.role === 'admin') {
      return [{ id: 'phases', label: 'Phases' }, ...baseLinks];
    }
    return baseLinks;
  }, [session?.role]);

  function handleLogin(result) {
    saveSession(result);
    setSession(result);
    setActiveSection(result.role === 'admin' ? 'phases' : 'dashboard');
  }

  function handleLogout() {
    clearSession();
    setSession(null);
    setActiveSection('dashboard');
  }

  const allowedSections = new Set(links.map(link => link.id));
  const fallbackSection = links[0]?.id || 'dashboard';
  const resolvedSection = allowedSections.has(activeSection) ? activeSection : fallbackSection;

  useEffect(() => {
    if (session && resolvedSection !== activeSection) {
      setActiveSection(resolvedSection);
    }
  }, [activeSection, resolvedSection, session]);

  if (!session) {
    return <Login onLogin={handleLogin} />;
  }

  const PageComponent = SECTIONS[resolvedSection] || Dashboard;

  return (
    <>
      <Navbar
        activeSection={resolvedSection}
        onNavigate={setActiveSection}
        links={links}
        role={session.role}
        displayName={session.display_name || session.username}
        onLogout={handleLogout}
      />
      <div className="container">
        <PageComponent />
      </div>
    </>
  );
}
