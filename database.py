from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ১. এনভায়রনমেন্ট ভেরিয়েবল থেকে URL নেওয়া
DATABASE_URL = os.environ.get("DATABASE_URL")

# ২. Railway 'postgres://' পাঠালে সেটাকে 'postgresql://' এ রূপান্তর করা (খুবই গুরুত্বপূর্ণ)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ৩. লোকাল টেস্টিং এর জন্য একটি ব্যাকআপ (ঐচ্ছিক)
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/railway"

# Create SQLAlchemy engine
# pool_pre_ping=True কানেকশন ড্রপ হওয়া রোধ করে
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
