# BengaluruTrafficAI Technical Report & Interview Preparation Handbook

Welcome to the **BengaluruTrafficAI Technical Report and Interview Preparation Handbook**. This directory contains the complete, modular LaTeX source code for the comprehensive technical report and interview preparation guide for the BengaluruTrafficAI project.

---

## 📚 Handbook Structure

The technical report is available in two equivalent formats:
1. **Modular Version:** Orchestrated by the master document [`BengaluruTrafficAI_Technical_Report.tex`](BengaluruTrafficAI_Technical_Report.tex) which imports 26 individual chapters from the `chapters/` folder.
2. **Single-File Consolidated Version:** [`BengaluruTrafficAI_Single_Complete.tex`](BengaluruTrafficAI_Single_Complete.tex) which bundles all 26 chapters and preamble into a single 2,790-line self-contained LaTeX document for single-file copy-pasting into Overleaf or any LaTeX IDE.

| Chapter | Title | Primary Focus & Source References |
| :--- | :--- | :--- |
| **01** | Executive Summary | High-level system overview, dual-mode architecture, core capabilities, and verified limitations. |
| **02** | Problem Statement & Motivation | Urban junction gridlock, Silk Board context, failure of fixed timers, edge CV motivation, research boundaries. |
| **03** | Requirements & System Scope | FR-01 through FR-11 requirements table, non-functional requirements (NFRs), and out-of-scope boundaries. |
| **04** | Complete Technology Stack | Deep dive into YOLOv8n, PyTorch, OpenCV, Flask, scikit-learn, React 18, Vite 5, Zustand, Tailwind, Recharts. |
| **05** | System Architecture | Detailed architecture schematic, component responsibility matrix, request/response boundaries, cold-start handling. |
| **06** | Repository Structure & Navigation | Annotated directory hierarchy, symbol maps, and call traceability matrix. |
| **07** | Frontend Architecture | React 18, Zustand state store, concurrent `Promise.all` polling, loading/error states, GPS validation. |
| **08** | Backend Architecture & API Lifecycle | Flask routing, endpoint specifications (`/api/status`, `/api/signal`, `/api/violations`, etc.), request validation schemas. |
| **09** | Local Computer-Vision Pipeline | Edge perception loop, background worker thread, YOLO inference, tracking, and spatial evaluation sequence. |
| **10** | Object Detection | Anchor-free YOLOv8 architecture, confidence thresholds, COCO vehicle filtering, IoU, and NMS mechanics. |
| **11** | Vehicle Tracking | Multi-object tracking, greedy IoU matching equation, track lifecycles, and trade-offs vs. DeepSORT/ByteTrack. |
| **12** | Traffic-Violation Detection | Stop-line red light crossing, directional wrong-side flow, helmet compliance, and in-memory deduplication. |
| **13** | Speed Estimation | Euclidean pixel displacement, monotonic timestamps, tracking gap resets, and camera homography limitations. |
| **14** | Lane Management & Signal Planning | Horizontal lane partitioning, dynamic proportional green-time allocator (10--60s), zero-vehicle fallback, emergency preemption. |
| **15** | Congestion ML Classification | 50-tree Random Forest classifier, 3D feature space, synthetic step rules, input sanitization against NaN/Inf. |
| **16** | Driver Portal & Geospatial Logic | Commuter advisory interface, Haversine spherical geodesic derivation, coordinate sanitization, and road-distance caveats. |
| **17** | Data Flow & State Management | End-to-end data lifecycle, FIFO buffer management (20 snapshots), and state synchronization. |
| **18** | Deployment & Configuration | Vercel SPA rewrites, Render blueprint configuration, environment variables, CORS, and cold-start mitigations. |
| **19** | Testing Strategy | 46 automated regression tests in Python `unittest`, test taxonomy table, and defect prevention mapping. |
| **20** | Security, Reliability & Failure Analysis | Threat modeling, coordinate bounds, input length limits, zero-secret `.gitignore`, and recovery matrix. |
| **21** | Performance & Complexity | Asymptotic time and space complexity table ($O$) for all perception, scheduling, and client algorithms. |
| **22** | Limitations & Future Work | Systematic limitations table (uncalibrated speed, synthetic RF, FOV delay, Haversine distance) and engineering roadmap. |
| **23** | Complete Interview Preparation | **62 high-quality tiered interview questions** across Beginner (L1), Intermediate (L2), Advanced (L3), and Deep Technical Follow-ups (L4). |
| **24** | Project Explanation Scripts | Spoken scripts for 30s, 60s, 2-min, 5-min, and 10-min interviews, explaining bugs, limitations, and contributions. |
| **25** | Whiteboard Exercises | 8 fully worked mathematical problems: IoU calculation, greedy tracking matching, speed from pixels, signal green splits, etc. |
| **26** | Glossary & Quick Revision Sheets | Essential terminology, core equations, API summary, common traps, 1-page rapid revision sheet, and readiness checklist. |

