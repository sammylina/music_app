
from flask import Blueprint, request, jsonify
from server.models import db, Playlist, Song

playlist_bp = Blueprint('playlist', __name__)

@playlist_bp.route('/api/playlists', methods=['GET'])
def get_playlists():
    playlists = Playlist.query.all()
    return jsonify([{
        "id": p.id,
        "title": p.title,
        "description": p.description
    } for p in playlists])

@playlist_bp.route('/api/playlists/<int:playlist_id>/songs', methods=['GET'])
def get_playlist_songs(playlist_id):
    songs = Song.query.filter_by(playlist_id=playlist_id).all()
    return jsonify([{
        "id": s.id,
        "title": s.title,
        "artist": s.artist,
        "playlistId": s.playlist_id,
        "audioFile": s.audio_file
    } for s in songs])

@playlist_bp.route('/api/playlists/<int:playlist_id>/songs', methods=['POST'])
def upload_song(playlist_id):
    # Check if playlist exists
    playlist = Playlist.query.get_or_404(playlist_id)
    
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
        
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No audio file selected"}), 400
        
    # Get other form data
    title = request.form.get('title')
    artist = request.form.get('artist')
    
    if not title or not artist:
        return jsonify({"error": "Title and artist are required"}), 400
    
    # Generate a unique filename to prevent conflicts
    import uuid
    filename = f"{uuid.uuid4()}_{audio_file.filename}"
    
    # Ensure storage directory exists
    import os
    storage_dir = os.path.join(os.path.dirname(__file__), 'storage', 'audio')
    os.makedirs(storage_dir, exist_ok=True)
    
    # Save file to disk
    file_path = os.path.join(storage_dir, filename)
    audio_file.save(file_path)
    
    # Save to database (without audio_data)
    song = Song(
        title=title,
        artist=artist,
        playlist_id=playlist_id,
        audio_file=filename
    )
    db.session.add(song)
    db.session.commit()
    
    return jsonify({
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "playlistId": song.playlist_id,
        "audioFile": song.audio_file
    }), 201
