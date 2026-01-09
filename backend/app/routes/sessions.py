import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import SleepSession, User
from app.schemas.sessions import SensorDataUpload, SleepSessionResponse

router = APIRouter(prefix="/sessions", tags=["Sleep Sessions"])
logger = logging.getLogger("app")


def save_sensor_data(user_id: int, session_id: int, data: SensorDataUpload) -> str:
    """센서 데이터를 파일로 저장"""
    if settings.storage_type == "local":
        # 로컬 스토리지
        storage_dir = Path(settings.storage_path) / f"user_{user_id}" / f"session_{session_id}"
        storage_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{data.session_date.strftime('%Y%m%d_%H%M%S')}.json"
        file_path = storage_dir / filename

        # 데이터를 JSON으로 저장
        json_data = {
            "device_type": data.device_type,
            "sampling_rate": data.sampling_rate,
            "duration_hours": data.duration_hours,
            "data": [item.model_dump() for item in data.data],
        }

        with open(file_path, "w") as f:
            json.dump(json_data, f, indent=2)

        return str(file_path)
    else:
        # S3 스토리지 (추후 구현)
        raise NotImplementedError("S3 저장소는 아직 구현되지 않았습니다")


@router.post("/upload", response_model=SleepSessionResponse, status_code=status.HTTP_201_CREATED)
async def upload_sensor_data(
    session_data: SensorDataUpload,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    센서 데이터 업로드

    - **session_date**: 수면 세션 시작 시간
    - **duration_hours**: 수면 시간 (1-24시간)
    - **device_type**: 기기 유형 (apple_watch, galaxy_watch 등)
    - **data**: 센서 데이터 배열

    반환:
    - **session_id**: 생성된 세션 ID
    - **analysis_status**: 분석 상태 (pending)
    """
    # 데이터 검증
    if not session_data.data:
        logger.warning(f"업로드 실패: 빈 센서 데이터 (user_id={current_user.id})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="센서 데이터가 없습니다",
        )

    # 새 수면 세션 생성
    new_session = SleepSession(
        user_id=current_user.id,
        session_date=session_data.session_date,
        duration_hours=session_data.duration_hours,
        analysis_status="pending",
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    logger.info(f"새 수면 세션 생성: session_id={new_session.id}, user_id={current_user.id}")

    # 센서 데이터 저장
    try:
        raw_data_path = save_sensor_data(current_user.id, new_session.id, session_data)
        new_session.raw_data_path = raw_data_path
        db.commit()
        db.refresh(new_session)
        logger.info(f"센서 데이터 저장: {raw_data_path}")
    except Exception as e:
        logger.error(f"센서 데이터 저장 실패: {str(e)}", exc_info=True)
        new_session.analysis_status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="데이터 저장 중 오류가 발생했습니다",
        )

    return new_session


@router.get("/{session_id}", response_model=SleepSessionResponse)
async def get_session(
    session_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    수면 세션 조회

    - **session_id**: 세션 ID
    """
    session = (
        db.query(SleepSession)
        .filter(
            SleepSession.id == session_id,
            SleepSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        logger.warning(
            f"세션 조회 실패: 세션 없음 (session_id={session_id}, user_id={current_user.id})"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다",
        )

    return session


@router.get("/", response_model=list[SleepSessionResponse])
async def list_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 10,
):
    """
    사용자의 수면 세션 목록 조회

    - **skip**: 건너뛸 항목 수 (페이징)
    - **limit**: 반환할 항목 수 (최대 100)
    """
    if limit > 100:
        limit = 100

    sessions = (
        db.query(SleepSession)
        .filter(SleepSession.user_id == current_user.id)
        .order_by(SleepSession.session_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return sessions
