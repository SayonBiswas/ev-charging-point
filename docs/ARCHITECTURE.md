# System Architecture Document
## Intelligent EV Charging & Route Optimization System — Bhubaneswar

| Field | Value |
|---|---|
| Document version | 1.0 |
| Based on | PRD v1.0, SRS v1.0 |
| Architecture style | Monolith, server-rendered (FastAPI + Jinja2) |

---

## 1. Architecture Goals

1. **Simple and demonstrable:** one process, one command to run, no external services.
2. **Secure by default:** hashed passwords, httpOnly JWT cookie, secrets in `.env`, ORM-only DB access.
3. **Fast responses:** models and station data are loaded once at startup.
4. **Replaceable parts:** ML models, station data, and database can be swapped without rewriting the app.

**Deliberately avoided (over-engineering):** microservices, message queues, Docker orchestration, a separate frontend SPA, Redis, a cloud database.

---

## 2. Recommended Technology Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.9+ | One language for web and ML |
| Web framework | FastAPI | Fast, typed, auto-generated `/docs` |
| Server | Uvicorn | ASGI server, `reload` for development |
| Templating / Frontend | Jinja2 + HTML + CSS + vanilla JS | No build step; easy to explain in a lab |
| Database | SQLite | Zero setup; file-based |
| ORM | SQLAlchemy | Prevents SQL injection; clean models |
| Auth | passlib (bcrypt) + python-jose (JWT) | Standard, well-tested |
| ML | scikit-learn (RandomForest), XGBoost (regressor) | Classification and regression |
| Data handling | pandas, numpy | CSV loading, filtering |
| Model storage | joblib `.pkl` files | Simple persistence |
| Config | python-dotenv | Secrets outside the code |

---

## 3. High-Level System Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                           │
│  HTML pages (Jinja2-rendered) · style.css · main.js             │
│  Geolocation API · cookie: access_token (httpOnly JWT)          │
└───────────────┬──────────────────────────────▲─────────────────┘
                │ HTTP (forms, GET/POST)       │ HTML responses
                ▼                              │
┌────────────────────────────────────────────────────────────────┐
│                  FASTAPI APPLICATION (Uvicorn)                  │
│                                                                 │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────────┐  │
│  │  main.py  │→ │  auth.py  │  │  utils.py │  │ predictor.py │  │
│  │  routes   │  │ hash/JWT  │  │ haversine │  │  ML wrapper  │  │
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
| **App entry** | `run.py` | Starts Uvicorn on port 8000 with reload |
| **Routes / controller** | `app/main.py` | All HTTP routes, orchestrates auth, prediction, DB, templates |
| **Configuration** | `app/config.py` | Reads secrets and settings from `.env` |
| **Authentication** | `app/auth.py` | Password hashing, token creation, cookie-based user lookup |
| **Data models** | `app/models.py` | Engine, session factory, `User` and `TripHistory`, `get_db()` |
| **Schemas** | `app/schemas.py` | Pydantic input/output shapes and validation |
| **Utilities** | `app/utils.py` | Haversine distance, corridor filter |
| **Predictor** | `app/predictor.py` | Loads `.pkl` models; wait time, needs-charge, charge time and cost |
| **ML training** | `ml/*.py` | Offline scripts that produce the models; not run by the server |
| **Templates** | `templates/*.html` | Server-rendered views |
| **Static assets** | `static/css`, `static/js` | Styling and small client script |

### 4.1 Layering

```
Presentation   →  templates/, static/
Controller     →  app/main.py
Domain logic   →  app/utils.py, app/predictor.py
Security       →  app/auth.py
Persistence    →  app/models.py → SQLite
Offline ML     →  ml/ → .pkl files → loaded by predictor.py
```

---

## 5. Frontend

- **Approach:** server-side rendered pages with Jinja2 template inheritance (`base.html` → other pages). `login.html` and `register.html` are standalone.
- **Interactivity:** `main.js` handles preset-destination coordinates, browser geolocation, and a basic battery range check.
- **Styling:** a single `style.css` with CSS variables and a mobile breakpoint.
- **Pages:** login, register, dashboard, results, history.

## 6. Backend

- **Framework:** FastAPI with `Form(...)` parameters for HTML form posts.
- **Dependency injection:** `Depends(get_db)` gives each request its own DB session.
- **Route protection:** each protected route calls `get_current_user_from_cookie(request)` and redirects to `/login` when it returns `None`.
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

## 8. API / Route Design

