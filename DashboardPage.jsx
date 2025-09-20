"use client";

import React, { useState, useEffect } from "react";

// Import your components
import Sidebar from "./Sidebar"; // Assuming Sidebar.jsx is in the same folder

// --- MOCK COMPONENTS FOR LAYOUT EXAMPLE ---
// In your real app, you would import your actual map and other panels
const MapPlaceholder = () => <div style={{ background: '#0a0a0a', border: '1px solid #333', color: '#555', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>MAP AREA</div>;
const TacticalOverviewPlaceholder = () => <div style={{ background: '#0a0a0a', border: '1px solid #333', color: '#555', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>TACTICAL OVERVIEW</div>;
const SignalPanelPlaceholder = () => <div style={{ background: '#0a0a0a', border: '1px solid #333', color: '#555', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>SIGNAL INTELLIGENCE</div>;


const DashboardPage = () => {
  // Step 1: Create the main state for the entire application
  const [gameState, setGameState] = useState({
    squadron: [],
    signals: [],
    rwr: [],
  });

  // Step 2: Use useEffect to fetch data from your backend in real-time
  useEffect(() => {
    const AI_BACKEND_URL = "http://10.108.40.253:5000"; // Your backend address

    const fetchGameState = async () => {
      try {
        // Fetch data from multiple endpoints if necessary
        const squadronRes = await fetch(`${AI_BACKEND_URL}/api/squadron_status`);
        const squadronData = await squadronRes.json();
        
        // You would also fetch signals and rwr data here
        // const signalsRes = await fetch(`${AI_BACKEND_URL}/api/signals`);
        // const signalsData = await signalsRes.json();
        
        // Update the state with the new data from the backend
        setGameState(prevState => ({
          ...prevState, // Keep old state for things you didn't fetch
          squadron: squadronData.jets || [], // Use the fetched jet data
          // signals: signalsData || [],
        }));

      } catch (error) {
        console.error("Failed to fetch game state:", error);
      }
    };

    // Fetch data immediately when the component loads
    fetchGameState();

    // Then, set up an interval to keep fetching new data every 2 seconds
    const intervalId = setInterval(fetchGameState, 2000);

    // Important: Clean up the interval when the component is unmounted
    return () => clearInterval(intervalId);
  }, []); // The empty array [] means this effect runs only once on mount

  // Step 3: Render your layout and pass the live gameState to the Sidebar
  return (
    <div style={{ display: "grid", gridTemplateColumns: "300px 1fr 450px", height: "100vh" }}>
      
      {/* The Sidebar now receives the live, updating gameState */}
      <div style={{ gridColumn: "1 / 2", gridRow: "1 / 1" }}>
        <Sidebar gameState={gameState} />
      </div>

      {/* Your other components would go here */}
      <div style={{ gridColumn: "2 / 3", gridRow: "1 / 1" }}>
        <MapPlaceholder />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gridColumn: "3 / 4", gridRow: "1 / 1" }}>
        <TacticalOverviewPlaceholder />
        <SignalPanelPlaceholder />
      </div>
    </div>
  );
};

export default DashboardPage;
