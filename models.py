from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# create SQLAlchemy instance, initialized later in app.py
db = SQLAlchemy()

class User(UserMixin, db.Model):
    name = db.Column(db.String(255))
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
