#!/bin/sh

set -eu

STRICT_SKILLS_REF="${STRICT_SKILLS_REF:-0}"
SKILLS_REF_SOURCE="${SKILLS_REF_SOURCE:-git+https://github.com/agentskills/agentskills#subdirectory=skills-ref}"

if ! command -v uvx >/dev/null 2>&1; then
  echo "uvx is required to run skills-ref validation." >&2
  exit 1
fi

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <path> [<path> ...]" >&2
  exit 1
fi

skills=""

for path in "$@"; do
  case "$path" in
    skills/*)
      skill_dir=$(printf '%s\n' "$path" | cut -d/ -f1-2)
      ;;
    *)
      continue
      ;;
  esac

  if [ ! -f "$skill_dir/SKILL.md" ]; then
    continue
  fi

  case "
$skills
" in
    *"
$skill_dir
"*) ;;
    *)
      skills="${skills}
$skill_dir"
      ;;
  esac
done

skills=$(printf '%s\n' "$skills" | sed '/^$/d')

if [ -z "$skills" ]; then
  echo "No touched skills to validate."
  exit 0
fi

echo "Validating skills with skills-ref:"
printf ' - %s\n' $skills

bootstrap_failed=0
validation_failed=0
skill_list=$(mktemp)
printf '%s\n' "$skills" >"$skill_list"

while IFS= read -r skill; do
  log_file=$(mktemp)
  if uvx --from "$SKILLS_REF_SOURCE" skills-ref validate "$skill" >"$log_file" 2>&1; then
    cat "$log_file"
    rm -f "$log_file"
    continue
  fi

  if grep -Eiq 'timed out|connection|dns|certificate|tls|resolve|download|clone|network|transport|temporary failure|could not fetch|no route to host' "$log_file"; then
    bootstrap_failed=1
    echo "skills-ref bootstrap failed while validating $skill." >&2
    cat "$log_file" >&2
    rm -f "$log_file"
    if [ "$STRICT_SKILLS_REF" = "1" ]; then
      exit 1
    fi
    echo "Skipping skills-ref locally because the validator could not be fetched or started. CI should run with STRICT_SKILLS_REF=1." >&2
    continue
  fi

  validation_failed=1
  cat "$log_file" >&2
  rm -f "$log_file"
done <"$skill_list"

rm -f "$skill_list"

if [ "$validation_failed" -ne 0 ]; then
  exit 1
fi

if [ "$bootstrap_failed" -ne 0 ] && [ "$STRICT_SKILLS_REF" = "1" ]; then
  exit 1
fi
