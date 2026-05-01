from api.models import *
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.core.database import engine, Base
from api.core.redis import init_redis, close_redis
from api.routes import auth, submissions, problems, test_cases, leaderboard

import os
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    from api.core.database import Base
    from api import models

    print("Models loaded")
    print("tables before")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("tables after")

    # ✅ Proper seeding using SQL file
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM problems"))
        count = result.scalar()

    if count == 0:
        import subprocess
        subprocess.run([
            "psql",
            "-U", "codejudge",
            "-d", "codejudge",
            "-f", "/app/db/seeds/001_problems.sql"
        ])

    await init_redis()
    yield

    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="CodeJudge API",
    description="High-concurrency online judge — C++, Python, Java",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register all routers ───────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(problems.router)
app.include_router(submissions.router)
app.include_router(test_cases.router)
app.include_router(leaderboard.router)


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "version": "2.0.0", "app": settings.APP_NAME}
