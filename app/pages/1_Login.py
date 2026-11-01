# app/pages/1_Login.py
# Login page for Streamlit app

import streamlit as st
from app.auth import authenticate_user

if st.session_state.get('logged_in', False):
    st.success("You are already logged in!")
    st.stop()

# Brand header
st.markdown("""
<div class="auth-brand">
    <div class="brand-mark">⚡</div>
    <h1 class="t-display">VoltRoute</h1>
    <p class="tagline">Intelligent EV Charging & Route Optimization</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Segmented switch
    st.markdown("""
    <div class="segmented">
        <a href="#" class="active">Sign In</a>
        <a href="#">Create Account</a>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                if authenticate_user(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    st.markdown("<p style='text-align: center; color: var(--text-muted); margin-top: 24px;'>Don't have an account? Switch to <strong>Register</strong> in the sidebar.</p>", unsafe_allow_html=True)
