# Product Requirements Document (PRD)
## Intelligent EV Charging & Route Optimization System — Bhubaneswar

| Field | Value |
|---|---|
| Document version | 1.0 |
| Status | Draft for lab submission |
| Scope | Bhubaneswar city, Odisha, India |
| Stack | Python (Streamlit), SQLite, scikit-learn, XGBoost |

---

## 1. Overview

The Intelligent EV Charging & Route Optimization System is a web application that helps electric vehicle (EV) drivers in Bhubaneswar decide **whether they need to charge** before reaching a destination and **where to charge** along the way. It combines a battery-sufficiency prediction, a route-corridor station filter, and a station waiting-time prediction to recommend up to three charging stations, with estimated wait time, charging time, cost, and a one-tap navigation link.

## 2. Problem Statement

EV drivers in Indian cities face three recurring problems:

1. **Range uncertainty:** Drivers cannot easily tell if the current battery will last the trip, since drain depends on distance, speed, temperature, and AC usage.
2. **Poor station discovery:** Existing maps list stations by proximity, not by whether they are actually on the way to the destination.
3. **Unknown waiting time:** Drivers reach a station only to find it crowded, wasting time and battery.

## 3. Goals and Non-Goals

### 3.1 Goals
- Predict whether a charge stop is needed for a given trip.
- Recommend up to 3 operational stations that lie along the route with minimal detour.
- Estimate wait time, charge time, and cost for each recommended station.
- Let users keep a history of past trips.
- Secure user accounts with hashed passwords and token-based sessions.

### 3.2 Non-Goals (Out of Scope for MVP)
- Real-time station availability or live occupancy data.
- Turn-by-turn navigation inside the app (Google Maps link is used instead).
- Booking or payment for charging sessions.
- Multi-city or national coverage.
- Mobile native apps.
- Real vehicle telemetry (OBD / manufacturer API) integration.
- Admin dashboard or station-owner portal.
- Social login, email verification, password reset.

## 4. Target Users

| Persona | Description | Key Need |
|---|---|---|
| **Daily commuter** | EV owner commuting across Bhubaneswar (e.g., KIIT ↔ city center) | Avoid range anxiety on routine trips |
| **Occasional EV driver** | Rental or new EV owner unfamiliar with local stations | Find a reliable nearby charging stop |
| **Student / evaluator** | Reviewer of the lab project | Clear, working demonstration of ML plus web stack |

## 5. User Stories

| ID | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | new user | register with username, email, and password | I can use the system |
| US-02 | registered user | log in and log out securely | my data stays private |
| US-03 | driver | enter my battery %, distance, speed, temperature, and AC status | the system can assess my trip |
| US-04 | driver | choose a destination from presets or enter a name | I can plan quickly |
| US-05 | driver | be told whether I need to charge before arriving | I can decide to stop or continue |
| US-06 | driver | see up to 3 on-route stations with distance from me | I choose a convenient stop |
| US-07 | driver | see estimated wait time, charge time, and cost per station | I can compare options |
| US-08 | driver | open directions to a station in Google Maps | I can navigate immediately |
| US-09 | returning user | view my past trips and recommended stations | I can revisit earlier plans |

## 5.1 User Journey (Summary)

Register → Login → Dashboard (enter trip details) → Submit → Results (charge verdict + station cards) → Get Directions / Plan another trip / View history → Logout.

## 6. Core Features

| # | Feature | Description | MVP |
|---|---|---|---|
| F1 | Authentication | Register, login, logout; bcrypt password hashing; Streamlit session state | ✅ |
| F2 | Trip input dashboard | Form for start/destination names, battery %, distance, speed, temperature, AC | ✅ |
| F3 | Battery sufficiency prediction | Random Forest classifier returns "needs charge" yes/no | ✅ |
| F4 | Route-corridor station filter | Haversine-based detour test selects stations near the straight-line path | ✅ |
| F5 | Wait-time prediction | XGBoost regressor estimates wait using hour, weekday, connectors, charger kW | ✅ |
| F6 | Charge time and cost estimate | Rule-based: 40 kWh battery assumption, ₹8.5 per kWh | ✅ |
| F7 | Directions link | Google Maps URL to the selected station | ✅ |
| F8 | Trip history | Per-user list of past trips | ✅ |

## 7. MVP Scope

**Included:** F1–F8 above, for Bhubaneswar only, using a cleaned station CSV and models trained on simulated data.

**Deliberately minimal:** Streamlit single-page app, SQLite (no external DB), straight-line route corridor (no road routing API).

## 8. Success Metrics

| Metric | Target |
|---|---|
| Battery model accuracy on held-out test split | ≥ 90% |
| Demand model MAE on held-out split | ≤ 6 minutes |
| End-to-end result time after form submit | < 2 seconds |
| Core flow completion (register → result → history) in demo | 100%, no errors |
| Stations returned when ≥ 1 exists in corridor | Always, up to 3 |
| Passwords stored in plain text | 0 |

> **Note:** Accuracy and MAE are measured on **simulated** data, so they show the pipeline works, not real-world performance.

## 9. Assumptions

1. Users are in Bhubaneswar and have a modern browser.
2. The station dataset includes latitude, longitude, charger type, kW rating, connector count, and operational status.
3. Battery capacity is fixed at 40 kWh for all vehicles.
4. Electricity cost is a flat ₹8.5 per kWh.
5. Training data is synthetic, standing in for real telemetry and session logs.
6. Straight-line distance (Haversine) is an acceptable approximation of road distance for the MVP.
7. Browser geolocation may be denied; the system falls back to a default City Center location.

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Models trained on synthetic data | Predictions not reliable in the real world | State limitation clearly; document path to real data |
| Dataset has missing or wrong coordinates | Wrong or no stations | Preprocessing drops invalid rows; sample CSV fallback |
| Straight-line corridor ignores roads | Station may not be conveniently reachable | Show Google Maps directions; list as future work |
| No station within corridor | Empty results | Friendly message; allow wider corridor later |
| Secret key leaked | Session forgery | Keep in `.env`, exclude from Git |
| Fixed battery and tariff assumptions | Inaccurate cost and time | Label as estimates; make configurable later |

## 11. Out-of-Scope Features (Future Work)

- Real road routing and ETA (Google Maps / OSRM API).
- Live charger availability and queue data.
- Per-vehicle profiles (battery capacity, efficiency).
- Station reviews and ratings.
- Reservation and payment.
- Email verification and password reset.
- Admin panel for managing stations.
- Multi-city expansion.

## 12. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-01 | A new user can register with a valid username, email, and password of 8+ characters; duplicate email is rejected with a clear message. |
| AC-02 | A registered user can log in; wrong credentials show "Invalid email or password." |
| AC-03 | Unauthenticated access to `/dashboard`, `/predict`, and `/history` redirects to `/login`. |
| AC-04 | Submitting battery % outside 1–100 or distance ≤ 0 shows a validation error and no prediction runs. |
| AC-05 | A valid submission displays the needs-charge verdict (warning or success banner). |
| AC-06 | Results list up to 3 stations sorted by distance from the car, each with name, address, distance, charger type/kW, wait time, charge time, and cost. |
| AC-07 | "Get Directions" opens Google Maps with the station as destination. |
| AC-08 | Each successful prediction creates one history record visible only to that user on `/history`. |
| AC-09 | `/logout` clears the session cookie and redirects to `/login`. |
| AC-10 | Passwords are stored only as bcrypt hashes; the secret key is read from `.env`. |
| AC-11 | `/docs` loads the FastAPI Swagger UI. |

---

*End of PRD*