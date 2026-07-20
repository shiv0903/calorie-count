from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("Profile", back_populates="user", uselist=False)
    meals = relationship("Meal", back_populates="user")
    
    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
    
    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    weight = Column(Float)  # kg
    height = Column(Float)  # cm
    age = Column(Integer)
    sex = Column(String)  # male, female
    activity_level = Column(String)  # sedentary, light, moderate, active, very_active
    goal = Column(String)  # lose, maintain, gain
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")

class Dish(Base):
    __tablename__ = "dishes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cuisine = Column(String)  # Indian, MiddleEastern
    calories_per_100g = Column(Float)
    
    meals = relationship("Meal", back_populates="dish")

class Meal(Base):
    __tablename__ = "meals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    grams_confirmed = Column(Float)
    calories = Column(Integer)
    date = Column(Date, default=datetime.utcnow().date())
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="meals")
    dish = relationship("Dish", back_populates="meals")
