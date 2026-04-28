import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

_log = logging.getLogger(__name__)


def send_password_reset_email(to: str, user_name: str, reset_url: str) -> None:
    host = (settings.smtp_host or "").strip()
    if not host:
        if settings.log_password_reset_link_sem_smtp:
            _log.warning("Redefinir senha (SMTP desligado). URL: %s", reset_url)
        return

    from_addr = (settings.smtp_from or settings.smtp_user or "").strip()
    if not from_addr:
        _log.error("smtp_from / smtp_user em falta; não é possível enviar e-mail.")
        return

    msg = EmailMessage()
    msg["Subject"] = "EquiVoz — redefinir senha"
    msg["From"] = from_addr
    msg["To"] = to
    msg.set_content(
        f"Olá, {user_name}.\n\n"
        f"Para criar uma nova senha, abra o link (válido por cerca de {settings.password_reset_token_horas} hora(s)):\n\n"
        f"{reset_url}\n\n"
        "Se não pediu isso, ignore este e-mail.\n"
    )

    with smtplib.SMTP(host, int(settings.smtp_port)) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        u, p = settings.smtp_user, settings.smtp_password
        if u and p is not None:
            smtp.login(u, p)
        smtp.send_message(msg)
