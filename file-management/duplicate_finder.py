#!/usr/bin/env python3
"""
Hash-based duplicate file detector with concurrent processing.
Efficiently identifies duplicate files across directory trees using MD5 hashing.

Designed for large-scale file deduplication with safety features.
"""

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Set


class DuplicateAnalyzer:
    def __init__(self, min_size: int = 0, max_workers: int = 4):
        self.min_size = min_size
        self.max_workers = max_workers
        self.stats = {
            "files_scanned": 0,
            "bytes_processed": 0,
            "duplicates_found": 0,
            "space_wasted": 0,
        }

    def calculate_file_hash(self, file_path: Path, algorithm: str = "md5") -> str:
        """Calculate hash of a file with specified algorithm."""
        hash_func = getattr(hashlib, algorithm)()

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):  # 64KB chunks
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except (IOError, OSError, PermissionError):
            return None

    def get_file_candidates(
        self, directories: List[Path], extensions: Set[str] = None
    ) -> List[Path]:
        """Get list of files to analyze, filtered by size and extension."""
        candidates = []

        for directory in directories:
            if not directory.exists():
                print(f"⚠️  Directory not found: {directory}")
                continue

            print(f"📁 Scanning directory: {directory}")

            for root, _, files in os.walk(directory):
                for file_name in files:
                    file_path = Path(root) / file_name

                    try:
                        file_size = file_path.stat().st_size

                        # Skip small files if minimum size specified
                        if file_size < self.min_size:
                            continue

                        # Filter by extensions if specified
                        if extensions and file_path.suffix.lower() not in extensions:
                            continue

                        candidates.append(file_path)
                        self.stats["files_scanned"] += 1
                        self.stats["bytes_processed"] += file_size

                    except (OSError, PermissionError):
                        continue

        return candidates

    def find_duplicates_concurrent(
        self, file_paths: List[Path], algorithm: str = "md5"
    ) -> Dict[str, List[Path]]:
        """Find duplicates using concurrent hash calculation."""
        file_hashes = defaultdict(list)

        print(
            f"🔍 Computing hashes for {len(file_paths)} files using {self.max_workers} workers..."
        )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit hash calculation tasks
            future_to_path = {
                executor.submit(self.calculate_file_hash, path, algorithm): path
                for path in file_paths
            }

            completed = 0
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                try:
                    file_hash = future.result()
                    if file_hash:
                        file_hashes[file_hash].append(file_path)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

                completed += 1
                if completed % 100 == 0:
                    print(f"   Progress: {completed}/{len(file_paths)} files processed")

        # Filter to only return actual duplicates
        duplicates = {
            hash_val: paths for hash_val, paths in file_hashes.items() if len(paths) > 1
        }

        # Update statistics
        self.stats["duplicates_found"] = len(duplicates)
        self.stats["space_wasted"] = sum(
            (len(paths) - 1) * paths[0].stat().st_size for paths in duplicates.values()
        )

        return duplicates

    def format_size(self, bytes_value: int) -> str:
        """Format bytes in human readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

    def print_report(self, duplicates: Dict[str, List[Path]], show_paths: bool = True):
        """Print formatted duplicate analysis report."""
        print("\n" + "=" * 60)
        print("🔍 DUPLICATE FILE ANALYSIS")
        print("=" * 60)

        print(f"Files scanned: {self.stats['files_scanned']:,}")
        print(f"Data processed: {self.format_size(self.stats['bytes_processed'])}")
        print(f"Duplicate sets: {len(duplicates)}")
        print(f"Wasted space: {self.format_size(self.stats['space_wasted'])}")

        if not duplicates:
            print("\n✅ No duplicate files found!")
            return

        if show_paths:
            print("\n📋 DUPLICATE SETS:")
            print("-" * 50)

            for i, (hash_val, paths) in enumerate(duplicates.items(), 1):
                file_size = paths[0].stat().st_size
                wasted = (len(paths) - 1) * file_size

                print(
                    f"\n{i}. Hash: {hash_val[:12]}... ({len(paths)} files, {self.format_size(wasted)} wasted)"
                )

                for j, path in enumerate(paths):
                    marker = (
                        "🟢" if j == 0 else "🔴"
                    )  # Green for keep, red for duplicate
                    print(f"   {marker} {path}")

    def remove_duplicates(
        self, duplicates: Dict[str, List[Path]], dry_run: bool = True
    ) -> int:
        """Remove duplicate files, keeping the first instance of each."""
        if dry_run:
            print("\n🧪 DRY RUN - No files will be deleted")
        else:
            print("\n🗑️  REMOVING DUPLICATES")

        deleted_count = 0
        space_freed = 0

        for hash_val, paths in duplicates.items():
            # Keep first file, remove the rest
            keep_file = paths[0]
            duplicates_to_remove = paths[1:]

            if not dry_run:
                print(f"\n📁 Keeping: {keep_file}")

            for dup_file in duplicates_to_remove:
                try:
                    file_size = dup_file.stat().st_size

                    if dry_run:
                        print(
                            f"   Would delete: {dup_file} ({self.format_size(file_size)})"
                        )
                    else:
                        dup_file.unlink()
                        print(f"   ✅ Deleted: {dup_file}")

                    deleted_count += 1
                    space_freed += file_size

                except (OSError, PermissionError) as e:
                    print(f"   ❌ Error deleting {dup_file}: {e}")

        action = "Would free" if dry_run else "Freed"
        print(
            f"\n📊 {action}: {self.format_size(space_freed)} by removing {deleted_count} duplicate files"
        )

        return deleted_count


def parse_extensions(ext_string: str) -> Set[str]:
    """Parse comma-separated extension list."""
    if not ext_string:
        return set()

    extensions = set()
    for ext in ext_string.split(","):
        ext = ext.strip().lower()
        if not ext.startswith("."):
            ext = "." + ext
        extensions.add(ext)

    return extensions


def main():
    parser = argparse.ArgumentParser(
        description="Find and optionally remove duplicate files using hash comparison"
    )
    parser.add_argument(
        "directories", nargs="+", type=Path, help="Directories to scan for duplicates"
    )
    parser.add_argument(
        "--min-size",
        "-s",
        type=int,
        default=0,
        help="Minimum file size in bytes (default: 0)",
    )
    parser.add_argument(
        "--algorithm",
        "-a",
        choices=["md5", "sha1", "sha256"],
        default="md5",
        help="Hash algorithm to use (default: md5)",
    )
    parser.add_argument(
        "--extensions",
        "-e",
        type=str,
        help="Comma-separated list of file extensions to include (e.g., jpg,png,mp4)",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=4,
        help="Number of concurrent workers (default: 4)",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Actually remove duplicate files (keeps first instance)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument("--json", "-j", type=Path, help="Export results to JSON file")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress detailed output"
    )

    args = parser.parse_args()

    # Validate directories
    for directory in args.directories:
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            sys.exit(1)
        if not directory.is_dir():
            print(f"❌ Not a directory: {directory}")
            sys.exit(1)

    # Parse extensions
    extensions = parse_extensions(args.extensions) if args.extensions else None

    # Initialize analyzer
    analyzer = DuplicateAnalyzer(min_size=args.min_size, max_workers=args.workers)

    # Get file candidates
    candidates = analyzer.get_file_candidates(args.directories, extensions)

    if not candidates:
        print("❌ No files found matching criteria")
        sys.exit(1)

    # Find duplicates
    duplicates = analyzer.find_duplicates_concurrent(candidates, args.algorithm)

    # Display results
    if not args.quiet:
        analyzer.print_report(duplicates, show_paths=not args.json)

    # Export to JSON if requested
    if args.json:
        export_data = {
            "statistics": analyzer.stats,
            "duplicates": {
                hash_val: [str(path) for path in paths]
                for hash_val, paths in duplicates.items()
            },
        }

        with open(args.json, "w") as f:
            json.dump(export_data, f, indent=2, default=str)
        print(f"📄 Results exported to: {args.json}")

    # Remove duplicates if requested
    if args.remove or args.dry_run:
        if duplicates:
            analyzer.remove_duplicates(duplicates, dry_run=args.dry_run)
        else:
            print("✅ No duplicates to remove")

    # Exit code for scripting
    sys.exit(0 if not duplicates else 1)


if __name__ == "__main__":
    main()
