from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Digital Career Twin"
    API_V1_PREFIX: str = "/api"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/career_twin"
    SQLITE_FALLBACK_URL: str = "sqlite:///./career_twin.db"
    DEBUG: bool = True
    APP_ENV: str = "development"
    SECRET_KEY: str = "dev_secret_key_career_twin_2026_super_secure_random"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = Settings()
