import logging
import smtplib
from email.message import EmailMessage
from smtplib import SMTPAuthenticationError, SMTPException

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

    smtp_pwd = (settings.smtp_password or "").strip()
    if not smtp_pwd:
        _log.error("SMTP_PASSWORD vazio: configure a chave SMTP do Brevo (não a palavra-passe da conta).")
        raise ValueError("SMTP_PASSWORD não está definida")

    u = (settings.smtp_user or "").strip()
    if not u:
        _log.error("SMTP_USER em falta.")
        raise ValueError("SMTP_USER não está definida")

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
            "SMTP falhou na autenticação. No Brevo use a chave da aba *SMTP* (MTP e API → SMTP), "
            "não outra chave. detalhe: %s",
            e,
        )
        raise
    except SMTPException as e:
        _log.error("Falha SMTP: %s", e)
        raise
    _log.info("E-mail de redefinição de senha enviado para %s (remetente: %s)", to, from_addr)
