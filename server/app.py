from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from io import BytesIO

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///music.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET', 'dev_key')

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    songs = db.relationship('Song', backref='playlist', lazy=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    artist = db.Column(db.String(120), nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    audio_file = db.Column(db.String(255), nullable=False)
    audio_data = db.Column(db.LargeBinary)

class PlayHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400
    
    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password, data['password']):
        return jsonify({
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin
        })
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/playlists', methods=['GET'])
def get_playlists():
    playlists = Playlist.query.all()
    return jsonify([{
        "id": p.id,
        "title": p.title,
        "description": p.description
    } for p in playlists])

@app.route('/api/playlists/<int:playlist_id>/songs', methods=['GET'])
def get_playlist_songs(playlist_id):
    songs = Song.query.filter_by(playlist_id=playlist_id).all()
    return jsonify([{
        "id": s.id,
        "title": s.title,
        "artist": s.artist,
        "playlistId": s.playlist_id,
        "audioFile": s.audio_file
    } for s in songs])

@app.route('/api/songs/<int:song_id>/audio', methods=['GET'])
def get_song_audio(song_id):
    song = Song.query.get_or_404(song_id)
    return send_file(
        BytesIO(song.audio_data),
        mimetype='audio/mpeg'
    )

@app.route('/api/songs/<int:song_id>/play', methods=['POST'])
def record_play(song_id):
    # TODO: Get actual user_id from session
    user_id = 1  # Temporary
    play = PlayHistory(user_id=user_id, song_id=song_id)
    db.session.add(play)
    db.session.commit()
    return '', 200

@app.route('/api/songs/<int:song_id>/plays', methods=['GET'])
def get_play_count(song_id):
    count = PlayHistory.query.filter_by(song_id=song_id).count()
    return jsonify(count)

# Create initial database
with app.app_context():
    db.create_all()
    
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
                audio_file="ocean-waves.mp3",
                audio_data=b""  # Empty audio data for demo
            ),
            Song(
                title="Gentle Rain",
                artist="Ambient Music",
                playlist_id=chill.id,
                audio_file="gentle-rain.mp3",
                audio_data=b""
            ),
            Song(
                title="Power Up",
                artist="Energy Beats",
                playlist_id=workout.id,
                audio_file="power-up.mp3",
                audio_data=b""
            ),
            Song(
                title="Fast Pace",
                artist="Workout Remix",
                playlist_id=workout.id,
                audio_file="fast-pace.mp3",
                audio_data=b""
            )
        ]
        db.session.add_all(songs)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
