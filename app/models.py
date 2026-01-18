from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(40), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(60), nullable=False)
    salary = db.Column(db.Double)
    url = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="applied")
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    count = db.Column(db.Integer, default=1)