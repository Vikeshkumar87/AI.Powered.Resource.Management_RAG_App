# Backend README

This document covers backend setup, run commands, and API usage.

## Backend Code Location

Backend implementation is now contained under `backend/`:

- `backend/app/main.py`: FastAPI app initialization and route mounting
- `backend/app/routes/`: API route modules (`resources`, `projects`, `allocations`, `rag`, `dashboard`, `admin`)
- `backend/app/models/`: SQLAlchemy ORM models
- `backend/app/services/`: Vector store and RAG service integration
- `backend/app/database.py`: DB session and table setup
- `backend/run.py`: Main startup script
- `backend/requirements.txt`: Backend Python dependencies
- `backend/tests/`: Backend test suite

## Prerequisites

- Python 3.10+
- Virtual environment recommended (`.venv`)

## Backend Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

## Environment Configuration

Copy and edit environment config:

```powershell
copy .env.example .env
```

Required key values for local Ollama usage:

- `LLM_PROVIDER=ollama`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=llama3.2`

## Run Backend

```powershell
# From repository root
.\.venv\Scripts\python.exe backend\run.py
```

Backend endpoints:

- App root: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health: `http://127.0.0.1:8000/api/v1/admin/health`

## Seed Sample Data

```powershell
Invoke-WebRequest -UseBasicParsing -Uri http://127.0.0.1:8000/api/v1/admin/seed -Method Post | Select-Object -ExpandProperty Content
```

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -v
```

## Verify Ollama Through Backend

```powershell
$body = @{ question = 'Who are the Python developers currently on bench?'; filter_bench = $true; n_context_docs = 5 } | ConvertTo-Json
Invoke-WebRequest -UseBasicParsing -Uri http://127.0.0.1:8000/api/v1/rag/query -Method Post -ContentType 'application/json' -Body $body | Select-Object -ExpandProperty Content
```

## Phase Validation Endpoints

Use these endpoints to validate the staged data/AI pipeline:

- Phase 1: `POST /api/v1/admin/phase1/prepare-data`
- Phase 2: `POST /api/v1/admin/phase2/build-rag`
- Phase 3: `POST /api/v1/admin/phase3/retrieve`
- Phase 4: `POST /api/v1/admin/phase4/recommend`
- Phase 5: `GET /api/v1/admin/phase5/dashboard`

Example Phase 3 request:

```powershell
$body = @{ staffing_request = 'Need a Python FastAPI backend developer with high availability'; top_k = 5; min_availability = 50; max_utilization = 50 } | ConvertTo-Json
Invoke-WebRequest -UseBasicParsing -Uri http://127.0.0.1:8000/api/v1/admin/phase3/retrieve -Method Post -ContentType 'application/json' -Body $body | Select-Object -ExpandProperty Content
```
