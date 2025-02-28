
import os
from flask import Flask
#from app.models import db
#from app.config import config

from models import db
from config import config

def init_db(app=None):
    """Initialize the database with proper configuration"""
    if app is None:
        app = Flask(__name__)
        app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])
        db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
    
    return app

if __name__ == "__main__":
    init_db()
