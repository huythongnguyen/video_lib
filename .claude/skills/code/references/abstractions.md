# Abstractions & duplication reduction

### Goal

Reduce repeated logic so changes happen in **one place** instead of many.

### When to create an abstraction

- Same logic appears in **2+ places** (or it’s clearly trending that way)
- Multiple functions share a **single domain** (e.g. “audio providers”, “job JSON parsing”, “path conventions”)
- A future change would require editing **multiple call sites**
- You can define a stable interface (inputs/outputs) and hide provider-specific details

### When NOT to create an abstraction

- Logic appears in **one place** and is unlikely to spread
- The functions aren’t cohesive (forcing them together harms readability)
- The abstraction would be a thin wrapper that just renames functions without reducing complexity

### What “good abstraction” looks like

- **Domain-grouped** modules/classes: `ResonaClient`, `JobLoader`, `ContentStyleRegistry`
- **Stable boundary**: call sites don’t need to know internal details (HTTP, file formats, retries)
- **Single responsibility**: one module owns one concept
- **Clear naming**: avoid vague buckets like `helpers.py`/`misc.py`

### Refactoring checklist

- Identify repeated patterns across files
- Pick the owning domain module (don’t create cross-domain dumping grounds)
- Move logic behind a small public API (functions/classes)
- Update all call sites to use the new API
- Delete dead/duplicated code after migration

