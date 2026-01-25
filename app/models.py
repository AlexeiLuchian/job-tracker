from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# Many-to-many relationship table
job_skills = db.Table('job_skills',
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """
    User model for authentication
    - UserMixin: Provides Flask-Login required methods (is_authenticated, is_active, etc.)
    - Each user can have multiple jobs (one-to-many relationship)
    """
    id = db.Column(db.Integer, primary_key=True)

    google_id = db.Column(db.String(100), unique=True, nullable=False)  # Unique ID from Google
    email = db.Column(db.String(100), unique=True, nullable=False)      # User's email
    name = db.Column(db.String(100))                                     # Display name
    picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    jobs = db.relationship('Job', backref='user', lazy=True, cascade='all, delete-orphan')

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    count = db.Column(db.Integer, default=1)