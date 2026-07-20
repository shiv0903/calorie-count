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
    new_meal = Meal(user_id=1, dish_id=meal.dish_id, grams_confirmed=meal.grams_confirmed, calories=calories, date=meal.date or datetime.now().date())
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return new_meal

@app.get("/api/meals")
def get_meals(date: str = None, db: Session = Depends(get_db)):
    if not date:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    meals = db.query(Meal).filter(Meal.date == date).all()
    return [{"id": m.id, "dish_id": m.dish_id, "dish_name": db.query(Dish).filter(Dish.id == m.dish_id).first().name, "grams_confirmed": m.grams_confirmed, "calories": m.calories, "date": m.date.isoformat()} for m in meals]

@app.delete("/api/meals/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.delete(meal)
    db.commit()
    return {"message": "Meal deleted"}

@app.get("/api/daily-summary")
def get_daily_summary(date: str = None, db: Session = Depends(get_db)):
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if not date:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    meals = db.query(Meal).filter(Meal.date == date).all()
    total_calories = sum(m.calories for m in meals)
    bmr = calculate_bmr(profile.weight, profile.height, profile.age, profile.sex)
    tdee = calculate_tdee(bmr, profile.activity_level)
    if profile.goal == "lose":
        daily_target = max(1200 if profile.sex == "female" else 1500, tdee - 500)
    elif profile.goal == "gain":
        daily_target = tdee + 400
    else:
        daily_target = tdee
    remaining = int(daily_target - total_calories)
    if total_calories < daily_target:
        status_val = "Low"
    elif total_calories <= daily_target + 100:
        status_val = "On Target"
    else:
        status_val = "Over"
    return {"date": date.isoformat(), "total_calories": total_calories, "daily_target": int(daily_target), "remaining": remaining, "status": status_val, "meals": [{"id": m.id, "dish_name": db.query(Dish).filter(Dish.id == m.dish_id).first().name, "calories": m.calories, "grams": m.grams_confirmed} for m in meals]}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/debug")
def debug():
    info = {}
    info["cwd"] = os.getcwd()
    info["static_exists"] = os.path.exists("/app/static")
    info["app_contents"] = os.listdir("/app") if os.path.exists("/app") else "no /app"
    info["static_contents"] = os.listdir("/app/static") if os.path.exists("/app/static") else "no /app/static"
    return info

static_dir = "/app/static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_frontend():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"error": "index.html not found", "static_dir_exists": os.path.exists(static_dir), "static_contents": os.listdir(static_dir) if os.path.exists(static_dir) else "missing", "app_contents": os.listdir("/app") if os.path.exists("/app") else "missing"}

@app.get("/{full_path:path}")
def catch_all(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API not found")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"error": "Not found"}
