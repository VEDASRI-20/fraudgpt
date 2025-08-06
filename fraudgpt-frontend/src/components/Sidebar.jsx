import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = ({ isOpen, toggleSidebar }) => {
  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          onClick={toggleSidebar}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            height: '100vh',
            width: '100vw',
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            zIndex: 999,
          }}
        />
      )}

      {/* Sidebar */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          // left: isOpen ? 0 : '-240px',
          width: '240px',
          height: '100vh',
          color: 'white',
          backgroundColor: '#231c3f',
          padding: '20px',
          transition: 'left 0.3s ease',
          zIndex: 1000,
        }}
      >
        <h2 style={{ fontSize: '20px', marginBottom: '30px', color:'white', }}>FraudNix</h2>
        <NavLink to="/dashboard" style={linkStyle}>Transactions</NavLink>
        <NavLink to="/flagged" style={linkStyle}>Flagged</NavLink>
        <NavLink to="/analysis" style={linkStyle}>Analysis</NavLink>
      </div>
    </>
  );
};

const linkStyle = ({ isActive }) => ({
  display: 'block',
  padding: '12px 16px',
  marginBottom: '10px',
  color: isActive ? '#ffffff' : '#cbd5e1',
  backgroundColor: isActive ? '#0c031b' : 'transparent',
  borderRadius: '6px',
  textDecoration: 'none',
  fontWeight: 500,
  fontFamily: 'Segoe UI',
});

export default Sidebar;
