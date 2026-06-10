<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=36&pause=1000&color=00D4FF&center=true&vCenter=true&width=800&lines=Bengaluru+Traffic+AI+%F0%9F%9A%A6%F0%9F%A4%96;Real-Time+Junction+Intelligence;YOLOv8+%7C+Flask+%7C+React+%7C+MongoDB" alt="Typing SVG" />

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B35?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/MongoDB-Optional-47A248?style=for-the-badge&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/Scikit--Learn-RandomForest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" />
  <img src="https://img.shields.io/badge/Junction-Silk%20Board%2C%20Bengaluru-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square" />
</p>

<br/>

> **An intelligent real-time traffic junction analysis system** for Silk Board, Bengaluru — powered by YOLOv8 computer vision, a Random Forest congestion predictor, adaptive signal timing, and a cinematic cyberpunk operations dashboard.

</div>

---

## 📸 Dashboard Preview

> The system features a cinematic glassmorphic dark-mode dashboard with live junction radar, real-time stream charts, and an AI operations terminal.

| Junction Radar & Live Stats | Analytics & Violation Feed |
|:---:|:---:|
| Live vehicle tracking across N/S/E/W lanes | Real-time congestion charts & violation logs |

---

## ✨ Features at a Glance

| Category | Capability |
|---|---|
| 🤖 **AI Vision** | YOLOv8n object detection — Cars, Motorcycles, Buses, Trucks |
| 🔁 **Object Tracking** | Pure-Python IoU tracker with persistent vehicle IDs |
| 🚦 **Adaptive Signals** | Dynamic green-time allocation based on live lane queue weights |
| 🚨 **Violations Suite** | Red light jumps · Speeding · Wrong-side · No-helmet |
| 🧠 **ML Forecasting** | scikit-learn Random Forest congestion predictor (Low / Medium / High) |
| 🚑 **Emergency Override** | Automatic + manual priority signal control for ambulances / fire trucks |
| 💾 **Database Logging** | MongoDB integration with graceful offline fallback |
| 📊 **Live Dashboard** | React + Vite + Tailwind + Recharts + Framer Motion |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   BengaluruTrafficAI                    │
│                                                         │
│  ┌──────────────┐    ┌───────────────┐    ┌──────────┐  │
│  │   AI Layer   │    │ Backend Layer │    │ Frontend │  │
│  │              │    │               │    │          │  │
│  │  YOLOv8n     │───▶│  Flask API    │───▶│  React   │  │
│  │  IoU Tracker │    │  Signal Svc   │    │  Vite    │  │
│  │  Violations  │    │  RF Predictor │    │  Recharts│  │
│  │  Speed Est.  │    │  REST Routes  │    │  Zustand │  │
│  └──────────────┘    └──────┬────────┘    └──────────┘  │
│                             │                           │
│                      ┌──────▼────────┐                  │
│                      │   MongoDB     │                  │
│                      │ (optional)    │                  │
│                      └───────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
BengaluruTrafficAI/
│
├── 📁 ai/                            # Computer Vision & Detection Modules
│   ├── 📁 dataset/
│   │   └── sample_traffic.mp4        # Input traffic video stream
│   ├── db_logger.py                  # Fail-safe MongoDB logging (graceful offline fallback)
│   ├── helmet_detector.py            # Motorcycle rider helmet violation simulation
│   ├── snapshot.py                   # Frame snapshot grabber for violation evidence
│   ├── speed_estimator.py            # Pixel-to-meter velocity calculator (km/h)
│   ├── violation_detector.py         # Red-light stop-line zone detection
│   ├── wrong_side_detector.py        # Motion vector wrong-way analysis
│   └── yolo_detection.py             # Raw YOLOv8 detection runner
│
├── 📁 backend/                       # Flask API Server
│   ├── app.py                        # 🚀 Main server — detection loop + REST API
│   ├── congestion_predictor.py       # Random Forest Classifier (trained at startup)
│   ├── lane_manager.py               # Frame boundary → N/S/E/W lane mapping
│   ├── signal_service.py             # Adaptive timer algorithm + emergency override
│   └── tracker_manager.py            # Pure-Python IoU multi-object tracker
│
├── 📁 frontend/                      # React + Vite Dashboard
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   │   ├── Layout.jsx            # Sidebar navigation & global theme wrapper
│   │   │   └── ParticleBackground.jsx # Animated ambient particle canvas
│   │   ├── 📁 pages/
│   │   │   ├── Dashboard.jsx         # Junction radar, live stats & AI terminal
│   │   │   └── Analytics.jsx         # Historical charts & violation breakdown
│   │   ├── 📁 store/
│   │   │   └── useStore.js           # Zustand global state + API polling logic
│   │   ├── App.jsx                   # Root component with router
│   │   └── index.css                 # Global Tailwind + custom dark-mode styles
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── requirements.txt                  # Python dependencies
├── yolov8n.pt                        # YOLOv8 nano pre-trained weights (6.5 MB)
└── .env                              # Environment variables (MongoDB URI etc.)
```

---

## 🧠 How It Works

### 1. 🎥 Real-Time Video Processing
A background thread in `app.py` continuously reads frames from `sample_traffic.mp4`, runs **YOLOv8n** inference, and feeds detections into the **IoU Tracker** to assign persistent vehicle IDs across frames.

### 2. 🗺️ Lane Assignment
Each confirmed track's bounding box centroid is mapped to one of four directional lanes (North, South, East, West) by dividing the frame width into equal quadrants via `lane_manager.py`.

### 3. 🚨 Violation Detection Pipeline
Every frame, each tracked vehicle is checked against **4 violation modules** in sequence:

```
Vehicle Track
    │
    ├──▶ check_red_light_violation()   → Stop-line breach during RED signal
    ├──▶ check_wrong_side()            → Motion vector against traffic flow
    ├──▶ check_speed_violation()       → Pixel-travel-time → km/h estimate
    └──▶ check_helmet_violation()      → Motorcycle rider safety check
         │
         └──▶ log_violation() → MongoDB (or console fallback)
