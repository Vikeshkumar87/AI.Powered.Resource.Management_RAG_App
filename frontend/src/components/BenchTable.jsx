export default function BenchTable({ employees = [] }) {
  if (!employees.length) {
    return <p className="text-gray-500 text-sm">No employees currently on bench.</p>
  }
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
          <tr>
            {['ID', 'Name', 'Domain', 'Skills', 'Experience', 'Bench Since'].map((h) => (
              <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {employees.map((emp) => (
            <tr key={emp.employee_id} className="hover:bg-blue-50 transition-colors">
              <td className="px-4 py-3 font-mono text-xs text-gray-500">{emp.employee_id}</td>
              <td className="px-4 py-3 font-medium">{emp.name}</td>
              <td className="px-4 py-3 text-gray-600">{emp.domain}</td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-1">
                  {(emp.skills || []).slice(0, 4).map((s) => (
                    <span key={s} className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">{s}</span>
                  ))}
                  {emp.skills?.length > 4 && (
                    <span className="text-gray-400 text-xs">+{emp.skills.length - 4}</span>
                  )}
                </div>
              </td>
              <td className="px-4 py-3 text-gray-600">{emp.experience_years} yrs</td>
              <td className="px-4 py-3 text-gray-500">{emp.bench_since ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
