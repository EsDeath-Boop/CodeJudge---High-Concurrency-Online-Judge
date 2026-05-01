"""
verdict_engine.py
Stateless verdict engine — called by the worker for each submission.
Fetches test cases from DB (preferred) or S3, runs them in Docker sandboxes,
and returns a structured verdict with per-case details.
"""

import json
import logging
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import docker

log = logging.getLogger("verdict_engine")

try:
    docker_client = docker.from_env()
except Exception as e:
    docker_client = None
    log.warning(f"Docker not available: {e}")

SANDBOX_IMAGES = {
    "cpp":    os.getenv("SANDBOX_IMAGE_CPP",    "codejudge-cpp"),
    "python": os.getenv("SANDBOX_IMAGE_PYTHON", "codejudge-python"),
    "java":   os.getenv("SANDBOX_IMAGE_JAVA",   "codejudge-java"),
}

CODE_FILENAMES = {
    "cpp":    "solution.cpp",
    "python": "solution.py",
    "java":   "Solution.java",
}

TERMINAL_VERDICTS = {
    "ACCEPTED", "WRONG_ANSWER", "TIME_LIMIT_EXCEEDED",
    "MEMORY_LIMIT_EXCEEDED", "COMPILATION_ERROR", "RUNTIME_ERROR",
}


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class TestCaseResult:
    index: int
    verdict: str                  # AC / WA / TLE / MLE / RE / CE
    runtime_ms: float
    memory_kb: float
    stdout: str = ""
    stderr: str = ""
    expected: str = ""
    actual: str = ""
    is_sample: bool = False


@dataclass
class VerdictResult:
    status: str                   # final status for DB
    verdict: str
    runtime_ms: float
    memory_kb: float
    test_cases_passed: int
    test_cases_total: int
    stderr: str
    case_results: list[TestCaseResult] = field(default_factory=list)


# ── Sandbox runner ─────────────────────────────────────────────────────────────

def run_sandbox(
    
    language: str,
    code: str,
    input_data: str,
    time_limit: int,
    memory_limit: int,
) -> dict:
    """
    Spin up a Docker container, run code, return results.
    Container is always destroyed after execution.
    """
    if docker_client is None:
        return {
            "stdout": "Mock Output",
            "stderr": "",
            "exit_code": 0,
            "runtime_ms": 1,
            "memory_kb": 0,
        }
    image = SANDBOX_IMAGES[language]
    code_filename = CODE_FILENAMES[language]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / code_filename).write_text(code, encoding="utf-8")
        (tmppath / "input.txt").write_text(input_data, encoding="utf-8")

        env = {
            "TIME_LIMIT": str(time_limit),
            "CODE_FILE":  f"/sandbox/{code_filename}",
            "INPUT_FILE": "/sandbox/input.txt",
        }

        start = time.monotonic()
        container = None

        try:
            container = docker_client.containers.run(
                image=image,
                environment=env,
                volumes={tmpdir: {"bind": "/sandbox", "mode": "rw"}},
                network_mode="none",
                mem_limit=f"{memory_limit}m",
                memswap_limit=f"{memory_limit}m",
                pids_limit=64,
                cpu_period=100_000,
                cpu_quota=100_000,
                detach=True,
            )

            try:
                result = container.wait(timeout=time_limit + 20)
            except Exception:
                container.kill()
                return {
                    "stdout": "",
                    "stderr": "TIME_LIMIT_EXCEEDED",
                    "exit_code": 124,
                    "runtime_ms": (time.monotonic() - start) * 1000,
                    "memory_kb": 0,
                }

            runtime_ms = (time.monotonic() - start) * 1000
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
            exit_code = result.get("StatusCode", -1)

            # Estimate memory from container stats (best effort)
            try:
                stats = container.stats(stream=False)
                mem_usage = stats.get("memory_stats", {}).get("max_usage", 0)
                memory_kb = mem_usage / 1024
            except Exception:
                memory_kb = 0

            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "runtime_ms": runtime_ms,
                "memory_kb": memory_kb,
            }

        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "runtime_ms": (time.monotonic() - start) * 1000,
                "memory_kb": 0,
            }
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass


# ── Normalization ──────────────────────────────────────────────────────────────

def normalize(s: str) -> str:
    return "\n".join(line.strip() for line in s.strip().splitlines())

    actual = normalize(stdout)
    expected = normalize(expected_output)

    if actual == expected:
        verdict = "ACCEPTED"
    else:
        verdict = "WRONG_ANSWER"

# ── Per-case judging ───────────────────────────────────────────────────────────

