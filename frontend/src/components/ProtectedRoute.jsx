import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth, useUserRoles } from '../contexts/AuthContext'

/**
 * ProtectedRoute Component
 * Protects routes that require authentication
 * Optionally checks for specific roles
 */
export const ProtectedRoute = ({ element, requiredRoles = [] }) => {
  const { isAuthenticated, isLoading } = useAuth()
  const userRoles = useUserRoles()

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
      }}>
        <div>Carregando...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Check if user has required roles
  if (requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.some((role) =>
      userRoles.includes(role)
    )

    if (!hasRequiredRole) {
      return (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          flexDirection: 'column',
          gap: '1rem',
        }}>
          <h1>Acesso Negado</h1>
          <p>Você não tem permissão para acessar esta página.</p>
          <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
            Roles necessárias: {requiredRoles.join(', ')}
          </p>
          <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
            Seus roles: {userRoles.join(', ') || 'nenhum'}
          </p>
        </div>
      )
    }
  }

  return element
}

export default ProtectedRoute
