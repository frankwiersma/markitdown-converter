"""
MarkItDown Converter Web Application
Converts various document formats to Markdown, including image analysis with OpenAI.
"""

from quart import Quart, render_template, request, jsonify
from markitdown import MarkItDown
from openai import OpenAI
from werkzeug.utils import secure_filename
import requests
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from config import get_config
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Get configuration
config = get_config()

# Create thread pool for async operations
executor = ThreadPoolExecutor(max_workers=4)

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
            return {'success': False, 'error': str(e)}, 400
        finally:
            if filepath.exists():
                filepath.unlink()

    @staticmethod
    async def process_file_async(filepath: Path, api_key: Optional[str] = None) -> Tuple[Dict[str, Any], int]:
        """Process a file asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, Converter.process_file, filepath, api_key)

    @staticmethod
    async def download_file_async(url: str) -> Optional[Path]:
        """Download a file from URL asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                executor,
                lambda: requests.get(url, timeout=config.REQUEST_TIMEOUT)
            )
            response.raise_for_status()
            
            filepath = config.UPLOAD_FOLDER / 'temp_file'
            await loop.run_in_executor(
                executor,
                lambda: filepath.write_bytes(response.content)
            )
            return filepath
        except Exception:
            return None

# Initialize Quart application
app = Quart(__name__)
config.init_app(app)

@app.route('/')
async def index() -> str:
    """Render the main page."""
    return await render_template('index.html', has_api_key=bool(config.OPENAI_API_KEY))

@app.route('/convert', methods=['POST'])
async def convert() -> Tuple[Dict[str, Any], int]:
    """Handle file conversion requests."""
    if 'file' in (await request.files):
        file = (await request.files)['file']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        filename = secure_filename(file.filename)
        filepath = config.UPLOAD_FOLDER / filename
        
        try:
            await file.save(filepath)
            form = await request.form
            api_key = form.get('api_key') or config.OPENAI_API_KEY
            return await Converter.process_file_async(filepath, api_key)
        except Exception as e:
            if filepath.exists():
                filepath.unlink()
            return jsonify({'success': False, 'error': str(e)}), 400

    elif 'url' in (await request.form):
        form = await request.form
        url = form['url'].strip()
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400

        filepath = await Converter.download_file_async(url)
        if not filepath:
            return jsonify({'success': False, 'error': 'Failed to download file'}), 400

        api_key = form.get('api_key') or config.OPENAI_API_KEY
        return await Converter.process_file_async(filepath, api_key)

    return jsonify({'success': False, 'error': 'No file or URL provided'}), 400

@app.errorhandler(413)
async def request_entity_too_large(error) -> Tuple[Dict[str, Any], int]:
    """Handle file size exceeded error."""
    return jsonify({
        'success': False,
        'error': f'File size exceeds the limit ({config.MAX_CONTENT_LENGTH // (1024*1024)}MB)'
    }), 413

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT)
    
    