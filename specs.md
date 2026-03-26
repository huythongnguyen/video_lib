# Video Library — Clean Design

## Goal

Build a standalone Python library to:
1. Parse book markdown → extract paragraphs
2. Generate video content via Claude Code CLI or Gemini
3. Generate audio via Resona API
4. Support multiple languages (Vietnamese, English, etc.)
5. Display in a web viewer

---

## Folder Structure

```
buddhist-content/
├── video_lib/                   # Main library
│   ├── __init__.py
│   ├── models.py                # Video, SubChapter, Paragraph
│   ├── utils.py                 # Shared utilities (text, HTTP, etc.)
│   ├── paths.py                 # PathManager - centralized path generation
│   ├── parser.py                # BookParser - parse MD into chapters/paragraphs
│   ├── llm_client.py            # LLMClient - generate content (Claude Code or Gemini)
│   ├── resona_client.py         # ResonaClient - generate audio
│   ├── generator.py             # VideoGenerator - orchestrates everything
│   ├── cache.py                 # CacheManager - handle storage
│   ├── prompts.py               # Prompt templates
│   └── viewer/                  # Web viewer
│       ├── __init__.py
│       ├── app.py               # Flask app
│       └── templates/
│           └── viewer.html
│
├── contents/
│   ├── books/                   # Raw book content (extracted)
│   │   └── <book>/
│   │       └── <chapter>/
│   │           └── <subchapter>/
│   │               └── ...
│   │
│   └── video_content/           # Video scripts (JSON) + Audio (MP3) together
│       └── <book>/
│           └── <chapter>/
│               └── <subchapter>/
│                   ├── cache.json
│                   ├── 9ace130b_the_preeminent_qualities.mp3
│                   ├── 6b9aee51_in_this_text.mp3
│                   └── ...
│
├── md/                          # Source books
│   └── Meaningful-to-Behold.md
│
├── video_lib_cli.py             # CLI entry point
├── pyproject.toml               # Package config
└── README.md
```

**Key changes**:
- Added `contents/books/` for raw extracted content
- Combined JSON and audio in same `video_content/<book>/<chapter>/<subchapter>/` folder
- Added `video_lib_cli.py` for command-line interface

---

## CLI Usage

The `video_lib_cli.py` script provides a command-line interface for processing job files from the existing short_videos pipeline.

### Basic Usage

```bash
# Process a job file
python video_lib_cli.py contents/books/Meaningful-to-Behold/14_Effort/08_EXAMININGTHECAUSEOFINDOLENCE/job.json

# Use Claude Code CLI
python video_lib_cli.py path/to/job.json --llm claude

# Generate English content
python video_lib_cli.py path/to/job.json --language English

# Force regeneration
python video_lib_cli.py path/to/job.json --force
```

### Features

- **Automatic .env loading**: Loads environment variables from `.env` file
- **Job file parsing**: Reads job.json files with book/chapter/subchapter metadata
- **Progress tracking**: Shows real-time progress during processing
- **Dual LLM support**: Works with Claude Code CLI or Gemini API
- **Hash-based output**: Audio files use hash-based filenames for traceability

### Job File Format

```json
{
  "book": "Meaningful-to-Behold.md",
  "chapter": "## Effort",
  "subchapter": "### EXAMINING THE CAUSE OF INDOLENCE",
  "paragraphs": [
    {
      "hash": "1b142c86f6e83dee...",
      "type": "heading",
      "original": "### EXAMINING THE CAUSE OF INDOLENCE"
    },
    {
      "hash": "a31d73f9600efb31...",
      "type": "paragraph",
      "original": "When overcome by the laziness..."
    }
  ]
}
```

### Output Structure

```
contents/video_content/Meaningful-to-Behold/Effort/EXAMININGTHECAUSEOFINDOLENCE/
├── cache.json                        # Generated content cache
├── 1b142c86_examining_the_cause.mp3  # Audio files with hash + snippet
└── a31d73f9_when_overcome_by.mp3
```

---

## Core Modules

### 1. `paths.py` - Centralized Path Management

**NEW!** All file paths are generated through `PathManager` to avoid duplication.

