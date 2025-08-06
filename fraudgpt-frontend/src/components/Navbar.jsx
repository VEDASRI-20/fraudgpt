import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav style={{
      height: '60px',
      background: 'linear-gradient(135deg, #0c031b 0%, #1f1147 100%)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 20px',
      fontWeight: 'bold',
      fontSize: '1.5rem',
      fontFamily: 'gill sans, sans-serif',
    }}>
      <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none' }}>
        FraudNix
      </Link>
    </nav>
  );
};

export default Navbar;
