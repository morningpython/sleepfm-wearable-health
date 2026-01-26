"""
수면 분석 API 라우트

Story 3.2: 수면 단계 분석 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, SleepSession, SleepAnalysis
from app.schemas.analysis import (
    SleepStageAnalysisRequest,
    SleepStageAnalysisResponse,
    SleepEpoch,
    SleepStageSummary
)
from app.ml.analysis.sleep_metrics import calculate_sleep_efficiency, calculate_stage_durations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analyze", tags=["analysis"])


@router.post("/sleep-stages", response_model=SleepStageAnalysisResponse)
def analyze_sleep_stages(
    request: SleepStageAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    수면 단계 분석 수행
    
    주어진 세션 ID의 센서 데이터를 분석하여 수면 단계를 예측합니다.
    
    Args:
        request: 분석 요청 (session_id)
        db: 데이터베이스 세션
        current_user: 현재 인증된 사용자
    
    Returns:
        SleepStageAnalysisResponse: 분석 결과
    
    Raises:
        HTTPException 404: 세션을 찾을 수 없음
        HTTPException 403: 권한 없음
    """
    # 1. 세션 조회
    session = db.query(SleepSession).filter(
        SleepSession.id == request.session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {request.session_id}"
        )
    
    # 권한 확인 (본인 세션만 분석 가능)
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this session"
        )
    
    logger.info(f"Analyzing sleep stages for session {session.id}")
    
    # 2. 수면 단계 분석 실행
    try:
        stages_data, summary_data = _perform_sleep_stage_analysis(session)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    
    # 3. 결과 DB 저장
    analysis = SleepAnalysis(
        session_id=session.id,
        user_id=current_user.id,
        analysis_type="sleep_stage",
        result_data={
            "stages": [s.dict() for s in stages_data],
            "summary": summary_data.dict()
        }
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    logger.info(f"Analysis saved: ID {analysis.id}")
    
    # 4. 응답 반환
    return SleepStageAnalysisResponse(
        analysis_id=analysis.id,
        session_id=session.id,
        stages=stages_data,
        summary=summary_data,
        created_at=analysis.created_at
    )


def _perform_sleep_stage_analysis(
    session: SleepSession
) -> tuple[List[SleepEpoch], SleepStageSummary]:
    """
    실제 수면 단계 분석 수행
    
    Args:
        session: 분석할 수면 세션
    
    Returns:
        (stages_data, summary_data): 에포크 데이터 및 요약
    """
    # TODO: 실제 파이프라인 통합 (전처리 → 임베딩 → 분류)
    # 현재는 더미 데이터 반환 (TDD Green 단계)
    
    import numpy as np
    
    # 8시간 = 960개 30초 에포크
    num_epochs = int(session.duration_hours * 120)  # 2 epochs/min
    
    # 더미 예측 생성 (실제로는 SleepStageClassifier 사용)
    np.random.seed(42)
    stage_predictions = np.random.randint(0, 5, size=num_epochs)
    stage_probabilities = np.random.uniform(0.5, 0.99, size=num_epochs)
    
    stage_names_map = ["Wake", "N1", "N2", "N3", "REM"]
    
    # 에포크별 수면 단계 생성
    stages_data = [
        SleepEpoch(
            epoch_number=i,
            stage=int(stage_predictions[i]),
            stage_name=stage_names_map[stage_predictions[i]],
            probability=float(stage_probabilities[i])
        )
        for i in range(num_epochs)
    ]
    
    # 수면 효율성 계산
    stage_list = stage_predictions.tolist()
    sleep_efficiency = calculate_sleep_efficiency(stage_list)
    
    # 단계별 지속 시간 계산
    stage_durations = calculate_stage_durations(stage_list, epoch_length_seconds=30)
    
    # 총 시간 및 수면 시간
    total_time_minutes = num_epochs * 0.5  # 30초 에포크
    total_sleep_time_minutes = total_time_minutes * (sleep_efficiency / 100.0)
    
    summary_data = SleepStageSummary(
        sleep_efficiency=sleep_efficiency,
        total_time_minutes=total_time_minutes,
        total_sleep_time_minutes=total_sleep_time_minutes,
        stage_durations=stage_durations
    )
    
    return stages_data, summary_data
