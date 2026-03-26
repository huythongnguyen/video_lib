"""Generate job.json files from markdown books."""
import re
import json
import argparse
import sys
from pathlib import Path

# Repo root: video_lib/scripts -> video_lib -> root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from video_lib.utils import TextProcessor
from video_lib.storage.paths import PathManager


class ContentGenerator:
    """Generate structured job files from markdown books."""

    def __init__(self, root_dir: Path, verbose: bool = True):
        """
        Initialize content generator.

        Args:
            root_dir: Project root directory
            verbose: Print detailed progress information
        """
        self.root_dir = root_dir
        self.verbose = verbose
        self.path_manager = PathManager(root_dir)
        self.md_dir = root_dir / "md"
        self.books_dir = root_dir / "contents" / "books"

        # Statistics
        self.stats = {
            "books_processed": 0,
            "chapters_created": 0,
            "subchapters_created": 0,
            "paragraphs_created": 0
        }

    def generate_all(self, dry_run: bool = False) -> None:
        """
        Generate contents for all markdown files in the md directory.

        Args:
            dry_run: If True, don't write files, just show what would be done
        """
        if not self.md_dir.exists():
            print(f"[ERROR] Markdown directory {self.md_dir} not found.")
            return

        md_files = sorted(self.md_dir.glob("*.md"))

        if not md_files:
            print(f"[WARN] No markdown files found in {self.md_dir}")
            return

        print(f"[INFO] Found {len(md_files)} markdown file(s)")
        if dry_run:
            print("[INFO] DRY RUN MODE - No files will be written")
        print()

        for md_file in md_files:
            self.generate_for_book(md_file, dry_run)

        self._print_summary()

    def generate_for_book(self, md_path: Path, dry_run: bool = False) -> None:
        """
        Generate structured chapters and subchapters for a single book.

        Args:
            md_path: Path to markdown book file
            dry_run: If True, don't write files
        """
        book_filename = md_path.name
        book_name = TextProcessor.normalize_book_name(book_filename)

        if self.verbose:
            print(f"[BOOK] Processing: {book_filename}")

        try:
            content = md_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"[ERROR] Failed to read {md_path}: {e}")
            return

        # Split by blank lines to get blocks
        blocks = [b.strip() for b in re.split(r'\n\s*\n', content) if b.strip()]

        # 1. Group blocks into chapters
        chapters = self._group_into_chapters(blocks)

        if not chapters:
            print(f"[WARN] No chapters found in {book_filename}")
            return

        # 2. Process each chapter
        for c_idx, chapter in enumerate(chapters, 1):
            self._process_chapter(
                book_filename,
                book_name,
                chapter,
                c_idx,
                dry_run
            )

        self.stats["books_processed"] += 1

        if self.verbose:
            print(f"[DONE] {book_name}: {len(chapters)} chapters")
            print()

    def _group_into_chapters(self, blocks: list[str]) -> list[dict]:
        """Group blocks into chapter structures."""
        chapters = []
        current_chapter = None

        for block in blocks:
            # Detect chapter headers (# or ##)
            if block.startswith('# ') or block.startswith('## '):
                current_chapter = {
                    "raw_heading": block,
                    "name": TextProcessor.normalize(block, remove_spaces=True),
                    "blocks": []
                }
                chapters.append(current_chapter)
            elif current_chapter:
                current_chapter["blocks"].append(block)

        return chapters

    def _process_chapter(
        self,
        book_filename: str,
        book_name: str,
        chapter: dict,
        chapter_index: int,
        dry_run: bool
    ) -> None:
        """Process a single chapter and create subchapters."""
        chapter_prefix = f"{chapter_index:02d}_{chapter['name']}"
        chapter_dir = self.books_dir / book_name / chapter_prefix

        # Group blocks into subchapters
        subchapters = self._group_into_subchapters(chapter)

        # Create job files for each subchapter
        for s_idx, subchapter in enumerate(subchapters):
            self._create_job_file(
                book_filename,
                chapter,
                subchapter,
                chapter_dir,
                s_idx,
                dry_run
            )

        self.stats["chapters_created"] += 1

    def _group_into_subchapters(self, chapter: dict) -> list[dict]:
        """Group chapter blocks into subchapter structures."""
        subchapters = []

        # Create intro subchapter with chapter heading
        current_subchapter = {
            "raw_heading": "00_Intro",
            "name": "00_00_Intro",
            "blocks": [chapter["raw_heading"]]
        }
        subchapters.append(current_subchapter)

        # Process remaining blocks
        for block in chapter["blocks"]:
            # Detect sub-chapter headers (### or ####)
            if block.startswith('### ') or block.startswith('#### '):
                current_subchapter = {
                    "raw_heading": block,
                    "name": TextProcessor.normalize(block, remove_spaces=True),
                    "blocks": [block]
                }
                subchapters.append(current_subchapter)
            else:
                current_subchapter["blocks"].append(block)

        return subchapters

    def _create_job_file(
        self,
        book_filename: str,
        chapter: dict,
        subchapter: dict,
        chapter_dir: Path,
        subchapter_index: int,
        dry_run: bool
    ) -> None:
        """Create job.json file for a subchapter."""
        # Determine subchapter naming
        if subchapter_index == 0:
            subchapter_prefix = "00_00_Intro"
            raw_subchapter_heading = "00_Intro"
        else:
            subchapter_prefix = f"{subchapter_index:02d}_{subchapter['name']}"
            raw_subchapter_heading = subchapter['raw_heading']

        subchapter_dir = chapter_dir / subchapter_prefix
        job_path = subchapter_dir / "job.json"

        # Create job data
        job_data = {
            "book": book_filename,
            "chapter": chapter["raw_heading"],
            "subchapter": raw_subchapter_heading,
            "paragraphs": []
        }

        # Add paragraphs
        for block in subchapter["blocks"]:
            is_heading = block.startswith('#')
            para_hash = TextProcessor.make_hash(block)

            job_data["paragraphs"].append({
                "hash": para_hash,
                "type": "heading" if is_heading else "paragraph",
                "status": "needs_processing",
                "original": block
            })

        self.stats["paragraphs_created"] += len(job_data["paragraphs"])
        self.stats["subchapters_created"] += 1

        # Write file
        if not dry_run:
            subchapter_dir.mkdir(parents=True, exist_ok=True)
            with open(job_path, "w", encoding="utf-8") as f:
                json.dump(job_data, f, ensure_ascii=False, indent=2)

        if self.verbose:
            rel_path = job_path.relative_to(self.root_dir)
            status = "[DRY RUN]" if dry_run else "[CREATED]"
            print(f"  {status} {rel_path}")

    def _print_summary(self) -> None:
        """Print generation statistics."""
        print()
        print("=" * 60)
        print("Generation Summary")
        print("=" * 60)
        print(f"Books processed:      {self.stats['books_processed']}")
        print(f"Chapters created:     {self.stats['chapters_created']}")
        print(f"Subchapters created:  {self.stats['subchapters_created']}")
        print(f"Paragraphs processed: {self.stats['paragraphs_created']}")
        print("=" * 60)


def main():
    """Main CLI entry point."""
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Generate job.json files for all books in md/ directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate for all books
    python video_lib/scripts/generate_contents.py

    # Dry run (don't write files)
    python video_lib/scripts/generate_contents.py --dry-run

    # Quiet mode
    python video_lib/scripts/generate_contents.py --quiet

    # Custom root directory
    python video_lib/scripts/generate_contents.py --root /path/to/project
        """
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=script_dir.parent.parent,
        help="Project root directory (default: repository root)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress detailed output"
    )

    args = parser.parse_args()

    # Create generator
    generator = ContentGenerator(args.root, verbose=not args.quiet)

    # Generate content
    generator.generate_all(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
