# Video Library

Generate short videos with Buddhist content and Vietnamese TTS audio from markdown books.

## Quick Start

### 1. Install

```bash
pip install -e .

# Optional: Install Gemini support
pip install -e ".[gemini]"
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```bash
# For Resona TTS (required)
RESONA_API_KEY=rsk_your_key_here

# For Gemini (optional - only if using Gemini instead of Claude Code)
GOOGLE_API_KEY=your_key_here
```

### 3. Generate Job Files

First, extract paragraphs from markdown books into structured job files:

```bash
python video_lib/scripts/generate_contents.py

# Options
python video_lib/scripts/generate_contents.py --dry-run  # Preview without writing
python video_lib/scripts/generate_contents.py --quiet    # Suppress detailed output
```

This creates `contents/books/<book>/<chapter>/<subchapter>/job.json` files.

### 4. Generate Videos

Process job files to create Vietnamese video scripts and audio:

```bash
# Basic usage (default: Vietnamese, Gemini, Vân Anh voice, Conversational style)
python video_lib_cli.py contents/books/Meaningful-to-Behold/14_Effort/08_EXAMININGTHECAUSEOFINDOLENCE/job.json

# With custom voice and content style
python video_lib_cli.py path/to/job.json --voice "Thanh Nhã" --style thought-provoking

# Use Claude Code CLI
python video_lib_cli.py path/to/job.json --llm claude

# List available options
python video_lib_cli.py --list-voices   # Show all 50+ voices
python video_lib_cli.py --list-styles   # Show all 10 content styles

# Force regeneration
python video_lib_cli.py path/to/job.json --force
```

**Output:** Generated content in `contents/video_content/<book>/<chapter>/<subchapter>/`
- `cache.json` - Video scripts
- `<hash>_<style>_<voice>_<snippet>.mp3` - Audio files

### 5. View in Browser

```bash
python video_lib/viewer/app.py
# Open http://localhost:5001
```

## Voice Options

### Recommended Buddhist Voices

| Voice | Gender | Region | Description |
|---|---|---|---|
| **Vân Anh** (default) | Female | Miền Bắc | Calm, elegant voice |
| Thanh Nhã | Female | Miền Bắc | Elegant and peaceful |
| Tuệ An | Female | Miền Nam | Wisdom and peace |
| Thuỷ Nguyên | Female | Miền Bắc | Water source, gentle |
| Suối Chậm Chạp | Female | Miền Nam | Slow stream, calm |

**50+ voices available.** Use `--list-voices` to see all options.

## Content Styles

Transform Buddhist teachings into different engaging formats:

| Style | Tone | Best For |
|---|---|---|
| **Conversational** (default) | Warm, personal | Friendly teaching style |
| Thought-Provoking | Reflective, questioning | Encouraging deep reflection |
| Claiming | Confident, assertive | Clear statements of truth |
| Storytelling | Narrative, vivid | Relatable stories and examples |
| Practical | Action-oriented | Daily practice guidance |
| Compassionate | Gentle, understanding | Support during difficulties |
| Challenging | Direct, motivating | Wake-up calls for change |
| Inspirational | Uplifting, hopeful | Motivation and encouragement |
| Philosophical | Analytical, deep | Deeper concept exploration |
| Humorous | Light, playful | Accessible through gentle humor |

Use `--list-styles` to see detailed descriptions.

## CLI Options

```bash
python video_lib_cli.py <job_file> [OPTIONS]

Required:
  job_file                 Path to job.json file

Options:
  --language TEXT          Target language (default: Vietnamese)
  --llm {claude|gemini}    LLM provider (default: gemini)
  --voice TEXT             TTS voice name (default: Vân Anh)
  --style TEXT             Content style (default: Conversational)
  --force                  Force regeneration (ignore cache)
  --list-voices            List all available voices
  --list-styles            List all content styles
```

## Project Structure

```
buddhist-content/
├── video_lib/                    # Main library
│   ├── models.py                 # Video, SubChapter, Paragraph
│   ├── parser.py                 # BookParser
│   ├── llm_client.py             # Claude Code or Gemini
│   ├── resona_client.py          # TTS client
│   ├── generator.py              # Main orchestrator
│   ├── cache.py                  # Cache manager
│   ├── paths.py                  # Path management
│   ├── prompts.py                # Prompt templates
│   ├── utils.py                  # Shared utilities
│   ├── voices.py                 # Voice enum (50+ voices)
│   ├── content_styles.py         # Content style enum
│   ├── job_processor.py          # CLI job processing
│   ├── viewer_helper.py          # Viewer utilities
│   ├── viewer/                   # Flask web app
│   │   └── app.py
│   └── scripts/                  # Utility scripts
│       ├── generate_contents.py  # Generate job.json files
│       └── rename_video_folders.py  # Rename folders to match books structure
│
├── contents/
│   ├── books/                    # Raw book content (extracted)
│   │   └── <book>/
│   │       └── XX_<chapter>/
│   │           └── XX_<subchapter>/
│   │               └── job.json
│   │
│   └── video_content/            # Generated content + audio
│       └── <book>/
│           └── XX_<chapter>/
│               └── XX_<subchapter>/
│                   ├── cache.json
│                   └── <hash>_<style>_<voice>_<snippet>.mp3
│
├── md/                           # Source books
│   └── Meaningful-to-Behold.md
│
├── video_lib_cli.py              # CLI entry point
└── pyproject.toml
```

## Python API

```python
from video_lib.generator import VideoGenerator
from video_lib.voices import ResonaVoice
from video_lib.content_styles import ContentStyle

