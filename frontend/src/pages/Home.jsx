import { useEffect, useState } from 'react'
import StatCard from '../components/StatCard'
import WeatherCard from '../components/WeatherCard'
import { getWeather, getFarms } from '../api/axiosClient'
import useStore from '../store/useStore'
import { Link } from 'react-router-dom'

export default function Home() {
  const { weatherData, setWeatherData, farms, setFarms } = useStore()
  const [loading, setLoading] = useState(true)
  const [selectedFarmId, setSelectedFarmId] = useState(null)

  useEffect(() => {
    async function fetchFarms() {
      try {
        const farmsRes = await getFarms()
        setFarms(farmsRes.data)
        if (farmsRes.data.length > 0) {
          const first = farmsRes.data[0]
          setSelectedFarmId(first.id)
          fetchWeather(first.latitude, first.longitude)
        }
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchFarms()
  }, [])

  async function fetchWeather(lat, lon) {
    try {
      const res = await getWeather(lat, lon)
      setWeatherData(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  function handleFarmChange(e) {
    const farmId = parseInt(e.target.value)
    setSelectedFarmId(farmId)
    const farm = farms.find(f => f.id === farmId)
    if (farm) fetchWeather(farm.latitude, farm.longitude)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-green-600 text-xl font-semibold">
        Loading AgroVolt Dashboard...
      </div>
    )
  }

  const selectedFarm = farms.find(f => f.id === selectedFarmId)

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-green-800">🌱 AgroVolt Dashboard</h1>
          <p className="text-gray-500 mt-1">Smart Agrovoltaic Management — Solar + Crop + Irrigation in one place</p>
        </div>
        <Link to="/predict" className="btn-primary">+ Run New Prediction</Link>
      </div>

      {/* Farm Selector */}
      {farms.length > 0 && (
        <div className="card flex items-center gap-4">
          <span className="text-green-700 font-semibold">📍 Viewing weather for:</span>
          <select
            value={selectedFarmId || ''}
            onChange={handleFarmChange}
            className="w-64"
          >
            {farms.map(farm => (
              <option key={farm.id} value={farm.id}>
                {farm.name} — {farm.location}
              </option>
            ))}
          </select>
          {selectedFarm && (
            <span className="text-sm text-gray-500">
              Lat: {selectedFarm.latitude}, Lon: {selectedFarm.longitude}
            </span>
          )}
        </div>
      )}

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon="🌾" label="Total Farms"      value={farms.length} unit="farms"   color="green"  />
        <StatCard icon="☀️" label="Avg Solar Output" value="142"          unit="kWh/day" color="yellow" />
        <StatCard icon="💧" label="Water Saved"      value="28"           unit="% less"  color="blue"   />
        <StatCard icon="📈" label="Land Equivalent"  value="1.42"         unit="LER"     color="green"  />
      </div>

      {/* Weather + Info */}
      <div className="grid md:grid-cols-2 gap-6">
        <WeatherCard data={weatherData} />
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">🔬 What is Agrovoltaics?</h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            Agrovoltaics places solar panels <strong>above crops</strong> on the same land.
            Panels create partial shade that reduces heat stress on crops, cuts irrigation needs
            by up to 30%, and simultaneously generates electricity. The <strong>Land Equivalent
            Ratio (LER)</strong> proves this dual-use approach is more efficient than keeping
            farming and solar separate.
          </p>
          <div className="mt-4 flex gap-3">
            <Link to="/predict"   className="btn-primary text-sm">Run Prediction →</Link>
            <Link to="/analytics" className="btn-secondary text-sm">View Analytics →</Link>
          </div>
        </div>
      </div>

      {/* Farms List */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-700">🏡 Your Farms</h3>
          <Link to="/settings" className="text-green-600 text-sm hover:underline">+ Add Farm</Link>
        </div>
        {farms.length === 0 ? (
          <p className="text-gray-400 text-sm">No farms yet. Go to Settings to add your first farm.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b text-gray-500">
                  <th className="pb-2">Name</th>
                  <th className="pb-2">Location</th>
                  <th className="pb-2">Crop</th>
                  <th className="pb-2">Panels</th>
                  <th className="pb-2">Area (ha)</th>
                </tr>
              </thead>
              <tbody>
                {farms.map(farm => (
                  <tr
                    key={farm.id}
                    className={`border-b last:border-0 cursor-pointer hover:bg-green-50
                      ${farm.id === selectedFarmId ? 'bg-green-100' : ''}`}
                    onClick={() => {
                      setSelectedFarmId(farm.id)
                      fetchWeather(farm.latitude, farm.longitude)
                    }}
                  >
                    <td className="py-2 font-medium">{farm.name}</td>
                    <td className="py-2 text-gray-500">{farm.location}</td>
                    <td className="py-2">{farm.crop_type}</td>
                    <td className="py-2">{farm.panel_count}</td>
                    <td className="py-2">{farm.area_hectares}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}