from fastapi import UploadFile, File, HTTPException, Depends
import uuid

from app.db import db
from app.auth.jwt import get_current_user
from app.services.loader import load_document
from app.services.namer import generate_doc_name
from app.services.chunker import chunk_text
from app.services.embedder import embed_text


def list_documents_service(bot_id: str, user=Depends(get_current_user)):
    docs = list(
        db.documents.find(
            {
                "bot_id": bot_id,
                "user_id": user["user_id"]
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


async def upload_document_service(
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

    return {"doc_id": doc_id, "doc_name": doc_name}
