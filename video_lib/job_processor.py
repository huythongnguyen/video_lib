"""Job file processing utilities for CLI."""
import os
import sys
import json
from pathlib import Path
from typing import Optional, Union
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from .models import Paragraph, SubChapter
from .generator import VideoGenerator
from .utils import TextProcessor
from video_lib.audio.voices import ResonaVoice
from video_lib.content.content_styles import ContentStyle


class JobProcessor:
    """Process job files and generate video content."""

    @staticmethod
    def _normalize_enum_token(value: str) -> str:
        """
        Normalize a user-provided token into an Enum member name.
        Examples:
          - "thought-provoking" -> "THOUGHT_PROVOKING"
          - "Thought Provoking" -> "THOUGHT_PROVOKING"
          - "tue_an" -> "TUE_AN"
        """
        return value.strip().upper().replace("-", "_").replace(" ", "_")

    @classmethod
    def _resolve_voice(cls, voice: Optional[Union[ResonaVoice, str]]) -> Optional[ResonaVoice]:
        """Resolve voice from enum member or string (enum-name first, then display-name)."""
        if voice is None or isinstance(voice, ResonaVoice):
            return voice

        if isinstance(voice, str):
            token = cls._normalize_enum_token(voice)
            try:
                return ResonaVoice[token]
            except KeyError:
                resolved = ResonaVoice.get_by_name(voice)
                if resolved is None:
                    raise ValueError(f"Unknown voice: {voice}. Use --list-voices to see available voices.")
                return resolved

        raise TypeError(f"voice must be ResonaVoice enum, str, or None, got {type(voice)}")

    @classmethod
    def _resolve_style(cls, style: Optional[Union[ContentStyle, str]]) -> Optional[ContentStyle]:
        """Resolve style from enum member or string (enum-name first, then display-name)."""
        if style is None or isinstance(style, ContentStyle):
            return style

        if isinstance(style, str):
            token = cls._normalize_enum_token(style)
            try:
                return ContentStyle[token]
            except KeyError:
                resolved = ContentStyle.get_by_name(style)
                if resolved is None:
                    raise ValueError(f"Unknown style: {style}. Use --list-styles to see available styles.")
                return resolved

        raise TypeError(f"content_style must be ContentStyle enum, str, or None, got {type(style)}")

    def __init__(self, root_dir: Path):
        """
        Initialize job processor.

        Args:
            root_dir: Project root directory
        """
        self.root_dir = root_dir

    def load_environment(self) -> None:
        """Load environment variables from .env file."""
        env_path = self.root_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"[ENV] Loaded environment from {env_path}")
        else:
            print(f"[WARN] No .env file found at {env_path}")

    def validate_environment(self, llm_provider: str) -> bool:
        """
        Validate required environment variables.

        Args:
            llm_provider: LLM provider (claude or gemini)

        Returns:
            True if valid, False otherwise
        """
        if llm_provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
            print("[ERROR] GOOGLE_API_KEY not found in environment")
            print("Please set it in .env file or environment")
            return False

        if not os.getenv("RESONA_API_KEY"):
            print("[ERROR] RESONA_API_KEY not found in environment")
            print("Please set it in .env file or environment")
            return False

        return True

    def parse_job_file(self, job_path: Path) -> dict:
        """
        Parse job.json file.

        Args:
            job_path: Path to job.json file

        Returns:
            Job data dictionary

        Raises:
            FileNotFoundError: If job file doesn't exist
            json.JSONDecodeError: If job file is invalid JSON
        """
        if not job_path.exists():
            raise FileNotFoundError(f"Job file not found: {job_path}")

        with open(job_path, "r", encoding="utf-8") as f:
            job_data = json.load(f)

        return job_data

    def extract_chapter_info(self, job_data: dict) -> tuple[str, str]:
        """
        Extract normalized chapter and subchapter names from job data.

        Args:
            job_data: Job data dictionary

        Returns:
            Tuple of (chapter_name, subchapter_name)
        """
        raw_chapter = job_data.get("chapter", "")
        raw_subchapter = job_data.get("subchapter", "")

        chapter = TextProcessor.normalize(raw_chapter, remove_spaces=True)
        subchapter = TextProcessor.normalize(raw_subchapter, remove_spaces=True)

        return chapter, subchapter

    def create_paragraphs(self, job_data: dict) -> list[Paragraph]:
        """
        Create Paragraph objects from job data.

        Args:
            job_data: Job data dictionary

        Returns:
            List of Paragraph objects
        """
        paragraphs = []

        for para_data in job_data.get("paragraphs", []):
            para_hash = para_data.get("hash", "")
            para_type = para_data.get("type", "paragraph")
            original_text = para_data.get("original", "")

            # Truncate hash to 16 characters to match our hash length
            para_hash_short = para_hash[:16]

            paragraph = Paragraph(
                text=original_text,
                hash=para_hash_short,
                is_heading=(para_type == "heading")
            )
            paragraphs.append(paragraph)

        return paragraphs

    def process(
        self,
        job_path: Path,
        language: str = "Vietnamese",
        llm_provider: str = "gemini",
        voice: Optional[Union[ResonaVoice, str]] = None,
        content_style: Optional[Union[ContentStyle, str]] = None,
        force: bool = False
    ) -> Optional[SubChapter]:
        """
        Process a job file and generate video content + audio.

        Args:
            job_path: Path to job.json file
            language: Target language (Vietnamese, English, etc.)
            llm_provider: LLM provider (claude or gemini)
            voice: TTS voice (ResonaVoice enum, voice name, or None for default)
            content_style: Content generation style (ContentStyle enum, style name, or None for default)
            force: Force re-generation even if cached

        Returns:
            SubChapter result or None if failed
        """
        print("=" * 60)
        print("Video Library CLI")
        print("=" * 60)

        # Parse job file
        print(f"\n[PARSE] Reading job file: {job_path}")
        job_data = self.parse_job_file(job_path)

        book = job_data.get("book", "")
        chapter, subchapter = self.extract_chapter_info(job_data)
        paragraphs = self.create_paragraphs(job_data)

        # Resolve CLI strings to enums (prefer enum tokens over display names)
        try:
            voice = self._resolve_voice(voice)
            content_style = self._resolve_style(content_style)
        except Exception as e:
            print(f"[ERROR] Invalid --voice/--style: {e}")
            return None

        # Get voice name for display
        if voice is None:
            _dv = ResonaVoice.get_default()
            voice_name = f"Default ({_dv.value.name})"
        elif isinstance(voice, ResonaVoice):
            voice_name = voice.value.name
        else:
            voice_name = voice

        # Get style name for display
        style_name = "Default (Conversational)"
        if content_style:
            if isinstance(content_style, ContentStyle):
                style_name = content_style.value.name
            else:
                style_name = content_style

        print(f"   Book: {book}")
        print(f"   Chapter: {chapter}")
        print(f"   Sub-chapter: {subchapter}")
        print(f"   Paragraphs: {len(paragraphs)}")
        print(f"   Language: {language}")
        print(f"   LLM Provider: {llm_provider}")
        print(f"   Content Style: {style_name}")
        print(f"   Voice: {voice_name}")

        # Create generator
        print(f"\n[INIT] Creating VideoGenerator...")
        try:
            generator = VideoGenerator(
                book=book,
                language=language,
                llm_provider=llm_provider,
                voice=voice,
                content_style=content_style,
                root_dir=self.root_dir
            )
            print("   VideoGenerator created successfully")
        except Exception as e:
            print(f"[ERROR] Failed to create VideoGenerator: {e}")
            return None

        # Process using the generator's internal methods
        print(f"\n[PROCESS] Generating content and audio...")
        try:
            book_name = TextProcessor.normalize_book_name(book)

            # Generate content (using existing cache or creating new)
            print(f"[CONTENT] Generating {language} content...")
            content_cache = generator._generate_content(
                book_name, chapter, subchapter, paragraphs, force
            )

            # Generate audio
            print(f"[AUDIO] Generating audio...")
            generator._generate_audio(
                book_name, chapter, subchapter, content_cache, force
            )

            # Load and display results
            result = generator._load_subchapter(
                book_name, chapter, subchapter, content_cache
            )

            self._print_results(result)
            return result

        except Exception as e:
            print(f"\n[ERROR] Processing failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _print_results(self, result: SubChapter) -> None:
        """Print processing results."""
        print("\n" + "=" * 60)
        print("[SUCCESS] Processing complete!")
        print("=" * 60)
        print(f"\nResults:")
        print(f"   Book: {result.book}")
        print(f"   Chapter: {result.chapter}")
        print(f"   Sub-chapter: {result.subchapter}")
        print(f"   Language: {result.language}")
        print(f"   Total videos: {len(result.videos)}")
        print(f"   Videos with audio: {result.audio_count()}")
        print(f"   Completion rate: {result.completion_rate():.1f}%")

        # Show video details
        if result.videos:
            print(f"\nGenerated videos:")
            for i, video in enumerate(result.videos, 1):
                audio_status = "[OK]" if video.has_audio() else "[NO AUDIO]"
                print(f"   [{i}] {video.video_id[:8]}... {audio_status}")

            # Show first video sample
            print(f"\nFirst video sample:")
            video = result.videos[0]
            print(f"   Hash: {video.video_id}")
            print(f"   Original (first 100 chars): {video.original_text[:100]}...")
            if video.video_content:
                print(f"   Content (first 100 chars): {video.video_content[:100]}...")
            if video.has_audio():
                print(f"   Audio file: {video.audio_file}")
