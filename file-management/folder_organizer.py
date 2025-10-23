#!/usr/bin/env python3
"""
Smart folder organization tool with customizable rules and safety features.
Organizes files by type, date, size, or custom patterns with undo capability.

Enterprise-grade file management with conflict resolution and comprehensive logging.
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple


class FolderOrganizer:
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path("organizer_config.json")
        self.operation_log = Path("organize_operations.json")
        self.operations = []
        self.stats = {
            "files_processed": 0,
            "files_moved": 0,
            "folders_created": 0,
            "conflicts_resolved": 0,
            "errors": 0,
        }

        # Default file type mappings
        self.default_mappings = {
            "Images": [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".tiff",
                ".svg",
                ".webp",
                ".ico",
                ".raw",
            ],
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
                ".csv",
            ],
            "Videos": [
                ".mp4",
                ".avi",
                ".mkv",
                ".mov",
                ".wmv",
                ".flv",
                ".webm",
                ".m4v",
                ".mpg",
                ".mpeg",
            ],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".lzma"],
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
                ".rs",
                ".ts",
            ],
            "Executables": [
                ".exe",
                ".msi",
                ".dmg",
                ".deb",
                ".rpm",
                ".appimage",
                ".pkg",
            ],
            "Data": [".json", ".xml", ".yaml", ".yml", ".sql", ".db", ".sqlite"],
            "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
            "3D": [".obj", ".fbx", ".dae", ".3ds", ".blend", ".stl"],
        }

        self.load_config()

    def load_config(self):
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.file_mappings = config.get(
                        "file_mappings", self.default_mappings
                    )
                    self.naming_patterns = config.get("naming_patterns", {})
                    self.exclude_patterns = config.get("exclude_patterns", [])
            except (json.JSONDecodeError, IOError):
                self.file_mappings = self.default_mappings
                self.naming_patterns = {}
                self.exclude_patterns = []
        else:
            self.file_mappings = self.default_mappings
            self.naming_patterns = {}
            self.exclude_patterns = []

    def save_config(self):
        """Save current configuration to file."""
        config = {
            "file_mappings": self.file_mappings,
            "naming_patterns": self.naming_patterns,
            "exclude_patterns": self.exclude_patterns,
        }

        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def get_file_category(self, file_path: Path) -> str:
        """Determine file category based on extension."""
        extension = file_path.suffix.lower()

        for category, extensions in self.file_mappings.items():
            if extension in extensions:
                return category

        return "Other"

    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from organization."""
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                return True
        return False

    def organize_by_type(
        self, source_dir: Path, target_dir: Optional[Path] = None
    ) -> List[Tuple[Path, Path]]:
        """Organize files by their type/extension."""
        target_dir = target_dir or source_dir
        operations = []

        for file_path in source_dir.iterdir():
            if not file_path.is_file() or self.should_exclude_file(file_path):
                continue

            category = self.get_file_category(file_path)
            category_dir = target_dir / category
            new_path = category_dir / file_path.name

            operations.append((file_path, new_path))

        return operations

    def organize_by_date(
        self,
        source_dir: Path,
        target_dir: Optional[Path] = None,
        date_format: str = "%Y-%m",
    ) -> List[Tuple[Path, Path]]:
        """Organize files by creation or modification date."""
        target_dir = target_dir or source_dir
        operations = []

        for file_path in source_dir.iterdir():
            if not file_path.is_file() or self.should_exclude_file(file_path):
                continue

            # Use modification time
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            date_folder = file_time.strftime(date_format)
            date_dir = target_dir / date_folder
            new_path = date_dir / file_path.name

            operations.append((file_path, new_path))

        return operations

    def organize_by_size(
        self, source_dir: Path, target_dir: Optional[Path] = None
    ) -> List[Tuple[Path, Path]]:
        """Organize files by size ranges."""
        target_dir = target_dir or source_dir
        operations = []

        size_ranges = {
            "Tiny": (0, 1024 * 10),  # < 10KB
            "Small": (1024 * 10, 1024 * 1024),  # 10KB - 1MB
            "Medium": (1024 * 1024, 1024 * 1024 * 10),  # 1MB - 10MB
            "Large": (1024 * 1024 * 10, 1024 * 1024 * 100),  # 10MB - 100MB
            "Huge": (1024 * 1024 * 100, float("inf")),  # > 100MB
        }

        for file_path in source_dir.iterdir():
            if not file_path.is_file() or self.should_exclude_file(file_path):
                continue

            file_size = file_path.stat().st_size

            for size_category, (min_size, max_size) in size_ranges.items():
                if min_size <= file_size < max_size:
                    size_dir = target_dir / size_category
                    new_path = size_dir / file_path.name
                    operations.append((file_path, new_path))
                    break

        return operations

    def organize_by_age(
        self,
        source_dir: Path,
        target_dir: Optional[Path] = None,
        days_threshold: int = 30,
    ) -> List[Tuple[Path, Path]]:
        """Organize files by age (recent vs old)."""
        target_dir = target_dir or source_dir
        operations = []
        cutoff_date = datetime.now() - timedelta(days=days_threshold)

        for file_path in source_dir.iterdir():
            if not file_path.is_file() or self.should_exclude_file(file_path):
                continue

            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)

            if file_time > cutoff_date:
                age_dir = target_dir / "Recent"
            else:
                age_dir = target_dir / "Old"

            new_path = age_dir / file_path.name
            operations.append((file_path, new_path))

        return operations

    def resolve_conflicts(
        self, operations: List[Tuple[Path, Path]], strategy: str = "rename"
    ) -> List[Tuple[Path, Path]]:
        """Resolve naming conflicts in move operations."""
        resolved_operations = []
        path_counts = {}

        for old_path, new_path in operations:
            if new_path.exists() and new_path != old_path:
                if strategy == "rename":
                    # Add counter to filename
                    counter = path_counts.get(str(new_path), 0) + 1
                    path_counts[str(new_path)] = counter

                    stem = new_path.stem
                    suffix = new_path.suffix
                    parent = new_path.parent

                    new_name = f"{stem}_{counter:03d}{suffix}"
                    new_path = parent / new_name

                elif strategy == "skip":
                    continue  # Skip this file
                elif strategy == "overwrite":
                    pass  # Keep original new_path (will overwrite)

            resolved_operations.append((old_path, new_path))

        return resolved_operations

    def execute_operations(
        self, operations: List[Tuple[Path, Path]], dry_run: bool = True
    ) -> int:
        """Execute file organization operations."""
        if dry_run:
            print("🧪 DRY RUN - No files will be moved")
        else:
            print("📁 EXECUTING ORGANIZATION")

        successful = 0
        timestamp = datetime.now().isoformat()
        created_dirs = set()

        for old_path, new_path in operations:
            self.stats["files_processed"] += 1

            try:
                # Create target directory if needed
                if not dry_run and not new_path.parent.exists():
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    if str(new_path.parent) not in created_dirs:
                        created_dirs.add(str(new_path.parent))
                        self.stats["folders_created"] += 1
                        print(f"   📂 Created directory: {new_path.parent}")

                if dry_run:
                    print(f"   Would move: {old_path.name} → {new_path}")
                else:
                    shutil.move(str(old_path), str(new_path))
                    print(f"   ✅ Moved: {old_path.name} → {new_path}")

                    # Log operation
                    self.operations.append(
                        {
                            "timestamp": timestamp,
                            "old_path": str(old_path),
                            "new_path": str(new_path),
                            "operation_type": "move",
                        }
                    )

                successful += 1
                self.stats["files_moved"] += 1

            except (OSError, PermissionError, shutil.Error) as e:
                print(f"   ❌ Error moving {old_path.name}: {e}")
                self.stats["errors"] += 1

        if not dry_run and self.operations:
            self.save_operation_log()

        action = "Would move" if dry_run else "Moved"
        print(f"\n📊 {action} {successful}/{len(operations)} files")

        if self.stats["folders_created"] > 0:
            print(f"📂 Created {self.stats['folders_created']} directories")

        if self.stats["errors"] > 0:
            print(f"⚠️  {self.stats['errors']} errors encountered")

        return successful

    def save_operation_log(self):
        """Save operations to log file."""
        all_operations = []

        if self.operation_log.exists():
            try:
                with open(self.operation_log, "r") as f:
                    all_operations = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        all_operations.extend(self.operations)

        with open(self.operation_log, "w") as f:
            json.dump(all_operations, f, indent=2, default=str)

    def undo_last_operation(self) -> int:
        """Undo the last organization operation."""
        if not self.operation_log.exists():
            print("❌ No operations to undo")
            return 0

        try:
            with open(self.operation_log, "r") as f:
                operations = json.load(f)
        except (json.JSONDecodeError, IOError):
            print("❌ Could not read operation log")
            return 0

        if not operations:
            print("❌ No operations to undo")
            return 0

        # Get the last timestamp
        last_timestamp = operations[-1]["timestamp"]
        last_ops = [op for op in operations if op["timestamp"] == last_timestamp]

        print(f"🔄 Undoing {len(last_ops)} operations from {last_timestamp}")

        successful = 0
        for op in reversed(last_ops):  # Reverse order for safety
            try:
                current_path = Path(op["new_path"])
                original_path = Path(op["old_path"])

                if current_path.exists():
                    # Ensure original directory exists
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(current_path), str(original_path))
                    print(f"   ✅ Restored: {current_path.name} → {original_path}")
                    successful += 1
                else:
                    print(f"   ⚠️  File not found: {current_path}")

            except (OSError, PermissionError, shutil.Error) as e:
                print(f"   ❌ Error restoring {op['new_path']}: {e}")

        # Remove undone operations from log
        remaining_ops = [op for op in operations if op["timestamp"] != last_timestamp]
        with open(self.operation_log, "w") as f:
            json.dump(remaining_ops, f, indent=2, default=str)

        print(f"📊 Restored {successful}/{len(last_ops)} files")
        return successful

    def print_statistics(self):
        """Print organization statistics."""
        print("\n📈 ORGANIZATION STATISTICS")
        print(f"Files processed: {self.stats['files_processed']:,}")
        print(f"Files moved: {self.stats['files_moved']:,}")
        print(f"Folders created: {self.stats['folders_created']:,}")
        print(f"Conflicts resolved: {self.stats['conflicts_resolved']:,}")
        if self.stats["errors"] > 0:
            print(f"Errors: {self.stats['errors']:,}")


