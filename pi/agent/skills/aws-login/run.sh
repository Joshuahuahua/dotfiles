#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <aws-profile>" >&2
  exit 1
fi

profile="$1"

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI not found. Install it first." >&2
  exit 1
fi

aws sso login --profile "$profile"
