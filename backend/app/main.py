"""
AI-Powered Resource Allocation & Bench Management RAG Application
Main FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import settings
from app.database import create_tables
from app.routes import resources, projects, allocations, rag, dashboard, admin, auth

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting AI Resource Management RAG Application...")
    create_tables()
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(
    title="AI-Powered Resource Allocation & Bench Management",
    description="""
## AI-Powered Resource Allocation & Bench Management with RAG

An intelligent system for managing employee resources, project allocations,
and bench management using Retrieval-Augmented Generation (RAG) technology.

### Key Features:
- 🧑‍💼 **Resource Management**: Track employees with skills, experience, and availability
- 📋 **Project Management**: Manage projects with requirements and team allocations
- 🔄 **Bench Management**: Monitor and manage unallocated resources
- 🤖 **AI-Powered Search**: Semantic search using sentence transformers
- 💬 **RAG Queries**: Natural language queries about resources and recommendations
- 📊 **Dashboard**: Analytics on bench utilization and project gaps

### Quick Start:
1. Visit `/admin/seed` to populate with sample data
2. Use `/rag/query` to ask natural language questions
3. Use `/rag/recommend` to get AI-powered resource recommendations
4. Check `/dashboard/stats` for an overview

### LLM Configuration:
Set `LLM_PROVIDER` in `.env` to:
- `demo` (default): Returns formatted context without an LLM
- `openai`: Uses OpenAI ChatGPT (requires `OPENAI_API_KEY`)
- `ollama`: Uses local Ollama instance (requires Ollama running)
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend.
# backend/app/main.py -> project root is three levels up.
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_react_dist = os.path.join(_project_root, "frontend-react", "dist")

if os.path.exists(_react_dist):
    frontend_dir = _react_dist
    app.mount("/assets", StaticFiles(directory=os.path.join(_react_dist, "assets")), name="assets")
else:
    frontend_dir = None


# Include routers
app.include_router(resources.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(allocations.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    """Root endpoint - serves the React frontend."""
    if frontend_dir:
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {
        "message": "AI-Powered Resource Allocation & Bench Management API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/admin/health",
        "frontend": "Build the React app: cd frontend-react && npm run build",
    }


@app.get("/health", tags=["Root"])
def health():
    """Simple health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}
