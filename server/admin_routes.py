# admin_routes.py
from flask import Blueprint, send_from_directory, request, flash, redirect, url_for
from flask_admin import Admin, form, expose
from flask_admin.contrib.sqla import ModelView
import os
import uuid
from .models import db, Lesson, Line
from wtforms.validators import ValidationError
from markupsafe import Markup

# Optional: protect admin with Flask-Login later
admin_bp = Blueprint('admin_files', __name__)

# Serve uploaded audio files
@admin_bp.route('/storage/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('storage/audio', filename)

# Custom Admin View for Line
class LineModelView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False

    @expose('/')
    def index_view(self):
        lesson_id = request.args.get('lesson_id', type=int)
        print('lesson id: ', lesson_id)
        if not lesson_id:
            flash('Please select a lesson first', 'warning')
            return redirect(url_for('lesson.index_view'))

        lesson = Lesson.query.get_or_404(lesson_id)

        return self.render('admin/line_custom_list.html', lesson=lesson, lines=lesson.lines)

    @expose('/edit/<int:id>', methods=('GET', 'POST'))
    def edit_view(self, id):
        line = Line.query.get_or_404(id)
        
        if request.method == 'POST':
            # Process form data manually (text, order, audio file)
            line.text = request.form.get('text', line.text)
            line.order = request.form.get('order', line.order)

            audio_file = request.files.get('audio_file')
            if audio_file and allowed_file(audio_file.filename):
                filename = secure_filename(audio_file.filename)
                audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                line.audio_file = filename
            
            db.session.commit()
            flash('Line updated', 'success')
            return redirect(url_for('.index_view', lesson_id=line.lesson_id))

        # Render your custom edit template with line data
        return self.render('admin/line_custom_edit.html', line=line)



# Custom Admin View for Lesson (with inline lines)
class LessonModelView(ModelView):

    def _title_formatter(view, context, model, name):
        line_url = url_for('line.index_view', lesson_id=model.id)
        return Markup(f'<a href="{line_url}">{model.title}</a>')

    column_formatters = {
        'title': _title_formatter
    }

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
    admin.add_view(LessonModelView(Lesson, db.session, endpoint='lesson'))
    admin.add_view(LineModelView(Line, db.session, endpoint='line'))

