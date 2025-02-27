from flask import Flask
from flask_cors import CORS
import os
from .models import db
from .auth_routes import auth_bp
from .playlist_routes import playlist_bp
from .song_routes import song_bp
from .config import config
from werkzeug.security import generate_password_hash
import psycopg2

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    # Configure from config classes
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Print the database URL without credentials for debugging
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    if db_url.startswith('postgresql'):
        print(f"Using PostgreSQL database")


    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(song_bp)

    # Create database and seed data
    with app.app_context():
        from .models import User, Playlist, Song
        try:
            db.create_all()
            print("Database tables created successfully.")
        except psycopg2.Error as e:
            print(f"Error creating database tables: {e}")
            return app #Return app to prevent further execution if DB creation fails

        # Add seed data if database is empty
        if not User.query.first():
            admin = User(
                username="admin@example.com",
                password=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)

            # Create playlists
            chill = Playlist(
                title="Chill Vibes",
                description="Relaxing tunes for your downtime"
            )
            workout = Playlist(
                title="Workout Mix",
                description="High-energy songs to keep you motivated"
            )
            db.session.add_all([chill, workout])
            db.session.commit()

            # Add songs
            songs = [
                Song(
                    title="Ocean Waves",
                    artist="Nature Sounds",
                    playlist_id=chill.id,
                    audio_file="ocean-waves.mp3"
                ),
                Song(
                    title="Gentle Rain",
                    artist="Ambient Music",
                    playlist_id=chill.id,
                    audio_file="gentle-rain.mp3"
                ),
                Song(
                    title="Power Up",
                    artist="Energy Beats",
                    playlist_id=workout.id,
                    audio_file="power-up.mp3"
                ),
                Song(
                    title="Fast Pace",
                    artist="Workout Kings",
                    playlist_id=workout.id,
                    audio_file="fast-pace.mp3"
                )
            ]
            db.session.add_all(songs)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
