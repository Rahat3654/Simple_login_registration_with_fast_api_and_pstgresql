from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/", StaticFiles(directory="static", html=True))

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    db: Session = SessionLocal()
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.close()
    return {"msg": "registered"}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    db: Session = SessionLocal()
    user = db.query(User).filter_by(username=username, password=password).first()
    db.close()

    if user:
        return {"msg": "login success"}
    return {"msg": "invalid credentials"}