# app/models.py
# SQLAlchemy ORM models for database tables

from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings
import os

Base = declarative_base()

# Get absolute path for database
if settings.DATABASE_URL.startswith("sqlite:///"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        # If relative path, make it absolute from project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, db_path)
    db_url = f"sqlite:///{db_path}"
else:
    db_url = settings.DATABASE_URL

# Create database engine
engine = create_engine(db_url, connect_args={"check_same_thread": False})

# Ensure database directory exists
db_dir = os.path.dirname(db_path)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)

class TripHistory(Base):
    """Trip history model"""
    __tablename__ = "trip_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(120), nullable=False, index=True)
    start_loc = Column(String(200))
    destination = Column(String(200))
    battery_pct = Column(Float)
    station_rec = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
