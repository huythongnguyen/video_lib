---
name: generate-video
description: Generate short video content and audio from Buddhist texts using the video_lib CLI with custom voices and content styles.
---

# Generate Video Content

Process Buddhist book content into Vietnamese short video scripts with TTS audio.

## Quick Usage

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
```

## What It Does

The CLI processes job.json files through this pipeline:

1. **Parse**: Reads book, chapter, subchapter, and paragraph data from job.json
2. **Generate Content**: Creates Vietnamese video scripts using LLM (with selected style)
3. **Generate Audio**: Synthesizes speech using Resona TTS (with selected voice)
4. **Cache**: Saves to `contents/video_content/<book>/<chapter>/<subchapter>/`
   - `cache.json` - Video scripts
   - `<hash>_<style>_<voice>_<snippet>.mp3` - Audio files

## Prerequisites

1. **Environment Variables** (`.env` file):
   - `RESONA_API_KEY=rsk_your_key_here` (required)
   - `GOOGLE_API_KEY=your_key_here` (only if using Gemini)

2. **Job Files**: Generate from markdown books first:
   ```bash
   python video_lib/scripts/generate_contents.py
   ```

## Complete Documentation

**For full documentation, see:** [`README.md`](../../../README.md)

The README includes:
- Voice options (50+ voices, 5 recommended for Buddhist content)
- Content styles (10 different writing approaches)
- CLI options reference
- Filename format explanation
- Project structure
- Python API usage
- Troubleshooting guide

## Related Skills

- **resona-tts**: Resona TTS API details
- **book_translation**: Translate Buddhist books to Vietnamese
