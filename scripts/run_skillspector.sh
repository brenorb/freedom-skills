#!/usr/bin/env bash

set -euo pipefail

if ! command -v uvx >/dev/null 2>&1; then
  echo "uvx is required to run SkillSpector." >&2
  exit 1
fi

status=0

while IFS= read -r skill; do
  echo "Scanning ${skill}"
  if ! uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
    skillspector scan "${skill}" --no-llm \
    --baseline .skillspector-baseline.yaml; then
    status=1
  fi
done < <(find skills -mindepth 1 -maxdepth 1 -type d | sort)

exit "${status}"