---

## 🛠️ Compilation Instructions

### Local Compilation Status
> **Notice on Compilation Environment:**
> In accordance with project instructions (zero package installation and zero cost), this repository has been audited for local LaTeX compilation tools. The current Windows development environment does not have a pre-installed TeX distribution (`pdflatex`, `xelatex`, `lualatex`, `latexmk`, or MiKTeX).
>
> Therefore, valid, modular LaTeX source code is provided. You can compile `BengaluruTrafficAI_Technical_Report.tex` into a publication-quality PDF using any of the free methods below.

---

### Method 1: Free Online Compilation via Overleaf (Recommended)
1. Navigate to [Overleaf](https://www.overleaf.com/) and create a free account.
2. Click **New Project** $\rightarrow$ **Upload Project**.
3. Create a ZIP archive of the `docs/interview-handbook/` folder (including `BengaluruTrafficAI_Technical_Report.tex` and the `chapters/` folder) and upload it.
4. Set the compiler to **pdfLaTeX** (default) in Menu $\rightarrow$ Settings.
5. Click **Recompile**.
6. Download the compiled `BengaluruTrafficAI_Technical_Report.pdf`.

---

### Method 2: Local Command-Line Compilation (TeXLive / MacTeX / MiKTeX)
If you have a TeX distribution installed on your local machine, run the following commands from the `docs/interview-handbook/` directory:

```bash
cd docs/interview-handbook

# First pass: generate auxiliary files and table of contents
pdflatex -interaction=nonstopmode BengaluruTrafficAI_Technical_Report.tex

# Second pass: resolve cross-references and numbering
pdflatex -interaction=nonstopmode BengaluruTrafficAI_Technical_Report.tex

# Third pass (optional, ensures complete reference resolution):
pdflatex -interaction=nonstopmode BengaluruTrafficAI_Technical_Report.tex
```

---

### Method 3: Containerized Compilation via Docker
You can compile the report in a self-contained Docker container without installing TeX on your host operating system:

```bash
# From the repository root:
docker run --rm -v "%cd%/docs/interview-handbook:/work" -w /work texlive/texlive:latest pdflatex -interaction=nonstopmode BengaluruTrafficAI_Technical_Report.tex
```

---

## 📖 How to Study This Handbook for Interviews

1. **Step 1: Rapid Orientation (Chapters 1, 24, and 26)**
   - Read **Chapter 1 (Executive Summary)** to internalize the overarching system narrative.
   - Practice the **30-second and 60-second spoken scripts** in **Chapter 24** until you can deliver them naturally.
   - Review the **One-Page Rapid Revision Sheet** in **Chapter 26** for a concise memory refresher.

2. **Step 2: Technical Deep Dive (Chapters 4--16)**
   - Study the **dual-mode architecture** in Chapter 5 to understand why `backend/app.py` and `backend/app_demo.py` are separate.
   - Trace the **computer vision pipeline** in Chapters 9--13 (YOLOv8 inference, IoU greedy tracking, speed estimation, violation deduplication).
   - Review **dynamic signal allocation** and safety clamping in Chapter 14.
   - Inspect **congestion classification** and synthetic model provenance in Chapter 15.

3. **Step 3: Whiteboard and Math Practice (Chapter 25)**
   - Work through the step-by-step mathematical exercises on paper:
     - IoU computation between overlapping bounding boxes.
     - Greedy association matrix selection.
     - Pixel-to-speed conversion and bounds clamping.
     - Proportional signal green allocation with min/max safety guards.
     - Great-circle Haversine distance calculation.

4. **Step 4: Tiered Interview Simulation (Chapter 23)**
   - Test yourself on all **62 interview questions**:
     - **Level 1 (Beginner):** Foundational concepts, API design, tech stack rationale.
     - **Level 2 (Intermediate):** Concurrency, tracking lifecycles, signal math, RF training mechanics.
     - **Level 3 (Advanced):** Trade-offs, cold-start handling, coordinate edge cases, perspective distortion.
     - **Level 4 (Deep Follow-Ups):** Architecture defense, debugging strategies, production scaling, and limitation handling.

5. **Step 5: Code Verification (Chapter 19)**
   - Run the automated test suite locally to verify that all 46 test cases pass:
     ```bash
     python -m unittest discover tests -v
     ```
