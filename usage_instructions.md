# MarkItDown

The MarkItDown library is a utility tool for converting various files to Markdown (e.g., for indexing, text analysis, etc.)

It presently supports:

- PDF (.pdf)
- PowerPoint (.pptx)
- Word (.docx)
- Excel (.xlsx)
- Images (EXIF metadata, and OCR)
- Audio (EXIF metadata, and speech transcription)
- HTML (special handling of Wikipedia, etc.)
- Various other text-based formats (csv, json, xml, etc.)

## Installation

You can install markitdown using pip:

```bash
pip install markitdown
```

or from the source

```bash
pip install -e .
```

## Usage

The API is simple:

```python
from markitdown import MarkItDown

markitdown = MarkItDown()
result = markitdown.convert("test.xlsx")
print(result.text_content)
You can also configure markitdown to use Large Language Models to describe images. To do so you must provide mlm_client and mlm_model parameters to MarkItDown object, according to your specific client.

from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(mlm_client=client, mlm_model="gpt-4o")
result = md.convert("example.jpg")
print(result.text_content)
```
