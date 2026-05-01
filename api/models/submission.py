from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from api.core.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    language = Column(String(20), nullable=False)   # cpp / python / java
    code = Column(Text, nullable=False)
    status = Column(String(30), default="PENDING", index=True)
    # PENDING / RUNNING / ACCEPTED / WRONG_ANSWER /
    # TIME_LIMIT_EXCEEDED / MEMORY_LIMIT_EXCEEDED /
    # COMPILATION_ERROR / RUNTIME_ERROR / INTERNAL_ERROR
    verdict = Column(String(30), nullable=True)
    runtime_ms = Column(Float, nullable=True)
    memory_kb = Column(Float, nullable=True)
    stderr = Column(Text, nullable=True)
    test_cases_passed = Column(Integer, default=0)
    test_cases_total = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
