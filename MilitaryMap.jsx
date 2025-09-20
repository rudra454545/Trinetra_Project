"use client";

import React, { useEffect, useState, useRef } from "react";
import { Stage, Layer, Circle, Line, Text } from "react-konva";
import { Line as ChartLine } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import io from "socket.io-client";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const socket = io("http://localhost:5000");

// --- New Compact Jet Status Component ---
const JetStatusItem = ({ jet }) => {
  // Assuming max remainingTime is 150 for the fuel bar calculation
  const fuelPercentage = (jet.remainingTime / 150) * 100;
  // Assuming max weapons is 10
  const weaponsPercentage = (jet.weapons / 10) * 100;

  const barStyle = {
    height: '8px',
    borderRadius: '4px',
    transition: 'width 0.5s ease-in-out',
  };

  return (
    <div style={{ marginBottom: '12px', padding: '8px', background: '#1A1A1A', borderRadius: '4px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <strong style={{ color: '#00BFFF' }}>{jet.name}</strong>
        <span style={{ color: jet.rwr_signal > 50 ? "red" : "lime", fontWeight: 'bold' }}>
          RWR: {jet.rwr_signal.toFixed(0)}
        </span>
      </div>
      <div style={{ fontSize: '0.8rem' }}>
        <div style={{ marginBottom: '4px' }}>
          <span>Fuel ({jet.remainingTime.toFixed(1)}m)</span>
          <div style={{ background: '#333', borderRadius: '4px' }}>
            <div style={{ ...barStyle, width: `${fuelPercentage}%`, background: 'linear-gradient(90deg, #00BFFF, #39FF14)' }}></div>
          </div>
        </div>
        <div>
          <span>Weapons ({jet.weapons})</span>
          <div style={{ background: '#333', borderRadius: '4px' }}>
            <div style={{ ...barStyle, width: `${weaponsPercentage}%`, background: 'linear-gradient(90deg, #FFD700, #FF4136)' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};


const MilitaryMapDashboard = () => {
  const [jets, setJets] = useState([]);
  const [enemies, setEnemies] = useState([]);
  const [jetPulses, setJetPulses] = useState({});
  const [frequencyData, setFrequencyData] = useState({});
  const [mapSize, setMapSize] = useState({ width: 0, height: 0 });
  const mapContainerRef = useRef(null);
  const enemyMaxRange = 200;

  // Effect to make the map responsive
  useEffect(() => {
    const handleResize = () => {
      if (mapContainerRef.current) {
        setMapSize({
          width: mapContainerRef.current.offsetWidth,
          height: mapContainerRef.current.offsetHeight,
        });
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Initialize fleet
  useEffect(() => {
    const initJets = [
      { id: 1, name: "Jet 1", position: { x: 100, y: 200 }, remainingTime: 120, weapons: 10, rwr_signal: 0, speed: 0.5, dir: 1 },
      { id: 2, name: "Jet 2", position: { x: 200, y: 250 }, remainingTime: 90, weapons: 10, rwr_signal: 0, speed: 0.3, dir: 1 },
      { id: 3, name: "Jet 3", position: { x: 300, y: 180 }, remainingTime: 150, weapons: 10, rwr_signal: 0, speed: 0.4, dir: 1 },
      { id: 4, name: "Jet 4", position: { x: 150, y: 300 }, remainingTime: 100, weapons: 10, rwr_signal: 0, speed: 0.35, dir: 1 },
      { id: 5, name: "Jet 5", position: { x: 250, y: 220 }, remainingTime: 110, weapons: 10, rwr_signal: 0, speed: 0.45, dir: 1 },
    ];
    const initEnemies = [{ id: 1, position: { x: 500, y: 250 }, active: true, speed: 0.25, dir: 1 }];
    setJets(initJets);
    setEnemies(initEnemies);
    const freqData = {};
    initJets.forEach(j => (freqData[j.id] = []));
    setFrequencyData(freqData);
  }, []);

  // Simulation loop
  useEffect(() => {
    const loop = setInterval(() => {
      setJets(prevJets =>
        prevJets.map(jet => {
          let newX = jet.position.x + jet.speed * jet.dir;
          if (newX > 600 || newX < 50) jet.dir *= -1;
          newX = jet.position.x + jet.speed * jet.dir;
          let maxSignal = 0;
          const newJetPulses = [];
          enemies.forEach(enemy => {
            const dx = newX - enemy.position.x;
            const dy = jet.position.y - enemy.position.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < enemyMaxRange) {
              const strength = Math.max(0, Math.min(100, 100 - distance / 3));
              maxSignal = Math.max(maxSignal, strength);
              newJetPulses.push({
                from: [enemy.position.x, enemy.position.y],
                to: [newX, jet.position.y],
                strength,
              });
              socket.emit("pulse_hit", {
                jetId: jet.id,
                enemyId: enemy.id,
                timestamp: new Date().toISOString(),
                position: { x: newX, y: jet.position.y },
              });
            }
          });
          setJetPulses(prev => ({
            ...prev,
            [jet.id]: [...(prev[jet.id] || []), ...newJetPulses].slice(-10),
          }));
          setFrequencyData(prev => ({
            ...prev,
            [jet.id]: [...(prev[jet.id] || []), maxSignal].slice(-20),
          }));
          return {
            ...jet,
            position: { ...jet.position, x: newX },
            rwr_signal: maxSignal,
            remainingTime: Math.max(jet.remainingTime - 0.02, 0),
            weapons: jet.weapons, // Assuming weapons don't decrease in this simulation
            dir: jet.dir,
          };
        })
      );
      setEnemies(prevEnemies =>
        prevEnemies.map(enemy => {
          let newX = enemy.position.x + enemy.speed * enemy.dir;
          if (newX > 700 || newX < 400) enemy.dir *= -1;
          newX = enemy.position.x + enemy.speed * enemy.dir;
          return { ...enemy, position: { ...enemy.position, x: newX }, dir: enemy.dir };
        })
      );
    }, 50);
    return () => clearInterval(loop);
  }, [enemies]);

  const chartData = {
    labels: Array.from({ length: 20 }, (_, i) => `T-${19 - i}`),
    datasets: jets.map((j, idx) => ({
      label: j.name,
      data: frequencyData[j.id] || [],
      borderColor: ["#00BFFF", "#39FF14", "#FFD700", "#FF00FF", "#FFFFFF"][idx % 5],
      backgroundColor: "transparent",
      tension: 0.4,
      pointRadius: 2,
      borderWidth: 1.5,
    })),
  };
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 0 },
    scales: {
      y: { min: 0, max: 100, ticks: { stepSize: 20, color: '#888' }, grid: { color: '#444' } },
      x: { ticks: { autoSkip: true, maxTicksLimit: 10, color: '#888' }, grid: { color: '#444' } },
    },
    plugins: { legend: { position: "top", labels: { color: '#ccc' } } },
  };

  return (
    <div style={{ display: "flex", height: "100vh", background: "#111", color: "white", fontFamily: "Arial" }}>
      {/* 2D Military Map */}
      <div ref={mapContainerRef} style={{ flex: 1.5, position: "relative", height: '100%' }}>
        <Stage width={mapSize.width} height={mapSize.height}>
          <Layer>
            {enemies.map(e => (
              <React.Fragment key={e.id}>
                <Circle x={e.position.x} y={e.position.y} radius={10} fill="red" />
                <Text x={e.position.x + 10} y={e.position.y - 15} text={`Enemy ${e.id}`} fill="red" fontSize={14} />
                <Circle x={e.position.x} y={e.position.y} radius={enemyMaxRange} stroke="red" strokeWidth={1} opacity={0.1} />
              </React.Fragment>
            ))}
            {jets.map(j => (
              <React.Fragment key={j.id}>
                <Circle x={j.position.x} y={j.position.y} radius={8} fill="cyan" />
                <Text
                  x={j.position.x + 10}
                  y={j.position.y - 15}
                  text={`${j.name}`}
                  fill="cyan"
                  fontSize={12}
                />
                {(jetPulses[j.id] || []).map((p, idx) => (
                  <Line key={`${j.id}-${idx}`} points={[...p.from, ...p.to]} stroke="yellow" strokeWidth={1} opacity={0.8} />
                ))}
              </React.Fragment>
            ))}
          </Layer>
        </Stage>
      </div>

      {/* Sidebar: Combined Tactical Overview */}
      <div style={{ flex: 1, padding: "10px", overflowY: "auto", background: '#000' }}>
        <h2>📡 Tactical Overview</h2>
        
        <h4 style={{ marginTop: '20px' }}>Signal Strength (RWR)</h4>
        <div style={{ height: "200px" }}>
          <ChartLine data={chartData} options={chartOptions} />
        </div>

        <h4 style={{ marginTop: '20px', borderTop: '1px solid #333', paddingTop: '20px' }}>🛩️ Fleet Status</h4>
        {jets.map(j => (
          <JetStatusItem key={j.id} jet={j} />
        ))}
      </div>
    </div>
  );
};

export default MilitaryMapDashboard;
