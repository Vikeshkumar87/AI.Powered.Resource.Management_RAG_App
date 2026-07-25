import { useEffect, useMemo, useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Resources from './pages/Resources';
import Bench from './pages/Bench';
import Projects from './pages/Projects';
import AIQuery from './pages/AIQuery';
import ChatAnalytics from './pages/ChatAnalytics';
import Recommendations from './pages/Recommendations';
import Phases from './pages/Phases';
import EmployeeProfile from './pages/EmployeeProfile';
import SkillDashboard from './pages/SkillDashboard';
import ConversationHistory from './pages/ConversationHistory';
import Feedback from './pages/Feedback';
import Settings from './pages/Settings';
import Login from './pages/Login';
import { clearSession, loadSession, saveSession } from './auth';
import { applyTheme, loadTheme, saveTheme } from './settingsStore';

const SECTIONS = {
  phases: Phases,
  dashboard: Dashboard,
  resources: Resources,
  bench: Bench,
  projects: Projects,
  profiles: EmployeeProfile,
  skills: SkillDashboard,
  'ai-query': AIQuery,
  'chat-analytics': ChatAnalytics,
  'conversation-history': ConversationHistory,
  recommendations: Recommendations,
  feedback: Feedback,
  settings: Settings,
};

export default function App() {
  const [session, setSession] = useState(() => loadSession());
  const [theme, setTheme] = useState(() => loadTheme());
  const [activeSection, setActiveSection] = useState('dashboard');

  const links = useMemo(() => {
    const baseLinks = [
      { id: 'dashboard', label: 'Dashboard' },
      { id: 'resources', label: 'Resources' },
      { id: 'bench', label: 'Bench' },
      { id: 'projects', label: 'Projects' },
      { id: 'profiles', label: 'Employee Profile' },
      // { id: 'skills', label: 'Skill Dashboard' },
      { id: 'ai-query', label: 'AI Assistant' },
      { id: 'chat-analytics', label: 'Chat Analytics' },
      { id: 'conversation-history', label: 'Conversation History' },
      { id: 'recommendations', label: 'Recommendations' },
      { id: 'feedback', label: 'Feedback' },
      { id: 'settings', label: 'Settings' },
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

  useEffect(() => {
    applyTheme(theme);
    saveTheme(theme);
  }, [theme]);

  if (!session) {
    return <Login onLogin={handleLogin} />;
  }

  const PageComponent = SECTIONS[resolvedSection] || Dashboard;
  const pageProps = resolvedSection === 'settings' ? { theme, onThemeChange: setTheme } : {};

  return (
    <>
      <Navbar
        activeSection={resolvedSection}
        onNavigate={setActiveSection}
        links={links}
        role={session.role}
        //displayName={session.role === 'user' ? session.username : (session.display_name || session.username)}
        onLogout={handleLogout}
      />
      <div className="container">
        <PageComponent {...pageProps} />
      </div>
    </>
  );
}
