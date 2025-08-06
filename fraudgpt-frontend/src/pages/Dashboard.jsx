import React, { useEffect, useState } from 'react';
import './Dashboard.css';

const Dashboard = ({ sidebarOpen }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("Fetching all transactions...");
    setLoading(true);
    fetch('http://localhost:8000/api/all-transactions')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        // Ensure data is an array, handling the case where it might be {message, data}
        const transactionList = Array.isArray(data) ? data : data.data || [];
        setTransactions(transactionList);
      })
      .catch(error => setError(error.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

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
          {transactions.length === 0 ? (
            <tr><td colSpan="5">No transactions found.</td></tr>
          ) : (
            transactions.map((tx, index) => (
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
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;