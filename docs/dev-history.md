# Dev history

Internal log of **development version** bumps and notable milestones. Keep entries short; use the main changelog or release notes for user-facing releases if you add them later.

## Format

Each bump is one section, newest first.

### Template

```markdown
## x.y.z — YYYY-MM-DD

- One-line summary of what changed for this dev bump (optional bullets).
```

---

## 0.3.13 — 2026-09-29

- `run_main.sh`: fix silent no-op at the 09:00 cron slot — cron's default `PATH` (typically `/usr/bin:/bin`) doesn't include `~/.local/bin`, where `uv` is installed, so the job failed with `uv: command not found` and only ever showed up in `logs/cron.log`, not Slack. Script now prepends `$HOME/.local/bin` to `PATH` before invoking `uv`. Verified by running under `env -i PATH=/usr/bin:/bin` (cron-equivalent) and confirming a real Slack post.

## 0.3.12 — 2026-09-28

- Desktop crontab time changed `7 8 * * 1-5` → `0 9 * * 1-5` per user request (desktop is reliably on by 08:09 local, wants the alert at 09:00 instead of ~08:07). README updated to match.

## 0.3.11 — 2026-09-28

- Scheduling moved off GitHub Actions to a local Linux cron job on the team desktop: `daily-menu.yml`'s `schedule` trigger (and the now-unneeded `keepalive` job) removed, leaving `workflow_dispatch` only. GitHub's scheduler kept slipping 3-5 hours behind despite the 0.3.10 `:07` slot fix, so alerts were still landing at 11am-12pm local instead of the 08:00-09:00 target window.
- `run_main.sh` fixed: `uv run python main.py` failed with `ModuleNotFoundError` (no project deps installed); now `uv run --with-requirements requirements.txt python main.py`, `cd`s to its own directory first so cron's CWD doesn't matter.
- Desktop crontab: `7 8 * * 1-5 run_main.sh >> logs/cron.log 2>&1` (desktop timezone is already `America/Los_Angeles`, matching `MENU_DATE_TZ`). `logs/` gitignored.
- README: replaced the GitHub Actions scheduling section with local-cron setup instructions.

## 0.3.10 — 2026-09-21

- `daily-menu.yml`: `schedule` cron `30 7` → `7 8` (`timezone: America/Los_Angeles` 유지). 2026-08-26부터 GitHub 스케줄러 큐 지연이 3~5시간으로 악화돼 발송이 로컬 10:45~12:30에 이뤄졌음(8월 중순엔 23~39분 지연). 혼잡 슬롯(`:00`/`:30`)을 피한 `:07`로 옮기고 명목 시각을 08:07로 올려 목표 창(로컬 08:00~09:00) 안에서 ~53분 지연 여유 확보.

## 0.3.9 — 2026-09-01

- `keepalive.yml` removed: its action (`gautamkrishnar/keepalive-workflow`) was disabled by GitHub Staff for a ToS violation, breaking every scheduled run (`Error: Repository access blocked`).
- `daily-menu.yml`: added a `keepalive` job (`liskin/gh-workflow-keepalive@v1`, `if: github.event_name == 'schedule'`) that re-enables the workflow via the API on each scheduled run instead of a separate dummy-commit workflow.

## 0.3.8 — 2026-05-08

- `scraper.py`: scrape `MENU_DAYPART` (default `lunch`) inside `<section id="lunch">` active tab; fixes wrong menu when the first global tab was breakfast (`#lunch` URL hash is not sent to the server).
- `.env.example`: document `MENU_DAYPART`.

## 0.3.7 — 2026-05-08

- `scraper.py`: temporary NDJSON debug logging (session `3a7e89`); superseded by 0.3.8 fix verification, instrumentation removed.

## 0.3.6 — 2026-04-24

- `daily-menu.yml`: `schedule` uses `timezone: "America/Los_Angeles"` with `cron` `30 7 * * 1-5` (weekday 07:30 local LA); replaces UTC-only `30 14 * * 1-5`.

## 0.3.5 — 2026-04-24

- Consolidate version log: canonical file is `docs/dev-history.md`; `docs/development-history.md` removed. Update README link.

## 0.3.4 — 2026-04-24

- `daily-menu.yml`: `schedule` cron to Mon–Fri only (`1-5`); skips Sat/Sun in `America/Los_Angeles` at the same UTC slot (14:30 UTC aligns local weekday with UTC weekday for this time).

## 0.3.3 — 2026-04-21

- Document GitHub `schedule` best-effort delays (runs can be tens of minutes apart despite `*/5` cron).

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
