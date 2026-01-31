from fastapi import Depends, HTTPException
import numpy as np

from app.db import db
from app.auth.jwt import get_current_user
from app.services.embedder import embed_text
from app.services.qa import answer_question


def ask_bot_service(
    bot_id: str,
    question: str,
    user=Depends(get_current_user)
):
    bot = db.bots.find_one({
        "bot_id": bot_id,
        "user_id": user["user_id"]
    })

    if not bot:
        raise HTTPException(status_code=403, detail="Bot not found")

    docs = list(db.documents.find({
        "bot_id": bot_id,
        "user_id": user["user_id"]
    }))

    if not docs:
        return {"answer": "No documents uploaded yet."}

    q_embedding = embed_text([question])[0]
    scored = []

    for doc in docs:
        col = db[doc["collection_name"]]
        for c in col.find({}, {"content": 1, "embedding": 1}):
            score = np.dot(q_embedding, c["embedding"])
            scored.append((score, c["content"]))

    top_chunks = sorted(scored, reverse=True)[:3]
    context = "\n".join([c[1] for c in top_chunks])

    answer = answer_question(context, question)
    return {"answer": answer}
