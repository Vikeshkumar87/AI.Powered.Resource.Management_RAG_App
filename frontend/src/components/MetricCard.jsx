export default function MetricCard({ label, value, icon, color = 'blue' }) {
  const colors = {
    blue:   'bg-blue-50 text-blue-700 border-blue-200',
    green:  'bg-green-50 text-green-700 border-green-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
  }
  return (
    <div className={`rounded-xl border p-5 flex flex-col gap-1 ${colors[color]}`}>
      <div className="text-2xl">{icon}</div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-sm font-medium opacity-80">{label}</div>
    </div>
  )
}
