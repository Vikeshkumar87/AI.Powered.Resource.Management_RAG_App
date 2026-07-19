import { useEffect, useState } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import MetricCard from '../components/MetricCard'
import BenchTable from '../components/BenchTable'

export default function Dashboard() {
  const [metrics, setMetrics]       = useState(null)
  const [benchSkills, setBenchSkills] = useState([])
  const [skillDemand, setSkillDemand] = useState([])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [m, bs, sd] = await Promise.all([
          axios.get('/api/dashboard/metrics'),
          axios.get('/api/dashboard/bench-by-skill'),
          axios.get('/api/dashboard/skill-demand'),
        ])
        setMetrics(m.data)
        setBenchSkills(bs.data)
        setSkillDemand(sd.data)
      } catch (e) {
        setError('Cannot reach backend. Make sure FastAPI is running on port 8000.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <div className="text-center py-20 text-gray-400">Loading dashboard…</div>
  if (error)   return <div className="text-center py-20 text-red-500">{error}</div>

  const COLORS = ['#3b82f6','#60a5fa','#93c5fd','#bfdbfe','#dbeafe']
  const ORANGE = ['#f97316','#fb923c','#fdba74','#fed7aa','#ffedd5']

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">📊 Resource Analytics Dashboard</h2>
        <p className="text-gray-500 text-sm mt-1">Real-time workforce utilization, bench status, and skill demand.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard icon="👥" label="Total Employees"   value={metrics.total_employees}    color="blue"   />
        <MetricCard icon="✅" label="Available (Bench)" value={metrics.available_resources} color="green"  />
        <MetricCard icon="📉" label="Bench %"           value={`${metrics.bench_percentage}%`} color="orange" />
        <MetricCard icon="⚡" label="Avg Utilization"   value={`${metrics.avg_utilization}%`}  color="purple" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Skill Demand */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-4">🎯 Skill Demand (Active Projects)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={skillDemand} layout="vertical" margin={{ left: 20 }}>
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis dataKey="skill" type="category" tick={{ fontSize: 11 }} width={80} />
              <Tooltip />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {skillDemand.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Bench by Skill */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-4">🪑 Bench by Skill</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={benchSkills} layout="vertical" margin={{ left: 20 }}>
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis dataKey="skill" type="category" tick={{ fontSize: 11 }} width={80} />
              <Tooltip />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {benchSkills.map((_, i) => <Cell key={i} fill={ORANGE[i % ORANGE.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Upcoming Projects */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-4">🚀 Upcoming Projects</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 uppercase text-xs">
              <tr>
                {['Project Name', 'Domain', 'Start Date', 'Resources Needed'].map(h => (
                  <th key={h} className="px-4 py-2 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {metrics.upcoming_projects.map((p, i) => (
                <tr key={i} className="hover:bg-blue-50">
                  <td className="px-4 py-2 font-medium">{p.name}</td>
                  <td className="px-4 py-2 text-gray-500">{p.domain}</td>
                  <td className="px-4 py-2 text-gray-500">{p.start_date}</td>
                  <td className="px-4 py-2">
                    <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-xs font-medium">
                      {p.resources_needed} needed
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bench Employees */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-4">🪑 Employees Currently on Bench</h3>
        <BenchTable employees={metrics.bench_employees} />
      </div>
    </div>
  )
}
