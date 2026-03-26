"""Helper utilities for Flask video viewer."""
import json
from pathlib import Path
from typing import Optional, List

from video_lib.models import Paragraph, Video
from video_lib.generator import VideoGenerator
from video_lib.storage.paths import PathManager
from video_lib.utils import TextProcessor


class ViewerHelper:
    """Helper class for video viewer operations."""

    def __init__(self, root_dir: Path):
        """
        Initialize viewer helper.

        Args:
            root_dir: Project root directory
        """
        self.root_dir = root_dir
        self.paths = PathManager(root_dir)

    def list_books(self) -> List[str]:
        """List all available books."""
        books = []
        books_dir = self.root_dir / "contents" / "books"

        if books_dir.exists():
            for book_path in sorted(books_dir.iterdir()):
                if book_path.is_dir():
                    books.append(book_path.name)

        return books

    def list_chapters(self, book: str, filter_generated: bool = False) -> List[dict]:
        """
        List chapters and subchapters for a book.

        Args:
            book: Book name
            filter_generated: Only show subchapters with generated content

        Returns:
            List of chapter dicts with 'name' and 'sub_dirs' keys
        """
        book_dir = self.root_dir / "contents" / "books" / book
        chapters = []

        if not book_dir.exists():
            return chapters

        for chapter_path in sorted(book_dir.iterdir()):
            if not chapter_path.is_dir():
                continue

            sub_dirs = []
            for sub_path in sorted(chapter_path.iterdir()):
                if not sub_path.is_dir():
                    continue

                if filter_generated:
                    # Check if content exists for this subchapter
                    cache_path = self._get_cache_path(book, chapter_path.name, sub_path.name)
                    if cache_path and cache_path.exists():
                        sub_dirs.append(sub_path.name)
                else:
                    sub_dirs.append(sub_path.name)

            if sub_dirs:
                chapters.append({
                    "name": chapter_path.name,
                    "sub_dirs": sub_dirs
                })

        return chapters

    def load_subchapter_videos(
        self,
        book: str,
        chapter: str,
        subchapter: str,
        language: str = "Vietnamese"
    ) -> tuple[List[Video], dict]:
        """
        Load videos for a subchapter.

        Args:
            book: Book name
            chapter: Chapter directory name
            subchapter: Subchapter directory name
            language: Target language

        Returns:
            Tuple of (videos list, metadata dict with chapter info)
        """
        # Load job.json to get original paragraphs
        job_path = self.root_dir / "contents" / "books" / book / chapter / subchapter / "job.json"
        if not job_path.exists():
            raise FileNotFoundError(f"Job file not found: {job_path}")

        with open(job_path, "r", encoding="utf-8") as f:
            job_data = json.load(f)

        raw_chapter = job_data.get("chapter", "")
        raw_subchapter = job_data.get("subchapter", "")
        para_data_list = job_data.get("paragraphs", [])

        # Create Paragraph objects
        paragraphs = []
        for p in para_data_list:
            paragraphs.append(Paragraph(
                text=p.get("original", ""),
                hash=p.get("hash", "")[:16],  # Truncate to 16 chars
                is_heading=(p.get("type") == "heading")
            ))

        # Load cache if it exists
        cache_path = self._get_cache_path(book, chapter, subchapter)
        cache = {}
        if cache_path and cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)

        # Create Video objects for all paragraphs
        videos = []
        for para in paragraphs:
            entry = cache.get(para.hash, {})
            video_content = entry.get("video_content", "")

            # Check for audio file
            audio_path = self._get_audio_path(book, chapter, subchapter, para.hash, para.text)

            videos.append(Video(
                video_id=para.hash,
                original_text=para.text,
                video_content=video_content,
                language=language,
                audio_file=audio_path if audio_path and audio_path.exists() else None
            ))

        metadata = {
            "raw_chapter": raw_chapter,
            "raw_subchapter": raw_subchapter,
            "completion": (sum(1 for v in videos if v.has_audio()) / len(videos) * 100) if videos else 0
        }

        return videos, metadata

    def _get_cache_path(self, book: str, chapter: str, subchapter: str) -> Optional[Path]:
        """Get cache.json path, trying both normalized and directory names."""
        # Try normalized names first (standard path)
        norm_chapter = TextProcessor.normalize(chapter, remove_spaces=True)
        norm_sub = TextProcessor.normalize(subchapter, remove_spaces=True)

        cache_path = self.paths.get_cache_json_path(book, norm_chapter, norm_sub)
        if cache_path.exists():
            return cache_path

        # Try directory names as fallback
        cache_path = self.paths.get_cache_json_path(book, chapter, subchapter)
        if cache_path.exists():
            return cache_path

        return None

    def _get_audio_path(
        self,
        book: str,
        chapter: str,
        subchapter: str,
        para_hash: str,
        text: str
    ) -> Optional[Path]:
        """Get audio file path, trying both normalized and directory names."""
        # Try normalized names first (standard path)
        norm_chapter = TextProcessor.normalize(chapter, remove_spaces=True)
        norm_sub = TextProcessor.normalize(subchapter, remove_spaces=True)

        audio_path = self.paths.get_video_audio_path(book, norm_chapter, norm_sub, para_hash, text)
        if audio_path.exists():
            return audio_path

        # Try directory names as fallback
        audio_path = self.paths.get_video_audio_path(book, chapter, subchapter, para_hash, text)
        if audio_path.exists():
            return audio_path

        return None

    def get_audio_file_path(
        self,
        book: str,
        chapter: str,
        subchapter: str,
        filename: str
    ) -> Optional[Path]:
        """
        Get full path to audio file.

        Args:
            book: Book name
            chapter: Chapter name
            subchapter: Subchapter name
            filename: Audio filename

        Returns:
            Path to audio file or None if not found
        """
        # Try normalized names
        norm_chapter = TextProcessor.normalize(chapter, remove_spaces=True)
        norm_sub = TextProcessor.normalize(subchapter, remove_spaces=True)

        audio_path = self.paths.get_video_content_dir(book, norm_chapter, norm_sub) / filename
        if audio_path.exists():
            return audio_path

        # Try directory names as fallback
        audio_path = self.paths.get_video_content_dir(book, chapter, subchapter) / filename
        if audio_path.exists():
            return audio_path

        return None
