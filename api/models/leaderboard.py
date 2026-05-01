from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, UniqueConstraint
from api.core.database import Base


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    username = Column(String(50), nullable=False)           # denormalized for fast reads
    language = Column(String(20), nullable=False)
    runtime_ms = Column(Float, nullable=False)
    memory_kb = Column(Float, nullable=False, default=0)
    solved_at = Column(DateTime(timezone=True), server_default=func.now())

    # One best entry per user per problem
    __table_args__ = (
        UniqueConstraint("problem_id", "user_id", name="uq_leaderboard_problem_user"),
    )


class GlobalLeaderboard(Base):
    __tablename__ = "global_leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=False)
    problems_solved = Column(Integer, default=0)
    total_submissions = Column(Integer, default=0)
    acceptance_rate = Column(Float, default=0.0)
    avg_runtime_ms = Column(Float, default=0.0)
    score = Column(Integer, default=0)           # points: easy=10, medium=20, hard=40
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
