import { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Resources from './pages/Resources';
import Bench from './pages/Bench';
import Projects from './pages/Projects';
import AIQuery from './pages/AIQuery';
import Recommendations from './pages/Recommendations';

const SECTIONS = {
  dashboard: Dashboard,
  resources: Resources,
  bench: Bench,
  projects: Projects,
  'ai-query': AIQuery,
  recommendations: Recommendations,
};

export default function App() {
  const [activeSection, setActiveSection] = useState('dashboard');

  const PageComponent = SECTIONS[activeSection] || Dashboard;

  return (
    <>
      <Navbar activeSection={activeSection} onNavigate={setActiveSection} />
      <div className="container">
        <PageComponent />
      </div>
    </>
  );
}
