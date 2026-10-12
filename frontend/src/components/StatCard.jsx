export default function StatCard({ icon, label, value, unit, color = 'green' }) {
  const colors = {
    green:  'bg-green-100  text-green-700  border-green-200',
    yellow: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    blue:   'bg-blue-100   text-blue-700   border-blue-200',
    red:    'bg-red-100    text-red-700    border-red-200',
  }

  return (
    <div className={`card border ${colors[color]} flex items-center gap-4`}>
      <span className="text-4xl">{icon}</span>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold">
          {value} <span className="text-base font-normal">{unit}</span>
        </p>
      </div>
    </div>
  )
}
