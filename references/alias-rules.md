# Alias rules

Aliases must start with `claude-` and map to exactly one target.

- Existing `claude-*` IDs are preserved.
- `gpt-X.Y-suffix` becomes `claude-oXY-suffix`.
- `gemini-X.Y-suffix` becomes `claude-gXY-suffix`.
- Other IDs are normalized and prefixed with `claude-`.
- Explicit aliases override generation.
- The same target may appear once as visible and once as a hidden compatibility alias.
- Duplicate targets inside one visibility group and aliases mapping to different targets are rejected.

Generated aliases are a convenience, not a protocol guarantee. Pin an explicit alias when external clients depend on a stable name.
