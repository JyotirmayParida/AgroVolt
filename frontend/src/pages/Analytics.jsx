import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  LineChart, Line, ResponsiveContainer, Legend, PieChart, Pie, Cell
} from 'recharts'

// Mock historical data — in production this comes from the DB
const yieldData = [
  { month: 'Jan', agrovoltaic: 4200, traditional: 3100 },
  { month: 'Feb', agrovoltaic: 4500, traditional: 3200 },
  { month: 'Mar', agrovoltaic: 5100, traditional: 3400 },
  { month: 'Apr', agrovoltaic: 5400, traditional: 3300 },
  { month: 'May', agrovoltaic: 4900, traditional: 3000 },
  { month: 'Jun', agrovoltaic: 4300, traditional: 2800 },
]

const solarData = [
  { day: 'Mon', kWh: 142 },
  { day: 'Tue', kWh: 138 },
  { day: 'Wed', kWh: 155 },
  { day: 'Thu', kWh: 110 },
  { day: 'Fri', kWh: 148 },
  { day: 'Sat', kWh: 160 },
  { day: 'Sun', kWh: 145 },
]

const waterData = [
  { name: 'Water Saved',  value: 28, color: '#16a34a' },
  { name: 'Water Used',   value: 72, color: '#d1fae5' },
]

export default function Analytics() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-green-800">📊 Analytics</h1>
        <p className="text-gray-500 mt-1">Farm performance over time.</p>
      </div>

      {/* Yield Comparison */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">
          🌾 Crop Yield: Agrovoltaic vs Traditional (kg/ha)
        </h2>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={yieldData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="agrovoltaic" fill="#16a34a" name="Agrovoltaic" radius={[4,4,0,0]} />
            <Bar dataKey="traditional" fill="#d1fae5" name="Traditional"  radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
        <p className="text-sm text-gray-500 mt-2">
          Agrovoltaic farming consistently yields 30–60% more than traditional farming on the same land.
        </p>
      </div>

      {/* Solar Output */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">☀️ Weekly Solar Output (kWh)</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={solarData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="kWh" stroke="#ca8a04" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Water Savings */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">💧 Water Savings</h2>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={waterData}
                cx="50%" cy="50%"
                innerRadius={60}
                outerRadius={90}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}%`}
              >
                {waterData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-500 text-center">
            Panel shading reduces soil evaporation by ~28%
          </p>
        </div>

        {/* LER Explanation */}
        <div className="card bg-green-50 border border-green-200">
          <h2 className="text-lg font-semibold text-green-800 mb-4">📐 Land Equivalent Ratio</h2>
          <div className="space-y-3 text-sm text-gray-700">
            <div className="flex justify-between items-center bg-white rounded-lg p-3">
              <span>Your Farm LER</span>
              <span className="text-2xl font-bold text-green-600">1.42</span>
            </div>
            <p>
              An LER of <strong>1.42</strong> means your land is 42% more productive
              than if farming and solar were done on separate plots.
            </p>
            <p>
              LER &gt; 1.0 → Agrovoltaic wins ✅<br />
              LER = 1.0 → Break even<br />
              LER &lt; 1.0 → Separate is better
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
