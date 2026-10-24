# Development Plan
## Intelligent EV Charging & Route Optimization System — Bhubaneswar

| Field | Value |
|---|---|
| Document version | 1.0 |
| Based on | PRD, SRS, Architecture, UI/UX (v1.0) |
| Target | Working MVP ready for lab demonstration |
| Suggested duration | ~8 working days (adjust to your deadline) |

---

## 1. Roadmap Overview

| Phase | Name | Output | Est. time |
|---|---|---|---|
| 0 | Setup | Project folder, venv, packages, `.env`, Git | 0.5 day |
| 1 | Backend foundation | `config`, `models`, `auth`, DB created | 1 day |
| 2 | Data and ML | Cleaned stations, 2 trained `.pkl` models | 2 days |
| 3 | Core logic | `utils.py`, `predictor.py` working in isolation | 1 day |
| 4 | Streamlit app | `main.py` with all views and session state | 1.5 days |
| 5 | Integration and testing | End-to-end flow passes all tests | 1.5 days |
| 6 | Bug fixing and polish | Stable build, README | 0.5 day |
| 7 | Deployment and demo prep | Runs cleanly on demo machine; optional hosting | 0.5 day |

```
Setup → Backend → Data/ML → Core logic → Streamlit app → Testing → Polish → Demo
```

---

## 2. Priorities

| Priority | Items |
|---|---|
| **P0 — Must have (MVP)** | Auth, DB, station cleaning, both models, corridor filter, prediction view, results view, history view, README |
| **P1 — Should have** | Input validation limits (speed, temp), submit-button loading state, helpful startup error messages, `.gitignore` |
| **P2 — Nice to have** | Custom CSS styling, preserved form values after error, logging |
| **P3 — Future (not in MVP)** | Road routing API, live availability, PostgreSQL, Docker |

---

## 3. Dependency Map

```
.env + config.py
      │
      ├─► models.py ─► database created ─┐
      ├─► auth.py ───────────────────────┤
      │                                  │
data CSV ─► preprocess.py ─► cleaned_data.csv ─┐
                                               │
train_battery_model.py ─► battery_model.pkl ─┐ │
train_demand_model.py  ─► demand_model.pkl  ─┤ │
                                             ▼ ▼
                            utils.py + predictor.py
                                      │
                                      ▼
                                   main.py (Streamlit)
                                      │
                                      ▼
                                 integration tests ─► demo
```

Rule: **never start a file before the files it depends on exist and run.**

---

## 4. Detailed Phases and Tasks

### Phase 0 — Setup (0.5 day)
- [ ] Check Python version (3.9+)
- [ ] Create `ev-charging-system/` and a virtual environment
- [ ] Install all packages (add `email-validator`)
- [ ] Create the folder structure and empty files
- [ ] Create `.env` and `.gitignore` (exclude `.env`, `venv/`, `__pycache__/`, `database/*.db`)
- [ ] Initialise Git; first commit
- [ ] `pip freeze > requirements.txt`

**Done when:** `python -c "import streamlit, sklearn, xgboost"` runs without error.

### Phase 1 — Backend Foundation (1 day)
- [ ] `app/config.py`
- [ ] `app/models.py` (User, TripHistory, `create_tables`, `get_db`)
- [ ] Run the create-tables command; confirm `database/ev_app.db` exists
- [ ] `app/auth.py` (hash, verify, token, cookie reader)
- [ ] `app/schemas.py`, `app/__init__.py`
- [ ] Quick Python check: hash a password, verify it, create and decode a token

**Done when:** tables exist in SQLite and the hash/token round trip works.

### Phase 2 — Data and ML (2 days)
- [ ] Obtain `data/bhubaneswar_stations.csv` (real dataset or synthetic fallback; label it clearly)
- [ ] Confirm required columns exist
- [ ] `ml/preprocess.py` → run → `data/cleaned_data.csv`
- [ ] Check station count is greater than 0 and coordinates look right
- [ ] (Optional) generate `data/raw_charging_sessions.csv`
- [ ] `ml/train_battery_model.py` → run → `ml/battery_model.pkl`
- [ ] `ml/train_demand_model.py` → run → `ml/demand_model.pkl`
- [ ] Reload both models in a Python shell and run a test prediction

