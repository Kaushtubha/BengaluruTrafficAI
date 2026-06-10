<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=34&pause=1000&color=FF9F1C&center=true&vCenter=true&width=900&lines=🚦+Bengaluru+Traffic+AI;Real-Time+Junction+Intelligence+System;YOLOv8+%7C+Random+Forest+%7C+React+%7C+Flask" alt="Typing SVG" />

<br/>

### 🌐 **[Live Demo → bengaluru-traffic-ai.vercel.app](https://bengaluru-traffic-ai.vercel.app/)**

<br/>

<p align="center">
  <a href="https://bengaluru-traffic-ai.vercel.app/">
    <img src="https://img.shields.io/badge/🚀_Live_Demo-bengaluru--traffic--ai.vercel.app-FF9F1C?style=for-the-badge&logoColor=white" />
  </a>
  <a href="https://bengalurutrafficai.onrender.com/api/status">
    <img src="https://img.shields.io/badge/⚙️_API-bengalurutrafficai.onrender.com-4A90D9?style=for-the-badge&logoColor=white" />
  </a>
</p>

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B35?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/scikit--learn-RandomForest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-Optional-47A248?style=for-the-badge&logo=mongodb&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-Vercel-000000?style=flat-square&logo=vercel" />
  <img src="https://img.shields.io/badge/Backend-Render-46E3B7?style=flat-square&logo=render" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=flat-square" />
  <img src="https://img.shields.io/badge/Junction-Silk%20Board%2C%20Bengaluru-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square" />
</p>

<br/>

> **An intelligent real-time traffic junction analysis system** for Silk Board, Bengaluru — powered by YOLOv8 computer vision, a Random Forest congestion predictor, adaptive signal timing with emergency vehicle override, and a cinematic cyberpunk glassmorphic operations dashboard.

</div>

---

## 🖥️ Live Dashboard Preview

| 🌑 Dark Mode — Junction Operations | ☀️ Light Mode — Analytics |
|:---:|:---:|
| Cyberpunk glassmorphic radar & live stats | Historical violation charts & breakdown |

