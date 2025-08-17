# Email Marketing Web App

A small Flask app that takes a prompt and a CSV of recipient emails, generates a polished subject and body with Gemini, shows a preview for approval, then sends via Gmail SMTP. The CSV is parsed in memory and is not saved to disk.

## Features
- Single page flow with preview and explicit approval
- Subject and body are generated from the prompt
- CSV parsed in memory, duplicates removed
- Sends one email per recipient using Gmail SMTP
- Result page shows what was sent and to whom

## Project structure
```
your-project/
  app.py
  utils/
    __init__.py
    email_utils.py
    send_email.py
  templates/
    index.html
    result.html
  static/
    styles.css
  .env
  requirements.txt
```

## Prerequisites
- Python 3.10 or newer
- Google API key for Gemini (in `.env` as `GOOGLE_API_KEY`)
- Gmail address and App Password
  - Turn on 2FA for the Google account
  - Create an App Password for Mail and use it in `.env`

## Setup

1) Create and activate a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS or Linux
source .venv/bin/activate
```

2) Install packages
```bash
pip install -r requirements.txt
```

3) Create `.env` in the project root
```env
FLASK_SECRET_KEY=replace_with_random_32_chars
GOOGLE_API_KEY=your_google_gemini_api_key
EMAIL_ADDRESS=youraddress@gmail.com
APP_PASSWORD=your_gmail_app_password
```



## How to run
```bash
python app.py
```
Open http://127.0.0.1:5000

### Flow
1. On the index page, type a prompt and upload a CSV.
2. The app generates a subject and body and shows a preview.
3. Click Approve and Send to send emails. Or click Try again to enter a new prompt.
4. The result page lists all recipients and the final content.

### CSV format
- Any CSV that contains email addresses in cells
- Duplicates are removed automatically

