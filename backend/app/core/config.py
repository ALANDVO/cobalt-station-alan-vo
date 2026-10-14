from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "development"
    debug: bool = True
    frontend_url: str = "http://localhost:5173"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/voicestudio.db"

    # TTS
    tts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    tts_device: str = "cpu"
    tts_cache_dir: Path = Path("./models/tts")

    # LLM (optional)
    llm_api_key: str = ""
    llm_provider: str = "openai-compatible"
    llm_model: str = ""
    llm_base_url: str = ""

    # Keycloak / OIDC
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "voicestudio"
    keycloak_client_id: str = "voicestudio-frontend"
    keycloak_client_secret: str = ""
    oidc_issuer: str = "http://localhost:8080/realms/voicestudio"

    # Security
    secret_key: str = "change-me-in-production-use-secure-random-32-bytes"
    access_token_expire_minutes: int = 30

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def cors_origins(self) -> list[str]:
        return [self.frontend_url]


settings = Settings()