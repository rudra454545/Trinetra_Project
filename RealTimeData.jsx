'use client';

import React, { useState, useEffect, useContext } from "react";
import { Line } from "react-chartjs-2";
import { GameStateContext } from "../../contexts/GameStateContext";
import { useSocket } from "../../contexts/SocketContext";

// Chart.js registration
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

const RealTimeData = () => {
  const gameState = useContext(GameStateContext);
  const { socket } = useSocket(); // ✅ Reuse global socket
  const [jetSignals, setJetSignals] = useState({});

  useEffect(() => {
    // Initialize signal arrays
    const initSignals = {};
    [1, 2, 3, 4, 5].forEach((id) => (initSignals[id] = []));
    setJetSignals(initSignals);

    // Handler for RWR updates
    const handleRwrUpdate = (detections) => {
      setJetSignals((prev) => {
        const updated = { ...prev };
        detections.forEach((det) => {
          if (!updated[det.jet_id]) updated[det.jet_id] = [];
          // Add new data & keep only last 10 points
          updated[det.jet_id] = [...updated[det.jet_id], det].slice(-10);
        });
        return updated;
      });
    };

    socket.on("rwr_update", handleRwrUpdate);

    // Cleanup: remove listener only
    return () => {
      socket.off("rwr_update", handleRwrUpdate);
    };
  }, [socket]);

  // Prepare chart data
  const chartData = {
    labels: Array.from({ length: 10 }, (_, i) => `T-${9 - i}`),
    datasets: [1, 2, 3, 4, 5].map((jetId, idx) => ({
      label: `Jet ${jetId}`,
      data: jetSignals[jetId]?.map((s) => s.strength_db) || [],
      borderColor: ["#00BFFF", "#39FF14", "#FFD700", "#FF00FF", "#FFFFFF"][idx],
      backgroundColor: "transparent",
      pointRadius: jetSignals[jetId]?.map((_, i, arr) =>
        i === arr.length - 1 ? 8 : 4
      ) || [],
      pointHoverRadius: 10,
      tension: 0.3,
      borderWidth: 2,
      segment: {
        borderColor: (ctx) => {
          const val = ctx.p0.parsed.y;
          return val > -40 ? "#FF4136" : ctx.dataset.borderColor;
        },
      },
    })),
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 0 },
    plugins: {
      legend: { position: "top" },
      tooltip: {
        callbacks: {
          label: function (context) {
            const jetId = context.dataset.label?.split(" ")[1];
            const sig = jetSignals[parseInt(jetId)]?.[context.dataIndex];
            return sig
              ? ` ${sig.strength_db.toFixed(1)} dB @ ${sig.frequency_ghz.toFixed(1)} GHz (${sig.timestamp.slice(11, 19)})`
              : "";
          },
        },
      },
    },
    scales: {
      y: {
        suggestedMin: -120,
        suggestedMax: 0,
        title: { display: true, text: "Signal Strength (dB)" },
      },
      x: { title: { display: true, text: "Latest Signals" } },
    },
  };

  return (
    <div
      className="real-time-data-panel"
      style={{
        padding: "0.8rem",
        backgroundColor: "#0D131A",
        borderRadius: "10px",
        border: "1px solid #00BFFF",
      }}
    >
      <h3 style={{ color: "#00BFFF", textAlign: "center" }}>
        📡 SIGNAL INTELLIGENCE
      </h3>
      <div style={{ height: "220px", marginBottom: "10px" }}>
        <Line data={chartData} options={chartOptions} />
      </div>

      <div
        className="signal-list"
        style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}
      >
        {Object.entries(jetSignals).map(([jetId, signals]) => {
          const latest = signals[signals.length - 1];
          const colorIntensity = latest
            ? Math.min(1, (100 + latest.strength_db) / 100)
            : 0;

          return (
            <div
              key={jetId}
              style={{
                flex: "1 1 180px",
                backgroundColor: "#111",
                padding: "6px 8px",
                borderRadius: "6px",
                boxShadow: latest
                  ? `0 0 12px rgba(255,65,54,${colorIntensity})`
                  : "",
              }}
            >
              <strong style={{ color: "#00BFFF" }}>Jet {jetId}</strong>
              <div>
                Latest:{" "}
                {latest ? (
                  <span style={{ color: "#FF4136", fontWeight: "bold" }}>
                    {latest.strength_db.toFixed(1)} dB
                  </span>
                ) : (
                  "—"
                )}
              </div>
              <div style={{ fontSize: "0.8rem", color: "#AAAAAA" }}>
                {signals.map((s, i) => (
                  <span
                    key={i}
                    style={{
                      display: "inline-block",
                      width: "22px",
                      textAlign: "center",
                    }}
                  >
                    {s.strength_db.toFixed(0)}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RealTimeData;