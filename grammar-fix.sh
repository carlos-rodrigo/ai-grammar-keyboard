#!/bin/bash
# Usage: echo "text to fix" | grammar-fix.sh

INPUT=$(cat)
[ -z "$INPUT" ] && exit 0

INPUT_ESCAPED=$(echo "$INPUT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read())[1:-1])')

PROMPT="Correct the following text for grammar, spelling, and punctuation. Return ONLY the corrected text, with no explanations, no preamble, and no additional comments.\n\nText: $INPUT_ESCAPED"

RESPONSE=$(curl -s --max-time 30 http://localhost:11434/api/generate \
  -d "{
    \"model\": \"llama3.2:3b\",
    \"prompt\": \"$PROMPT\",
    \"stream\": false
  }")

CORRECTED=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('response','').strip())" 2>/dev/null)

if [ -n "$CORRECTED" ]; then
    echo -n "$CORRECTED"
else
    echo -n "$INPUT"
fi
