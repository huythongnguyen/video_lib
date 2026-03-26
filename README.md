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

# For Gemini (optional — use one of these)
GOOGLE_API_KEY=your_key_here
# or
GEMINI_API_KEY=your_key_here

# Optional: override Gemini model id
# GEMINI_MODEL=gemini-2.0-flash
```

### 3. Generate Job Files

Extract paragraphs from markdown books into structured job files:

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
# Basic usage (default: Vietnamese, Gemini, HO_MIN_MANG voice, Conversational style)
python video_lib_cli.py contents/books/Meaningful-to-Behold/14_Effort/08_EXAMININGTHECAUSEOFINDOLENCE/job.json

# With custom voice and content style (enum names recommended)
python video_lib_cli.py path/to/job.json --voice TUE_AN --style COMPASSIONATE

# Use Claude Code CLI
python video_lib_cli.py path/to/job.json --llm claude

# List available options
python video_lib_cli.py --list-voices   # Show all 50+ voices
python video_lib_cli.py --list-styles   # Show all 10 content styles

# Force regeneration
python video_lib_cli.py path/to/job.json --force
```

**Output:** Generated content in `contents/video_content/<book>/<chapter>/<subchapter>/`

- `cache.json` — Video scripts
- `<hash>_<style>_<voice>_<snippet>.mp3` — Audio files

### 5. View in Browser

```bash
python video_lib/viewer/app.py
# Open http://localhost:5001
```

## Voice Options

### Recommended Buddhist Voices

Default CLI voice is **Hổ Mịn Màng** (`HO_MIN_MANG`). Other calm options:

| Voice | Gender | Region | Description |
|---|---|---|---|
| **Hổ Mịn Màng** (CLI default) | Male | Miền Bắc | Soft, smooth tone |
| Vân Anh | Female | Miền Bắc | Calm, elegant |
| Thanh Nhã | Female | Miền Bắc | Elegant and peaceful |
| Tuệ An | Female | Miền Nam | Wisdom and peace |
| Thuỷ Nguyên | Female | Miền Bắc | Gentle |
| Suối Chậm Chạp | Female | Miền Nam | Slow stream, calm |

**50+ voices available.** Use `--list-voices` to see all options. Pass `--voice` as an enum name (e.g. `HO_MIN_MANG`, `VAN_ANH`).

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

Use `--list-styles` for details. Pass `--style` as an enum name (e.g. `COMPASSIONATE`).

## CLI Options

```bash
python video_lib_cli.py <job_file> [OPTIONS]

Required:
  job_file                 Path to job.json file

Options:
  --language TEXT          Target language (default: Vietnamese)
  --llm {claude|gemini}    LLM provider (default: gemini)
  --voice TEXT             TTS voice enum name (default: HO_MIN_MANG)
  --style TEXT             Content style enum name (default: CONVERSATIONAL)
  --force                  Force regeneration (ignore cache)
  --list-voices            List all available voices
  --list-styles            List all content styles
```

## Project Structure

```
buddhist-content/
├── video_lib/                    # Main library
│   ├── models.py
│   ├── parser.py
│   ├── generator.py
│   ├── job_processor.py
│   ├── utils.py
│   ├── audio/                    # TTS & voices
│   │   ├── resona_client.py
│   │   └── voices.py
│   ├── content/                  # Prompts & styles
│   │   ├── prompts.py
│   │   └── content_styles.py
│   ├── llm/
│   │   └── client.py             # Claude Code or Gemini
│   ├── storage/
│   │   ├── cache.py
│   │   └── paths.py
│   ├── viewer/                   # Flask web app
│   │   ├── app.py
│   │   ├── viewer_helper.py
│   │   └── templates/
│   └── scripts/                  # Utility scripts
│       ├── generate_contents.py
│       └── rename_video_folders.py
│
├── contents/
│   ├── books/                    # Book jobs (extracted)
│   │   └── <book>/XX_<chapter>/XX_<subchapter>/job.json
│   └── video_content/            # Generated cache + audio
│       └── <book>/...
│
├── md/                           # Source markdown books
├── video_lib_cli.py              # CLI entry point
├── pyproject.toml
└── README.md
```

## Python API

```python
from pathlib import Path
from video_lib.generator import VideoGenerator
from video_lib.audio.voices import ResonaVoice
from video_lib.content.content_styles import ContentStyle

gen = VideoGenerator(
    "Meaningful-to-Behold.md",
    language="Vietnamese",
    llm_provider="gemini",
    voice=ResonaVoice.THANH_NHA,
    content_style=ContentStyle.THOUGHT_PROVOKING,
    root_dir=Path.cwd(),
)

result = gen.process(
    chapter="Effort",
    subchapter="EXAMININGTHECAUSEOFINDOLENCE",
)

print(f"Generated {len(result.videos)} videos")
print(f"Completion: {result.completion_rate():.1f}%")
```

## Features

- **Multiple voices** — 50+ Vietnamese voices; several recommended for Buddhist content
- **Content styles** — 10 writing styles for varied engagement
- **Multi-language** — Vietnamese, English, and more
- **Dual LLM support** — Claude Code CLI or Gemini API
- **Caching** — Reuse generated content and audio
- **Hash-based naming** — Traceable filenames with style/voice metadata
- **Web viewer** — Browse and play generated clips
- **Modular layout** — `audio/`, `content/`, `llm/`, `storage/`, `viewer/`

## Utility Scripts

### Generate job files

```bash
python video_lib/scripts/generate_contents.py [OPTIONS]

Options:
  --root PATH      Project root directory
  --dry-run        Preview without writing files
  --quiet          Suppress detailed output
```

### Rename video folders

```bash
python video_lib/scripts/rename_video_folders.py [OPTIONS]

Options:
  --root PATH      Project root directory
  --execute        Actually rename (default is dry-run)
```

Renames `contents/video_content/` folders to match `contents/books/` (`XX_Name` format).

## Filename format

Audio files use:

```
<16-char-hash>_<style-code>_<voice-code>_<text-snippet>.mp3
```

Example:

```
a31d73f9600efb31_conv_ho_min_mang_when_overcome_by.mp3
```

## Job file format

`contents/books/<book>/<chapter>/<subchapter>/job.json`:

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

## Cache file format

`contents/video_content/<book>/<chapter>/<subchapter>/cache.json` maps paragraph hashes to generated text.

## Development

### Architecture

- Shared utilities in `video_lib.utils`
- Paths and audio naming in `video_lib.storage.paths.PathManager`
- Voice and style enums in `video_lib.audio.voices` and `video_lib.content.content_styles`

### Adding voices

Edit `video_lib/audio/voices.py` and add a `VoiceConfig` entry on `ResonaVoice`.

### Adding content styles

Edit `video_lib/content/content_styles.py` and add a `StyleConfig` entry on `ContentStyle`.

## Troubleshooting

### Gemini API key not found

- Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` in `.env`, or use `--llm claude`.

### RESONA_API_KEY not found

- Add `RESONA_API_KEY=rsk_...` to `.env` (see https://resona.live).

### Job file not found

- Run `python video_lib/scripts/generate_contents.py` first.

### Folder structure mismatch

- Run `python video_lib/scripts/rename_video_folders.py --execute` after reviewing dry-run output.

## License

[Your License Here]
