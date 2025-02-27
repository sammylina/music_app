#!/usr/bin/env python3

import os
import sys
from flask import Flask
from werkzeug.security import generate_password_hash
import random
import shutil
from app.models import db, User, Playlist, Song, PlayHistory
from server.app.config import config
from datetime import datetime, timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    
    # Ensure storage directory exists
    storage_dir = os.path.join(os.path.dirname(__file__), 'storage', 'audio')
    os.makedirs(storage_dir, exist_ok=True)
    
    return app

def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing existing data...")
        PlayHistory.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        User.query.delete()
        db.session.commit()
        
        print("Creating users...")
        # Create users
        users = [
            User(username="admin@example.com", password=generate_password_hash("admin123"), is_admin=True),
            User(username="john@example.com", password=generate_password_hash("password123"), is_admin=False),
            User(username="alice@example.com", password=generate_password_hash("password123"), is_admin=False),
            User(username="bob@example.com", password=generate_password_hash("password123"), is_admin=False),
        ]
        db.session.add_all(users)
        db.session.commit()
        
        print("Creating playlists...")
        # Create playlists
        playlists = [
            Playlist(title="Chill Vibes", description="Relaxing tunes for your downtime"),
            Playlist(title="Workout Mix", description="High-energy songs to keep you motivated"),
            Playlist(title="Study Session", description="Focus-enhancing music for productive studying"),
            Playlist(title="Road Trip", description="Perfect tracks for long drives"),
        ]
        db.session.add_all(playlists)
        db.session.commit()
        
        print("Creating songs...")
        # Create songs
        songs = [
            # Chill Vibes songs
            Song(title="Ocean Waves", artist="Nature Sounds", playlist_id=playlists[0].id, 
                 audio_file="ocean-waves.mp3"),
            Song(title="Gentle Rain", artist="Ambient Music", playlist_id=playlists[0].id,
                 audio_file="gentle-rain.mp3"),
            Song(title="Sunset Meditation", artist="Zen Masters", playlist_id=playlists[0].id,
                 audio_file="sunset-meditation.mp3"),
            
            # Workout Mix songs
            Song(title="Power Up", artist="Energy Beats", playlist_id=playlists[1].id,
                 audio_file="power-up.mp3"),
            Song(title="Fast Pace", artist="Workout Kings", playlist_id=playlists[1].id,
                 audio_file="fast-pace.mp3"),
            Song(title="No Pain No Gain", artist="Gym Heroes", playlist_id=playlists[1].id,
                 audio_file="no-pain-no-gain.mp3"),
            
            # Study Session songs
            Song(title="Deep Focus", artist="Study Guru", playlist_id=playlists[2].id,
                 audio_file="deep-focus.mp3"),
            Song(title="Brain Waves", artist="Concentration", playlist_id=playlists[2].id,
                 audio_file="brain-waves.mp3"),
            
            # Road Trip songs
            Song(title="Highway Cruising", artist="Road Warriors", playlist_id=playlists[3].id,
                 audio_file="highway-cruising.mp3"),
            Song(title="Desert Sunset", artist="Journey", playlist_id=playlists[3].id,
                 audio_file="desert-sunset.mp3"),
        ]
        db.session.add_all(songs)
        db.session.commit()
        
        # Create dummy audio files for each song
        for song in songs:
            file_path = os.path.join(os.path.dirname(__file__), 'storage', 'audio', song.audio_file)
            with open(file_path, 'wb') as f:
                f.write(generate_dummy_audio())
            print(f"Created audio file: {song.audio_file}")
        
        print("Creating play history...")
        # Create play history (simulate users listening to songs)
        play_histories = []
        
        for user in users:
            # Each user listens to 5-15 songs randomly
            listen_count = random.randint(5, 15)
            for _ in range(listen_count):
                song = random.choice(songs)
                # Random date within last 30 days
                days_ago = random.randint(0, 30)
                played_at = datetime.utcnow() - timedelta(days=days_ago, 
                                                          hours=random.randint(0, 23), 
                                                          minutes=random.randint(0, 59))
                
                play_histories.append(
                    PlayHistory(user_id=user.id, song_id=song.id, played_at=played_at)
                )
        
        db.session.add_all(play_histories)
        db.session.commit()
        
        print("Database seeded successfully!")
        print(f"Created {len(users)} users, {len(playlists)} playlists, {len(songs)} songs, and {len(play_histories)} play history records.")

def generate_dummy_audio():
    # Generate random binary data to simulate audio file (500KB)
    return os.urandom(512 * 1024)

if __name__ == "__main__":
    seed_database()

