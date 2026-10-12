# 🌱 AgroVolt — Smart Agrovoltaic Management System

A full-stack web app that predicts crop yield, forecasts solar energy output,
and recommends irrigation schedules for agrovoltaic farms using ML models.

---

## 🛠️ Tech Stack

| Layer     | Technology                             |
|-----------|----------------------------------------|
| Backend   | FastAPI (Python)                       |
| ML Models | XGBoost, Random Forest, LSTM (planned) |
| Database  | SQLite (dev) / PostgreSQL Neon (prod)  |
| Frontend  | React + Vite + Tailwind CSS            |
| Charts    | Recharts                               |
| State     | Zustand                                |
| HTTP      | Axios                                  |

---

## 🚀 How to Run

### Step 1 — Clone / Open in VS Code
Open the `agrovolt/` folder in VS Code.

---

### Step 2 — Backend Setup

Open a **new terminal** in VS Code (Terminal → New Terminal).

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create database tables
python init_db.py

# Train ML models (takes ~30 seconds)
python ../ml_notebooks/train_models.py

# Start the backend server
uvicorn app.main:app --reload
```

✅ Backend runs at: http://localhost:8000
✅ Swagger API docs: http://localhost:8000/docs

---

### Step 3 — Frontend Setup

Open a **second terminal** in VS Code.

```bash
cd frontend

# Install packages
npm install

# Start the React dev server
npm run dev
```

✅ Frontend runs at: http://localhost:5173

---

### Step 4 — Add API Key (optional but recommended)

Edit `backend/.env`:
```
OPENWEATHER_API_KEY=your_key_from_openweathermap.org
```

Without the key, weather data shows mock values so everything still works.

---

## 📁 Project Structure

```
agrovolt/
├── backend/               ← FastAPI Python server
│   ├── app/
│   │   ├── main.py        ← Entry point
│   │   ├── api/routes/    ← crop, solar, irrigation, weather, farms
│   │   ├── ml/            ← XGBoost, LSTM, Random Forest logic
│   │   ├── models/        ← Pydantic schemas
│   │   ├── database/      ← SQLAlchemy ORM + CRUD
│   │   └── utils/         ← Weather + NASA API helpers
│   ├── models_saved/      ← Trained .pkl files (generated after training)
│   ├── requirements.txt
│   └── .env               ← API keys (never push to GitHub!)
│
├── frontend/              ← React + Vite + Tailwind
│   └── src/
│       ├── pages/         ← Home, Predict, Analytics, Settings
│       ├── components/    ← Navbar, Charts, Cards
│       ├── api/           ← Axios client
│       └── store/         ← Zustand global state
│
└── ml_notebooks/          ← Model training scripts
    └── train_models.py
```

---

## 🤖 ML Models

| Model | Algorithm | Purpose |
|-------|-----------|---------|
| Crop Yield | XGBoost Regressor | Predict kg/hectare |
| Irrigation | Random Forest Classifier | Classify irrigation need |
| Solar Forecast | LSTM (time series) | 7-day kWh forecast |

---

## 🔑 APIs Used

| API | Key Required | Used For |
|-----|-------------|----------|
| OpenWeatherMap | Yes (free) | Live weather data |
| NASA POWER | No | Solar irradiance data |

---

## 📦 Deployment

- **Backend** → Render (free tier)
- **Frontend** → Vercel (free tier)
- **Database** → Neon PostgreSQL (free tier)
