import asyncio
import json
from typing import Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.core.database import get_db
from api.core.redis import get_redis
from api.core.security import get_current_user
from api.models.problem import Problem
from api.models.submission import Submission
from api.models.user import User

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

SUPPORTED_LANGUAGES = {"cpp", "python", "java"}

TERMINAL_STATUSES = {
    "ACCEPTED", "WRONG_ANSWER", "TIME_LIMIT_EXCEEDED",
    "MEMORY_LIMIT_EXCEEDED", "COMPILATION_ERROR",
    "RUNTIME_ERROR", "INTERNAL_ERROR",
}


# ── Schemas ────────────────────────────────────────────────────────────────────

class SubmitRequest(BaseModel):
    problem_id: int
    language: str
    code: str


class SubmissionResponse(BaseModel):
    id: int
    problem_id: int
    language: str
    status: str
    verdict: Optional[str] = None
    runtime_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    test_cases_passed: int
    test_cases_total: int
    stderr: Optional[str] = None

    class Config:
        from_attributes = True


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("", response_model=SubmissionResponse, status_code=202)
async def submit(
    body: SubmitRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    if body.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Language must be one of {SUPPORTED_LANGUAGES}")

    if len(body.code) > settings.MAX_CODE_LENGTH:
        raise HTTPException(status_code=400, detail="Code exceeds maximum allowed length")

    result = await db.execute(
        select(Problem).where(Problem.id == body.problem_id, Problem.is_active == True)
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    submission = Submission(
        user_id=current_user.id,
        problem_id=body.problem_id,
        language=body.language,
        code=body.code,
        status="PENDING",
        test_cases_total=0,
        test_cases_passed=0,
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)

    job = {
        "submission_id":    submission.id,
        "user_id":          current_user.id,        # needed for leaderboard
        "problem_id":       body.problem_id,
        "language":         body.language,
        "code":             body.code,
        "time_limit":       problem.time_limit,
        "memory_limit":     problem.memory_limit,
        "test_cases_s3_key":problem.test_cases_s3_key or "",
        "sample_input":     problem.sample_input or "",
        "sample_output":    problem.sample_output or "",
    }
    await redis.xadd("submissions_stream", {"data": json.dumps(job)})

    return submission


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Submission).where(
            Submission.id == submission_id,
            Submission.user_id == current_user.id,
        )
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("", response_model=list[SubmissionResponse])
async def list_submissions(
    problem_id: Optional[int] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Submission).where(Submission.user_id == current_user.id)
    if problem_id:
        query = query.where(Submission.problem_id == problem_id)
    query = query.order_by(Submission.created_at.desc()).limit(min(limit, 100))
    result = await db.execute(query)
    return result.scalars().all()


# ── WebSocket — Redis pub/sub (real push, not polling) ─────────────────────────

@router.websocket("/ws/{submission_id}")
async def submission_ws(
    websocket: WebSocket,
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    redis_client=Depends(get_redis),
):
    await websocket.accept()

    # Send current state immediately on connect
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalar_one_or_none()

    if not submission:
        await websocket.send_json({"error": "Submission not found"})
        await websocket.close()
        return

    await websocket.send_json({
        "submission_id":     submission.id,
        "status":            submission.status,
        "verdict":           submission.verdict,
        "runtime_ms":        submission.runtime_ms,
        "memory_kb":         submission.memory_kb,
        "test_cases_passed": submission.test_cases_passed,
        "test_cases_total":  submission.test_cases_total,
    })

    # If already terminal, close immediately
    if submission.status in TERMINAL_STATUSES:
        await websocket.close()
        return

    # Subscribe to Redis channel for live updates from worker
    channel = f"submission:{submission_id}"

    # Create a fresh pubsub connection for this websocket
    pubsub_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    pubsub = pubsub_client.pubsub()
    await pubsub.subscribe(channel)

    try:
        # Wait up to 5 minutes for verdict
        timeout = 300
        elapsed = 0

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            data = json.loads(message["data"])
            await websocket.send_json(data)

            # Close when terminal state received
            if data.get("status") in TERMINAL_STATUSES:
                break

            elapsed += 1
            if elapsed > timeout:
                await websocket.send_json({"error": "Timeout waiting for verdict"})
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub_client.close()
