import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, LoginForm } from '../types'
import apiService from '../services/api'
import toast from 'react-hot-toast'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (credentials: LoginForm) => Promise<void>
  logout: () => void
  isAdmin: () => boolean
  isStaff: () => boolean
  toggleDarkMode: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on app load
    const token = localStorage.getItem('access_token')
    if (token) {
      apiService
        .getCurrentUser()
        .then((userData) => {
          setUser(userData)
          // Apply dark mode based on user preference
          if (userData.dark_mode) {
            document.documentElement.classList.add('dark')
          } else {
            document.documentElement.classList.remove('dark')
          }
        })
        .catch(() => {
          // Token is invalid, remove it
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (credentials: LoginForm) => {
    try {
      const response = await apiService.login(credentials)

      // Store tokens
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)

      // Get user info
      const user = await apiService.getCurrentUser()
      setUser(user)

      toast.success('Successfully logged in!')
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    toast.success('Successfully logged out')
  }

  const isAdmin = () => {
    return user?.role === 'admin'
  }

  const isStaff = () => {
    return user?.role === 'staff'
  }

  const toggleDarkMode = async () => {
    if (!user) return

    const newDarkMode = !user.dark_mode
    const previousDarkMode = user.dark_mode

    // Optimistically update the UI immediately
    setUser({ ...user, dark_mode: newDarkMode })

    // Apply dark mode to document immediately
    if (newDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }

    try {
      // Update on server
      const updatedUser = await apiService.updateDarkMode(newDarkMode)
      setUser(updatedUser)
      toast.success(`Dark mode ${newDarkMode ? 'enabled' : 'disabled'}`)
    } catch (error) {
      console.error('Failed to toggle dark mode:', error)

      // Rollback on failure
      setUser({ ...user, dark_mode: previousDarkMode })

      // Revert dark mode to document
      if (previousDarkMode) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }

      toast.error('Failed to toggle dark mode')
    }
  }

  const value = {
    user,
    loading,
    login,
    logout,
    isAdmin,
    isStaff,
    toggleDarkMode,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}