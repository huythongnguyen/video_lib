"""Cache management for content and audio."""
import json
from pathlib import Path
from typing import Optional, Union
from video_lib.storage.paths import PathManager


class CacheManager:
    """Manage cached content and audio using PathManager."""

    def __init__(self, root_dir: Path):
        self.paths = PathManager(root_dir)

    def load_content(self, book: str, chapter: str, subchapter: str) -> Optional[dict]:
        """Load cached content."""
        cache_path = self.paths.get_cache_json_path(book, chapter, subchapter)
        if not cache_path.exists():
            return None

        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_content(self, book: str, chapter: str, subchapter: str, data: dict) -> None:
        """Save content to cache."""
        cache_path = self.paths.get_cache_json_path(book, chapter, subchapter)
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_audio_path(
        self,
        book: str,
        chapter: str,
        subchapter: str,
        para_hash: str,
        text: str = None,
        style: Optional[Union['ContentStyle', str]] = None,
        voice: Optional[Union['ResonaVoice', str]] = None
    ) -> Path:
        """Get path to audio file with style and voice."""
        return self.paths.get_video_audio_path(
            book, chapter, subchapter, para_hash, text, style, voice
        )

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
        """Check if audio file exists with style and voice."""
        return self.paths.audio_exists(
            book, chapter, subchapter, para_hash, text, style, voice
        )
