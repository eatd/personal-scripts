# Built-in modules only
import hashlib
import os
from collections import defaultdict
from pathlib import Path
from tkinter import Tk, filedialog, messagebox


def calculate_file_hash(file_path, chunk_size=8192):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (IOError, OSError):
        return None


def find_duplicates(directory):
    """Find duplicate files in a directory."""
    file_hashes = defaultdict(list)

    print("Scanning files...")
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                file_hashes[file_hash].append(file_path)

    # Return only hashes with more than one file
    return {
        hash_val: paths for hash_val, paths in file_hashes.items() if len(paths) > 1
    }


def main():
    root = Tk()
    root.withdraw()

    directory = filedialog.askdirectory(title="Select directory to scan for duplicates")
    if not directory:
        return

    print(f"Scanning for duplicates in: {directory}")
    duplicates = find_duplicates(directory)

    if not duplicates:
        print("No duplicates found!")
        messagebox.showinfo("Result", "No duplicate files found!")
        return

    print(f"\nFound {len(duplicates)} sets of duplicate files:")
    for hash_val, paths in duplicates.items():
        print(f"\nDuplicate set (hash: {hash_val[:8]}...):")
        for path in paths:
            print(f"  - {path}")

    # Ask if user wants to delete duplicates (keeping the first one)
    response = messagebox.askyesno(
        "Delete Duplicates",
        f"Found {len(duplicates)} sets of duplicates. "
        "Delete duplicates (keeping first file in each set)?",
    )

    if response:
        deleted_count = 0
        for paths in duplicates.values():
            # Keep first file, delete the rest
            for path in paths[1:]:
                try:
                    os.remove(path)
                    print(f"Deleted: {path}")
                    deleted_count += 1
                except OSError as e:
                    print(f"Error deleting {path}: {e}")

        print(f"\nDeleted {deleted_count} duplicate files.")
        messagebox.showinfo("Complete", f"Deleted {deleted_count} duplicate files.")


if __name__ == "__main__":
    main()
