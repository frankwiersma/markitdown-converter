"""
Configuration settings for MarkItDown Converter
"""

import os
from pathlib import Path

class Config:
    # Application paths
    BASE_DIR = Path(__file__).parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    
    # File handling
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    
    # API configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4o'
    
    # Network settings
    HOST = '0.0.0.0'
    PORT = 8080
    REQUEST_TIMEOUT = 10
    
    # Development settings
    DEBUG = os.getenv('QUART_ENV') == 'development'
    
    @classmethod
    def init_app(cls, app):
        cls.UPLOAD_FOLDER.mkdir(exist_ok=True)
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH
        app.config['DEBUG'] = cls.DEBUG

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.getenv('QUART_ENV', 'development')
    return config.get(env, config['default'])