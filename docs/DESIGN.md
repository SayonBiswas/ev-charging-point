# UI/UX Design Document
## VoltRoute — Intelligent EV Charging & Route Optimization System (Bhubaneswar)

| Field | Value |
|---|---|
| Document version | 2.0 (replaces v1.0 light theme) |
| Based on | PRD v1.0, SRS v1.0, Architecture v1.0, Stitch export "EcoTech Kinetic" |
| Design goals | Dark, glanceable, mobile-first; still plain HTML + CSS + vanilla JS (no Tailwind, no build step) |

---

## 1. What changed from v1.0

| Area | v1.0 | v2.0 |
|---|---|---|
| Theme | Light, green buttons | Dark "EcoTech Kinetic": obsidian surfaces, emerald energy accents, soft glass cards |
| Fonts | System stack | Plus Jakarta Sans (headings, numbers) + Inter (body), system fallback |
| Icons | Emoji | Material Symbols Outlined (emoji kept only in verdict text for the "not colour alone" rule) |
| Navigation | Top navbar, 3 links | Header + links on desktop, fixed bottom nav on mobile (Plan Trip, History, Logout) |
| Auth pages | Plain card | Brand header + Sign In / Create Account segmented switch (still two routes) |
| Dashboard | Long single form | Two cards: Route Waypoints (chips, swap, GPS) and Vehicle Telemetry (battery slider and gauge, speed slider, AC switch) with a live preview |
| Results | Text lines | Station cards with DC/AC badges, spec grid, glow on the top pick |
| History | Striped table | Dark table with coloured battery badges |

Not carried over from the Stitch mockups, because the backend has no data or feature behind them: Google/Apple sign-in, Forgot Password, "9,420+ stations", "ISO 27001" claims, EV model picker, live plug availability ("3/4 plugs open"), detour km, amenities, notifications, avatar, "Save to History" (history is saved automatically), Stations/Account tabs. SRS and PRD list social login and password reset as non-goals. Add them to the UI only when the feature exists.

---

## 2. Design Principles

1. **Answer first:** results open with the verdict, then stations.
2. **Glanceable numbers:** kW, minutes, rupees and battery % use Plus Jakarta Sans with tabular digits.
3. **Honest UI:** show only what the data supports; estimates are labelled as estimates.
4. **Few inputs, sensible defaults:** battery 50%, speed 60, temperature 30, AC off; only destination and battery really matter.
5. **Thumb-first:** controls at least 48 px high, bottom nav on phones, works at 360 px.
6. **Never colour alone:** every state has an icon and text as well as a colour.

---

## 3. Colour Tokens

Defined as CSS variables on `:root` in `style.css`.

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#0f131c` | Page background (with faint emerald and sky radial glows) |
| `--surface-lowest` | `#0a0e16` | Segmented switch track |
| `--surface-low` | `#181c24` | Inset panels inside cards |
| `--surface` | `#1c2028` | Cards, station cards |
| `--surface-high` | `#262a33` | Chips, hover, active tab |
| `--surface-highest` | `#31353e` | Slider and gauge tracks |
| `--text` / `--text-muted` / `--outline` | `#dfe2ee` / `#bbcabf` / `#86948a` | Body / secondary / hints |
| `--primary` | `#4edea3` | Links, active nav, healthy battery |
| `--primary-container` | `#10b981` | Button gradient start, switch on, selected chip |
| `--secondary` | `#93ccff` | AC chargers, charge-time and telemetry accents |
| `--tertiary` | `#ffb95f` | DC badge, warnings, low battery (20 to 40%) |
| `--error` / `--error-strong` | `#ffb4ab` / `#ef4444` | Errors, critical battery (below 20%) |

Elevation: Level 0 background; Level 1 card (`rgba(28,32,40,.9)`, 1 px `rgba(255,255,255,.08)` border, 12 px blur); Level 2 shadow `0 12px 32px -8px rgba(0,0,0,.55)`; "active energy" glow `0 0 20px -3px rgba(16,185,129,.35)` on primary buttons and the recommended station.

Contrast: primary button text is `#002113` on the emerald gradient (about 6.8:1). Body text on surfaces is above 10:1. `--outline` is for hints only, never for essential text.

## 4. Typography

