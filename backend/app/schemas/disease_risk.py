"""
질병 위험 예측 API 스키마

Story 4.2 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class DiseaseRiskRequest(BaseModel):
    """질병 위험 분석 요청"""
    
    session_id: int = Field(..., description="분석할 수면 세션 ID")


class ConfidenceInterval(BaseModel):
    """신뢰 구간"""
    
    lower: float = Field(..., ge=0.0, le=100.0, description="신뢰 구간 하한")
    upper: float = Field(..., ge=0.0, le=100.0, description="신뢰 구간 상한")


class DiseasePrediction(BaseModel):
    """질환별 예측 결과"""
    
    disease: str = Field(..., description="질환 영문명")
    disease_name_ko: str = Field(..., description="질환 한글명")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="위험 스코어 (0-100)")
    category: str = Field(..., description="위험 카테고리 (Low/Medium/High)")
    confidence_interval: ConfidenceInterval = Field(..., description="신뢰 구간")
    recommendations: Optional[List[str]] = Field(
        default=None, 
        description="권장사항 (High 카테고리인 경우에만)"
    )


class DiseaseRiskResponse(BaseModel):
    """질병 위험 분석 응답"""
    
    analysis_id: int = Field(..., description="분석 ID")
    session_id: int = Field(..., description="세션 ID")
    predictions: List[DiseasePrediction] = Field(..., description="질환별 예측 결과")
    created_at: datetime = Field(..., description="분석 생성 시간")
    
    class Config:
        from_attributes = True


# 통합 분석 관련 스키마 (Story 4.3)

class IntegratedAnalysisRequest(BaseModel):
    """통합 분석 요청"""
    
    session_id: int = Field(..., description="분석할 수면 세션 ID")
    analysis_types: Optional[List[str]] = Field(
        default=None,
        description="분석 유형 (기본값: 모두 포함)"
    )


class AnalysisStatusResponse(BaseModel):
    """분석 상태 응답"""
    
    session_id: int = Field(..., description="세션 ID")
    status: str = Field(..., description="분석 상태 (pending/processing/completed/failed)")
    progress: Optional[Dict[str, str]] = Field(
        default=None,
        description="각 분석 유형별 진행 상태"
    )
    result_url: Optional[str] = Field(
        default=None,
        description="결과 URL (완료 시)"
    )


class IntegratedAnalysisResponse(BaseModel):
    """통합 분석 응답"""
    
    session_id: int = Field(..., description="세션 ID")
    analyses: Dict[str, dict] = Field(..., description="분석 유형별 결과")
    created_at: datetime = Field(..., description="분석 생성 시간")
    errors: Optional[Dict[str, str]] = Field(
        default=None,
        description="실패한 분석 유형별 에러 메시지"
    )


# 히스토리/결과 관련 스키마 (Story 4.4)

class SessionSummary(BaseModel):
    """세션 요약"""
    
    session_id: int = Field(..., description="세션 ID")
    session_date: datetime = Field(..., description="수면 날짜")
    duration_hours: Optional[float] = Field(default=None, description="수면 시간")
    analysis_status: str = Field(..., description="분석 상태")
    analysis_count: int = Field(default=0, description="분석 수")


class SessionListResponse(BaseModel):
    """세션 목록 응답"""
    
    sessions: List[SessionSummary] = Field(..., description="세션 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    page_size: int = Field(..., description="페이지 크기")
    total_pages: int = Field(..., description="전체 페이지 수")


class AnalysisSummary(BaseModel):
    """분석 요약"""
    
    analysis_id: int = Field(..., description="분석 ID")
    analysis_type: str = Field(..., description="분석 유형")
    created_at: datetime = Field(..., description="생성 시간")


class SessionResultsResponse(BaseModel):
    """세션 결과 응답"""
    
    session_id: int = Field(..., description="세션 ID")
    session_date: datetime = Field(..., description="수면 날짜")
    duration_hours: Optional[float] = Field(default=None, description="수면 시간")
    analyses: List[AnalysisSummary] = Field(..., description="분석 목록")
    results: Dict[str, dict] = Field(..., description="분석 유형별 결과")
