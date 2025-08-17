
import os
from uuid import uuid4
from flask import Flask, render_template, request, redirect, url_for, flash, session

from utils.email_utils import generate_email            # must return (subject, body)
from utils.send_email import read_emails, send_emails   # read_emails must accept file-like objects


try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "Techinoid Email Marketing")

# list of recipient emails
INMEM_RECIPIENTS = {}


@app.route("/", methods=["GET", "POST"])
def index():
    """
    GET: show form
    POST action=generate: read recipients from uploaded file in-memory, generate subject+body, show preview
    POST action=send: send to recipients stored in-memory by token, then clear everything
    """
    if request.method == "POST":
        action = request.form.get("action", "generate")

        if action == "send":
            subject = session.get("subject")
            body = session.get("body")
            token = session.get("recipients_token")

            if not subject or not body or not token:
                flash("Nothing to send. Please start again.", "error")
                return redirect(url_for("index"))

            # Get recipients from RAM and remove them to avoid leaks
            recipients = INMEM_RECIPIENTS.pop(token, [])

            if not recipients:
                flash("No recipients found for this session. Please try again.", "error")
                session.clear()
                return redirect(url_for("index"))

            sent = send_emails(subject=subject, body=body, recipients=recipients)

            # Clear the session since we are done
            session.clear()

            # Show confirmation page
            return render_template(
                "result.html",
                subject=subject,
                body=body,
                recipients=recipients,
                sent=sent,
            )

        # action == "generate"
        prompt_text = (request.form.get("prompt") or "").strip()
        uploaded = request.files.get("csv_file")

        if not prompt_text or not uploaded or uploaded.filename == "":
            flash("Please provide a prompt and a CSV file.", "error")
            return redirect(url_for("index"))

        # Generate subject and body from the prompt
        subject, body = generate_email(prompt_text)

        # Read recipients directly from the uploaded file object (no saving)
        recipients = read_emails(uploaded)

        if not recipients:
            flash("No valid email addresses were found in the CSV.", "error")
            return redirect(url_for("index"))

        # Keep recipients only in memory, referenced by a short token
        token = uuid4().hex[:12]
        INMEM_RECIPIENTS[token] = recipients

        # Keep only small items in session
        session["subject"] = subject
        session["body"] = body
        session["recipients_token"] = token

        # Render preview on the same page
        return render_template(
            "index.html",
            preview=True,
            subject=subject,
            body=body,
            recipients=recipients,
        )

    # GET request
    return render_template("index.html", preview=False)


@app.route("/reset")
def reset():
    """Clear any stored data and return to the form."""
    token = session.get("recipients_token")
    if token:
        INMEM_RECIPIENTS.pop(token, None)
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
