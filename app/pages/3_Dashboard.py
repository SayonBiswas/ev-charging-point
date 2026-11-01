# app/pages/3_Dashboard.py
# Dashboard page for trip prediction and charging station recommendations

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from app.models import SessionLocal, TripHistory
from app.predictor import predictor
from app.utils import filter_stations_on_route
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import folium
from streamlit_folium import st_folium
import time

# Page title
st.markdown('<h1 class="t-headline">Plan Your Trip</h1>', unsafe_allow_html=True)
st.markdown("---")

# Load station data
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIONS_CSV_PATH = os.path.join(PROJECT_ROOT, "backend", "data", "cleaned_data.csv")

try:
    stations_df = pd.read_csv(STATIONS_CSV_PATH)
except FileNotFoundError:
    st.error(f"Station data file not found at {STATIONS_CSV_PATH}")
    st.info("Please run: python backend/ml/preprocess.py")
    st.stop()

# Geocoding function
@st.cache_data(ttl=3600)
def geocode_location(location_name):
    """Convert location name to coordinates using Nominatim (OpenStreetMap)"""
    try:
        geolocator = Nominatim(user_agent="voltroute_ev_charging")
        location = geolocator.geocode(location_name, timeout=5)
        if location:
            return location.latitude, location.longitude
        return None, None
    except (GeocoderTimedOut, GeocoderServiceError):
        return None, None

