# System Architecture Document
## Intelligent EV Charging & Route Optimization System — Bhubaneswar

| Field | Value |
|---|---|
| Document version | 1.0 |
| Based on | PRD v1.0, SRS v1.0 |
| Architecture style | Monolith, Streamlit single-page app |

---

## 1. Architecture Goals

1. **Simple and demonstrable:** one process, one command to run, no external services.
2. **Secure by default:** hashed passwords, Streamlit session state, secrets in `.env`, ORM-only DB access.
3. **Fast responses:** models and station data are loaded once at startup.
4. **Replaceable parts:** ML models, station data, and database can be swapped without rewriting the app.

**Deliberately avoided (over-engineering):** microservices, message queues, Docker orchestration, a separate frontend SPA, Redis, a cloud database.

---

## 2. Recommended Technology Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.9+ | One language for web and ML |
| Web framework | Streamlit | Fast prototyping, built-in UI components |
| Database | SQLite | Zero setup; file-based |
| ORM | SQLAlchemy | Prevents SQL injection; clean models |
| Auth | passlib (bcrypt) + Streamlit session state | Standard password hashing, simple session management |
| ML | scikit-learn (RandomForest), XGBoost (regressor) | Classification and regression |
| Data handling | pandas, numpy | CSV loading, filtering |
| Model storage | joblib `.pkl` files | Simple persistence |
| Config | python-dotenv | Secrets outside the code |

---

## 3. High-Level System Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                           │
│  Streamlit UI (auto-rendered) · Geolocation API                 │
│  Session state (managed by Streamlit)                           │
└───────────────┬──────────────────────────────▲─────────────────┘
                │ WebSocket / HTTP             │ UI updates
                ▼                              │
┌────────────────────────────────────────────────────────────────┐
│                  STREAMLIT APPLICATION                          │
│                                                                 │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────────┐  │
│  │  main.py  │→ │  auth.py  │  │  utils.py │  │ predictor.py │  │
│  │  views    │  │ hash/state│  │ haversine │  │  ML wrapper  │  │
│  └─────┬─────┘  └───────────┘  │ corridor  │  └──────┬───────┘  │
│        │                       └─────┬─────┘         │          │
│        ▼                             ▼               ▼          │
│  ┌───────────┐              ┌──────────────┐  ┌─────────────┐   │
│  │ models.py │              │ stations_df  │  │ battery.pkl │   │
│  │ SQLAlchemy│              │ (in memory)  │  │ demand.pkl  │   │
│  └─────┬─────┘              └──────▲───────┘  └─────────────┘   │
│        │                           │ loaded once at startup      │
└────────┼───────────────────────────┼────────────────────────────┘
         ▼                           │
 ┌──────────────┐          ┌─────────┴─────────┐
 │  ev_app.db   │          │ data/cleaned_data │
 │   (SQLite)   │          │       .csv        │
 └──────────────┘          └───────────────────┘

 External (link only):  Google Maps directions URL
