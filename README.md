<<<<<<< HEAD
# Backend (from repo root)
python run.py          # → http://localhost:8000

# Frontend dev server (optional, separate terminal)
cd frontend-react
npm run dev            # → http://localhost:5173

# 1. Go to repo root (NOT \backend)
cd C:\Users\vikesh.naipal\Desktop\Projects\Capstone_Project\AI.Powered.Resource.Management_RAG_App

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up .env
copy .env.example .env

# 4. Run the backend
python run.py
=======
# AI-Powered Resource Allocation & Bench Management — RAG Application

An intelligent, full-stack application for managing employee resources, project allocations, and bench management using **Retrieval-Augmented Generation (RAG)** technology.

## Features

| Feature | Description |
|---|---|
| 🧑‍💼 **Resource Management** | Full CRUD for employees with skills, experience, availability tracking |
| 📋 **Project Management** | Manage projects with requirements, priorities and team allocations |
| 🪑 **Bench Management** | Monitor unallocated resources with bench-aging reports |
| 🔄 **Allocation Engine** | Allocate/deallocate resources to projects with availability enforcement |
| 🤖 **Semantic Search** | Vector-based search across resources and projects using sentence-transformers |
| 💬 **RAG Queries** | Natural language Q&A powered by LLM + vector retrieval |
| 💡 **AI Recommendations** | Intelligent resource matching for project requirements |
| 📊 **Analytics Dashboard** | Stats, project gaps, bench aging, department breakdown |
| 🌐 **Web UI** | React frontend (built and served by FastAPI) + legacy HTML/JS frontend |

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy (SQLite by default)
- **Vector Store**: ChromaDB with sentence-transformers embeddings
- **RAG Pipeline**: Configurable LLM (OpenAI, Ollama, or Demo mode — no LangChain dependency)
- **Frontend (React)**: React 19 + Vite (built into `frontend-react/dist/`, served by FastAPI)
- **Frontend (Legacy)**: Plain HTML/CSS/JS in `frontend/` (served by FastAPI as fallback)

---

## Quick Start

### Prerequisites

