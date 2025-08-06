import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const Analysis = () => {
  const [chartData, setChartData] = useState({ labels: [], datasets: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("Fetching transaction analysis...");
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