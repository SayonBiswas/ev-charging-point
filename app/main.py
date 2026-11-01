# app/main.py
# Main Streamlit application entry point

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth import init_session_state, is_logged_in, logout_user
from app.models import create_tables, SessionLocal, User
from app.config import settings

# Page configuration
st.set_page_config(
    page_title="VoltRoute - EV Charging & Route Optimization",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'static', 'style.css')
    with open(css_path, 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Initialize session state
init_session_state()

# Create database tables on first run
if 'db_initialized' not in st.session_state:
    create_tables()
    st.session_state.db_initialized = True

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div class="brand-container" style="margin-bottom: 24px;">
        <div class="brand-mark" style="width: 40px; height: 40px; font-size: 20px; margin: 0;">⚡</div>
        <div class="brand-name" style="font-size: 18px;">VoltRoute</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if is_logged_in():
        st.markdown(f'<div style="color: var(--primary); font-weight: 600;">Welcome, {st.session_state.username}</div>', unsafe_allow_html=True)
        st.markdown("---")
        page = st.radio(
            "Navigate",
            ["Dashboard", "History"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()
    else:
        page = st.radio(
            "Navigate",
            ["Login", "Register"],
            label_visibility="collapsed"
        )

# Main content routing
if page == "Login":
    exec(open(os.path.join(os.path.dirname(__file__), 'pages', '1_Login.py')).read())
elif page == "Register":
    exec(open(os.path.join(os.path.dirname(__file__), 'pages', '2_Register.py')).read())
elif page == "Dashboard":
    if not is_logged_in():
        st.error("Please login to access the dashboard")
        st.stop()
    exec(open(os.path.join(os.path.dirname(__file__), 'pages', '3_Dashboard.py')).read())
elif page == "History":
    if not is_logged_in():
        st.error("Please login to access the history")
        st.stop()
    exec(open(os.path.join(os.path.dirname(__file__), 'pages', '4_History.py')).read())