```python
"""Centralized path management for all content."""
import re
from pathlib import Path


class PathManager:
    """Manage all file paths for books and video content."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.books_dir = root_dir / "contents/books"
        self.video_content_dir = root_dir / "contents/video_content"
        self.md_dir = root_dir / "md"

    # Book paths
    def get_book_md_path(self, book: str) -> Path:
        """Get path to source markdown book."""
        return self.md_dir / book

    def get_book_content_dir(self, book: str, chapter: str = None, subchapter: str = None) -> Path:
        """Get directory for extracted book content."""
        path = self.books_dir / book.replace(".md", "")
        if chapter:
            path = path / chapter
        if subchapter:
            path = path / subchapter
        return path

    # Video content paths
    def get_video_content_dir(self, book: str, chapter: str, subchapter: str) -> Path:
        """Get directory for video content (contains cache.json + audio files)."""
        book_name = book.replace(".md", "")
        return self.video_content_dir / book_name / chapter / subchapter

    def get_cache_json_path(self, book: str, chapter: str, subchapter: str) -> Path:
        """Get path to cache.json file."""
        return self.get_video_content_dir(book, chapter, subchapter) / "cache.json"

    def get_video_audio_path(self, book: str, chapter: str, subchapter: str, para_hash: str, text: str = None) -> Path:
        """
        Get path to video audio file.

        Returns path like: <hash>_snippet.mp3
        Example: 9ace130b_the_preeminent_qualities.mp3
        """
        filename = self._make_audio_filename(para_hash, text)
        return self.get_video_content_dir(book, chapter, subchapter) / filename

    def _make_audio_filename(self, para_hash: str, text: str = None) -> str:
        """
        Create audio filename from hash and optional text.

        Format: <hash>_<snippet>.mp3
        If no text: <hash>.mp3
        """
        if not text:
            return f"{para_hash}.mp3"

        snippet = self._text_to_snippet(text)
        return f"{para_hash}_{snippet}.mp3"

    def _text_to_snippet(self, text: str, max_words: int = 4) -> str:
        """Convert text to URL-friendly snippet (first 4 words)."""
        clean = re.sub(r'^#+\s*', '', text)  # Remove headings
        clean = re.sub(r'[^\w\s]', '', clean)  # Remove punctuation
        clean = clean.lower().strip()
        words = clean.split()[:max_words]
        return "_".join(words)
```

**Key features:**
- Hash-based video filenames with readable text snippets
- Single source of truth for all paths
- Easy to trace videos back to source paragraphs

---

### 2. `models.py` - Data Models

```python
"""Simple data models."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class Video:
    """A single short video."""
    video_id: str                  # Paragraph hash (e.g., "9ace130b")
    original_text: str             # Source paragraph
    video_content: str             # Translated video content (single field)
    language: str                  # "Vietnamese", "English", etc.
    audio_file: Optional[Path] = None

    def has_audio(self) -> bool:
        return self.audio_file and self.audio_file.exists()


@dataclass
class SubChapter:
    """Container for videos from one sub-chapter."""
    book: str
    chapter: str
    subchapter: str
    language: str              # Target language
    videos: list[Video]

    def audio_count(self) -> int:
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
```

---

### 3. `utils.py` - Shared Utilities (Class-Based)

**NEW!** Common utilities organized into classes for better abstraction and maintainability.

```python
"""Shared utilities used across the library."""
import re
import hashlib
import json
import urllib.request
from typing import Optional


class TextProcessor:
    """Text processing utilities for normalization, hashing, and formatting."""

    @staticmethod
    def normalize(text: str, remove_spaces: bool = True, lowercase: bool = False) -> str:
        """Normalize text by removing markdown, punctuation, and optionally spaces."""
        clean = re.sub(r'^#+\s*', '', text)  # Remove markdown headings
        clean = re.sub(r'[^\w\s]', '', clean)  # Remove punctuation
        if lowercase:
            clean = clean.lower()
        if remove_spaces:
            clean = re.sub(r'\s+', '', clean)
        else:
            clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    @staticmethod
    def to_snippet(text: str, max_words: int = 4) -> str:
        """Convert text to URL-friendly snippet (first N words)."""
        clean = TextProcessor.normalize(text, remove_spaces=False, lowercase=True)
        words = clean.split()[:max_words]
        return "_".join(words)

    @staticmethod
    def make_hash(text: str, length: int = 16) -> str:
        """Generate SHA256 hash of text."""
        return hashlib.sha256(text.encode()).hexdigest()[:length]

    @staticmethod
    def extract_from_code_block(text: str) -> str:
        """Extract content from markdown code blocks."""
        text = text.strip()
        if "```" not in text:
            return text
        parts = text.split("```")
        if len(parts) < 2:
            return text
        content = parts[1]
        if content.startswith("json") or content.startswith("text"):
            content = "\n".join(content.split("\n")[1:])
        return content.strip()

    @staticmethod
    def normalize_book_name(book: str) -> str:
        """Remove .md extension from book filename."""
        return book.replace(".md", "")


