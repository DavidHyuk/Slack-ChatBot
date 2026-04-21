# Development history

Internal log of **development version** bumps and notable milestones. Keep entries short; use the main changelog or release notes for user-facing releases if you add them later.

## Format

Each bump is one section, newest first.

### Template

```markdown
## x.y.z — YYYY-MM-DD

- One-line summary of what changed for this dev bump (optional bullets).
```

---

## 0.3.2 — 2026-04-21

- Actions: explicit `workflow_dispatch: {}` and `schedule` before `workflow_dispatch` in `menu-bot-frequent-schedule.yml` (and `daily-menu.yml`) for reliable trigger parsing.

## 0.3.1 — 2026-04-21

- `menu-bot-frequent-schedule.yml`: use `*/5 * * * *` (GitHub minimum schedule interval); document that sub-5-minute `cron` is not supported.

## 0.3.0 — 2026-04-21

- `TARGET_URL` supports `{date}` (default `MENU_DATE_TZ` / `America/Los_Angeles`) for Bon Appétit `/cafe/YYYY-MM-DD/` URLs.
- Scheduled Actions: dual UTC cron with local 8am window guard; `workflow_dispatch` bypasses the window.

## 0.2.0 — 2026-04-21

- GitHub Actions: `daily-menu.yml` runs once per day by default (02:00 UTC); added `menu-bot-frequent-schedule.yml` for manual runs and optional every-minute `cron` (commented until enabled for testing).
- Documented Actions setup and testing workflow notes in README.

## 0.1.0 — 2026-04-20

- Initial project setup: Added `requirements.txt`, `.env.example`, and initialized development history.
