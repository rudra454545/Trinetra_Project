'use client';

import React, { useContext } from "react";
import { GameStateContext } from "../../contexts/GameStateContext";
import "./Header.css"; // The CSS file you provided

const Header = ({ isConnected }) => {
  const gameState = useContext(GameStateContext);

  // Safely access game state properties with default fallbacks
  const lastEvent = gameState?.events?.[0] || "No new events";
  const missionStatus = gameState?.mission_status || "STANDBY";
  const threatCount = gameState?.threats?.length || 0;

  // Determine dynamic class names
  const statusClass = missionStatus === "ACTIVE" ? "status-active" : "status-standby";
  const threatClass = threatCount > 0 ? "threat-high" : "";

  return (
    <header className="app-header">
      <div className="header-title">
        <h1>TRINETRA</h1>
        <span className="subtitle">AI Mission Command</span>
      </div>

      <div className="header-kpis">
        <div className="kpi-item">
          <span className="kpi-label">MISSION STATUS</span>
          <span className={`kpi-value ${statusClass}`}>{missionStatus}</span>
        </div>
        <div className="kpi-item">
          <span className="kpi-label">DETECTED THREATS</span>
          <span className={`kpi-value ${threatClass}`}>{threatCount}</span>
        </div>
        <div className="kpi-item">
          <span className="kpi-label">LAST EVENT</span>
          <div className="kpi-value-small">
            <span className={lastEvent.length > 25 ? "marquee" : ""}>{lastEvent}</span>
          </div>
        </div>
      </div>

      <div className="header-time">
        <div className={`kpi-value ${isConnected ? "status-active" : "status-alert"}`}>
          {isConnected ? "● CONNECTED" : "● ONLINE"}
        </div>
        <div className="date">{new Date().toLocaleDateString()}</div>
        <div className="time">{new Date().toLocaleTimeString()}</div>
      </div>
    </header>
  );
};

export default Header;