class HttpClient:
    """HTTP client utilities for API requests and file downloads."""

    @staticmethod
    def request(url: str, headers: dict, method: str = "GET", data: Optional[dict] = None) -> dict:
        """Make HTTP request and return JSON response."""
        request_data = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def download(url: str, dest_path, headers: Optional[dict] = None) -> None:
        """Download file from URL to local path."""
        headers = headers or {}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            if hasattr(dest_path, 'write_bytes'):
                dest_path.write_bytes(resp.read())
            else:
                with open(dest_path, 'wb') as f:
                    f.write(resp.read())
```

**Benefits:**
- **Better organization**: Related functions grouped in classes
- **Clear abstraction**: `TextProcessor` for text, `HttpClient` for HTTP
- **DRY principle**: Code reuse across multiple modules
- **Single source of truth**: Change once, update everywhere
- **Easier testing**: Classes can be tested independently
- **Type safety**: Static methods with clear namespaces

**Used by:**
- `parser.py`: `TextProcessor.normalize()`, `TextProcessor.make_hash()`
- `paths.py`: `TextProcessor.to_snippet()`, `TextProcessor.normalize_book_name()`
- `llm_client.py`: `TextProcessor.extract_from_code_block()`
- `resona_client.py`: `HttpClient.request()`, `HttpClient.download()`
- `generator.py`: `TextProcessor.normalize_book_name()`

---

### 4. `parser.py` - Book Parser

```python
"""Parse markdown books into structured data."""
import hashlib
import re
from pathlib import Path
from .models import Paragraph

class BookParser:
    """Parse a markdown book into chapters and paragraphs."""

    def __init__(self, book_path: Path):
        self.book_path = book_path
        self.content = book_path.read_text(encoding="utf-8")

    def parse_subchapter(self, chapter: str, subchapter: str) -> list[Paragraph]:
        """
        Extract all paragraphs from a specific sub-chapter.

        Args:
            chapter: Chapter name (e.g., "08_TheBenefitsofBodhichitta")
            subchapter: Sub-chapter name (e.g., "19_DEVELOPINGBODHICHITTA")

        Returns:
            List of Paragraph objects
        """
        blocks = re.split(r'\n\s*\n', self.content)

        paragraphs = []
        in_target = False
        current_chapter = None
        current_subchapter = None

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # Detect chapter headers (# or ##)
            if block.startswith('# ') or block.startswith('## '):
                current_chapter = self._normalize_name(block)
                current_subchapter = None
                in_target = False

            # Detect sub-chapter headers (### or ####)
            elif block.startswith('### ') or block.startswith('#### '):
                current_subchapter = self._normalize_name(block)
                if current_chapter == chapter and current_subchapter == subchapter:
                    in_target = True
                    paragraphs.append(self._make_paragraph(block, is_heading=True))
                else:
                    in_target = False

            # Regular paragraph
            elif in_target:
                paragraphs.append(self._make_paragraph(block))

        return paragraphs

    def _make_paragraph(self, text: str, is_heading: bool = False) -> Paragraph:
        """Create a Paragraph with hash."""
        para_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return Paragraph(text=text, hash=para_hash, is_heading=is_heading)

    def _normalize_name(self, heading: str) -> str:
        """Convert '### My Heading' to 'MyHeading'."""
        clean = re.sub(r'^#+\s*', '', heading)
        clean = re.sub(r'[^\w\s]', '', clean)
        clean = re.sub(r'\s+', '', clean)
        return clean
