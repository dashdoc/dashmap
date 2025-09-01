import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Spinner, Center } from '@chakra-ui/react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AuthPage } from './components/auth/AuthPage';
import { Layout } from './components/layout/Layout';
import { VehicleManagement } from './components/vehicles/VehicleManagement';

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }

  if (!user) {
    return <AuthPage />;
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/map" replace />} />
        <Route path="/map" element={<div>Map Component Coming Soon</div>} />
        <Route path="/trips" element={<div>Trips Component Coming Soon</div>} />
        <Route path="/vehicles" element={<VehicleManagement />} />
        <Route path="/settings" element={<div>Settings Component Coming Soon</div>} />
      </Routes>
    </Layout>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
