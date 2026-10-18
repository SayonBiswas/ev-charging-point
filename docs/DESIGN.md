# UI/UX Design Document
## Intelligent EV Charging & Route Optimization System — Bhubaneswar

| Field | Value |
|---|---|
| Document version | 1.0 |
| Based on | PRD v1.0, SRS v1.0, Architecture v1.0 |
| Design goals | Simple, modern, implementation-ready (plain HTML + CSS + vanilla JS) |

---

## 1. Design Principles

1. **One task per screen:** enter trip → see answer → act.
2. **Answer first:** the results page opens with the verdict (charge needed or not) before the details.
3. **Few inputs, sensible defaults:** speed 60, temperature 30, AC off, so only battery and distance are essential.
4. **Clear feedback:** every error appears next to the form in plain language.
5. **Mobile-first:** drivers use phones; every page works at 360 px width.
6. **No dead ends:** every page has a clear next action.

---

## 2. User Journey

```
Open app
   │
   ├─ not logged in ──► Login ──(no account)──► Register ──► Login
   │
   ▼
Dashboard: enter trip details
   │  Submit
   ▼
Results: verdict banner + up to 3 station cards
   │
   ├─ "Get Directions" ──► Google Maps (new tab)
   ├─ "Plan Another Trip" ──► Dashboard
   └─ "View History" ──► History ──► Dashboard
   
Logout (from navbar, any time) ──► Login
```

---

## 3. Navigation

| Element | Where | Items |
|---|---|---|
| **Top navbar** (logged-in pages) | Fixed at top | Brand "⚡ EV Charging System" (left) · Home · History · Logout (right) |
| **Auth pages** | No navbar | Cross-links: Login ⇄ Register |
| **Mobile (< 600 px)** | Navbar wraps; links stay visible in a single row with smaller padding | No hamburger needed (only 3 links) |
| **Active link** | Highlight current page link | Underline or bold in primary color |

---

## 4. Screens

### 4.1 Login (`login.html`)
**Purpose:** authenticate returning users.

```
┌──────────────────────────────┐
│     ⚡ EV Charging System     │
│            Login             │
│  [ error message if any ]    │
│  ┌────────────────────────┐  │
│  │ Email                  │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ Password               │  │
│  └────────────────────────┘  │
│  [        Login           ]  │
│  Don't have an account?      │
│  Register here               │
└──────────────────────────────┘
```

### 4.2 Register (`register.html`)
Same layout as Login with fields: Username, Email, Password (hint: "At least 8 characters"), button **Register**, link "Already have an account? Login".

### 4.3 Dashboard (`dashboard.html`)
**Purpose:** collect trip details.

```
┌───────────────────────────────────────────┐
│ ⚡ EV Charging System     Home History Logout │
├───────────────────────────────────────────┤
│  Plan Your EV Trip in Bhubaneswar          │
│  [ error message if any ]                  │
│                                            │
│  Starting Location Name   [____________]   │
│  Destination Name         [____________]   │
│  Select Destination       [ Pick ▾     ]   │
│  Current Battery %        [____]           │
│  Distance to Destination  [____] km        │
│  Current Speed            [ 60 ] km/h      │
│  Outside Temperature      [ 30 ] °C        │
│  AC Running?              [ No ▾ ]         │
│                                            │
│  [   Find Charging Stations →   ]          │
└───────────────────────────────────────────┘
```
Hidden fields: `car_lat`, `car_lon`, `dest_lat`, `dest_lon`.

### 4.4 Results (`results.html`)
**Purpose:** give the verdict and the recommended stations.

```
┌───────────────────────────────────────────┐
│ Trip: KIIT University → Railway Station    │
│ Current battery: 45%                       │
│ ┌───────────────────────────────────────┐  │
│ │ ⚠️ Battery predicted to run low ...    │  │  ← amber (or green ✅)
│ └───────────────────────────────────────┘  │
│ Recommended Charging Stations On Your Route│
│ ┌───────────────────────────────────────┐  │
│ │ 1. Station Name                        │  │
│ │ 📍 Address — 2.4 km from you           │  │
│ │ ⚡ DC · 50 kW                           │  │
│ │ ⏳ Wait: 12 min  🔋 Charge: ~26 min     │  │
│ │ 💰 ₹187.00                              │  │
│ │ [ Get Directions → ]                    │  │
│ └───────────────────────────────────────┘  │
│  ... (up to 3 cards)                       │
│ [Plan Another Trip] [View History]         │
└───────────────────────────────────────────┘
```

