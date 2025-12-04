#!/bin/bash
set -euo pipefail

INPUT=$(mktemp input.XXXXXXXX)
trap 'rm -f "$INPUT"' EXIT

cat <<'EOF' > "$INPUT"
@import "tailwindcss" source(none);
@source ".venv/lib/python3.12/site-packages/crispy_tailwind"
EOF

# not perfect, but good enough for now
# doing it properly would require a full CSS parser
npx @tailwindcss/cli -i "$INPUT" \
  | grep -F '{' \
  | sed -n '/^@layer utilities/,/^@property/p' \
  | grep '^  \.' \
  | sed -e 's/^  \.\(.*\) {/\1/' -e 's/\\:/:/' \
  | tr '\n' ' '
