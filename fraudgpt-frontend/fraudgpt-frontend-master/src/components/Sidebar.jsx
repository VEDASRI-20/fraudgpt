import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = ({ isOpen, toggleSidebar, theme }) => {
  const isDark = theme === 'dark';

  return (
    <>
    {isOpen && (
      <div
        onClick={toggleSidebar}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          height: '100vh',
          width: '100vw',
          backgroundColor: 'rgba(0, 0, 0, 0)',
          zIndex: 999,
        }}
      />
    )}
      <div
        style={{
          position: 'fixed',
          top: 0,
          width: '240px',
          height: '100vh',
          color: isDark ? 'white' : '#111',
          backgroundColor: isDark ? '#0c031b' : '#f8fafc',
          padding: '20px',
          transition: 'left 0.3s ease',
          zIndex: 1000,
          borderRight: `1px solid ${
              isDark ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)'
            }`
        }}
      >
        <h2 style={{ fontSize: '20px', marginBottom: '30px' }}>FraudNix</h2>
        <NavLink to="/dashboard" style={(props) => linkStyle(props, isDark)}>Transactions</NavLink>
        <NavLink to="/flagged" style={(props) => linkStyle(props, isDark)}>Flagged</NavLink>
        <NavLink to="/analysis" style={(props) => linkStyle(props, isDark)}>Analysis</NavLink>
      </div>
    </>
  );
};

const linkStyle = ({ isActive }, isDark) => ({
  display: 'block',
  padding: '12px 16px',
  marginBottom: '10px',
  color: isActive ? (isDark ? '#fff' : '#fff') : (isDark ? '#cbd5e1' : '#111'),
  backgroundColor: isActive ? (isDark ? '#0c031b' : '#2563eb') : 'transparent',
  borderRadius: '6px',
  textDecoration: 'none',
  fontWeight: 500,
  fontFamily: 'Segoe UI',
});

export default Sidebar;
