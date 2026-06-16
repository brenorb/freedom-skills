#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <media-or-url> [destination]" >&2
  exit 1
fi

input=$1
destination=${2:--}

exec fscript "$input" "$destination" --text=plain -D
