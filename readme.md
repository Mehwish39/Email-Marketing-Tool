# Email Marketing Web App with AI Email Generation

A small Flask app that takes a prompt and a CSV of recipient emails, generates a subject and body with Gemini, shows a preview for approval, then sends one message per recipient using your configured SMTP. Each recipient is logged in the database. You can review a filterable history page.

## Features
- Login and signup with Flask-Login
- AI Compose, preview, edit, approve, and send
- CSV parsed in memory with a recipient manager
- Sends via a single SMTP account you configure in .env
- Per-recipient logging with status and timestamp
- History page with search, status filter, and date range

## Project structure
your-project/
  app.py
  auth.py
  models.py
  utils/
    __init__.py
    email_utils.py
    send_email.py
  templates/
    index.html
    result.html
    login.html
    signup.html
    history.html
  static/
    styles.css
  .env
  requirements.txt

## Prerequisites
- Python 3.10 or newer
- Google API key for Gemini
- One SMTP sender account for the app to use
  - Gmail works with an App Password

## Setup

1) Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS or Linux
source .venv/bin/activate

2) Install packages
pip install -r requirements.txt

3) Create .env in the project root
Local SQLite by default.
FLASK_SECRET_KEY=replace_with_random_32_chars
GOOGLE_API_KEY=your_gemini_api_key

# SMTP used for all sends
EMAIL_ADDRESS=your_sender@example.com
APP_PASSWORD=your_app_password

# Database
DATABASE_URL=sqlite:///app.db

## Run locally
python app.py
Open http://127.0.0.1:5000

## Flow
1. Sign up or log in.
2. On the index page, enter a prompt and upload a CSV.
3. The app generates a subject and body and shows a preview.
4. Use the recipient manager if needed, then click Approve and Send.
5. The result page lists recipients and the final content.
6. Open /history to filter by recipient, status, and date.

## CSV format
- One column of emails or a column named email
- You can remove entries in the preview before sending

## History page
- Path: /history
- Filters: search text, status sent or failed, start date, end date
- Pagination included
- Each send creates one row per recipient with subject, body, status, and timestamp

## Deploy to Render

Start command
gunicorn -b 0.0.0.0:$PORT app:app

Environment variables
Set in Render -> Environment.
FLASK_SECRET_KEY=...
GOOGLE_API_KEY=...
EMAIL_ADDRESS=...
APP_PASSWORD=...
DATABASE_URL=sqlite:////tmp/app.db            # temp SQLite on Render
# or if you attach a Disk at /var/lib/data:
# DATABASE_URL=sqlite:////var/lib/data/app.db
# or use your Postgres URL and add psycopg2-binary to requirements

Notes for Render
- The repo folder is read-only at runtime. Use /tmp or a mounted Disk for SQLite.
- On first boot the app creates tables automatically.
- For Postgres add to requirements:
  psycopg2-binary==2.9.9

## Troubleshooting
- 502 on Render: open Logs and fix the first error line
- Read-only database: set a writable DATABASE_URL like sqlite:////tmp/app.db
- No such table: restart the app so db.create_all() runs
- Gmail issues: use an App Password with 2FA enabled

## Security notes
- Do not commit .env or app.db
- The app uses a single SMTP account defined in .env
- Consider setting SESSION_COOKIE_SECURE=True, SESSION_COOKIE_HTTPONLY=True, and SESSION_COOKIE_SAMESITE="Lax" in production

## License
MIT