from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ProfileCreate(BaseModel):
    weight: float
    height: float
    age: int
    sex: str  # male, female
    activity_level: str  # sedentary, light, moderate, active, very_active
    goal: str  # lose, maintain, gain

class ProfileResponse(BaseModel):
    id: int
    weight: float
    height: float
    age: int
    sex: str
    activity_level: str
    goal: str
    bmr: float
    tdee: float
    daily_target: int
    
    class Config:
        from_attributes = True

class DishResponse(BaseModel):
    id: int
    name: str
    calories_per_100g: float
    
    class Config:
        from_attributes = True

class MealCreate(BaseModel):
    dish_id: int
    grams_confirmed: float
    date: Optional[date] = None

class MealResponse(BaseModel):
    id: int
    dish_id: int
    dish_name: str
    grams_confirmed: float
    calories: int
    date: date
    
    class Config:
        from_attributes = True

class DailySummaryResponse(BaseModel):
    date: date
    total_calories: int
    daily_target: int
    remaining: int
    status: str  # Low, On Target, Over
    meals: list[MealResponse]