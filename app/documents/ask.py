from fastapi import APIRouter
from app.db import db
from app.services.embedder import embed_text
from app.services.qa import answer_question
import numpy as np

router = APIRouter(prefix="/documents")

@router.post("/ask")
def ask(user_id: str, doc_id: str, question: str):
    doc = db.documents.find_one({"doc_id": doc_id, "user_id": user_id})
    if not doc:
        return {"error": "Document not found"}

    collection = db[doc["collection"]]
    q_embed = embed_text([question])[0]

    scored = []
    for c in collection.find():
        score = np.dot(q_embed, c["embedding"])
        scored.append((score, c["content"]))

    top = sorted(scored, reverse=True)[:3]
    context = "\n".join([t[1] for t in top])

    return {"answer": answer_question(context, question)}
