import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { AuthProvider, useAuth } from './hooks/useAuth'
import Layout from './components/Layout'
import KioskLayout from './components/KioskLayout'
import LoadingScreen from './components/LoadingScreen'
import LoginPage from './pages/LoginPage'
import PasswordSetupPage from './pages/PasswordSetupPage'
import ChangePasswordPage from './pages/ChangePasswordPage'
import DashboardPage from './pages/DashboardPage'
import ClientsPage from './pages/ClientsPage'
import ClientDetailPage from './pages/ClientDetailPage'
import CheckInsPage from './pages/CheckInsPage'
import AdminPage from './pages/AdminPage'
import KioskPage from './pages/KioskPage'
import NotFoundPage from './pages/NotFoundPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const location = window.location.pathname

  if (loading) {
    return <LoadingScreen />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  // If user needs to change password and not already on change-password page
  if (user.password_setup_required && location !== '/change-password') {
    return <Navigate to="/change-password" replace />
  }

  // If user is on change-password page but doesn't need to change password
  if (!user.password_setup_required && location === '/change-password') {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

function AppRoutes() {
  const [isKioskMode, setIsKioskMode] = useState(false)

  useEffect(() => {
    // Detect if we're on the kiosk subdomain or path
    const hostname = window.location.hostname
    const pathname = window.location.pathname
    setIsKioskMode(hostname.startsWith('kiosk.') || pathname.startsWith('/kiosk'))
  }, [])

  if (isKioskMode) {
    return (
      <KioskLayout>
        <Routes>
          <Route path="/kiosk" element={<KioskPage />} />
          <Route path="/" element={<Navigate to="/kiosk" replace />} />
          <Route path="*" element={<Navigate to="/kiosk" replace />} />
        </Routes>
      </KioskLayout>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/setup-password" element={<PasswordSetupPage />} />
      <Route path="/change-password" element={
        <ProtectedRoute>
          <ChangePasswordPage />
        </ProtectedRoute>
      } />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="clients" element={<ClientsPage />} />
        <Route path="clients/:id" element={<ClientDetailPage />} />
        <Route path="checkins" element={<CheckInsPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}

export default App