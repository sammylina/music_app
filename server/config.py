from dotenv import load_dotenv
import os

env = os.getenv("FLASK_ENV", "development").lower()

# Load the appropriate .env file
if env == "production":
    load_dotenv(dotenv_path=".env.production")
elif env == "development":
    load_dotenv(dotenv_path=".env.development")
else:
    load_dotenv(dotenv_path=".env")  #
    

class Config:
    SECRET_KEY = os.getenv('SESSION_SECRET', 'dev_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUDIO_STORAGE_ROOT = os.getenv('AUDIO_STORAGE_ROOT', '/var/www/audio/')

    # Use Replit's PostgreSQL database URL if available
    db_url = os.getenv('DATABASE_URL')
    if db_url and db_url.startswith('postgresql'):
        # Make the URL compatible with SQLAlchemy
        db_url = db_url.replace('postgres://', 'postgresql://')
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # Fallback to SQLite for local development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///music.db'

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

