from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not name or not email or not password:
            flash("Name, email and password are required", "error")
            return render_template("signup.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return render_template("signup.html")

        u = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()

        login_user(u)
        flash("Welcome", "success")
        return redirect(url_for("index"))
    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        u = User.query.filter_by(email=email).first()
        if not u or not check_password_hash(u.password_hash, password):
            flash("Invalid credentials", "error")
            return render_template("login.html")
        login_user(u, remember=True)
        flash("Signed in", "success")
        return redirect(url_for("index"))
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Signed out", "success")
    return redirect(url_for("auth.login"))
