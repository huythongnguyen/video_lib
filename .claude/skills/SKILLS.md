# Buddhist Content Generation — Skills Index

This is the centralized skills directory for the `buddhist-content` project.
All Claude Code tasks should reference the relevant SKILL.md from here.

---

## Available Skills

| Skill | Folder | Purpose |
|---|---|---|
| **Short Video Generator** | `short_videos/` | Full pipeline: job prep → LLM scripts → Markdown → TTS audio |
| **Book Translator** | `book_translation/` | Translate Buddhist books chapter-by-chapter into Vietnamese |
| **Resona TTS** | `resona-tts/` | Vietnamese text-to-speech via Resona API |
| **Run Claude Codes** | `run_claude_codes/` | Best practices for running Claude Code efficiently |

---

## Quick Reference — Short Video Pipeline

```bash
# Stage 1: Prepare jobs (splits book into subchapter job files)
python .claude/skills/short_videos/scripts/prepare_job.py --book <book>.md

# Stage 2: Generate scripts (Claude Code — see short_videos/SKILL.md Stage 2)
claude --dangerously-skip-permissions --print "<prompt>"

# Stage 3: Assemble Markdown
python .claude/skills/short_videos/scripts/assemble_videos.py --book <book>.md

# Stage 4: Synthesize TTS audio
set RESONA_API_KEY=rsk_...
python .claude/skills/short_videos/scripts/generate_tts.py --book <book>.md --chapter <ch> --subchapter <sub>
```

**Content lives in:** `contents/`
- `books/` - Job files (extracted book paragraphs)
- `video_content/` - Generated scripts (cache.json) + audio (MP3)

---

## Token Optimization via CLAUDE.md

**Claude Code automatically loads `CLAUDE.md`** from the project root before every session.
This means you can embed tightly-scoped task instructions directly in `CLAUDE.md` instead of
repeating them in every prompt — saving significant tokens per run.

See the root `CLAUDE.md` file for the current active task instructions.
