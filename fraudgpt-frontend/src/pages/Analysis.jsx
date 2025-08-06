import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const Analysis = () => {
  const [chartData, setChartData] = useState({ labels: [], datasets: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initial fetch
    console.log("Fetching initial transaction analysis...");
    setLoading(true);
    fetch('http://localhost:8000/api/transaction-analysis')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setChartData(data);
      })
      .catch(error => setError(error.message))
      .finally(() => setLoading(false));

    // WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws/all');

    ws.onopen = () => {
      console.log('WebSocket Connected for Analysis');
      // Send periodic ping to keep connection alive
      setInterval(() => ws.send(JSON.stringify({ type: 'ping' })), 30000);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data && data.fraud_score && data.hour_of_day !== undefined) {
        // Update chart data with new fraud event
        setChartData(prevData => {
          const labels = [...prevData.labels];
          const dataset = [...prevData.datasets];
          const hourIndex = labels.indexOf(`2025-07-30 ${data.hour_of_day}:00`);
          
          if (hourIndex === -1) {
            labels.push(`2025-07-30 ${data.hour_of_day}:00`);
            dataset[0] = {
              ...dataset[0],
              data: [...dataset[0].data, 1],
              backgroundColor: '#f87171',
              borderRadius: 6,
            };
          } else {
            dataset[0].data[hourIndex] += 1;
          }

          return { labels, datasets: dataset };
        });
      }
    };

    ws.onclose = () => console.log('WebSocket Disconnected');
    ws.onerror = (error) => console.error('WebSocket Error:', error);

    return () => ws.close(); // Cleanup on unmount
  }, []);

  const options = {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        ticks: { stepSize: 1 },
      },
    },
    plugins: {
      legend: { position: 'bottom' },
    },
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>📈 Fraud Activity Analysis</h2>
      <div style={{ width: '80%', marginTop: '30px' }}>
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
};

export default Analysis;