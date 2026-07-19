from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database.postgresql import create_tables
from backend.routers import employees, projects, allocations, dashboard, rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()  # Create PostgreSQL tables if they don't exist
    yield


app = FastAPI(
    title="AI Resource Management API",
    description="RAG-powered resource allocation & bench management backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(projects.router)
app.include_router(allocations.router)
app.include_router(dashboard.router)
app.include_router(rag.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "AI Resource Management API is running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