def judge_single_case(
    index: int,
    language: str,
    code: str,
    input_data: str,
    expected_output: str,
    time_limit: int,
    memory_limit: int,
    is_sample: bool = False,
) -> TestCaseResult:

    result = run_sandbox(language, code, input_data, time_limit, memory_limit)

    stdout    = result["stdout"]
    stderr    = result["stderr"]
    exit_code = result["exit_code"]
    runtime_ms = result["runtime_ms"]
    memory_kb  = result["memory_kb"]

    # Detect compilation error
    if "COMPILATION_ERROR" in stdout or "COMPILATION_ERROR" in stderr:
        return TestCaseResult(
            index=index, verdict="COMPILATION_ERROR",
            runtime_ms=runtime_ms, memory_kb=memory_kb,
            stderr=stderr, is_sample=is_sample,
        )

    # TLE
    if exit_code == 124 or "TIME_LIMIT_EXCEEDED" in stderr:
        return TestCaseResult(
            index=index, verdict="TIME_LIMIT_EXCEEDED",
            runtime_ms=runtime_ms, memory_kb=memory_kb,
            stderr=stderr, is_sample=is_sample,
        )

    # MLE (OOM kill = exit 137)
    if exit_code == 137:
        return TestCaseResult(
            index=index, verdict="MEMORY_LIMIT_EXCEEDED",
            runtime_ms=runtime_ms, memory_kb=memory_kb,
            stderr=stderr, is_sample=is_sample,
        )

    # Runtime error
    if exit_code != 0:
        return TestCaseResult(
            index=index, verdict="RUNTIME_ERROR",
            runtime_ms=runtime_ms, memory_kb=memory_kb,
            stderr=stderr, is_sample=is_sample,
        )

    # Compare output
    actual   = normalize(stdout)
    expected = normalize(expected_output)

    if actual == expected:
        return TestCaseResult(
            index=index, verdict="ACCEPTED",
            runtime_ms=runtime_ms, memory_kb=memory_kb,
            stdout=stdout, is_sample=is_sample,
            actual=actual, expected=expected,
        )
    else:
        return TestCaseResult(
            index=index, verdict="WRONG_ANSWER",
            runtime_ms=runtime_ms, memory_kb=memory_kb,
            stdout=stdout, stderr=stderr,
            actual=actual[:500], expected=expected[:500],
            is_sample=is_sample,
        )


# ── Main entry point ───────────────────────────────────────────────────────────

def run_verdict(
    language: str,
    code: str,
    test_cases: list[dict],
    time_limit: int,
    memory_limit: int,
) -> VerdictResult:

    if not test_cases:
        return VerdictResult(
            status="INTERNAL_ERROR",
            verdict="INTERNAL_ERROR",
            runtime_ms=0,
            memory_kb=0,
            test_cases_passed=0,
            test_cases_total=0,
            stderr="No test cases configured for this problem",
        )

    total = len(test_cases)
    passed = 0
    max_runtime = 0.0
    max_memory = 0.0
    case_results = []

    final_status = "ACCEPTED"
    final_verdict = "ACCEPTED"

    verdict_map = {
        "COMPILATION_ERROR":    ("COMPILATION_ERROR",    "COMPILATION_ERROR"),
        "TIME_LIMIT_EXCEEDED":  ("TIME_LIMIT_EXCEEDED",  "TIME_LIMIT_EXCEEDED"),
        "MEMORY_LIMIT_EXCEEDED":("MEMORY_LIMIT_EXCEEDED","MEMORY_LIMIT_EXCEEDED"),
        "RUNTIME_ERROR":        ("RUNTIME_ERROR",        "RUNTIME_ERROR"),
        "WRONG_ANSWER":         ("WRONG_ANSWER",         "WRONG_ANSWER"),
    }

    for i, tc in enumerate(test_cases):
        tc_time_limit   = tc.get("time_limit_override") or time_limit
        tc_memory_limit = tc.get("memory_limit_override") or memory_limit

        case_result = judge_single_case(
            index=i,
            language=language,
            code=code,
            input_data=tc["input"],
            expected_output=tc["output"],
            time_limit=tc_time_limit,
            memory_limit=tc_memory_limit,
            is_sample=tc.get("is_sample", False),
        )

        case_results.append(case_result)
        max_runtime = max(max_runtime, case_result.runtime_ms)
        max_memory  = max(max_memory,  case_result.memory_kb)

        if case_result.verdict == "ACCEPTED":
            passed += 1
        else:
            # 🔥 DO NOT STOP — just update final verdict
            if final_status == "ACCEPTED":
                final_status, final_verdict = verdict_map.get(
                    case_result.verdict,
                    ("INTERNAL_ERROR", "INTERNAL_ERROR")
                )

    return VerdictResult(
        status=final_status,
        verdict=final_verdict,
        runtime_ms=max_runtime,
        memory_kb=max_memory,
        test_cases_passed=passed,
        test_cases_total=total,
        stderr="",
        case_results=case_results,
    )