- **Python 3.10+** — Download from [python.org](https://python.org/downloads/)
  - ⚠️ Windows: During install, check **"Add Python to PATH"**
  - ⚠️ Windows: If `python` opens the Microsoft Store, go to **Settings → Apps → Advanced app settings → App execution aliases** and disable the `python.exe` alias
- **Node.js 18+** — Download from [nodejs.org](https://nodejs.org/)

### Step 1 — Clone & navigate to the repo root

```bash
# Make sure you're at the REPO ROOT, not a subfolder like \backend
cd AI.Powered.Resource.Management_RAG_App
```

### Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Windows users:** If `pip` is not found, use `py -m pip install -r requirements.txt`

### Step 3 — Build the React frontend

```bash
cd frontend-react
npm install
npm run build
cd ..
```

### Step 4 — Configure environment

```bash
# macOS / Linux
cp .env.example .env

# Windows PowerShell
copy .env.example .env
```

Edit `.env` if needed (the defaults work for demo mode out of the box).

### Step 5 — Start the server

```bash
python run.py
# or
uvicorn app.main:app --reload --port 8000
```

> **Windows users:** If `python` is not found, use `py run.py`

### Step 6 — Seed sample data

```bash
curl -X POST http://localhost:8000/api/v1/admin/seed
```

Or click **"Seed Sample Data"** in the Dashboard UI.

### Step 7 — Open the app

| URL | What |
|---|---|
| **http://localhost:8000** | Full web application |
| **http://localhost:8000/docs** | Interactive Swagger API docs |
| **http://localhost:8000/redoc** | ReDoc API documentation |
| **http://localhost:8000/api/v1/admin/health** | System health check |

---

## Frontend Development Mode

Run the React frontend with hot-reload alongside the backend:

```bash
# Terminal 1 — start backend
python run.py

# Terminal 2 — start Vite dev server
cd frontend-react
npm run dev
# Opens at http://localhost:5173
# API calls to /api/* are automatically proxied to http://localhost:8000
```

---

## Configuration

All settings are controlled via environment variables (`.env` file):

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./resource_management.db` | Database connection URL |
| `LLM_PROVIDER` | `demo` | LLM backend: `demo`, `openai`, or `ollama` |
| `OPENAI_API_KEY` | — | Required if `LLM_PROVIDER=openai` |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model to use |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama2` | Ollama model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model for embeddings |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage directory |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug/reload mode |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### LLM Provider Modes

- **`demo`** (default): No LLM required. Returns formatted context from vector search. Perfect for development and testing.
- **`openai`**: Uses OpenAI ChatGPT for intelligent analysis. Set `OPENAI_API_KEY` in `.env`.
- **`ollama`**: Uses a local Ollama instance. [Install Ollama](https://ollama.ai), then run `ollama pull llama2`.

---

## API Reference

### Resources — `/api/v1/resources`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List all resources (supports filters: `department`, `skill`, `is_on_bench`, `location`, `min_experience`) |
| `POST` | `/` | Create a new resource/employee |
| `GET` | `/{id}` | Get resource by ID |
| `PUT` | `/{id}` | Update resource |
| `DELETE` | `/{id}` | Delete resource |
| `GET` | `/bench` | Get bench (unallocated) resources |
| `POST` | `/{id}/allocate` | Allocate resource to a project |
| `POST` | `/{id}/release` | Release resource back to bench |

### Projects — `/api/v1/projects`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List all projects (filter by `status`) |
| `POST` | `/` | Create a project |
| `GET` | `/{id}` | Get project details |
| `PUT` | `/{id}` | Update project |
| `DELETE` | `/{id}` | Delete project |
| `GET` | `/{id}/team` | Get allocated team for a project |

### Allocations — `/api/v1/allocations`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List all allocations |
| `POST` | `/` | Create allocation |
| `GET` | `/{id}` | Get allocation details |
| `DELETE` | `/{id}` | End/delete an allocation |

### RAG / AI — `/api/v1/rag`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/query` | Natural language question (RAG) |
| `POST` | `/recommend` | AI-powered resource recommendation |
| `GET` | `/search?q=...` | Semantic search |

### Dashboard — `/api/v1/dashboard`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/stats` | Overall statistics (totals, departments, top skills) |
| `GET` | `/bench-aging` | Bench resources sorted by days on bench |
| `GET` | `/project-gaps` | Projects with unfilled positions |

### Admin — `/api/v1/admin`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/seed` | Seed sample data (15 resources, 6 projects, 6 allocations) |
| `POST` | `/reindex` | Rebuild ChromaDB vector index |
| `GET` | `/health` | System health (DB + vector store + LLM config) |
| `DELETE` | `/clear?confirm=true` | Clear all data from the database |

---

## RAG Query Examples

### Natural Language Query (curl)

```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who are the Python developers currently on bench?",
    "filter_bench": true,
    "n_context_docs": 5
  }'
```

### Resource Recommendations (curl)

```bash
curl -X POST http://localhost:8000/api/v1/rag/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "project_requirements": "6-month FinTech microservices project using Java and Kafka",
    "required_skills": ["Java", "Spring Boot", "Kafka"],
    "team_size": 2
  }'
```

### Semantic Search (curl)

```bash
curl "http://localhost:8000/api/v1/rag/search?q=cloud+architect&bench_only=true&n=5"
```

---

## Running Tests

All 39 tests use an in-memory SQLite database — no `.env` file or external services needed.

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_resources.py -v
python -m pytest tests/test_projects.py -v
python -m pytest tests/test_allocations.py -v
python -m pytest tests/test_dashboard.py -v
```

> **Windows users:** Use `py -m pytest tests/ -v`

---

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI app: lifespan, CORS, route registration, static files
│   ├── config.py            # Pydantic Settings (reads from .env)
│   ├── database.py          # SQLAlchemy engine, session, Base, create_tables()
│   ├── models/
│   │   ├── resource.py      # Resource (employee) SQLAlchemy ORM model
│   │   ├── project.py       # Project ORM model + ProjectStatus enum
│   │   └── allocation.py    # Allocation ORM model (resource ↔ project)
│   ├── routes/
│   │   ├── schemas.py       # Pydantic request/response schemas for Resources
│   │   ├── resources.py     # Resource CRUD + allocate/release endpoints
│   │   ├── projects.py      # Project CRUD + team endpoint
│   │   ├── allocations.py   # Allocation CRUD endpoints
│   │   ├── rag.py           # RAG query, recommend, and semantic search endpoints
│   │   ├── dashboard.py     # Stats, bench-aging, project-gaps analytics
│   │   └── admin.py         # Seed, reindex, health, clear endpoints
│   ├── services/
│   │   ├── vector_store.py  # ChromaDB + sentence-transformers (lazy init, graceful fallback)
│   │   └── rag_service.py   # RAG pipeline: retrieval → context → LLM (OpenAI/Ollama/demo)
│   └── data/
│       └── sample_data.py   # 15 sample resources, 6 projects, 6 allocations
├── frontend-react/          # React 19 + Vite frontend
│   ├── src/                 # React source components
│   ├── dist/                # Built output (served by FastAPI at /)
│   └── package.json
├── frontend/                # Legacy plain HTML/CSS/JS frontend (fallback)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/
│   ├── conftest.py          # In-memory SQLite fixtures, TestClient setup
│   ├── test_resources.py    # 13 resource endpoint tests
│   ├── test_projects.py     # 9 project endpoint tests
│   ├── test_allocations.py  # 8 allocation endpoint tests
│   └── test_dashboard.py    # 9 dashboard/analytics tests
├── run.py                   # uvicorn entry point (reads host/port from settings)
├── requirements.txt         # Python dependencies (minimum version pins)
├── .env.example             # Template for environment configuration
└── README.md
```

---

## How RAG Works

```
User Query
    │
    ▼
[1] Embed query using sentence-transformers (all-MiniLM-L6-v2)
    │
    ▼
[2] ChromaDB semantic search → top-N matching resource/project documents
    │
    ▼
[3] Build context string from retrieved documents
    │
    ▼
[4] Send context + question to LLM (OpenAI / Ollama / demo formatter)
    │
    ▼
[5] Return structured answer with sources and relevance scores
```

- **Indexing**: Resources and projects are embedded via `to_document_string()` on create/update and stored in ChromaDB. Use `/api/v1/admin/reindex` to rebuild.
- **Retrieval**: Cosine similarity search returns the most semantically relevant entries.
- **Generation**: OpenAI or Ollama produces a natural language answer; demo mode formats the raw context.

---

## License

MIT
>>>>>>> 2a1a7caa38d0cbea04ebabb8e7ad1ae87486eaa8
