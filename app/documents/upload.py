from fastapi import APIRouter, UploadFile
from app.db import db
from app.services.loader import load_document
from app.services.chunker import chunk_text
from app.services.embedder import embed_text
import uuid

router = APIRouter(prefix="/documents")

@router.post("/upload")
async def upload(file: UploadFile, user_id: str):
    text = load_document(file)
    chunks = chunk_text(text)
    embeddings = embed_text(chunks)

    doc_id = str(uuid.uuid4())
    collection_name = f"{user_id}_{file.filename.replace('.', '_')}"

    db.documents.insert_one({
        "doc_id": doc_id,
        "user_id": user_id,
        "doc_name": file.filename,
        "collection": collection_name
    })

    collection = db[collection_name]

    for i, chunk in enumerate(chunks):
        collection.insert_one({
            "chunk_id": i,
            "content": chunk,
            "embedding": embeddings[i].tolist()
        })

    return {"doc_id": doc_id, "collection": collection_name}
