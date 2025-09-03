from __future__ import annotations
from dotenv import load_dotenv
import os, csv, smtplib
from email.message import EmailMessage
from typing import Any

load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD  = os.getenv("APP_PASSWORD")
if not EMAIL_ADDRESS or not APP_PASSWORD:
    raise RuntimeError("Set EMAIL_ADDRESS and APP_PASSWORD in .env")

def read_emails(source: Any) -> list[str]:
    """Accepts a file path or an uploaded file object (request.files['csv_file'])."""
    rows = []
    if hasattr(source, "stream"):                     # uploaded file
        content = source.stream.read()
        try: source.stream.seek(0)
        except Exception: pass
        if isinstance(content, bytes):
            content = content.decode("utf-8-sig", errors="ignore")
        rows = list(csv.reader(content.splitlines()))
    else:                                             # path
        with open(source, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))

    seen, emails = set(), []
    for row in rows:
        for cell in row:
            cell = (cell or "").strip()
            if cell and "@" in cell and cell not in seen:
                emails.append(cell); seen.add(cell)
    return emails

def _make_msg(to_email: str, subject: str, body: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    return msg

def send_emails(subject: str, body: str, recipients: list[str]):
    """
    Returns:
      [{"to": "a@x.com", "ok": True, "error": None}, {"to": "b@x.com", "ok": False, "error": "smtp error"}]
    """
    results = []
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, APP_PASSWORD)
        for to in recipients:
            try:
                msg = _make_msg(to, subject, body)
                smtp.send_message(msg)
                results.append({"to": to, "ok": True, "error": None})
            except Exception as e:
                results.append({"to": to, "ok": False, "error": str(e)})
    return results

def send_from_csv_source(subject: str, body: str, source: Any) -> int:
    recipients = read_emails(source)
    if not recipients:
        return 0
    return send_emails(subject, body, recipients)
