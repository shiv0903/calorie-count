from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Dish

# Database URL - SQLite for local, PostgreSQL for production
DATABASE_URL = "sqlite:///./calorie_count.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed dishes into database
def seed_dishes(db):
    # Check if dishes already exist
    existing_dishes = db.query(Dish).count()
    if existing_dishes > 0:
        return
    
    # Indian Dishes
    indian_dishes = [
        Dish(name="Butter Chicken", cuisine="Indian", calories_per_100g=150),
        Dish(name="Tandoori Chicken", cuisine="Indian", calories_per_100g=165),
        Dish(name="Chicken Biryani", cuisine="Indian", calories_per_100g=210),
        Dish(name="Chana Masala", cuisine="Indian", calories_per_100g=140),
        Dish(name="Dal Makhani", cuisine="Indian", calories_per_100g=160),
        Dish(name="Paneer Tikka", cuisine="Indian", calories_per_100g=175),
        Dish(name="Aloo Gobi", cuisine="Indian", calories_per_100g=95),
        Dish(name="Naan", cuisine="Indian", calories_per_100g=280),
        Dish(name="Roti", cuisine="Indian", calories_per_100g=165),
        Dish(name="Paratha", cuisine="Indian", calories_per_100g=200),
        Dish(name="Fish Curry", cuisine="Indian", calories_per_100g=130),
        Dish(name="Mutton Curry", cuisine="Indian", calories_per_100g=180),
        Dish(name="Shrimp Curry", cuisine="Indian", calories_per_100g=120),
        Dish(name="Vegetable Biryani", cuisine="Indian", calories_per_100g=185),
        Dish(name="Raita", cuisine="Indian", calories_per_100g=60),
        Dish(name="Lentil Soup", cuisine="Indian", calories_per_100g=85),
        Dish(name="Mulligatawny", cuisine="Indian", calories_per_100g=95),
        Dish(name="Bhindi Fry", cuisine="Indian", calories_per_100g=80),
        Dish(name="Basmati Rice", cuisine="Indian", calories_per_100g=130),
        Dish(name="Brown Rice", cuisine="Indian", calories_per_100g=111),
        Dish(name="Jeera Rice", cuisine="Indian", calories_per_100g=135),
        Dish(name="Puri", cuisine="Indian", calories_per_100g=250),
        Dish(name="Pickled Vegetables", cuisine="Indian", calories_per_100g=30),
        Dish(name="Chicken Shawarma", cuisine="MiddleEastern", calories_per_100g=195),
        Dish(name="Lamb Shawarma", cuisine="MiddleEastern", calories_per_100g=220),
        Dish(name="Hummus", cuisine="MiddleEastern", calories_per_100g=160),
        Dish(name="Falafel", cuisine="MiddleEastern", calories_per_100g=330),
        Dish(name="Tabbouleh", cuisine="MiddleEastern", calories_per_100g=80),
        Dish(name="Baba Ghanoush", cuisine="MiddleEastern", calories_per_100g=140),
        Dish(name="Kofta", cuisine="MiddleEastern", calories_per_100g=250),
        Dish(name="Kibbeh", cuisine="MiddleEastern", calories_per_100g=280),
        Dish(name="Grilled Lamb Chops", cuisine="MiddleEastern", calories_per_100g=290),
        Dish(name="Grilled Fish", cuisine="MiddleEastern", calories_per_100g=130),
        Dish(name="Lula Kebab", cuisine="MiddleEastern", calories_per_100g=240),
        Dish(name="Mujadara", cuisine="MiddleEastern", calories_per_100g=110),
        Dish(name="Dolma", cuisine="MiddleEastern", calories_per_100g=100),
        Dish(name="Fattoush", cuisine="MiddleEastern", calories_per_100g=120),
        Dish(name="Mansaf", cuisine="MiddleEastern", calories_per_100g=180),
        Dish(name="Maqluba", cuisine="MiddleEastern", calories_per_100g=200),
        Dish(name="Pita Bread", cuisine="MiddleEastern", calories_per_100g=275),
        Dish(name="Lavash", cuisine="MiddleEastern", calories_per_100g=240),
        Dish(name="Tzatziki", cuisine="MiddleEastern", calories_per_100g=70),
        Dish(name="Tahini Paste", cuisine="MiddleEastern", calories_per_100g=595),
        Dish(name="Tomato Lentil Soup", cuisine="MiddleEastern", calories_per_100g=90),
    ]
    
    db.add_all(indian_dishes)
    db.commit()

# Seed on startup
db = SessionLocal()
seed_dishes(db)
db.close()
