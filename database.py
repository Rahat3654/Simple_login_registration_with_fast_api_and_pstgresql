from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Railway থেকে ডাটাবেস ইউআরএল নেওয়া
DATABASE_URL = os.environ.get("DATABASE_URL")

# Railway 'postgres://' পাঠালে সেটাকে SQLAlchemy এর জন্য 'postgresql://' এ রূপান্তর
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# কানেকশন ইঞ্জিন (pool_pre_ping কানেকশন ড্রপ হওয়া রোধ করে)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
