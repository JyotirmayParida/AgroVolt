import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts'

export default function SolarChart({ forecast }) {
  if (!forecast || forecast.length === 0) return null

  const data = forecast.map((kwh, i) => ({
    day: `Day ${i + 1}`,
    kWh: kwh,
  }))

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">☀️ 7-Day Solar Forecast</h3>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="solarGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#ca8a04" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#ca8a04" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="day" tick={{ fontSize: 12 }} />
          <YAxis unit=" kWh" tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v) => [`${v} kWh`, 'Solar Output']} />
          <Area
            type="monotone"
            dataKey="kWh"
            stroke="#ca8a04"
            fill="url(#solarGradient)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