def main():
    parser = argparse.ArgumentParser(
        description="Smart folder organization with customizable rules and safety features"
    )

    subparsers = parser.add_subparsers(dest="command", help="Organization methods")

    # Organize by type
    type_parser = subparsers.add_parser("type", help="Organize files by type/extension")
    type_parser.add_argument("source", type=Path, help="Source directory to organize")
    type_parser.add_argument(
        "--target", type=Path, help="Target directory (default: source)"
    )

    # Organize by date
    date_parser = subparsers.add_parser("date", help="Organize files by date")
    date_parser.add_argument("source", type=Path, help="Source directory to organize")
    date_parser.add_argument(
        "--target", type=Path, help="Target directory (default: source)"
    )
    date_parser.add_argument(
        "--format", default="%Y-%m", help="Date format for folders (default: %%Y-%%m)"
    )

    # Organize by size
    size_parser = subparsers.add_parser("size", help="Organize files by size ranges")
    size_parser.add_argument("source", type=Path, help="Source directory to organize")
    size_parser.add_argument(
        "--target", type=Path, help="Target directory (default: source)"
    )

    # Organize by age
    age_parser = subparsers.add_parser(
        "age", help="Organize files by age (recent vs old)"
    )
    age_parser.add_argument("source", type=Path, help="Source directory to organize")
    age_parser.add_argument(
        "--target", type=Path, help="Target directory (default: source)"
    )
    age_parser.add_argument(
        "--days", type=int, default=30, help="Days threshold for recent files"
    )

    # Configuration management
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument(
        "--show", action="store_true", help="Show current configuration"
    )
    config_parser.add_argument(
        "--reset", action="store_true", help="Reset to default configuration"
    )

    # Undo operation
    subparsers.add_parser("undo", help="Undo last organization operation")

    # Common arguments
    for p in [type_parser, date_parser, size_parser, age_parser]:
        p.add_argument(
            "--recursive", "-r", action="store_true", help="Process subdirectories"
        )
        p.add_argument(
            "--dry-run", action="store_true", help="Preview changes without executing"
        )
        p.add_argument(
            "--execute", action="store_true", help="Execute the organization"
        )
        p.add_argument(
            "--conflict",
            choices=["rename", "skip", "overwrite"],
            default="rename",
            help="Conflict resolution strategy",
        )
        p.add_argument("--config", type=Path, help="Configuration file location")
        p.add_argument("--exclude", action="append", help="Exclude patterns (glob)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize organizer
    organizer = FolderOrganizer(getattr(args, "config", None))

    # Add exclude patterns from command line
    if hasattr(args, "exclude") and args.exclude:
        organizer.exclude_patterns.extend(args.exclude)

    # Handle config command
    if args.command == "config":
        if args.show:
            print("📋 Current Configuration:")
            print(
                json.dumps(
                    {
                        "file_mappings": organizer.file_mappings,
                        "naming_patterns": organizer.naming_patterns,
                        "exclude_patterns": organizer.exclude_patterns,
                    },
                    indent=2,
                )
            )
        elif args.reset:
            organizer.file_mappings = organizer.default_mappings
            organizer.naming_patterns = {}
            organizer.exclude_patterns = []
            organizer.save_config()
            print("✅ Configuration reset to defaults")
        return

    # Handle undo command
    if args.command == "undo":
        organizer.undo_last_operation()
        return

    # Validate source directory
    if not args.source.exists():
        print(f"❌ Source directory not found: {args.source}")
        sys.exit(1)

    if not args.source.is_dir():
        print(f"❌ Source is not a directory: {args.source}")
        sys.exit(1)

    # Get files to organize
    if args.recursive:
        files = list(args.source.rglob("*"))
        files = [f for f in files if f.is_file()]
    else:
        files = [f for f in args.source.iterdir() if f.is_file()]

    if not files:
        print(f"❌ No files found in {args.source}")
        sys.exit(1)

    print(f"📁 Found {len(files)} files to organize")

    # Generate operations based on command
    operations = []

    if args.command == "type":
        operations = organizer.organize_by_type(args.source, args.target)
    elif args.command == "date":
        operations = organizer.organize_by_date(args.source, args.target, args.format)
    elif args.command == "size":
        operations = organizer.organize_by_size(args.source, args.target)
    elif args.command == "age":
        operations = organizer.organize_by_age(args.source, args.target, args.days)

    if not operations:
        print("✅ No files need organizing")
        sys.exit(0)

    # Resolve conflicts
    operations = organizer.resolve_conflicts(operations, args.conflict)

    # Execute operations
    dry_run = args.dry_run or not args.execute
    if not dry_run and not args.execute:
        print("⚠️  Use --execute to perform the organization or --dry-run to preview")
        sys.exit(1)

    organizer.execute_operations(operations, dry_run)

    if not dry_run:
        organizer.print_statistics()


if __name__ == "__main__":
    main()
