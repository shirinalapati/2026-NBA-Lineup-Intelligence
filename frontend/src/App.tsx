import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { Leaderboard } from './pages/Leaderboard'
import { TeamExplorer } from './pages/TeamExplorer'
import { Underrated } from './pages/Underrated'
import { Simulator } from './pages/Simulator'
import { AboutProject } from './pages/AboutProject'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<AboutProject />} />
        <Route path="/about" element={<Navigate to="/" replace />} />
        <Route path="/overview" element={<Home />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/explorer" element={<TeamExplorer />} />
        <Route path="/underrated" element={<Underrated />} />
        <Route path="/simulator" element={<Simulator />} />
        <Route path="/methodology" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
