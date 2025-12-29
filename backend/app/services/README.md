# AI Services Module

This directory contains reusable AI and processing services for the FastAPI application.

## 📁 Structure

```
services/
├── __init__.py           # Exports all service functions
├── ocr_tools.py          # OCR and document processing utilities
└── README.md             # This file
```

## 🎯 Purpose

The services module provides a centralized location for:
- **OCR (Optical Character Recognition)** services
- **Document conversion** utilities (Excel to PDF, PDF to images)
- **Image processing** tools
- **AI/ML integration** services (future)
- **External API** integrations (future)

## 📦 Current Services

### OCR Tools (`ocr_tools.py`)

Document processing and OCR utilities for comparing Excel and PDF files.

**Functions:**

1. **`convert_excel_to_pdf(excel_path: Path) -> Path`**
   - Converts Excel files to PDF format
   - Libraries: openpyxl + reportlab, or libreoffice subprocess
   - Returns: Path to generated PDF

2. **`convert_pdf_to_images(pdf_path: Path, dpi: int = 200) -> list[Image.Image]`**
   - Converts PDF pages to images for OCR processing
   - Libraries: pdf2image (requires poppler)
   - Returns: List of PIL Image objects

3. **`encode_image(image: Image.Image) -> bytes`**
   - Converts PIL Image to bytes (PNG format)
   - Use for storing or transmitting images

4. **`base64_encode_image(image: Image.Image) -> str`**
   - Converts PIL Image to base64 string
   - Use for JSON embedding or API transmission

5. **`extract_ocr_texts(images: list[Image.Image]) -> list[dict[str, Any]]`**
   - Extracts text from images using OCR
   - Libraries: pytesseract (requires tesseract installation)
   - Returns: List of OCR results with text, confidence, and metadata

6. **`compare_ocr_texts(excel_texts, pdf_texts) -> dict[str, Any]`**
   - Compares OCR extracted texts from two documents
   - Returns similarity score and differences

## 🚀 Usage Example

```python
from app.services.ocr_tools import (
    convert_excel_to_pdf,
    convert_pdf_to_images,
    extract_ocr_texts,
    compare_ocr_texts
)

# Convert Excel to PDF
excel_pdf = convert_excel_to_pdf(Path("invoice.xlsx"))

# Convert PDFs to images
excel_images = convert_pdf_to_images(excel_pdf)
pdf_images = convert_pdf_to_images(Path("invoice.pdf"))

# Extract text via OCR
excel_texts = extract_ocr_texts(excel_images)
pdf_texts = extract_ocr_texts(pdf_images)

# Compare texts
comparison = compare_ocr_texts(excel_texts, pdf_texts)
print(f"Similarity: {comparison['similarity_score']}%")
```

## 📚 Dependencies

### Required System Packages

```bash
# For pdf2image
sudo apt-get install poppler-utils  # Ubuntu/Debian
brew install poppler                 # macOS

# For pytesseract OCR
sudo apt-get install tesseract-ocr   # Ubuntu/Debian
brew install tesseract               # macOS
```

### Python Packages

```bash
pip install pdf2image       # PDF to image conversion
pip install pytesseract     # OCR text extraction
pip install Pillow          # Image processing
pip install openpyxl        # Excel file handling
pip install reportlab       # PDF generation (for Excel to PDF)
```

### Alternative Libraries

If the default libraries don't work in your environment:

**Excel to PDF:**
- `win32com` (Windows only)
- `libreoffice` subprocess (cross-platform, requires LibreOffice installed)
- `xlsxwriter` + custom PDF generation

**PDF to Images:**
- `PyMuPDF` (fitz) - faster, no system dependencies
- `wand` (ImageMagick wrapper)

**OCR:**
- `EasyOCR` - deep learning based, more accurate
- `Google Cloud Vision API` - cloud-based, best accuracy
- `AWS Textract` - cloud-based, good for forms
- `Azure Computer Vision` - cloud-based

## 🔧 Adding New Services

### Step 1: Create Service Module

Create a new file in `services/` directory:

```python
# services/nlp_tools.py
"""
NLP (Natural Language Processing) tools for text analysis.
"""

from app.core.logging import get_logger

logger = get_logger(__name__)

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of text."""
    # Implementation
    pass
```

### Step 2: Export from `__init__.py`

```python
# services/__init__.py
from app.services.nlp_tools import analyze_sentiment

__all__ = [
    # ... existing exports
    "analyze_sentiment",
]
```

### Step 3: Use in Routes

```python
# api/routes/your_route.py
from app.services import analyze_sentiment

result = analyze_sentiment(text)
```

## 🎨 Service Design Guidelines

1. **Modular:** Each service should be self-contained
2. **Reusable:** Functions should work across different contexts
3. **Documented:** Include docstrings with args, returns, and examples
4. **Logged:** Use logger for important steps and errors
5. **Typed:** Use type hints for all parameters and returns
6. **Tested:** Add unit tests in `tests/services/`

## 🌟 Future Services (Planned)

- `nlp_tools.py` - Text analysis, entity extraction, summarization
- `vision_tools.py` - Image analysis, object detection
- `translation_tools.py` - Multi-language translation services
- `generation_tools.py` - AI content generation (GPT, etc.)
- `embedding_tools.py` - Text/image embeddings for similarity search

## 📝 Contributing

When adding new AI services:

1. Create a new module file in `services/`
2. Follow the existing code style and documentation patterns
3. Add comprehensive docstrings
4. Include TODO markers for unimplemented features
5. Export functions in `__init__.py`
6. Update this README with your new service
7. Add unit tests

## 🔗 Related Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pdf2image Docs](https://github.com/Belval/pdf2image)
- [pytesseract Docs](https://github.com/madmaze/pytesseract)
- [Pillow Docs](https://pillow.readthedocs.io/)

---

**Maintainers:** AI Engineering Team  
**Last Updated:** 2025-12-29
