from flask import Flask, jsonify
from flask_cors import CORS
import os
from .models import db
from .auth_routes import auth_bp
from .playlist_routes import playlist_bp
from .song_routes import song_bp
from .admin_routes import admin_bp, init_admin
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
    print('db location: ', db_url)
    if db_url.startswith('postgresql'):
        print(f"Using PostgreSQL database")


    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(song_bp)
    app.register_blueprint(admin_bp)

    init_admin(app)

    # Create database and seed data
    with app.app_context():
        from .models import User, Playlist, Song
        try:
            db.create_all()
            print("Database tables created successfully by the App.")
        except psycopg2.Error as e:
            print(f"Error creating database tables: {e}")
            return app #Return app to prevent further execution if DB creation fails

        # Add seed data if database is empty
        if not User.query.first():
            print('creating another user')
            admin = User(
                username="admin@example.com",
                password=generate_password_hash("admin123", method='pbkdf2:sha256', salt_length=8),
                is_admin=True
            )
            db.session.add(admin)

            # Create playlists
            chill = Playlist(
                title="Level 1",
                description="If you are a beginner start here!!"
            )
            workout = Playlist(
                title="Level 2",
                description="For intermediate students only"
            )
            db.session.add_all([chill, workout])
            db.session.commit()

            # Add songs
            songs = [
                Song(
                    title="Exercise 1",
                    artist="Nature Sounds",
                    playlist_id=chill.id,
                    audio_file="amharic_lesson_1.mp3"
                ),
                Song(
                    title="Exercise 2",
                    artist="Ambient Music",
                    playlist_id=chill.id,
                    audio_file="amharic_lesson_2.mp3"
                ),
                Song(
                    title="Exercise 3",
                    artist="Energy Beats",
                    playlist_id=workout.id,
                    audio_file="amharic_lesson_3.mp3"
                ),
                Song(
                    title="Exercise 4",
                    artist="Workout Kings",
                    playlist_id=workout.id,
                    audio_file="amharic_lesson_4.mp3"
                )
            ]
            db.session.add_all(songs)
            db.session.commit()

   #Added test endpoint
    @app.route('/api/test', methods=['GET'])
    def test_connection():
        return jsonify({"message": "Backend connection successful!"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
