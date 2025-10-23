# Text Processing Scripts

Scripts for manipulating, converting, and processing text documents and files.

## Scripts

### pdf_merger.py
**Purpose**: Merge multiple PDF files into a single document.

**Features**:
- Select multiple PDF files through file dialog
- Preserves document order based on selection
- Progress feedback during merging process
- Error handling for corrupted or protected PDFs

**Usage**: `python pdf_merger.py`
**Dependencies**: `pip install PyPDF2`

---

### text_extractor.py
**Purpose**: Extract text from various document types and images using OCR.

**Features**:
- Supports PDF, Word documents, text files, and images
- OCR capability for extracting text from images
- Graceful fallback when optional dependencies are missing
- Save extracted text to file or display in console

**Usage**: `python text_extractor.py`
**Dependencies**: 
- `pip install PyPDF2 python-docx pillow pytesseract`
- Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract

**Supported Formats**:
- **PDF**: .pdf
- **Word**: .docx, .doc
- **Text**: .txt
- **Images**: .png, .jpg, .jpeg, .tiff, .bmp

---

### markdown_converter.py
**Purpose**: Convert between Markdown and HTML formats.

**Features**:
- Bidirectional conversion (Markdown ↔ HTML)
- Enhanced conversion with markdown2 library (optional)
- Basic built-in conversion when external library unavailable
- Auto-detection of input format based on file extension

**Usage**: `python markdown_converter.py`
**Dependencies**: `pip install markdown2` (optional, has built-in fallback)

**Features Supported**:
- Headers (H1, H2, H3)
- Bold and italic text
- Links and code blocks
- Basic HTML tag removal for HTML→Markdown

---

### log_parser.py
**Purpose**: Parse and analyze log files for patterns, errors, and statistics.

**Features**:
- Configurable regex patterns for different log formats
- Extract errors, warnings, timestamps, IP addresses
- HTTP status code analysis
- Generate detailed reports with statistics
- Time range analysis from log timestamps

**Usage**: `python log_parser.py`
**Dependencies**: Built-in modules only

**Analysis Features**:
- **Error Detection**: Finds lines containing error keywords
- **Warning Detection**: Identifies warning messages
- **Timestamp Extraction**: Extracts and analyzes time ranges
- **IP Address Collection**: Finds unique IP addresses
- **HTTP Status Codes**: Counts different response codes
- **Summary Statistics**: Line counts, time ranges, unique IPs

## Requirements

Most scripts use built-in Python modules when possible. Optional dependencies enhance functionality but are not required for basic operation.

## Usage Tips

- **Text Extraction**: For best OCR results, use high-quality, high-contrast images
- **PDF Merging**: Ensure PDFs are not password-protected
- **Log Parsing**: Works best with standard log formats (Apache, Nginx, etc.)
- **Markdown Conversion**: Install markdown2 for better HTML conversion quality