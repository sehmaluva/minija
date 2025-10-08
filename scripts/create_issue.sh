#!/usr/bin/env bash
# Simple helper to create GitHub issues using the `gh` CLI.
# Usage examples:
#   ./scripts/create_issue.sh -t "Bug: cannot login" -b "Steps to reproduce..." -l "bug,high" -a "sehmaluva"
#   ./scripts/create_issue.sh --title "Feature: export" --body "Please add CSV export" --labels "enhancement"

set -euo pipefail

PROG_NAME="$(basename "$0")"
DEFAULT_ASSIGNEE="sehmaluva"
DEFAULT_LABELS="triage"

usage() {
  cat <<EOF
Usage: $PROG_NAME -t "title" [-b "body"] [-l "label1,label2"] [-a "assignee1,assignee2"]

Options:
  -t, --title       Issue title (required)
  -b, --body        Issue body/description (optional)
  -l, --labels      Comma-separated labels (optional). Defaults to: ${DEFAULT_LABELS}
  -a, --assignees   Comma-separated assignees (optional). Defaults to: ${DEFAULT_ASSIGNEE}
  -p, --priority    Priority: high|medium|low (optional). Defaults to medium.
  -h, --help        Show this help

Examples:
  $PROG_NAME -t "Bug: crash on save" -b "Steps..." -l "bug,urgent" -a "sehmaluva"

Make sure you have the GitHub CLI installed and authenticated (gh auth login).
EOF
}

# Parse args
TITLE=""
BODY=""
LABELS=""
ASSIGNEES=""
PRIORITY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--title)
      TITLE="$2"
      shift 2
      ;;
    -b|--body)
      BODY="$2"
      shift 2
      ;;
    -l|--labels)
      LABELS="$2"
      shift 2
      ;;
    -p|--priority)
      PRIORITY="$2"
      shift 2
      ;;
    -a|--assignees)
      ASSIGNEES="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 2
      ;;
  esac
done

if [ -z "$TITLE" ]; then
  echo "Error: title is required"
  usage
  exit 2
fi

# defaults
if [ -z "$LABELS" ]; then
  LABELS="$DEFAULT_LABELS"
fi
if [ -z "$ASSIGNEES" ]; then
  ASSIGNEES="$DEFAULT_ASSIGNEE"
fi

# handle priority
if [ -z "$PRIORITY" ]; then
  PRIORITY="medium"
fi
PRIORITY_LOWER=$(echo "$PRIORITY" | tr '[:upper:]' '[:lower:]')
case "$PRIORITY_LOWER" in
  high|medium|low)
    PRIORITY_LABEL="priority:$PRIORITY_LOWER"
    ;;
  *)
    echo "Unknown priority: $PRIORITY. Use high, medium, or low."
    exit 2
    ;;
esac

# append priority label if not already present
if [[ ",${LABELS}," != *",${PRIORITY_LABEL},"* ]]; then
  LABELS="${LABELS},${PRIORITY_LABEL}"
fi

# Ensure gh is available
if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install it from https://cli.github.com/ and authenticate (gh auth login)."
  exit 1
fi

# Build gh command
GH_CMD=(gh issue create --title "$TITLE")
if [ -n "$BODY" ]; then
  GH_CMD+=(--body "$BODY")
fi
# gh accepts comma-separated labels and assignees
GH_CMD+=(--label "$LABELS" --assignee "$ASSIGNEES")

# Execute
echo "Creating issue with title: $TITLE"
# shellcheck disable=SC2086
eval "${GH_CMD[*]}"

echo "Done."
