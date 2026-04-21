#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Missing .venv/bin/python. Create the virtualenv first." >&2
  exit 1
fi

echo "[1/3] Fetching Notion data"
.venv/bin/python scripts/fetch_notion.py

echo "[2/3] Transforming snapshots"
.venv/bin/python scripts/transform.py

echo "[3/3] Building HTML embeds"
.venv/bin/python scripts/build_html.py

echo "life_os rebuild complete."
