# CONTRIBUTING

This repository follows an issue-first, milestone-backed contribution flow.

## Live Source Of Truth

GitHub is the live source of truth for:

- issues and milestones
- pull requests and review state
- CI and release runs
- release artifacts

If markdown in the repo drifts from live GitHub state, GitHub wins.

## Contribution Workflow

For non-trivial work:

1. Find an existing issue or open a new one.
2. Ensure the issue has a milestone.
3. Use `Backlog` if no thematic milestone fits.
4. Create a branch before editing code.
5. Open a PR that links the issue and uses the required title format.
6. Merge with squash after required checks and approval.

### Branch Naming

Use this branch format:

```text
<actor>/<type>/<scope>/<task>-<id>
```

Examples:

- `codex/chore/shared/repo-contribution-operating-system-1`
- `jane/fix/scan/linux-drive-visibility-42`

Allowed `type` values:

- `feat`
- `fix`
- `chore`
- `docs`
- `refactor`
- `perf`
- `test`
- `build`
- `ci`

### PR Title Format

Use Conventional Commit style:

```text
<type>(<scope>): <summary>
```

`(<scope>)` is optional.

Examples:

- `chore(shared): add contribution guardrails`
- `fix(scan): handle empty mountpoint on linux`

### Required PR Metadata

- PR body must include at least one closing issue reference:
  - `Closes #123`
  - `Fixes #123`
  - `Resolves #123`
- The linked issue must have a milestone.
- The issue id in the branch suffix (`-<id>`) must appear in linked issue references.

## Required Checks

Protected branches require these checks:

- `contribution-guardrails`
- `frontend-build`
- `rust-check`

## Repository Map

- Web UI (React + Vite): `src/`
- Desktop shell (Tauri + Rust): `src-tauri/`
- Static assets and icons: `public/`, `src/assets/`
- GitHub automation and policy: `.github/`

## Local Validation

```bash
# Frontend type-check + build
npm ci
npm run build

# Rust formatting guardrail
cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check

# Guardrail policy check (local, with token for milestone validation)
python .github/scripts/validate_contribution_guardrails.py --pr-number <id> --repo pcoletsos/squirreldisk --token <token>
```

## Upstream Compatibility (Fork Policy)

This repository is a fork of `adileo/squirreldisk`. Keep practical upstream compatibility:

- avoid unnecessary divergence in app/runtime behavior
- keep release/tag conventions stable (`v*` tags)
- prefer additive process/docs changes over invasive product rewrites

## Quick Prompt Vocabulary

- `start <task>`: issue + milestone + branch, then begin work
- `record it`: commit current changes
- `publish it`: push current branch
- `propose it`: open or update the PR
- `land it`: squash-merge the PR after checks and approval
- `ship it`: commit + push + PR
- `finish it`: commit + push + PR + merge
- `finish it for #<id>`: canonical full-flow shorthand tied to an issue
