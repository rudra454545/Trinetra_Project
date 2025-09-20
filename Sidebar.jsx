import React from "react";
import { Doughnut, Bar, Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
} from "chart.js";

import "./Sidebar.css";

// Register all the necessary components for Chart.js
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
);

// --- Chart Component for Fleet Status ---
const FleetStatusChart = ({ squadron }) => {
  const statusCounts = squadron.reduce((acc, jet) => {
    acc[jet.status] = (acc[jet.status] || 0) + 1;
    return acc;
  }, {});

  const data = {
    labels: Object.keys(statusCounts),
    datasets: [
      {
        label: "Jet Status",
        data: Object.values(statusCounts),
        backgroundColor: [
          "rgba(0, 255, 127, 0.6)", // Spring Green for Active
          "rgba(255, 206, 86, 0.6)", // Yellow for Warning
          "rgba(255, 99, 132, 0.6)",  // Red for Damaged
        ],
        borderColor: ["#00FF7F", "#FFCE56", "#FF6384"],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top", labels: { color: '#ddd' } },
      title: { display: true, text: "Squadron Readiness", color: '#ddd' },
    },
  };

  return <Doughnut data={data} options={options} />;
};

// --- Chart Component for Signal Intelligence ---
const SignalTypeChart = ({ signals }) => {
  const signalTypeCounts = signals.reduce((acc, sig) => {
    acc[sig.type] = (acc[sig.type] || 0) + 1;
    return acc;
  }, {});

  const data = {
    labels: Object.keys(signalTypeCounts),
    datasets: [
      {
        label: "Detected Signal Types",
        data: Object.values(signalTypeCounts),
        backgroundColor: "rgba(54, 162, 235, 0.6)",
        borderColor: "#36A2EB",
        borderWidth: 1,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: "Signal Type Analysis", color: '#ddd' },
    },
    scales: {
        x: { ticks: { color: '#aaa' }, grid: { color: 'rgba(255,255,255,0.1)' } },
        y: { ticks: { color: '#aaa' }, grid: { color: 'rgba(255,255,255,0.1)' } },
    }
  };

  return <Bar data={data} options={options} />;
};

// --- Chart Component for RWR Detections ---
const RwrRadarChart = ({ detections }) => {
  const data = {
    labels: detections.map(ping => `${ping.emitter} (${ping.angle}°) `),
    datasets: [
      {
        label: 'Threat Proximity (1=Near, 3=Far)',
        data: detections.map(ping => ping.range),
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: '#FF6384',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    scales: {
      r: {
        beginAtZero: true, max: 3, min: 0,
        ticks: { stepSize: 1, color: '#111', backdropColor: 'rgba(255,255,255,0.6)', borderRadius: 4 },
        pointLabels: { color: '#ddd', font: { size: 10 } },
        grid: { color: 'rgba(255,255,255,0.2)' },
        angleLines: { color: 'rgba(255,255,255,0.2)' }
      },
    },
    plugins: {
        legend: { position: 'top', labels: { color: '#ddd' } },
    }
  };

  return <Radar data={data} options={options} />;
};

const Sidebar = ({ gameState }) => {
  const handleControlClick = (action) => {
    console.log(`Control action: ${action}`);
    // You can emit a socket event here, e.g., socket.emit('control_action', action);
  };

  return (
    <div className="app-sidebar">
      {/* --- FLEET STATUS --- */}
      <div className="sidebar-section">
        <h4>🛡️ FLEET STATUS</h4>
        <div className="fleet-status-list">
          {gameState.squadron.length ? (
            gameState.squadron.map((jet) => (
              <div className="unit" key={jet.name}>
                <span>{jet.name}</span>
                <span>{jet.status} | F: {jet.fuel}% | W: {jet.weapons}</span>
              </div>
            ))
          ) : (
            <p>No jets online</p>
          )}
        </div>
        <div className="chart-container">
          {gameState.squadron.length > 0 && <FleetStatusChart squadron={gameState.squadron} />}
        </div>
      </div>

      {/* --- SIGNAL INTELLIGENCE --- */}
      <div className="sidebar-section">
        <h4>🛰️ SIGNAL INTELLIGENCE</h4>
        <div className="chart-container">
          {gameState.signals.length ? (
            <SignalTypeChart signals={gameState.signals} />
          ) : (
            <p>No signals detected</p>
          )}
        </div>
      </div>

      {/* --- RWR DETECTION --- */}
      <div className="sidebar-section">
        <h4>📡 RWR DETECTION</h4>
        <div className="chart-container">
          {gameState.rwr.length ? (
            <RwrRadarChart detections={gameState.rwr} />
          ) : (
            <p>No threats detected</p>
          )}
        </div>
      </div>

      {/* --- CONTROLS INFO --- */}
      <div className="sidebar-section">
        <h4>⌨️ CONTROLS</h4>
        <div className="controls-container">
          <button onClick={() => handleControlClick('throttle_toggle')}>Toggle Throttle</button>
          <button onClick={() => handleControlClick('fire_weapon')}>Fire Weapon</button>
          <button onClick={() => handleControlClick('radar_sweep')}>Radar Sweep</button>
          <button onClick={() => handleControlClick('pause_menu')}>Pause / Menu</button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
