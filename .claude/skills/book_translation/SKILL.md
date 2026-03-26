---
name: buddhist-book-translator
description: Translates Buddhist book content paragraph-by-paragraph into Vietnamese, maintaining a glossary for consistent terminology across the full book.
---

# Book Translation SKILL

This skill translates English Buddhist books into Vietnamese. It uses a job/cache architecture identical to the `short_videos` skill.

All data lives under `contents/book_translation/`:
- `contents/book_translation/jobs/<book>/<chapter>/<subchapter>/job.json`
- `contents/book_translation/cache/<book>/<chapter>/<subchapter>/cache.json`
- `contents/book_translation/output/<book>/<chapter>/<subchapter>.md`

---

## Glossary
A shared glossary lives at `book_translation/glossary.json`. Always consult it for established term translations and update it whenever a new important term is first translated.

Key translation rules:
- **Bodhichitta** → Bồ đề tâm
- **Bodhisattva** → Bồ Tát
- **Buddha** → Phật
- **Dharma** → Pháp
- **Karma** → Nghiệp
- **Samsara** → Vòng luân hồi
- **Nirvana** → Niết Bàn
- **Sangha** → Tăng đoàn
- Prefer elegant Vietnamese over literal transliteration wherever possible.
- Preserve the contemplative, reverent tone of the original.

---

## Step 1 — Pre-process (Python)
*(Script TBD — mirror the short_video prepare_job.py but writing to `contents/book_translation/`)*

---

## Step 2 — Translate (Claude Code)
For each paragraph with `"status": "needs_processing"`:
- Translate the full paragraph into Vietnamese.
- Consult the glossary for established terms.
- Update the glossary if new important terms appear.

Save to `contents/book_translation/cache/<book>/<chapter>/<subchapter>/cache.json`:
```json
{
  "<hash>": {
    "original": "...",
    "translation": "..."
  }
}
```

---

## Step 3 — Assemble Output (Python)
*(Script TBD — mirror assemble_videos.py but for translations)*
