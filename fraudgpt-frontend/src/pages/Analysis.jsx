import React, { useState } from "react";
import { Bar, Scatter, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  ArcElement,
  Tooltip,
  Legend
);

const Analysis = () => {
  const [loading] = useState(false); // No loading since data is hardcoded
  const [error] = useState(null); // No error handling needed for static data

  // Hardcoded sample data
  const barData = {
    labels: ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM"],
    datasets: [
      {
        label: "Fraud Events",
        data: [2, 5, 3, 8, 4],
        backgroundColor: "#f87171", // Red for visibility
        borderColor: "#ef4444",
        borderWidth: 1,
        borderRadius: 6,
      },
    ],
  };

  const scatterData = {
    datasets: [
      {
        label: "Suspicious Transactions",
        data: [
          { x: 200, y: 0.9 },
          { x: 500, y: 0.85 },
          { x: 1500, y: 0.99 },
          { x: 300, y: 0.7 },
        ],
        backgroundColor: "#facc15", // Yellow for contrast
        pointRadius: 6,
      },
    ],
  };

  const pieData = {
    labels: ["Card Fraud", "Account Takeover", "Phishing", "Other"],
    datasets: [
      {
        data: [40, 25, 20, 15],
        backgroundColor: ["#ef4444", "#f97316", "#eab308", "#3b82f6"], // Distinct colors
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: { beginAtZero: true, ticks: { stepSize: 1 } },
      x: { title: { display: true, text: "Transaction Amount" } },
    },
    plugins: { legend: { position: "bottom" } },
  };

  if (loading) return <p style={{ color: "white", padding: "20px" }}>Loading...</p>;
  if (error) return <p style={{ color: "red", padding: "20px" }}>{error}</p>;

  return (
    <div
      style={{
        padding: "20px",
        overflowY: "auto",
        maxHeight: "100vh",
        color: "white",
        background: "#1a1a2e",
        borderRadius: "10px",
        boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
      }}
    >
      <h2 style={{ marginBottom: "20px", color: "#ffffff", fontWeight: "bold" }}>
        Fraud Analysis Dashboard
      </h2>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* Bar Chart */}
        <div style={{ background: "#16213e", padding: "15px", borderRadius: "10px", height: "300px" }}>
          <h3 style={{ color: "#a3bffa", marginBottom: "10px" }}>Fraud Events Over Time</h3>
          <Bar data={barData} options={{ ...chartOptions, plugins: { legend: { position: "top" } } }} />
        </div>

        {/* Scatter Plot */}
        <div style={{ background: "#16213e", padding: "15px", borderRadius: "10px", height: "300px" }}>
          <h3 style={{ color: "#a3bffa", marginBottom: "10px" }}>Suspicious Outliers</h3>
          <Scatter
            data={scatterData}
            options={{
              ...chartOptions,
              scales: { y: { title: { display: true, text: "Risk Score" } } },
              plugins: { legend: { position: "top" } },
            }}
          />
        </div>

        {/* Pie Chart */}
        <div style={{ background: "#16213e", padding: "15px", borderRadius: "10px", height: "300px", gridColumn: "span 2" }}>
          <h3 style={{ color: "#a3bffa", marginBottom: "10px" }}>Fraud Breakdown by Category</h3>
          <Pie
            data={pieData}
            options={{ ...chartOptions, plugins: { legend: { position: "right" } } }}
          />
        </div>
      </div>
    </div>
  );
};

export default Analysis;