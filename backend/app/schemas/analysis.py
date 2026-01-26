"""
수면 분석 API 스키마

Story 3.2 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime


class SleepStageAnalysisRequest(BaseModel):
    """수면 단계 분석 요청"""
    
    session_id: int = Field(..., description="분석할 수면 세션 ID")


class SleepEpoch(BaseModel):
    """에포크별 수면 단계"""
    
    epoch_number: int = Field(..., description="에포크 번호 (0부터 시작)")
    stage: int = Field(..., ge=0, le=4, description="수면 단계 (0=Wake, 1=N1, 2=N2, 3=N3, 4=REM)")
    stage_name: str = Field(..., description="수면 단계 이름")
    probability: float = Field(..., ge=0.0, le=1.0, description="예측 확률")


class SleepStageSummary(BaseModel):
    """수면 단계 요약"""
    
    sleep_efficiency: float = Field(..., ge=0.0, le=100.0, description="수면 효율성 (%)")
    total_time_minutes: float = Field(..., description="총 시간 (분)")
    total_sleep_time_minutes: float = Field(..., description="총 수면 시간 (분)")
    stage_durations: Dict[str, float] = Field(..., description="단계별 지속 시간 (분)")


class SleepStageAnalysisResponse(BaseModel):
    """수면 단계 분석 응답"""
    
    analysis_id: int = Field(..., description="분석 ID")
    session_id: int = Field(..., description="세션 ID")
    stages: List[SleepEpoch] = Field(..., description="에포크별 수면 단계")
    summary: SleepStageSummary = Field(..., description="수면 요약")
    created_at: datetime = Field(..., description="분석 생성 시간")
    
    class Config:
        from_attributes = True
