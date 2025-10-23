# Built-in modules only
import os
from pathlib import Path
from tkinter import Tk, filedialog, messagebox


def format_size(size_bytes):
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f} {size_names[i]}"


def analyze_directory(directory, max_files=20):
    """Analyze directory and return size information."""
    path = Path(directory)
    file_sizes = []
    folder_sizes = {}
    total_size = 0

    print("Analyzing directory structure...")

    # Analyze files
    for root, dirs, files in os.walk(path):
        root_path = Path(root)
        folder_size = 0

        for file in files:
            file_path = root_path / file
            try:
                size = file_path.stat().st_size
                file_sizes.append((file_path, size))
                folder_size += size
                total_size += size
            except (OSError, FileNotFoundError):
                continue

        if folder_size > 0:
            folder_sizes[root_path] = folder_size

    # Sort by size (largest first)
    file_sizes.sort(key=lambda x: x[1], reverse=True)
    folder_sizes = dict(sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True))

    return {
        "total_size": total_size,
        "largest_files": file_sizes[:max_files],
        "largest_folders": list(folder_sizes.items())[:max_files],
        "file_count": len(file_sizes),
    }


def main():
    root = Tk()
    root.withdraw()

    # Select directory to analyze
    directory = filedialog.askdirectory(title="Select directory to analyze")
    if not directory:
        return

    print(f"Analyzing directory: {directory}")
    print("This may take a while for large directories...\n")

    analysis = analyze_directory(directory)

    # Display results
    print("=" * 60)
    print("DIRECTORY ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Total Size: {format_size(analysis['total_size'])}")
    print(f"Total Files: {analysis['file_count']:,}")
    print()

    print("LARGEST FILES:")
    print("-" * 40)
    for i, (file_path, size) in enumerate(analysis["largest_files"], 1):
        try:
            relative_path = file_path.relative_to(directory)
        except ValueError:
            relative_path = file_path.name
        print(f"{i:2d}. {format_size(size):>10} - {relative_path}")

    print("\nLARGEST FOLDERS:")
    print("-" * 40)
    for i, (folder_path, size) in enumerate(analysis["largest_folders"], 1):
        try:
            relative_path = folder_path.relative_to(directory)
            if not relative_path.parts:  # Root directory
                relative_path = Path(".")
        except ValueError:
            relative_path = folder_path
        print(f"{i:2d}. {format_size(size):>10} - {relative_path}")

    # Show summary in dialog
    summary = (
        f"Analysis Complete!\n\n"
        f"Total Size: {format_size(analysis['total_size'])}\n"
        f"Total Files: {analysis['file_count']:,}\n\n"
        f"Check console for detailed breakdown."
    )

    messagebox.showinfo("Analysis Complete", summary)


if __name__ == "__main__":
    main()
