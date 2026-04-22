#!/usr/bin/env python3
"""
Print America/Los_Angeles wall time for fixed UTC cron minutes used by GitHub workflows.

  python3 scripts/pacific_cron_preview.py
  python3 scripts/pacific_cron_preview.py --date 2026-01-15   # PST 예시
  python3 scripts/pacific_cron_preview.py --date 2026-04-22   # PDT 예시
"""
from __future__ import annotations

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

LA = ZoneInfo("America/Los_Angeles")
# (label, UTC hour, minute) — daily-menu.yml / test 워크플로와 맞출 것
SLOTS = (
    ("daily-menu prod (UTC 15:05, ~8am PDT / ~7am PST)", 15, 5),
    ("~10am PDT test workflow (UTC 17:05)", 17, 5),
)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--date",
        help="Resolve DST as of this calendar date in LA (YYYY-MM-DD). Default: today UTC date at LA midnight edge case avoided by using noon LA.",
    )
    args = p.parse_args()

    if args.date:
        y, m, d = (int(x) for x in args.date.split("-", 2))
        base = datetime(y, m, d, 12, 0, tzinfo=LA)
    else:
        base = datetime.now(LA)

    print(f"Reference local date in {LA.key}: {base.date()}\n")
    for label, uh, um in SLOTS:
        utc = datetime(base.year, base.month, base.day, uh, um, tzinfo=ZoneInfo("UTC"))
        local = utc.astimezone(LA)
        dst = local.dst()
        dst_note = "PDT" if (dst and dst.total_seconds()) else "PST" if dst is not None else "?"
        print(f"{label}")
        print(f"  UTC  {utc.strftime('%Y-%m-%d %H:%M')}Z")
        print(f"  LA   {local.strftime('%Y-%m-%d %H:%M')} ({dst_note})\n")


if __name__ == "__main__":
    main()
