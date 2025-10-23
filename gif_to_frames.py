# pip install pillow
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from PIL import Image, ImageSequence

# 1) Ask the user to pick a GIF file
root = Tk()
root.withdraw()  # hide the root window
gif_path = askopenfilename(title="Select a GIF", filetypes=[("GIF files", "*.gif")])

# 2) Where to save: the folder that contains this .py file
output_dir = Path(__file__).parent

# 3) Open the GIF and save each frame as a PNG
img = Image.open(gif_path)
for idx, frame in enumerate(ImageSequence.Iterator(img)):
    frame.convert("RGBA").save(
        output_dir / f"frame_{idx:03d}.png"
    )  # frame_000.png, frame_001.png, ...

print(f"Done! Saved frames to: {output_dir}")
