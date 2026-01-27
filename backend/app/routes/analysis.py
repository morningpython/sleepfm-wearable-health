"""
수면 분석 API 라우트

Story 3.2: 수면 단계 분석 API 엔드포인트
Story 4.2: 질병 위험 예측 API 엔드포인트
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
from app.schemas.apnea import (
    ApneaAnalysisRequest,
    ApneaAnalysisResponse,
    ApneaEvent
)
from app.schemas.disease_risk import (
    DiseaseRiskRequest,
    DiseaseRiskResponse,
    DiseasePrediction,
    ConfidenceInterval
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
    
    TDD Refactor Phase:
    - 실제 SleepStageClassifier 사용
    - 더미 임베딩 생성 (실제 SleepFM 통합은 향후)
    
    Args:
        session: 분석할 수면 세션
    
    Returns:
        (stages_data, summary_data): 에포크 데이터 및 요약
    """
    import torch
    import numpy as np
    from app.ml.models.heads import SleepStageClassifier
    
    # duration_hours를 분으로 변환
    duration_minutes = (session.duration_hours or 8) * 60  # 기본 8시간
    # 8시간 = 960개 30초 에포크
    num_epochs = int(duration_minutes / 0.5)  # duration_minutes / 0.5
    
    # 실제 분류기 생성
    classifier = SleepStageClassifier(input_dim=512, num_classes=5)
    classifier.eval()
    
    # 더미 임베딩 생성 (실제로는 SleepFM 인코더 사용)
    # TODO: 실제 센서 데이터 로딩 → 전처리 → SleepFM 임베딩
    embeddings = torch.randn(1, num_epochs, 512)
    
    # batch 차원 제거하여 (num_epochs, 512)로 변환
    embeddings_2d = embeddings.squeeze(0)  # (num_epochs, 512)
    
    # 실제 모델로 예측
    with torch.no_grad():
        predictions, probabilities = classifier.predict(embeddings_2d, return_probs=True)
    
    # numpy 변환
    stage_predictions = predictions.cpu().numpy()  # (num_epochs,)
    stage_probs = probabilities.cpu().numpy()  # (num_epochs, 5)
    
    # 각 에포크의 최대 확률값
    max_probs = np.max(stage_probs, axis=1)
    
    stage_names_map = ["Wake", "N1", "N2", "N3", "REM"]
    
    # 에포크별 수면 단계 생성
    stages_data = [
        SleepEpoch(
            epoch_number=i,
            stage=int(stage_predictions[i]),
            stage_name=stage_names_map[int(stage_predictions[i]) % len(stage_names_map)],  # 안전하게 인덱스 처리
            probability=float(max_probs[i])
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


@router.post("/apnea", response_model=ApneaAnalysisResponse)
def analyze_apnea(
    request: ApneaAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    수면무호흡 분석 수행
    
    주어진 세션 ID의 호흡 신호를 분석하여 무호흡/저호흡 이벤트를 탐지합니다.
    
    Args:
        request: 분석 요청 (session_id)
        db: 데이터베이스 세션
        current_user: 현재 인증된 사용자
    
    Returns:
        ApneaAnalysisResponse: 분석 결과 (이벤트, AHI, 심각도, 권장사항)
    
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
    
    # 권한 확인
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this session"
        )
    
    logger.info(f"Analyzing apnea for session {session.id}")
    
    # 2. 무호흡 분석 실행
    try:
        events_data, ahi, severity, recommendations = _perform_apnea_analysis(session)
    except Exception as e:
        logger.error(f"Apnea analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    
    # 3. 분석 결과 DB 저장
    analysis = SleepAnalysis(
        session_id=session.id,
        user_id=current_user.id,
        analysis_type="apnea",
        result_data={
            "events": [event.dict() for event in events_data],
            "ahi": ahi,
            "severity": severity,
            "recommendations": recommendations
        }
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    logger.info(f"Apnea analysis saved (ID: {analysis.id})")
    
    # 4. 응답 반환
    return ApneaAnalysisResponse(
        analysis_id=analysis.id,
        session_id=session.id,
        events=events_data,
        ahi=ahi,
        severity=severity,
        recommendations=recommendations,
        created_at=analysis.created_at
    )


def _perform_apnea_analysis(session: SleepSession):
    """
    무호흡 분석 수행 (내부 헬퍼 함수)
    
    TDD Refactor Phase:
    - 실제 ApneaDetector 사용
    - 더미 임베딩 생성 (실제 SleepFM 통합은 향후)
    
    Args:
        session: SleepSession 인스턴스
    
    Returns:
        tuple: (events_data, ahi, severity, recommendations)
    """
    import torch
    from app.ml.models.heads import ApneaDetector
    
    # 실제 무호흡 탐지기 생성
    detector = ApneaDetector(input_dim=512, num_classes=3)
    detector.eval()
    
    # duration_hours를 분으로 변환
    duration_minutes = (session.duration_hours or 8) * 60  # 기본 8시간
    # 8시간 데이터
    num_epochs = int(duration_minutes / 0.5)  # 30초 에포크
    
    # 더미 임베딩 생성 (실제로는 SleepFM 인코더 사용)
    # TODO: 실제 호흡 신호 데이터 로딩 → 전처리 → SleepFM 임베딩
    embeddings = torch.randn(1, num_epochs, 512)
    
    # 실제 모델로 이벤트 탐지
    events_dict_list = detector.detect_events(
        embeddings,
        threshold=0.5,
        epoch_length_seconds=30
    )
    
    # ApneaEvent 스키마로 변환
    events_data = [
        ApneaEvent(
            epoch_start=event['epoch_start'],
            epoch_end=event['epoch_end'],
            event_type=event['event_type'],
            duration_seconds=event['duration_seconds'],
            confidence=event['confidence']
        )
        for event in events_dict_list
    ]
    
    # AHI 계산
    total_sleep_hours = (session.duration_hours or 8)
    ahi = detector.calculate_ahi(events_dict_list, total_sleep_hours)
    
    # 심각도 분류
    severity = detector.classify_severity(ahi)
    
    # 권장사항 생성
    recommendations = _generate_apnea_recommendations(ahi, severity)
    
    return events_data, ahi, severity, recommendations


def _generate_apnea_recommendations(ahi: float, severity: str) -> List[str]:
    """
    AHI 및 심각도 기반 권장사항 생성
    
    Args:
        ahi: AHI 값
        severity: 심각도 (Normal/Mild/Moderate/Severe)
    
    Returns:
        권장사항 리스트
    """
    recommendations = []
    
    if severity == "Normal":
        recommendations.extend([
            "정상 범위의 호흡 패턴입니다. 건강한 수면 습관을 유지하세요.",
            "규칙적인 수면 시간을 유지하고, 수면 환경을 쾌적하게 관리하세요.",
            "측면으로 자는 자세가 호흡에 도움이 될 수 있습니다."
        ])
    
    elif severity == "Mild":
        recommendations.extend([
            "경증 수면무호흡이 감지되었습니다. 생활습관 개선이 도움이 될 수 있습니다.",
            "체중 감량, 금주, 금연이 증상 완화에 효과적입니다.",
            "증상이 지속되면 수면 전문의 상담을 권장합니다.",
            "옆으로 누워 자는 자세가 무호흡 감소에 도움이 됩니다."
        ])
    
    elif severity == "Moderate":
        recommendations.extend([
            "중등도 수면무호흡이 감지되었습니다. 전문의 상담이 필요합니다.",
            "수면다원검사(PSG) 등 정밀 검사를 권장합니다.",
            "CPAP 치료가 필요할 수 있으니 수면 전문의와 상담하세요.",
            "심혈관 질환 위험이 증가할 수 있으니 조기 치료가 중요합니다."
        ])
    
    else:  # Severe
        recommendations.extend([
            "중증 수면무호흡이 감지되었습니다. 즉시 전문의 상담이 필요합니다.",
            "CPAP 또는 BiPAP 치료가 필요할 수 있습니다.",
            "심혈관계 합병증 예방을 위해 긴급한 치료가 권장됩니다.",
            "수면 전문 클리닉에서 정밀 검사 및 치료 계획을 수립하세요."
        ])
    
    return recommendations


@router.post("/disease-risk", response_model=DiseaseRiskResponse)
def analyze_disease_risk(
    request: DiseaseRiskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    질병 위험 분석 수행 (Story 4.2)
    
    주어진 세션 ID의 데이터를 분석하여 5개 질환의 위험도를 예측합니다.
    
    Args:
        request: 분석 요청 (session_id)
        db: 데이터베이스 세션
        current_user: 현재 인증된 사용자
    
    Returns:
        DiseaseRiskResponse: 분석 결과 (5개 질환별 예측)
    
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
    
    logger.info(f"Analyzing disease risk for session {session.id}")
    
    # 2. 질병 위험 분석 실행
    try:
        predictions_data = _perform_disease_risk_analysis(session)
    except Exception as e:
        logger.error(f"Disease risk analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    
    # 3. 결과 DB 저장
    analysis = SleepAnalysis(
        session_id=session.id,
        user_id=current_user.id,
        analysis_type="disease_risk",
        result_data={
            "predictions": [p.dict() for p in predictions_data]
        }
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    logger.info(f"Disease risk analysis saved: ID {analysis.id}")
    
    # 4. 응답 반환
    return DiseaseRiskResponse(
        analysis_id=analysis.id,
        session_id=session.id,
        predictions=predictions_data,
        created_at=analysis.created_at
    )


def _perform_disease_risk_analysis(session: SleepSession) -> List[DiseasePrediction]:
    """
    실제 질병 위험 분석 수행
    
    Args:
        session: 분석할 수면 세션
    
    Returns:
        DiseasePrediction 리스트
    """
    import torch
    from app.ml.models.disease_risk import (
        DiseaseRiskPredictor,
        DISEASE_NAMES,
        DISEASE_NAMES_KO,
        categorize_risk,
        get_disease_recommendations,
    )
    
    # 실제 예측기 생성
    predictor = DiseaseRiskPredictor(embedding_dim=512)
    predictor.eval()
    
    # 더미 임베딩 생성 (실제로는 세션 데이터 → SleepFM 임베딩)
    # TODO: 실제 센서 데이터 로딩 및 임베딩 생성
    duration_minutes = (session.duration_hours or 8) * 60
    num_epochs = int(duration_minutes / 0.5)
    
    # 세션의 모든 에포크 임베딩을 평균하여 단일 임베딩 생성
    dummy_embeddings = torch.randn(num_epochs, 512)
    session_embedding = dummy_embeddings.mean(dim=0, keepdim=True)  # (1, 512)
    
    # Monte Carlo Dropout으로 신뢰 구간 포함 예측
    with torch.no_grad():
        result = predictor.predict_with_confidence(
            session_embedding,
            confidence_level=0.95,
            num_samples=50  # 빠른 응답을 위해 샘플 수 줄임
        )
    
    risk_scores = result["risk_scores"].squeeze(0).numpy()  # (5,)
    lower_bounds = result["confidence_lower"].squeeze(0).numpy()  # (5,)
    upper_bounds = result["confidence_upper"].squeeze(0).numpy()  # (5,)
    
    # 예측 결과 생성
    predictions = []
    for i, disease in enumerate(DISEASE_NAMES):
        score = float(risk_scores[i])
        category = categorize_risk(score)
        
        # 권장사항 (High 카테고리만)
        recommendations = None
        if category == "High":
            recommendations = get_disease_recommendations(disease, category)
        
        prediction = DiseasePrediction(
            disease=disease,
            disease_name_ko=DISEASE_NAMES_KO[disease],
            risk_score=score,
            category=category,
            confidence_interval=ConfidenceInterval(
                lower=float(lower_bounds[i]),
                upper=float(upper_bounds[i])
            ),
            recommendations=recommendations
        )
        predictions.append(prediction)
    
    return predictions


# ============================================================
# Story 4.3: 통합 분석 API
# ============================================================

@router.post("", status_code=status.HTTP_200_OK)
def analyze_integrated(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    통합 분석 수행 (Story 4.3)
    
    모든 분석(수면 요약, 수면 단계, 무호흡, 질병 위험)을 한 번에 수행합니다.
    
    Args:
        request: {"session_id": int, "analysis_types": Optional[List[str]]}
        db: 데이터베이스 세션
        current_user: 현재 인증된 사용자
    
    Returns:
        통합 분석 결과
    """
    from datetime import datetime
    from app.schemas.disease_risk import IntegratedAnalysisRequest
    
    # 요청 파싱
    session_id = request.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="session_id is required"
        )
    
    analysis_types = request.get("analysis_types")  # None이면 전체 분석
    
    # 1. 세션 조회
    session = db.query(SleepSession).filter(
        SleepSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}"
        )
    
    # 권한 확인
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this session"
        )
    
    logger.info(f"Starting integrated analysis for session {session.id}")
    
    # 분석할 타입 결정
    all_types = ["sleep_stages", "apnea", "disease_risk"]
    types_to_run = analysis_types if analysis_types else all_types
    
    # 결과 및 에러 저장
    results = {}
    errors = {}
    
    # 2. 수면 단계 분석
    if "sleep_stages" in types_to_run:
        try:
            stages_data, summary_data = _perform_sleep_stage_analysis(session)
            
            # DB 저장
            analysis = SleepAnalysis(
                session_id=session.id,
                user_id=current_user.id,
                analysis_type="sleep_stage",
                result_data={
                    "stages": [s.model_dump() for s in stages_data],
                    "summary": summary_data.model_dump()
                }
            )
            db.add(analysis)
            
            results["sleep_stages"] = {
                "stages": [s.model_dump() for s in stages_data[-10:]],  # 마지막 10개만 (축약)
                "stage_durations": summary_data.stage_durations
            }
            results["sleep_summary"] = {
                "total_time_minutes": summary_data.total_time_minutes,
                "total_sleep_time_minutes": summary_data.total_sleep_time_minutes,
                "sleep_efficiency": summary_data.sleep_efficiency,
                "sleep_onset_latency": 15.0,  # 더미 값 (실제로는 계산)
                "wake_after_sleep_onset": 30.0  # 더미 값
            }
        except Exception as e:
            logger.error(f"Sleep stage analysis failed: {e}")
            errors["sleep_stages"] = str(e)
    
    # 3. 무호흡 분석
    if "apnea" in types_to_run:
        try:
            events_data, ahi, severity, recommendations = _perform_apnea_analysis(session)
            
            # DB 저장
            analysis = SleepAnalysis(
                session_id=session.id,
                user_id=current_user.id,
                analysis_type="apnea",
                result_data={
                    "events": [e.model_dump() for e in events_data],
                    "ahi": ahi,
                    "severity": severity,
                    "recommendations": recommendations
                }
            )
            db.add(analysis)
            
            results["apnea"] = {
                "ahi": ahi,
                "severity": severity,
                "event_count": len(events_data),
                "recommendations": recommendations
            }
        except Exception as e:
            logger.error(f"Apnea analysis failed: {e}")
            errors["apnea"] = str(e)
    
    # 4. 질병 위험 분석
    if "disease_risk" in types_to_run:
        try:
            predictions_data = _perform_disease_risk_analysis(session)
            
            # DB 저장
            analysis = SleepAnalysis(
                session_id=session.id,
                user_id=current_user.id,
                analysis_type="disease_risk",
                result_data={
                    "predictions": [p.model_dump() for p in predictions_data]
                }
            )
            db.add(analysis)
            
            results["disease_risk"] = {
                "predictions": [p.model_dump() for p in predictions_data]
            }
        except Exception as e:
            logger.error(f"Disease risk analysis failed: {e}")
            errors["disease_risk"] = str(e)
    
    # 세션 상태 업데이트
    if errors:
        session.analysis_status = "partial" if results else "failed"
    else:
        session.analysis_status = "completed"
    
    db.commit()
    
    # 5. 응답 구성
    analysis_status = "completed" if not errors else ("partial" if results else "failed")
    
    response = {
        "session_id": session.id,
        "analysis_status": analysis_status,
        "created_at": datetime.utcnow().isoformat(),
        **results
    }
    
    if errors:
        response["errors"] = errors
    
    logger.info(f"Integrated analysis completed: status={analysis_status}")
    
    return response


@router.get("/{session_id}/status")
def get_analysis_status(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    분석 상태 조회 (Story 4.3)
    
    Args:
        session_id: 세션 ID
        db: 데이터베이스 세션
        current_user: 현재 인증된 사용자
    
    Returns:
        분석 상태 정보
    """
    # 세션 조회
    session = db.query(SleepSession).filter(
        SleepSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}"
        )
    
    # 권한 확인
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )
    
    # 완료된 분석 유형 조회
    analyses = db.query(SleepAnalysis).filter_by(
        session_id=session_id
    ).all()
    
    completed_analyses = [a.analysis_type for a in analyses]
    
    return {
        "session_id": session_id,
        "status": session.analysis_status,
        "completed_analyses": completed_analyses
    }
