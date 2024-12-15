"""
Configuration settings for the MarkItDown Converter application.
"""

import os
from pathlib import Path
from typing import Set

class Config:
    """Application configuration settings."""
    
    # Application paths
    BASE_DIR = Path(__file__).parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    STATIC_FOLDER = BASE_DIR / 'static'
    TEMPLATE_FOLDER = BASE_DIR / 'templates'
    
    # File handling
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    ALLOWED_IMAGE_EXTENSIONS: Set[str] = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    
    # API configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4o'
    
    # Network settings
    HOST = '0.0.0.0'
    PORT = 8080
    REQUEST_TIMEOUT = 10  # Timeout for HTTP requests in seconds
    
    # Security
    ALLOWED_HOSTS = ['*']  # Configure this in production
    CORS_ORIGINS = ['*']   # Configure this in production
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGERS = {
        'werkzeug': {'level': 'INFO'},
        'pdfminer': {'level': 'WARNING'},  # Augmente le niveau pour pdfminer
        'markitdown': {'level': 'INFO'},
        'openai': {'level': 'INFO'},
    }
    
    # Development settings
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    TESTING = False
    
    @classmethod
    def init_app(cls, app) -> None:
        """Initialize Flask application with configuration."""
        # Create required directories
        cls.UPLOAD_FOLDER.mkdir(exist_ok=True)
        
        # Configure Flask app
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        app.config['DEBUG'] = cls.DEBUG
        app.config['TESTING'] = cls.TESTING
        
        # Configure logging
        import logging
        
        # Configuration de base
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT
        )
        
        # Configuration spécifique par logger
        for logger_name, logger_config in cls.LOGGERS.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(logger_config['level'])
        
        # Configuration du logger Flask
        app.logger.setLevel(getattr(logging, cls.LOG_LEVEL))

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    LOGGERS = {
        **Config.LOGGERS,
        'werkzeug': {'level': 'DEBUG'},
        'pdfminer': {'level': 'WARNING'},  # Toujours en WARNING même en dev
    }

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ALLOWED_HOSTS = ['your-domain.com']  # Configure for production
    CORS_ORIGINS = ['https://your-domain.com']  # Configure for production

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Get current configuration
def get_config():
    """Get the current configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default']) 