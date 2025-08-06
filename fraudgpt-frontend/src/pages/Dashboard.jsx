import React, { useEffect, useState } from 'react';
import './Dashboard.css';
// import Navbar from '../components/Navbar';


const Dashboard = ({ sidebarOpen }) => {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    setTransactions([
      { id: 1, amount: 2200, timestamp: "2025-07-31 10:23", fraud_score: 0.84 },
      { id: 2, amount: 399, timestamp: "2025-07-31 10:24", fraud_score: 0.3 },
      { id: 3, amount: 1350, timestamp: "2025-07-31 10:25", fraud_score: 0.91 },
      { id: 4, amount: 1350, timestamp: "2025-07-31 10:26", fraud_score: 0.9 },
      { id: 5, amount: 1350, timestamp: "2025-07-31 10:27", fraud_score: 0.65 },
      { id: 6, amount: 1350, timestamp: "2025-07-31 10:28", fraud_score: 0.2 },
      { id: 7, amount: 1350, timestamp: "2025-07-31 10:29", fraud_score: 0.8 },
      { id: 8, amount: 1350, timestamp: "2025-07-31 10:29", fraud_score: 0.8 },
      { id: 9, amount: 1350, timestamp: "2025-07-31 10:29", fraud_score: 0.8 },
      { id: 10, amount: 1350, timestamp: "2025-07-31 10:29", fraud_score: 0.8 },
      { id: 11, amount: 1350, timestamp: "2025-07-31 10:29", fraud_score: 0.8 },

    ]);
  }, []);

  return (
    <div className={`dashboard-wrapper ${sidebarOpen ? 'sidebar-open' : ''}`}>

      {/* <h2 className="dashboard-title">Live Transactions</h2> */}
      <table className="dashboard-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Amount</th>
            <th>Timestamp</th>
            <th>Fraud Score</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx, index) => (
            <tr key={index}>
              <td>{tx.id}</td>
              <td>₹{tx.amount}</td>
              <td>{tx.timestamp}</td>
              <td>{(tx.fraud_score * 100).toFixed(2)}%</td>
              <td className="indicator-cell">
                {tx.fraud_score > 0.7 && (
                  <span className="fraud-indicator">⚠️</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;
