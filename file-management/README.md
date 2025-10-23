# File Management Scripts

Scripts for organizing, analyzing, and managing files and directories.

## Scripts

### duplicate_finder.py
**Purpose**: Find and optionally remove duplicate files based on MD5 hash comparison.

**Features**:
- Scans entire directory tree recursively
- Uses MD5 hashing for accurate duplicate detection
- Interactive deletion with confirmation dialogs
- Preserves one copy of each duplicate set

**Usage**: `python duplicate_finder.py`
**Dependencies**: Built-in modules only

---

### batch_rename.py
**Purpose**: Rename multiple files using regex patterns.

**Features**:
- Regex pattern matching and replacement
- Optional file extension filtering
- Interactive preview before applying changes
- Handles naming conflicts automatically

**Usage**: `python batch_rename.py`
**Dependencies**: Built-in modules only

**Examples**:
- Remove spaces: Pattern `\s+` → Replacement `_`
- Remove prefixes: Pattern `^IMG_` → Replacement ``
- Add prefixes: Pattern `^` → Replacement `Photo_`

---

### folder_organizer.py
**Purpose**: Organize files by type into folders or with prefixes.

**Features**:
- Categorizes files by extension (Images, Documents, Videos, etc.)
- Two organization modes: subfolders or filename prefixes
- Handles naming conflicts with automatic numbering
- Supports 7 main categories plus "Other"

**Usage**: `python folder_organizer.py`
**Dependencies**: Built-in modules only

**Categories**:
- **Images**: jpg, png, gif, bmp, tiff, svg, webp
- **Documents**: pdf, doc, docx, txt, rtf, odt, xls, xlsx, ppt, pptx
- **Videos**: mp4, avi, mkv, mov, wmv, flv, webm, m4v
- **Audio**: mp3, wav, flac, aac, ogg, wma, m4a
- **Archives**: zip, rar, 7z, tar, gz, bz2
- **Code**: py, js, html, css, cpp, c, java, php, rb, go
- **Executables**: exe, msi, dmg, deb, rpm, appimage

---

### file_size_analyzer.py
**Purpose**: Analyze directory structure and identify largest files and folders.

**Features**:
- Recursive directory scanning with progress indication
- Human-readable size formatting (B, KB, MB, GB, TB)
- Top 20 largest files and folders
- Total size and file count statistics
- Relative path display for easy navigation

**Usage**: `python file_size_analyzer.py`
**Dependencies**: Built-in modules only

## Safety Features

- **Confirmation dialogs**: All destructive operations require user confirmation
- **Error handling**: Graceful handling of file access errors and permissions
- **Conflict resolution**: Automatic handling of naming conflicts
- **Backup recommendations**: Always backup important data before running batch operations