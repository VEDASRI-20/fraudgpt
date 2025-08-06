import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';

import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';

import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import FlaggedTransactions from './pages/FlaggedTransactions';
import Analysis from './pages/Analysis';

import { FiMenu, FiX } from 'react-icons/fi';


const App = () => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  const renderLayout = (children) => {
    const { pathname } = location;

    if (pathname === '/') {
      return <>{children}</>; // Landing page
    }

    if (pathname === '/login' || pathname === '/signup') {
      return <div>{children}</div>;
    }

    return (
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        {sidebarOpen && (
          <div style={{ position: 'fixed', width: '240px', height: '100vh', zIndex: 10 }}>
            <Sidebar />
          </div>
        )}

        <div style={{
          marginLeft: sidebarOpen ? '240px' : '0',
          transition: 'margin-left 0.3s ease',
          flexGrow: 1,
          width: '100%',
          padding: '20px'
        }}>
        <button
          onClick={toggleSidebar}
          style={{
            marginBottom: '20px',
            marginLeft: '30px',
            padding: '8px 12px',
            backgroundColor: '#0c031b',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '18px'
          }}
        >
          {sidebarOpen ? <FiX /> : <FiMenu />}
        </button>

          {children}
        </div>
      </div>
    );
  };

  return renderLayout(
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/flagged" element={<FlaggedTransactions />} />
      <Route path="/analysis" element={<Analysis />} />
      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
};

export default function WrappedApp() {
  return (
    <Router>
      <App />
    </Router>
  );
}
