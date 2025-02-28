
import os
from flask import Flask
from models import db, Song
from config import config
import shutil

def migrate_db():
    """Migrate from storing audio in database to filesystem"""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    
    with app.app_context():
        # Ensure storage directory exists
        storage_dir = os.path.join(os.path.dirname(__file__), 'storage', 'audio')
        os.makedirs(storage_dir, exist_ok=True)
        
        # Get all songs with audio_data
        songs = Song.query.all()
        print(f"Found {len(songs)} songs to migrate")
        
        for song in songs:
            try:
                if hasattr(song, 'audio_data') and song.audio_data:
                    # Write audio data to file
                    file_path = os.path.join(storage_dir, song.audio_file)
                    with open(file_path, 'wb') as f:
                        f.write(song.audio_data)
                    print(f"Migrated song: {song.title}")
            except Exception as e:
                print(f"Error migrating song {song.title}: {e}")
                
        print("Migration completed!")
        
        # Now, let's update the database schema - this is already handled by SQLAlchemy
        # when you remove the column from the model and run db.create_all()

if __name__ == "__main__":
    migrate_db()

