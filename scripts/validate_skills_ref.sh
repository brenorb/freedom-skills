#!/bin/sh

set -eu

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

printf '%s\n' "$skills" | while IFS= read -r skill; do
  uvx --from git+https://github.com/agentskills/agentskills#subdirectory=skills-ref \
    skills-ref validate "$skill"
done
