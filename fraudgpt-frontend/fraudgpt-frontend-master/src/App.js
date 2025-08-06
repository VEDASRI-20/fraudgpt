import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import FlaggedTransactions from './pages/FlaggedTransactions';
import Analysis from './pages/Analysis';

import { FiMenu, FiX, FiLogOut, FiSun, FiMoon } from 'react-icons/fi';

const App = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState('dark'); // dark or light

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const handleLogout = () => navigate('/');
  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  const renderLayout = (children) => {
    const { pathname } = location;

    // Pages without navbar/sidebar
    if (pathname === '/' || pathname === '/login' || pathname === '/signup') {
      return <div>{children}</div>;
    }

    const isDark = theme === 'dark';

    // Colors for themes
    const navbarBg = isDark ? '#231c3f' : '#ffffff';
    const sidebarBg = isDark ? '#1e1b2e' : '#f0f0f0';
    const textColor = isDark ? '#ffffff' : '#000000';
    const pageBg = isDark ? '#0c031b' : '#f9f9f9';

    // Table styling injection
    const tableStyles = document.createElement('style');
    tableStyles.innerHTML = `
      .dashboard-table thead th {
        background-color: ${isDark ? '#1e1b2e' : '#e6e6e6'};
        color: ${isDark ? '#cbd5e1' : '#333'};
      }
      .dashboard-table tbody td {
        background-color: ${isDark ? '#16122b' : '#ffffff'};
        color: ${isDark ? '#e2e8f0' : '#222'};
      }
      .dashboard-table tbody tr:hover td {
        background-color: ${isDark ? '#231c3f' : '#f2f2f2'};
      }
    `;
    const existingStyle = document.getElementById('dynamic-theme');
    if (existingStyle) existingStyle.remove();
    tableStyles.id = 'dynamic-theme';
    document.head.appendChild(tableStyles);

    return (
      <div style={{ minHeight: '100vh', backgroundColor: pageBg, color: textColor }}>
        {/* Navbar */}
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0, // use right instead of width to avoid overflow
            height: '60px',
            background: navbarBg,
            color: textColor,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 20px',
            boxSizing: 'border-box', // ensures padding doesn’t add to width
            zIndex: 100,
            fontFamily: 'Outfit, sans-serif',
            fontWeight: '600',
            fontSize: '20px',
            borderBottom: `1px solid ${
              isDark ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
            }`,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={toggleSidebar}
              style={{
                background: 'transparent',
                border: 'none',
                color: textColor,
                fontSize: '24px',
                cursor: 'pointer',
              }}
            >
              {sidebarOpen ? <FiX /> : <FiMenu />}
            </button>
            FraudNix
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <button
              onClick={toggleTheme}
              style={{
                background: 'transparent',
                border: 'none',
                color: textColor,
                fontSize: '22px',
                cursor: 'pointer',
              }}
              title="Toggle Theme"
            >
              {isDark ? <FiSun /> : <FiMoon />}
            </button>
            <button
              onClick={handleLogout}
              style={{
                background: 'transparent',
                border: 'none',
                color: textColor,
                fontSize: '22px',
                cursor: 'pointer',
              }}
              title="Logout"
            >
              <FiLogOut />
            </button>
          </div>
        </div>

        {/* Sidebar + Content */}
        <div style={{ display: 'flex', paddingTop: '60px', height: 'calc(100vh - 60px)' }}>
          {sidebarOpen && (
            <div
              style={{
                position: 'fixed',
                top: '60px',
                left: 0,
                width: '240px',
                height: 'calc(100vh - 60px)',
                transition: 'transform 0.3s ease',
                zIndex: 10,
                backgroundColor: sidebarBg,
              }}
            >
              <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} theme={theme} />

            </div>
          )}

          <div
            style={{
              marginLeft: sidebarOpen ? '240px' : '0',
              transition: 'margin-left 0.3s ease',
              flexGrow: 1,
              padding: '20px',
              width: '100%',
            }}
          >
            {children}
          </div>
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
