from fastapi import APIRouter, HTTPException
from app.db import db
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_token
import uuid

router = APIRouter(prefix="/auth")

@router.post("/signup")
def signup(email: str, password: str):
    if db.users.find_one({"email": email}):
        raise HTTPException(400, "User exists")

    user_id = str(uuid.uuid4())
    db.users.insert_one({
        "user_id": user_id,
        "email": email,
        "password": hash_password(password)
    })
    return {"message": "User created"}

@router.post("/login")
def login(email: str, password: str):
    user = db.users.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(user["user_id"])
    return {"token": token}
