import React from 'react';
import { Link } from 'react-router-dom';
import './Landing.css';

const Landing = () => {
  return (
    <div className="landing-container">
      <div className="glow-bg"></div>

      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">FraudNix</div>

        <Link to="/signup" className="cta-button">Get Started</Link>
      </nav>

      {/* Main content split into left (hero) and right (cards) */}
      <div className="main-content">
        <div className="content-wrapper">

        {/* Hero Section */}
          <div className="hero">
            <p className="tagline">The new AI-powered fraud shield</p>
            <h1 className="hero-title">
              Accelerate Your <br />
              <span className="highlight">Fraud Intelligence</span>
            </h1>
            <p className="hero-subtitle">
              Real-time fraud detection, tailored for your business. Stay ahead, stay secure.
            </p>
            <div className="hero-buttons">
              <Link to="/login" className="login-button">Login</Link>
              <Link to="/signup" className="signup-button">Signup</Link>
            </div>
          </div>

        {/* Floating Cards */}
        <div className="cards-container">
          <div className="card">AI Analyst</div>
          <div className="card">Live Model Output</div>
          <div className="card">Explainability Firewall</div>
          <div className="card">Live WebSocket Alerts</div>
          <div className="card">Fraud Score</div>
          <div className="card">Analyst Dashboard</div>
        </div>
        </div>

      </div>
    </div>
  );
};

export default Landing;
