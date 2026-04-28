import json
import logging
import smtplib
import urllib.error
import urllib.request
from datetime import datetime
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
    subject: str,
) -> None:
    """Envio transacional via API REST (chave xkeysib- no painel Brevo)."""
    payload = {
        "sender": {"name": "EquiVoz", "email": from_email},
        "to": [{"email": to, "name": (user_name or "").strip() or "Usuário"}],
        "subject": subject,
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
    _log.info("E-mail (Brevo API) enviado para %s (assunto: %s)", to, subject)


def _enviar_texto_brevo_ou_smtp(
    to: str,
    user_name: str,
    subject: str,
    text_body: str,
) -> bool:
    """
    Tenta enviar e-mail transacional. Retorna True se enviou.
    Retorna False se não houver Brevo nem SMTP (sem exceção).
    Pode lançar em falha de autenticação ou rede quando a configuração existe.
    """
    from_addr = (settings.smtp_from or settings.smtp_user or "").strip()
    api_key = (settings.brevo_api_key or "").strip()
    if api_key:
        if not from_addr:
            _log.error("Defina SMTP_FROM (e-mail remetente verificado no Brevo).")
            raise ValueError("SMTP_FROM não definido")
        _send_via_brevo_api(to, user_name, from_addr, text_body, api_key, subject)
        return True

    host = (settings.smtp_host or "").strip()
    if not host:
        return False

    if not from_addr:
        _log.error("smtp_from / smtp_user não definidos; não é possível enviar e-mail.")
        raise ValueError("SMTP_FROM não definido")

    smtp_pwd = (settings.smtp_password or "").strip()
    if not smtp_pwd:
        _log.error("SMTP_PASSWORD vazio: use BREVO_API_KEY ou a chave SMTP do Brevo.")
        raise ValueError("SMTP_PASSWORD não definida")

    u = (settings.smtp_user or "").strip()
    if not u:
        _log.error("SMTP_USER não definido.")
        raise ValueError("SMTP_USER não definido")

    msg = EmailMessage()
    msg["Subject"] = subject
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
    _log.info("E-mail (SMTP) enviado para %s (assunto: %s)", to, subject)
    return True


def send_password_reset_email(to: str, user_name: str, reset_url: str) -> None:
    text_body = _body_text(user_name, reset_url)
    sent = _enviar_texto_brevo_ou_smtp(to, user_name, "EquiVoz — redefinir senha", text_body)
    if not sent and settings.log_password_reset_link_sem_smtp:
        _log.warning("Redefinir senha (sem Brevo API nem SMTP). URL: %s", reset_url)


def _resumo_texto(s: str, max_len: int = 800) -> str:
    t = (s or "").strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def _formatar_ocorrencia_br(occ: datetime | None) -> str:
    if occ is None:
        return "não informada"
    try:
        return occ.strftime("%d/%m/%Y às %H:%M")
    except (TypeError, ValueError):
        return str(occ)


def send_denuncia_cadastro_confirmacao(
    destinatario_email: str,
    nome_usuario: str,
    denuncia_id: int,
    titulo: str,
    tipo_violacao_exibicao: str,
    empresa: str | None,
    ocorrido_em: datetime | None,
    local_texto: str | None,
    descricao: str,
) -> None:
    """
    E-mail de confirmação após o usuário registrar uma denúncia (pt-BR).
    Falha de envio não interrompe o fluxo: quem chama trata com try/except.
    """
    emp = (empresa or "").strip() or "não informada"
    loc = (local_texto or "").strip() or "não informada"
    corpo = (
        f"Olá, {nome_usuario.strip()},\n\n"
        "O EquiVoz registrou a sua ocorrência com sucesso. Seguem os dados para a sua confirmação "
        f"(número de referência: {denuncia_id}):\n\n"
        f"Título: {titulo}\n"
        f"Tipo de violação: {tipo_violacao_exibicao}\n"
        f"Estabelecimento / empresa: {emp}\n"
        f"Data e hora da ocorrência: {_formatar_ocorrencia_br(ocorrido_em)}\n"
        f"Local (texto livre): {loc}\n\n"
        "Resumo do relato:\n"
        f"{_resumo_texto(descricao)}\n\n"
        "O EquiVoz organiza relatos para visibilidade e análise agregada. "
        "Este e-mail é apenas confirmação de cadastro no sistema; não substitui protocolo em órgãos "
        "competentes, quando for o caso.\n\n"
        "EquiVoz\n"
    )
    try:
        ok = _enviar_texto_brevo_ou_smtp(
            destinatario_email,
            nome_usuario,
            "EquiVoz — confirmação de denúncia",
            corpo,
        )
        if not ok:
            _log.info("Confirmação de denúncia por e-mail não enviada (Brevo e SMTP desligados).")
    except Exception as e:
        _log.warning("Não foi possível enviar confirmação de denúncia por e-mail: %s", e)
