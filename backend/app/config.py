from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./equivoz.db"
    secret_key: str = "change-me-in-production-use-env-var"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    # Base URL do front (links no e-mail de confirmação, sem barra no fim)
    app_public_url: str = "http://localhost:5173"
    # SMTP — se SMTP_HOST estiver vazio, o e-mail de verificação não é enviado (só use em dev com cuidado)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True
    verificacao_email_horas: int = 48
    # Só em desenvolvimento: imprime o link de verificação se SMTP não estiver definido
    log_link_verificacao_se_sem_smtp: bool = False

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
