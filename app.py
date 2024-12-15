from flask import Flask, render_template, request, jsonify
from markitdown import MarkItDown
import os
import requests
from werkzeug.utils import secure_filename
from openai import OpenAI

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_markitdown_instance(file_path=None):
    """Crée une instance de MarkItDown avec la configuration appropriée"""
    if file_path and file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        api_key = app.config['OPENAI_API_KEY'] or request.form.get('api_key')
        if api_key:
            client = OpenAI(api_key=api_key)
            return MarkItDown(mlm_client=client, mlm_model='gpt-4o')
    return MarkItDown()

@app.route('/')
def index():
    return render_template('index.html', has_api_key=bool(app.config['OPENAI_API_KEY']))

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                md = get_markitdown_instance(filepath)
                result = md.convert(filepath)
                os.remove(filepath)  # Cleanup file
                return jsonify({'success': True, 'markdown': result.text_content})
            except Exception as e:
                os.remove(filepath)  # Cleanup on error
                return jsonify({'success': False, 'error': str(e)})
    
    elif 'url' in request.form:
        url = request.form['url']
        try:
            response = requests.get(url)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_file')
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            md = get_markitdown_instance(filepath)
            result = md.convert(filepath)
            os.remove(filepath)
            return jsonify({'success': True, 'markdown': result.text_content})
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': False, 'error': 'No file or URL provided'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 