from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import jwt

from database import engine, SessionLocal, Base
from models import User, Profile, Dish, Meal
from schemas import UserCreate, UserLogin, ProfileCreate, MealCreate, MealResponse
from calculations import calculate_bmr, calculate_tdee

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Calorie Count API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
