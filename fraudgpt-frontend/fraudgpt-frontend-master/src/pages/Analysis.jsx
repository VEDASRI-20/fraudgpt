import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const Analysis = () => {
  const data = {
    labels: ['July 25', 'July 26', 'July 27', 'July 28', 'July 29', 'July 30'],
    datasets: [
      {
        label: 'Flagged Frauds per Day',
        data: [3, 5, 2, 4, 7, 6],
        backgroundColor: '#f87171',
        borderRadius: 6,
      },
    ],
  };

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

  return (
    <div>
      <h2>📈 Fraud Activity Analysis</h2>
      <div style={{ width: '80%', marginTop: '30px' }}>
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default Analysis;
