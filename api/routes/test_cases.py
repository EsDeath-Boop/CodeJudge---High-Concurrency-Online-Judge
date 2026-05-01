import json
import boto3
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import Optional

from api.core.database import get_db
from api.core.security import get_current_user
from api.core.config import settings
from api.models.test_case import TestCase
from api.models.problem import Problem
from api.models.user import User

router = APIRouter(prefix="/api/problems/{problem_id}/testcases", tags=["test-cases"])

s3 = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


# ── Schemas ────────────────────────────────────────────────────────────────────

class TestCaseCreate(BaseModel):
    input_data: str
    expected_output: str
    is_sample: bool = False
    order_index: int = 0
    time_limit_override: Optional[int] = None
    memory_limit_override: Optional[int] = None


class TestCaseResponse(BaseModel):
    id: int
    problem_id: int
    is_sample: bool
    order_index: int
    # Only return input/output for sample cases to public; hidden from non-admins
    input_data: Optional[str] = None
    expected_output: Optional[str] = None

    class Config:
        from_attributes = True


class TestCaseAdminResponse(BaseModel):
    id: int
    problem_id: int
    input_data: str
    expected_output: str
    is_sample: bool
    order_index: int
    time_limit_override: Optional[int]
    memory_limit_override: Optional[int]

    class Config:
        from_attributes = True


# ── Helpers ────────────────────────────────────────────────────────────────────

async def get_problem_or_404(problem_id: int, db: AsyncSession) -> Problem:
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


def sync_to_s3(problem_id: int, test_cases: list[TestCase]):
    """Sync all test cases to S3 as JSON for the worker to consume."""
    data = [
        {"input": tc.input_data, "output": tc.expected_output}
        for tc in sorted(test_cases, key=lambda x: x.order_index)
    ]
    key = f"problems/{problem_id}/testcases.json"
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json",
    )
    return key


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[TestCaseResponse])
async def list_test_cases(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List test cases. Admins see all; users only see sample cases (no I/O data)."""
    await get_problem_or_404(problem_id, db)

    result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == problem_id)
        .order_by(TestCase.order_index)
    )
    cases = result.scalars().all()

    response = []
    for tc in cases:
        if current_user.is_admin:
            response.append(TestCaseResponse(
                id=tc.id,
                problem_id=tc.problem_id,
                is_sample=tc.is_sample,
                order_index=tc.order_index,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
            ))
        elif tc.is_sample:
            # Regular users only see sample cases with their I/O
            response.append(TestCaseResponse(
                id=tc.id,
                problem_id=tc.problem_id,
                is_sample=tc.is_sample,
                order_index=tc.order_index,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
            ))
        else:
            # Hidden test cases: existence shown, I/O hidden
            response.append(TestCaseResponse(
                id=tc.id,
                problem_id=tc.problem_id,
                is_sample=False,
                order_index=tc.order_index,
            ))
    return response


@router.post("", response_model=TestCaseAdminResponse, status_code=201)
async def add_test_case(
    problem_id: int,
    body: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a single test case. Admin only."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    problem = await get_problem_or_404(problem_id, db)

    tc = TestCase(problem_id=problem_id, **body.model_dump())
    db.add(tc)
    await db.flush()

    # Sync all test cases to S3
    result = await db.execute(
        select(TestCase).where(TestCase.problem_id == problem_id)
    )
    all_cases = result.scalars().all()

    try:
        s3_key = sync_to_s3(problem_id, all_cases)
        problem.test_cases_s3_key = s3_key
    except Exception:
        pass  # S3 sync is best-effort; test cases are in DB

    await db.refresh(tc)
    return tc


@router.post("/bulk", status_code=201)
async def bulk_import_test_cases(
    problem_id: int,
    file: UploadFile = File(...),
    replace: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk import test cases from a JSON file.
    Format: [{"input": "...", "output": "...", "is_sample": false}, ...]
    Set replace=true to delete existing test cases first.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    problem = await get_problem_or_404(problem_id, db)

    content = await file.read()
    try:
        cases_data = json.loads(content)
        if not isinstance(cases_data, list):
            raise ValueError("Expected a JSON array")
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    if replace:
        await db.execute(delete(TestCase).where(TestCase.problem_id == problem_id))

    new_cases = []
    for i, item in enumerate(cases_data):
        if "input" not in item or "output" not in item:
            raise HTTPException(
                status_code=400,
                detail=f"Item {i} missing 'input' or 'output' field"
            )
        tc = TestCase(
            problem_id=problem_id,
            input_data=item["input"],
            expected_output=item["output"],
            is_sample=item.get("is_sample", False),
            order_index=item.get("order_index", i),
        )
        db.add(tc)
        new_cases.append(tc)

    await db.flush()

    # Sync to S3
    result = await db.execute(
        select(TestCase).where(TestCase.problem_id == problem_id)
    )
    all_cases = result.scalars().all()

    try:
        s3_key = sync_to_s3(problem_id, all_cases)
        problem.test_cases_s3_key = s3_key
    except Exception:
        pass

    return {
        "imported": len(new_cases),
        "total": len(all_cases),
        "message": f"Successfully imported {len(new_cases)} test cases",
    }


@router.delete("/{test_case_id}", status_code=204)
async def delete_test_case(
    problem_id: int,
    test_case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a single test case. Admin only."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(
        select(TestCase).where(
            TestCase.id == test_case_id,
            TestCase.problem_id == problem_id,
        )
    )
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")

    await db.delete(tc)
    await db.flush()

    # Re-sync S3
    result = await db.execute(
        select(TestCase).where(TestCase.problem_id == problem_id)
    )
    remaining = result.scalars().all()
    try:
        sync_to_s3(problem_id, remaining)
    except Exception:
        pass


@router.post("/validate", status_code=200)
async def validate_test_case(
    problem_id: int,
    body: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dry-run a test case without saving it.
    Returns what the expected output format should look like.
    Admin only.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    await get_problem_or_404(problem_id, db)

    normalized_input = body.input_data.strip()
    normalized_output = body.expected_output.strip()

    return {
        "valid": True,
        "normalized_input_lines": len(normalized_input.splitlines()),
        "normalized_output_lines": len(normalized_output.splitlines()),
        "input_preview": normalized_input[:200],
        "output_preview": normalized_output[:200],
    }
