from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from api.core.database import get_db
from api.core.security import get_current_user
from api.models.leaderboard import LeaderboardEntry, GlobalLeaderboard
from api.models.problem import Problem
from api.models.user import User

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class ProblemLeaderboardEntry(BaseModel):
    rank: int
    username: str
    language: str
    runtime_ms: float
    memory_kb: float
    solved_at: datetime

    class Config:
        from_attributes = True


class GlobalLeaderboardEntry(BaseModel):
    rank: int
    username: str
    problems_solved: int
    total_submissions: int
    acceptance_rate: float
    score: int
    avg_runtime_ms: float

    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    username: str
    problems_solved: int
    total_submissions: int
    acceptance_rate: float
    score: int
    global_rank: Optional[int]


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("/global", response_model=list[GlobalLeaderboardEntry])
async def global_leaderboard(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Top users ranked by score (problems_solved × difficulty weight)."""
    result = await db.execute(
        select(GlobalLeaderboard)
        .order_by(GlobalLeaderboard.score.desc(), GlobalLeaderboard.problems_solved.desc())
        .offset(offset)
        .limit(min(limit, 100))
    )
    rows = result.scalars().all()

    return [
        GlobalLeaderboardEntry(
            rank=offset + i + 1,
            username=row.username,
            problems_solved=row.problems_solved,
            total_submissions=row.total_submissions,
            acceptance_rate=round(row.acceptance_rate or 0, 3),
            score=row.score,
            avg_runtime_ms=round(row.avg_runtime_ms or 0, 2),
        )
        for i, row in enumerate(rows)
    ]


@router.get("/problem/{problem_id}", response_model=list[ProblemLeaderboardEntry])
async def problem_leaderboard(
    problem_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Top submissions for a specific problem, ranked by runtime."""
    result = await db.execute(
        select(Problem).where(Problem.id == problem_id, Problem.is_active == True)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Problem not found")

    result = await db.execute(
        select(LeaderboardEntry)
        .where(LeaderboardEntry.problem_id == problem_id)
        .order_by(LeaderboardEntry.runtime_ms.asc())
        .limit(min(limit, 100))
    )
    rows = result.scalars().all()

    return [
        ProblemLeaderboardEntry(
            rank=i + 1,
            username=row.username,
            language=row.language,
            runtime_ms=round(row.runtime_ms, 2),
            memory_kb=round(row.memory_kb, 2),
            solved_at=row.solved_at,
        )
        for i, row in enumerate(rows)
    ]


@router.get("/me", response_model=UserStatsResponse)
async def my_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Current user's stats and global rank."""
    result = await db.execute(
        select(GlobalLeaderboard).where(GlobalLeaderboard.user_id == current_user.id)
    )
    row = result.scalar_one_or_none()

    if not row:
        return UserStatsResponse(
            username=current_user.username,
            problems_solved=0,
            total_submissions=0,
            acceptance_rate=0.0,
            score=0,
            global_rank=None,
        )

    # Calculate rank: count users with higher score
    rank_result = await db.execute(
        select(func.count(GlobalLeaderboard.id)).where(
            GlobalLeaderboard.score > row.score
        )
    )
    rank = (rank_result.scalar() or 0) + 1

    return UserStatsResponse(
        username=current_user.username,
        problems_solved=row.problems_solved,
        total_submissions=row.total_submissions,
        acceptance_rate=round(row.acceptance_rate or 0, 3),
        score=row.score,
        global_rank=rank,
    )


@router.get("/problem/{problem_id}/my-rank")
async def my_problem_rank(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check current user's rank on a specific problem."""
    result = await db.execute(
        select(LeaderboardEntry).where(
            LeaderboardEntry.problem_id == problem_id,
            LeaderboardEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        return {"ranked": False, "message": "You have not solved this problem yet"}

    # Count users faster than this user
    rank_result = await db.execute(
        select(func.count(LeaderboardEntry.id)).where(
            LeaderboardEntry.problem_id == problem_id,
            LeaderboardEntry.runtime_ms < entry.runtime_ms,
        )
    )
    rank = (rank_result.scalar() or 0) + 1

    return {
        "ranked": True,
        "rank": rank,
        "runtime_ms": round(entry.runtime_ms, 2),
        "memory_kb": round(entry.memory_kb, 2),
        "language": entry.language,
        "solved_at": entry.solved_at,
    }
