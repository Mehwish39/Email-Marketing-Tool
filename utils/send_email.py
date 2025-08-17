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

def send_emails(subject: str, body: str, recipients: list[str]) -> int:
    count = 0
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, APP_PASSWORD)
        for to in recipients:
            smtp.send_message(_make_msg(to, subject, body))
            count += 1
    return count

def send_from_csv_source(subject: str, body: str, source: Any) -> int:
    recipients = read_emails(source)
    if not recipients:
        return 0
    return send_emails(subject, body, recipients)
