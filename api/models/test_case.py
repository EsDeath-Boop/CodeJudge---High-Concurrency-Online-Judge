from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from api.core.database import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_sample = Column(Boolean, default=False)   # sample = shown to user; hidden = judge only
    order_index = Column(Integer, default=0)      # run in order
    time_limit_override = Column(Integer, nullable=True)    # per-case override if needed
    memory_limit_override = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
