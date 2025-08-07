import React, { useEffect, useState } from 'react';
import './Dashboard.css';

const FlaggedTransactions = () => {
  // We'll use this state to hold the list of flagged transactions
  const [flagged, setFlagged] = useState([]);
  
  // New state to manage which transaction is expanded
  const [expandedTxId, setExpandedTxId] = useState(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws/fraud-only');

    ws.onopen = () => {
      console.log('WebSocket Connected for Flagged Transactions');
      // Send a periodic ping to keep the connection alive.
      setInterval(() => ws.send(JSON.stringify({ type: 'ping' })), 30000);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data && data.is_flagged && data.fraud_score !== undefined) {
        // We now store the full data object, so all details are available for the modal.
        setFlagged(prev => [data, ...prev]);
      }
    };

    ws.onclose = () => console.log('WebSocket Disconnected');
    ws.onerror = (error) => console.error('WebSocket Error:', error);

    // This cleanup function is crucial. It ensures the WebSocket connection
    // is closed properly when the component unmounts.
    return () => ws.close();
  }, []); // The empty dependency array ensures this effect runs only once

  // Function to toggle the expanded details for a specific transaction
  const handleViewDetails = (id) => {
    setExpandedTxId(prevId => prevId === id ? null : id);
  };

  return (
    <div className="dashboard-wrapper">
      <div className="table-scroll-container">
        <table className="dashboard-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Amount</th>
              <th>Timestamp</th>
              <th>Fraud Score</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {flagged.length === 0 ? (
              <tr><td colSpan="5">No frauds detected yet.</td></tr>
            ) : (
              flagged.map((tx) => (
                <React.Fragment key={tx.id}>
                  <tr key={tx.id}>
                    <td>{tx.id}</td>
                    <td>₹{tx.transaction.amount}</td>
                    <td>{tx.timestamp}</td>
                    <td className="indicator-cell">{(tx.fraud_score * 100).toFixed(2)}%</td>
                    <td>
                      <button 
                        onClick={() => handleViewDetails(tx.id)}
                        className="view-details-button"
                      >
                        <span className="expand-icon">
                          {expandedTxId === tx.id ? '▼' : '▶'}
                        </span>
                      </button>
                    </td>
                  </tr>
                  {expandedTxId === tx.id && (
                    <tr className="details-row">
                      <td colSpan="5">
                        <div className="details-content">
                          <h4>Fraud Analysis</h4>
                          <p><strong>Primary Reason:</strong> {tx.primary_reason || 'N/A'}</p>
                          <p><strong>Detailed Explanation:</strong> {tx.detailed_explanation || 'No detailed explanation provided.'}</p>
                          <p><strong>Risk Level:</strong> {tx.risk_level}</p>
                          <p><strong>Recommendation:</strong> {tx.recommendation}</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FlaggedTransactions;
