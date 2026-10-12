import { useState } from 'react'
import { createFarm } from '../api/axiosClient'
import { getErrorMessage } from '../api/errorHandler'
import useStore from '../store/useStore'

export default function Settings() {
  const { farms, setFarms } = useStore()
  const [success, setSuccess] = useState(false)
  const [error,   setError]   = useState(null)
  const [loading, setLoading] = useState(false)

  const [form, setForm] = useState({
    name:           '',
    location:       '',
    latitude:       20.29,
    longitude:      85.82,
    panel_count:    50,
    crop_type:      'Wheat',
    area_hectares:  2.5,
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async () => {
    if (!form.name || !form.location) {
      setError('Farm name and location are required.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await createFarm({
        ...form,
        latitude:      parseFloat(form.latitude),
        longitude:     parseFloat(form.longitude),
        panel_count:   parseInt(form.panel_count),
        area_hectares: parseFloat(form.area_hectares),
      })
      setFarms([...farms, res.data])
      setSuccess(true)
      setForm({ name: '', location: '', latitude: 20.29, longitude: 85.82,
                panel_count: 50, crop_type: 'Wheat', area_hectares: 2.5 })
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to add farm. Please verify backend connection.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-green-800">⚙️ Settings</h1>
        <p className="text-gray-500 mt-1">Add and manage your agrovoltaic farms.</p>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-gray-700 mb-6">Add New Farm</h2>
        <div className="grid md:grid-cols-2 gap-5">
          <div>
            <label>Farm Name</label>
            <input name="name" value={form.name} onChange={handleChange} placeholder="e.g. Sunrise Farm" />
          </div>
          <div>
            <label>Location</label>
            <input name="location" value={form.location} onChange={handleChange} placeholder="e.g. Bhubaneswar, Odisha" />
          </div>
          <div>
            <label>Latitude</label>
            <input type="number" name="latitude" value={form.latitude} onChange={handleChange} step={0.01} />
          </div>
          <div>
            <label>Longitude</label>
            <input type="number" name="longitude" value={form.longitude} onChange={handleChange} step={0.01} />
          </div>
          <div>
            <label>Crop Type</label>
            <select name="crop_type" value={form.crop_type} onChange={handleChange}>
              {['Wheat', 'Rice', 'Vegetables', 'Berries'].map(c => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label>Number of Solar Panels</label>
            <input type="number" name="panel_count" value={form.panel_count} onChange={handleChange} />
          </div>
          <div>
            <label>Area (hectares)</label>
            <input type="number" name="area_hectares" value={form.area_hectares} onChange={handleChange} step={0.1} />
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn-primary mt-6 disabled:opacity-50"
        >
          {loading ? 'Adding...' : '+ Add Farm'}
        </button>

        {success && <p className="mt-3 text-green-600 font-medium">✅ Farm added successfully!</p>}
        {error   && <p className="mt-3 text-red-500 text-sm">{error}</p>}
      </div>

      {/* Farms list */}
      {farms.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Registered Farms</h2>
          <div className="space-y-3">
            {farms.map(farm => (
              <div key={farm.id} className="flex justify-between items-center bg-green-50 rounded-xl p-4">
                <div>
                  <p className="font-semibold text-green-800">{farm.name}</p>
                  <p className="text-sm text-gray-500">{farm.location} · {farm.crop_type} · {farm.panel_count} panels</p>
                </div>
                <span className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-full">
                  {farm.area_hectares} ha
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
