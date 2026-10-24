# ⚡ Intelligent EV Charging & Route Optimization System

A Streamlit web application that helps electric vehicle drivers in **Bhubaneswar, India** decide whether they need to charge before reaching a destination, and where to charge along the way.

Given the current battery level, distance, speed, temperature and AC usage, the system predicts whether a charging stop is needed, finds charging stations along the route, and estimates the waiting time, charging time and cost at each one.

> Built for academic lab submission — Bhubaneswar city scope.

---

## ✨ Features

- **User accounts:** register, log in and log out with bcrypt-hashed passwords
- **Battery prediction:** a Random Forest model predicts whether the car needs to charge before arriving
- **Route-aware station search:** shows only stations near the path from your location to the destination
- **Wait-time prediction:** an XGBoost model estimates the queue at each station
- **Charge time and cost estimate:** based on charger power and remaining battery
- **Directions:** one-click Google Maps link to the chosen station
- **Trip history:** every search is saved per user

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Streamlit |
| Frontend | Streamlit components, HTML/CSS custom styling |
| Database | SQLite via SQLAlchemy |
| ML | scikit-learn (RandomForest), XGBoost |
| Auth | passlib (bcrypt), Streamlit session state |
| Data | pandas, numpy, joblib |

Recommended Python version: **3.12** (3.9 or above is required).

---

## 📁 Project Structure

```
ev-charging-system/
│
├── app/
│   ├── __init__.py               # App initialization
│   ├── main.py                   # Streamlit app entry
│   ├── models.py                 # SQLAlchemy DB models (User, TripHistory)
│   ├── auth.py                   # Login, register, session state logic
│   ├── utils.py                  # Haversine distance, route corridor filter
│   ├── predictor.py              # ML model loader and prediction functions
│   └── config.py                 # Settings loaded from .env
│
├── ml/
│   ├── train_battery_model.py    # Train battery drain prediction model
│   ├── train_demand_model.py     # Train station waiting time model
│   ├── battery_model.pkl         # Saved battery model (generated after training)
│   ├── demand_model.pkl          # Saved demand model (generated after training)
│   └── preprocess.py             # Data cleaning script
│
├── data/
│   ├── bhubaneswar_stations.csv  # EV station dataset filtered to Bhubaneswar
│   ├── raw_charging_sessions.csv # Raw training data
│   └── cleaned_data.csv          # Cleaned version used for training
│
├── database/
│   └── ev_app.db                 # SQLite DB (auto-created on first run)
│
├── .env                          # Secret keys — never commit this
├── .gitignore
├── requirements.txt              # All Python packages
├── run.py                        # Entry point to start the Streamlit app
└── README.md
```

---

## 🚀 Setup and Installation

### 1. Create and activate a virtual environment

```bash
cd ev-charging-system
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# Mac / Linux (bash or zsh)
source venv/bin/activate

# Linux with fish shell
source venv/bin/activate.fish
```

### 2. Install the packages

```bash
pip install -r requirements.txt
```

If you are starting without a `requirements.txt`:

```bash
pip install fastapi uvicorn jinja2 python-multipart sqlalchemy "passlib[bcrypt]" "python-jose[cryptography]" scikit-learn xgboost pandas numpy joblib python-dotenv aiofiles email-validator
pip freeze > requirements.txt
```

> If you see a bcrypt / passlib version error, run `pip install bcrypt==4.0.1`.

### 3. Create the `.env` file

Create a file named `.env` in the project root:

```
SECRET_KEY=replace_this_with_a_long_random_string
DATABASE_URL=sqlite:///./database/ev_app.db
```

Generate a strong secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Create the database tables

```bash
python -c "from app.models import create_tables; create_tables(); print('Database and tables created successfully')"
```

### 5. Prepare the station data

Place your station file at `data/bhubaneswar_stations.csv` with these columns:

```
station_id, station_name, latitude, longitude, charger_type,
charger_rating_kw, total_connectors, address, is_operational, city
```

Then clean it:

```bash
python ml/preprocess.py
```

This creates `data/cleaned_data.csv`.

### 6. Train the ML models

```bash
python ml/train_battery_model.py
python ml/train_demand_model.py
```

This creates `ml/battery_model.pkl` and `ml/demand_model.pkl`.

### 7. Run the application

```bash
streamlit run app/main.py
```

Or using the run script:

```bash
python run.py
```

Open in your browser:

| URL | Purpose |
|---|---|
| http://localhost:8501 | Application |

Run all commands from the **project root folder**, otherwise the `.env`, CSV and model paths will not be found.

