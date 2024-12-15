from flask import Flask, render_template, request, jsonify
from markitdown import MarkItDown
from openai import OpenAI
from werkzeug.utils import secure_filename
import os
import requests
from typing import Optional, Tuple
from pathlib import Path

class Config:
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    UPLOAD_FOLDER = Path('uploads')
    ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
app.config.from_object(Config)

# Ensure uploads directory exists
Config.UPLOAD_FOLDER.mkdir(exist_ok=True)

def is_image_file(filename: str) -> bool:
    """Check if a file is an image based on its extension."""
    return Path(filename).suffix.lower() in Config.ALLOWED_IMAGE_EXTENSIONS

def get_markitdown_instance(file_path: Optional[str] = None) -> MarkItDown:
    """Create a MarkItDown instance with appropriate configuration."""
    if file_path and is_image_file(file_path):
        api_key = Config.OPENAI_API_KEY or request.form.get('api_key')
        if api_key:
            client = OpenAI(api_key=api_key)
            return MarkItDown(mlm_client=client, mlm_model='gpt-4o')
    return MarkItDown()

def handle_file_conversion(file_path: Path) -> Tuple[dict, int]:
    """Convert a file to markdown and handle cleanup."""
    try:
        md = get_markitdown_instance(str(file_path))
        result = md.convert(str(file_path))
        return {'success': True, 'markdown': result.text_content}, 200
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400
    finally:
        if file_path.exists():
            file_path.unlink()

def download_and_save_file(url: str) -> Optional[Path]:
    """Download a file from URL and save it temporarily."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        file_path = Config.UPLOAD_FOLDER / 'temp_file'
        file_path.write_bytes(response.content)
        return file_path
    except requests.RequestException as e:
        return None

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', 
                         has_api_key=bool(Config.OPENAI_API_KEY))

@app.route('/convert', methods=['POST'])
def convert():
    """Handle file conversion requests."""
    if 'file' in request.files:
        file = request.files['file']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        filename = secure_filename(file.filename)
        filepath = Config.UPLOAD_FOLDER / filename
        
        try:
            file.save(filepath)
            api_key = request.form.get('api_key')
            if api_key and is_image_file(filename):
                client = OpenAI(api_key=api_key)
                md = MarkItDown(mlm_client=client, mlm_model='gpt-4o')
            else:
                md = MarkItDown()
                
            result = md.convert(str(filepath))
            return jsonify({
                'success': True, 
                'markdown': result.text_content,
                'filename': filename
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            if filepath.exists():
                filepath.unlink()
    
    elif 'url' in request.form:
        url = request.form['url'].strip()
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            filepath = Config.UPLOAD_FOLDER / 'temp_file'
            filepath.write_bytes(response.content)
            
            api_key = request.form.get('api_key')
            if api_key and any(url.lower().endswith(ext) for ext in Config.ALLOWED_IMAGE_EXTENSIONS):
                client = OpenAI(api_key=api_key)
                md = MarkItDown(mlm_client=client, mlm_model='gpt-4o')
            else:
                md = MarkItDown()
                
            result = md.convert(str(filepath))
            return jsonify({
                'success': True, 
                'markdown': result.text_content,
                'source_url': url
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            if filepath.exists():
                filepath.unlink()

    return jsonify({'success': False, 'error': 'No file or URL provided'}), 400

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size exceeded error."""
    return jsonify({
        'success': False,
        'error': 'File size exceeds the limit (16MB)'
    }), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 
    
    