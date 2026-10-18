# backend/app/schemas.py
# Pydantic schemas for request/response validation

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8)

class User(UserBase):
    """Schema for user response"""
    id: int
    
    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None

# Trip Prediction Schema
class TripPredictionRequest(BaseModel):
    """Schema for trip prediction request"""
    start_name: str
    dest_name: str
    battery_pct: float = Field(..., ge=1, le=100)
    distance_km: float = Field(..., gt=0)
    speed_kmh: float = Field(default=60, gt=0, le=200)
    temp_celsius: float = Field(default=30, ge=-10, le=60)
    ac_on: int = Field(default=0, ge=0, le=1)
    car_lat: float = Field(default=20.2961)
    car_lon: float = Field(default=85.8245)
    dest_lat: Optional[float] = None
    dest_lon: Optional[float] = None
