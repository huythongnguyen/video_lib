## Code

### Reduce Logic Duplication

In the code structure, there are often multiple repeated patterns that should be abstracted, so that when we want to modify an abstraction, instead of modifying multiple files, we can simply modify one abstraction and the edits will automatically propagate.

**Tasks:** Identify those abstractions in the codebase, and refactor them.

### Prefer Abstraction

If multiple similar functions can be grouped under an abstraction (e.g., Python class), add those abstractions.

**Guidelines:**

1. **Identify patterns**: Look for similar logic across 2+ files
2. **Group by domain**: Text processing, HTTP requests, path generation, etc.
3. **Use classes**: Create static method classes for utility functions
4. **Clear naming**: `TextProcessor`, `HttpClient`, `PathManager`
5. **Update all usages**: Refactor all files to use the new abstractions

**When to create abstractions:**
- ✅ Same logic appears in 3+ files
- ✅ Related functions can be logically grouped
- ✅ Functions share a common theme/domain
- ✅ Changes would require editing multiple files

**When NOT to create abstractions:**
- ❌ Logic only appears in 1 file
- ❌ Functions are unrelated or serve different purposes
- ❌ Over-engineering simple one-time operations 