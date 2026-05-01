from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from api.core.database import get_db
from api.core.security import get_current_user
from api.models.problem import Problem
from api.models.user import User

router = APIRouter(prefix="/api/problems", tags=["problems"])


class ProblemCreate(BaseModel):
    title: str
    slug: str
    description: str
    difficulty: str = "medium"
    time_limit: int = 5
    memory_limit: int = 256
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    test_cases_s3_key: Optional[str] = None


class ProblemResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    difficulty: str
    time_limit: int
    memory_limit: int
    sample_input: Optional[str]
    sample_output: Optional[str]

    class Config:
        from_attributes = True


@router.get("", response_model=list[ProblemResponse])
async def list_problems(
    difficulty: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(Problem).where(Problem.is_active == True)
    if difficulty:
        query = query.where(Problem.difficulty == difficulty)
    query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{slug}", response_model=ProblemResponse)
async def get_problem(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Problem).where(Problem.slug == slug, Problem.is_active == True)
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.post("", response_model=ProblemResponse, status_code=201)
async def create_problem(
    body: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(select(Problem).where(Problem.slug == body.slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Slug already exists")

    problem = Problem(**body.model_dump())
    db.add(problem)
    await db.flush()
    await db.refresh(problem)
    return problem


@router.delete("/{problem_id}", status_code=204)
async def delete_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    problem.is_active = False