**Done when:** cleaned CSV has stations, both `.pkl` files load, and battery accuracy and demand MAE meet the PRD targets (≥ 90% and ≤ 6 min).

### Phase 3 — Core Logic (1 day)
- [ ] `app/utils.py`: `haversine`, `filter_stations_on_route`
- [ ] Test haversine: City Center → Railway Station ≈ 3.5–4 km
- [ ] Test corridor filter with KIIT → Railway Station; confirm sorted output
- [ ] `app/predictor.py`: `predict_needs_charge`, `predict_wait_time`, `estimate_charge_time_and_cost`
- [ ] Test: battery 60%, 22 kW → 16 kWh, ~43.6 min, ₹136.00

**Done when:** all three predictor functions return sensible values from a Python shell.

### Phase 4 — Streamlit App (1.5 days)
- [ ] App setup: static mount, templates, load `stations_df`, `create_tables()`
- [ ] Register routes (GET/POST) with validation
- [ ] Login, logout routes with cookie handling
- [ ] `/` redirect, `/dashboard`
- [ ] `/predict` with validation, ML calls, history save
- [ ] `/history`
- [ ] `run.py`; start the server; open `/docs` and confirm routes are listed
- [ ] (P1) Add speed and temperature validation to `/predict`
- [ ] (P1) Add `/health`

**Done when:** `/docs` shows all routes and the server starts without errors.

### Phase 5 — Frontend (2 days)
- [ ] `templates/base.html`
- [ ] `login.html`, `register.html`
- [ ] `dashboard.html` with preset destinations
- [ ] `results.html` with verdict banner and station cards
- [ ] `history.html` with empty state
- [ ] `static/js/main.js` (preset coords, geolocation, battery check, submit loading state)
- [ ] `static/css/style.css` using tokens from the UI/UX document
- [ ] Check at 360 px, 768 px, and desktop widths

**Done when:** every page renders correctly in the browser and matches the UI/UX document.

### Phase 6 — Integration and Testing (1.5 days)
Run test cases **T-01 to T-20** from the SRS (Section 11). Record pass/fail in a table.

Priority checks:
- [ ] Register → login → dashboard → predict → results → history → logout
- [ ] Protected routes redirect when logged out
- [ ] Validation errors for bad battery or distance
- [ ] No-stations message
- [ ] Two users cannot see each other's history
- [ ] Google Maps link opens the correct station

**Done when:** all P0 tests pass.

### Phase 7 — Bug Fixing and Polish (0.5 day)
- [ ] Fix failures from Phase 6
- [ ] Known items to check: bcrypt/passlib version warning (pin `bcrypt==4.0.1` if needed), Jinja2 `TemplateResponse` signature differences in newer Starlette versions, error templates missing the `user` variable
- [ ] Handle `None` or NaN values in station rows
- [ ] Write `README.md` (setup steps, features, limitations)
- [ ] Clean up code comments; remove debug prints

**Done when:** no known P0 or P1 bugs remain.

### Phase 8 — Deployment and Demo Prep (0.5 day)
- [ ] Fresh-machine test: clone, create venv, install, train, run
- [ ] Prepare a demo account and 2–3 trip scenarios (low battery, enough battery, no stations)
- [ ] Prepare a short explanation of the two ML models and their limitations
- [ ] (Optional) deploy to a simple host (see Architecture section 14)
- [ ] Take screenshots for the report

**Done when:** the demo runs end to end on the presentation machine.

---

## 5. Milestones

| # | Milestone | Success check | Target day |
|---|---|---|---|
| M1 | Environment ready | Imports work, structure created | Day 1 |
| M2 | Backend foundation | DB created, auth functions verified | Day 2 |
| M3 | ML models trained | Both `.pkl` files saved, metrics acceptable | Day 4 |
| M4 | Core logic verified | Station filter and predictor tested in shell | Day 5 |
| M5 | API complete | All routes working at `/docs` | Day 6 |
| M6 | UI complete | All 5 pages match the design | Day 8 |
| M7 | MVP tested | Test table T-01…T-20 completed | Day 9 |
| M8 | Demo ready | README, screenshots, fresh-run verified | Day 10 |

---

## 6. MVP Scope (Frozen)

**In:** registration, login, logout, trip form, battery prediction, route-corridor filter (max 3 stations), wait/charge/cost estimates, Google Maps link, trip history, FastAPI docs.

