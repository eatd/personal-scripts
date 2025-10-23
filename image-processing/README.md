# Image Processing Scripts

Scripts for manipulating, converting, and processing images.

## Scripts

### gif_to_frames.py
**Description:** Extract individual frames from a GIF file and save them as PNG images.

**Dependencies:** 
```bash
pip install pillow
```

**Usage:** Run the script and select a GIF file through the file dialog. Frames will be saved in the same directory as the script with names like `frame_000.png`, `frame_001.png`, etc.

**Features:**
- Interactive file selection dialog
- Automatic frame numbering with zero-padding
- RGBA conversion for better quality
- Saves frames in the script's directory