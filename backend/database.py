import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Dish

# Use Postgres in production (Railway sets DATABASE_URL), fall back to SQLite locally
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./calorie_count.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed dishes into database
def seed_dishes(db):
    existing_dishes = db.query(Dish).count()
    if existing_dishes > 0:
        return

    dishes = [
        Dish(name="Butter Chicken", cuisine="Indian", calories_per_100g=150, protein_per_100g=10, carbs_per_100g=6, fat_per_100g=9),
        Dish(name="Tandoori Chicken", cuisine="Indian", calories_per_100g=165, protein_per_100g=25, carbs_per_100g=2, fat_per_100g=7),
        Dish(name="Chicken Biryani", cuisine="Indian", calories_per_100g=210, protein_per_100g=9, carbs_per_100g=26, fat_per_100g=8),
        Dish(name="Chana Masala", cuisine="Indian", calories_per_100g=140, protein_per_100g=7, carbs_per_100g=20, fat_per_100g=4),
        Dish(name="Dal Makhani", cuisine="Indian", calories_per_100g=160, protein_per_100g=8, carbs_per_100g=18, fat_per_100g=7),
        Dish(name="Paneer Tikka", cuisine="Indian", calories_per_100g=175, protein_per_100g=14, carbs_per_100g=5, fat_per_100g=12),
        Dish(name="Aloo Gobi", cuisine="Indian", calories_per_100g=95, protein_per_100g=3, carbs_per_100g=12, fat_per_100g=4),
        Dish(name="Naan", cuisine="Indian", calories_per_100g=280, protein_per_100g=9, carbs_per_100g=50, fat_per_100g=5),
        Dish(name="Roti", cuisine="Indian", calories_per_100g=165, protein_per_100g=6, carbs_per_100g=33, fat_per_100g=2),
        Dish(name="Paratha", cuisine="Indian", calories_per_100g=200, protein_per_100g=5, carbs_per_100g=28, fat_per_100g=8),
        Dish(name="Fish Curry", cuisine="Indian", calories_per_100g=130, protein_per_100g=14, carbs_per_100g=4, fat_per_100g=6),
        Dish(name="Mutton Curry", cuisine="Indian", calories_per_100g=180, protein_per_100g=15, carbs_per_100g=4, fat_per_100g=12),
        Dish(name="Shrimp Curry", cuisine="Indian", calories_per_100g=120, protein_per_100g=15, carbs_per_100g=5, fat_per_100g=5),
        Dish(name="Vegetable Biryani", cuisine="Indian", calories_per_100g=185, protein_per_100g=4, carbs_per_100g=30, fat_per_100g=6),
        Dish(name="Raita", cuisine="Indian", calories_per_100g=60, protein_per_100g=3, carbs_per_100g=5, fat_per_100g=3),
        Dish(name="Lentil Soup", cuisine="Indian", calories_per_100g=85, protein_per_100g=6, carbs_per_100g=12, fat_per_100g=1),
        Dish(name="Mulligatawny", cuisine="Indian", calories_per_100g=95, protein_per_100g=4, carbs_per_100g=11, fat_per_100g=4),
        Dish(name="Bhindi Fry", cuisine="Indian", calories_per_100g=80, protein_per_100g=2, carbs_per_100g=8, fat_per_100g=5),
        Dish(name="Basmati Rice", cuisine="Indian", calories_per_100g=130, protein_per_100g=3, carbs_per_100g=28, fat_per_100g=0),
        Dish(name="Brown Rice", cuisine="Indian", calories_per_100g=111, protein_per_100g=3, carbs_per_100g=23, fat_per_100g=1),
        Dish(name="Jeera Rice", cuisine="Indian", calories_per_100g=135, protein_per_100g=3, carbs_per_100g=27, fat_per_100g=2),
        Dish(name="Puri", cuisine="Indian", calories_per_100g=250, protein_per_100g=5, carbs_per_100g=32, fat_per_100g=12),
        Dish(name="Pickled Vegetables", cuisine="Indian", calories_per_100g=30, protein_per_100g=1, carbs_per_100g=5, fat_per_100g=1),
        Dish(name="Chicken Shawarma", cuisine="MiddleEastern", calories_per_100g=195, protein_per_100g=17, carbs_per_100g=4, fat_per_100g=12),
        Dish(name="Lamb Shawarma", cuisine="MiddleEastern", calories_per_100g=220, protein_per_100g=16, carbs_per_100g=4, fat_per_100g=15),
        Dish(name="Hummus", cuisine="MiddleEastern", calories_per_100g=160, protein_per_100g=5, carbs_per_100g=14, fat_per_100g=10),
        Dish(name="Falafel", cuisine="MiddleEastern", calories_per_100g=330, protein_per_100g=13, carbs_per_100g=32, fat_per_100g=18),
        Dish(name="Tabbouleh", cuisine="MiddleEastern", calories_per_100g=80, protein_per_100g=2, carbs_per_100g=12, fat_per_100g=3),
        Dish(name="Baba Ghanoush", cuisine="MiddleEastern", calories_per_100g=140, protein_per_100g=3, carbs_per_100g=9, fat_per_100g=11),
        Dish(name="Kofta", cuisine="MiddleEastern", calories_per_100g=250, protein_per_100g=16, carbs_per_100g=5, fat_per_100g=18),
        Dish(name="Kibbeh", cuisine="MiddleEastern", calories_per_100g=280, protein_per_100g=13, carbs_per_100g=20, fat_per_100g=17),
        Dish(name="Grilled Lamb Chops", cuisine="MiddleEastern", calories_per_100g=290, protein_per_100g=25, carbs_per_100g=0, fat_per_100g=21),
        Dish(name="Grilled Fish", cuisine="MiddleEastern", calories_per_100g=130, protein_per_100g=22, carbs_per_100g=0, fat_per_100g=5),
        Dish(name="Lula Kebab", cuisine="MiddleEastern", calories_per_100g=240, protein_per_100g=15, carbs_per_100g=3, fat_per_100g=18),
        Dish(name="Mujadara", cuisine="MiddleEastern", calories_per_100g=110, protein_per_100g=5, carbs_per_100g=18, fat_per_100g=3),
        Dish(name="Dolma", cuisine="MiddleEastern", calories_per_100g=100, protein_per_100g=2, carbs_per_100g=14, fat_per_100g=4),
        Dish(name="Fattoush", cuisine="MiddleEastern", calories_per_100g=120, protein_per_100g=2, carbs_per_100g=13, fat_per_100g=7),
        Dish(name="Mansaf", cuisine="MiddleEastern", calories_per_100g=180, protein_per_100g=12, carbs_per_100g=18, fat_per_100g=7),
        Dish(name="Maqluba", cuisine="MiddleEastern", calories_per_100g=200, protein_per_100g=8, carbs_per_100g=28, fat_per_100g=7),
        Dish(name="Pita Bread", cuisine="MiddleEastern", calories_per_100g=275, protein_per_100g=9, carbs_per_100g=55, fat_per_100g=2),
        Dish(name="Lavash", cuisine="MiddleEastern", calories_per_100g=240, protein_per_100g=8, carbs_per_100g=48, fat_per_100g=2),
        Dish(name="Tzatziki", cuisine="MiddleEastern", calories_per_100g=70, protein_per_100g=3, carbs_per_100g=4, fat_per_100g=5),
        Dish(name="Tahini Paste", cuisine="MiddleEastern", calories_per_100g=595, protein_per_100g=17, carbs_per_100g=21, fat_per_100g=54),
        Dish(name="Tomato Lentil Soup", cuisine="MiddleEastern", calories_per_100g=90, protein_per_100g=5, carbs_per_100g=14, fat_per_100g=2),
    ]

    db.add_all(dishes)
    db.commit()

# Seed on startup
db = SessionLocal()
seed_dishes(db)
db.close()
