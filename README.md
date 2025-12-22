# 🤖 DocuBot AI

**DocuBot AI** is a **multi-user, multi-bot Retrieval-Augmented Generation (RAG) platform** that allows users to create personalized AI chatbots grounded strictly in their own documents. Each user can create multiple bots, upload documents to each bot, and chat with them securely — with responses generated **only from the uploaded content**.

> ❌ No hallucinations
> ✅ Strict document-based answers
> 🔐 Secure, user-isolated bots

---

## 🚀 Features

### 🔐 Authentication & User Isolation

* User **signup and login** with JWT-based authentication
* Each user can access **only their own bots and documents**

### 🤖 Multi-Bot Architecture

* Create **multiple RAG bots per user**
* Each bot maintains its **own knowledge base**
* Example:

  * *Internship Bot*
  * *Resume Bot*
  * *Project Notes Bot*

### 📄 Document Ingestion

* Upload documents in:

  * PDF
  * DOCX
  * TXT
* Automatic:

  * Text extraction
  * Chunking
  * Embedding generation
* Each document creates a **dedicated MongoDB collection**

### 🧠 Retrieval-Augmented Generation (RAG)

* Documents are split into overlapping chunks
* Chunks are converted into vector embeddings
* User queries are embedded and matched using **semantic similarity**
* Only the **most relevant chunks** are passed to the LLM

### 🚫 Strict Context Control

* The AI **cannot answer outside uploaded documents**
* If information is missing, the bot responds gracefully:

  > *“The uploaded documents do not contain this information.”*

### 🗄️ Persistent Storage

* MongoDB stores:

  * Users
  * Bots
  * Documents metadata
  * Chunks and embeddings
* Data persists across server restarts

### 🧪 API Testing with Swagger

* Fully testable via Swagger UI
  👉 `http://localhost:8000/docs`

---

## 🛠️ Tech Stack

### Backend

* **FastAPI** – REST API framework
* **Uvicorn** – ASGI server
* **MongoDB** – Persistent storage
* **PyMongo** – MongoDB client

### AI & NLP

* **Sentence Transformers** – Text embeddings
* **FAISS (CPU)** – Vector similarity (optional)
* **Google Gemini API** – Language model
* **RAG (Retrieval-Augmented Generation)** architecture

### Security

* **JWT (python-jose)** – Authentication
* **Passlib + bcrypt** – Secure password hashing

---

## 📁 Project Structure

```
backend/
│
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── db.py                  # MongoDB connection
│   │
│   ├── auth/                  # Authentication
│   │   ├── routes.py
│   │   ├── jwt.py
│   │   └── password.py
│   │
│   ├── services/              # Core RAG logic
│   │   ├── loader.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── namer.py
│   │   └── qa.py
│   │
│   └── bots/                  # Bot management
│       └── routes.py
│
├── requirements.txt
├── .env
└── .gitignore
```

---

## 🔄 Application Flow

1. User signs up / logs in
2. User creates one or more **bots**
3. Documents are uploaded **to a specific bot**
4. Documents are:

   * Chunked
   * Embedded
   * Stored in MongoDB
5. User chats with a selected bot
6. Bot retrieves relevant chunks and generates an answer

---

## 🧪 API Endpoints (Overview)

### 🔐 Authentication

* `POST /auth/signup`
* `POST /auth/login`

### 🤖 Bots

* `POST /bots/create`
* `GET /bots`

### 📄 Documents

* `POST /bots/{bot_id}/upload`

### 💬 Chat

* `POST /bots/{bot_id}/ask`

---

## ▶️ Running the Project Locally

### 1️⃣ Create virtual environment

```bash
python -m venv rag_venv
rag_venv\Scripts\activate   # Windows
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set environment variables (`.env`)

```env
GEMINI_API_KEY=your_api_key_here
MONGO_URL=mongodb://localhost:27017
```

### 4️⃣ Start the server

```bash
python -m uvicorn app.main:app --reload
```

### 5️⃣ Open Swagger

```
http://localhost:8000/docs
```

---

## 🎯 Why DocuBot AI?

DocuBot AI is designed with **real-world AI product architecture** in mind:

* Multi-tenant user isolation
* Scalable RAG design
* Secure authentication
* Clean service separation
* Production-ready backend patterns

This makes it ideal for:

* AI SaaS products
* Enterprise knowledge assistants
* Document intelligence platforms
* Resume and interview demonstrations

---

## 🔮 Future Enhancements

* JWT middleware with Swagger Authorize button
* Role-based access (teams, orgs)
* Frontend (React) chat UI
* Streaming responses
* Vector DB integration (Chroma / Pinecone)
* Docker & cloud deployment

---

## 📌 Author

**Hariharan M V**
Software Developer | AI & Full-Stack Enthusiast
