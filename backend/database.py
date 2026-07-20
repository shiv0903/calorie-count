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
    # Check if dishes