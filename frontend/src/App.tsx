import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Spinner, Center } from '@chakra-ui/react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { AuthPage } from './components/auth/AuthPage'
import { Layout } from './components/layout/Layout'
import { VehicleManagement } from './components/vehicles/VehicleManagement'
import { OrderManagement } from './components/orders/OrderManagement'
import { TripManagement } from './components/trips/TripManagement'
import { Settings } from './components/settings/Settings'
import MapView from './components/maps/MapView'

const AppContent: React.FC = () => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    )
  }

  if (!user) {
    return <AuthPage />
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/map" replace />} />
      <Route
        path="/map"
        element={
          <Layout isFullScreen>
            <MapView />
          </Layout>
        }
      />
      <Route
        path="/trips"
        element={
          <Layout>
            <TripManagement />
          </Layout>
        }
      />
      <Route
        path="/vehicles"
        element={
          <Layout>
            <VehicleManagement />
          </Layout>
        }
      />
      <Route
        path="/orders"
        element={
          <Layout>
            <OrderManagement />
          </Layout>
        }
      />
      <Route
        path="/settings"
        element={
          <Layout>
            <Settings />
          </Layout>
        }
      />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
