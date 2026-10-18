# backend/app/main.py
# Main FastAPI application with all route endpoints

import sys
import os
# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

from app.config import settings
from app.models import Base, User, TripHistory, create_tables, get_db
from app.schemas import UserCreate, TripPredictionRequest
from app.auth import (
    verify_password, get_password_hash, create_access_token, get_current_user_from_cookie
)
from app.utils import haversine, filter_stations_on_route
from app.predictor import predictor

# Initialize FastAPI app
app = FastAPI(title=settings.APP_NAME)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Load station data at startup
stations_df = None
STATIONS_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cleaned_data.csv")

# Ensure data directory exists
os.makedirs(os.path.dirname(STATIONS_CSV_PATH), exist_ok=True)

@app.on_event("startup")
def startup_event():
    """Create database tables and load station data on startup"""
    global stations_df
    
    # Create database tables
    create_tables()
    
    # Load station data
    try:
        stations_df = pd.read_csv(STATIONS_CSV_PATH)
        print(f"Loaded {len(stations_df)} stations from {STATIONS_CSV_PATH}")
    except FileNotFoundError:
        print(f"Warning: Station data file not found at {STATIONS_CSV_PATH}")
        print("Please run ml/preprocess.py to generate cleaned_data.csv")
        stations_df = pd.DataFrame()

# ==================== Authentication Routes ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - redirect to dashboard if logged in, else login"""
    user_email = get_current_user_from_cookie(request)
    if user_email:
        return RedirectResponse(url="/dashboard", status_code=307)
    return RedirectResponse(url="/login", status_code=307)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password."}
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "username": user.username},
        expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=3600
    )
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle registration form submission"""
    # Check password length
    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Password must be at least 8 characters."}
        )
    
    # Check password is not too long (bcrypt limitation: 72 bytes)
    if len(password.encode('utf-8')) > 72:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Password is too long. Maximum 72 characters allowed."}
        )
    
    # Check if email already exists
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered."}
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username already exists."}
        )
    
    # Create user
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
async def logout():
    """Handle logout"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response

# ==================== Dashboard Routes ====================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard with trip input form"""
    user_email = get_current_user_from_cookie(request)
    if not user_email:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(User).filter(User.email == user_email).first()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user}
    )

# ==================== Prediction Routes ====================

@app.post("/predict", response_class=HTMLResponse)
async def predict_route(
    request: Request,
    start_name: str = Form(...),
    dest_name: str = Form(...),
    battery_pct: float = Form(...),
    distance_km: float = Form(...),
    speed_kmh: float = Form(default=60),
    temp_celsius: float = Form(default=30),
    ac_on: int = Form(default=0),
    car_lat: float = Form(default=20.2961),
    car_lon: float = Form(default=85.8245),
    dest_lat: Optional[float] = Form(None),
    dest_lon: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """Handle route optimization prediction"""
    user_email = get_current_user_from_cookie(request)
    if not user_email:
        return RedirectResponse(url="/login", status_code=303)
    
    # Validation
    if battery_pct < 1 or battery_pct > 100:
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user": None, "error": "Battery % must be between 1 and 100."}
        )
    
    if distance_km <= 0:
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user": None, "error": "Distance must be greater than 0."}
        )
    
    # Use default destination coordinates if not provided
    if dest_lat is None or dest_lon is None:
        dest_lat = 20.2920  # Default: Railway Station
        dest_lon = 85.8280
    
    # Predict if charging is needed
    needs_charge = predictor.predict_needs_charge(
        battery_pct, distance_km, speed_kmh, temp_celsius, ac_on
    )
    
    # Filter stations on route
    stations_with_details = []
    if stations_df is not None and len(stations_df) > 0:
        filtered_stations = filter_stations_on_route(
            stations_df, car_lat, car_lon, dest_lat, dest_lon
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
    
    # Save to trip history
    top_station = stations_with_details[0]['name'] if stations_with_details else "None"
    trip = TripHistory(
        user_email=user_email,
        start_loc=start_name,
        destination=dest_name,
        battery_pct=battery_pct,
        station_rec=top_station
    )
    db.add(trip)
    db.commit()
    
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "user": None,
            "start_name": start_name,
            "destination": dest_name,
            "battery_pct": battery_pct,
            "needs_charge": needs_charge,
            "stations": stations_with_details
        }
    )

# ==================== History Routes ====================

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request, db: Session = Depends(get_db)):
    """Charging session history for the current user"""
    user_email = get_current_user_from_cookie(request)
    if not user_email:
        return RedirectResponse(url="/login", status_code=303)
    
    trips = db.query(TripHistory).filter(
        TripHistory.user_email == user_email
    ).order_by(TripHistory.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "user": None, "trips": trips}
    )

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
