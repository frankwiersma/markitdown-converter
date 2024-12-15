# MarkItDown Converter

MarkItDown Converter is a web application that converts various document formats into Markdown. It supports files, URLs, and includes AI-powered image analysis capabilities.

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

3. Optional: Set environment variables:
```bash
export QUART_ENV=development  # or production
export OPENAI_API_KEY=your-api-key  # required for image analysis
```

## Usage

### Running the Application

For development:
```bash
# Using uvicorn (recommended)
uv run uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

For production:
```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --workers 4
```

### Web Interface

Open your browser and navigate to `http://localhost:8080`. You can:
- Drag and drop files
- Select files using the file dialog
- Convert content from URLs
- Use OpenAI for image analysis (API key required)

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
- Quart (async Python web framework)
- MarkItDown library for conversions
- OpenAI GPT-4o for image analysis
- Modern JavaScript (ES6+)
- CSS3 with custom properties

Project structure:
```
markitdown-converter/
├── app.py              # Quart application
├── config.py          # Configuration
├── static/
│   ├── style.css      # Styles
│   ├── script.js      # Frontend logic
│   └── icons/         # Application icons
└── templates/
    └── index.html     # Main template
```

## Requirements

- Python 3.12 or higher
- Dependencies listed in pyproject.toml

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [MarkItDown](https://github.com/path/to/markitdown)
- Uses OpenAI's GPT-4o for image analysis
- Icons from Font Awesome