| Method | Path | Auth | Purpose | Response |
|---|---|---|---|---|
| GET | `/` | – | Redirect | 307 → `/dashboard` |
| GET | `/register` | – | Registration form | HTML |
| POST | `/register` | – | Create account | 302 → `/login` or HTML with error |
| GET | `/login` | – | Login form | HTML |
| POST | `/login` | – | Authenticate, set cookie | 302 → `/dashboard` or HTML with error |
| GET | `/logout` | – | Clear cookie | 302 → `/login` |
| GET | `/dashboard` | ✅ | Trip form | HTML |
| POST | `/predict` | ✅ | Run prediction, save history | HTML (results) |
| GET | `/history` | ✅ | User's past trips | HTML |
| GET | `/docs` | – | Swagger UI | HTML |
| GET | `/static/*` | – | CSS and JS | Static files |

## 9. Authentication Flow

```
Register:  form → validate → bcrypt hash → INSERT users → redirect /login
Login:     form → find user by email → verify bcrypt hash
                → create JWT {sub: email, username, exp} → Set-Cookie httpOnly
                → redirect /dashboard
Request:   cookie → jose.decode(SECRET_KEY, ALGORITHM)
                → valid? email : None → redirect /login
Logout:    delete cookie → redirect /login
```

## 10. Data Flow — Main Prediction Request

```
1. User submits dashboard form  ──────────────►  POST /predict
2. Verify cookie → user email
3. Validate battery % and distance
4. predict_needs_charge(battery, distance, speed, temp, ac)   → 0 / 1
5. filter_stations_on_route(car, dest, stations_df)           → candidate stations
6. Take nearest 3; for each:
      predict_wait_time(connectors, kW)                       → wait (min)
      estimate_charge_time_and_cost(battery, kW)              → time, ₹
      build Google Maps URL
7. INSERT TripHistory (user_email, start, dest, battery, top station)
8. Render results.html with verdict + recommendations
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
| Session theft via JavaScript | `httpOnly` cookie |
| Token forgery | JWT signed with secret from `.env` |
| SQL injection | SQLAlchemy ORM only |
| XSS | Jinja2 auto-escaping |
| Unauthorized access | Cookie check on every protected route |
| Long-lived sessions | Token expiry (60 min, configurable) |
| Leaked secrets | `.env` in `.gitignore` |
| Information leakage | Generic login error; no stack traces in responses |

**Known gaps for production:** CSRF tokens, `secure` and `samesite` cookie flags over HTTPS, rate limiting on login, account lockout, password reset, HTTPS termination.

## 14. Deployment

### 14.1 Development / Lab (primary target)
```
python run.py   →   http://localhost:8000
```
Single machine, virtual environment, SQLite file, `reload=True`.

### 14.2 Optional Simple Hosting
| Item | Recommendation |
|---|---|
| Host | Any VM or PaaS that runs Python (Render, Railway, a small VPS) |
| Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (no `--reload`) |
| HTTPS | Provided by the host or a reverse proxy (Nginx / Caddy) |
| Secrets | Set as environment variables on the host instead of `.env` |
| Persistence | Mount a persistent volume for `database/ev_app.db` |
| Models and data | Commit `.pkl` and CSV, or regenerate in the build step |

## 15. Monitoring and Logging

| Need | Approach (MVP) |
|---|---|
| Request logs | Uvicorn access log in the console |
| Application errors | Python `logging` module to console; avoid logging passwords or tokens |
| Health check | Optional `GET /health` returning `{"status": "ok"}` |
| Model sanity | Print metrics at training time; startup fails loudly if a model file is missing |
| Later upgrade | Log to file, add Sentry or Prometheus if deployed publicly |

## 16. Scalability

| Concern | Current limit | Upgrade path |
|---|---|---|
| Concurrent users | Suited to tens of users (single process, SQLite) | Multiple Uvicorn workers + PostgreSQL |
| Station count | Row-by-row Python loop is fine for hundreds to a few thousand | Vectorise with NumPy, add a spatial index, or use PostGIS |
| Model inference | Fast in-process | Separate model service only if models grow large |
| Routing accuracy | Straight-line corridor | OSRM or Google Directions for road distance |
| Live data | None | Add live availability feed and cache |
| Static files | Served by FastAPI | Serve via CDN or Nginx |

## 17. Key Design Decisions

| Decision | Alternative considered | Why this choice |
|---|---|---|
| Server-rendered Jinja2 | React / Vue SPA | Fewer moving parts; no build tooling |
| SQLite | PostgreSQL | No setup for a lab; same ORM allows later switch |
| JWT in cookie | Server sessions | Stateless; httpOnly protects from JS access |
| Haversine corridor | Road routing API | Free, offline, explainable |
| Offline model training | Train at startup | Faster startup; reproducible artifacts |
| Google Maps link | Embedded map | No API key or billing |

---

*End of Architecture Document*