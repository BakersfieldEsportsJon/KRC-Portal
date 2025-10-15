import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { AuthProvider, useAuth } from './hooks/useAuth'
import Layout from './components/Layout'
import KioskLayout from './components/KioskLayout'
import LoadingScreen from './components/LoadingScreen'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ClientsPage from './pages/ClientsPage'
import ClientDetailPage from './pages/ClientDetailPage'
import CheckInsPage from './pages/CheckInsPage'
import AdminPage from './pages/AdminPage'
import KioskPage from './pages/KioskPage'
import NotFoundPage from './pages/NotFoundPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingScreen />
  }

  if (!user) {
    return <Navigate to="/login" replace />
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