import React, { useEffect, useState } from 'react';
import './Dashboard.css';

const Dashboard = ({ sidebarOpen }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initial fetch
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
        const transactionList = Array.isArray(data) ? data : data.data || [];
        setTransactions(transactionList);
      })
      .catch(error => setError(error.message))
      .finally(() => setLoading(false));

    // WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws/all');

    ws.onopen = () => {
      console.log('WebSocket Connected for Dashboard');
      // Send periodic ping to keep connection alive
      setInterval(() => ws.send(JSON.stringify({ type: 'ping' })), 30000);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data && data.transaction && data.fraud_score !== undefined) {
        // Add new transaction to the top of the list
        setTransactions(prev => [
          {
            id: prev.length + 1,
            amount: data.transaction.amount,
            timestamp: data.timestamp,
            fraud_score: data.fraud_score,
          },
          ...prev,
        ]);
      }
    };

    ws.onclose = () => console.log('WebSocket Disconnected');
    ws.onerror = (error) => console.error('WebSocket Error:', error);

    return () => ws.close(); // Cleanup on unmount
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className={`dashboard-wrapper ${sidebarOpen ? 'sidebar-open' : ''}`}>
      <h2 className="dashboard-title">Live Transactions</h2>
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