> 🔗 **Try it live: [bengaluru-traffic-ai.vercel.app](https://bengaluru-traffic-ai.vercel.app/)**

---

## ✨ Features at a Glance

| Category | Capability |
|---|---|
| 🤖 **AI Vision** | YOLOv8n object detection — Cars, Motorcycles, Buses, Trucks |
| 🔁 **Object Tracking** | Pure-Python IoU multi-object tracker with persistent vehicle IDs |
| 🚦 **Adaptive Signals** | Dynamic green-time allocation based on live lane queue weights |
| 🚨 **Violations Suite** | Red light jumps · Speeding (km/h) · Wrong-side driving · No-helmet |
| 🧠 **ML Forecasting** | scikit-learn Random Forest congestion predictor — Low / Medium / High |
| 🚑 **Emergency Override** | Auto-detection + manual frontend trigger for ambulances / fire trucks |
| 💾 **Database Logging** | MongoDB integration with graceful offline console fallback |
| 📊 **Live Dashboard** | React 18 + Vite + Tailwind + Recharts + Framer Motion |
| 🌐 **Fully Deployed** | Frontend on Vercel · Backend API on Render · Both free-tier |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     BengaluruTrafficAI                           │
│                                                                  │
│  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────┐  │
│  │    AI Layer      │   │  Backend Layer   │   │   Frontend   │  │
│  │                  │   │                  │   │              │  │
│  │  YOLOv8n         │──▶│  Flask REST API  │──▶│  React + Vite│  │
│  │  IoU Tracker     │   │  Signal Service  │   │  Tailwind CSS│  │
│  │  Violation Suite │   │  RF Predictor    │   │  Recharts    │  │
│  │  Speed Estimator │   │  Emergency Ctrl  │   │  Zustand     │  │
│  └─────────────────┘   └────────┬─────────┘   └──────────────┘  │
│                                  │                               │
│                         ┌────────▼─────────┐                    │
│                         │    MongoDB        │                    │
│                         │  (optional)       │                    │
│                         └──────────────────┘                    │
│                                                                  │
│  Deployed:  Render.com (backend)   ·   Vercel (frontend)        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
BengaluruTrafficAI/
│
├── 📁 ai/                             # Computer Vision & Detection Modules
│   ├── 📁 dataset/
│   │   └── sample_traffic.mp4         # Input traffic video stream
│   ├── db_logger.py                   # Fail-safe MongoDB logging (offline fallback)
│   ├── helmet_detector.py             # Motorcycle rider helmet violation simulation
│   ├── snapshot.py                    # Frame snapshot grabber for violation evidence
│   ├── speed_estimator.py             # Pixel-to-meter velocity calculator (km/h)
│   ├── violation_detector.py          # Red-light stop-line zone detection
│   ├── wrong_side_detector.py         # Motion vector wrong-way analysis
│   └── yolo_detection.py              # Raw YOLOv8 detection runner
│
├── 📁 backend/                        # Flask API Server
│   ├── app.py                         # 🚀 Full AI server — YOLOv8 detection loop + REST API
│   ├── app_demo.py                    # ⚡ Lightweight demo server (Render free-tier)
│   ├── congestion_predictor.py        # Random Forest Classifier (trained at startup)
│   ├── lane_manager.py                # Frame boundary → N/S/E/W lane mapping
│   ├── signal_service.py              # Adaptive timer algorithm + emergency override
│   └── tracker_manager.py             # Pure-Python IoU multi-object tracker
│
├── 📁 frontend/                       # React + Vite Dashboard
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   │   ├── Layout.jsx             # Sidebar navigation & global theme wrapper
│   │   │   └── ParticleBackground.jsx # Animated ambient particle canvas
│   │   ├── 📁 pages/
│   │   │   ├── Dashboard.jsx          # Junction radar, live stats & AI terminal
│   │   │   └── Analytics.jsx          # Historical charts & violation breakdown
│   │   ├── 📁 store/
│   │   │   └── useStore.js            # Zustand global state + API polling logic
│   │   ├── App.jsx                    # Root component with router
│   │   └── index.css                  # Global Tailwind + dark/light mode styles
│   ├── vercel.json                    # Vercel deployment config
│   ├── package.json
│   └── index.html
│
├── render.yaml                        # Render deployment config
├── requirements.txt                   # Full Python dependencies (local AI)
├── requirements-demo.txt              # Minimal deps for Render free-tier
├── yolov8n.pt                         # YOLOv8 nano pre-trained weights (6.5 MB)
└── .env                               # Environment variables (MongoDB URI etc.)
```

---

## 🧠 How It Works

### 1. 🎥 Real-Time Video Processing
A background thread continuously reads frames from `sample_traffic.mp4`, runs **YOLOv8n** inference, and feeds detections into the **IoU Tracker** to assign persistent vehicle IDs across frames.

### 2. 🗺️ Lane Assignment
Each confirmed track's bounding box centroid is mapped to one of four directional lanes by dividing the frame width into equal quadrants via `lane_manager.py`.

```
Frame Width
├── 0% ─── 25%   →  West Lane
├── 25% ── 50%   →  North Lane
├── 50% ── 75%   →  South Lane
└── 75% ── 100%  →  East Lane
```

### 3. 🚨 Violation Detection Pipeline
Every frame, each tracked vehicle is checked against **4 violation modules** in sequence:

```
Vehicle Track (confirmed, ID assigned)
    │
    ├──▶ check_red_light_violation()  → Cross stop-line during RED signal
    ├──▶ check_wrong_side()           → Motion vector opposite to traffic flow
    ├──▶ check_speed_violation()      → pixel_travel × PIXEL_TO_METER / Δtime → km/h > 40
    └──▶ check_helmet_violation()     → Motorcycle rider safety check
         │
         └──▶ log_violation() ──▶ MongoDB  (or graceful console fallback)
```

### 4. 🌲 Random Forest Congestion Predictor
Trained **at server startup** on synthetic traffic data with features:

| Feature | Description |
|---------|-------------|
| `hour` | Time of day (0–23) |
| `total_vehicles` | Junction-wide vehicle count |
| `active_lane_count` | Busiest single-lane vehicle count |

**Output:** `"Low"` · `"Medium"` · `"High"` congestion classification.

### 5. ⚡ Adaptive Signal Timing Algorithm

Green times are proportionally allocated per lane:

```
green_time[lane] = MIN_GREEN(10s) + (count[lane] / total) × (MAX_GREEN(60s) - MIN_GREEN(10s))
```

**Emergency Override Protocol:** When an ambulance/fire truck is detected (or manually triggered from dashboard), the affected lane receives **MAX_GREEN = 60 seconds** instantly.

---

## 🌐 Live Deployment

| Service | URL | Platform |
|---------|-----|----------|
| 🖥️ **Frontend Dashboard** | [bengaluru-traffic-ai.vercel.app](https://bengaluru-traffic-ai.vercel.app/) | Vercel (Free) |
| ⚙️ **Backend REST API** | [bengalurutrafficai.onrender.com](https://bengalurutrafficai.onrender.com/api/status) | Render (Free) |

> ⚠️ **Note:** Render free-tier spins down after 15 min of inactivity. First request may take 30–60 seconds to wake up. After that, data streams normally.

---

## 📡 API Reference

### `GET /api/status`
Full live traffic state snapshot.

```json
{
  "status": "online",
  "junction": "Silk Board, Bengaluru",
  "active_lane": "South",
  "congestion_level": "Medium",
  "vehicle_counts": {
    "North": 12, "South": 18, "East": 9, "West": 4
  },
  "total_vehicles": 43,
  "tracked_vehicles": 1247,
  "violations": 14,
  "signal_plan": {
    "green_times": { "North": 28.3, "South": 37.5, "East": 22.1, "West": 12.1 },
    "priority_lane": "South",
    "cycle_time": 100.0
  },
  "mode": "demo"
}
```

### `GET /api/signal`
Current adaptive signal plan.

### `GET /api/violations`
Violation breakdown by category.

```json
{
  "total_violations": 14,
  "red_light": 3,
  "wrong_side": 2,
  "speeding": 7,
  "no_helmet": 2
}
```

### `POST /api/simulate_emergency`
Trigger priority signal override.

```json
// Request
{ "lane": "North" }

// Response
{ "status": "success", "message": "Emergency vehicle simulated in North lane." }
```

### `GET /api/health`
Backend health check.

---

## ⚙️ Local Installation & Setup

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.8+ | Core AI & backend runtime |
| Node.js | 18+ | Frontend dev server |
| MongoDB | Any | **Optional** — console fallback if offline |
| GPU (CUDA) | Optional | Accelerates YOLOv8 inference significantly |

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

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional — for MongoDB)
# Create .env file:
# MONGO_URI=mongodb://localhost:27017/
# DB_NAME=bengaluru_traffic

# 5. Start the Flask backend (full AI mode)
python backend/app.py
```

**API server starts at `http://127.0.0.1:5000/`**

### ⚛️ Step 2 — Frontend Setup

```bash
# In a new terminal
cd frontend

# Install npm dependencies
npm install

# Start Vite dev server
npm run dev
```

**Open `http://localhost:5173/` in your browser.**

### 🚀 Quick Start (Both Servers)

```bash
# Terminal 1 — Backend (full AI)
.venv\Scripts\activate && python backend/app.py

# Terminal 2 — Frontend
cd frontend && npm run dev
```

### 🌐 Environment Variables

```env
# .env (root directory)
MONGO_URI=mongodb://localhost:27017/
DB_NAME=bengaluru_traffic

# frontend/.env.local (for connecting to remote backend)
VITE_API_URL=https://bengalurutrafficai.onrender.com
```

---

## 🚀 Deploy Your Own (Free)

| Part | Platform | Guide |
|------|----------|-------|
| **Frontend** | Vercel | Import repo → set Root Dir = `frontend` → add `VITE_API_URL` env var |
| **Backend** | Render | New Web Service → Build: `pip install -r requirements-demo.txt` → Start: `python backend/app_demo.py` |
| **Database** | MongoDB Atlas | Create free M0 cluster → add `MONGO_URI` to Render env vars |

---

## 🛠️ Tech Stack

### Backend & AI
| Library | Version | Role |
|---------|---------|------|
| `ultralytics` (YOLOv8) | 8.4.60 | Real-time vehicle detection & classification |
| `opencv-python` | 4.13 | Frame capture & image processing |
| `scikit-learn` | 1.9 | Random Forest congestion classifier |
| `Flask` + `flask-cors` | 3.1 | REST API server |
| `pymongo` | 4.17 | MongoDB integration |
| `numpy` | 2.4 | Numerical computation |
| `python-dotenv` | 1.2 | Environment configuration |
| `torch` + `torchvision` | 2.12 | Deep learning runtime for YOLOv8 |

### Frontend
| Library | Version | Role |
|---------|---------|------|
| `React` + `Vite` | 18 + 5.2 | UI framework & build tooling |
| `Tailwind CSS` | 3.4 | Utility-first styling |
| `Framer Motion` | 11 | Smooth animations & micro-interactions |
| `Recharts` | 2.12 | Real-time data visualization charts |
| `Zustand` | 4.5 | Lightweight global state management |
| `Axios` | 1.7 | HTTP client for API polling |
| `Lucide React` | 0.395 | Icon system |
| `React Hot Toast` | 2.4 | Notification system |
| `React Router` | 6.23 | Client-side routing |

---

## 🗺️ Roadmap

- [x] YOLOv8n vehicle detection & classification
- [x] IoU multi-object tracker with persistent vehicle IDs
- [x] 4-type violation detection suite (red light, speeding, wrong-side, helmet)
- [x] Random Forest congestion predictor (trains on startup)
- [x] Adaptive signal timing algorithm with proportional allocation
- [x] Emergency vehicle priority override (auto-detect + manual)
- [x] Fail-safe MongoDB violation & stats logging
- [x] Cyberpunk glassmorphic React dashboard (dark + light mode)
- [x] Real-time junction SVG radar visualizer with animated traffic dots
- [x] Live vehicle count streaming chart (Recharts AreaChart)
- [x] **Deployed live — Frontend (Vercel) + Backend (Render)**
- [ ] ALPR — Automatic License Plate Recognition integration
- [ ] Live CCTV RTSP stream support (replace sample video)
- [ ] Multi-junction coordination network
- [ ] Historical trend analytics with time-series database
- [ ] Mobile operator app (React Native)

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the project
2. Create your feature branch:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'feat: add AmazingFeature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request

---

## ⚖️ License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

**🚦 BengaluruTrafficAI** — Built for smarter cities · Bengaluru, India 🇮🇳

<br/>

### 🌐 [bengaluru-traffic-ai.vercel.app](https://bengaluru-traffic-ai.vercel.app/) | ⚙️ [API Status](https://bengalurutrafficai.onrender.com/api/health)

<br/>

**[⭐ Star this repo](https://github.com/Kaushtubha/BengaluruTrafficAI)** if you find it useful — it helps a lot!

</div>
