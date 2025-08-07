import React, { useEffect, useState, useRef } from 'react';
import './Dashboard.css';

const Dashboard = ({ sidebarOpen }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const ws = useRef(null);

  // New state to manage which transaction is expanded
  const [expandedTxId, setExpandedTxId] = useState(null);

  useEffect(() => {
    // We remove the initial fetch call entirely since the backend doesn't support it.
    // We'll immediately establish the WebSocket connection.
    try {
      ws.current = new WebSocket('ws://localhost:8080/ws/all');

      ws.current.onopen = () => {
        console.log('WebSocket Connected for Dashboard');
        setLoading(false);
      };

      ws.current.onmessage = (event) => {
        const liveData = JSON.parse(event.data);
        if (liveData) {
          // Add the new transaction to the beginning of the list
          setTransactions(prev => [liveData, ...prev]);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket Disconnected');
        // You might want to handle reconnection logic here
      };
      
      ws.current.onerror = (err) => {
        console.error('WebSocket Error:', err);
        setError('WebSocket connection error. Please ensure the backend is running.');
        setLoading(false);
      };

    } catch (err) {
      setError(err.message);
      setLoading(false);
    }

    // Cleanup function to close the WebSocket connection when the component unmounts
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  // Function to toggle the expanded details for a specific transaction
  const handleViewDetails = (id) => {
    setExpandedTxId(prevId => prevId === id ? null : id);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className={`dashboard-wrapper ${sidebarOpen ? 'sidebar-open' : ''}`}>
      <div className="table-scroll-container">

        <table className="dashboard-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Amount</th>
              <th>Timestamp</th>
              <th>Fraud Score</th>
              <th></th>
              <th></th> {/* Added a new empty header for the details button */}
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 ? (
              <tr><td colSpan="6">No transactions found.</td></tr>
            ) : (
              transactions.map((tx) => (
                <React.Fragment key={tx.id}>
                  <tr key={tx.id}>
                    <td>{tx.id}</td>
                    <td>₹{tx.transaction.amount}</td>
                    <td>{tx.timestamp}</td>
                    <td>{(tx.fraud_score * 100).toFixed(2)}%</td>
                    <td className="indicator-cell">
                      {tx.is_flagged && (
                        <span className="fraud-indicator">⚠️</span>
                      )}
                    </td>
                    <td>
                      <span
                        onClick={() => handleViewDetails(tx.id)}
                        className="expand-icon"
                        style={{ cursor: 'pointer' }}
                        role="button"
                        tabIndex="0"
                      >
                        {'☰'}
                      </span>
                    </td>
                  </tr>
                  {expandedTxId === tx.id && (
                    <tr className="details-row">
                      <td colSpan="6">
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

export default Dashboard;
