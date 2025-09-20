import React, { useState, useEffect } from "react";

interface SignalData {
  signal_strength_db: number;
  frequency_ghz: number;
  is_known_threat: number;
  threat_priority_level: number;
  timestamp: string;
}

const RealTimeData: React.FC = () => {
  const [signalData, setSignalData] = useState<SignalData[]>([]);
  const AI_BACKEND_URL = "http://10.108.40.253:5000"; // Your backend address

  // This function now fetches data from the Python server
  const fetchSignalData = async () => {
    try {
      const response = await fetch(`${AI_BACKEND_URL}/api/signal_intelligence`);
      const newSignals: SignalData[] = await response.json();
      
      // Add the newly detected signals to the top of our list
      if (newSignals.length > 0) {
        setSignalData(prev => [...newSignals, ...prev].slice(0, 5));
      }
      console.log("Fetched new signal data:", newSignals);
    } catch (error) {
      console.error("Failed to fetch signal data:", error);
    }
  };

  useEffect(() => {
    // Fetch data immediately on load
    fetchSignalData();
    // Set up an interval to fetch new data every 2 seconds
    const interval = setInterval(fetchSignalData, 2000);
    // Clean up when the component is removed
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="real-time-data-panel">
      <h3>📡 SIGNAL INTELLIGENCE</h3>
      <div className="signal-grid">
        {signalData.map((signal, index) => (
          <div key={index} className="signal-item">
            <div className="signal-header">
              <span className="signal-time">
                {new Date(signal.timestamp).toLocaleTimeString()}
              </span>
              {signal.is_known_threat === 1 ? (
                <span className="threat-alert">⚠️ KNOWN THREAT</span>
              ) : (
                <span className="threat-level">P{signal.threat_priority_level}</span>
              )}
            </div>
            <div className="signal-details">
              <div className="signal-strength">
                <span>Strength: </span>
                <div className="strength-bar-container">
                  {/* Normalizing strength from a range of -100 to 0 for the bar width */}
                  <div
                    className="strength-bar"
                    style={{ width: `${100 - Math.abs(signal.signal_strength_db)}%` }}
                  ></div>
                </div>
                <span>{signal.signal_strength_db.toFixed(1)} dB</span>
              </div>
              <div className="signal-frequency">
                Frequency: {signal.frequency_ghz.toFixed(1)} GHz
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RealTimeData;