### 4.5 History (`history.html`)
**Purpose:** show past trips.

| # | Date & Time | From | To | Battery % | Recommended Station |
|---|---|---|---|---|---|
| 1 | 2026-10-18 10:45 | KIIT | Railway Station | 45 | Station A |

Below the table: **Plan a Trip** button.

---

## 5. Key User Flows

### 5.1 First-time use
1. Open `/` → redirected to `/login`.
2. Click "Register here" → fill form → Register.
3. Redirected to Login → sign in → Dashboard.

### 5.2 Plan a trip
1. Dashboard → fill start and destination names, pick a preset destination.
2. Enter battery % and distance (other fields optional).
3. Submit → Results page with verdict and stations.
4. Tap "Get Directions" → Google Maps opens in a new tab.

### 5.3 Review history
1. Navbar → History → table of trips (newest first).

### 5.4 Error recovery
1. Invalid input → same page reloads with a red message; previously typed values should be preserved where practical.

---

## 6. Components

| Component | Description | States |
|---|---|---|
| **Navbar** | Brand + 3 links | default, hover, active |
| **Card** (`.card`) | White container with padding and soft shadow | – |
| **Auth card** (`.auth-card`) | Narrow centered card | – |
| **Text / number input** | Full width, label above | default, focus (green outline), error, disabled |
| **Select** | Same style as input | default, focus |
| **Primary button** | Green fill, white text | default, hover (darker), active, disabled, loading |
| **Secondary button** | White with green border | default, hover |
| **Alert** (`.alert`) | Full-width banner with icon | `warning` (amber), `success` (green), `error` (red) |
| **Station card** (`.station-card`) | Border, rounded, icon lines | default, hover (raised shadow) |
| **Directions button** (`.btn-directions`) | Primary button inside card | default, hover |
| **History table** | Striped rows, sticky header on scroll | default, empty |

## 7. Interactions

| Interaction | Behavior |
|---|---|
| Preset destination select | Instantly fills hidden `dest_lat` / `dest_lon` |
| Page load on dashboard | Browser asks for location; on allow, fills `car_lat` / `car_lon`; on deny, keeps defaults silently |
| Form submit | Button changes to "Finding stations…" and is disabled to prevent double submit |
| Battery out of range | Browser-side alert before submit; server-side error as backup |
| Get Directions | Opens Google Maps in a new tab |
| Hover on buttons and cards | Subtle color or shadow change (150 ms transition) |
| Logout | Immediate redirect to Login |

## 8. Forms

| Form | Fields | Validation |
|---|---|---|
| Login | email, password | Required; email format |
| Register | username, email, password | Required; password ≥ 8 characters; unique email (server) |
| Trip | start_name, dest_name, preset, battery_pct, distance_km, speed_kmh, temp, ac_on | battery 1–100, distance > 0, speed 1–200, temp −10 to 60 |

Rules: labels always visible; use `type="email"`, `type="number"`, and proper `min` / `max`; mark required fields; place the error message at the top of the card in red; keep the submit button full width on mobile.

## 9. Loading, Error, and Empty States

| Situation | Treatment |
|---|---|
| **Loading** (submitting trip) | Disable button, show "Finding stations…" text |
| **Loading** (geolocation) | No blocking UI; defaults apply until location arrives |
| **Error — login** | Red text: "Invalid email or password." |
| **Error — register** | "Password must be at least 8 characters." / "Email already registered." |
| **Error — trip form** | "Battery % must be between 1 and 100." / "Distance must be greater than 0." |
| **Error — server** | Friendly generic page: "Something went wrong. Please try again." with a Home link |
| **Empty — no stations** | Card text: "No charging stations found on this route corridor." plus Plan Another Trip button |
| **Empty — history** | "No trips yet. Plan your first trip." plus button to Dashboard |
| **Partial results** | If fewer than 3 stations, show only those; no filler cards |

