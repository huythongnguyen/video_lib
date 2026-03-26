"""Rename video_content folders to match books folder structure.

This script renames chapter and subchapter folders in video_content/ to match
the indexed naming convention used in books/ (e.g., 01_ChapterName).
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_lib.utils import TextProcessor


class FolderRenamer:
    """Rename video_content folders to match books structure."""

    def __init__(self, root_dir: Path, dry_run: bool = True):
        """
        Initialize folder renamer.

        Args:
            root_dir: Project root directory
            dry_run: If True, show what would be done without renaming
        """
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.books_dir = root_dir / "contents" / "books"
        self.video_dir = root_dir / "contents" / "video_content"

        self.stats = {
            "books_processed": 0,
            "chapters_renamed": 0,
            "subchapters_renamed": 0,
            "errors": 0
        }

    def rename_all(self):
        """Rename all video_content folders to match books structure."""
        if not self.video_dir.exists():
            print(f"[INFO] video_content directory not found: {self.video_dir}")
            return

        if not self.books_dir.exists():
            print(f"[ERROR] books directory not found: {self.books_dir}")
            print("Run generate_contents.py first to create books structure")
            return

        print("[INFO] Scanning video_content directory...")
        if self.dry_run:
            print("[INFO] DRY RUN MODE - No folders will be renamed")
        print()

        # Process each book
        for book_dir in sorted(self.video_dir.iterdir()):
            if not book_dir.is_dir():
                continue

            self._process_book(book_dir)

        self._print_summary()

    def _process_book(self, video_book_dir: Path):
        """Process a single book's video_content folder."""
        book_name = video_book_dir.name
        books_ref_dir = self.books_dir / book_name

        if not books_ref_dir.exists():
            print(f"[WARN] No matching book structure for: {book_name}")
            return

        print(f"[BOOK] Processing: {book_name}")

        # Build chapter mapping from books structure
        chapter_mapping = self._build_chapter_mapping(books_ref_dir)

        # Rename chapters in video_content
        for chapter_dir in sorted(video_book_dir.iterdir()):
            if not chapter_dir.is_dir():
                continue

            self._rename_chapter(chapter_dir, chapter_mapping)

        self.stats["books_processed"] += 1

    def _build_chapter_mapping(self, books_ref_dir: Path) -> dict:
        """
        Build mapping of normalized chapter names to indexed names.

        Args:
            books_ref_dir: Reference books directory

        Returns:
            Dict mapping normalized name to indexed name
        """
        mapping = {}

        for chapter_dir in books_ref_dir.iterdir():
            if not chapter_dir.is_dir():
                continue

            # Extract normalized name from indexed folder name
            # Format: XX_NormalizedName -> NormalizedName
            folder_name = chapter_dir.name
            if "_" in folder_name:
                # Remove index prefix
                normalized = "_".join(folder_name.split("_")[1:])
                mapping[normalized] = folder_name

        return mapping

    def _rename_chapter(self, chapter_dir: Path, chapter_mapping: dict):
        """Rename a chapter folder to match books structure."""
        current_name = chapter_dir.name
        normalized_name = current_name

        # If already indexed (XX_Name), extract normalized part
        if current_name[0].isdigit() and "_" in current_name:
            normalized_name = "_".join(current_name.split("_")[1:])

        # Find matching indexed name
        if normalized_name in chapter_mapping:
            new_name = chapter_mapping[normalized_name]

            if current_name != new_name:
                new_path = chapter_dir.parent / new_name

                if new_path.exists():
                    print(f"  [SKIP] {current_name} -> {new_name} (target exists)")
                    return

                action = "[DRY RUN]" if self.dry_run else "[RENAME]"
                print(f"  {action} {current_name} -> {new_name}")

                if not self.dry_run:
                    try:
                        chapter_dir.rename(new_path)
                        self.stats["chapters_renamed"] += 1

                        # Rename subchapters in this chapter
                        self._rename_subchapters(new_path)
                    except Exception as e:
                        print(f"  [ERROR] Failed to rename: {e}")
                        self.stats["errors"] += 1
                else:
                    # In dry run, still check subchapters
                    self._rename_subchapters(chapter_dir)
            else:
                # Already correctly named, check subchapters
                self._rename_subchapters(chapter_dir)
        else:
            print(f"  [WARN] No mapping found for: {current_name}")

    def _rename_subchapters(self, chapter_dir: Path):
        """Rename subchapter folders to match books structure."""
        # Build subchapter mapping from books
        books_chapter = self.books_dir / chapter_dir.parent.name / chapter_dir.name

        if not books_chapter.exists():
            return

        subchapter_mapping = self._build_chapter_mapping(books_chapter)

        for sub_dir in sorted(chapter_dir.iterdir()):
            if not sub_dir.is_dir():
                continue

            current_name = sub_dir.name
            normalized_name = current_name

            # Extract normalized name if indexed
            if current_name[0].isdigit() and "_" in current_name:
                normalized_name = "_".join(current_name.split("_")[1:])

            if normalized_name in subchapter_mapping:
                new_name = subchapter_mapping[normalized_name]

                if current_name != new_name:
                    new_path = sub_dir.parent / new_name

                    if new_path.exists():
                        print(f"    [SKIP] {current_name} -> {new_name} (target exists)")
                        continue

                    action = "[DRY RUN]" if self.dry_run else "[RENAME]"
                    print(f"    {action} {current_name} -> {new_name}")

                    if not self.dry_run:
                        try:
                            sub_dir.rename(new_path)
                            self.stats["subchapters_renamed"] += 1
                        except Exception as e:
                            print(f"    [ERROR] Failed to rename: {e}")
                            self.stats["errors"] += 1

    def _print_summary(self):
        """Print renaming statistics."""
        print()
        print("=" * 60)
        print("Renaming Summary")
        print("=" * 60)
        print(f"Books processed:       {self.stats['books_processed']}")
        print(f"Chapters renamed:      {self.stats['chapters_renamed']}")
        print(f"Subchapters renamed:   {self.stats['subchapters_renamed']}")
        print(f"Errors:                {self.stats['errors']}")
        print("=" * 60)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Rename video_content folders to match books structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run (show what would be done)
    python rename_video_folders.py

    # Actually rename folders
    python rename_video_folders.py --execute

    # Custom root directory
    python rename_video_folders.py --root /path/to/project --execute
        """
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=script_dir.parent.parent,
        help="Project root directory (default: auto-detect)"
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually rename folders (default is dry-run mode)"
    )

    args = parser.parse_args()

    # Create renamer
    renamer = FolderRenamer(args.root, dry_run=not args.execute)

    # Rename folders
    renamer.rename_all()


if __name__ == "__main__":
    main()
