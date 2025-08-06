import React from 'react';
import { FiMenu, FiX, FiLogOut } from 'react-icons/fi';
import './Navbar.css';

const Navbar = ({ sidebarOpen, toggleSidebar, handleLogout }) => {
  return (
    <div className="navbar">
      <button className="sidebar-toggle" onClick={toggleSidebar}>
        {sidebarOpen ? <FiX /> : <FiMenu />}
      </button>
      <h1 className="navbar-title">FraudGPT</h1>
      <button className="logout-btn" onClick={handleLogout}>
        <FiLogOut />
      </button>
    </div>
  );
};

export default Navbar;
