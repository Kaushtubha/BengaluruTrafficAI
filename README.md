# Bengaluru Traffic AI (BLR TrafficAI) 🚦🤖

An intelligent, real-time traffic junction analysis and adaptive signaling system designed to monitor vehicle flow, estimate congestion levels, trigger adaptive signaling, log violations, and prioritize emergency lanes. 

The project incorporates **AI/ML vision tracking**, a **Random Forest Classifier** for real-time congestion forecasting, and a **cinematic glassmorphic dark-mode web dashboard** with interactive radar visualizers.

---

## 🌟 Key Features

### 📡 1. AI Vision & Real-Time Object Tracking
* **YOLOv8 & custom IoU Tracker**: Identifies, classifies (Cars, Motorcycles, Buses, Trucks), and tracks vehicles across frames without complex external system dependencies.
* **Lane Assignment**: Uses dynamic frame boundary partitioning to assign vehicles to specific lanes (North, South, East, West).

### 🚨 2. Smart Traffic Violations Suite
* **Red Light Jumps**: Automatically flags vehicles entering junction zones during active RED lights.
* **Speeding Violations**: Estimates speeds based on cross-frame coordinate travel times and flags speeding vehicles.
* **Wrong-Side Driving**: Detects vehicles traveling against traffic flow vectors.
* **No-Helmet Detection**: Simulates motorcycle rider helmet checks and flags violations.
* **Live Violations Feed**: Visualizes all violations in a real-time scrolling operator terminal.

### 🧠 3. ML Congestion Forecasting (Random Forest)
* Trains a local **Random Forest Classifier** (`scikit-learn`) on server startup to predict junction density categories (**Low**, **Medium**, **High**) based on hours, active vehicle count, and lane distribution volumes.

### ⚡ 4. Adaptive Signaling & Emergency Priorities
* **Adaptive Timers**: Allocates active green times dynamically based on lane queue weights.
* **Emergency Override**: Detects priority emergency vehicles (e.g., Ambulances/Fire trucks) and triggers override protocols, giving maximum green-light priority to the emergency lane.

### 💾 5. Fail-Safe Database Logging
* Integrates connection checks with local **MongoDB** services. If the database is offline, it gracefully falls back to console logging instead of crashing, ensuring maximum system uptime.

### 🖥️ 6. Cyberpunk Operations Dashboard
* Custom built React + Vite + Tailwind CSS dashboard.
* **Junction Radar Visualizer**: Interactive SVG grid animating vehicle dots and signal statuses.
* **Stream Charts**: Real-time Recharts visual graphs rendering density streams.

---

## 📂 Project Structure

```text
BengaluruTrafficAI/
├── ai/
│   ├── dataset/
│   │   └── sample_traffic.mp4     # Input traffic stream video
│   ├── db_logger.py              # Fail-safe MongoDB logging integration
│   ├── helmet_detector.py        # Motorcycle rider helmet checking simulation
│   ├── snapshot.py               # Frame snapshot grabber for violations
│   ├── speed_estimator.py        # Object coordinates velocity calculator
│   ├── violation_detector.py     # Red-light jump detection zone checks
│   ├── wrong_side_detector.py    # Wrong-way motion vector analysis
│   └── yolo_detection.py         # Standard raw YOLO runner
├── backend/
│   ├── app.py                    # Main Flask API and tracking loop runner
│   ├── congestion_predictor.py   # Random Forest Classifier model
│   ├── lane_manager.py           # Coordinate boundary lane assignment
│   ├── signal_service.py         # Dynamic timings and Emergency Priority
│   └── tracker_manager.py        # Pure Python IoU tracking class
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx        # Sidebar navigation & theme state wrapper
│   │   │   └── ParticleBackground.jsx # Smooth ambient background animations
│   │   ├── pages/
│   │   │   └── Dashboard.jsx     # High-fidelity dashboard & SVG Visualizer
│   │   ├── store/
│   │   │   └── useStore.js       # Zustand local state and API polling
│   │   └── index.css             # Main styling tailwind utilities
│   ├── package.json              # Vite dependencies
│   └── index.html                # Main index entry file
├── requirements.txt              # Backend python packages list
└── yolov8n.pt                    # 6.5 MB YOLOv8 pre-trained model
```

---

## ⚙️ Installation & Setup

### 🔧 1. Prerequisites
Ensure you have the following installed:
* Python 3.8+
* Node.js 18+
* MongoDB (Optional - console logging fallbacks are fully enabled)

### 🐍 2. Backend Configuration
1. Open a terminal in the root directory.
2. Initialize and activate a python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Flask backend:
   ```bash
   python backend/app.py
   ```
   *The server will start running on `http://127.0.0.1:5000/`.*

### ⚛️ 3. Frontend Configuration
1. Open a new terminal in the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Launch the Vite development server:
   ```bash
   npm run dev
   ```
   *Open `http://localhost:5173/` in your browser to view the live dashboard.*
4. To build production assets:
   ```bash
   npm run build
   ```

---

## 🔬 Technologies Used

* **AI & Machine Learning**: Python, Ultralytics YOLOv8, OpenCV, Scikit-Learn (Random Forest)
* **Backend Framework**: Flask, Flask-CORS, PyMongo
* **Frontend Library**: React 18 (Vite template)
* **State Management**: Zustand
* **Styling & Motion**: Tailwind CSS, Framer Motion
* **Analytics Charts**: Recharts
* **Icons & Notifications**: Lucide React, React Hot Toast

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for details.
