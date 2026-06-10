import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';

export default function App() {
  return (
    <Router>
      <Toaster
        position="top-right"
        gutter={8}
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1e2433',
            color: '#e2e8f0',
            fontSize: '13px',
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            fontWeight: '500',
            borderRadius: '12px',
            padding: '12px 16px',
            border: '1px solid rgba(255,255,255,0.07)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.4), 0 1px 0 rgba(255,255,255,0.05) inset',
          },
          success: {
            iconTheme: { primary: '#10b981', secondary: '#1e2433' },
          },
          error: {
            iconTheme: { primary: '#e8184a', secondary: '#1e2433' },
          },
        }}
      />
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </Layout>
    </Router>
  );
}
