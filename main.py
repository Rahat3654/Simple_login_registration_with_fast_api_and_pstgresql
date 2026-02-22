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

# ---------- DATABASE TABLES CREATE ----------
# এটি রান হওয়ার সময় অটোমেটিক Railway ডাটাবেসে টেবিল তৈরি করবে
Base.metadata.create_all(bind=engine)

# ---------- APP INIT ----------
app = FastAPI(title="Rahat Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- FILE PATH ----------
BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "Index.html"

# ---------- DATABASE MODEL ----------
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    student_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String)
    hall_name = Column(String)
    password = Column(String)

# ---------- SERVE INDEX ----------
@app.get("/")
async def serve_index():
    if not INDEX_FILE.exists():
        raise HTTPException(status_code=404, detail="Index.html not found")
    return FileResponse(INDEX_FILE)

# ---------- REGISTER (Updated with Form) ----------
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
        # ১. ইউজার আগে থেকেই আছে কিনা চেক করা
        existing_user = db.query(UserModel).filter(
            (UserModel.student_id == student_id) | 
            (UserModel.email == email)
        ).first()
        
        if existing_user:
            # যদি ইউজার থাকে তবে এরর মেসেজ
            return {"status": "error", "message": "User already registered with this Student ID or Email"}
        
        # ২. নতুন ইউজার তৈরি করা
        db_user = UserModel(
            name=name,
            student_id=student_id,
            email=email,
            department=department,
            hall_name=hall_name,
            password=password
        )
        
        # ৩. ডাটাবেসে সেভ করা
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "status": "success", 
            "message": f"Data for {name} saved successfully to Railway Database!"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ---------- RUN APP ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
