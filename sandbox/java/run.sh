#!/bin/sh
# run.sh for Java sandbox

TIME_LIMIT=${TIME_LIMIT:-5}
CODE_FILE=${CODE_FILE:-/sandbox/Solution.java}
INPUT_FILE=${INPUT_FILE:-/sandbox/input.txt}

# Compile
javac "$CODE_FILE" -d /sandbox 2>/sandbox/compile_error.txt
COMPILE_EXIT=$?

if [ $COMPILE_EXIT -ne 0 ]; then
    echo "COMPILATION_ERROR"
    cat /sandbox/compile_error.txt >&2
    exit 1
fi

# Run with timeout and memory limit
if [ -f "$INPUT_FILE" ]; then
    timeout "$TIME_LIMIT" java -Xmx256m -cp /sandbox Solution < "$INPUT_FILE"
else
    timeout "$TIME_LIMIT" java -Xmx256m -cp /sandbox Solution
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 124 ]; then
    echo "TIME_LIMIT_EXCEEDED" >&2
    exit 124
fi

exit $EXIT_CODE
