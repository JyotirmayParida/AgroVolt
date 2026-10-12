export default function WeatherCard({ data }) {
  if (!data) return null

  return (
    <div className="card border border-blue-200 bg-blue-50">
      <h3 className="text-lg font-semibold text-blue-700 mb-3">🌤️ Current Weather</h3>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-gray-500">Temperature</p>
          <p className="font-bold text-xl">{data.temperature}°C</p>
        </div>
        <div>
          <p className="text-gray-500">Humidity</p>
          <p className="font-bold text-xl">{data.humidity}%</p>
        </div>
        <div>
          <p className="text-gray-500">Rainfall (last hr)</p>
          <p className="font-bold text-xl">{data.rainfall} mm</p>
        </div>
        <div>
          <p className="text-gray-500">Wind Speed</p>
          <p className="font-bold text-xl">{data.wind_speed} m/s</p>
        </div>
      </div>
      <p className="mt-3 text-blue-600 text-sm">{data.description}</p>
    </div>
  )
}
