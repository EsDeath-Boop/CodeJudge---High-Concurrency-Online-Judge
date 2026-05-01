#!/bin/bash
# run.sh for C++ sandbox
# Environment variables:
#   TIME_LIMIT - in seconds (default 5)
#   CODE_FILE  - path to source file

set -e

TIME_LIMIT=${TIME_LIMIT:-5}
CODE_FILE=${CODE_FILE:-/sandbox/solution.cpp}
INPUT_FILE=${INPUT_FILE:-/sandbox/input.txt}

# Compile
g++ -O2 -o /sandbox/solution "$CODE_FILE" 2>/sandbox/compile_error.txt
COMPILE_EXIT=$?

if [ $COMPILE_EXIT -ne 0 ]; then
    echo "COMPILATION_ERROR"
    cat /sandbox/compile_error.txt >&2
    exit 1
fi

# Run with timeout and input
if [ -f "$INPUT_FILE" ]; then
    timeout "$TIME_LIMIT" /sandbox/solution < "$INPUT_FILE"
else
    timeout "$TIME_LIMIT" /sandbox/solution
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 124 ]; then
    echo "TIME_LIMIT_EXCEEDED" >&2
    exit 124
fi

exit $EXIT_CODE
