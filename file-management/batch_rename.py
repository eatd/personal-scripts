# Built-in modules only
import re
from pathlib import Path
from tkinter import Tk, filedialog, messagebox, simpledialog


def batch_rename_files(directory, pattern, replacement, file_extension=None):
    """Batch rename files using regex pattern."""
    renamed_count = 0
    errors = []

    for file_path in Path(directory).iterdir():
        if file_path.is_file():
            # Filter by extension if specified
            if file_extension and not file_path.suffix.lower().endswith(
                file_extension.lower()
            ):
                continue

            old_name = file_path.name
            new_name = re.sub(pattern, replacement, old_name)

            if new_name != old_name:
                new_path = file_path.parent / new_name
                try:
                    file_path.rename(new_path)
                    print(f"Renamed: {old_name} -> {new_name}")
                    renamed_count += 1
                except OSError as e:
                    errors.append(f"Error renaming {old_name}: {e}")

    return renamed_count, errors


def main():
    root = Tk()
    root.withdraw()

    # Select directory
    directory = filedialog.askdirectory(title="Select directory with files to rename")
    if not directory:
        return

    # Get rename pattern
    pattern = simpledialog.askstring(
        "Pattern",
        "Enter regex pattern to match:\n"
        "Examples:\n"
        "- '\\s+' (replace spaces)\n"
        "- '^IMG_' (remove IMG_ prefix)\n"
        "- '\\d{4}' (match 4 digits)",
    )
    if not pattern:
        return

    # Get replacement
    replacement = simpledialog.askstring(
        "Replacement",
        "Enter replacement text:\n"
        "Examples:\n"
        "- '_' (replace with underscore)\n"
        "- '' (remove matched text)\n"
        "- 'Photo_' (replace with Photo_)",
    )
    if replacement is None:  # Allow empty string
        return

    # Get file extension filter (optional)
    extension = simpledialog.askstring(
        "Extension Filter",
        "Filter by extension (optional):\n"
        "Examples: .jpg, .txt, .pdf\n"
        "Leave empty for all files",
    )

    # Confirm action
    if not messagebox.askyesno(
        "Confirm",
        f"Rename files in {directory}\n"
        f"Pattern: {pattern}\n"
        f"Replacement: {replacement}\n"
        f"Extension: {extension or 'All files'}",
    ):
        return

    renamed_count, errors = batch_rename_files(
        directory, pattern, replacement, extension
    )

    result_msg = f"Renamed {renamed_count} files."
    if errors:
        result_msg += f"\n{len(errors)} errors occurred."
        for error in errors:
            print(error)

    print(result_msg)
    messagebox.showinfo("Complete", result_msg)


if __name__ == "__main__":
    main()
