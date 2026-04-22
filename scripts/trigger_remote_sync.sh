#!/usr/bin/env bash
set -euo pipefail

WORKFLOW_FILE="daily-sync.yml"
WATCH_RUN="${1:-}"

echo "Triggering GitHub Actions workflow ${WORKFLOW_FILE} on main..."
gh workflow run "${WORKFLOW_FILE}" --ref main

echo "Workflow dispatched."

if [[ "${WATCH_RUN}" == "--watch" ]]; then
  sleep 3
  RUN_ID="$(gh run list --workflow "${WORKFLOW_FILE}" --limit 1 --json databaseId --jq '.[0].databaseId')"
  if [[ -z "${RUN_ID}" ]]; then
    echo "Unable to resolve latest run id." >&2
    exit 1
  fi
  echo "Watching run ${RUN_ID}..."
  gh run watch "${RUN_ID}" --interval 5 --exit-status
else
  echo "Use: bash scripts/trigger_remote_sync.sh --watch"
fi
