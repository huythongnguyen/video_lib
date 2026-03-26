---
name: run-claude-codes
description: Hard-learned operational knowledge for running Claude Code efficiently against the buddhist-content workflow — covering correct commands, permission modes, path pitfalls, and best practices.
---

# Running Claude Code — Operational Guide

This skill documents lessons learned from running Claude Code as a non-interactive agent for the buddhist-content pipeline.

---

## ✅ Correct Command to Run Non-Interactively

**This is the only reliable non-interactive invocation:**

```bash
claude --dangerously-skip-permissions --print "<your prompt here>"
```

Run from: `buddhist-content/` root.

- `--dangerously-skip-permissions` — skips all "Do you want to...?" confirmation prompts for file writes and shell commands.
- `--print` — runs in non-interactive/headless mode and prints the response to stdout, then exits cleanly.
- **Do NOT use `claude code --dangerously-skip-permissions`** (that opens the interactive TUI and requires Enter to confirm the prompt).
- **Do NOT use `-p` flag** — use `--print` instead.

---

## 📁 Critical Path Rules (as of March 2026)

All content data lives under `contents/short_videos/`, **not** under `short_video/` or root-level `jobs/`:

| Resource | Path |
|---|---|
| Job files | `contents/short_videos/jobs/<book>/<chapter>/<subchapter>/job.json` |
| Cache files | `contents/short_videos/cache/<book>/<chapter>/<subchapter>/cache.json` |
| Output files | `contents/short_videos/output/<book>/<chapter>/<subchapter>.md` |
| Source books | `md/<book_name>.md` |
| Python scripts | `short_video/scripts/prepare_job.py`, `short_video/scripts/assemble_videos.py` |
| Skill files | `.claude/skills/<skill_name>/SKILL.md` |

---

## 📝 Standard Prompt Template

When dispatching Claude Code to process a sub-chapter:

```
Please run the buddhist-video-generator workflow exactly as described in .claude/skills/short_videos/SKILL.md.
Process all paragraphs found in contents/short_videos/jobs/<book>/<chapter>/<subchapter>/job.json,
and save the results to contents/short_videos/cache/<book>/<chapter>/<subchapter>/cache.json.
```

---

## ⚠️ Common Mistakes to Avoid

1. **Wrong cache path**: Claude often tries to write to `cache/...` (root) or `short_video/cache/...` instead of `contents/short_videos/cache/...`. Always be explicit in the prompt.
2. **Wrong script path**: Run scripts as `python short_video/scripts/prepare_job.py`, not `python scripts/prepare_job.py`.
3. **Interactive mode with prompt**: `claude code --dangerously-skip-permissions` opens the TUI — you must then type and Enter your prompt. Prefer `--print` for automation.
4. **mkdir prompts**: Even with `--dangerously-skip-permissions`, some shell commands may still prompt. Using `--print` avoids this entirely.

---

## 🔄 Full Workflow Sequence

```bash
# Step 1: Prepare jobs for a book
python short_video/scripts/prepare_job.py --book Meaningful-to-Behold.md

# Step 2: Process one sub-chapter with Claude
claude --dangerously-skip-permissions --print "Process jobs/... per .claude/skills/short_videos/SKILL.md"

# Step 3: Assemble output
python short_video/scripts/assemble_videos.py --book Meaningful-to-Behold.md
```
