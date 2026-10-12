import { Link, useLocation } from 'react-router-dom'

const links = [
  { to: '/',          label: '🏠 Dashboard' },
  { to: '/predict',   label: '🔮 Predict' },
  { to: '/analytics', label: '📊 Analytics' },
  { to: '/settings',  label: '⚙️ Settings' },
]

export default function Navbar() {
  const { pathname } = useLocation()

  return (
    <nav className="bg-green-700 text-white shadow-lg">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🌱</span>
          <span className="text-xl font-bold tracking-tight">AgroVolt</span>
          <span className="text-xs bg-green-500 px-2 py-0.5 rounded-full">Smart Agrovoltaic System</span>
        </div>
        <div className="flex gap-2">
          {links.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition
                ${pathname === to
                  ? 'bg-white text-green-700'
                  : 'hover:bg-green-600'}`}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}
