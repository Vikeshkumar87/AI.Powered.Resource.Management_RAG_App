import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import AIAssistant from './pages/AIAssistant'

const navClass = ({ isActive }) =>
  `px-4 py-2 rounded-md text-sm font-medium transition-colors ${
    isActive
      ? 'bg-blue-600 text-white'
      : 'text-gray-600 hover:bg-blue-50 hover:text-blue-700'
  }`

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Nav */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🤖</span>
            <h1 className="text-lg font-bold text-gray-900">AI Resource Management</h1>
          </div>
          <nav className="flex gap-2">
            <NavLink to="/" end className={navClass}>
              📊 Dashboard
            </NavLink>
            <NavLink to="/assistant" className={navClass}>
              💬 AI Assistant
            </NavLink>
          </nav>
        </div>
      </header>

      {/* Page content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/assistant" element={<AIAssistant />} />
        </Routes>
      </main>

      <footer className="text-center text-xs text-gray-400 py-4">
        Powered by RAG · FastAPI · PostgreSQL · LangChain · OpenAI
      </footer>
    </div>
  )
}
