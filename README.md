# ECGViewer
This project implements a full-stack ECG episode viewer and lightweight arrhythmia classification pipeline as described in the TriFetch take-home assignment.

It includes: 
- A React + Vite frontend for browsing episodes and visualizing ECG traces
- A FastAPI backend for dataset indexing, ECG loading, ML inference, and event-start detection
- A hybrid 5-fold ensemble classifier (RandomForest + XGBoost + SVM)
- A scalable and explainable event onset detector
- A design focused on clarity, simplicity, maintainability, and speed

The purpose of this assignment is not ML performance, but demonstrating clear end-to-end architecture and thoughtful engineering tradeoffs.
```
🗂️ Project Structure
backend/
  app/
    main.py
    ecg_loader.py
    hybrid_ensemble_classifier.py
    event_detector.py
    models/
      hybrid_ensemble.pkl

frontend/
  src/
    App.tsx
    main.tsx
    index.css
    styles.css
    components/
```
## 🛠️ Setup Instructions
1️⃣ Backend (FastAPI)
Install dependencies
cd backend
pip install -r requirements.txt

Run the server
```uvicorn app.main:app --reload```

API Endpoints
Endpoint	Description
GET /events	List all episodes with metadata
GET /events/{id}	Load episode metadata, ECG signal, model prediction, and event-start index

The backend trains (or loads) the 5-fold ensemble on startup and indexes all ECG episodes for fast lookup.

2️⃣ Frontend (React + Vite)
Install dependencies
```
cd frontend
npm install
```
Start dev server
```
npm run dev
```
Build for production
```
npm run build
npm run preview
```

## Features
Scrollable sidebar grouped by arrhythmia type
AFIB / VTACH / PAUSE
Approved / Rejected

Hovering an episode highlights the predicted event window

Clicking loads:
Event metadata
ML predicted arrhythmia class
Event start marker in the ECG trace

Clean ECG visualization using Recharts, downsampled for responsiveness

## 🧠 Technical Choices & Reasoning
1. Frontend Architecture
React + Vite

Vite provides extremely fast dev server performance and a lightweight build system—ideal for a demo application.

UI Principles

Match the TriFetch UI reference as closely as possible

Sidebar navigation is prioritized for clinical usability

ECG plot is spacious, with clear event markers

Interactions (hover + click) help reviewers quickly identify events

Styling

I used vanilla CSS (index.css + styles.css) to maintain clarity, avoid Tailwind overhead, and ensure predictable styling during the short development window.

2. Backend Architecture (FastAPI)
- Why FastAPI
Built-in type checking
High performance + clean routing
Dataset Indexing
On startup, the backend: (1) Recursively scans all event folders. (2) Loads each event.json and all ECG text files. (3) Builds a searchable in-memory index. (4) Provides fast retrieval for UI queries. This prevents repeated filesystem reads and keeps latency minimal.

3. ECG Loading & Downsampling

Raw ECG files are:
3× 30 seconds
200 Hz sampling


4. Machine Learning Pipeline
   
✔ Hybrid 5-Fold Ensemble

The classifier trains 15 models total:
5× RandomForest
5× XGBoost
5× SVM (RBF kernel)

Each fold trains one of each model type, computes validation accuracy, and saves them.
Prediction uses majority vote across all 15 models, which stabilizes the output and reduces overfitting.

✔ Feature Engineering
For each ECG signal, I extract:

Mean, std, max, min for both channels
Average absolute derivative (rhythm variation)
Amplitude range features
These give simple, interpretable signal characteristics suitable for tabular ML.

✔ Why a Hybrid Ensemble?

RandomForest → low variance
XGBoost → strong performance on tabular data
SVM → robustness on small feature sets
Ensemble → smooths out model biases

Excellent tradeoff between speed and stability for an assignment like this.
Acheives an average of 0.92 F1 on 5-Fold Cross Validation ![Accuracy summary](https://i.ibb.co/BRkcRND/image.png)

5. Event-Start Detection

A lightweight anomaly-based event-start detector:

Compute baseline mean from early portion of the signal

Slide a short window across the trace

Measure deviation from baseline

Peak deviation = predicted event onset

- Advantages:

No training required

Simple and explainable

Fast enough for real-time use

Matches assignment requirements

## 🔮 Future Improvements (Optional Scope)

If given more time, I would explore:

- Modeling

A compact 1D CNN / ResNet for raw waveform classification

A class-specific onset detector (AFIB vs VTACH require different logic)

Improved pre-processing (bandpass filters, R-peak detection)

- Frontend

Zoom/pan support in ECG viewer

Annotations or AI-generated explanations

Confidence scores and uncertainty intervals

- Backend

Caching for repeated ECG accesses

Parallel loading + async request handling

Move to WFDB-compatible ECG parsing
