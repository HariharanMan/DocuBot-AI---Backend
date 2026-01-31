from fastapi import Depends
from pydantic import BaseModel
import uuid

from app.db import db
from app.auth.jwt import get_current_user


class BotCreate(BaseModel):
    bot_name: str


def create_bot_service(data: BotCreate, user=Depends(get_current_user)):
    bot_id = str(uuid.uuid4())

    db.bots.insert_one({
        "bot_id": bot_id,
        "user_id": user["user_id"],
        "bot_name": data.bot_name,
    })

    return {
        "bot_id": bot_id,
        "bot_name": data.bot_name
    }


def list_bots_service(user=Depends(get_current_user)):
    bots = list(
        db.bots.find(
            {"user_id": user["user_id"]},
            {"_id": 0}
        )
    )
    return bots
