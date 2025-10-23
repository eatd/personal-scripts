# Personal Scripts Collection

A comprehensive collection of small personal utility scripts for various everyday tasks, organized by category.

## 📁 Script Categories

### 🗂️ File Management (`file-management/`)
- **duplicate_finder.py** - Find and remove duplicate files using hash comparison
- **batch_rename.py** - Rename multiple files using regex patterns
- **folder_organizer.py** - Organize files by type into folders or with prefixes
- **file_size_analyzer.py** - Analyze directory structure and find largest files

### 📝 Text Processing (`text-processing/`)
- **pdf_merger.py** - Merge multiple PDF files into one
- **text_extractor.py** - Extract text from PDFs, Word docs, or images (OCR)
- **markdown_converter.py** - Convert between Markdown and HTML
- **log_parser.py** - Parse and analyze log files for patterns

### 🌐 Web & Data (`web-data/`)
- **qr_generator.py** - Generate QR codes from text/URLs
- **url_shortener.py** - Create shortened URLs using service APIs
- **weather_checker.py** - Get current weather for any location

### 🖼️ Image Processing (`image-processing/`)
- **gif_to_frames.py** - Extract individual frames from GIF files as PNG images

## 🚀 Quick Start

1. **Navigate to category**: `cd <category-name>`
2. **Install dependencies**: Check script comments for `pip install` requirements
3. **Run script**: `python script_name.py`

## 📋 Requirements

Each script may have its own dependencies. Check the comments at the top of each script for installation instructions. Most scripts use built-in Python modules when possible.

### Common Dependencies
- **PIL (Pillow)** - Image processing
- **PyPDF2** - PDF manipulation
- **requests** - Web requests
- **qrcode** - QR code generation
- **tkinter** - GUI dialogs (usually built-in)

## 🔧 Usage Examples

### File Management
```bash
cd file-management
python duplicate_finder.py      # Find duplicate files
python folder_organizer.py      # Organize downloads folder
python batch_rename.py          # Rename files with patterns
python file_size_analyzer.py    # Analyze disk usage
```

### Text Processing
```bash
cd text-processing
python pdf_merger.py            # Merge PDFs
python text_extractor.py        # Extract text from documents
python markdown_converter.py    # Convert Markdown ↔ HTML
python log_parser.py            # Analyze log files
```

### Web & Data
```bash
cd web-data
python qr_generator.py          # Generate QR codes
python url_shortener.py         # Shorten long URLs
python weather_checker.py       # Check weather
```

### Image Processing
```bash
cd image-processing
python gif_to_frames.py         # Extract GIF frames
```

## 🛡️ Safety Features

- **Confirmation dialogs** for destructive operations
- **Backup recommendations** before batch operations
- **Error handling** with informative messages
- **Preview modes** where applicable

## 🤝 Contributing

These are personal utility scripts, but feel free to:
- Use them as inspiration for your own projects
- Suggest improvements or additional scripts
- Report bugs or issues

## 📜 License

Personal use scripts - use at your own discretion and always backup important data before running batch operations.