| Role | Font | Size / line | Weight |
|---|---|---|---|
| Display (auth brand on desktop) | Plus Jakarta Sans | 40 / 48 (32 / 38 mobile) | 700 |
| Headline (`.t-headline`) | Plus Jakarta Sans | 24 / 32 | 700 |
| Title (`.t-title`) | Plus Jakarta Sans | 20 / 28 | 600 |
| Subhead (`.t-sub`) | Plus Jakarta Sans | 16 / 24 | 600 |
| Metric (`.metric`) | Plus Jakarta Sans, tabular digits | 24 / 28 | 700 |
| Body | Inter | 14 / 20 (16 px in inputs to stop iOS zoom) | 400 |
| Label (`.t-label`) | Inter | 12 / 16 | 600 |
| Micro caps (`.t-micro`) | Inter | 11 / 14, uppercase | 700 |

Fonts load from Google Fonts. Offline, the system fallback stack applies and the app still works. Icons fall back to their text names if the icon font cannot load, so for an offline demo either self-host the two fonts or open the page once online first.

## 5. Layout, Shape, Spacing

| Item | Value |
|---|---|
| Spacing scale | 4, 8, 12, 16, 24, 36 px |
| Page padding | 16 px (24 px at 640 px and up) |
| Max content width | 1180 px |
| Radius | Cards 16 px, inputs/buttons/inset panels 12 px, pills 999 px |
| Header height | 60 px; bottom nav 64 px (plus safe-area inset) |
| Touch target | 48 px minimum |

| Breakpoint | Behaviour |
|---|---|
| below 640 px | One column; bottom nav; header shows brand only |
| 640 to 899 px | One column, larger padding, action buttons in two columns |
| 900 px and up | Header links replace bottom nav; dashboard splits into Route and Telemetry columns; station cards in an auto-fit grid |

## 6. Navigation

| Element | Where | Items |
|---|---|---|
| Header | Fixed top, logged-in pages | Brand (left); Plan Trip, History, Logout (right, 900 px and up) |
| Bottom nav | Fixed bottom, below 900 px | Plan Trip (`/dashboard`), History (`/history`), Logout (`/logout`) |
| Active state | Both | Emerald text plus soft glow; matched with `request.url.path` |
| Auth pages | No header or nav | Segmented switch links `/login` and `/register` |

## 7. Screens

### 7.1 Login (`login.html`) and Register (`register.html`)
Brand mark (emerald gradient square with a bolt), "VoltRoute", tagline, then a glass card containing the Sign In / Create Account switch, the error alert (if any), and the form.
- Login fields: `email`, `password` (show/hide button).
- Register fields: `username`, `email`, `password` (strength meter, show/hide), confirm password (client-side only, no `name`, never sent).
- Errors use `.alert.error` with `role="alert"` and `aria-live="polite"`.

### 7.2 Dashboard (`dashboard.html`), posts to `/predict`
**Route Waypoints card:** Starting point (`start_name`, GPS button), swap button, Destination (`dest_name`, clear button), preset chips (KIIT, Railway Station, Master Canteen, Airport, Patia), a hint line, and Distance (`distance_km`). Choosing a chip fills `dest_name`, `dest_lat`, `dest_lon` and auto-fills distance (straight line, editable). Hidden: `car_lat`, `car_lon`, `dest_lat`, `dest_lon`.
**Vehicle Telemetry card:** battery slider (`battery_pct`, 1 to 100) with a gauge and status badge; speed slider (`speed_kmh`, 20 to 120); temperature (`temp_celsius`); AC switch (`ac_on`, value 1, absent means 0); live preview; primary CTA "Find Charging Stations".

Battery states: above 40% emerald; 20 to 40% amber; below 20% red with a slow pulse.

The live preview uses the same rule as SRS BR-5 (battery % divided by km below 0.45 means charge). It is a hint only; the ML model decides the real verdict on the results page.

### 7.3 Results (`results.html`)
1. Trip card: "Start → Destination", verdict alert (amber "Charging stop recommended" or green "Battery looks sufficient"), battery gauge.
2. Heading "Recommended charging stations" with a count.
3. Up to 3 station cards: rank or "Nearest on route" badge, distance from car, name, address, estimated cost, DC (amber) or AC (sky) badge with kW, spec grid (queue wait, charge time, power), "Get Directions" button (Google Maps link, new tab).
4. Empty state "No charging stations found on this route corridor."
5. Actions: Plan Another Trip, View History. Footnote that figures are estimates.

