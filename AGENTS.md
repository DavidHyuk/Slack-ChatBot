# Agent instructions (Slack-ChatBot)

These mirror `.cursor/rules` so Agent picks them up reliably. Prefer the detailed rules there when in doubt.

## Git commit suggestions

After any meaningful code change, end the reply with a section titled exactly **Suggested git commits** and list **1–3** messages in **English**, [Conventional Commits](https://www.conventionalcommits.org/) style (`type(scope): summary`), imperative mood, ~50 chars subject, no trailing period. Do not run `git commit` unless the user asks; only suggest.

## Development version history

When bumping or introducing the canonical project version (`package.json`, `pyproject.toml`, `Cargo.toml`, `VERSION`, etc.), update **`docs/development-history.md`** in the same task: add `## x.y.z — YYYY-MM-DD` (newest first after the intro), 1–5 short bullets on why the bump happened. Trivial patch: still add one bullet (e.g. patch bump, no functional change).
