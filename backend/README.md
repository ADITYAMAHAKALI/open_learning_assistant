# open_learning_assistant – Backend

Backend for **open_learning_assistant** – an open source learning assistant that helps students learn complex topics from their own PDFs/TXT files using Language Models, prerequisite graphs, and gamified questions.

This repo contains:

- A **FastAPI** backend (`app/main.py`)
- A **service / service_impl** architecture for business logic
- Integration hooks for:
  - **OpenSearch** as a vector store
  - **Ollama** (local) or **Gemini** as LLM providers
  - **Postgres** as the relational database
  - **Local filesystem storage** for uploaded materials

> ⚠️ Status: Early skeleton. Some pieces are intentionally stubbed (RAG search, ingestion embeddings, real auth).

---

## Architecture (Backend)

Key concepts:

- `api/v1/routes/*` – HTTP routes (FastAPI routers)
- `services/*` – abstract service interfaces
- `services_impl/*` – concrete implementations (service-serviceimpl pattern)
- `adapters/*` – integration adapters (LLM, vector store, storage)
- `db/*` – SQLAlchemy models + session
- `workers/ingestion_worker.py` – ingestion pipeline skeleton

Rough data flow for MVP:

1. Student uploads a PDF → `/api/v1/materials/upload`
2. Backend stores file via `ObjectStorage` and creates a `learning_materials` row
3. Ingestion worker (later) will:
   - Parse PDF → text
   - Chunk text
   - Embed chunks
   - Index into OpenSearch
4. Student asks questions → `/api/v1/learning/ask`
   - RAG service retrieves relevant chunks (OpenSearch)
   - LLM generates an answer + follow-up questions

### Learning sessions & prerequisite graphs

The backend can orchestrate a structured learning session that combines multiple
uploaded materials.

- `POST /api/v1/learning/sessions` – create a multi-material session, trigger
  prerequisite discovery via the configured LLM provider, and enrich topics with
  Wikipedia summaries.
- `GET /api/v1/learning/sessions` – list prior sessions for the authenticated
  learner.
- `GET /api/v1/learning/sessions/{id}` – fetch the full prerequisite tree for a
  specific session.

---

## Tech Stack

- **Language / Framework**
  - Python 3.11
  - FastAPI
  - Uvicorn

- **Database**
  - Postgres
  - SQLAlchemy ORM

- **Vector Store**
  - OpenSearch with `knn_vector` fields

- **LLMs**
  - Ollama (default)
  - Gemini (via `google-genai`)

- **Other**
  - PyMuPDF (`fitz`) for PDF parsing
  - Docker + docker-compose

---

## Getting Started

### 1. Clone & create your `.env`

```bash
cd backend
cp .env.example .env
