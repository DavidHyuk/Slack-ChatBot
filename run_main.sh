#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
# cron's default PATH doesn't include ~/.local/bin, where uv lives.
export PATH="$HOME/.local/bin:$PATH"
uv run --with-requirements requirements.txt python main.py