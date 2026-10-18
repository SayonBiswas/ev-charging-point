# Software Requirements Specification (SRS)
## Intelligent EV Charging & Route Optimization System — Bhubaneswar

| Field | Value |
|---|---|
| Document version | 1.0 |
| Based on | PRD v1.0 |
| Status | Draft for lab submission |

---

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements of the Intelligent EV Charging & Route Optimization System, so it can be designed, built, and tested without ambiguity.

### 1.2 Scope
A server-rendered web application for Bhubaneswar that predicts whether an EV needs charging for a trip and recommends up to three on-route stations with estimated wait time, charge time, and cost.

### 1.3 Definitions

| Term | Meaning |
|---|---|
| EV | Electric vehicle |
| JWT | JSON Web Token used for session identity |
| Corridor | Region around the straight line from start to destination in which stations are considered "on route" |
| Haversine | Formula for great-circle distance between two lat/lon points |
| kW / kWh | Charger power / energy |

### 1.4 Technology Constraints
Python 3.9+, FastAPI, Uvicorn, Jinja2, SQLAlchemy with SQLite, scikit-learn, XGBoost, pandas, joblib, passlib (bcrypt), python-jose.

---

## 2. Overall Description

### 2.1 System Context
Browser (user) ⇄ FastAPI app ⇄ SQLite DB, station CSV, and two trained model files (`.pkl`). Google Maps is only linked to, not integrated through an API.

### 2.2 User Roles and Permissions

| Role | Description | Permissions |
|---|---|---|
| **Guest** | Not logged in | View `/login`, `/register`; nothing else |
| **Registered User** | Logged in with a valid token | Dashboard, prediction, own history, logout |

There is no admin role in the MVP.

### 2.3 Assumptions and Dependencies
- Cleaned station data exists at `data/cleaned_data.csv` before the server starts.
- Both model files exist at `ml/battery_model.pkl` and `ml/demand_model.pkl`.
- `.env` provides `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DATABASE_URL`.

---

## 3. Functional Requirements

### 3.1 Registration

| ID | Requirement |
|---|---|
| FR-1.1 | The system shall provide a registration page at `GET /register`. |
| FR-1.2 | `POST /register` shall accept `username`, `email`, `password`. |
| FR-1.3 | The system shall reject a password shorter than 8 characters and re-display the form with an error. |
| FR-1.4 | The system shall reject an email that already exists and re-display the form with an error. |
| FR-1.5 | On success the system shall store the user with a bcrypt-hashed password and redirect to `/login` (HTTP 302). |

### 3.2 Login / Logout

| ID | Requirement |
|---|---|
| FR-2.1 | `GET /login` shall display the login form. |
| FR-2.2 | `POST /login` shall verify email and password against the stored hash. |
| FR-2.3 | On failure the system shall re-display the form with "Invalid email or password." without revealing which field was wrong. |
| FR-2.4 | On success the system shall create a JWT containing the email (`sub`) and username, set it as an `httpOnly` cookie named `access_token` (max age 3600 s), and redirect to `/dashboard`. |
| FR-2.5 | `GET /logout` shall delete the cookie and redirect to `/login`. |
| FR-2.6 | `GET /` shall redirect to `/dashboard`. |

### 3.3 Dashboard (Trip Input)

| ID | Requirement |
|---|---|
| FR-3.1 | `GET /dashboard` shall require authentication; otherwise redirect to `/login`. |
| FR-3.2 | The form shall collect: start name, destination name, preset destination, battery %, distance (km), speed (km/h), temperature (°C), AC on/off. |
| FR-3.3 | Selecting a preset destination shall populate hidden destination latitude and longitude fields. |
| FR-3.4 | The page shall attempt to populate the car's coordinates using browser geolocation; if unavailable or denied, defaults to City Center (20.2961, 85.8245). |
| FR-3.5 | Defaults: speed 60 km/h, temperature 30 °C, AC off. |

### 3.4 Battery Sufficiency Prediction