```

---

### 5. `llm_client.py` - LLM Client (Claude Code or Gemini)

```python
"""LLM client for generating video content (Claude Code CLI or Gemini API)."""
import os
import subprocess
import json
from typing import Optional
from .models import Paragraph
from .prompts import get_filter_prompt, get_writer_prompt

class LLMClient:
    """Generate video content using Claude Code or Gemini."""

    def __init__(self, language: str = "Vietnamese", provider: str = "claude"):
        """
        Initialize LLM client.

        Args:
            language: Target language for content
            provider: "claude" (Claude Code CLI) or "gemini" (Gemini API)
        """
        self.language = language
        self.provider = provider.lower()

        if self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_content(self, paragraph: Paragraph) -> Optional[str]:
        """
        Generate video content for a paragraph.

        Returns:
            Video content string or None if skip
        """
        # Step 1: Filter - should we create content for this?
        should_create = self._filter(paragraph)
        if not should_create:
            return None

        # Step 2: Write content
        content = self._write_content(paragraph)
        return content

    def _filter(self, paragraph: Paragraph) -> bool:
        """Decide if paragraph should become video content."""
        if paragraph.is_heading:
            return False

        prompt = get_filter_prompt(paragraph.text)
        response = self._call_llm(prompt, max_tokens=100)

        decision = response.strip().upper()
        return "CREATE" in decision

    def _write_content(self, paragraph: Paragraph) -> str:
        """Generate video content."""
        prompt = get_writer_prompt(paragraph.text, self.language)
        response = self._call_llm(prompt, max_tokens=1000)

        # Extract content (remove markdown if present)
        content = response.strip()
        if "```" in content:
            # Remove code blocks
            content = content.split("```")[1]
            if content.startswith("json") or content.startswith("text"):
                content = "\n".join(content.split("\n")[1:])

        return content.strip()

    def _call_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call LLM provider (Claude Code or Gemini)."""
        if self.provider == "claude":
            return self._call_claude_code(prompt)
        elif self.provider == "gemini":
            return self._call_gemini(prompt, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _call_claude_code(self, prompt: str) -> str:
        """Call Claude Code CLI."""
        cmd = [
            "claude",
            "--dangerously-skip-permissions",
            "--print",
            prompt
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude Code failed: {result.stderr}")

        return result.stdout.strip()

    def _call_gemini(self, prompt: str, max_tokens: int) -> str:
        """Call Gemini API."""
        response = self.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": 0.7,
            }
        )
        return response.text
```

---

### 6. `resona_client.py` - Resona TTS Client

```python
"""Resona TTS API client."""
import os
import time
import json
import urllib.request
from pathlib import Path

# Voice IDs for different languages
VOICE_IDS = {
    "Vietnamese": "ES9XihN1RcFVpypacTTh",  # Thanh Nhã (calm female)
    "English": "ES9XihN1RcFVpypacTTh",     # TODO: Find English voice
}

class ResonaClient:
    """Generate audio via Resona API."""

    def __init__(self, language: str = "Vietnamese"):
        self.api_key = os.getenv("RESONA_API_KEY")
        if not self.api_key:
            raise ValueError("RESONA_API_KEY environment variable not set")

        self.base_url = "https://resona.live"
        self.voice_id = VOICE_IDS.get(language, VOICE_IDS["Vietnamese"])
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Origin": "https://resona.live",
            "Referer": "https://resona.live/",
        }

    def generate_audio(self, text: str, output_path: Path) -> None:
        """Generate audio from text and save to file."""
        request_id = self._submit_job(text)
        audio_url = self._wait_for_completion(request_id)
        self._download(audio_url, output_path)

    def _submit_job(self, text: str) -> str:
        """Submit TTS job, return request_id."""
        url = f"{self.base_url}/api/v1/generate-speech"
        data = {
            "text": f"Speaker 1: {text}",
            "voice_ids": [self.voice_id]
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=self.headers,
            method="POST"
        )

        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["request_id"]

    def _wait_for_completion(self, request_id: str, timeout: int = 180) -> str:
        """Poll until completed, return audio URL."""
        deadline = time.time() + timeout

        while time.time() < deadline:
            status = self._check_status(request_id)

            if status["status"] == "completed":
                result = self._get_result(request_id)
                return result["audio_urls"][0]

            elif status["status"] == "failed":
                raise RuntimeError(f"TTS job {request_id} failed")

            time.sleep(3)

        raise TimeoutError(f"TTS job {request_id} timed out")

    def _check_status(self, request_id: str) -> dict:
        """Check job status."""
        url = f"{self.base_url}/api/v1/generate-speech/{request_id}/status"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _get_result(self, request_id: str) -> dict:
        """Get completed job result."""
        url = f"{self.base_url}/api/v1/generate-speech/{request_id}"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _download(self, url: str, dest: Path) -> None:
        """Download audio file."""
        headers = {"User-Agent": self.headers["User-Agent"]}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            dest.write_bytes(resp.read())
```

---

### 7. `prompts.py` - Prompt Templates

```python
"""Prompt templates for LLM."""

def get_filter_prompt(text: str) -> str:
    """Prompt for filtering content."""
    return f"""You are a content filter for short videos (TikTok/Shorts).

