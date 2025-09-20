# Trinetra_Project
​🧠 An AI-powered dashboard providing complete situational awareness for air combat through real-time data fusion, threat prediction, and a dynamic tactical map.
# 🛰️ Project Trinetra: AI Commando Dashboard


Trinetra is a real-time tactical command and control dashboard designed to visualize fleet movements, process signal intelligence, and display AI-driven threat assessments on a dynamic 2D map.

## About The Project

This project provides a sophisticated front-end interface built with **React** and **TypeScript** for monitoring a simulated battlefield. It is powered by a **Python** backend that runs the core simulation and AI models. The dashboard leverages WebSockets for live data updates, interactive charts for data visualization, and a canvas-based map for rendering entity positions and events, creating a comprehensive situational awareness tool.

## ✨ Key Features

* 🗺️ **Real-Time Tactical Map:** Visualizes the positions of friendly jets and enemy entities using `react-konva`, providing a live, bird's-eye view of the operational area.
* 📊 **Dynamic Data Feeds:** Displays live updates for fleet status, Signal Intelligence (SIGINT), and RWR (Radar Warning Receiver) detections in dedicated panels.
* 📈 **Interactive Data Visualization:** Uses `Chart.js` to render various graphs, including line charts for signal strength, doughnut charts for fleet readiness, and radar charts for threat analysis.
* 🧠 **Dual AI Core Integration:** The backend processes data through specialized AI models for image analysis (IMINT) and signal analysis (SIGINT), fusing the results for a unified threat assessment.
* 🕹️ **Simulation Controls:** A dedicated panel allows for controlling the backend simulation, such as starting, pausing, or resetting the scenario.
* 🌐 **Live Backend Communication:** Connects to the Python backend server via `Socket.IO` for receiving a constant stream of real-time simulation data.

## 🛠️ Tech Stack

| Category     | Technology                                                                          |
| :----------- | :---------------------------------------------------------------------------------- |
| **Frontend** | React, TypeScript, Chart.js, Konva, Socket.IO Client                                |
| **Backend** | Python, Flask, Flask-SocketIO, Pygame (for simulation), TensorFlow/Keras (for AI)   |
| **Language** | TypeScript (Frontend), Python (Backend)                                             |
| **Styling** | CSS Modules / Styled-Components (assumed)                                           |

## 🏛️ System Architecture

The project follows a client-server architecture where the simulation logic and AI models are decoupled from the user interface.


​+--------------------------+      +---------------------------------+      +---------------------------+
| Pygame Simulator         | ---> | Python Backend (Flask/SocketIO) | ---> | React Frontend (Dashboard)|
| (Generates entity data)  |      | (Serves API & WebSocket Events) |      | (Visualizes real-time data)|
+--------------------------+      +---------------------------------+      +---------------------------+



## 📂 File Structure
## TRINETRA_PROJECT/
## ├── ai_backend/
## │   ├── data/
## │   │   └── alert.wav
## │   ├── model/
## │   │   ├── fusion_model.h5
## │   │   └── strategic_model.h5
## │   ├── venv/
## │   ├── app.py
## │   ├── get-pip.py
## │   ├── pygame_simulator.py
## │   ├── requirements.txt
## │   ├── sim_state.json
## │   ├── tactical_dashboard_simulator.py
## │   ├── train_fusion_model.py
## │   └── train_satellite_model.py
## └── trinetra-dashboard/
## ├── public/
## │   └── ...
## ├── src/
## │   ├── components/
## │   │   ├── Controls/
## │   │   │   └── SimulationControls.jsx
## │   │   ├── Dashboard/
## │   │   │   ├── JetStatusPanel.jsx
## │   │   │   └── TacticalViews.jsx
## │   │   ├── DataFeeds/
## │   │   │   ├── DashboardPage.jsx
## │   │   │   └── RealTimeData.jsx
## │   │   ├── Layout/
## │   │   │   ├── Header.jsx
## │   │   │   └── Sidebar.jsx
## │   │   └── Map/
## │   │       ├── Flowchart.html
## │   │       ├── MilitaryMap.jsx
## │   │       └── RwrDetectionsChart.jsx
## │   ├── context/
## │   │   ├── GameStateContext.tsx
## │   │   └── SocketContext.tsx
## │   ├── App.css
## │   ├── App.tsx
## │   ├── index.css
## │   └── .env
## ├── .gitignore
## ├── package.json
## └── README.md



​🚀 Getting Started
​To get a local copy up and running, follow these simple steps.
​Prerequisites
​Make sure you have the following installed on your machine:

​Node.js (v16 or later is recommended)
​npm (comes with Node.js) or yarn
​Python (v3.8 or later is recommended)
​pip (comes with Python)

Installation and Setup
1.​Clone the repository:
git clone https://github.com/rudra454545/Trinetra_Project.git
cd Trinetra_Project

2.Setup the Python Backend:
cd ai_backend
# It's recommended to create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install Python dependencies
pip install -r requirements.txt


3.Setup the React Frontend:
# Navigate back to the root and into the frontend directory
cd ../trinetra-dashboard

# Install Node.js dependencies
npm install


Running the Application
1.​Start the Backend Server:

​Make sure you are in the ai_backend directory with your virtual environment activated.

​<!-- end list -->
python app.py
.​You should see output indicating that the Flask server is running on http://localhost:5000.


2.Start the Frontend Application:

​Open a new terminal and navigate to the trinetra-dashboard directory.

​<!-- end list -->
npm start
.This will open the dashboard in your default browser at http://localhost:3000. The dashboard will automatically connect to the running backend.

​📦 Core Dependencies
​Frontend

​react, react-dom
​typescript
​chart.js, react-chartjs-2
​konva, react-konva
​socket.io-client

​Backend

​Flask
​Flask-SocketIO
​Flask-Cors
​pygame
​tensorflow (or keras)
​numpy



