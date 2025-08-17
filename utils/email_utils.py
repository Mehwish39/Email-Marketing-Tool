import os, re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GOOGLE_API_KEY = (os.getenv("GOOGLE_API_KEY") or "").strip()
if not GOOGLE_API_KEY:
    raise RuntimeError("Set GOOGLE_API_KEY in .env")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_email(prompt_text: str) -> tuple[str, str]:
    """
    Return a subject and body generated from the user prompt.
    We ask the model to format output with SUBJECT: and BODY: so parsing is easy.
    """
    instructions = f"""
Create a marketing email from this prompt:
{prompt_text}

Rules:
- Output must contain exactly two labeled parts:
  SUBJECT: <concise, title case, 45-65 chars, no spammy words>
  BODY: <120-160 words, warm, professional, no placeholders, no links>
- Greeting may be generic but professional.
- Salutations at the end.
"""
    resp = model.generate_content(instructions)
    text = (getattr(resp, "text", "") or "").strip()

    # Parse SUBJECT and BODY
    m_subj = re.search(r"^SUBJECT:\s*(.+)$", text, flags=re.I | re.M)
    m_body = re.search(r"BODY:\s*(.*)\Z", text, flags=re.I | re.S)
    subject = (m_subj.group(1).strip() if m_subj else "").strip()
    body = (m_body.group(1).strip() if m_body else "").strip()

    # Fallbacks if model response is not perfectly formatted
    if not subject:
        first = text.splitlines()[0] if text else "Your Product Update"
        subject = first[:65].strip()
    if not body:
        body = text

    return subject, body