Analyze this paragraph and decide if it should be turned into video content.

CREATE content for:
- Meaningful teachings
- Stories and examples
- Practice instructions
- Philosophical concepts

SKIP:
- Headings and titles
- Citations and references
- Transitional text
- Acknowledgments

Paragraph:
{text}

Respond with ONLY one word: "CREATE" or "SKIP"
"""


def get_writer_prompt(text: str, language: str) -> str:
    """Prompt for writing video content."""

    # Language-specific guidelines
    guidelines = {
        "Vietnamese": """
Write natural, conversational Vietnamese content for a short video (30-60 seconds when read aloud).

Guidelines:
- Use inclusive pronouns ("ta", "chúng ta")
- Warm, accessible tone (no academic jargon)
- Natural flow for social media
- 3-7 sentences total
""",
        "English": """
Write natural, conversational English content for a short video (30-60 seconds when read aloud).

Guidelines:
- Warm, accessible tone (no academic jargon)
- Natural flow for social media
- 3-7 sentences total
"""
    }

    guide = guidelines.get(language, guidelines["English"])

    return f"""You are a video content writer for short videos (TikTok/Shorts/Reels).

{guide}

Original text (English):
{text}

Write the {language} video content. Output ONLY the content text, no explanation, no labels, no markdown formatting.
"""
```

---

### 8. `cache.py` - Cache Manager

**Simplified!** Delegates all path logic to `PathManager`.

```python
"""Cache management for content and audio."""
import json
from pathlib import Path
from typing import Optional
from .paths import PathManager


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

    def get_audio_path(self, book: str, chapter: str, subchapter: str, para_hash: str, text: str = None) -> Path:
        """Get path to audio file."""
        return self.paths.get_video_audio_path(book, chapter, subchapter, para_hash, text)

    def audio_exists(self, book: str, chapter: str, subchapter: str, para_hash: str, text: str = None) -> bool:
        """Check if audio file exists."""
        return self.paths.audio_exists(book, chapter, subchapter, para_hash, text)
```

**Key changes:**
- Uses `PathManager` for all paths
- Simplified from ~48 lines to ~32 lines
- Hash-based audio filenames with text snippets

---

### 9. `generator.py` - Main Orchestrator

```python
"""Main video generator orchestrator."""
from pathlib import Path
from .models import Video, SubChapter, Paragraph
from .parser import BookParser
from .llm_client import LLMClient
from .resona_client import ResonaClient
from .cache import CacheManager
from .paths import PathManager

class VideoGenerator:
    """Generate short videos with content and audio."""

    def __init__(
        self,
        book: str,
        language: str = "Vietnamese",
        llm_provider: str = "claude",  # "claude" or "gemini"
        root_dir: Path = None
    ):
        self.book = book
        self.language = language
        self.root_dir = root_dir or Path.cwd()
        self.paths = PathManager(self.root_dir)

        # Initialize components
        self.parser = BookParser(self.paths.get_book_md_path(book))
        self.llm = LLMClient(language, llm_provider)
        self.resona = ResonaClient(language)
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
        book_name = self.book.replace(".md", "")

        # Step 1: Parse paragraphs
        print(f"📖 Parsing {chapter}/{subchapter}...")
        paragraphs = self.parser.parse_subchapter(chapter, subchapter)
        print(f"   Found {len(paragraphs)} paragraphs")

        # Step 2: Generate content
        print(f"✍️  Generating {self.language} content...")
        content_cache = self._generate_content(book_name, chapter, subchapter, paragraphs, force)

        # Step 3: Generate audio
        print(f"🎵 Generating audio...")
        self._generate_audio(book_name, chapter, subchapter, content_cache, force)

        # Step 4: Load and return
        result = self._load_subchapter(book_name, chapter, subchapter, content_cache)
        print(f"✅ Complete! {len(result.videos)} videos, {result.audio_count()} with audio")
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
                print("✓" if content else "skip")

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

            # Check if already generated (hash-based filename)
            if not force and self.cache.audio_exists(book, chapter, subchapter, para_hash, original_text):
                print(f"   [{idx}] {para_hash[:8]}... cached")
                idx += 1
                continue

            # Generate audio
            print(f"   [{idx}] {para_hash[:8]}... generating...", end=" ")
            audio_path = self.cache.get_audio_path(book, chapter, subchapter, para_hash, original_text)

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
            audio_path = self.cache.get_audio_path(book, chapter, subchapter, para_hash, original_text)

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
```

---

### 10. `viewer/app.py` - Flask Web App

```python
"""Web viewer for short videos."""
from flask import Flask, render_template, send_file
from pathlib import Path
from video_lib.generator import VideoGenerator

app = Flask(__name__)

@app.route("/viewer/<book>/<chapter>/<subchapter>")
def viewer(book, chapter, subchapter, language="Vietnamese"):
    """View videos for a sub-chapter."""
    gen = VideoGenerator(f"{book}.md", language=language)
    result = gen.process(chapter, subchapter)

    return render_template(
        "viewer.html",
        book=book,
        chapter=chapter,
        subchapter=subchapter,
        language=language,
        videos=result.videos,
        completion=result.completion_rate()
    )

@app.route("/audio/<book>/<chapter>/<subchapter>/<filename>")
def audio(book, chapter, subchapter, filename):
    """Serve audio file."""
    audio_path = Path(f"contents/video_content/{book}/{chapter}/{subchapter}/{filename}")
    return send_file(audio_path, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

---

## Usage

### Generate Vietnamese Videos

```python
from video_lib.generator import VideoGenerator

gen = VideoGenerator(
    "Meaningful-to-Behold.md",
    language="Vietnamese",
    llm_provider="claude"
)

result = gen.process("08_TheBenefitsofBodhichitta", "19_DEVELOPINGBODHICHITTA")
```

### Generate English Videos

```python
gen = VideoGenerator(
    "Meaningful-to-Behold.md",
    language="English",
    llm_provider="gemini"
)

result = gen.process("08_TheBenefitsofBodhichitta", "19_DEVELOPINGBODHICHITTA")
```

---

## Dependencies

```toml
# pyproject.toml
[project]
name = "video-lib"
version = "0.1.0"
dependencies = [
    "flask>=3.0.0",
]

[project.optional-dependencies]
gemini = [
    "google-generativeai>=0.8.0",
]
dev = [
    "pytest>=8.0.0",
]
```

---

## Environment Variables

```bash
# For Claude Code (no API key needed)
# claude command must be in PATH

# For Gemini (optional)
export GEMINI_API_KEY=your_key_here

# For Resona TTS
export RESONA_API_KEY=rsk_your_key_here
```

---

## Key Design Decisions

1. **Single content field** - Just `video_content` (no hook/closing structure)
2. **Hash-based filenames** - Audio files named `<hash>_<snippet>.mp3` for easy tracing
3. **Centralized paths** - `PathManager` handles all path generation (single source of truth)
4. **Shared utilities** - `utils.py` provides common functions (text processing, HTTP, etc.)
5. **DRY principle** - No code duplication across modules
6. **Combined storage** - JSON and MP3 files together in `video_content/<book>/<chapter>/<subchapter>/`
7. **Raw content folder** - `books/` for extracted book content
8. **Generic naming** - `video_lib` (not Buddhist-specific)
9. **Claude Code CLI preferred** - Uses subprocess, no API key needed
10. **Multi-language support** - Language parameter throughout
