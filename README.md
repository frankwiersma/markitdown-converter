# MarkItDown Converter

MarkItDown Converter is a web application that converts various document formats into Markdown. It supports files, URLs, and includes AI-powered image analysis capabilities.

![MarkItDown Screenshot](screenshot.png)

## Features

- **Multiple Input Methods**:
  - Drag & drop files
  - File selection dialog
  - URL conversion
  - Image analysis with GPT-4o

- **Supported Formats**:
  - PDF documents
  - Word documents (.docx)
  - PowerPoint presentations (.pptx)
  - Excel spreadsheets (.xlsx)
  - Images (PNG, JPG, JPEG, GIF, WEBP)
  - Web pages (via URL)

- **API Integration**:
  - RESTful API for programmatic access
  - cURL support for command-line usage
  - OpenAI integration for image analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/markitdown-converter.git
cd markitdown-converter
```

2. Install dependencies with uv (recommended):
```bash
# Install uv if not already installed
pip install uv

# Install dependencies
uv pip install -e .
```

## Usage

### Running with uv (Recommended)

For local development:
```bash
# Basic usage
uv run app.py

# Or with uvicorn (using ASGI)
uv run uvicorn app:asgi_app --host 0.0.0.0 --port 8080 --reload
```

### Running with Uvicorn in Production

For production deployment:
```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --workers 4
```

Additional Uvicorn options:
- `--reload`: Enable auto-reload on code changes
- `--workers N`: Number of worker processes (recommended: 2-4 × CPU cores)
- `--log-level`: Set log level (debug, info, warning, error, critical)
- `--ssl-keyfile`: SSL key file for HTTPS
- `--ssl-certfile`: SSL certificate file for HTTPS

*Note: Using `uv run` is recommended for development as it provides better dependency isolation and faster startup times.*

### Flask Development Server

For local development only:
```bash
python app.py
```

*Note: The Flask development server is not suitable for production use.*

### Web Interface

1. Start the server:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:8080`

3. Use the application by:
   - Dragging and dropping files
   - Clicking "Select a file"
   - Entering a URL
   - For images, provide an OpenAI API key if not set in environment

### API Usage

Convert a file:
```bash
curl -X POST \
    -F "file=@your_file.pdf" \
    http://localhost:8080/convert
```

Convert from URL:
```bash
curl -X POST \
    -F "url=https://example.com/document.pdf" \
    http://localhost:8080/convert
```

Analyze image with OpenAI:
```bash
curl -X POST \
    -F "file=@image.jpg" \
    -F "api_key=your-openai-key" \
    http://localhost:8080/convert
```

## Development

The application is built with:
- Flask (Python web framework)
- MarkItDown library for conversions
- OpenAI GPT-4o for image analysis
- Modern JavaScript (ES6+)
- CSS3 with custom properties

Project structure:
```
markitdown-converter/
├── app.py              # Flask application
├── static/
│   ├── style.css      # Styles
│   ├── script.js      # Frontend logic
│   └── icons/         # Application icons
├── templates/
│   └── index.html     # Main template
└── pyproject.toml     # Project configuration
```

## Requirements

- Python 3.12 or higher
- Flask 3.1.0 or higher
- MarkItDown 0.0.1a2 or higher
- OpenAI API key (for image analysis)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [MarkItDown](https://github.com/path/to/markitdown)
- Uses OpenAI's GPT-4o for image analysis
- Icons from Font Awesome
