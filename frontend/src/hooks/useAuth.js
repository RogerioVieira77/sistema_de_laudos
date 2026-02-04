import { useEffect, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'

/**
 * useTokenRefresh - Hook to automatically refresh token before expiration
 * Calls renewToken at intervals to keep session alive
 */
export const useTokenRefresh = (intervalMs = 10000) => {
  const { renewToken, isAuthenticated } = useAuth()
  const intervalRef = useRef(null)

  useEffect(() => {
    if (!isAuthenticated) {
      return
    }

    // Start token refresh interval
    intervalRef.current = setInterval(() => {
      renewToken()
    }, intervalMs)

    // Cleanup interval on unmount or when auth state changes
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isAuthenticated, renewToken, intervalMs])

  return null
}

/**
 * useRequestInterceptor - Hook to add auth token to API requests
 * Automatically adds Authorization header to axios requests
 */
export const useRequestInterceptor = (axiosInstance) => {
  const { getAccessToken } = useAuth()

  useEffect(() => {
    const requestInterceptor = axiosInstance.interceptors.request.use(
      (config) => {
        const token = getAccessToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    return () => {
      axiosInstance.interceptors.request.eject(requestInterceptor)
    }
  }, [getAccessToken, axiosInstance])
}

export default useTokenRefresh
