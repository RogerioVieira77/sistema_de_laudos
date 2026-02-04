import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

/**
 * Callback Page
 * Handles OAuth callback after Keycloak login
 */
const Callback = () => {
  const navigate = useNavigate()
  const { handleCallback, isLoading, error } = useAuth()

  useEffect(() => {
    const processCallback = async () => {
      try {
        await handleCallback()
        // Redirect to home on success
        navigate('/')
      } catch (err) {
        console.error('Callback error:', err)
        // Redirect to login on error
        navigate('/login')
      }
    }

    if (!isLoading) {
      processCallback()
    }
  }, [isLoading, handleCallback, navigate])

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      flexDirection: 'column',
      gap: '1rem',
    }}>
      <h1>Processando login...</h1>
      {error && <p style={{ color: '#dc2626' }}>Erro: {error}</p>}
    </div>
  )
}

export default Callback
