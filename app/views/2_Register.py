# app/views/2_Register.py
# Registration page for Streamlit app

import streamlit as st
from app.auth import register_user

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
        <a href="#">Sign In</a>
        <a href="#" class="active">Create Account</a>
    </div>
    """, unsafe_allow_html=True)

    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Create a password (min 8 characters)")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            if not username or not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(username, email, password)
                if success:
                    st.success(message)
                    st.info("Please switch to Login in the sidebar to sign in.")
                else:
                    st.error(message)

    st.markdown("<p style='text-align: center; color: var(--text-muted); margin-top: 24px;'>Already have an account? Switch to <strong>Login</strong> in the sidebar.</p>", unsafe_allow_html=True)
