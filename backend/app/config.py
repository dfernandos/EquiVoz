from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./equivoz.db"
    secret_key: str = "change-me-in-production-use-env-var"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    # URL pública do front (link “esqueci a senha” no e-mail, sem barra no fim)
    app_public_url: str = "http://localhost:5173"
    # SMTP opcional — redefinição de senha por e-mail; vazio = não envia (ver log abaixo)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True
    password_reset_token_horas: int = 1
    # Só em dev: registar no log a URL de redefinição se não houver SMTP
    log_password_reset_link_sem_smtp: bool = False
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
