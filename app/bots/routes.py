from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
import uuid
import numpy as np

from app.db import db
from app.services.loader import load_document
from app.services.namer import generate_doc_name
from app.services.chunker import chunk_text
from app.services.embedder import embed_text
from app.services.qa import answer_question
from app.auth.jwt import get_current_user


router = APIRouter(prefix="/bots", tags=["Bots"])


# =========================================================
# 🤖 CREATE BOT  (unchanged)
# =========================================================
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


# =========================================================
# 📋 LIST BOTS  (unchanged)
# =========================================================
@router.get("/")
def list_bots(user_id: str = "demo_user"):
    bots = list(
        db.bots.find(
            {"user_id": user_id},
            {"_id": 0}
        )
    )
    return bots


# =========================================================
# 📄 LIST DOCUMENTS OF A BOT
# =========================================================
@router.get("/{bot_id}/documents")
def list_documents(bot_id: str, user_id: str = "demo_user"):
    docs = list(
        db.documents.find(
            {
                "bot_id": bot_id,
                "user_id": user_id
            },
            {
                "_id": 0,
                "doc_id": 1,
                "doc_name": 1,
                "original_filename": 1
            }
        )
    )
    return docs


# =========================================================
# 📤 UPLOAD DOCUMENT TO BOT
# =========================================================
@router.post("/{bot_id}/upload")
async def upload_document(
    bot_id: str,
    file: UploadFile = File(...),
    user_id: str = "demo_user"
):
    bot = db.bots.find_one({
        "bot_id": bot_id,
        "user_id": user_id
    })

    if not bot:
        raise HTTPException(status_code=403, detail="Bot not found")

    text = load_document(file)
    doc_name = generate_doc_name(text)
    doc_id = str(uuid.uuid4())

    chunks = chunk_text(text)
    embeddings = embed_text(chunks)

    collection_name = f"{user_id}_{bot_id}_{doc_name.replace(' ', '_')}"

    db.documents.insert_one({
        "doc_id": doc_id,
        "bot_id": bot_id,
        "user_id": user_id,
        "doc_name": doc_name,
        "original_filename": file.filename,
        "collection_name": collection_name
    })

    collection = db[collection_name]

    for i, chunk in enumerate(chunks):
        collection.insert_one({
            "chunk_id": i,
            "content": chunk,
            "embedding": embeddings[i].tolist()
        })

    return {
        "doc_id": doc_id,
        "doc_name": doc_name
    }


# =========================================================
# 💬 ASK BOT
# =========================================================
@router.post("/{bot_id}/ask")
def ask_bot(
    bot_id: str,
    question: str,
    user_id: str = "demo_user"
):
    bot = db.bots.find_one({
        "bot_id": bot_id,
        "user_id": user_id
    })

    if not bot:
        raise HTTPException(status_code=403, detail="Bot not found")

    docs = list(db.documents.find({
        "bot_id": bot_id,
        "user_id": user_id
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
