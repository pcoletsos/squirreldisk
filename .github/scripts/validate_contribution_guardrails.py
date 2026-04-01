#!/usr/bin/env python3
"""Validate contribution guardrails for pull requests.

Checks:
- PR title format: <type>(<scope>): <summary>
- Branch naming: <actor>/<type>/<scope>/<task>-<id>
- PR body includes at least one closing issue reference
- Branch issue id is included in linked issue references
- Linked issue(s) have milestones (requires token + repo)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterable

PR_TITLE_RE = re.compile(
    r"^(feat|fix|chore|docs|refactor|perf|test|build|ci|revert)(\([a-z0-9][a-z0-9\-_/]*\))?: .+"
)
BRANCH_RE = re.compile(
    r"^([a-z0-9][a-z0-9\-]*)/"
    r"(feat|fix|chore|docs|refactor|perf|test|build|ci)/"
    r"([a-z0-9][a-z0-9\-]*)/"
    r"([a-z0-9][a-z0-9\-]*)-(\d+)$"
)
CLOSING_ISSUE_RE = re.compile(r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)\b")


@dataclass
class ValidationState:
    errors: list[str]
    warnings: list[str]

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-path", default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    parser.add_argument("--pr-number", type=int, default=None)
    return parser.parse_args()


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_json(url: str, token: str | None = None) -> dict:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_pr_payload(args: argparse.Namespace, state: ValidationState) -> dict | None:
    if args.event_path and os.path.exists(args.event_path):
        event = load_json(args.event_path)
        pr = event.get("pull_request")
        if not pr:
            state.error("No pull_request payload found in event data.")
            return None
        return pr

    if args.pr_number is None:
        state.error("No event payload found. Provide --pr-number for local validation.")
        return None
    if not args.repo:
        state.error("Missing --repo (or GITHUB_REPOSITORY).")
        return None

    pr_url = f"https://api.github.com/repos/{args.repo}/pulls/{args.pr_number}"
    try:
        return fetch_json(pr_url, args.token)
    except urllib.error.HTTPError as exc:
        state.error(f"Failed to fetch PR #{args.pr_number}: HTTP {exc.code}")
        return None
    except urllib.error.URLError as exc:
        state.error(f"Failed to fetch PR #{args.pr_number}: {exc}")
        return None


def parse_issue_ids_from_body(body: str) -> list[int]:
    return [int(match.group(1)) for match in CLOSING_ISSUE_RE.finditer(body or "")]


def validate_pr_title(title: str, state: ValidationState) -> None:
    if not PR_TITLE_RE.match(title or ""):
        state.error(
            "PR title must match '<type>(<scope>): <summary>' "
            "where type is one of feat|fix|chore|docs|refactor|perf|test|build|ci|revert."
        )


def validate_branch_name(branch_name: str, state: ValidationState) -> int | None:
    match = BRANCH_RE.match(branch_name or "")
    if not match:
        state.error(
            "Branch must match '<actor>/<type>/<scope>/<task>-<id>' "
            "using lowercase letters, digits, and hyphens."
        )
        return None
    return int(match.group(5))


def fetch_issues(repo: str, issue_ids: Iterable[int], token: str | None, state: ValidationState) -> dict[int, dict]:
    if not token:
        state.warn("No GitHub token available; skipping linked issue milestone validation.")
        return {}
    issues: dict[int, dict] = {}
    for issue_id in sorted(set(issue_ids)):
        issue_url = f"https://api.github.com/repos/{repo}/issues/{issue_id}"
        try:
            issues[issue_id] = fetch_json(issue_url, token)
        except urllib.error.HTTPError as exc:
            state.error(f"Failed to fetch linked issue #{issue_id}: HTTP {exc.code}")
        except urllib.error.URLError as exc:
            state.error(f"Failed to fetch linked issue #{issue_id}: {exc}")
    return issues


def validate_issue_milestones(issues: dict[int, dict], state: ValidationState) -> None:
    for issue_id, issue in issues.items():
        if issue.get("pull_request"):
            state.error(f"Linked reference #{issue_id} is a pull request, expected an issue.")
            continue
        milestone = issue.get("milestone")
        if milestone is None:
            state.error(
                f"Linked issue #{issue_id} has no milestone. "
                "Assign a milestone (use 'Backlog' when no thematic milestone fits)."
            )


def main() -> int:
    args = parse_args()
    state = ValidationState(errors=[], warnings=[])
    pr = get_pr_payload(args, state)
    if pr is None:
        return 1

    title = pr.get("title", "")
    body = pr.get("body") or ""
    branch_name = (pr.get("head") or {}).get("ref", "")
    linked_issue_ids = parse_issue_ids_from_body(body)

    validate_pr_title(title, state)
    branch_issue_id = validate_branch_name(branch_name, state)

    if not linked_issue_ids:
        state.error("PR body must include a closing issue reference (e.g. 'Closes #123').")
    elif branch_issue_id is not None and branch_issue_id not in linked_issue_ids:
        state.error(
            f"Branch references issue #{branch_issue_id}, but PR body closes {sorted(set(linked_issue_ids))}. "
            "Include the branch issue id in a closing reference."
        )

    if args.repo and linked_issue_ids:
        issues = fetch_issues(args.repo, linked_issue_ids, args.token, state)
        if issues:
            validate_issue_milestones(issues, state)

    for warning in state.warnings:
        print(f"WARNING: {warning}")
    if state.errors:
        for err in state.errors:
            print(f"ERROR: {err}")
        return 1

    print("Contribution guardrails validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
