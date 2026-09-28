import os
from dotenv import load_dotenv
from models import db

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

DATABASE_URL = os.getenv('DATABASE_URL')


def init_db(app):
    """Initialize the database connection and create tables."""
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()


def get_db():
    """Get the database session."""
    return db


def test_connection():
    """Test if PostgreSQL is connected."""
    try:
        result = db.session.execute(db.text('SELECT 1'))
        return True
    except Exception:
        return False
