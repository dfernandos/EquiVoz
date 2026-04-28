import json
import logging
import smtplib
import urllib.error
import urllib.request
from email.message import EmailMessage
from smtplib import SMTPAuthenticationError, SMTPException

from app.config import settings

_log = logging.getLogger(__name__)

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"


def _body_text(user_name: str, reset_url: str) -> str:
    return (
        f"Olá, {user_name}.\n\n"
        f"Para criar uma nova senha, abra o link (válido por cerca de {settings.password_reset_token_horas} hora(s)):\n\n"
        f"{reset_url}\n\n"
        "Se não pediu isso, ignore este e-mail.\n"
    )


def _send_via_brevo_api(
    to: str,
    user_name: str,
    from_email: str,
    text_body: str,
    api_key: str,
) -> None:
    """Envio transacional via API REST (a mesma chave xkeysib- do painel, aba *Chaves de API*)."""
    payload = {
        "sender": {"name": "EquiVoz", "email": from_email},
        "to": [{"email": to, "name": (user_name or "").strip() or "Utilizador"}],
        "subject": "EquiVoz — redefinir senha",
        "textContent": text_body,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BREVO_SEND_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "api-key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        _log.error("Brevo API HTTP %s: %s", e.code, err)
        raise
    _log.info("E-mail de redefinição (Brevo API) enviado para %s (remetente: %s)", to, from_email)


def send_password_reset_email(to: str, user_name: str, reset_url: str) -> None:
    text_body = _body_text(user_name, reset_url)
    from_addr = (settings.smtp_from or settings.smtp_user or "").strip()

    api_key = (settings.brevo_api_key or "").strip()
    if api_key:
        if not from_addr:
            _log.error("Defina SMTP_FROM (e-mail remetente verificado no Brevo).")
            raise ValueError("SMTP_FROM em falta")
        _send_via_brevo_api(to, user_name, from_addr, text_body, api_key)
        return

    host = (settings.smtp_host or "").strip()
    if not host:
        if settings.log_password_reset_link_sem_smtp:
            _log.warning("Redefinir senha (sem Brevo API nem SMTP). URL: %s", reset_url)
        return

    if not from_addr:
        _log.error("smtp_from / smtp_user em falta; não é possível enviar e-mail.")
        raise ValueError("SMTP_FROM em falta")

    smtp_pwd = (settings.smtp_password or "").strip()
    if not smtp_pwd:
        _log.error("SMTP_PASSWORD vazio: use BREVO_API_KEY ou a chave SMTP do Brevo.")
        raise ValueError("SMTP_PASSWORD não está definida")

    u = (settings.smtp_user or "").strip()
    if not u:
        _log.error("SMTP_USER em falta.")
        raise ValueError("SMTP_USER não está definida")

    msg = EmailMessage()
    msg["Subject"] = "EquiVoz — redefinir senha"
    msg["From"] = from_addr
    msg["To"] = to
    msg.set_content(text_body)

    try:
        with smtplib.SMTP(host, int(settings.smtp_port), timeout=30) as smtp:
            smtp.ehlo()
            if settings.smtp_use_tls:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(u, smtp_pwd)
            smtp.send_message(msg)
    except SMTPAuthenticationError as e:
        _log.error(
            "SMTP falhou na autenticação. Alternativa: defina BREVO_API_KEY (chave xkeysib) em vez de SMTP. %s",
            e,
        )
        raise
    except SMTPException as e:
        _log.error("Falha SMTP: %s", e)
        raise
    _log.info("E-mail de redefinição (SMTP) enviado para %s (remetente: %s)", to, from_addr)
