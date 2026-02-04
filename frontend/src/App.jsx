import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { OIDCAuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Callback from './pages/Callback'
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
        <OIDCAuthProvider>
          <Notifications />
          <Routes>
            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/callback" element={<Callback />} />

            {/* Protected Routes */}
            <Route path="/" element={<ProtectedRoute element={<Home />} />} />
            <Route path="/upload" element={<ProtectedRoute element={<Upload />} />} />
            <Route path="/contratos" element={<ProtectedRoute element={<Contratos />} />} />
            <Route path="/map" element={<ProtectedRoute element={<Map />} />} />
            <Route path="/resultado/:id" element={<ProtectedRoute element={<Resultado />} />} />

            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </OIDCAuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
