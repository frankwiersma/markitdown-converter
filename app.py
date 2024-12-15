from flask import Flask, render_template, request, jsonify
from markitdown import MarkItDown
import os
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['UPLOAD_FOLDER'] = 'uploads'

# Assurez-vous que le dossier uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

md = MarkItDown()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            try:
                result = md.convert(filepath)
                os.remove(filepath)  # Nettoyage du fichier
                return jsonify({'success': True, 'markdown': result.text_content})
            except Exception as e:
                os.remove(filepath)  # Nettoyage en cas d'erreur
                return jsonify({'success': False, 'error': str(e)})
    
    elif 'url' in request.form:
        url = request.form['url']
        try:
            response = requests.get(url)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_file')
            with open(filepath, 'wb') as f:
                f.write(response.content)
            result = md.convert(filepath)
            os.remove(filepath)
            return jsonify({'success': True, 'markdown': result.text_content})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': False, 'error': 'No file or URL provided'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 