# Create generator with custom voice and style
gen = VideoGenerator(
    "Meaningful-to-Behold.md",
    language="Vietnamese",
    llm_provider="gemini",
    voice=ResonaVoice.THANH_NHA,  # or voice name string
    content_style=ContentStyle.THOUGHT_PROVOKING  # or style name string
)

# Process a sub-chapter
result = gen.process(
    chapter="Effort",
    subchapter="EXAMININGTHECAUSEOFINDOLENCE"
)

# Check results
print(f"Generated {len(result.videos)} videos")
print(f"Completion: {result.completion_rate():.1f}%")
```

## Features

- ✅ **Multiple Voices** - 50+ Vietnamese voices, 5 recommended for Buddhist content
- ✅ **Content Styles** - 10 different writing styles for varied engagement
- ✅ **Multi-language** - Vietnamese, English, and more
- ✅ **Dual LLM Support** - Claude Code CLI (no API key) or Gemini API
- ✅ **Smart Caching** - Reuse generated content and audio
- ✅ **Hash-based Naming** - Traceable filenames with style/voice metadata
- ✅ **Web Viewer** - Browse and play generated videos
- ✅ **Clean Architecture** - DRY principles, class-based utilities

## Utility Scripts

### Generate Job Files

```bash
python video_lib/scripts/generate_contents.py [OPTIONS]

Options:
  --root PATH      Project root directory
  --dry-run        Preview without writing files
  --quiet          Suppress detailed output
```

Creates structured job files from markdown books.

### Rename Video Folders

```bash
python video_lib/scripts/rename_video_folders.py [OPTIONS]

Options:
  --root PATH      Project root directory
  --execute        Actually rename (default is dry-run)
```

Renames `video_content/` folders to match `books/` structure (XX_Name format).

## Filename Format

Audio files follow this naming convention:

```
<16-char-hash>_<style-code>_<voice-code>_<text-snippet>.mp3
```

**Example:**
```
a31d73f9600efb31_conv_vananh_when_overcome_by.mp3
│                │    │       └─ First 3 words of text
│                │    └─────── Voice code (vananh = Vân Anh)
│                └──────────── Style code (conv = Conversational)
└───────────────────────────── Paragraph hash (traceable)
```

## Job File Format

Job files are located at `contents/books/<book>/<chapter>/<subchapter>/job.json`:

```json
{
  "book": "Meaningful-to-Behold.md",
  "chapter": "## Effort",
  "subchapter": "### EXAMINING THE CAUSE OF INDOLENCE",
  "paragraphs": [
    {
      "hash": "1b142c86f6e83dee...",
      "type": "heading",
      "status": "needs_processing",
      "original": "### EXAMINING THE CAUSE OF INDOLENCE"
    },
    {
      "hash": "a31d73f9600efb31...",
      "type": "paragraph",
      "status": "needs_processing",
      "original": "When overcome by the laziness..."
    }
  ]
}
```

## Cache File Format

Generated content is stored in `contents/video_content/<book>/<chapter>/<subchapter>/cache.json`:

```json
{
  "1b142c86f6e83dee": {
    "original": "### EXAMINING THE CAUSE OF INDOLENCE",
    "video_content": null
  },
  "a31d73f9600efb31": {
    "original": "When overcome by the laziness of indolence...",
    "video_content": "Đã bao giờ bạn cảm thấy mình chỉ muốn nằm dài..."
  }
}
```

## Development

### Architecture Principles

- **DRY (Don't Repeat Yourself)** - Shared utilities in class-based modules
- **Single Responsibility** - Each module has one clear purpose
- **Centralized Path Management** - All paths generated in `PathManager`
- **Enum-based Configuration** - Type-safe voice and style selection

### Adding New Voices

Edit `video_lib/voices.py` to add new voices:

```python
NEW_VOICE = VoiceConfig(
    voice_id="voice_id_from_resona",
    name="Voice Name",
    gender="Nữ",
    region="Miền Bắc",
    recommended_for_buddhist=True,  # if suitable
    description="Description of voice"
)
```

### Adding New Content Styles

Edit `video_lib/content_styles.py`:

```python
NEW_STYLE = StyleConfig(
    name="Style Name",
    tone="Tone description",
    approach="Approach description",
    description="When to use this style"
)
```

## Troubleshooting

### GOOGLE_API_KEY not found
- Add to `.env`: `GOOGLE_API_KEY=your_key`
- Or use Claude: `--llm claude`

### RESONA_API_KEY not found
- Add to `.env`: `RESONA_API_KEY=rsk_your_key`
- Get key from https://resona.live

### Job file not found
- Run `python video_lib/scripts/generate_contents.py` first

### Audio not generating
- Check Resona API key is valid
- Check network connection
- Review error messages in CLI output

### Folder structure mismatch
- Run `python video_lib/scripts/rename_video_folders.py --execute`

## License

[Your License Here]