| ID | Requirement |
|---|---|
| FR-4.1 | `POST /predict` shall require authentication. |
| FR-4.2 | The system shall call the battery model with `battery_pct`, `distance_remaining_km`, `speed_kmh`, `temp_celsius`, `ac_on`. |
| FR-4.3 | The model shall return `1` (needs charge) or `0` (safe to continue). |
| FR-4.4 | The results page shall show a warning banner for `1` and a success banner for `0`. |

### 3.5 Station Filtering

| ID | Requirement |
|---|---|
| FR-5.1 | The system shall load stations from `data/cleaned_data.csv` once at startup. |
| FR-5.2 | A station is **on route** if `d(car, station) + d(station, destination) ≤ d(car, destination) + corridor_km`, with default `corridor_km = 5.0`. |
| FR-5.3 | Distances shall be computed with the Haversine formula (Earth radius 6371 km). |
| FR-5.4 | The result shall be sorted by distance from the car ascending and shall include `distance_from_car_km` and `distance_to_dest_km` rounded to 2 decimals. |
| FR-5.5 | Only the nearest 3 on-route stations shall be shown. |
| FR-5.6 | If no stations qualify, the system shall display a "No charging stations found" message. |

### 3.6 Wait Time, Charge Time, and Cost

| ID | Requirement |
|---|---|
| FR-6.1 | Wait time shall be predicted by the demand model from: current hour, current weekday, station connectors, charger kW, weekend flag. |
| FR-6.2 | Wait time shall be rounded to 1 decimal minute. |
| FR-6.3 | Energy needed (kWh) = `(100 − battery_pct) / 100 × 40`. |
| FR-6.4 | Charge time (min) = `energy_needed / charger_kW × 60`, rounded to 1 decimal. |
| FR-6.5 | Cost (₹) = `energy_needed × 8.5`, rounded to 2 decimals. |
| FR-6.6 | If a station lacks `total_connectors` or `charger_rating_kw`, defaults of 4 and 22 kW shall be used. |

### 3.7 Results Display

| ID | Requirement |
|---|---|
| FR-7.1 | Each station card shall show: rank, name, address, distance from car, charger type, kW, wait time, charge time, cost. |
| FR-7.2 | Each card shall include a "Get Directions" link to `https://www.google.com/maps/dir/?api=1&destination=<lat>,<lon>` opening in a new tab. |
| FR-7.3 | The page shall offer "Plan Another Trip" and "View History" actions. |

### 3.8 Trip History

| ID | Requirement |
|---|---|
| FR-8.1 | Each successful prediction shall save: user email, start name, destination name, battery %, top recommended station name (or "None"), UTC timestamp. |
| FR-8.2 | `GET /history` shall require authentication and list only the current user's trips, newest first. |

---

## 4. User Roles and Route Access Matrix

| Route | Method | Guest | User |
|---|---|---|---|
| `/` | GET | Redirect | Redirect to dashboard |
| `/register` | GET, POST | ✅ | ✅ |
| `/login` | GET, POST | ✅ | ✅ |
| `/logout` | GET | ✅ | ✅ |
| `/dashboard` | GET | ❌ → `/login` | ✅ |
| `/predict` | POST | ❌ → `/login` | ✅ |
| `/history` | GET | ❌ → `/login` | ✅ |
| `/docs` | GET | ✅ (dev only) | ✅ |

---

## 5. Business Rules

| ID | Rule |
|---|---|
| BR-1 | Email is the unique account identifier. |
| BR-2 | Only operational stations in Bhubaneswar are eligible for recommendation. |
| BR-3 | A maximum of 3 stations is recommended per request. |
| BR-4 | Battery capacity is assumed 40 kWh; tariff is ₹8.5 per kWh. |
| BR-5 | Training label rule for the battery model: `needs_charge = 1` when `battery_pct / distance_remaining_km < 0.45`. |
| BR-6 | Users can see only their own trip history. |
| BR-7 | All cost and time values are estimates, not guarantees. |

---

## 6. Data Requirements

### 6.1 Database (SQLite via SQLAlchemy)

**Table `users`**

| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, indexed |
| username | String(80) | Unique, not null |
| email | String(120) | Unique, not null |
| password_hash | String(256) | Not null |

**Table `trip_history`**

| Column | Type | Constraints |
|---|---|---|
| id | Integer | PK, indexed |
| user_email | String(120) | Not null |
| start_loc | String(200) | |
| destination | String(200) | |
| battery_pct | Float | |
| station_rec | String(200) | |
| created_at | DateTime | Default UTC now |

### 6.2 Station Dataset (`data/bhubaneswar_stations.csv`)

`station_id, station_name, latitude, longitude, charger_type, charger_rating_kw, total_connectors, address, is_operational, city`

### 6.3 Cleaned Dataset (`data/cleaned_data.csv`)
Same columns after removing rows with missing latitude/longitude, non-Bhubaneswar rows, and non-operational stations.

### 6.4 Model Features

| Model | Inputs | Output |
|---|---|---|
| Battery (RandomForestClassifier) | battery_pct, distance_remaining_km, speed_kmh, temp_celsius, ac_on | needs_charge (0/1) |
| Demand (XGBRegressor) | hour_of_day, day_of_week, total_connectors, charger_rating_kw, is_weekend | wait_minutes |

---

## 7. Input Validation Rules

| Field | Rule | Error message |
|---|---|---|
| username | Required, 3–80 characters | "Username is required." |
| email | Required, valid email format, unique | "Email already registered." |
| password | Minimum 8 characters | "Password must be at least 8 characters." |
| battery_pct | Number, 1–100 | "Battery % must be between 1 and 100." |
| distance_km | Number, > 0 | "Distance must be greater than 0." |
| speed_kmh | Number, > 0, ≤ 200 | "Speed must be between 1 and 200." |
| temp | Number, −10 to 60 | "Temperature out of range." |
| ac_on | 0 or 1 | "Invalid AC value." |
| latitude / longitude | Valid numbers within −90..90 / −180..180 | "Invalid coordinates." |

All validation shall be performed **server-side**; client-side checks are only a convenience.

---

## 8. Authentication and Authorization

| ID | Requirement |
|---|---|
| AUTH-1 | Passwords shall be hashed with bcrypt via passlib; plain text is never stored or logged. |
| AUTH-2 | Sessions shall use a JWT signed with `SECRET_KEY` and `ALGORITHM` from `.env`. |
| AUTH-3 | The JWT shall be stored in an `httpOnly` cookie so JavaScript cannot read it. |
| AUTH-4 | The token shall expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60). |
| AUTH-5 | Every protected route shall decode and verify the cookie before rendering; invalid or expired tokens are treated as logged out. |
| AUTH-6 | Authorization is ownership-based: history queries filter by the token's email. |

---

## 9. Error Handling and Edge Cases

| Scenario | Expected behaviour |
|---|---|
| Missing or invalid cookie | Redirect to `/login` |
| Expired token | Redirect to `/login` |
| Validation failure | Re-render the same page with an error message; no prediction and no DB write |
| No stations on route | Show "no stations found" message; still save the trip with `station_rec = "None"` |
| Fewer than 3 stations on route | Show only those available |
| Missing `.pkl` model files | Server fails to start with a clear message naming the training script to run |
| Missing `cleaned_data.csv` | Server fails to start with a clear message to run `ml/preprocess.py` |
| Geolocation denied | Use default City Center coordinates |
| Destination equals start (distance ≈ 0 km) | Still valid; stations within the corridor are returned |
| Battery 100% | Charge time and cost = 0 |
| Station missing connectors/kW | Use defaults (4 connectors, 22 kW) |
| Database unavailable | Return HTTP 500 with a generic error page; no stack trace shown |
| Duplicate form submission | Creates a separate history row (accepted for MVP) |

---

## 10. Non-Functional Requirements

### 10.1 Security

