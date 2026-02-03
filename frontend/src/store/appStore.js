import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

/**
 * App Store - Manages global app state
 * For notifications, modals, global loading, etc.
 */
const useAppStore = create(
  devtools((set, get) => ({
    // Notifications
    notifications: [],

    // Add notification
    addNotification: (notification) => {
      const id = Date.now()
      const newNotification = {
        id,
        duration: 5000,
        ...notification,
      }

      set((state) => ({
        notifications: [...state.notifications, newNotification],
      }))

      // Auto-remove after duration
      if (newNotification.duration) {
        setTimeout(() => {
          get().removeNotification(id)
        }, newNotification.duration)
      }

      return id
    },

    // Remove notification
    removeNotification: (id) => {
      set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id),
      }))
    },

    // Clear all notifications
    clearNotifications: () => {
      set({ notifications: [] })
    },

    // Modal state
    modal: null,

    // Open modal
    openModal: (modal) => {
      set({ modal })
    },

    // Close modal
    closeModal: () => {
      set({ modal: null })
    },

    // Global loading
    isLoading: false,
    setIsLoading: (isLoading) => {
      set({ isLoading })
    },

    // Sidebar state
    sidebarOpen: true,
    toggleSidebar: () => {
      set((state) => ({
        sidebarOpen: !state.sidebarOpen,
      }))
    },

    // Theme
    theme: localStorage.getItem('theme') || 'light',
    setTheme: (theme) => {
      localStorage.setItem('theme', theme)
      set({ theme })
    },

    // Helper functions
    showSuccess: (message, duration = 5000) => {
      return get().addNotification({
        type: 'success',
        message,
        duration,
      })
    },

    showError: (message, duration = 7000) => {
      return get().addNotification({
        type: 'error',
        message,
        duration,
      })
    },

    showWarning: (message, duration = 6000) => {
      return get().addNotification({
        type: 'warning',
        message,
        duration,
      })
    },

    showInfo: (message, duration = 5000) => {
      return get().addNotification({
        type: 'info',
        message,
        duration,
      })
    },
  }))
)

export default useAppStore
