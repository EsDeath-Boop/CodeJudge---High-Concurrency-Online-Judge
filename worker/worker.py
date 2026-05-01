"""
CodeJudge Worker v2
- Consumes jobs from Redis Stream
- Fetches test cases from DB (with S3 fallback)
- Uses verdict_engine for isolated Docker execution
- Writes verdict + updates leaderboard in PostgreSQL
- Publishes real-time updates to Redis pub/sub
"""

import json
import logging
import os
import time
import threading

import boto3
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from verdict_engine import run_verdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
log = logging.getLogger("worker")

# ── Config ─────────────────────────────────────────────────────────────────────
DATABASE_URL   = os.getenv("DATABASE_URL_SYNC", "postgresql://codejudge:codejudge@db:5432/codejudge")
REDIS_URL      = os.getenv("REDIS_URL", "redis://redis:6379")
STREAM_NAME    = "submissions_stream"
CONSUMER_GROUP = "workers"
CONSUMER_NAME  = f"worker-{os.getpid()}"
BLOCK_MS       = 5000

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET  = os.getenv("S3_BUCKET", "codejudge-testcases")

# ── Clients ────────────────────────────────────────────────────────────────────
engine  = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5)
Session = sessionmaker(bind=engine)
r       = redis.from_url(REDIS_URL, decode_responses=True)
s3      = boto3.client("s3", region_name=AWS_REGION)


# ── DB helpers ─────────────────────────────────────────────────────────────────

def update_submission(submission_id: int, **kwargs):
    with Session() as db:
        sets = ", ".join(f"{k} = :{k}" for k in kwargs)
        kwargs["submission_id"] = submission_id
        db.execute(
            text(f"UPDATE submissions SET {sets}, updated_at = NOW() WHERE id = :submission_id"),
            kwargs,
        )
        db.commit()


def get_test_cases_from_db(problem_id: int) -> list[dict]:
    with Session() as db:
        rows = db.execute(
            text("""
                SELECT input_data, expected_output, is_sample,
                       time_limit_override, memory_limit_override
                FROM test_cases
                WHERE problem_id = :problem_id
                ORDER BY order_index ASC
            """),
            {"problem_id": problem_id},
        ).fetchall()
        return [
            {
                "input":                 row.input_data,
                "output":               row.expected_output,
                "is_sample":            row.is_sample,
                "time_limit_override":  row.time_limit_override,
                "memory_limit_override":row.memory_limit_override,
            }
            for row in rows
        ]


def get_test_cases_from_s3(s3_key: str) -> list[dict]:
    if not s3_key:
        return []
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
        return json.loads(obj["Body"].read())
    except Exception as e:
        log.warning(f"S3 fetch failed ({s3_key}): {e}")
        return []


def get_problem_info(problem_id: int) -> dict:
    with Session() as db:
        row = db.execute(
            text("SELECT time_limit, memory_limit, difficulty FROM problems WHERE id = :id"),
            {"id": problem_id},
        ).fetchone()
        if not row:
            return {}
        return {
            "time_limit":   row.time_limit,
            "memory_limit": row.memory_limit,
            "difficulty":   row.difficulty,
        }


# ── Leaderboard ────────────────────────────────────────────────────────────────

DIFFICULTY_SCORE = {"easy": 10, "medium": 20, "hard": 40}


def update_leaderboard(submission_id, problem_id, user_id, language, runtime_ms, memory_kb, difficulty):
    with Session() as db:
        row = db.execute(
            text("SELECT username FROM users WHERE id = :id"),
            {"id": user_id},
        ).fetchone()
        if not row:
            return
        username = row.username

        # Per-problem leaderboard — keep best runtime
        existing = db.execute(
            text("SELECT id, runtime_ms FROM leaderboard WHERE problem_id=:pid AND user_id=:uid"),
            {"pid": problem_id, "uid": user_id},
        ).fetchone()

        if existing:
            if runtime_ms < existing.runtime_ms:
                db.execute(
                    text("""
                        UPDATE leaderboard
                        SET submission_id=:sid, language=:lang,
                            runtime_ms=:rt, memory_kb=:mem, solved_at=NOW()
                        WHERE id=:id
                    """),
                    {"id": existing.id, "sid": submission_id, "lang": language,
                     "rt": runtime_ms, "mem": memory_kb},
                )
        else:
            # First solve — insert and award score
            db.execute(
                text("""
                    INSERT INTO leaderboard
                        (problem_id, user_id, submission_id, username, language, runtime_ms, memory_kb)
                    VALUES (:pid, :uid, :sid, :uname, :lang, :rt, :mem)
                """),
                {"pid": problem_id, "uid": user_id, "sid": submission_id,
                 "uname": username, "lang": language, "rt": runtime_ms, "mem": memory_kb},
            )

            score = DIFFICULTY_SCORE.get(difficulty, 10)

            global_row = db.execute(
                text("SELECT id FROM global_leaderboard WHERE user_id=:uid"),
                {"uid": user_id},
            ).fetchone()

            if global_row:
                db.execute(
                    text("""
                        UPDATE global_leaderboard
                        SET problems_solved=problems_solved+1,
                            total_submissions=total_submissions+1,
                            score=score+:score, updated_at=NOW()
                        WHERE user_id=:uid
                    """),
                    {"uid": user_id, "score": score},
                )
            else:
                db.execute(
                    text("""
                        INSERT INTO global_leaderboard
                            (user_id, username, problems_solved, total_submissions, score)
                        VALUES (:uid, :uname, 1, 1, :score)
                    """),
                    {"uid": user_id, "uname": username, "score": score},
                )

        db.commit()


