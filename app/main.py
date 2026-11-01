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
    <div class="sb-brand">
        <div class="sb-mark">⚡</div>
        <div>
            <div class="sb-name">VoltRoute</div>
            <div class="sb-tag">EV Route Planner</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if is_logged_in():
        initial = (st.session_state.username or "U")[0].upper()
        st.markdown(f"""
        <div class="sb-user">
            <div class="sb-avatar">{initial}</div>
            <div>
                <div class="sb-hello">Welcome back</div>
                <div class="sb-username">{st.session_state.username}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigate",
            ["Dashboard", "History"],
            format_func=lambda p: {"Dashboard": "🗺️  Plan Trip", "History": "🕘  History"}[p],
            label_visibility="collapsed",
        )

        st.markdown('<div class="sb-spacer"></div>', unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            logout_user()
            st.rerun()
    else:
        page = st.radio(
            "Navigate",
            ["Login", "Register"],
            format_func=lambda p: {"Login": "🔑  Sign In", "Register": "✨  Create Account"}[p],
            label_visibility="collapsed",
        )

# Main content routing
if page == "Login":
    exec(open(os.path.join(os.path.dirname(__file__), 'views', '1_Login.py')).read())
elif page == "Register":
    exec(open(os.path.join(os.path.dirname(__file__), 'views', '2_Register.py')).read())
elif page == "Dashboard":
    if not is_logged_in():
        st.error("Please login to access the dashboard")
        st.stop()
    exec(open(os.path.join(os.path.dirname(__file__), 'views', '3_Dashboard.py')).read())
elif page == "History":
    if not is_logged_in():
        st.error("Please login to access the history")
        st.stop()
    exec(open(os.path.join(os.path.dirname(__file__), 'views', '4_History.py')).read())
