from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/resource_management"
    sync_database_url: str = "postgresql://postgres:password@localhost:5432/resource_management"
    openai_api_key: str = ""
    backend_url: str = "http://localhost:8000"
    faiss_index_path: str = "./faiss_store/employee_index"

    class Config:
        env_file = ".env"


settings = Settings()
