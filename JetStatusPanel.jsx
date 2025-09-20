'use client';

import React, { useState, useEffect } from "react";

const JetStatusPanel = () => {
  const [jets, setJets] = useState([]);
  const AI_BACKEND_URL = "http://10.108.40.253:5000"; // Fetch jet data from backend

  const fetchJetData = async () => {
    try {
      const response = await fetch(`${AI_BACKEND_URL}/api/squadron_status`);
      const data = await response.json();
      const updatedJets = data.jets.map((jet, idx) => ({
        id: idx + 1,
        name: `${idx + 1}`,
        status: jet.status,
        fuel: jet.fuel,
        weapons: jet.weapons,
        position: jet.position,
        rwr_signal: jet.signal_history?.length
          ? jet.signal_history[jet.signal_history.length - 1].strength_db
          : 0,
        path_history: jet.path || [],
        locked: jet.locked || false,
      }));
      setJets(updatedJets);
    } catch (error) {
      console.error("Failed to fetch jet data:", error);
    }
  };

  useEffect(() => {
    fetchJetData();
    const intervalId = setInterval(fetchJetData, 1000); // update every second
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="jet-status-panel">
      <h3>🛩️ FLEET STATUS</h3>
      <div className="jets-container">
        {jets.map((jet) => (
          <div
            key={jet.id}
            className={`jet-status ${jet.status.toLowerCase()}`}
            style={{
              boxShadow: jet.rwr_signal && jet.rwr_signal > 0
                ? `0 0 15px rgba(255,0,0,${Math.min(jet.rwr_signal / 100, 1)})`
                : "",
              border: jet.locked ? "2px solid #FF4136" : "1px solid #333",
              transition: "all 0.5s ease",
              position: "relative",
            }}
          >
            <div className="jet-header">
              <span className="jet-id">{jet.name}</span>
              <span className={`status-indicator ${jet.status.toLowerCase()}`}>
                {jet.status}
              </span>
              {jet.locked && (
                <span
                  style={{
                    color: "#FF4136",
                    fontWeight: "bold",
                    marginLeft: 10,
                  }}
                >
                  🔒 LOCKED
                </span>
              )}
            </div>

            <div className="jet-details">
              <div className="fuel-gauge">
                <div className="fuel-label">FUEL</div>
                <div className="fuel-bar-container">
                  <div
                    className="fuel-level"
                    style={{ width: `${jet.fuel}%` }}
                  ></div>
                </div>
                <span className="fuel-percentage">{jet.fuel}%</span>
              </div>

              <div className="weapons-status">
                <span>MISSILES: {jet.weapons}</span>
              </div>

              <div className="position-data">
                POS: {jet.position.x.toFixed(4)}, {jet.position.y.toFixed(4)}
              </div>

              {jet.rwr_signal && jet.rwr_signal > 0 && (
                <div
                  className="rwr-indicator"
                  style={{
                    color: "#FF4136",
                    fontWeight: "bold",
                    animation: "pulse-alert 1s infinite",
                  }}
                >
                  ⚡ Pulse Detected: {jet.rwr_signal.toFixed(1)} dB
                </div>
              )}

              {/* Path history small graph */}
              {jet.path_history && jet.path_history.length > 1 && (
                <svg
                  width="150"
                  height="100"
                  style={{ border: "1px solid #555", marginTop: 5 }}
                >
                  {jet.path_history.map((p, i) => {
                    if (i === 0) return null;
                    const prev = jet.path_history[i - 1];
                    const scaleX = 150 / 0.2; // assuming patrol box ~0.2 deg
                    const scaleY = 100 / 0.2;
                    return (
                      <line
                        key={i}
                        x1={(prev.x - 22.2) * scaleX}
                        y1={100 - (prev.y - 84.7) * scaleY}
                        x2={(p.x - 22.2) * scaleX}
                        y2={100 - (p.y - 84.7) * scaleY}
                        stroke="#0ff"
                        strokeWidth="1"
                      />
                    );
                  })}
                </svg>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default JetStatusPanel;
