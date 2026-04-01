# Copilot Instructions

Read `CONTRIBUTING.md` before proposing edits.

Contribution guardrails for this repository:

- Use issue-first workflow with milestones (`Backlog` as fallback).
- Use branch naming format: `<actor>/<type>/<scope>/<task>-<id>`.
- Use PR title format: `<type>(<scope>): <summary>`.
- Include closing issue references in PR body (`Closes #<id>`, etc.).
- Keep changes compatible with fork/upstream behavior where practical.
- Avoid reverting unrelated edits in a shared working tree.

Repository layout:

- React/Vite frontend: `src/`
- Tauri/Rust backend: `src-tauri/`
- CI/policy automation: `.github/`
