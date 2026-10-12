import { useState } from 'react'
import {
  predictCropYield,
  getSolarForecast,
  getIrrigationRecommendation
} from '../api/axiosClient'
import { getErrorMessage } from '../api/errorHandler'
import useStore from '../store/useStore'
import SolarChart from '../components/SolarChart'
import IrrigationPanel from '../components/IrrigationPanel'

const CROP_TYPES = [
  { id: 0, name: 'Wheat' },
  { id: 1, name: 'Rice' },
  { id: 2, name: 'Vegetables' },
  { id: 3, name: 'Berries' },
]

export default function Predict() {
  const { setCropResult, setSolarResult, setIrrigationResult,
          cropResult, solarResult, irrigationResult } = useStore()

  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  const [form, setForm] = useState({
    shading_pct:         30,
    temperature:         28,
    soil_moisture:       45,
    rainfall:            5,
    crop_type_encoded:   0,
    panel_tilt:          15,
    latitude:            20.29,
    longitude:           85.82,
    panel_count:         50,
    panel_watt_peak:     400,
    rainfall_last_24h:   5,
    time_of_day:         10,
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: parseFloat(value) || value }))
  }

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    try {
      const [cropRes, solarRes, irrigRes] = await Promise.all([
        predictCropYield({
          shading_pct:       form.shading_pct,
          temperature:       form.temperature,
          soil_moisture:     form.soil_moisture,
          rainfall:          form.rainfall,
          crop_type_encoded: parseInt(form.crop_type_encoded),
          panel_tilt:        form.panel_tilt,
        }),
        getSolarForecast({
          latitude:        form.latitude,
          longitude:       form.longitude,
          panel_count:     form.panel_count,
          panel_watt_peak: form.panel_watt_peak,
        }),
        getIrrigationRecommendation({
          soil_moisture:     form.soil_moisture,
          temperature:       form.temperature,
          crop_type_encoded: parseInt(form.crop_type_encoded),
          rainfall_last_24h: form.rainfall_last_24h,
          time_of_day:       parseInt(form.time_of_day),
        }),
      ])
      setCropResult(cropRes.data)
      setSolarResult(solarRes.data)
      setIrrigationResult(irrigRes.data)
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to complete predictions. Please verify backend connection.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-green-800">🔮 Run Prediction</h1>
        <p className="text-gray-500 mt-1">Enter your farm parameters to get AI-powered predictions.</p>
      </div>

      {/* Form */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-700 mb-6">Farm Parameters</h2>
        <div className="grid md:grid-cols-3 gap-5">

          {/* Crop parameters */}
          <div>
            <label>Crop Type</label>
            <select name="crop_type_encoded" value={form.crop_type_encoded} onChange={handleChange}>
              {CROP_TYPES.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label>Panel Shading (% of crop area)</label>
            <input type="number" name="shading_pct" value={form.shading_pct} onChange={handleChange} min={0} max={100} />
          </div>
          <div>
            <label>Panel Tilt (degrees)</label>
            <input type="number" name="panel_tilt" value={form.panel_tilt} onChange={handleChange} min={0} max={90} />
          </div>
          <div>
            <label>Temperature (°C)</label>
            <input type="number" name="temperature" value={form.temperature} onChange={handleChange} />
          </div>
          <div>
            <label>Soil Moisture (%)</label>
            <input type="number" name="soil_moisture" value={form.soil_moisture} onChange={handleChange} min={0} max={100} />
          </div>
          <div>
            <label>Rainfall (mm)</label>
            <input type="number" name="rainfall" value={form.rainfall} onChange={handleChange} />
          </div>

          {/* Solar parameters */}
          <div>
            <label>Latitude</label>
            <input type="number" name="latitude" value={form.latitude} onChange={handleChange} step={0.01} />
          </div>
          <div>
            <label>Longitude</label>
            <input type="number" name="longitude" value={form.longitude} onChange={handleChange} step={0.01} />
          </div>
          <div>
            <label>Number of Solar Panels</label>
            <input type="number" name="panel_count" value={form.panel_count} onChange={handleChange} />
          </div>
          <div>
            <label>Panel Watt Peak (W)</label>
            <input type="number" name="panel_watt_peak" value={form.panel_watt_peak} onChange={handleChange} />
          </div>

          {/* Irrigation parameters */}
          <div>
            <label>Rainfall Last 24h (mm)</label>
            <input type="number" name="rainfall_last_24h" value={form.rainfall_last_24h} onChange={handleChange} />
          </div>
          <div>
            <label>Time of Day (0–23)</label>
            <input type="number" name="time_of_day" value={form.time_of_day} onChange={handleChange} min={0} max={23} />
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn-primary mt-6 w-full text-lg disabled:opacity-50"
        >
          {loading ? '⏳ Running Models...' : '🚀 Run All Predictions'}
        </button>

        {error && (
          <p className="mt-4 text-red-500 text-sm bg-red-50 p-3 rounded-lg">{error}</p>
        )}
      </div>

      {/* Results */}
      {cropResult && (
        <div className="card border border-green-300 bg-green-50">
          <h2 className="text-lg font-semibold text-green-800 mb-4">🌾 Crop Yield Prediction</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-gray-500 text-sm">Predicted Yield</p>
              <p className="text-3xl font-bold text-green-700">
                {cropResult.predicted_yield_kg_per_hectare.toLocaleString()}
              </p>
              <p className="text-sm text-gray-500">kg / hectare</p>
            </div>
            <div className="text-center">
              <p className="text-gray-500 text-sm">Land Equivalent Ratio</p>
              <p className="text-3xl font-bold text-yellow-600">{cropResult.land_equivalent_ratio}</p>
              <p className="text-sm text-gray-500">LER (target &gt; 1.0)</p>
            </div>
            <div className="flex items-center">
              <div className="bg-white rounded-xl p-4 text-sm text-gray-700 shadow-sm">
                💡 {cropResult.recommendation}
              </div>
            </div>
          </div>
        </div>
      )}

      {solarResult && (
        <div>
          <SolarChart forecast={solarResult.forecast_7_days} />
          <div className="grid md:grid-cols-2 gap-4 mt-4">
            <div className="card text-center border border-yellow-200">
              <p className="text-gray-500 text-sm">Total (7 days)</p>
              <p className="text-3xl font-bold text-yellow-600">{solarResult.total_kwh}</p>
              <p className="text-sm text-gray-500">kWh</p>
            </div>
            <div className="card text-center border border-yellow-200">
              <p className="text-gray-500 text-sm">Daily Average</p>
              <p className="text-3xl font-bold text-yellow-600">{solarResult.avg_daily_kwh}</p>
              <p className="text-sm text-gray-500">kWh/day</p>
            </div>
          </div>
        </div>
      )}

      {irrigationResult && <IrrigationPanel result={irrigationResult} />}
    </div>
  )
}
