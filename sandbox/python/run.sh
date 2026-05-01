#!/bin/bash
# run.sh for Python sandbox

set -e

TIME_LIMIT=${TIME_LIMIT:-5}
CODE_FILE=${CODE_FILE:-/sandbox/solution.py}
INPUT_FILE=${INPUT_FILE:-/sandbox/input.txt}

# Run with timeout
if [ -f "$INPUT_FILE" ]; then
    timeout "$TIME_LIMIT" python3 "$CODE_FILE" < "$INPUT_FILE"
else
    timeout "$TIME_LIMIT" python3 "$CODE_FILE"
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 124 ]; then
    echo "TIME_LIMIT_EXCEEDED" >&2
    exit 124
fi

exit $EXIT_CODE
