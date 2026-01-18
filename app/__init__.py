from flask import Flask
from app.models import db
import os
SECRET_KEY = os.getenv("SQL_ALCHEMY_SECRET_KEY")

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///jobs.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

