import React, { useEffect, useState } from 'react';
import './Dashboard.css';

const FlaggedTransactions = () => {
  const [flagged, setFlagged] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initial fetch
    console.log("Fetching flagged transactions...");
    setLoading(true);
    fetch('http://localhost:8000/api/flagged-transactions')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => setFlagged(data))
      .catch(error => setError(error.message))
      .finally(() => setLoading(false));

    // WebSocket connection for fraud-only updates
    const ws = new WebSocket('ws://localhost:8000/ws/fraud-only');

    ws.onopen = () => {
      console.log('WebSocket Connected for Flagged Transactions');
      // Send periodic ping to keep connection alive
      setInterval(() => ws.send(JSON.stringify({ type: 'ping' })), 30000);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data && data.is_flagged && data.fraud_score !== undefined) {
        // Add new flagged transaction to the top of the list
        setFlagged(prev => [
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
    <div className="dashboard-wrapper">
      <table className="dashboard-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Amount</th>
            <th>Timestamp</th>
            <th>Fraud Score</th>
          </tr>
        </thead>
        <tbody>
          {flagged.length === 0 ? (
            <tr><td colSpan="4">No frauds detected yet.</td></tr>
          ) : (
            flagged.map((tx) => (
              <tr key={tx.id}>
                <td>{tx.id}</td>
                <td>₹{tx.amount}</td>
                <td>{tx.timestamp}</td>
                <td className="indicator-cell">{(tx.fraud_score * 100).toFixed(2)}%</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default FlaggedTransactions;