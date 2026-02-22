import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import Column, String, Integer
from pathlib import Path
from sqlalchemy.orm import Session

# আপনার database.py থেকে ইমপোর্ট করা
from database import engine, SessionLocal, Base, get_db

# Railway-তে রান হওয়ার সময় অটোমেটিক টেবিল তৈরি করবে
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JINIE Backend")

# CORS সেটিংস (ব্রাউজার এরর এড়াতে)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "Index.html"

# Database Model (টেবিল স্ট্রাকচার)
class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    student_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String)
    hall_name = Column(String)
    password = Column(String)

@app.get("/")
async def serve_index():
    if not INDEX_FILE.exists():
        return {"error": "Index.html not found in root directory"}
    return FileResponse(INDEX_FILE)

# REGISTER ROUTE (Form Data রিসিভ করার জন্য আপডেট করা)
@app.post("/register")
async def register(
    name: str = Form(...),
    student_id: str = Form(...),
    email: str = Form(...),
    department: str = Form(...),
    hall_name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # ইউজার চেক
        existing = db.query(UserModel).filter(
            (UserModel.student_id == student_id) | (UserModel.email == email)
        ).first()
        
        if existing:
            return "Error: User already registered!"

        # নতুন ইউজার সেভ
        new_user = UserModel(
            name=name, student_id=student_id, email=email,
            department=department, hall_name=hall_name, password=password
        )
        db.add(new_user)
        db.commit()
        return f"Success: {name}, your account is created!"
    except Exception as e:
        db.rollback()
        return f"Error: {str(e)}"

# LOGIN ROUTE
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    return f"Welcome back, {username}! Login successful."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
