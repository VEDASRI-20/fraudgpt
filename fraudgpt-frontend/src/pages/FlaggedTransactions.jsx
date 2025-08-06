import React, { useEffect, useState } from 'react';
import './Dashboard.css'; // Reuse same table styles

const FlaggedTransactions = () => {
  const [flagged, setFlagged] = useState([]);

  useEffect(() => {
    setFlagged([
      { id: 1, amount: 4200, timestamp: "2025-07-31 11:00", fraud_score: 0.93 },
      { id: 2, amount: 1950, timestamp: "2025-07-31 11:02", fraud_score: 0.81 },
      { id: 3, amount: 3700, timestamp: "2025-07-31 11:04", fraud_score: 0.77 },
    ]);
  }, []);

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
            flagged.map((tx, index) => (
              <tr key={index}>
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
