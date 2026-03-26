"""Simple data models."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Video:
    """A single short video."""
    video_id: str                  # "video_01"
    original_text: str             # Source paragraph
    video_content: str             # Translated video content (single field)
    language: str                  # "Vietnamese", "English", etc.
    audio_file: Optional[Path] = None

    def has_audio(self) -> bool:
        """Check if audio file exists."""
        if self.audio_file is None:
            return False

        # On Windows, very long paths can cause Path.exists() to return False
        # even when the file exists. Use extended-path aware checker.
        from video_lib.storage.paths import PathManager
        return PathManager.path_exists(self.audio_file)


@dataclass
class SubChapter:
    """Container for videos from one sub-chapter."""
    book: str
    chapter: str
    subchapter: str
    language: str              # Target language
    videos: list[Video]

    def audio_count(self) -> int:
        """Count videos that have audio."""
        return sum(1 for v in self.videos if v.has_audio())

    def completion_rate(self) -> float:
        """Percentage of videos with audio."""
        if not self.videos:
            return 0.0
        return (self.audio_count() / len(self.videos)) * 100


@dataclass
class Paragraph:
    """A paragraph from the book."""
    text: str
    hash: str                  # SHA256 hash (unique ID)
    is_heading: bool = False   # True if this is a heading (# ## ###)
