from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./equivoz.db"
    secret_key: str = "change-me-in-production-use-env-var"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    # Origens extra para CORS (separadas por vírgula), ex.: o site no Netlify e deploy previews
    # https://equivoz.netlify.app,https://xxxxx--equivoz.netlify.app
    cors_origins: str | None = None

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Aceita `postgres://` e normaliza para `postgresql://` (SQLAlchemy)."""
        s = str(value).strip()
        if s.startswith("postgres://"):
            return "postgresql://" + s[len("postgres://") :]
        return s

    class Config:
        env_file = ".env"


settings = Settings()
