from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Many-to-many relationship table
job_skills = db.Table('job_skills',
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(40), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(60), nullable=False)
    salary = db.Column(db.String(20))
    url = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="applied")
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    skills = db.relationship('Skill', secondary=job_skills, backref='jobs')

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    count = db.Column(db.Integer, default=1)