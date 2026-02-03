import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { getUser, setTokens, clearTokens, isAuthenticated } from '../services/api'

/**
 * Auth Store - Manages authentication state globally
 * Persists to localStorage for session recovery
 */
const useAuthStore = create(
  devtools(
    persist(
      (set, get) => ({
        // State
        user: getUser(),
        isAuthenticated: isAuthenticated(),
        isLoading: false,
        error: null,

        // Actions - Set user after login
        setUser: (user, accessToken, refreshToken) => {
          setTokens(accessToken, refreshToken, user)
          set({
            user,
            isAuthenticated: true,
            error: null,
          })
        },

        // Logout - Clear user and tokens
        logout: () => {
          clearTokens()
          set({
            user: null,
            isAuthenticated: false,
            error: null,
          })
        },

        // Check authentication status
        checkAuth: () => {
          const authenticated = isAuthenticated()
          const user = getUser()
          set({
            isAuthenticated: authenticated,
            user: authenticated ? user : null,
          })
          return authenticated
        },

        // Set loading state
        setLoading: (isLoading) => {
          set({ isLoading })
        },

        // Set error
        setError: (error) => {
          set({ error })
        },

        // Clear error
        clearError: () => {
          set({ error: null })
        },

        // Update user info
        updateUser: (updates) => {
          const currentUser = get().user
          const updatedUser = { ...currentUser, ...updates }
          set({ user: updatedUser })
          localStorage.setItem('user', JSON.stringify(updatedUser))
        },
      }),
      {
        name: 'auth-store', // localStorage key
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }), // only persist these fields
      }
    )
  )
)

export default useAuthStore
