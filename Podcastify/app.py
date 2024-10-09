from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from podcastify import get_final_results

app = Flask(__name__)


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf'}
VOICE_FOLDER = 'static/voice'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        podcast_name = request.values.get("podcast_name")
        print("------------------------------")
        print(podcast_name)
        print("------------------------------")
 
        print(file)
        print("--------------------------------------------------")
        print(file.filename)
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            get_final_results(filename,podcast_name)
            


            return redirect(url_for('audio_player', podcast_name=podcast_name))
    return render_template('index.html')


@app.route('/audio_player/<podcast_name>')
def audio_player(podcast_name):
    audio_filename = f"{podcast_name}.wav"
    return render_template('audio_player.html', podcast_name=podcast_name, audio_filename=audio_filename)

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(VOICE_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)