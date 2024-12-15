"""
MarkItDown Converter Web Application
Converts various document formats to Markdown, including image analysis with OpenAI.
"""

from flask import Flask, render_template, request, jsonify
from markitdown import MarkItDown
from openai import OpenAI
from werkzeug.utils import secure_filename
import requests
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from asgiref.wsgi import WsgiToAsgi
from config import get_config

# Get configuration
config = get_config()

class Converter:
    """Handles document conversion operations."""
    
    @staticmethod
    def is_image_file(filename: str) -> bool:
        """Check if a file is an image based on its extension."""
        return Path(filename).suffix.lower() in config.ALLOWED_IMAGE_EXTENSIONS

    @staticmethod
    def get_markitdown_instance(file_path: Optional[str] = None, api_key: Optional[str] = None) -> MarkItDown:
        """Create a MarkItDown instance with appropriate configuration."""
        if file_path and Converter.is_image_file(file_path) and api_key:
            client = OpenAI(api_key=api_key)
            return MarkItDown(mlm_client=client, mlm_model=config.OPENAI_MODEL)
        return MarkItDown()

    @staticmethod
    def process_file(filepath: Path, api_key: Optional[str] = None) -> Tuple[Dict[str, Any], int]:
        """Process a file and convert it to markdown."""
        try:
            md = Converter.get_markitdown_instance(str(filepath), api_key)
            result = md.convert(str(filepath))
            return {
                'success': True,
                'markdown': result.text_content,
                'filename': filepath.name,
                'is_image': Converter.is_image_file(filepath.name)
            }, 200
        except Exception as e:
            logging.error(f"Error processing file: {str(e)}")
            return {'success': False, 'error': str(e)}, 400
        finally:
            if filepath.exists():
                filepath.unlink()

    @staticmethod
    def download_file(url: str) -> Optional[Path]:
        """Download a file from URL and save it temporarily."""
        try:
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            filepath = config.UPLOAD_FOLDER / 'temp_file'
            filepath.write_bytes(response.content)
            return filepath
        except requests.RequestException as e:
            logging.error(f"Error downloading file: {str(e)}")
            return None

# Initialize Flask application
app = Flask(__name__)
config.init_app(app)

@app.route('/')
def index() -> str:
    """Render the main page."""
    return render_template('index.html', has_api_key=bool(config.OPENAI_API_KEY))

@app.route('/convert', methods=['POST'])
def convert() -> Tuple[Dict[str, Any], int]:
    """Handle file conversion requests."""
    if 'file' in request.files:
        file = request.files['file']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        filename = secure_filename(file.filename)
        filepath = config.UPLOAD_FOLDER / filename
        
        try:
            file.save(filepath)
            api_key = request.form.get('api_key') or config.OPENAI_API_KEY
            return Converter.process_file(filepath, api_key)
        except Exception as e:
            if filepath.exists():
                filepath.unlink()
            return jsonify({'success': False, 'error': str(e)}), 400

    elif 'url' in request.form:
        url = request.form['url'].strip()
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400

        filepath = Converter.download_file(url)
        if not filepath:
            return jsonify({'success': False, 'error': 'Failed to download file'}), 400

        api_key = request.form.get('api_key') or config.OPENAI_API_KEY
        return Converter.process_file(filepath, api_key)

    return jsonify({'success': False, 'error': 'No file or URL provided'}), 400

@app.errorhandler(413)
def request_entity_too_large(error) -> Tuple[Dict[str, Any], int]:
    """Handle file size exceeded error."""
    return jsonify({
        'success': False,
        'error': f'File size exceeds the limit ({config.MAX_CONTENT_LENGTH // (1024*1024)}MB)'
    }), 413

# Convert Flask app to ASGI
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT)
    
    