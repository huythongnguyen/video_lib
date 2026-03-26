# Folder structure & CLI layout

### Folder structure principles

- **Separation of concerns**: keep domain logic separate from I/O, CLI wiring, and vendor integrations.
- **Functional grouping**: group by feature/domain (e.g. `audio/`, `content/`, `jobs/`, `rendering/`) rather than broad buckets.
- **Naming conventions**:
  - Prefer explicit names over `utils/` or `helpers/`.
  - Use plural for collections (`providers/`, `services/`) and singular for single-purpose modules (`config.py`).
- **Depth balance**: avoid “everything in one folder” and avoid 5+ nested levels; 2–4 levels is usually enough.

### Where to put “helpers”

If a helper exists, it should have a **home domain**:

- Path building → a `paths.py` / `path_manager.py` in the domain that owns the convention
- HTTP calls → a client module (`resona_client.py`) with retries/timeouts in one place
- JSON job loading/validation → `job_loader.py` / `schemas.py`

If you can’t name the domain, don’t create the helper yet—figure out the module boundary first.

### Recommended Python CLI pattern

- Each top-level tool/library has a `main.py` that acts as the CLI entry point.
- Keep `main.py` thin:
  - parse args / dispatch subcommands
  - load env/config
  - call domain functions (no deep business logic)

