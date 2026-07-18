"""
Configuration settings for the AI Resource Management RAG Application.
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
import json
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "AI Resource Management RAG App"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite:///./resource_management.db"

    # Vector Store
    chroma_persist_dir: str = "./chroma_db"
    collection_name: str = "resource_management"

    # LLM Configuration
    llm_provider: str = "demo"  # "openai", "ollama", or "demo"
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # Embedding Model
    embedding_model: str = "all-MiniLM-L6-v2"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

    # Logging
    log_level: str = "INFO"

    model_config = ConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
