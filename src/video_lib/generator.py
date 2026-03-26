"""Main video generator orchestrator."""
from pathlib import Path
from typing import Union, Optional
from video_lib.models import Video, SubChapter, Paragraph
from video_lib.parser import BookParser
from video_lib.llm.client import LLMClient
from video_lib.audio.resona_client import ResonaClient
from video_lib.storage.cache import CacheManager
from video_lib.storage.paths import PathManager
from video_lib.utils import TextProcessor
from video_lib.audio.voices import ResonaVoice
from video_lib.content.content_styles import ContentStyle


class VideoGenerator:
    """Generate short videos with content and audio."""

    def __init__(
        self,
        book: str,
        language: str = "Vietnamese",
        llm_provider: str = "claude",  # "claude" or "gemini"
        voice: Optional[Union[ResonaVoice, str]] = None,
        content_style: Optional[Union[ContentStyle, str]] = None,
        root_dir: Path = None
    ):
        """
        Initialize video generator.

        Args:
            book: Book filename (e.g., "Meaningful-to-Behold.md")
            language: Target language for content
            llm_provider: LLM provider ("claude" or "gemini")
            voice: TTS voice (ResonaVoice enum, voice name string, or None for default)
            content_style: Content generation style (ContentStyle enum, style name, or None for default)
            root_dir: Project root directory
        """
        self.book = book
        self.language = language
        self.root_dir = root_dir or Path.cwd()
        self.paths = PathManager(self.root_dir)

        # Store voice and style for filename generation
        self.voice = voice
        self.content_style = content_style

        # Initialize components
        self.parser = BookParser(self.paths.get_book_md_path(book))
        self.llm = LLMClient(language, llm_provider, content_style)
        self.resona = ResonaClient(language, voice)
        self.cache = CacheManager(self.root_dir)

    def process(
        self,
        chapter: str,
        subchapter: str,
        force: bool = False
    ) -> SubChapter:
        """
        Generate videos with audio for a sub-chapter.

        Steps:
        1. Parse paragraphs from book
        2. Generate content (with cache)
        3. Generate audio (with cache)
        4. Return SubChapter object

        Args:
            chapter: Chapter name
            subchapter: Sub-chapter name
            force: Re-generate even if cached

        Returns:
            SubChapter with all videos and audio
        """
        book_name = TextProcessor.normalize_book_name(self.book)

        # Step 1: Parse paragraphs
        print(f"[PARSE] {chapter}/{subchapter}...")
        paragraphs = self.parser.parse_subchapter(chapter, subchapter)
        print(f"   Found {len(paragraphs)} paragraphs")

        # Step 2: Generate content
        print(f"[CONTENT] Generating {self.language} content...")
        content_cache = self._generate_content(book_name, chapter, subchapter, paragraphs, force)

        # Step 3: Generate audio
        print(f"[AUDIO] Generating audio...")
        self._generate_audio(book_name, chapter, subchapter, content_cache, force)

        # Step 4: Load and return
        result = self._load_subchapter(book_name, chapter, subchapter, content_cache)
        print(f"[SUCCESS] Complete! {len(result.videos)} videos, {result.audio_count()} with audio")
        return result

    def _generate_content(
        self,
        book: str,
        chapter: str,
        subchapter: str,
        paragraphs: list[Paragraph],
        force: bool
    ) -> dict:
        """Generate content for all paragraphs."""
        # Check cache
        cache = self.cache.load_content(book, chapter, subchapter)
        if cache and not force:
            print(f"   Using cached content")
            return cache

        # Generate new content
        cache = {}
        for i, para in enumerate(paragraphs, 1):
            print(f"   [{i}/{len(paragraphs)}] {para.hash[:8]}...", end=" ")

            if para.is_heading:
                cache[para.hash] = {
                    "original": para.text,
                    "video_content": None
                }
                print("(heading)")
            else:
                content = self.llm.generate_content(para)
                cache[para.hash] = {
                    "original": para.text,
                    "video_content": content
                }
                print("[OK]" if content else "[SKIP]")

        # Save cache
        self.cache.save_content(book, chapter, subchapter, cache)
        return cache

    def _generate_audio(
        self,
        book: str,
        chapter: str,
        subchapter: str,
        content_cache: dict,
        force: bool
    ) -> None:
        """Generate audio for all content."""
        content_dir = self.cache.paths.get_video_content_dir(book, chapter, subchapter)
        content_dir.mkdir(parents=True, exist_ok=True)

        idx = 1
        for para_hash, entry in content_cache.items():
            content = entry.get("video_content")
            if not content:
                continue

            original_text = entry.get("original", "")

            # Check if already generated (with style and voice in filename)
            if not force and self.cache.audio_exists(
                book, chapter, subchapter, para_hash, original_text,
                self.content_style, self.voice
            ):
                print(f"   [{idx}] {para_hash[:8]}... cached")
                idx += 1
                continue

            # Generate audio
            print(f"   [{idx}] {para_hash[:8]}... generating...", end=" ")
            audio_path = self.cache.get_audio_path(
                book, chapter, subchapter, para_hash, original_text,
                self.content_style, self.voice
            )

            try:
                self.resona.generate_audio(content, audio_path)
                print("[OK]")
            except Exception as e:
                print(f"[FAIL] {e}")

            idx += 1

    def _load_subchapter(
        self,
        book: str,
        chapter: str,
        subchapter: str,
        content_cache: dict
    ) -> SubChapter:
        """Create SubChapter object from cached data."""
        videos = []

        for para_hash, entry in content_cache.items():
            content = entry.get("video_content")
            if not content:
                continue

            original_text = entry.get("original", "")
            audio_path = self.cache.get_audio_path(
                book, chapter, subchapter, para_hash, original_text,
                self.content_style, self.voice
            )

            videos.append(Video(
                video_id=para_hash,  # Use hash as video_id
                original_text=original_text,
                video_content=content,
                language=self.language,
                audio_file=audio_path if audio_path.exists() else None
            ))

        return SubChapter(
            book=f"{book}.md",
            chapter=chapter,
            subchapter=subchapter,
            language=self.language,
            videos=videos
        )
