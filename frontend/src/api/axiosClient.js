import axios from 'axios'

const getBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL

  if (envUrl && envUrl.trim()) {
    const trimmed = envUrl.trim().replace(/\/+$/, '')
    return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`
  }

  if (import.meta.env.DEV) {
    return 'http://localhost:8000/api'
  }

  // In production, never silently fall back to localhost
  console.error('VITE_API_URL environment variable is not defined in production.')
  return ''
}

const api = axios.create({
  baseURL: getBaseUrl(),
  headers: { 'Content-Type': 'application/json' },
})

// ─── Crop ─────────────────────────────────────────────────────────────────
export const predictCropYield = (data) => api.post('/crop/predict', data)
export const getCropTypes     = ()     => api.get('/crop/crop-types')

// ─── Solar ────────────────────────────────────────────────────────────────
export const getSolarForecast = (data) => api.post('/solar/forecast', data)

// ─── Irrigation ───────────────────────────────────────────────────────────
export const getIrrigationRecommendation = (data) => api.post('/irrigation/recommend', data)

// ─── Weather ──────────────────────────────────────────────────────────────
export const getWeather = (lat, lon) => api.get(`/weather/${lat}/${lon}`)

// ─── Farms ────────────────────────────────────────────────────────────────
export const getFarms         = ()           => api.get('/farms/')
export const createFarm       = (data)       => api.post('/farms/', data)
export const getFarmPredictions = (farmId)   => api.get(`/farms/${farmId}/predictions`)

export default api
