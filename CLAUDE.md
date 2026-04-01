# CLAUDE.md

Use `CONTRIBUTING.md` as the canonical operating contract for this repository.

Minimum expectations:

- non-trivial work starts from a GitHub issue with a milestone (`Backlog` fallback)
- branch naming follows `<actor>/<type>/<scope>/<task>-<id>`
- PR titles follow `<type>(<scope>): <summary>`
- PR body links issue(s) with a closing keyword (`Closes #<id>`, `Fixes #<id>`, `Resolves #<id>`)
- do not discard unrelated in-flight edits from other contributors

Repo structure:

- `src/` (React + Vite)
- `src-tauri/` (Rust + Tauri)
- `.github/` (workflows, templates, contribution guardrails)
