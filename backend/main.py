from fastapi import FastAPI, Depends, HTTPException, status
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

def get_current_user(token: str = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ============== AUTH ENDPOINTS ==============

@app.post("/api/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = User(email=user.email)
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create JWT token
    token = jwt.encode({"sub": new_user.id}, SECRET_KEY, algorithm="HS256")
    
    return {"id": new_user.id, "email": new_user.email, "token": token}

@app.post("/api/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not db_user.check_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    token = jwt.encode({"sub": db_user.id}, SECRET_KEY, algorithm="HS256")
    
    return {"id": db_user.id, "email": db_user.email, "token": token}

# ============== PROFILE ENDPOINTS ==============

@app.post("/api/profile")
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db), authorization: str = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    
    # Check if profile exists
    existing_profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if existing_profile:
        # Update existing
        existing_profile.weight = profile.weight
        existing_profile.height = profile.height
        existing_profile.age = profile.age
        existing_profile.sex = profile.sex
        existing_profile.activity_level = profile.activity_level
        existing_profile.goal = profile.goal
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    
    # Create new profile
    new_profile = Profile(
        user_id=user.id,
        weight=profile.weight,
        height=profile.height,
        age=profile.age,
        sex=profile.sex,
        activity_level=profile.activity_level,
        goal=profile.goal
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return new_profile

@app.get("/api/profile")
def get_profile(db: Session = Depends(get_db), authorization: str = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
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
    
    return {
        "id": profile.id,
        "weight": profile.weight,
        "height": profile.height,
        "age": profile.age,
        "sex": profile.sex,
        "activity_level": profile.activity_level,
        "goal": profile.goal,
        "bmr": bmr,
        "tdee": tdee,
        "daily_target": int(daily_target)
    }

# ============== DISHES ENDPOINTS ==============

@app.get("/api/dishes")
def get_dishes(db: Session = Depends(get_db)):
    dishes = db.query(Dish).all()
    return [{"id": d.id, "name": d.name, "calories_per_100g": d.calories_per_100g} for d in dishes]

# ============== MEALS ENDPOINTS ==============

@app.post("/api/meals")
def create_meal(meal: MealCreate, db: Session = Depends(get_db), authorization: str = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    
    dish = db.query(Dish).filter(Dish.id == meal.dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    calories = int((dish.calories_per_100g / 100) * meal.grams_confirmed)
    
    new_meal = Meal(
        user_id=user.id,
        dish_id=meal.dish_id,
        grams_confirmed=meal.grams_confirmed,
        calories=calories,
        date=meal.date or datetime.now().date()
    )
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    
    return new_meal

@app.get("/api/meals")
def get_meals(date: str = None, db: Session = Depends(get_db), authorization: str = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    
    if not date:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    
    meals = db.query(Meal).filter(Meal.user_id == user.id, Meal.date == date).all()
    
    return [
        {
            "id": m.id,
            "dish_id": m.dish_id,
            "dish_name": db.query(Dish).filter(Dish.id == m.dish_id).first().name,
            "grams_confirmed": m.grams_confirmed,
            "calories": m.calories,
            "date": m.date.isoformat()
        }
        for m in meals
    ]

@app.delete("/api/meals/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db), authorization: str = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == user.id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    db.delete(meal)
    db.commit()
    
    return {"message": "Meal deleted"}

# ============== SUMMARY ENDPOINTS ==============

@app.get("/api/daily-summary")
def get_daily_summary(date: str = None, db: Session = Depends(get_db), authorization: str = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if not date:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    
    meals = db.query(Meal).filter(Meal.user_id == user.id, Meal.date == date).all()
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
        status = "Low"
    elif total_calories <= daily_target + 100:
        status = "On Target"
    else:
        status = "Over"
    
    return {
        "date": date.isoformat(),
        "total_calories": total_calories,
        "daily_target": int(daily_target),
        "remaining": remaining,
        "status": status,
        "meals": [
            {
                "id": m.id,
                "dish_name": db.query(Dish).filter(Dish.id == m.dish_id).first().name,
                "calories": m.calories,
                "grams": m.grams_confirmed
            }
            for m in meals
        ]
    }

# ============== HEALTH CHECK ==============

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# ============== SERVE FRONTEND ==============

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(static_dir, "index.html"))