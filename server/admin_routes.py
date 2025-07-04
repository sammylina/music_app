# admin_routes.py
from flask import Blueprint, request, flash, redirect, url_for, current_app
from flask_admin import Admin, form, expose
from flask_admin.contrib.sqla import ModelView
import os
from server.models import db, Lesson, Line, Song
from markupsafe import Markup
from pydub import AudioSegment

# Optional: protect admin with Flask-Login later
admin_bp = Blueprint('admin_files', __name__)


# Custom Admin View for Line
class LineModelView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav', 'ogg'}

    @expose('/')
    def index_view(self):
        lesson_id = request.args.get('lesson_id', type=int)
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
            line.break_after = 'break_after' in request.form

            audio_file = request.files.get('audio_file')
            if audio_file and self.allowed_file(audio_file.filename):
                lesson_id = line.lesson_id
                line_id = line.id
                filename = f'lesson_{lesson_id}/line_{line_id}.wav'
                full_path = os.path.join(current_app.config['AUDIO_STORAGE_ROOT'], 'lines', filename)

                try:
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                except Exception as e:
                    flash('Unable to create folder for {full_path}','error') 

                audio_file.save(full_path)

                line.audio_file = filename  # save relative path

            
            db.session.commit()
            flash('Line updated', 'success')
            return redirect(url_for('.index_view', lesson_id=line.lesson_id))

        # Render your custom edit template with line data
        return self.render('admin/line_custom_edit.html', line=line)


    @expose('/reorder', methods=['POST'])
    def reorder_view(self):
        lesson_id = request.args.get('lesson_id', type=int)
        if not lesson_id:
            flash('Lesson ID is missing', 'error')
            return redirect(url_for('lesson.index_view'))

        lesson = Lesson.query.get_or_404(lesson_id)

        # 'ordered_line_ids' holds all line ids in the new order
        ordered_line_ids = request.form.getlist('ordered_line_ids')

        try:
            # Validate all IDs belong to this lesson
            lines_by_id = {str(line.id): line for line in lesson.lines}
            if set(ordered_line_ids) != set(lines_by_id.keys()):
                flash('Invalid line IDs submitted.', 'error')
                return redirect(url_for('.index_view', lesson_id=lesson_id))

            # Update order based on position in ordered_line_ids list
            for order_idx, line_id in enumerate(ordered_line_ids):
                lines_by_id[line_id].order = order_idx + 1 # 1-based order

            db.session.commit()
            flash('Line order updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating order: {e}', 'error')

        return redirect(url_for('.index_view', lesson_id=lesson_id))

    @expose('/add')
    def add_line(self):
        lesson_id = request.args.get('lesson_id', type=int)
        if not lesson_id:
            flash('Lesson ID missing', 'error')
            return redirect(url_for('lesson.index_view'))

        lesson = Lesson.query.get_or_404(lesson_id)

        # Determine next order
        max_order = db.session.query(db.func.max(Line.order)).filter_by(lesson_id=lesson_id).scalar() or 0
        new_line = Line(
            text='[Your text here]',
            audio_file='',  # or maybe 'placeholder.mp3'
            order=max_order + 1,
            lesson_id=lesson_id
        )

        db.session.add(new_line)
        db.session.commit()

        flash('✅ New line added!', 'success')
        return redirect(url_for('.index_view', lesson_id=lesson_id))



    @expose('/build')
    def build_lesson_audio(self):
        lesson_id = request.args.get('lesson_id', type=int)
        if not lesson_id:
            flash("Lesson ID is missing", "error")
            return redirect(url_for('lesson.index_view'))

        lesson = Lesson.query.get_or_404(lesson_id)
        lines = sorted(lesson.lines, key=lambda l: l.order)

        if not lines:
            flash("No lines found for this lesson", "warning")
            return redirect(url_for('.index_view', lesson_id=lesson_id))

        combined = AudioSegment.empty()

        try:
            for line in lines:
                if not line.audio_file:
                    continue  # skip empty

                audio_path = os.path.join(current_app.config['AUDIO_STORAGE_ROOT'], 'lines', line.audio_file)
                if not os.path.exists(audio_path):
                    flash(f"Missing file: {line.audio_file}", "error")
                    return redirect(url_for('.index_view', lesson_id=lesson_id))

                if os.path.getsize(audio_path) < 1000:
                    flash(f"Audio file {line.audio_file} is too small or empty.", "error")
                    return redirect(url_for('.index_view', lesson_id=lesson_id))


                clip = AudioSegment.from_file(audio_path)

                combined += clip  # no silence, no fade

                if getattr(line, 'break_after', False):  # check break_after attribute
                    silence = AudioSegment.silent(duration=len(clip))  # silence same length as clip
                    combined += silence  # add silence break after clip

            # Export combined audio
            output_filename = f'lesson_{lesson.id}.mp3'
            output_path = os.path.join(current_app.config['AUDIO_STORAGE_ROOT'], 'songs', output_filename)
            combined.export(output_path, format='mp3')

            # Create or update Song entry
            if lesson.song:
                lesson.song.audio_file = output_filename  # overwrite file path

            else:
                song = Song( title=lesson.title,
                    artist='System',
                    playlist_id=1,
                    audio_file=output_filename
                )
                db.session.add(song)
                db.session.flush() # Get song.id before commit
                lesson.song = song

            db.session.commit()

            flash("✅ Lesson audio built and saved to Song!", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"⚠️ Build failed: {str(e)}", "error")

        return redirect(url_for('.index_view', lesson_id=lesson_id))


# Custom Admin View for Lesson (with inline lines)
class LessonModelView(ModelView):

    can_edit = False

    def _title_formatter(view, context, model, name):
        line_url = url_for('line.index_view', lesson_id=model.id)
        return Markup(f'<a href="{line_url}">{model.title}</a>')

    column_formatters = {
        'title': _title_formatter
    }

#    inline_models = [(Line, dict(form_extra_fields={
#        'audio_file': form.FileUploadField(
#            'Audio File',
#            base_path=os.path.join(os.getcwd(), 'storage/audio'),
#            relative_path='.',
#            allow_overwrite=True
#        )
#    }))]
    #form_columns = ['title', 'lines']

# Function to init Flask-Admin (called from app.py)
def init_admin(app):
    admin = Admin(app, name='Lesson CMS', template_mode='bootstrap4')
    admin.add_view(LessonModelView(Lesson, db.session, endpoint='lesson'))
    admin.add_view(LineModelView(Line, db.session, endpoint='line'))

