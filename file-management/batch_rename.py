#!/usr/bin/env python3
"""
Professional batch file renaming utility with pattern matching and safety features.
Supports various renaming operations with undo capability and validation.

Designed for large-scale file management with comprehensive error handling.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BatchRenamer:
    def __init__(self, operation_log: Optional[Path] = None):
        self.operation_log = operation_log or Path("rename_operations.json")
        self.operations = []
        self.stats = {"files_processed": 0, "successful_renames": 0, "errors": 0}

    def load_operation_log(self) -> List[Dict]:
        """Load previous operations for undo functionality."""
        if self.operation_log.exists():
            try:
                with open(self.operation_log, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_operation_log(self):
        """Save operations to log file."""
        all_operations = self.load_operation_log()
        all_operations.extend(self.operations)

        with open(self.operation_log, "w") as f:
            json.dump(all_operations, f, indent=2, default=str)

    def sequential_rename(
        self, files: List[Path], pattern: str, start: int = 1, zero_pad: int = 0
    ) -> List[Tuple[Path, Path]]:
        """Rename files with sequential numbering."""
        operations = []

        for i, file_path in enumerate(files):
            extension = file_path.suffix
            number = start + i

            # Apply zero padding if specified
            if zero_pad > 0:
                number_str = str(number).zfill(zero_pad)
            else:
                number_str = str(number)

            # Create new name using pattern
            new_name = pattern.format(
                n=number_str,
                name=file_path.stem,
                ext=extension[1:] if extension else "",
                date=datetime.now().strftime("%Y%m%d"),
                time=datetime.now().strftime("%H%M%S"),
            )

            new_path = file_path.parent / new_name
            operations.append((file_path, new_path))

        return operations

    def pattern_replace(
        self,
        files: List[Path],
        find: str,
        replace: str,
        use_regex: bool = False,
        ignore_case: bool = False,
    ) -> List[Tuple[Path, Path]]:
        """Replace text patterns in filenames."""
        operations = []

        for file_path in files:
            if use_regex:
                flags = re.IGNORECASE if ignore_case else 0
                new_name = re.sub(find, replace, file_path.name, flags=flags)
            else:
                if ignore_case:
                    # Case-insensitive replace
                    new_name = re.sub(
                        re.escape(find), replace, file_path.name, flags=re.IGNORECASE
                    )
                else:
                    new_name = file_path.name.replace(find, replace)

            if new_name != file_path.name:
                new_path = file_path.parent / new_name
                operations.append((file_path, new_path))

        return operations

    def case_change(self, files: List[Path], operation: str) -> List[Tuple[Path, Path]]:
        """Change case of filenames."""
        operations = []

        for file_path in files:
            stem = file_path.stem
            extension = file_path.suffix

            if operation == "upper":
                new_stem = stem.upper()
            elif operation == "lower":
                new_stem = stem.lower()
            elif operation == "title":
                new_stem = stem.title()
            elif operation == "capitalize":
                new_stem = stem.capitalize()
            elif operation == "snake":
                # Convert to snake_case
                new_stem = re.sub(r"(?<!^)(?=[A-Z])", "_", stem).lower()
            elif operation == "kebab":
                # Convert to kebab-case
                new_stem = re.sub(r"(?<!^)(?=[A-Z])", "-", stem).lower()
                new_stem = re.sub(r"[\s_]+", "-", new_stem)
            else:
                continue

            new_name = new_stem + extension
            if new_name != file_path.name:
                new_path = file_path.parent / new_name
                operations.append((file_path, new_path))

        return operations

    def add_prefix_suffix(
        self, files: List[Path], prefix: str = "", suffix: str = ""
    ) -> List[Tuple[Path, Path]]:
        """Add prefix or suffix to filenames."""
        operations = []

        for file_path in files:
            stem = file_path.stem
            extension = file_path.suffix

            new_stem = prefix + stem + suffix
            new_name = new_stem + extension

            if new_name != file_path.name:
                new_path = file_path.parent / new_name
                operations.append((file_path, new_path))

        return operations

    def sanitize_names(
        self, files: List[Path], replacement: str = "_"
    ) -> List[Tuple[Path, Path]]:
        """Sanitize filenames by removing invalid characters."""
        operations = []
        invalid_chars = r'<>:"|?*\/'

        for file_path in files:
            stem = file_path.stem
            extension = file_path.suffix

            # Replace invalid characters
            clean_stem = re.sub(f"[{re.escape(invalid_chars)}]", replacement, stem)

            # Remove multiple consecutive replacement characters
            clean_stem = re.sub(f"{re.escape(replacement)}+", replacement, clean_stem)

            # Remove leading/trailing replacement characters
            clean_stem = clean_stem.strip(replacement)

            new_name = clean_stem + extension
            if new_name != file_path.name and clean_stem:  # Don't create empty names
                new_path = file_path.parent / new_name
                operations.append((file_path, new_path))

        return operations

    def validate_operations(self, operations: List[Tuple[Path, Path]]) -> List[str]:
        """Validate rename operations and return list of issues."""
        issues = []
        target_paths = set()

        for old_path, new_path in operations:
            # Check if source file exists
            if not old_path.exists():
                issues.append(f"Source file not found: {old_path}")
                continue

            # Check for empty names
            if not new_path.name.strip():
                issues.append(f"Empty filename would be created from: {old_path.name}")
                continue

            # Check for duplicate target names
            if new_path in target_paths:
                issues.append(f"Duplicate target name: {new_path}")
            target_paths.add(new_path)

            # Check if target already exists
            if new_path.exists() and new_path != old_path:
                issues.append(f"Target already exists: {new_path}")

            # Check for invalid characters (Windows/cross-platform)
            invalid_chars = '<>:"|?*'
            if any(char in new_path.name for char in invalid_chars):
                issues.append(f"Invalid characters in filename: {new_path.name}")

            # Check filename length
            if len(new_path.name) > 255:
                issues.append(f"Filename too long: {new_path.name}")

        return issues

    def execute_operations(
        self, operations: List[Tuple[Path, Path]], dry_run: bool = True
    ) -> int:
        """Execute rename operations with comprehensive error handling."""
        if dry_run:
            print("🧪 DRY RUN - No files will be renamed")
        else:
            print("📝 EXECUTING RENAME OPERATIONS")

        successful = 0
        timestamp = datetime.now().isoformat()

        for old_path, new_path in operations:
            self.stats["files_processed"] += 1

            try:
                if dry_run:
                    print(f"   Would rename: {old_path.name} → {new_path.name}")
                else:
                    old_path.rename(new_path)
                    print(f"   ✅ Renamed: {old_path.name} → {new_path.name}")

                    # Log operation for undo
                    self.operations.append(
                        {
                            "timestamp": timestamp,
                            "old_path": str(old_path),
                            "new_path": str(new_path),
                            "operation_type": "rename",
                        }
                    )

                successful += 1
                self.stats["successful_renames"] += 1

            except (OSError, PermissionError) as e:
                print(f"   ❌ Error renaming {old_path.name}: {e}")
                self.stats["errors"] += 1

        if not dry_run and self.operations:
            self.save_operation_log()

        action = "Would rename" if dry_run else "Renamed"
        print(f"\n📊 {action} {successful}/{len(operations)} files")

        if self.stats["errors"] > 0:
            print(f"⚠️  {self.stats['errors']} errors encountered")

        return successful

    def undo_last_operation(self) -> int:
        """Undo the last batch rename operation."""
        operations = self.load_operation_log()

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
                old_path = Path(op["new_path"])  # Current name
                new_path = Path(op["old_path"])  # Original name

                if old_path.exists():
                    old_path.rename(new_path)
                    print(f"   ✅ Restored: {old_path.name} → {new_path.name}")
                    successful += 1
                else:
                    print(f"   ⚠️  File not found: {old_path}")

            except (OSError, PermissionError) as e:
                print(f"   ❌ Error restoring {op['new_path']}: {e}")

        # Remove undone operations from log
        remaining_ops = [op for op in operations if op["timestamp"] != last_timestamp]
        with open(self.operation_log, "w") as f:
            json.dump(remaining_ops, f, indent=2, default=str)

        print(f"📊 Restored {successful}/{len(last_ops)} files")
        return successful


def get_files_by_pattern(
    directory: Path,
    pattern: str = "*",
    recursive: bool = False,
    include_dirs: bool = False,
) -> List[Path]:
    """Get files matching pattern with filtering options."""
    if recursive:
        matches = list(directory.rglob(pattern))
    else:
        matches = list(directory.glob(pattern))

    if include_dirs:
        return matches
    else:
        return [f for f in matches if f.is_file()]


def main():
    parser = argparse.ArgumentParser(
        description="Professional batch file renaming with pattern matching and undo support"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Rename operations")

    # Sequential rename
    seq_parser = subparsers.add_parser(
        "sequential", help="Rename files with sequential numbers"
    )
    seq_parser.add_argument("directory", type=Path, help="Directory containing files")
    seq_parser.add_argument(
        "pattern", help="Pattern with {n} for number, {name} for original name"
    )
    seq_parser.add_argument("--start", type=int, default=1, help="Starting number")
    seq_parser.add_argument(
        "--zero-pad", type=int, default=0, help="Zero-pad numbers to width"
    )
    seq_parser.add_argument("--filter", default="*", help="File pattern filter")
    seq_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Include subdirectories"
    )

    # Pattern replace
    replace_parser = subparsers.add_parser("replace", help="Replace text in filenames")
    replace_parser.add_argument(
        "directory", type=Path, help="Directory containing files"
    )
    replace_parser.add_argument("find", help="Text to find")
    replace_parser.add_argument("replace", help="Replacement text")
    replace_parser.add_argument(
        "--regex", action="store_true", help="Use regular expressions"
    )
    replace_parser.add_argument(
        "--ignore-case", "-i", action="store_true", help="Case-insensitive matching"
    )
    replace_parser.add_argument("--filter", default="*", help="File pattern filter")
    replace_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Include subdirectories"
    )

    # Case change
    case_parser = subparsers.add_parser("case", help="Change filename case")
    case_parser.add_argument("directory", type=Path, help="Directory containing files")
    case_parser.add_argument(
        "operation",
        choices=["upper", "lower", "title", "capitalize", "snake", "kebab"],
        help="Case operation",
    )
    case_parser.add_argument("--filter", default="*", help="File pattern filter")
    case_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Include subdirectories"
    )

    # Add prefix/suffix
    fix_parser = subparsers.add_parser("fix", help="Add prefix or suffix to filenames")
    fix_parser.add_argument("directory", type=Path, help="Directory containing files")
    fix_parser.add_argument("--prefix", default="", help="Prefix to add")
    fix_parser.add_argument("--suffix", default="", help="Suffix to add")
    fix_parser.add_argument("--filter", default="*", help="File pattern filter")
    fix_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Include subdirectories"
    )

    # Sanitize filenames
    sanitize_parser = subparsers.add_parser(
        "sanitize", help="Remove invalid characters from filenames"
    )
    sanitize_parser.add_argument(
        "directory", type=Path, help="Directory containing files"
    )
    sanitize_parser.add_argument(
        "--replacement", default="_", help="Character to replace invalid chars"
    )
    sanitize_parser.add_argument("--filter", default="*", help="File pattern filter")
    sanitize_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Include subdirectories"
    )

    # Undo operation
    undo_parser = subparsers.add_parser("undo", help="Undo last rename operation")
    undo_parser.add_argument(
        "--log-file", type=Path, help="Operation log file location"
    )

    # Common arguments
    for p in [seq_parser, replace_parser, case_parser, fix_parser, sanitize_parser]:
        p.add_argument(
            "--dry-run", action="store_true", help="Preview changes without executing"
        )
        p.add_argument(
            "--execute", action="store_true", help="Execute the rename operations"
        )
        p.add_argument("--log-file", type=Path, help="Operation log file location")
        p.add_argument(
            "--include-dirs",
            action="store_true",
            help="Include directories in operation",
        )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle undo command
    if args.command == "undo":
        renamer = BatchRenamer(args.log_file)
        renamer.undo_last_operation()
        return

    # Validate directory
    if not args.directory.exists():
        print(f"❌ Directory not found: {args.directory}")
        sys.exit(1)

    # Get files
    files = get_files_by_pattern(
        args.directory,
        args.filter,
        args.recursive,
        getattr(args, "include_dirs", False),
    )

    if not files:
        print(f"❌ No files found matching pattern '{args.filter}' in {args.directory}")
        sys.exit(1)

    print(f"📁 Found {len(files)} files in {args.directory}")

    # Initialize renamer
    renamer = BatchRenamer(args.log_file)

    # Generate operations based on command
    operations = []

    if args.command == "sequential":
        operations = renamer.sequential_rename(
            files, args.pattern, args.start, getattr(args, "zero_pad", 0)
        )
    elif args.command == "replace":
        operations = renamer.pattern_replace(
            files,
            args.find,
            args.replace,
            args.regex,
            getattr(args, "ignore_case", False),
        )
    elif args.command == "case":
        operations = renamer.case_change(files, args.operation)
    elif args.command == "fix":
        if not args.prefix and not args.suffix:
            print("❌ Must specify either --prefix or --suffix")
            sys.exit(1)
        operations = renamer.add_prefix_suffix(files, args.prefix, args.suffix)
    elif args.command == "sanitize":
        operations = renamer.sanitize_names(files, args.replacement)

    if not operations:
        print("✅ No files need renaming")
        sys.exit(0)

    # Validate operations
    issues = renamer.validate_operations(operations)
    if issues:
        print("⚠️  VALIDATION ISSUES:")
        for issue in issues:
            print(f"   • {issue}")

        if not args.dry_run and not args.execute:
            print("\nUse --dry-run to preview or fix issues before executing")
            sys.exit(1)

    # Execute operations
    dry_run = args.dry_run or not args.execute
    if not dry_run and not args.execute:
        print(
            "⚠️  Use --execute to perform the rename operations or --dry-run to preview"
        )
        sys.exit(1)

    renamer.execute_operations(operations, dry_run)


if __name__ == "__main__":
    main()
