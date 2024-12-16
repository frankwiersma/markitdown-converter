"""
MarkItDown Converter Web Application
"""

from quart import Quart, render_template, request
from markitdown import MarkItDown
from openai import OpenAI
from werkzeug.utils import secure_filename
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from config import get_config
import asyncio
from concurrent.futures import ThreadPoolExecutor

config = get_config()
executor = ThreadPoolExecutor(max_workers=4)

class Converter:
    @staticmethod
    def is_image_file(filename: str) -> bool:
        return Path(filename).suffix.lower() in config.ALLOWED_IMAGE_EXTENSIONS

    @staticmethod
    def get_markitdown_instance(file_path: Optional[str] = None, api_key: Optional[str] = None) -> MarkItDown:
        if file_path and Converter.is_image_file(file_path) and api_key:
            return MarkItDown(mlm_client=OpenAI(api_key=api_key), mlm_model=config.OPENAI_MODEL)
        return MarkItDown()

    @staticmethod
    async def process_file_async(filepath: Path, api_key: Optional[str] = None) -> Dict[str, Any]:
        try:
            md = Converter.get_markitdown_instance(str(filepath), api_key)
            result = md.convert(str(filepath))
            return {'success': True, 'markdown': result.text_content}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            if filepath.exists():
                filepath.unlink()

    @staticmethod
    async def download_file_async(url: str) -> Optional[Path]:
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: requests.get(url, timeout=config.REQUEST_TIMEOUT)
            )
            filepath = config.UPLOAD_FOLDER / 'temp_file'
            await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: filepath.write_bytes(response.content)
            )
            return filepath
        except Exception:
            return None

app = Quart(__name__)
config.init_app(app)

@app.route('/')
async def index():
    return await render_template('index.html', has_api_key=bool(config.OPENAI_API_KEY))

@app.route('/convert', methods=['POST'])
async def convert():
    if 'file' in (await request.files):
        file = (await request.files)['file']
        if not file.filename:
            return {'success': False, 'error': 'No file provided'}, 400

        filepath = config.UPLOAD_FOLDER / secure_filename(file.filename)
        try:
            await file.save(filepath)
            form = await request.form
            return await Converter.process_file_async(filepath, form.get('api_key') or config.OPENAI_API_KEY)
        except Exception as e:
            return {'success': False, 'error': str(e)}, 400

    elif 'url' in (await request.form):
        form = await request.form
        url = form['url'].strip()
        if not url:
            return {'success': False, 'error': 'No URL provided'}, 400

        filepath = await Converter.download_file_async(url)
        if not filepath:
            return {'success': False, 'error': 'Failed to download file'}, 400

        return await Converter.process_file_async(filepath, form.get('api_key') or config.OPENAI_API_KEY)

    return {'success': False, 'error': 'No file or URL provided'}, 400

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT)