```

### 4. 🌲 Random Forest Congestion Predictor
Trained **at server startup** on synthetic traffic data with features:
- `hour` — time of day (0–23)
- `total_vehicles` — junction-wide vehicle count
- `active_lane_count` — busiest lane vehicle count

Outputs: `"Low"` | `"Medium"` | `"High"` congestion level every frame.

### 5. ⚡ Adaptive Signal Timing Algorithm
Green times are proportionally allocated using:

```
green_time[lane] = MIN_GREEN + (count[lane] / total) × (MAX_GREEN - MIN_GREEN)
```

With **emergency override**: if an ambulance or fire truck is detected (or manually triggered from the frontend), the affected lane immediately receives **60 seconds** of green priority.

### 6. 📊 Live REST API
The Flask server exposes these endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Full traffic state snapshot |
| `GET` | `/api/lanes` | Per-lane vehicle counts |
| `GET` | `/api/signal` | Current adaptive signal plan |
| `GET` | `/api/violations` | Violation breakdown by type |
| `POST` | `/api/simulate_emergency` | Trigger emergency lane override |

---

## ⚙️ Installation & Setup

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.8+ | Core AI & backend runtime |
| Node.js | 18+ | Frontend dev server |
| MongoDB | Any | **Optional** — graceful console fallback if offline |
| GPU (CUDA) | Optional | Accelerates YOLOv8 inference |

---

### 🐍 Step 1 — Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/Kaushtubha/BengaluruTrafficAI.git
cd BengaluruTrafficAI

# 2. Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure environment variables (optional — for MongoDB)
cp .env.example .env
# Edit .env with your MONGO_URI and DB_NAME if needed
```

**Environment Variables (`.env`):**

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=bengaluru_traffic
```

> ⚠️ **MongoDB is fully optional.** If no database is available, the system gracefully falls back to console-only logging with zero crashes.

```bash
# 5. Start the Flask backend
python backend/app.py
```

The API server starts at **`http://127.0.0.1:5000/`**

---

### ⚛️ Step 2 — Frontend Setup

```bash
# Open a new terminal in the frontend directory
cd frontend

# Install npm dependencies
npm install

# Start the Vite development server
npm run dev
```

Open **`http://localhost:5173/`** in your browser to access the live dashboard.

```bash
# Build for production
npm run build
```

---

### 🚀 Quick Start (Both Servers)

```bash
# Terminal 1 — Backend
.venv\Scripts\activate && python backend/app.py

# Terminal 2 — Frontend
cd frontend && npm run dev
```

---

## 🛠️ Tech Stack

### Backend & AI
| Library | Role |
|---------|------|
| `ultralytics` (YOLOv8) | Real-time vehicle detection |
| `opencv-python` | Frame capture & image processing |
| `scikit-learn` | Random Forest congestion classifier |
| `Flask` + `flask-cors` | REST API server |
| `pymongo` | MongoDB integration |
| `numpy` | Numerical computation |
| `python-dotenv` | Environment configuration |

### Frontend
| Library | Role |
|---------|------|
| `React 18` + `Vite` | UI framework & build tooling |
| `Tailwind CSS` | Utility-first styling |
| `Framer Motion` | Smooth animations & transitions |
| `Recharts` | Real-time data visualization |
| `Zustand` | Lightweight global state management |
| `Axios` | HTTP client for API polling |
| `Lucide React` | Icon system |
| `React Hot Toast` | Notification system |

---

## 🚦 API Reference

### `GET /api/status`
Returns the full live traffic state.

```json
{
  "status": "online",
  "junction": "Silk Board, Bengaluru",
  "active_lane": "North",
  "congestion_level": "Medium",
  "vehicle_counts": { "North": 12, "South": 5, "East": 8, "West": 3 },
  "total_vehicles": 28,
  "tracked_vehicles": 143,
  "violations": 7,
  "signal_plan": {
    "green_times": { "North": 45.2, "South": 18.0, "East": 28.6, "West": 10.8 },
    "priority_lane": "North",
    "cycle_time": 102.6
  }
}
```

### `GET /api/violations`
```json
{
  "total_violations": 7,
  "red_light": 2,
  "wrong_side": 1,
  "speeding": 3,
  "no_helmet": 1
}
```

### `POST /api/simulate_emergency`
```json
// Request body
{ "lane": "North" }

// Response
{ "status": "success", "message": "Simulated emergency vehicle in North lane." }
```

---

## 🗺️ Roadmap

- [x] YOLOv8 vehicle detection & classification
- [x] IoU multi-object tracking with persistent IDs
- [x] 4-type violation detection suite
- [x] Random Forest congestion predictor
- [x] Adaptive signal timing algorithm
- [x] Emergency vehicle priority override (auto + manual)
- [x] MongoDB violation & stats logging
- [x] Cyberpunk glassmorphic React dashboard
- [x] Real-time junction radar SVG visualizer
- [ ] ALPR (Automatic License Plate Recognition) integration
- [ ] Live CCTV RTSP stream support
- [ ] Multi-junction coordination network
- [ ] Mobile operator app (React Native)
- [ ] Historical trend analytics with time-series DB

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⚖️ License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

Made with ❤️ for smarter cities · Bengaluru, India 🇮🇳

**[⭐ Star this repo](https://github.com/Kaushtubha/BengaluruTrafficAI)** if you find it useful!

</div>