# Auto-geocode section
st.markdown('<p class="t-label">Location Autocomplete</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    start_location = st.text_input("Starting Location", placeholder="e.g., KIIT University, Bhubaneswar")
    auto_geocode_start = st.button("📍 Auto-detect Coordinates", key="auto_start")

with col2:
    dest_location = st.text_input("Destination", placeholder="e.g., Bhubaneswar Railway Station")
    auto_geocode_dest = st.button("📍 Auto-detect Coordinates", key="auto_dest")

# Initialize coordinates in session state
if 'start_lat' not in st.session_state:
    st.session_state.start_lat = 20.2961
    st.session_state.start_lon = 85.8245
    st.session_state.dest_lat = 20.2662
    st.session_state.dest_lon = 85.8354

# Handle auto-geocoding
if auto_geocode_start and start_location:
    with st.spinner("Finding coordinates for starting location..."):
        lat, lon = geocode_location(start_location)
        if lat and lon:
            st.session_state.start_lat = lat
            st.session_state.start_lon = lon
            st.success(f"Found: {lat:.4f}, {lon:.4f}")
        else:
            st.warning("Could not find coordinates. Please enter manually.")

if auto_geocode_dest and dest_location:
    with st.spinner("Finding coordinates for destination..."):
        lat, lon = geocode_location(dest_location)
        if lat and lon:
            st.session_state.dest_lat = lat
            st.session_state.dest_lon = lon
            st.success(f"Found: {lat:.4f}, {lon:.4f}")
        else:
            st.warning("Could not find coordinates. Please enter manually.")

# Trip input form
with st.form("trip_form"):
    st.markdown('<p class="t-label">Trip Details</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        battery_pct = st.slider("Current Battery Level (%)", 1, 100, 50)
        distance_km = st.number_input("Distance to Destination (km)", min_value=0.1, value=20.0, step=0.1)

    with col2:
        speed_kmh = st.slider("Average Speed (km/h)", 20, 120, 60)
        temp_celsius = st.slider("Temperature (°C)", -10, 50, 30)
        ac_on = st.checkbox("AC On")

    # Battery gauge visualization
    st.markdown('<p class="t-label">Battery Status</p>', unsafe_allow_html=True)
    battery_color = "#4edea3" if battery_pct > 50 else "#ffb95f" if battery_pct > 20 else "#ef4444"
    st.markdown(f"""
    <div style="margin: 16px 0;">
        <div class="gauge" data-level="{'ok' if battery_pct > 50 else 'mid' if battery_pct > 20 else 'low'}">
            <div class="gauge-bar" style="width: {battery_pct}%; background-color: {battery_color};"></div>
        </div>
        <p style="text-align: center; font-weight: 600; color: var(--text); margin-top: 8px;">
            {battery_pct}% - {'Good' if battery_pct > 50 else 'Medium' if battery_pct > 20 else 'Low'}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Coordinates section (collapsible)
    with st.expander("Advanced: Manual Coordinates", expanded=False):
        st.markdown('<p class="t-label">Coordinates</p>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.session_state.start_lat = st.number_input("Starting Latitude", value=st.session_state.start_lat, format="%.4f")
            st.session_state.start_lon = st.number_input("Starting Longitude", value=st.session_state.start_lon, format="%.4f")
        with col_b:
            st.session_state.dest_lat = st.number_input("Destination Latitude", value=st.session_state.dest_lat, format="%.4f")
            st.session_state.dest_lon = st.number_input("Destination Longitude", value=st.session_state.dest_lon, format="%.4f")

    submitted = st.form_submit_button("Find Charging Stations", use_container_width=True)

if submitted:
    # Validation
    if battery_pct < 1 or battery_pct > 100:
        st.error("Battery % must be between 1 and 100.")
        st.stop()

    if distance_km <= 0:
        st.error("Distance must be greater than 0.")
        st.stop()

    if not start_location or not dest_location:
        st.error("Please enter starting location and destination.")
        st.stop()

    # Loading animation
    with st.spinner("Analyzing your route..."):
        time.sleep(0.5)  # Simulate processing

        # Predict if charging is needed
        needs_charge = predictor.predict_needs_charge(
            battery_pct, distance_km, speed_kmh, temp_celsius, int(ac_on)
        )

        # Display verdict with animation
        st.markdown('<h2 class="t-title">Verdict</h2>', unsafe_allow_html=True)
        if needs_charge:
            st.markdown("""
            <div class="alert warning">
                <span>⚠️</span>
                <span>You need to charge before reaching your destination!</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert success">
                <span>✅</span>
                <span>You can reach your destination without charging.</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Filter stations on route
        stations_with_details = []
        if len(stations_df) > 0:
            filtered_stations = filter_stations_on_route(
                stations_df,
                st.session_state.start_lat,
                st.session_state.start_lon,
                st.session_state.dest_lat,
                st.session_state.dest_lon
            )

            # Get current time for demand prediction
            now = datetime.now()
            hour_of_day = now.hour
            day_of_week = now.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0

            for station_info in filtered_stations:
                station = station_info['station']

                # Get station details with defaults
                total_connectors = station.get('total_connectors', 4)
                charger_rating_kw = station.get('charger_rating_kw', 22)

                # Predict wait time
                wait_minutes = predictor.predict_wait_time(
                    hour_of_day, day_of_week, total_connectors, charger_rating_kw, is_weekend
                )

                # Estimate charge time and cost
                charge_time_min, cost = predictor.estimate_charge_time_and_cost(
                    battery_pct, charger_rating_kw
                )

                stations_with_details.append({
                    'name': station['station_name'],
                    'address': station['address'],
                    'latitude': station['latitude'],
                    'longitude': station['longitude'],
                    'charger_type': station['charger_type'],
                    'charger_rating_kw': charger_rating_kw,
                    'distance_from_car_km': station_info['distance_from_car_km'],
                    'wait_minutes': round(wait_minutes, 1),
                    'charge_time_min': charge_time_min,
                    'cost': cost
                })

        # Display results
        if stations_with_details:
            st.markdown('<h2 class="t-title">Recommended Charging Stations</h2>', unsafe_allow_html=True)

            # Create map
            m = folium.Map(
                location=[st.session_state.start_lat, st.session_state.start_lon],
                zoom_start=12,
                tiles="CartoDB dark_matter"
            )

            # Add start marker
            folium.Marker(
                [st.session_state.start_lat, st.session_state.start_lon],
                popup="Start",
                icon=folium.Icon(color="blue", icon="play", prefix="fa")
            ).add_to(m)

            # Add destination marker
            folium.Marker(
                [st.session_state.dest_lat, st.session_state.dest_lon],
                popup="Destination",
                icon=folium.Icon(color="red", icon="flag", prefix="fa")
            ).add_to(m)

            # Add station markers
            for i, station in enumerate(stations_with_details):
                color = "green" if i == 0 else "orange"
                folium.Marker(
                    [station['latitude'], station['longitude']],
                    popup=f"{station['name']}<br>Wait: {station['wait_minutes']} min<br>Cost: ₹{station['cost']}",
                    icon=folium.Icon(color=color, icon="bolt", prefix="fa")
                ).add_to(m)

            # Draw route line
            folium.PolyLine(
                [
                    [st.session_state.start_lat, st.session_state.start_lon],
                    [st.session_state.dest_lat, st.session_state.dest_lon]
                ],
                color="blue",
                weight=2,
                opacity=0.5
            ).add_to(m)

            # Display map
            st_folium(m, width="100%", height=400)

            # Station cards
            for i, station in enumerate(stations_with_details, 1):
                is_recommended = i == 1
                recommended_class = "recommended" if is_recommended else ""
                badge_html = '<span class="badge badge-rec">Recommended</span>' if is_recommended else ''

                st.markdown(f"""
                <div class="station-card {recommended_class}">
                    <div class="station-header">
                        <div class="station-name">{station['name']}</div>
                        {badge_html}
                    </div>
                    <div class="station-address">{station['address']}</div>
                    <div class="station-specs">
                        <div class="station-spec">
                            <p class="t-micro">Distance</p>
                            <p class="metric">{station['distance_from_car_km']} km</p>
                        </div>
                        <div class="station-spec">
                            <p class="t-micro">Wait Time</p>
                            <p class="metric">{station['wait_minutes']} min</p>
                        </div>
                        <div class="station-spec">
                            <p class="t-micro">Charge Time</p>
                            <p class="metric">{station['charge_time_min']} min</p>
                        </div>
                    </div>
                    <div class="station-cost">₹{station['cost']}</div>
                    <div class="row row-between">
                        <span class="badge badge-{station['charger_type'].lower()}">{station['charger_type']}</span>
                        <span class="badge badge-ac">{station['charger_rating_kw']} kW</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Google Maps link
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={station['latitude']},{station['longitude']}"
                st.markdown(f'<a href="{maps_url}" target="_blank" class="btn btn-directions">Get Directions</a>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            # Save to trip history
            db = SessionLocal()
            try:
                top_station = stations_with_details[0]['name']
                trip = TripHistory(
                    user_email=st.session_state.email,
                    start_loc=start_location,
                    destination=dest_location,
                    battery_pct=battery_pct,
                    station_rec=top_station
                )
                db.add(trip)
                db.commit()
            finally:
                db.close()

            st.markdown("""
            <div class="alert success">
                <span>✓</span>
                <span>Trip saved to history!</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert warning">
                <span>⚠</span>
                <span>No charging stations found along your route.</span>
            </div>
            """, unsafe_allow_html=True)
            st.info("Try adjusting your coordinates or check if station data is available.")

# Display trip tips
st.markdown("---")
st.markdown('<h2 class="t-title">Trip Tips</h2>', unsafe_allow_html=True)
st.markdown("""
<div class="card">
    <ul style="color: var(--text-muted); line-height: 1.8;">
        <li>🚗 Use lower speeds to conserve battery</li>
        <li>❄️ Turn off AC when possible to extend range</li>
        <li>⏰ Charge during off-peak hours for shorter wait times</li>
        <li>⚡ Plan charging stops at stations with higher power ratings</li>
        <li>📍 Use the auto-detect feature for accurate coordinates</li>
    </ul>
</div>
""", unsafe_allow_html=True)