## 10. Responsive Behavior

| Breakpoint | Layout |
|---|---|
| **≥ 900 px (desktop)** | Content centered, max width ~720 px; cards with comfortable padding |
| **600–899 px (tablet)** | Same layout, reduced side margins |
| **< 600 px (mobile)** | Single column; full-width inputs and buttons; navbar links tighter; history table scrolls horizontally inside its own container; station card text stacks |

Additional rules: use relative units (`rem`, `%`); `meta viewport` on every page; minimum touch target 44 × 44 px; no horizontal page scroll.

## 11. Accessibility

- Every input has an associated `<label>` (use `for` / `id`) in addition to any placeholder.
- Color contrast at least 4.5:1 for text (white on `#16a34a` passes for large and bold text; use `#15803d` for small text if needed).
- Do not rely on color alone: alerts include icons and text ("⚠️ Battery predicted…", "✅ Battery should be…").
- Visible focus outline on all interactive elements.
- Logical heading order (`h2` page title, `h3` sections, `h4` station names).
- Buttons are real `<button>` elements and links are real `<a>` elements.
- Set `lang="en"` on `<html>`; use `aria-live="polite"` for the error message area.
- Keyboard: full form can be completed with Tab, Enter, and arrow keys on selects.
- Avoid placing a `<button>` inside an `<a>` where possible; style the link as a button instead.

## 12. Typography

| Use | Font | Size | Weight |
|---|---|---|---|
| Body | System UI stack: `-apple-system, "Segoe UI", Roboto, Arial, sans-serif` | 16 px | 400 |
| Page title (`h2`) | Same | 24–28 px | 700 |
| Section title (`h3`) | Same | 20 px | 600 |
| Station name (`h4`) | Same | 18 px | 600 |
| Labels | Same | 14 px | 500 |
| Small / hint text | Same | 13 px | 400 |
| Buttons | Same | 16 px | 600 |

Line height 1.5 for body text.

## 13. Colors

| Token | Hex | Use |
|---|---|---|
| `--primary` | `#16a34a` | Buttons, brand, links |
| `--primary-dark` | `#15803d` | Button hover, small green text |
| `--bg` | `#f3f4f6` | Page background |
| `--surface` | `#ffffff` | Cards |
| `--text` | `#111827` | Main text |
| `--muted` | `#6b7280` | Hints, secondary text |
| `--border` | `#e5e7eb` | Inputs, cards, table lines |
| `--warning-bg` / `--warning-text` | `#fef3c7` / `#92400e` | Charge-needed banner |
| `--success-bg` / `--success-text` | `#dcfce7` / `#166534` | Battery-sufficient banner |
| `--error` | `#dc2626` | Error messages |

## 14. Spacing and Shape

| Item | Value |
|---|---|
| Spacing scale | 4, 8, 12, 16, 24, 32 px |
| Card padding | 24 px (16 px on mobile) |
| Gap between form fields | 12–16 px |
| Border radius | 8 px (cards, inputs, buttons) |
| Card shadow | `0 1px 3px rgba(0,0,0,0.1)` |
| Max content width | 720 px |
| Navbar height | 56 px |

## 15. Design Guidelines Summary

- Keep copy short and friendly; use ₹ and km consistently.
- Use emoji icons sparingly (⚡ 📍 ⏳ 🔋 💰 ⚠️ ✅) as in the station cards.
- One primary button per screen.
- Use the same card style on all pages.
- Never show raw errors or stack traces to users.

## 16. Implementation Notes (for `static/css/style.css`)

1. Define the color tokens above as CSS variables on `:root`.
2. Styles needed: `body`, `nav`, `main`, `.card`, `.auth-card`, `label`, `input`, `select`, `button`, `.error`, `.alert.warning`, `.alert.success`, `.station-card`, `.btn-directions`, `table`, and one `@media (max-width: 600px)` block.
3. Keep `main.js` limited to: preset destination coordinates, geolocation, simple battery check, and disabling the submit button on submit.

---

*End of UI/UX Document*