| ID | Requirement |
|---|---|
| SEC-1 | Secrets must be read from `.env` and never committed to source control. |
| SEC-2 | All DB access shall use the SQLAlchemy ORM (no string-built SQL) to prevent SQL injection. |
| SEC-3 | Jinja2 auto-escaping shall remain enabled to prevent XSS. |
| SEC-4 | Cookies shall be `httpOnly`; `secure` and `samesite` flags shall be enabled when deployed over HTTPS. |
| SEC-5 | CSRF protection is **not** implemented in the MVP and is listed as a known limitation. |
| SEC-6 | Error responses shall not expose stack traces or internal paths. |

### 10.2 Performance

| ID | Requirement |
|---|---|
| PERF-1 | `/predict` shall respond within 2 seconds for a station set of up to 1,000 rows. |
| PERF-2 | Models and station data shall be loaded once at startup, not per request. |
| PERF-3 | Pages shall load in under 1 second on a local network. |

### 10.3 Usability and Compatibility

| ID | Requirement |
|---|---|
| USE-1 | Interface shall work on current Chrome, Firefox, and Edge, and be responsive down to 360 px width. |
| USE-2 | Every form field shall have a visible label or placeholder. |
| USE-3 | Errors shall be shown in plain language near the form. |

### 10.4 Reliability and Maintainability

| ID | Requirement |
|---|---|
| REL-1 | Database tables shall be auto-created on first run. |
| MNT-1 | Code shall be organised per the project folder structure with comments on each function. |
| MNT-2 | Dependencies shall be pinned in `requirements.txt`. |

---

## 11. Testable Acceptance Criteria

| ID | Linked requirements | Test | Expected result |
|---|---|---|---|
| T-01 | FR-1.3 | Register with a 5-character password | Error shown; no user created |
| T-02 | FR-1.4 | Register twice with the same email | Second attempt rejected |
| T-03 | FR-1.5, AUTH-1 | Register valid user, inspect DB | `password_hash` starts with `$2b$`; plain text absent |
| T-04 | FR-2.3 | Login with wrong password | "Invalid email or password." |
| T-05 | FR-2.4, AUTH-3 | Login, inspect cookie | `access_token` set, `HttpOnly` flag present |
| T-06 | AUTH-5 | Open `/dashboard` with no cookie | Redirected to `/login` |
| T-07 | FR-2.5 | Visit `/logout`, then `/dashboard` | Redirected to `/login` |
| T-08 | Section 7 | Submit battery = 0 / 101 | Validation error; no history row |
| T-09 | Section 7 | Submit distance = −5 | Validation error; no history row |
| T-10 | FR-4.3, FR-4.4 | Battery 10%, distance 100 km | Warning banner shown |
| T-11 | FR-4.4 | Battery 95%, distance 10 km | Success banner shown |
| T-12 | FR-5.2, FR-5.5 | Valid trip with many stations | At most 3 stations, sorted by distance from car |
| T-13 | FR-5.6 | Trip in a corridor with no stations | "No charging stations found" message |
| T-14 | FR-6.3–6.5 | Battery 60%, 22 kW charger | Energy 16 kWh; time ≈ 43.6 min; cost ₹136.00 |
| T-15 | FR-7.2 | Click "Get Directions" | Google Maps opens in a new tab with the station as destination |
| T-16 | FR-8.1, FR-8.2 | Make 2 trips, open `/history` | Two rows, newest first |
| T-17 | BR-6 | Log in as user B | User A's trips are not visible |
| T-18 | REL-1 | Delete DB file, restart | DB and tables recreated automatically |
| T-19 | PERF-1 | Submit trip with 1,000-row station file | Response in under 2 seconds |
| T-20 | USE-1 | View dashboard at 360 px width | No horizontal scrolling; form usable |

---

## 12. Known Limitations

1. ML models are trained on **simulated** data; metrics do not reflect real-world accuracy.
2. The route corridor uses straight-line distance, not actual roads.
3. Battery capacity (40 kWh) and tariff (₹8.5/kWh) are fixed assumptions.
4. Wait time is a model estimate, not live occupancy.
5. No CSRF protection, rate limiting, or account recovery.
6. SQLite is suitable for single-instance lab use only.

---

*End of SRS*