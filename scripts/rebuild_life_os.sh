#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Missing .venv/bin/python. Create the virtualenv first." >&2
  exit 1
fi

.venv/bin/python - <<'PY'
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import pathlib

env_path = pathlib.Path(".env")
lines = env_path.read_text().splitlines() if env_path.exists() else []
now = datetime.now(ZoneInfo("Europe/Paris"))
quarter = ((now.month - 1) // 3) + 1
dynamic = {
    "CURRENT_WEEK": f"W{now:%V}",
    "CURRENT_TRIMESTER": f"T{quarter} {now:%Y}",
    "CURRENT_DATE": f"{now:%Y-%m-%d}",
}
filtered = [line for line in lines if not any(line.startswith(f"{key}=") for key in dynamic)]
filtered.extend(f"{key}={value}" for key, value in dynamic.items())
env_path.write_text("\n".join(filtered).rstrip() + "\n")
print(f"Calendar context set to {dynamic['CURRENT_WEEK']} / {dynamic['CURRENT_TRIMESTER']} / {dynamic['CURRENT_DATE']}")
PY

echo "[1/3] Fetching Notion data"
.venv/bin/python scripts/fetch_notion.py

echo "[2/3] Transforming snapshots"
.venv/bin/python scripts/transform.py

echo "[3/3] Building HTML embeds"
.venv/bin/python scripts/build_html.py

echo "[4/4] Verifying outputs"
.venv/bin/python scripts/verify_build.py

echo "life_os rebuild complete."