### 7.4 History (`history.html`)
Dark table: Date and Time, From, To, Battery badge (red below 20, amber 20 to 40, green above), Recommended station. Table scrolls inside its own container on phones. Empty state with "Plan a Trip".

## 8. Components

| Component | Class | Notes |
|---|---|---|
| Card | `.card`, `.inset` | Glass card; inset panel for grouped controls |
| Primary button | `.btn.btn-primary` | Emerald gradient, inner top highlight, glow; 1 px press shift; `.btn-lg` for the main CTA |
| Ghost button | `.btn.btn-ghost` | Translucent, emerald-tinted border, fills emerald on hover |
| Directions button | `.btn-directions` | Solid mint, full width in the station card |
| Input | `.input-wrap` + `input` | Icon prefix, 48 px high, emerald focus ring |
| Slider | `input[type=range]` | Custom thumb; `.accent-warn` for speed |
| Switch | `.switch` | Real checkbox under a styled track |
| Chip | `.chip`, `.chip.selected` | Scrollable row of presets |
| Badge | `.badge-dc / -ac / -rec / -ok / -warn / -bad` | Capsules |
| Alert | `.alert.warning / .success / .error` | Icon plus text, never colour alone |
| Gauge | `.gauge[data-level=ok|mid|low]` | Level drives bar colour |
| Station card | `.station-card`, `.recommended` | Header, specs, action |
| Segmented switch | `.segmented` | Auth tab look using real links |

## 9. Interactions

| Interaction | Behaviour |
|---|---|
| Preset chip | Fills destination name and coordinates, selects chip, auto-fills distance |
| GPS button / page load | Asks for location; on allow updates `car_lat/lon` and distance; on deny keeps City Center defaults silently |
| Battery slider | Updates value, gauge, icon, badge and preview instantly |
| AC switch | Updates label text |
| Swap | Swaps names (and coordinates if a preset is chosen) |
| Submit | Client checks (same limits as SRS section 7), then disables the button and shows "Finding stations…" |
| Hover | Cards lift 2 px, buttons brighten (150 ms) |
| Reduced motion | Animations and transitions switch off |

## 9.1 Loading, Error, Empty States

| Situation | Treatment |
|---|---|
| Submitting | Disabled button, "Finding stations…" |
| Login or register error | Red alert at top of the card |
| Trip validation error | Client: inline alert above the form. Server: same alert via `error` |
| No stations | Empty-state card plus Plan Another Trip |
| No history | Empty state plus Plan a Trip |
| Fewer than 3 stations | Show only those; no filler |

## 10. Accessibility

- Every input has a `<label for>` (waypoint inputs use a label above the field).
- Visible focus ring (`:focus-visible`, 2 px emerald).
- Alerts use `role="alert"` or `role="status"` with `aria-live`.
- Icon-only buttons have `aria-label`.
- Nav is a `<nav aria-label="Primary">`; current page marked with the `active` class.
- Slider values are mirrored in text next to the control.
- `lang="en"`, viewport meta with `viewport-fit=cover`, safe-area padding for notched phones.

## 11. Files That Implement This Design

| File | Change |
|---|---|
| `frontend/static/css/style.css` | Replaced |
| `frontend/static/js/main.js` | Replaced (all dashboard JS lives here) |
| `frontend/templates/base.html` | Replaced (nav shows by default; auth pages switch it off) |
| `frontend/templates/login.html`, `register.html`, `dashboard.html`, `results.html`, `history.html` | Replaced |
| `backend/app/main.py` | No change required |

Notes for the developer:
1. `base.html` no longer depends on a `user` variable, so the header and nav now appear on Results and History too. They were hidden before because `/predict` and `/history` pass `user=None`.
2. The inline `<script>` in the old `dashboard.html` is removed; it duplicated `main.js` and attached every handler twice.
3. The brand name "VoltRoute" appears in `base.html`, `login.html`, `register.html`; change it there if your report uses another name.
4. Optional later: pass `total_connectors` and `distance_to_dest_km` into each station dict in `/predict` and add them to the spec grid.

---

*End of UI/UX Document v2.0*