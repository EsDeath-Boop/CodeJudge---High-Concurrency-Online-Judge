from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, func
from api.core.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), default="medium")   # easy / medium / hard
    time_limit = Column(Integer, default=5)              # seconds
    memory_limit = Column(Integer, default=256)          # MB
    test_cases_s3_key = Column(String(500), nullable=True)  # S3 key for test cases
    sample_input = Column(Text, nullable=True)
    sample_output = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