---

## 🧭 How to Use

1. On the sidebar, select **Register** and create an account.
2. Log in with your credentials.
3. On the main dashboard, enter your starting location, destination, battery %, distance, speed, temperature and AC status.
4. Click **Find Charging Stations**.
5. Read the verdict (charge needed or not) and the recommended stations with distance, wait time, charge time and cost.
6. Click **Get Directions** to open Google Maps.
7. Visit the **History** tab to see earlier trips.

---

## 🤖 How It Works

```
Trip form → battery model (needs charge?) 
          → filter stations near the route (Haversine detour test)
          → for the nearest 3: predict wait time + estimate charge time and cost
          → save trip to history → show results
```

| Component | Method |
|---|---|
| Needs charge? | RandomForestClassifier on battery %, distance, speed, temperature, AC |
| Wait time | XGBRegressor on hour, weekday, connectors, charger kW, weekend flag |
| On-route stations | A station qualifies if going via it adds no more than 5 km to the direct trip |
| Charge time and cost | Assumes a 40 kWh battery and ₹8.5 per kWh |

---

## 🔒 Security Summary

| What | How it is handled |
|---|---|
| Passwords | Hashed with bcrypt via passlib, never stored as plain text |
| Sessions | Streamlit session state for user authentication |
| Secret key | Loaded from `.env`, never hardcoded |
| SQL injection | All queries go through the SQLAlchemy ORM |
| Route protection | Session state checked before allowing access to protected pages |
| Input validation | Server-side checks on battery % and distance |

---

## 📌 Bhubaneswar Coordinates Reference

| Location | Latitude | Longitude |
|---|---|---|
| City Center | 20.2961 | 85.8245 |
| Bhubaneswar Railway Station | 20.2662 | 85.8354 |
| Biju Patnaik Airport (BBI) | 20.2444 | 85.8178 |
| Infocity / IT Hub | 20.3469 | 85.8141 |
| KIIT University | 20.3549 | 85.8194 |
| Kalinga Stadium | 20.2711 | 85.8082 |
| Patia Square | 20.3508 | 85.8189 |

---

## ✅ Pre-Demo Checklist

```
[ ] venv is activated
[ ] pip install done, requirements.txt exists
[ ] .env file created with SECRET_KEY
[ ] data/bhubaneswar_stations.csv is in place
[ ] python ml/preprocess.py → cleaned_data.csv generated
[ ] python ml/train_battery_model.py → battery_model.pkl generated
[ ] python ml/train_demand_model.py → demand_model.pkl generated
[ ] streamlit run app/main.py → server starts on port 8501 without errors
[ ] Register a test account and log in
[ ] Submit the dashboard form → results show stations
[ ] "Get Directions" opens Google Maps
[ ] History tab shows the trip just made
[ ] Logout functionality works
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | Run commands from the project root; start with `streamlit run app/main.py` |
| `FileNotFoundError: ml/battery_model.pkl` | Run both training scripts first |
| `FileNotFoundError: data/cleaned_data.csv` | Run `python ml/preprocess.py` |
| No stations on results | Check the CSV has Bhubaneswar rows with valid latitude and longitude, and `is_operational` set to True |
| bcrypt / passlib error | `pip install bcrypt==4.0.1` |
| `.env` values not read | File must be named exactly `.env` and sit in the project root |
| Model file fails to load | Retrain the models in the same Python and package versions you run the app with |
| `unable to open database file` | Make sure the `database/` folder exists |
| Streamlit not found | Make sure streamlit is installed: `pip install streamlit` |

---

## ⚠️ Limitations

- The ML models are trained on **simulated data**, so reported accuracy shows that the pipeline works, not real-world performance.
- The route corridor uses **straight-line distance**, not actual roads.
- Battery capacity (40 kWh) and electricity price (₹8.5/kWh) are fixed assumptions.
- Wait times are estimates, not live occupancy.
- No CSRF protection, rate limiting or password reset.
- SQLite suits a single-user or lab setup only.

## 🔭 Future Work

- Real vehicle telemetry and real charging-session data for model training
- Road routing (OSRM or Google Directions) instead of a straight-line corridor
- Live station availability
- Per-vehicle profiles (battery capacity and efficiency)
- CSRF tokens, secure cookies over HTTPS and login rate limiting
- PostgreSQL and Docker for deployment
- Multi-city support

---

## 📄 Documentation

Project documents: PRD, SRS, System Architecture, UI/UX Design and Development Plan.

---

*Backend: Streamlit · Database: SQLite · ML: scikit-learn + XGBoost*