export default function IrrigationPanel({ result }) {
  if (!result) return null

  const colorMap = {
    irrigate_now:    'bg-red-100    border-red-400    text-red-700',
    irrigate_in_2h: 'bg-yellow-100 border-yellow-400 text-yellow-700',
    no_irrigation:  'bg-green-100  border-green-400  text-green-700',
  }

  const cls = colorMap[result.recommendation] || 'bg-gray-100 border-gray-300 text-gray-700'

  return (
    <div className={`card border-2 ${cls}`}>
      <h3 className="text-lg font-semibold mb-2">💧 Irrigation Recommendation</h3>
      <p className="text-2xl font-bold mb-1">{result.label}</p>
      <p className="text-sm">{result.reason}</p>
      <p className="text-xs mt-2 text-gray-500">
        Model confidence: {(result.confidence * 100).toFixed(0)}%
      </p>
    </div>
  )
}