```

---

## 4. System Components

| Component | File | Responsibility |
|---|---|---|
| **App entry** | `run.py` | Starts Streamlit on port 8501 |
| **Main app** | `app/main.py` | All Streamlit views, orchestrates auth, prediction, DB |
| **Configuration** | `app/config.py` | Reads secrets and settings from `.env` |
| **Authentication** | `app/auth.py` | Password hashing, session state management |
| **Data models** | `app/models.py` | Engine, session factory, `User` and `TripHistory`, `get_db()` |
| **Utilities** | `app/utils.py` | Haversine distance, corridor filter |
| **Predictor** | `app/predictor.py` | Loads `.pkl` models; wait time, needs-charge, charge time and cost |
| **ML training** | `ml/*.py` | Offline scripts that produce the models; not run by the server |

### 4.1 Layering

```
Presentation   →  Streamlit components (st.*, pages)
Controller     →  app/main.py
Domain logic   →  app/utils.py, app/predictor.py
Security       →  app/auth.py
Persistence    →  app/models.py → SQLite
Offline ML     →  ml/ → .pkl files → loaded by predictor.py
```

---

## 5. Frontend

- **Approach:** Streamlit single-page app with sidebar navigation and conditional rendering based on session state.
- **Interactivity:** Streamlit widgets (st.text_input, st.slider, st.selectbox, st.button) handle user input; browser geolocation via JavaScript injection if needed.
- **Styling:** Streamlit's built-in theming with optional custom CSS via st.markdown.
- **Views:** login, register, dashboard, results, history (rendered conditionally in one app).

## 6. Backend

- **Framework:** Streamlit with session state for user authentication.
- **State management:** `st.session_state` stores user credentials and current view.
- **View protection:** each protected view checks `st.session_state.get('authenticated')` and shows login if False.
- **Startup:** loads `cleaned_data.csv` into a DataFrame and calls `create_tables()`; `predictor.py` loads both models at import.

## 7. Database

**Engine:** SQLite file at `database/ev_app.db`, created automatically.

```
┌───────────────────────┐          ┌─────────────────────────────┐
│ users                 │          │ trip_history                │
├───────────────────────┤          ├─────────────────────────────┤
│ id (PK)               │          │ id (PK)                     │
│ username (unique)     │          │ user_email  ─ ─ ─ ─ ─ ─ ─ ─┼─ ─ logical link to users.email
│ email (unique)        │ 1      * │ start_loc                   │
│ password_hash         │──────────│ destination                 │
└───────────────────────┘          │ battery_pct                 │
                                   │ station_rec                 │
                                   │ created_at                  │
                                   └─────────────────────────────┘
```

> The link between the tables is by email (no foreign key constraint) to keep the MVP simple. A future version should use `user_id` as a real foreign key.

## 8. View Design

| View | Auth | Purpose |
|---|---|---|
| Login | – | Login form |
| Register | – | Registration form |
| Dashboard | ✅ | Trip form |
| Results | ✅ | Prediction results |
| History | ✅ | User's past trips |

## 9. Authentication Flow

```
Register:  form → validate → bcrypt hash → INSERT users → set session_state['authenticated'] = True
Login:     form → find user by email → verify bcrypt hash
                → set session_state['authenticated'] = True, session_state['user_email'], session_state['username']
Request:   check session_state['authenticated']
                → True? show view : show login
Logout:    clear session_state → show login
```

## 10. Data Flow — Main Prediction Request

```
1. User submits dashboard form (button click)
2. Verify session_state['authenticated'] → user email
3. Validate battery % and distance
4. predict_needs_charge(battery, distance, speed, temp, ac)   → 0 / 1
5. filter_stations_on_route(car, dest, stations_df)           → candidate stations
6. Take nearest 3; for each:
      predict_wait_time(connectors, kW)                       → wait (min)
      estimate_charge_time_and_cost(battery, kW)              → time, ₹
      build Google Maps URL
7. INSERT TripHistory (user_email, start, dest, battery, top station)
8. Render results view with verdict + recommendations
```

## 11. ML Components

| Model | Algorithm | Training script | Artifact | Used by |
|---|---|---|---|---|
| Battery sufficiency | RandomForestClassifier (150 trees, depth 8) | `ml/train_battery_model.py` | `ml/battery_model.pkl` | `predict_needs_charge` |
| Station wait time | XGBRegressor (200 estimators, lr 0.05, depth 5) | `ml/train_demand_model.py` | `ml/demand_model.pkl` | `predict_wait_time` |

- **Training is offline.** The server only loads `.pkl` files.
- **Data is simulated** for the MVP; real telemetry and session logs are the upgrade path.
- **Rule-based pieces:** charge time and cost use fixed assumptions (40 kWh battery, ₹8.5/kWh).

## 12. Storage

| Data | Location | Notes |
|---|---|---|
| Users and trips | `database/ev_app.db` | Auto-created; excluded from Git |
| Stations | `data/bhubaneswar_stations.csv` → `data/cleaned_data.csv` | Cleaned by `ml/preprocess.py` |
| Training data | `data/raw_charging_sessions.csv` | Optional; used to explore or replace simulation |
| Models | `ml/*.pkl` | Generated artifacts |
| Secrets | `.env` | Never committed |

## 13. Security Architecture

| Threat | Control |
|---|---|
| Password theft from DB | bcrypt hashing with per-password salt |
| Session theft via JavaScript | Streamlit manages session state server-side |
| SQL injection | SQLAlchemy ORM only |
| XSS | Streamlit's built-in sanitization |
| Unauthorized access | Session state check on every protected view |
| Leaked secrets | `.env` in `.gitignore` |
| Information leakage | Generic login error; no stack traces in responses |

**Known gaps for production:** CSRF tokens, rate limiting on login, account lockout, password reset, HTTPS termination.

## 14. Deployment

### 14.1 Development / Lab (primary target)
```
streamlit run app/main.py   →   http://localhost:8501
```
Or:
```
python run.py   →   http://localhost:8501
```
Single machine, virtual environment, SQLite file.

### 14.2 Optional Simple Hosting
| Item | Recommendation |
|---|---|
| Host | Streamlit Cloud, or any VM/PaaS that runs Python |
| Command | `streamlit run app/main.py --server.port $PORT` |
| HTTPS | Provided by Streamlit Cloud or configured via reverse proxy |
| Secrets | Set as environment variables or Streamlit secrets |
| Persistence | Mount a persistent volume for `database/ev_app.db` |
| Models and data | Commit `.pkl` and CSV, or regenerate in the build step |

## 15. Monitoring and Logging

| Need | Approach (MVP) |
|---|---|
| Request logs | Streamlit console output |
| Application errors | Python `logging` module to console; avoid logging passwords or session data |
| Model sanity | Print metrics at training time; startup fails loudly if a model file is missing |
| Later upgrade | Log to file, add Sentry or monitoring if deployed publicly |

## 16. Scalability

| Concern | Current limit | Upgrade path |
|---|---|---|
| Concurrent users | Suited to tens of users (single process, SQLite) | Streamlit Cloud with multiple instances + PostgreSQL |
| Station count | Row-by-row Python loop is fine for hundreds to a few thousand | Vectorise with NumPy, add a spatial index, or use PostGIS |
| Model inference | Fast in-process | Separate model service only if models grow large |
| Routing accuracy | Straight-line corridor | OSRM or Google Directions for road distance |
| Live data | None | Add live availability feed and cache |

## 17. Key Design Decisions

| Decision | Alternative considered | Why this choice |
|---|---|---|
| Streamlit SPA | React / Vue SPA or FastAPI/Jinja2 | Fewer moving parts; no build tooling; faster ML prototyping |
| SQLite | PostgreSQL | No setup for a lab; same ORM allows later switch |
| Streamlit session state | JWT in cookie | Simpler for MVP; managed by framework |
| Haversine corridor | Road routing API | Free, offline, explainable |
| Offline model training | Train at startup | Faster startup; reproducible artifacts |
| Google Maps link | Embedded map | No API key or billing |

---

*End of Architecture Document*