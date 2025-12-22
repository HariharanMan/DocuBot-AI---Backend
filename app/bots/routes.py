from fastapi import APIRouter, HTTPException
from app.db import db
import uuid

router = APIRouter(prefix="/bots", tags=["Bots"])


@router.post("/create")
def create_bot(bot_name: str, user_id: str = "demo_user"):
    bot_id = str(uuid.uuid4())

    db.bots.insert_one({
        "bot_id": bot_id,
        "user_id": user_id,
        "bot_name": bot_name
    })

    return {
        "bot_id": bot_id,
        "bot_name": bot_name
    }


@router.get("/")
def list_bots(user_id: str = "demo_user"):
    bots = list(
        db.bots.find(
            {"user_id": user_id},
            {"_id": 0}
        )
    )
    return bots
