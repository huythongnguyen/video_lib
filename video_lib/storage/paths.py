"""Centralized path management for all content."""
import os
from pathlib import Path
from typing import Optional, Union
from video_lib.utils import TextProcessor


class PathManager:
    """Manage all file paths for books and video content."""
    @staticmethod
    def path_exists(path: Path) -> bool:
        """
        Windows: use extended-length paths to avoid MAX_PATH issues.
        Python's Path.exists()/os.path.exists can incorrectly return False
        for already-existing files when the full path is very long.
        """
        if os.name == "nt":
            p = str(path)
            # Threshold chosen to align with common Windows MAX_PATH failure modes.
            if len(p) >= 250:
                p_resolved = str(path.resolve())
                if p_resolved.startswith("\\\\"):
                    # UNC path
                    ext = "\\\\?\\UNC\\" + p_resolved[2:]
                else:
                    ext = "\\\\?\\" + p_resolved
                return os.path.exists(ext)

        return path.exists()


    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.books_dir = root_dir / "contents/books"
        self.video_content_dir = root_dir / "contents/video_content"
        self.md_dir = root_dir / "md"

    # ====================
    # Helper Methods
    # ====================

    @staticmethod
    def get_style_code(style: Optional[Union['ContentStyle', str]]) -> str:
        """
        Get short code for content style.

        Args:
            style: ContentStyle enum or style name string

        Returns:
            Short code (e.g., "conv", "thot", "clai")
        """
        if style is None:
            return "conv"  # default

        # Import here to avoid circular dependency
        from video_lib.content.content_styles import ContentStyle

        if isinstance(style, str):
            style_obj = ContentStyle.get_by_name(style)
            if style_obj is None:
                return "conv"
            style = style_obj

        # Map enum to short codes
        style_codes = {
            ContentStyle.CONVERSATIONAL: "conv",
            ContentStyle.THOUGHT_PROVOKING: "thot",
            ContentStyle.CLAIMING: "clai",
            ContentStyle.STORYTELLING: "stor",
            ContentStyle.PRACTICAL: "prac",
            ContentStyle.COMPASSIONATE: "comp",
            ContentStyle.CHALLENGING: "chal",
            ContentStyle.INSPIRATIONAL: "insp",
            ContentStyle.PHILOSOPHICAL: "phil",
            ContentStyle.HUMOROUS: "humo"
        }

        return style_codes.get(style, "conv")

    @staticmethod
    def get_voice_code(voice: Optional[Union['ResonaVoice', str]]) -> str:
        """
        Get short code for voice using enum name.

        Args:
            voice: ResonaVoice enum or voice name string

        Returns:
            Short code from enum name (e.g., "ho_min_mang", "van_anh")
        """
        # Import here to avoid circular dependency
        from video_lib.audio.voices import ResonaVoice

        if voice is None:
            return ResonaVoice.get_default().name.lower()

        if isinstance(voice, str):
            voice_obj = ResonaVoice.get_by_name(voice)
            if voice_obj is None:
                return ResonaVoice.get_default().name.lower()
            voice = voice_obj

        return voice.name.lower()

    # ====================
    # Book Paths
    # ====================

    def get_book_md_path(self, book: str) -> Path:
        """Get path to source markdown book."""
        return self.md_dir / book

    def get_book_content_dir(self, book: str, chapter: str = None, subchapter: str = None) -> Path:
        """Get directory for extracted book content."""
        path = self.books_dir / TextProcessor.normalize_book_name(book)
        if chapter:
            path = path / chapter
        if subchapter:
            path = path / subchapter
        return path

    # ====================
    # Video Content Paths
    # ====================

    def get_video_content_dir(self, book: str, chapter: str, subchapter: str) -> Path:
        """Get directory for video content (contains cache.json + audio files)."""
        book_name = TextProcessor.normalize_book_name(book)
        return self.video_content_dir / book_name / chapter / subchapter

    def get_cache_json_path(self, book: str, chapter: str, subchapter: str) -> Path:
        """Get path to cache.json file."""
        return self.get_video_content_dir(book, chapter, subchapter) / "cache.json"

    def get_video_audio_path(
        self,
        book: str,
        chapter: str,
        subchapter: str,
        para_hash: str,
        text: str = None,
        style: Optional[Union['ContentStyle', str]] = None,
        voice: Optional[Union['ResonaVoice', str]] = None
    ) -> Path:
        """
        Get path to video audio file.

        Args:
            book: Book name
            chapter: Chapter name
            subchapter: Sub-chapter name
            para_hash: Paragraph hash (used as video ID)
            text: Original text (optional, for readable filename)
            style: Content style (optional, adds style code to filename)
            voice: Voice (optional, adds voice code to filename)

        Returns:
            Path like: video_content/<book>/<chapter>/<subchapter>/<hash>_<style>_<voice>_snippet.mp3
        """
        filename = self._make_audio_filename(para_hash, text, style, voice)
        return self.get_video_content_dir(book, chapter, subchapter) / filename

    def audio_exists(
        self,
        book: str,
        chapter: str,
        subchapter: str,
        para_hash: str,
        text: str = None,
        style: Optional[Union['ContentStyle', str]] = None,
        voice: Optional[Union['ResonaVoice', str]] = None
    ) -> bool:
        """Check if audio file exists for a paragraph hash."""
        audio_path = self.get_video_audio_path(book, chapter, subchapter, para_hash, text, style, voice)
        return self.path_exists(audio_path)

    # ====================
    # Filename Generation
    # ====================

    def _make_audio_filename(
        self,
        para_hash: str,
        text: str = None,
        style: Optional[Union['ContentStyle', str]] = None,
        voice: Optional[Union['ResonaVoice', str]] = None
    ) -> str:
        """
        Create audio filename from hash, text, style, and voice.

        Format: <hash>_<style_code>_<voice_code>_<snippet>.mp3
        Example: 9ace130b_conv_vananh_the_preeminent_qualities.mp3

        If no style/voice provided, uses defaults.
        If no text provided: <hash>_<style_code>_<voice_code>.mp3
        """
        # Get style and voice codes
        style_code = self.get_style_code(style)
        voice_code = self.get_voice_code(voice)

        # Build filename parts
        parts = [para_hash, style_code, voice_code]

        # Add text snippet if provided
        if text:
            snippet = TextProcessor.to_snippet(text, max_words=3)  # Reduced to 3 words
            parts.append(snippet)

        return "_".join(parts) + ".mp3"
