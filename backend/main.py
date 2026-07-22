from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
import jwt
import requests
from database import engine, SessionLocal, Base
from models import User, Profile, Dish, Meal
from schemas import UserCreate, UserLogin, ProfileCreate, MealCreate
from calculations import calculate_bmr, calculate_tdee

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
USDA_API_KEY = os.getenv("USDA_API_KEY", "")

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
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

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
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Profile).filter(Profile.user_id == current_user.id).first()
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
    new_profile = Profile(user_id=current_user.id, weight=profile.weight, height=profile.height, age=profile.age, sex=profile.sex, activity_level=profile.activity_level, goal=profile.goal)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@app.get("/api/profile")
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
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

@app.post("/api/dishes")
def create_dish(name: str, calories_per_100g: float, cuisine: str = "Custom", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Dish).filter(Dish.name == name).first()
    if existing:
        return {"id": existing.id, "name": existing.name, "calories_per_100g": existing.calories_per_100g}
    new_dish = Dish(name=name, cuisine=cuisine, calories_per_100g=calories_per_100g)
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    return {"id": new_dish.id, "name": new_dish.name, "calories_per_100g": new_dish.calories_per_100g}

@app.get("/api/lookup-calories")
def lookup_calories(name: str, current_user: User = Depends(get_current_user)):
    if not USDA_API_KEY:
        raise HTTPException(status_code=503, detail="Calorie lookup is not configured")
    try:
        resp = requests.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={"api_key": USDA_API_KEY, "query": name, "pageSize": 5, "dataType": "Survey (FNDDS),Foundation,SR Legacy"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Could not reach the nutrition database")

    foods = data.get("foods", [])
    if not foods:
        raise HTTPException(status_code=404, detail=f"No nutrition match found for '{name}'")

    for food in foods:
        for nutrient in food.get("foodNutrients", []):
            nutrient_name = (nutrient.get("nutrientName") or "").lower()
            unit = (nutrient.get("unitName") or "").lower()
            if "energy" in nutrient_name and unit == "kcal":
                value = nutrient.get("value")
                if value is not None:
                    return {
                        "name": name,
                        "matched_food": food.get("description", name),
                        "calories_per_100g": round(float(value), 1),
                    }
    raise HTTPException(status_code=404, detail=f"No calorie data found for '{name}'")

@app.post("/api/meals")
def create_meal(meal: MealCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dish = db.query(Dish).filter(Dish.id == meal.dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    calories = int((dish.calories_per_100g / 100) * meal.grams_confirmed)
    meal_date = meal.date if meal.date else datetime.now().date()
    new_meal = Meal(user_id=current_user.id, dish_id=meal.dish_id, grams_confirmed=meal.grams_confirmed, calories=calories, date=meal_date)
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return new_meal

@app.get("/api/meals")
def get_meals(date: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not date:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    meals = db.query(Meal).filter(Meal.user_id == current_user.id, Meal.date == date).all()
    return [{"id": m.id, "dish_id": m.dish_id, "dish_name": db.query(Dish).filter(Dish.id == m.dish_id).first().name, "grams_confirmed": m.grams_confirmed, "calories": m.calories, "date": m.date.isoformat()} for m in meals]

@app.delete("/api/meals/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == current_user.id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.delete(meal)
    db.commit()
    return {"message": "Meal deleted"}

@app.get("/api/daily-summary")
def get_daily_summary(date: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if not date:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    meals = db.query(Meal).filter(Meal.user_id == current_user.id, Meal.date == date).all()
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

app.mount("/static", StaticFiles(directory="/app/static/static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("/app/static/index.html", media_type="text/html")

@app.get("/{full_path:path}")
def catch_all(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API not found")
    file_path = os.path.join("/app/static", full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse("/app/static/index.html", media_type="text/html")
