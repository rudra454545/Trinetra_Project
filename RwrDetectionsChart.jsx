// src/components/Map/RwrDetectionsChart.jsx
import React, { createContext, useContext, useState } from "react";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Radar } from "react-chartjs-2";

// Register Chart.js components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

// --- Context Setup ---
const RwrContext = createContext();

export const RwrDetectionsProvider = ({ children }) => {
  const [detections, setDetections] = useState([
    { emitter: "Radar A", angle: 30, range: 1 }, // Near
    { emitter: "Radar B", angle: 120, range: 2 }, // Mid
    { emitter: "Radar C", angle: 210, range: 3 }, // Far
  ]);

  return (
    <RwrContext.Provider value={{ detections, setDetections }}>
      {children}
    </RwrContext.Provider>
  );
};

export const useRwrDetections = () => useContext(RwrContext);

// --- RWR Chart Component ---
export const RwrChart = () => {
  const { detections } = useRwrDetections();

  // Convert detections into chart data
  const labels = detections.map((d) => `${d.emitter} (${d.angle}°)`);

  const data = {
    labels,
    datasets: [
      {
        label: "RWR Detections",
        data: detections.map((d) => d.range),
        backgroundColor: "rgba(0, 191, 255, 0.2)",
        borderColor: "rgba(166, 0, 255, 1)",
        borderWidth: 2,
        pointBackgroundColor: "rgba(255, 0, 0, 0.8)",
        pointRadius: 5,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 0 },
    scales: {
      r: {
        min: 0,
        max: 3, // Near=1, Mid=2, Far=3
        ticks: {
          stepSize: 1,
        },
        grid: {
          color: "rgba(0,191,255,0.2)",
        },
        angleLines: {
          color: "rgba(0,191,255,0.2)",
        },
      },
    },
    plugins: {
      legend: { position: "top" },
    },
  };

  return (
    <div style={{ width: "100%", height: "400px" }}>
      <Radar data={data} options={chartOptions} />
    </div>
  );
};