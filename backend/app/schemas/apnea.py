"""
무호흡 분석 API 스키마

Story 3.4: Apnea Analysis API
"""

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class ApneaAnalysisRequest(BaseModel):
    """무호흡 분석 요청"""
    session_id: int = Field(..., description="분석할 세션 ID")


class ApneaEvent(BaseModel):
    """무호흡/저호흡 이벤트"""
    epoch_start: int = Field(..., description="시작 에포크 번호")
    epoch_end: int = Field(..., description="종료 에포크 번호")
    event_type: str = Field(..., description="이벤트 타입 (apnea/hypopnea)")
    duration_seconds: int = Field(..., description="지속 시간 (초)")
    confidence: float = Field(..., ge=0, le=1, description="확률값")


class ApneaAnalysisResponse(BaseModel):
    """무호흡 분석 결과"""
    analysis_id: int = Field(..., description="분석 ID")
    session_id: int = Field(..., description="세션 ID")
    events: List[ApneaEvent] = Field(..., description="무호흡/저호흡 이벤트 리스트")
    ahi: float = Field(..., description="AHI (Apnea-Hypopnea Index)")
    severity: str = Field(..., description="심각도 (Normal/Mild/Moderate/Severe)")
    recommendations: List[str] = Field(..., description="권장사항")
    created_at: datetime = Field(..., description="분석 생성 시각")
    
    class Config:
        from_attributes = True
