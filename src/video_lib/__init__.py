"""Video Library - Video content generation with LLM and TTS."""

__version__ = "0.1.0"

from video_lib.models import Video, SubChapter, Paragraph
from video_lib.parser import BookParser
from video_lib.generator import VideoGenerator

__all__ = ["Video", "SubChapter", "Paragraph", "BookParser", "VideoGenerator"]
