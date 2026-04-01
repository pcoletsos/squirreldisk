# AGENTS.md

Read `CONTRIBUTING.md` first. It is the canonical workflow contract for this repo.

## Repo Map

- UI app: `src/`
- Tauri/Rust backend: `src-tauri/`
- Workflow and policy automation: `.github/`
- Static assets: `public/`, `src/assets/`

## Hard Constraints

- GitHub is the source of truth for issues, milestones, CI, and releases.
- Non-trivial work must flow through issue -> milestone -> branch -> PR.
- Use branch format from `CONTRIBUTING.md`:
  - `<actor>/<type>/<scope>/<task>-<id>`
- Keep fork compatibility with `adileo/squirreldisk` where practical.
- Do not revert unrelated changes from other collaborators.

## Useful Commands

```bash
npm ci
npm run build
cargo check --manifest-path src-tauri/Cargo.toml
python .github/scripts/validate_contribution_guardrails.py --help
```
