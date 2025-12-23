from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import numpy as np

# services
from app.services.loader import load_document
from app.services.namer import generate_doc_name
from app.services.chunker import chunk_text
from app.services.embedder import embed_text
from app.services.qa import answer_question

# database
from app.db import db

# auth
from app.auth.routes import router as auth_router
from app.auth.jwt import get_current_user


app = FastAPI(title="DocuBot AI – Multi User RAG")

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# auth routes
app.include_router(auth_router)

# =========================
# BOT MODELS
# =========================
class BotCreate(BaseModel):
    bot_name: str


# =========================
# BOT MANAGEMENT
# =========================
@app.post("/bots/create")
def create_bot(
    data: BotCreate,
    user=Depends(get_current_user)
):
    bot_id = str(uuid.uuid4())

    db.bots.insert_one({
        "bot_id": bot_id,
        "user_id": user["user_id"],
        "bot_name": data.bot_name
    })

    return {
        "bot_id": bot_id,
        "bot_name": data.bot_name
    }


@app.get("/bots")
def list_bots(user=Depends(get_current_user)):
    bots = list(
        db.bots.find(
            {"user_id": user["user_id"]},
            {"_id": 0}
        )
    )
    return bots


# =========================
# UPLOAD DOCUMENT
# =========================
@app.post("/bots/{bot_id}/upload")
async def upload_document(
    bot_id: str,
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    bot = db.bots.find_one({
        "bot_id": bot_id,
        "user_id": user["user_id"]
    })

    if not bot:
        raise HTTPException(status_code=403, detail="Bot not found")

    text = load_document(file)
    doc_name = generate_doc_name(text)
    doc_id = str(uuid.uuid4())

    chunks = chunk_text(text)
    embeddings = embed_text(chunks)

    collection_name = f"{user['user_id']}_{bot_id}_{doc_name.replace(' ', '_')}"

    db.documents.insert_one({
        "doc_id": doc_id,
        "bot_id": bot_id,
        "user_id": user["user_id"],
        "collection_name": collection_name
    })

    collection = db[collection_name]

    for i, chunk in enumerate(chunks):
        collection.insert_one({
            "chunk_id": i,
            "content": chunk,
            "embedding": embeddings[i].tolist()
        })

    return {"doc_name": doc_name}


# =========================
# ASK BOT
# =========================
@app.post("/bots/{bot_id}/ask")
def ask_bot(
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
        for c in col.find():
            score = np.dot(q_embedding, c["embedding"])
            scored.append((score, c["content"]))

    top_chunks = sorted(scored, reverse=True)[:3]
    context = "\n".join([c[1] for c in top_chunks])

    answer = answer_question(context, question)
    return {"answer": answer}
