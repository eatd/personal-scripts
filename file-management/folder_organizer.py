# Built-in modules only
import shutil
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

# File type mappings
FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"],
    "Documents": [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    ],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [
        ".py",
        ".js",
        ".html",
        ".css",
        ".cpp",
        ".c",
        ".java",
        ".php",
        ".rb",
        ".go",
    ],
    "Executables": [".exe", ".msi", ".dmg", ".deb", ".rpm", ".appimage"],
}


def get_file_category(file_extension):
    """Determine file category based on extension."""
    file_extension = file_extension.lower()
    for category, extensions in FILE_TYPES.items():
        if file_extension in extensions:
            return category
    return "Other"


def organize_folder(source_dir, create_subfolders=True):
    """Organize files in a folder by type."""
    source_path = Path(source_dir)
    organized_count = 0
    errors = []

    for file_path in source_path.iterdir():
        if file_path.is_file():
            category = get_file_category(file_path.suffix)

            if create_subfolders:
                # Create category subfolder
                category_dir = source_path / category
                category_dir.mkdir(exist_ok=True)
                destination = category_dir / file_path.name
            else:
                # Just add prefix to filename
                new_name = f"{category}_{file_path.name}"
                destination = source_path / new_name

            try:
                # Check if destination already exists
                if destination.exists():
                    # Add number suffix if file already exists
                    counter = 1
                    while destination.exists():
                        stem = destination.stem
                        suffix = destination.suffix
                        destination = destination.parent / f"{stem}_{counter}{suffix}"
                        counter += 1

                shutil.move(str(file_path), str(destination))
                print(
                    f"Moved: {file_path.name} -> {destination.relative_to(source_path)}"
                )
                organized_count += 1

            except OSError as e:
                errors.append(f"Error moving {file_path.name}: {e}")

    return organized_count, errors


def main():
    root = Tk()
    root.withdraw()

    # Select directory to organize
    directory = filedialog.askdirectory(title="Select directory to organize")
    if not directory:
        return

    # Ask organization method
    use_subfolders = messagebox.askyesno(
        "Organization Method",
        "How would you like to organize?\n\n"
        "Yes: Create subfolders (Images/, Documents/, etc.)\n"
        "No: Add prefixes (Images_photo.jpg, etc.)",
    )

    # Confirm action
    if not messagebox.askyesno(
        "Confirm",
        f"Organize files in: {directory}\n"
        f"Method: {'Subfolders' if use_subfolders else 'Prefixes'}",
    ):
        return

    print(f"Organizing files in: {directory}")
    organized_count, errors = organize_folder(directory, use_subfolders)

    result_msg = f"Organized {organized_count} files."
    if errors:
        result_msg += f"\n{len(errors)} errors occurred."
        for error in errors:
            print(error)

    print(result_msg)
    messagebox.showinfo("Complete", result_msg)


if __name__ == "__main__":
    main()
