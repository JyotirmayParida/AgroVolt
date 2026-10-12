import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Predict from './pages/Predict'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-green-50">
        <Navbar />
        <main className="max-w-6xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/"          element={<Home />} />
            <Route path="/predict"   element={<Predict />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings"  element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