def increment_total_submissions(user_id: int):
    with Session() as db:
        db.execute(
            text("""
                UPDATE global_leaderboard
                SET total_submissions = total_submissions + 1,
                    acceptance_rate = problems_solved::float / NULLIF(total_submissions + 1, 0)
                WHERE user_id = :uid
            """),
            {"uid": user_id},
        )
        db.commit()


# ── Real-time pub/sub ──────────────────────────────────────────────────────────

def publish_update(submission_id: int, status: str, verdict: str, extra: dict = None):
    payload = {"submission_id": submission_id, "status": status, "verdict": verdict, **(extra or {})}
    r.publish(f"submission:{submission_id}", json.dumps(payload))


# ── Core job processor ─────────────────────────────────────────────────────────

def process_job(job: dict):
    submission_id = job["submission_id"]
    problem_id    = job["problem_id"]
    language      = job["language"]
    code          = job["code"]
    user_id       = job.get("user_id", 0)

    log.info(f"[{submission_id}] Starting — lang={language} problem={problem_id}")

    update_submission(submission_id, status="RUNNING")
    publish_update(submission_id, "RUNNING", "")

    problem_info = get_problem_info(problem_id)
    time_limit   = problem_info.get("time_limit",   job.get("time_limit", 5))
    memory_limit = problem_info.get("memory_limit", job.get("memory_limit", 256))
    difficulty   = problem_info.get("difficulty",   "medium")

    # Test case resolution: DB → S3 → sample I/O
    test_cases = get_test_cases_from_db(problem_id)
    if not test_cases:
        test_cases = get_test_cases_from_s3(job.get("test_cases_s3_key", ""))
    if not test_cases and job.get("sample_input") and job.get("sample_output"):
        test_cases = [{"input": job["sample_input"], "output": job["sample_output"], "is_sample": True}]

    try:
        result = run_verdict(
            language=language,
            code=code,
            test_cases=test_cases,
            time_limit=time_limit,
            memory_limit=memory_limit,
        )
    except Exception as e:
        log.error(f"[{submission_id}] Engine crash: {e}", exc_info=True)
        update_submission(submission_id, status="INTERNAL_ERROR", verdict="INTERNAL_ERROR", stderr=str(e)[:2000])
        publish_update(submission_id, "INTERNAL_ERROR", "INTERNAL_ERROR")
        return

    update_submission(
        submission_id,
        status=result.status,
        verdict=result.verdict,
        runtime_ms=round(result.runtime_ms, 2),
        memory_kb=round(result.memory_kb, 2),
        test_cases_passed=result.test_cases_passed,
        test_cases_total=result.test_cases_total,
        stderr=result.stderr[:2000] if result.stderr else "",
    )

    if result.status == "ACCEPTED" and user_id:
        try:
            update_leaderboard(submission_id, problem_id, user_id, language,
                               result.runtime_ms, result.memory_kb, difficulty)
        except Exception as e:
            log.error(f"[{submission_id}] Leaderboard failed: {e}", exc_info=True)

    if user_id:
        try:
            increment_total_submissions(user_id)
        except Exception:
            pass

    publish_update(submission_id, result.status, result.verdict, {
        "runtime_ms":        result.runtime_ms,
        "memory_kb":         result.memory_kb,
        "test_cases_passed": result.test_cases_passed,
        "test_cases_total":  result.test_cases_total,
    })

    log.info(f"[{submission_id}] {result.status} ({result.test_cases_passed}/{result.test_cases_total}) {result.runtime_ms:.1f}ms")


# ── Stream consumer ────────────────────────────────────────────────────────────

def ensure_consumer_group():
    try:
        r.xgroup_create(STREAM_NAME, CONSUMER_GROUP, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise


def worker_loop():
    thread_name = threading.current_thread().name
    log.info(f"Worker thread ready: {thread_name}")
    ensure_consumer_group()

    while True:
        try:
            messages = r.xreadgroup(
                groupname=CONSUMER_GROUP,
                consumername=f"{CONSUMER_NAME}-{thread_name}",
                streams={STREAM_NAME: ">"},
                count=1,
                block=BLOCK_MS,
            )
            if not messages:
                continue

            for stream, entries in messages:
                for message_id, data in entries:
                    try:
                        job = json.loads(data["data"])
                        process_job(job)
                        r.xack(STREAM_NAME, CONSUMER_GROUP, message_id)
                    except Exception as e:
                        log.error(f"Message {message_id} failed: {e}", exc_info=True)

        except redis.exceptions.ConnectionError as e:
            log.error(f"Redis disconnected: {e}. Retry in 5s...")
            time.sleep(5)
        except KeyboardInterrupt:
            break


def main():
    worker_count = int(os.getenv("WORKER_THREADS", "4"))
    log.info(f"Spawning {worker_count} worker threads")
    threads = []
    for i in range(worker_count):
        t = threading.Thread(target=worker_loop, name=f"t{i}", daemon=True)
        t.start()
        threads.append(t)
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        log.info("Shutting down")


if __name__ == "__main__":
    main()
