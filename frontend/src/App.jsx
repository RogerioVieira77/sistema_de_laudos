import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Upload from './pages/Upload'
import Contratos from './pages/Contratos'
import Map from './pages/Map'
import Resultado from './pages/Resultado'
import NotFound from './pages/NotFound'
import ErrorBoundary from './components/ErrorBoundary'
import Notifications from './components/Notifications'
import './App.css'

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Notifications />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/contratos" element={<Contratos />} />
          <Route path="/map" element={<Map />} />
          <Route path="/resultado/:id" element={<Resultado />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
