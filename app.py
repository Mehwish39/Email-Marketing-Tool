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
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# In-memory store of recipient lists keyed by a short token
INMEM_RECIPIENTS = {}


@app.route("/", methods=["GET", "POST"])
def index():
    """
    GET:
      - If a draft exists in session and recipients are in memory, show the preview with current subject/body.
      - Otherwise show the compose form.
    POST actions:
      - generate: create a draft (subject, body) from prompt, parse CSV to recipients, show editable preview.
      - remove: remove selected recipients from the in-memory list and re-render the preview.
      - send: send the edited or original draft to recipients, then clear state and show result page.
    """
    if request.method == "GET":
        subject = session.get("subject")
        body = session.get("body")
        token = session.get("recipients_token")
        recipients = INMEM_RECIPIENTS.get(token, [])
        if subject and body and recipients:
            return render_template(
                "index.html",
                preview=True,
                subject=subject,
                body=body,
                recipients=recipients,
            )
        return render_template("index.html", preview=False)

    # POST
    action = request.form.get("action", "generate")

    if action == "generate":
        prompt_text = (request.form.get("prompt") or "").strip()
        uploaded = request.files.get("csv_file")

        if not prompt_text or not uploaded or uploaded.filename == "":
            flash("Please provide a prompt and a CSV file.", "error")
            return redirect(url_for("index"))

        # 1) Generate draft from the model
        subject, body = generate_email(prompt_text)

        # 2) Read recipients directly from the uploaded file object (no saving)
        recipients = read_emails(uploaded)
        if not recipients:
            flash("No valid email addresses were found in the CSV.", "error")
            return redirect(url_for("index"))

        # Store recipients in memory under a short token and keep small fields in session
        token = uuid4().hex[:12]
        INMEM_RECIPIENTS[token] = recipients
        session["recipients_token"] = token
        session["subject"] = subject
        session["body"] = body

        # Show editable preview
        return render_template(
            "index.html",
            preview=True,
            subject=subject,
            body=body,
            recipients=recipients,
        )

    if action == "remove":
        # Remove selected recipients by value. If duplicates exist, all matching values are removed.
        token = session.get("recipients_token")
        if not token or token not in INMEM_RECIPIENTS:
            flash("No recipients to manage. Please start again.", "error")
            session.clear()
            return redirect(url_for("index"))

        selected = request.form.getlist("remove[]") or request.form.getlist("remove")
        recipients = INMEM_RECIPIENTS.get(token, [])

        if not selected:
            flash("No addresses selected to remove.", "info")
        else:
            new_list = [e for e in recipients if e not in selected]
            removed_count = len(recipients) - len(new_list)
            INMEM_RECIPIENTS[token] = new_list
            if removed_count > 0:
                flash(f"Removed {removed_count} address(es).", "info")
            else:
                flash("No matching addresses found to remove.", "info")

            # If list is now empty, clear token and send user back to compose
            if not new_list:
                INMEM_RECIPIENTS.pop(token, None)
                session.pop("recipients_token", None)
                flash("All recipients removed. Please upload a new CSV.", "error")
                return redirect(url_for("index"))

        # Re-render preview with current draft and updated recipients
        return render_template(
            "index.html",
            preview=True,
            subject=session.get("subject", ""),
            body=session.get("body", ""),
            recipients=INMEM_RECIPIENTS.get(token, []),
        )

    if action == "send":
        # Prefer values posted from the preview form; fall back to session draft
        subject = (request.form.get("subject") or session.get("subject") or "").strip()
        body = (request.form.get("body") or session.get("body") or "").strip()
        token = session.get("recipients_token")

        if not subject or not body or not token:
            flash("Nothing to send. Please start again.", "error")
            return redirect(url_for("index"))

        # Pop recipients from memory to avoid leaks or repeat sends
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

    # Fallback to form if action not recognized
    return redirect(url_for("index"))


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
