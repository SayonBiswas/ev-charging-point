# app/auth.py
# Authentication utilities using Streamlit session state and passlib

import streamlit as st
from passlib.context import CryptContext
from app.models import SessionLocal, User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    # Truncate password to 72 bytes if longer (bcrypt limitation)
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    # Truncate password to 72 bytes if longer (bcrypt limitation)
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'email' not in st.session_state:
        st.session_state.email = None

def is_logged_in() -> bool:
    """Check if user is logged in"""
    return st.session_state.get('logged_in', False)

def login_user(email: str, username: str):
    """Log in a user by setting session state"""
    st.session_state.logged_in = True
    st.session_state.email = email
    st.session_state.username = username

def logout_user():
    """Log out the current user by clearing session state"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.email = None

def authenticate_user(email: str, password: str) -> bool:
    """
    Authenticate a user with email and password
    Returns True if authentication successful, False otherwise
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.password_hash):
            login_user(email, user.username)
            return True
        return False
    finally:
        db.close()

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user
    Returns (success: bool, message: str)
    """
    db = SessionLocal()
    try:
        # Check password length
        if len(password) < 8:
            return False, "Password must be at least 8 characters."

        # Check password is not too long (bcrypt limitation: 72 bytes)
        if len(password.encode('utf-8')) > 72:
            return False, "Password is too long. Maximum 72 characters allowed."

        # Check if email already exists
        if db.query(User).filter(User.email == email).first():
            return False, "Email already registered."

        # Check if username already exists
        if db.query(User).filter(User.username == username).first():
            return False, "Username already exists."

        # Create user
        hashed_password = get_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.add(new_user)
        db.commit()

        return True, "Registration successful! Please login."
    except Exception as e:
        db.rollback()
        return False, f"Registration failed: {str(e)}"
    finally:
        db.close()
