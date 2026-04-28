import hashlib
import logging
import smtplib
from email.message import EmailMessage
from urllib.parse import quote

from app.config import settings

logger = logging.getLogger(__name__)


def hash_token_verificacao(token_em_texto: str) -> str:
    return hashlib.sha256(token_em_texto.encode("utf-8")).hexdigest()


def _montar_url_verificacao(token: str) -> str:
    base = settings.app_public_url.rstrip("/")
    return f"{base}/verificar-email?token={quote(token, safe='')}"


def enviar_email_verificacao(destinatario: str, nome: str, token: str) -> None:
    """Envia o e-mail com o link de confirmação. Se SMTP não estiver configurado, regista aviso (e opcionalmente o link em dev)."""
    url = _montar_url_verificacao(token)
    if not settings.smtp_host:
        msg = (
            "SMTP não configurado: defina SMTP_HOST (e credenciais) no ambiente. "
            "E-mail de verificação não enviado."
        )
        if settings.log_link_verificacao_se_sem_smtp:
            logger.warning("%s Link de teste: %s", msg, url)
        else:
            logger.warning("%s", msg)
        return

    remetente = settings.smtp_from or settings.smtp_user
    if not remetente:
        raise OSError("Defina SMTP_FROM ou SMTP_USER para enviar e-mail.")

    assunto = "Confirme seu e-mail — EquiVoz"
    texto = (
        f"Olá, {nome.strip() or 'visitante'}.\n\n"
        "Para ativar sua conta no EquiVoz, abra o link abaixo (válido por "
        f"{settings.verificacao_email_horas} horas):\n\n{url}\n\n"
        "Se você não se cadastrou, ignore este e-mail.\n"
    )
    html = (
        f"<p>Olá, {nome.strip() or 'visitante'}.</p>"
        "<p>Para <strong>ativar sua conta</strong> no EquiVoz, clique no link abaixo "
        f"(válido por {settings.verificacao_email_horas} horas):</p>"
        f'<p><a href="{url}">Confirmar e-mail</a></p>'
        f"<p>Ou copie: {url}</p>"
        "<p>Se você não se cadastrou, ignore este e-mail.</p>"
    )

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario
    msg.set_content(texto)
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_user and settings.smtp_password:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
    except OSError as e:
        logger.exception("Falha ao enviar e-mail de verificação: %s", e)
        raise
