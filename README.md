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
| 🌐 **Web UI** | Single-page frontend for all features |

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy (SQLite by default)
- **Vector Store**: ChromaDB with sentence-transformers embeddings
- **RAG Pipeline**: Configurable LLM (OpenAI, Ollama, or Demo mode)
- **Frontend**: React 18 + Vite (built and served by FastAPI)

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Build the React Frontend

```bash
cd frontend-react
npm install
npm run build
cd ..
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env as needed (see Configuration section below)
```

### 4. Start the Server

```bash
python run.py
# or
uvicorn app.main:app --reload --port 8000
```

### 5. Seed Sample Data

```bash
curl -X POST http://localhost:8000/api/v1/admin/seed
```

### 6. Open the UI

Visit **http://localhost:8000** in your browser.

Or visit **http://localhost:8000/docs** for the interactive Swagger API documentation.

### Frontend Development

To run the React frontend in development mode with hot-reload:

```bash
# Start the FastAPI backend first
python run.py

# In another terminal, start the Vite dev server
cd frontend-react
npm run dev
# Opens http://localhost:5173 (proxies /api calls to FastAPI on port 8000)
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
| `LOG_LEVEL` | `INFO` | Logging level |

### LLM Provider Modes

- **`demo`** (default): No LLM needed. Returns formatted context from vector search. Great for development/testing.
- **`openai`**: Uses OpenAI ChatGPT for intelligent analysis. Set `OPENAI_API_KEY`.
- **`ollama`**: Uses a local Ollama instance. [Install Ollama](https://ollama.ai) and pull a model first.

---

## API Reference

### Resources

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/resources/` | List all resources (with filters) |
| `POST` | `/api/v1/resources/` | Create a new resource |
| `GET` | `/api/v1/resources/{id}` | Get resource by ID |
| `PUT` | `/api/v1/resources/{id}` | Update resource |
| `DELETE` | `/api/v1/resources/{id}` | Delete resource |
| `GET` | `/api/v1/resources/bench` | Get bench resources |
| `POST` | `/api/v1/resources/{id}/allocate` | Allocate to a project |
| `POST` | `/api/v1/resources/{id}/release` | Release to bench |

### Projects

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/projects/` | List all projects |
| `POST` | `/api/v1/projects/` | Create a project |
| `GET` | `/api/v1/projects/{id}` | Get project details |
| `PUT` | `/api/v1/projects/{id}` | Update project |
| `DELETE` | `/api/v1/projects/{id}` | Delete project |
| `GET` | `/api/v1/projects/{id}/team` | Get allocated team |

### Allocations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/allocations/` | List all allocations |
| `POST` | `/api/v1/allocations/` | Create allocation |
| `GET` | `/api/v1/allocations/{id}` | Get allocation details |
| `DELETE` | `/api/v1/allocations/{id}` | End allocation |

### RAG / AI

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/rag/query` | Natural language query |
| `POST` | `/api/v1/rag/recommend` | Resource recommendation |
| `GET` | `/api/v1/rag/search` | Semantic search |

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/dashboard/stats` | Overall statistics |
| `GET` | `/api/v1/dashboard/bench-aging` | Bench aging report |
| `GET` | `/api/v1/dashboard/project-gaps` | Projects with open positions |

### Admin

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/admin/seed` | Seed sample data |
| `POST` | `/api/v1/admin/reindex` | Rebuild vector index |
| `GET` | `/api/v1/admin/health` | System health check |
| `DELETE` | `/api/v1/admin/clear` | Clear all data |

---

## RAG Query Examples

### Natural Language Queries

```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who are the Python developers currently on bench?",
    "filter_bench": true
  }'
```

### Resource Recommendations

```bash
curl -X POST http://localhost:8000/api/v1/rag/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "project_requirements": "6-month FinTech microservices project using Java and Kafka",
    "required_skills": ["Java", "Spring Boot", "Kafka"],
    "team_size": 2
  }'
```

---

## Running Tests

```bash
# Install test dependencies (included in requirements.txt)
pip install pytest pytest-asyncio httpx

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_resources.py -v
```

---

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Settings and configuration
│   ├── database.py          # Database setup and session management
│   ├── models/
│   │   ├── resource.py      # Resource/Employee SQLAlchemy model
│   │   ├── project.py       # Project SQLAlchemy model
│   │   └── allocation.py    # Allocation SQLAlchemy model
│   ├── routes/
│   │   ├── resources.py     # Resource CRUD API routes
│   │   ├── projects.py      # Project CRUD API routes
│   │   ├── allocations.py   # Allocation API routes
│   │   ├── rag.py           # RAG query & recommendation routes
│   │   ├── dashboard.py     # Analytics & dashboard routes
│   │   ├── admin.py         # Admin routes (seed, reindex, health)
│   │   └── schemas.py       # Shared Pydantic schemas
│   ├── services/
│   │   ├── vector_store.py  # ChromaDB vector store service
│   │   └── rag_service.py   # RAG pipeline (retrieval + generation)
│   └── data/
│       └── sample_data.py   # 15 resources, 6 projects, 6 allocations
├── frontend/
│   ├── index.html           # Single-page web application
│   ├── style.css            # UI styles
│   └── app.js               # Frontend JavaScript
├── tests/
│   ├── conftest.py          # Test fixtures and configuration
│   ├── test_resources.py    # Resource endpoint tests
│   ├── test_projects.py     # Project endpoint tests
│   ├── test_allocations.py  # Allocation endpoint tests
│   └── test_dashboard.py    # Dashboard endpoint tests
├── run.py                   # Application runner
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
└── README.md
```

---

## How RAG Works

1. **Indexing**: When resources and projects are created/updated, they are converted to text documents and embedded using `sentence-transformers` (default: `all-MiniLM-L6-v2`). Embeddings are stored in ChromaDB.

2. **Retrieval**: When a user submits a query (e.g., "Python developers on bench"), the query is embedded and semantically similar documents are retrieved from ChromaDB.

3. **Generation**: The retrieved documents form a context window that is sent to the configured LLM (OpenAI/Ollama/Demo) along with the user's question.

4. **Response**: The LLM generates an intelligent, context-aware response explaining which resources match the requirements and why.

---

## License

MIT
