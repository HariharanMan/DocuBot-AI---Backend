from fastapi import APIRouter, HTTPException
from app.db import db
from app.auth.jwt import create_token
from app.auth.password import hash_password, verify_password
import uuid

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup")
def signup(email: str, password: str):
    if db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")

    user_id = str(uuid.uuid4())

    db.users.insert_one({
        "user_id": user_id,
        "email": email,
        "password": hash_password(password)
    })

    return {"message": "User created successfully"}


@router.post("/login")
def login(email: str, password: str):
    user = db.users.find_one({"email": email})

    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "user_id": user["user_id"],
        "email": user["email"]
    })

    return {"token": token}
