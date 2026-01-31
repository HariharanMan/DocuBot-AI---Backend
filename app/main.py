from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- DB ---
from app.db import db

# --- Routers ---
from app.auth.routes import router as auth_router
from app.bots.routes import router as bots_router


app = FastAPI(title="DocuBot AI – Multi User RAG")

# =======================================
# 🌐 CORS (Frontend Access)
# =======================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =======================================
# 🔗 Router Registration
# =======================================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(bots_router)   # already has prefix="/bots"


# =======================================
# 🏠 Health Check
# =======================================
@app.get("/")
def home():
    return {"status": "DocuBot API running"}
