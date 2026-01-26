from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey, JSON, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """모든 모델의 기본 클래스"""

    pass


class User(Base):
    """사용자 모델"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)  # Boolean
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"


class SleepSession(Base):
    """수면 세션 데이터 모델"""

    __tablename__ = "sleep_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_date = Column(DateTime(timezone=True), nullable=False)
    duration_hours = Column(Integer, nullable=True)  # 수면 시간
    raw_data_path = Column(String(500), nullable=True)  # S3/로컬 경로
    analysis_status = Column(
        String(50), default="pending", nullable=False
    )  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<SleepSession(id={self.id}, user_id={self.user_id}, status='{self.analysis_status}')>"


class SleepAnalysis(Base):
    """수면 분석 결과 모델"""

    __tablename__ = "sleep_analyses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sleep_sessions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False)  # sleep_stage, apnea, etc.
    result_data = Column(JSON, nullable=True)  # 분석 결과 (JSON 형식)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SleepAnalysis(id={self.id}, session_id={self.session_id}, type='{self.analysis_type}')>"


# Export all models
__all__ = ["Base", "User", "SleepSession", "SleepAnalysis"]