**Out:** live availability, road routing, booking/payment, admin panel, password reset, multi-city, mobile apps, CSRF, Docker.

> Any new idea during development goes to a "Later" list, not into the MVP.

---

## 7. Testing Strategy

| Level | What | How |
|---|---|---|
| Unit (manual shell) | `haversine`, corridor filter, predictor functions, hash/verify, token create/decode | Python shell snippets |
| Integration | Route → auth → ML → DB → template | Browser walkthrough |
| Acceptance | SRS tests T-01 to T-20 | Table with pass/fail and notes |
| Cross-device | 360 px mobile and desktop | Browser dev tools |
| Security checks | Plain-text password absent, cookie `HttpOnly`, protected routes redirect | DB viewer, browser dev tools |
| Optional automated | `pytest` with FastAPI `TestClient` for auth and `/predict` | Add if time permits |

**Suggested test scenarios**

| Scenario | Input | Expected |
|---|---|---|
| Low battery, long trip | 10%, 100 km | Warning banner, stations shown |
| Healthy battery, short trip | 95%, 10 km | Success banner, stations still shown |
| Invalid battery | 0 or 101 | Error message |
| Invalid distance | −5 | Error message |
| Far-off destination | Destination outside the city | May return no stations |
| Full battery | 100% | Charge time and cost = 0 |

---

## 8. Bug Fixing Process

1. Reproduce and note the steps.
2. Log it in a bug table (ID, description, severity, status).
3. Fix in priority order: **crash → security → wrong output → UI → cosmetic**.
4. Re-run the related test case, then the full flow once.
5. Commit with a clear message (`fix: redirect missing for /history when logged out`).

| Severity | Meaning |
|---|---|
| Critical | App will not start or core flow broken |
| High | Wrong prediction, security hole, data leak |
| Medium | Validation or display problem |
| Low | Styling or wording |

---

## 9. Risks and Contingency

| Risk | Likelihood | Contingency |
|---|---|---|
| Real station dataset is unavailable or messy | Medium | Use the synthetic Bhubaneswar CSV; label it |
| Library version conflicts (bcrypt, Starlette) | Medium | Pin versions in `requirements.txt` |
| ML metrics look "too perfect" on simulated data | High | Explain in the report that data is synthetic |
| Time runs short | Medium | Cut P2 and P3 items; never cut P0 |
| Geolocation blocked | Low | Defaults to City Center |
| Demo machine has no internet | Low | App runs offline; only the Maps link needs internet |

---

## 10. Definition of Done

**A task is done when:**
- the code runs without errors,
- it matches the SRS requirement and UI/UX design,
- it has been tested at least once manually,
- comments are present and debug prints are removed.

**The MVP is done when all of the following are true:**
- [ ] `python run.py` starts without errors on a fresh setup
- [ ] A new user can register, log in, plan a trip, view results, view history, and log out
- [ ] Battery verdict, up to 3 stations, wait time, charge time, and cost all display
- [ ] "Get Directions" opens Google Maps at the correct station
- [ ] Protected routes redirect when logged out
- [ ] Validation errors display for invalid input
- [ ] Passwords are stored only as bcrypt hashes; the secret key is in `.env`
- [ ] Tests T-01 to T-20 are executed and results recorded
- [ ] `README.md` explains setup, usage, and limitations
- [ ] Known limitations (synthetic data, straight-line corridor, fixed battery and tariff) are documented

---

## 11. Command Cheat Sheet

```bash
# Setup
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # Mac/Linux
pip install -r requirements.txt

# Create DB tables
python -c "from app.models import create_tables; create_tables()"

# Data and ML
python ml/preprocess.py
python ml/train_battery_model.py
python ml/train_demand_model.py

# Run
python run.py                    # http://localhost:8000
                                 # http://localhost:8000/docs
```

---

## 12. Suggested Git Commit Sequence

1. `chore: project structure, venv, requirements`
2. `feat: config and database models`
3. `feat: authentication utilities`
4. `feat: data preprocessing`
5. `feat: battery and demand models`
6. `feat: route filter and predictor`
7. `feat: FastAPI routes`
8. `feat: templates, css, js`
9. `test: acceptance tests and fixes`
10. `docs: README and final polish`

---

*End of Development Plan*