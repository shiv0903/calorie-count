from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
import jwt

from database import engine, SessionLocal, Base
from models import User, Profile, Dish, Meal
from schemas import UserCreate, UserLogin, ProfileCreate, MealCreate
from calculations import calculate_bmr, calculate_tdee

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

SECRET_KEY = "your-secret-key"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=user.email)
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = jwt.encode({"sub": new_user.id}, SECRET_KEY, algorithm="HS256")
    return {"id": new_user.id, "email": new_user.email, "token": token}

@app.post("/api/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not db_user.check_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": db_user.id}, SECRET_KEY, algorithm="HS256")
    return {"id": db_user.id, "email": db_user.email, "token": token}

@app.post("/api/profile")
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(Profile).first()
    if existing:
        existing.weight = profile.weight
        existing.height = profile.height
        existing.age = profile.age
        existing.sex = profile.sex
        existing.activity_level = profile.activity_level
        existing.goal = profile.goal
        db.commit()
        db.refresh(existing)
        return existing
    new_profile = Profile(user_id=1, weight=profile.weight, height=profile.height, age=profile.age, sex=profile.sex, activity_level=profile.activity_level, goal=profile.goal)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@app.get("/api/profile")
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    bmr = calculate_bmr(profile.weight, profile.height, profile.age, profile.sex)
    tdee = calculate_tdee(bmr, profile.activity_level)
    if profile.goal == "lose":
        daily_target = max(1200 if profile.sex == "female" else 1500, tdee - 500)
    elif profile.goal == "gain":
        daily_target = tdee + 400
    else:
        daily_target = tdee
    return {"id": profile.id, "weight": profile.weight, "height": profile.height, "age": profile.age, "sex": profile.sex, "activity_level": profile.activity_level, "goal": profile.goal, "bmr": bmr, "tdee": tdee, "daily_target": int(daily_target)}

@app.get("/api/dishes")
def get_dishes(db: Session = Depends(get_db)):
    dishes = db.query(Dish).all()
    return [{"id": d.id, "name": d.name, "calories_per_100g": d.calories_per_100g} for d in dishes]

@app.post("/api/meals")
def create_meal(meal: MealCreate, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == meal.dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    calories = int((dish.calories_per_100g / 100) * meal.grams_confirmed)
    new_meal = Meal(user_id=1, dish_id=meal.dish_id,
