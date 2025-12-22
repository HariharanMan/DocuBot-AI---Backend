from fastapi import FastAPI, UploadFile, File, HTTPException
import uuid
import numpy as np

# ===== services =====
from app.services.loader import load_document
from app.services.namer import generate_doc_name
from app.services.chunker import chunk_text
from app.services.embedder import embed_text
from app.services.qa import answer_question

# ===== database =====
from app.db import db

# ===== auth =====
from app.auth.routes import router as auth_router


app = FastAPI(title="Multi-Bot RAG with FastAPI + MongoDB")

# 🔐 auth routes
app.include_router(auth_router)

# =========================================================
# 🤖 BOT MANAGEMENT
# =========================================================

@app.post("/bots/create")
def create_bot(
    bot_name: str,
    user_id: str = "demo_user"   # later from JWT
):
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


@app.get("/bots")
def list_bots(user_id: str = "demo_user"):
    bots = list(
        db.bots.find(
            {"user_id": user_id},
            {"_id": 0}
        )
    )
    return bots


# =========================================================
# 📄 UPLOAD DOCUMENT TO A BOT
# =========================================================

@app.post("/bots/{bot_id}/upload")
async def upload_document(
    bot_id: str,
    file: UploadFile = File(...),
    user_id: str = "demo_user"
):
    # ✅ validate bot ownership
    bot = db.bots.find_one({
        "bot_id": bot_id,
        "user_id": user_id
    })

    if not bot:
        raise HTTPException(status_code=403, detail="Bot not found")

    # extract + process document
    text = load_document(file)
    doc_name = generate_doc_name(text)
    doc_id = str(uuid.uuid4())

    chunks = chunk_text(text)
    embeddings = embed_text(chunks)

    collection_name = f"{user_id}_{bot_id}_{doc_name.replace(' ', '_').lower()}"

    # store document metadata
    db.documents.insert_one({
        "doc_id": doc_id,
        "bot_id": bot_id,
        "user_id": user_id,
        "doc_name": doc_name,
        "collection_name": collection_name
    })

    collection = db[collection_name]

    for i, chunk in enumerate(chunks):
        collection.insert_one({
            "doc_id": doc_id,
            "chunk_id": i,
            "content": chunk,
            "embedding": embeddings[i].tolist()
        })

    return {
        "doc_id": doc_id,
        "doc_name": doc_name,
        "bot_id": bot_id
    }


# =========================================================
# 💬 ASK QUESTION TO A BOT
# =========================================================

@app.post("/bots/{bot_id}/ask")
def ask_bot(
    bot_id: str,
    question: str,
    user_id: str = "demo_user"
):
    # validate bot ownership
    bot = db.bots.find_one({
        "bot_id": bot_id,
        "user_id": user_id
    })

    if not bot:
        raise HTTPException(status_code=403, detail="Bot not found")

    # get all documents linked to this bot
    docs = list(db.documents.find({
        "bot_id": bot_id,
        "user_id": user_id
    }))

    if not docs:
        return {
            "answer": "No documents uploaded for this bot yet."
        }

    question_embedding = embed_text([question])[0]
    scored_chunks = []

    for doc in docs:
        collection = db[doc["collection_name"]]
        for c in collection.find():
            score = np.dot(question_embedding, c["embedding"])
            scored_chunks.append((score, c["content"]))

    if not scored_chunks:
        return {
            "answer": "The uploaded documents do not contain this information."
        }

    top_chunks = sorted(scored_chunks, reverse=True)[:3]
    context = "\n".join([c[1] for c in top_chunks])

    answer = answer_question(context, question)
    return {"answer": answer}
