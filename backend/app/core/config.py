"""Application configuration management using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.
    
    Loads from environment variables or .env file.
    Uses Pydantic v2 settings.
    """
    
    # Application
    app_name: str = "ProjectMind"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    workers: int = 4
    reload: bool = False
    
    # Database - PostgreSQL
    database_url: str = "postgresql+asyncpg://projectmind:projectmind@localhost:5432/projectmind"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Database - Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j"
    neo4j_database: str = "neo4j"
    
    # Database - ChromaDB
    chromadb_host: str = "localhost"
    chromadb_port: int = 8001
    chromadb_persistence_dir: str = "/data/chromadb"
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    cors_allow_headers: list[str] = ["*"]
    
    # Logging
    log_format: str = "json"  # json or text
    log_file: str = "/logs/projectmind.log"
    
    # External APIs
    arxiv_api_base: str = "https://api.arxiv.org/v1/query"
    crossref_api_base: str = "https://api.crossref.org"
    semantic_scholar_api_base: str = "https://api.semanticscholar.org/graph/v1"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Cached Settings instance.
    """
    return Settings()
