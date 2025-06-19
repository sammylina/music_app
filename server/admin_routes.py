# admin_routes.py
from flask import Blueprint, send_from_directory
from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView
import os
from .models import db, Lesson, Line

# Optional: protect admin with Flask-Login later
admin_bp = Blueprint('admin_files', __name__)

# Serve uploaded audio files
@admin_bp.route('/storage/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('storage/audio', filename)

# Custom Admin View for Line

class LineModelView(ModelView):
    form_columns = ['text', 'audio_file', 'lesson']
    form_extra_fields = {
        'audio_file': form.FileUploadField(
            'Audio File',
            base_path=os.path.join(os.getcwd(), 'storage/audio'),
            relative_path='.',
            allow_overwrite=True
        )
    }

    column_formatters = {
        'audio_file': lambda v, c, m, p: f'''
            {m.audio_file or "No file"}
            <br>
            <audio controls>
                <source src="/storage/audio/{m.audio_file}" type="audio/mpeg">
            </audio>
        ''' if m.audio_file else 'No audio'
    }

# Custom Admin View for Lesson (with inline lines)
class LessonModelView(ModelView):
    inline_models = [(Line, dict(form_extra_fields={
        'audio_file': form.FileUploadField(
            'Audio File',
            base_path=os.path.join(os.getcwd(), 'storage/audio'),
            relative_path='.',
            allow_overwrite=True
        )
    }))]
    form_columns = ['title', 'lines']

# Function to init Flask-Admin (called from app.py)
def init_admin(app):
    admin = Admin(app, name='Lesson CMS', template_mode='bootstrap4')
    admin.add_view(LessonModelView(Lesson, db.session))
    admin.add_view(LineModelView(Line, db.session))

