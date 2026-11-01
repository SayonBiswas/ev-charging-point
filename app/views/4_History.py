# app/views/4_History.py
# Trip history page for Streamlit app

import streamlit as st
import pandas as pd
from app.models import SessionLocal, TripHistory

st.markdown('<h1 class="t-headline">Trip History</h1>', unsafe_allow_html=True)
st.markdown("---")

# Get trip history for current user
db = SessionLocal()
try:
    trips = db.query(TripHistory).filter(
        TripHistory.user_email == st.session_state.email
    ).order_by(TripHistory.created_at.desc()).all()
finally:
    db.close()

if not trips:
    st.markdown("""
    <div class="empty-state">
        <p>No trip history found.</p>
        <p>Start by planning a trip on the Dashboard!</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Convert to DataFrame for display
    trip_data = []
    for trip in trips:
        trip_data.append({
            "Date": trip.created_at.strftime("%Y-%m-%d %H:%M"),
            "From": trip.start_loc,
            "To": trip.destination,
            "Battery (%)": f"{trip.battery_pct:.1f}",
            "Recommended Station": trip.station_rec
        })

    df = pd.DataFrame(trip_data)

    # Display as table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Summary statistics
    st.markdown("---")
    st.markdown('<h2 class="t-title">Summary</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Trips", len(trips))

    with col2:
        avg_battery = sum(trip.battery_pct for trip in trips) / len(trips)
        st.metric("Average Battery Level", f"{avg_battery:.1f}%")

    with col3:
        unique_destinations = len(set(trip.destination for trip in trips))
        st.metric("Unique Destinations", unique_destinations)
