import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer
from pathlib import Path
from database import engine, SessionLocal, Base, get_db
from sqlalchemy.orm import Session

# Create tables
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

# ---------- PYDANTIC MODEL ----------
class User(BaseModel):
    name: str
    student_id: str
    email: str
    department: str
    hall_name: str
    password: str

# ---------- REGISTER ----------
@app.post("/register")
async def register(user: User, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = db.query(UserModel).filter(
            (UserModel.student_id == user.student_id) | 
            (UserModel.email == user.email)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already registered")
        
        # Create new user
        db_user = UserModel(
            name=user.name,
            student_id=user.student_id,
            email=user.email,
            department=user.department,
            hall_name=user.hall_name,
            password=user.password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "status": "success",
            "message": f"Data for {user.name} saved successfully!"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ---------- FOR RUNNING DIRECTLY ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
