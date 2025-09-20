import React from "react";
import "./App.css";
import { SocketProvider, useSocket } from "./contexts/SocketContext";
import Header from "./components/Layout/Header";
import Sidebar from "./components/Layout/Sidebar";
import MilitaryMap from "./components/Map/MilitaryMap";
import JetStatusPanel from "./components/Dashboard/JetStatusPanel";
import RealTimeData from "./components/DataFeeds/RealTimeData";
import { RwrDetectionsProvider, RwrChart } from "./components/Map/RwrDetectionsChart";

// A new component to render the main content of the application.
// This keeps the main App component clean and focused on providing context.
const AppContent = () => {
  // Get everything needed from the single, powerful useSocket hook.
  const { isConnected, gameState } = useSocket();

  return (
    <div className="dashboard-layout">
      <Header isConnected={isConnected} />
      {/* Sidebar receives gameState directly as a prop */}
      <Sidebar gameState={gameState} />
      <main className="main-content">
        {/* Deeper components like MilitaryMap can now call useSocket() themselves to get the gameState */}
        <MilitaryMap />
        <section className="data-feeds-grid">
          <JetStatusPanel />
          <RealTimeData />
        </section>
        <RwrDetectionsProvider>
          <section className="rwr-section">
            <RwrChart />
          </section>
        </RwrDetectionsProvider>
      </main>
    </div>
  );
};

// The main App component is now extremely simple.
// Its only job is to set up the context provider.
const App = () => {
  return (
    <SocketProvider>
      <AppContent />
    </SocketProvider>
  );
};

export default App;
