import React, { useEffect, useState } from 'react';
import './Dashboard.css';

const FlaggedTransactions = () => {
  const [flagged, setFlagged] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
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