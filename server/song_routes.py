
from flask import Blueprint, request, jsonify, send_file
import os
from .models import db, Song, PlayHistory

song_bp = Blueprint('song', __name__)

@song_bp.route('/api/songs/<int:song_id>/audio', methods=['GET'])
def get_song_audio(song_id):
    song = Song.query.get_or_404(song_id)
    file_path = os.path.join(os.path.dirname(__file__), 'storage', 'audio', song.audio_file)
    return send_file(
        file_path,
        mimetype='audio/mpeg'
    )

@song_bp.route('/api/songs/<int:song_id>/play', methods=['POST'])
def record_play(song_id):
    from flask import session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
        
    play = PlayHistory(user_id=user_id, song_id=song_id)
    db.session.add(play)
    db.session.commit()
    return '', 200

@song_bp.route('/api/songs/<int:song_id>/plays', methods=['GET'])
def get_play_count(song_id):
    count = PlayHistory.query.filter_by(song_id=song_id).count()
    return jsonify(count)
