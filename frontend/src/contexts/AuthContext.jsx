import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { UserManager, WebStorageStateStore, Log } from 'oidc-client-ts'

// Create Auth Context
const AuthContext = createContext(null)

/**
 * OIDCAuthProvider - Provides OIDC authentication to the app
 * Manages user session, tokens, and authentication state
 */
export const OIDCAuthProvider = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState(null)
  const [error, setError] = useState(null)
  const [userManager, setUserManager] = useState(null)

  // Initialize OIDC UserManager on component mount
  useEffect(() => {
    const initializeOIDC = async () => {
      try {
        // Enable logging for development
        if (import.meta.env.DEV) {
          Log.setLogger(console)
          Log.setLevel(Log.DEBUG)
        }

        const settings = {
          authority: import.meta.env.VITE_KEYCLOAK_URL,
          client_id: import.meta.env.VITE_KEYCLOAK_CLIENT_ID,
          client_secret: import.meta.env.VITE_KEYCLOAK_CLIENT_SECRET,
          redirect_uri: `${window.location.origin}/callback`,
          post_logout_redirect_uri: `${window.location.origin}/`,
          response_type: 'code',
          scope: 'openid profile email roles',
          userStore: new WebStorageStateStore({ store: window.localStorage }),
          automaticSilentRenew: true,
          silent_redirect_uri: `${window.location.origin}/silent-renew.html`,
          filterProtocolClaims: true,
          loadUserInfo: true,
          revokeAccessTokenOnSignout: true,
        }

        const manager = new UserManager(settings)

        // Handle successful sign-in
        manager.events.addUserLoaded((user) => {
          console.log('✅ User loaded:', user.profile.email)
          setUser(user)
          setError(null)
        })

        // Handle token expiry
        manager.events.addAccessTokenExpiring(() => {
          console.warn('⚠️ Access token expiring soon, refreshing...')
        })

        // Handle silent renew error
        manager.events.addAccessTokenExpired(() => {
          console.warn('⚠️ Access token expired, please login again')
          setError('Session expired. Please login again.')
        })

        // Handle sign-out
        manager.events.addUserUnloaded(() => {
          console.log('✅ User signed out')
          setUser(null)
        })

        // Handle errors
        manager.events.addErrorEvent((error) => {
          console.error('❌ OIDC Error:', error.error, error.error_description)
          setError(error.error_description || 'Authentication error occurred')
        })

        setUserManager(manager)

        // Try to restore existing session
        const existingUser = await manager.getUser()
        if (existingUser && !existingUser.expired) {
          setUser(existingUser)
          console.log('✅ Session restored from storage')
        } else if (existingUser && existingUser.expired) {
          console.log('⚠️ Stored session expired')
          await manager.removeUser()
          setUser(null)
        }

        setIsLoading(false)
      } catch (err) {
        console.error('❌ OIDC initialization error:', err)
        setError(err.message)
        setIsLoading(false)
      }
    }

    initializeOIDC()
  }, [])

  // Login with redirect to Keycloak
  const login = useCallback(async () => {
    if (!userManager) {
      setError('OIDC not initialized')
      return
    }
    try {
      await userManager.signinRedirect()
    } catch (err) {
      console.error('❌ Login error:', err)
      setError('Failed to initiate login')
    }
  }, [userManager])

  // Handle callback after login
  const handleCallback = useCallback(async () => {
    if (!userManager) {
      setError('OIDC not initialized')
      return
    }
    try {
      const user = await userManager.signinRedirectCallback()
      setUser(user)
      setError(null)
      console.log('✅ Callback handled, user authenticated')
      return user
    } catch (err) {
      console.error('❌ Callback error:', err)
      setError('Failed to process login callback')
      throw err
    }
  }, [userManager])

  // Logout with redirect
  const logout = useCallback(async () => {
    if (!userManager) {
      setError('OIDC not initialized')
      return
    }
    try {
      setUser(null)
      await userManager.signoutRedirect()
    } catch (err) {
      console.error('❌ Logout error:', err)
      setError('Failed to logout')
    }
  }, [userManager])

  // Silent renew (called periodically)
  const renewToken = useCallback(async () => {
    if (!userManager) {
      return
    }
    try {
      const newUser = await userManager.signinSilent()
      if (newUser) {
        setUser(newUser)
        console.log('✅ Token renewed silently')
      }
    } catch (err) {
      console.error('⚠️ Silent renew failed:', err)
      // This is expected when user is not logged in
    }
  }, [userManager])

  // Get access token
  const getAccessToken = useCallback(() => {
    return user?.access_token || null
  }, [user])

  // Get user roles from ID token
  const getUserRoles = useCallback(() => {
    if (!user) return []
    // Roles are typically in realm_access.roles or resource_access
    const roles = user.profile?.realm_access?.roles || []
    return roles.filter((role) => !role.startsWith('default-'))
  }, [user])

  // Check if user has specific role
  const hasRole = useCallback(
    (role) => {
      return getUserRoles().includes(role)
    },
    [getUserRoles]
  )

  // Check if user is authenticated
  const isAuthenticated = !!user && !user.expired

  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    handleCallback,
    renewToken,
    getAccessToken,
    getUserRoles,
    hasRole,
    userManager,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Hook to use Auth Context
 */
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within OIDCAuthProvider')
  }
  return context
}

/**
 * Hook for getting current user
 */
export const useUser = () => {
  const { user } = useAuth()
  return user?.profile || null
}

/**
 * Hook for getting user roles
 */
export const useUserRoles = () => {
  const { getUserRoles } = useAuth()
  return getUserRoles()
}

/**
 * Hook to check if user has role
 */
export const useHasRole = (role) => {
  const { hasRole } = useAuth()
  return hasRole(role)
}
