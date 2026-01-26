from flask import Flask
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from app.models import db
from app import routes
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask-Login
login_manager = LoginManager()

# Initialize OAuth for Google authentication
oauth = OAuth()

def create_app():
    app = Flask(__name__)

    # Configuration
    database_url = os.getenv('DATABASE_URL', 'sqlite:///jobs.db')
    
    # Fix for Supabase/Heroku compatibility
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Engine options optimized for serverless (Vercel)
    if database_url.startswith('postgresql://'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': False,           # Disable pre-ping for serverless
            'pool_recycle': 300,              # Recycle connections every 5 minutes
            'pool_size': 1,                   # Smaller pool for serverless
            'max_overflow': 0,                # No overflow connections
            'connect_args': {
                'connect_timeout': 10,        # 10 second timeout
                'sslmode': 'require'          # Require SSL
            }
        }
    
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'routes.login_page'
    
    # Configure Google OAuth
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    # Create database tables
    with app.app_context():
        db.create_all()

    app.register_blueprint(routes.bp)

    return app

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))