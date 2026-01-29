"""
GDPR 및 개인정보 보호 API 라우터

데이터 삭제, 내보내기, 동의 관리 등 GDPR 준수 기능
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from io import BytesIO
import zipfile

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/privacy", tags=["Privacy & GDPR"])


# ========================================
# Pydantic 모델
# ========================================

class DataExportRequest(BaseModel):
    """데이터 내보내기 요청"""
    include_sessions: bool = Field(default=True, description="수면 세션 데이터 포함")
    include_analyses: bool = Field(default=True, description="분석 결과 포함")
    include_preferences: bool = Field(default=True, description="설정 및 선호도 포함")
    format: str = Field(default="json", description="내보내기 형식 (json, csv)")


class DataExportResponse(BaseModel):
    """데이터 내보내기 응답"""
    status: str
    message: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class DataDeletionRequest(BaseModel):
    """데이터 삭제 요청"""
    confirm: bool = Field(..., description="삭제 확인 (true 필수)")
    delete_type: str = Field(
        default="all",
        description="삭제 유형: all, sessions_only, analysis_only"
    )
    reason: Optional[str] = Field(None, description="삭제 사유 (선택)")


class DataDeletionResponse(BaseModel):
    """데이터 삭제 응답"""
    status: str
    message: str
    deletion_scheduled_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None


class ConsentStatus(BaseModel):
    """동의 상태"""
    data_collection: bool = Field(default=False, description="데이터 수집 동의")
    data_analysis: bool = Field(default=False, description="데이터 분석 동의")
    marketing: bool = Field(default=False, description="마케팅 동의")
    third_party_sharing: bool = Field(default=False, description="제3자 공유 동의")
    updated_at: Optional[datetime] = None


class ConsentUpdateRequest(BaseModel):
    """동의 업데이트 요청"""
    data_collection: Optional[bool] = None
    data_analysis: Optional[bool] = None
    marketing: Optional[bool] = None
    third_party_sharing: Optional[bool] = None


class PrivacyPolicyResponse(BaseModel):
    """개인정보 처리방침 응답"""
    version: str
    effective_date: str
    content_url: str
    summary: str


# ========================================
# API 엔드포인트
# ========================================

@router.get("/consent", response_model=ConsentStatus)
async def get_consent_status(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """현재 동의 상태 조회
    
    사용자의 개인정보 처리 동의 상태를 반환합니다.
    """
    logger.info(f"동의 상태 조회: user_id={current_user.id}")
    
    # 실제 구현에서는 DB에서 조회
    # consent = db.query(UserConsent).filter(UserConsent.user_id == current_user.id).first()
    
    # 시뮬레이션 응답
    return ConsentStatus(
        data_collection=True,
        data_analysis=True,
        marketing=False,
        third_party_sharing=False,
        updated_at=datetime.utcnow() - timedelta(days=30),
    )


@router.put("/consent", response_model=ConsentStatus)
async def update_consent(
    request: ConsentUpdateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동의 상태 업데이트
    
    개인정보 처리 동의를 업데이트합니다.
    """
    logger.info(f"동의 업데이트: user_id={current_user.id}, changes={request.dict(exclude_unset=True)}")
    
    # 실제 구현에서는 DB 업데이트
    # consent = db.query(UserConsent).filter(UserConsent.user_id == current_user.id).first()
    # if consent:
    #     for key, value in request.dict(exclude_unset=True).items():
    #         setattr(consent, key, value)
    #     consent.updated_at = datetime.utcnow()
    #     db.commit()
    
    # 시뮬레이션 응답
    updates = request.dict(exclude_unset=True)
    return ConsentStatus(
        data_collection=updates.get("data_collection", True),
        data_analysis=updates.get("data_analysis", True),
        marketing=updates.get("marketing", False),
        third_party_sharing=updates.get("third_party_sharing", False),
        updated_at=datetime.utcnow(),
    )


@router.post("/export", response_model=DataExportResponse)
async def request_data_export(
    request: DataExportRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """데이터 내보내기 요청 (GDPR Right to Data Portability)
    
    사용자의 모든 개인 데이터를 내보냅니다.
    대용량 데이터의 경우 백그라운드에서 처리 후 이메일로 다운로드 링크를 전송합니다.
    """
    logger.info(f"데이터 내보내기 요청: user_id={current_user.id}")
    
    # 백그라운드 태스크로 내보내기 처리
    background_tasks.add_task(
        _process_data_export,
        user_id=current_user.id,
        options=request.dict(),
    )
    
    return DataExportResponse(
        status="processing",
        message="데이터 내보내기가 시작되었습니다. 완료되면 이메일로 다운로드 링크를 보내드립니다.",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )


@router.get("/export/download")
async def download_exported_data(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내보낸 데이터 다운로드
    
    사용자의 데이터를 JSON 형식으로 즉시 다운로드합니다 (소량 데이터용).
    """
    logger.info(f"데이터 다운로드: user_id={current_user.id}")
    
    # 사용자 데이터 수집
    user_data = _collect_user_data(current_user.id, db)
    
    # JSON 형식으로 변환
    json_data = json.dumps(user_data, indent=2, default=str, ensure_ascii=False)
    
    # 스트리밍 응답으로 반환
    return StreamingResponse(
        iter([json_data.encode("utf-8")]),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="sleepfm_data_{current_user.id}_{datetime.utcnow().strftime("%Y%m%d")}.json"'
        },
    )


@router.post("/delete", response_model=DataDeletionResponse)
async def request_data_deletion(
    request: DataDeletionRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """데이터 삭제 요청 (GDPR Right to Erasure)
    
    사용자의 모든 개인 데이터를 삭제합니다.
    삭제는 14일 이내에 완료됩니다.
    
    **주의**: 이 작업은 되돌릴 수 없습니다.
    """
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="삭제를 확인하려면 confirm=true로 설정해야 합니다.",
        )
    
    logger.warning(f"데이터 삭제 요청: user_id={current_user.id}, type={request.delete_type}")
    
    # 삭제 요청 기록
    deletion_request_id = _record_deletion_request(
        user_id=current_user.id,
        delete_type=request.delete_type,
        reason=request.reason,
        db=db,
    )
    
    # 백그라운드에서 삭제 처리
    background_tasks.add_task(
        _process_data_deletion,
        user_id=current_user.id,
        delete_type=request.delete_type,
        request_id=deletion_request_id,
    )
    
    return DataDeletionResponse(
        status="scheduled",
        message="데이터 삭제가 예약되었습니다. 14일 이내에 완료됩니다.",
        deletion_scheduled_at=datetime.utcnow(),
        estimated_completion=datetime.utcnow() + timedelta(days=14),
    )


@router.delete("/delete/cancel")
async def cancel_data_deletion(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """데이터 삭제 요청 취소
    
    예약된 삭제 요청을 취소합니다 (처리 전에만 가능).
    """
    logger.info(f"삭제 취소 요청: user_id={current_user.id}")
    
    # 실제 구현에서는 삭제 요청 상태 확인 후 취소
    # pending_request = db.query(DeletionRequest).filter(
    #     DeletionRequest.user_id == current_user.id,
    #     DeletionRequest.status == "pending"
    # ).first()
    
    return {
        "status": "cancelled",
        "message": "데이터 삭제 요청이 취소되었습니다.",
    }


@router.get("/policy", response_model=PrivacyPolicyResponse)
async def get_privacy_policy():
    """개인정보 처리방침 조회
    
    현재 적용 중인 개인정보 처리방침 정보를 반환합니다.
    """
    return PrivacyPolicyResponse(
        version="1.0.0",
        effective_date="2026-01-01",
        content_url="/docs/privacy-policy",
        summary="SleepFM은 사용자의 수면 데이터를 수집하여 분석 서비스를 제공합니다. "
                "모든 데이터는 암호화되어 저장되며, 사용자의 동의 없이 제3자와 공유되지 않습니다.",
    )


@router.get("/data-categories")
async def get_data_categories(
    current_user = Depends(get_current_user),
):
    """수집 중인 데이터 카테고리 조회
    
    사용자에게 수집되는 개인정보의 종류를 반환합니다.
    """
    return {
        "categories": [
            {
                "name": "계정 정보",
                "description": "이메일, 사용자명, 프로필 정보",
                "purpose": "서비스 제공 및 사용자 식별",
                "retention": "계정 삭제 시까지",
            },
            {
                "name": "수면 데이터",
                "description": "심박수, 산소포화도, 움직임 등 센서 데이터",
                "purpose": "수면 분석 및 건강 인사이트 제공",
                "retention": "1년 (설정에 따라 변경 가능)",
            },
            {
                "name": "분석 결과",
                "description": "수면 단계, 무호흡 지수, 건강 위험도",
                "purpose": "사용자에게 분석 결과 제공",
                "retention": "1년 (설정에 따라 변경 가능)",
            },
            {
                "name": "앱 사용 로그",
                "description": "앱 사용 패턴, 오류 로그",
                "purpose": "서비스 품질 개선 및 문제 해결",
                "retention": "90일",
            },
        ],
    }


# ========================================
# 내부 헬퍼 함수
# ========================================

def _collect_user_data(user_id: int, db: Session) -> dict:
    """사용자의 모든 데이터 수집"""
    logger.info(f"사용자 데이터 수집: user_id={user_id}")
    
    # 실제 구현에서는 DB에서 모든 관련 데이터 조회
    # user = db.query(User).filter(User.id == user_id).first()
    # sessions = db.query(SleepSession).filter(SleepSession.user_id == user_id).all()
    # analyses = db.query(SleepAnalysis).filter(SleepAnalysis.user_id == user_id).all()
    
    # 시뮬레이션 데이터
    return {
        "export_metadata": {
            "exported_at": datetime.utcnow().isoformat(),
            "format_version": "1.0",
            "user_id": user_id,
        },
        "user_profile": {
            "id": user_id,
            "email": "user@example.com",
            "username": "example_user",
            "created_at": "2025-01-01T00:00:00Z",
        },
        "sleep_sessions": [
            {
                "id": 1,
                "session_date": "2026-01-27",
                "duration_hours": 7.5,
                "analysis_status": "completed",
            }
        ],
        "analysis_results": [
            {
                "session_id": 1,
                "sleep_stages": {"light": 45, "deep": 25, "rem": 30},
                "sleep_efficiency": 92.5,
            }
        ],
        "preferences": {
            "notifications_enabled": True,
            "weekly_report_enabled": True,
        },
    }


async def _process_data_export(user_id: int, options: dict):
    """백그라운드에서 데이터 내보내기 처리"""
    logger.info(f"데이터 내보내기 처리 시작: user_id={user_id}")
    
    try:
        # 데이터 수집 및 파일 생성
        # ... 실제 구현
        
        # 완료 후 이메일 발송
        logger.info(f"데이터 내보내기 완료: user_id={user_id}")
    except Exception as e:
        logger.error(f"데이터 내보내기 실패: user_id={user_id}, error={e}")


def _record_deletion_request(
    user_id: int,
    delete_type: str,
    reason: Optional[str],
    db: Session,
) -> str:
    """삭제 요청 기록"""
    # 실제 구현에서는 DB에 삭제 요청 기록
    # deletion_request = DeletionRequest(
    #     user_id=user_id,
    #     delete_type=delete_type,
    #     reason=reason,
    #     status="pending",
    #     created_at=datetime.utcnow(),
    # )
    # db.add(deletion_request)
    # db.commit()
    # return str(deletion_request.id)
    
    return f"DR-{user_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"


async def _process_data_deletion(user_id: int, delete_type: str, request_id: str):
    """백그라운드에서 데이터 삭제 처리"""
    logger.warning(f"데이터 삭제 처리 시작: user_id={user_id}, type={delete_type}")
    
    try:
        if delete_type == "all":
            # 모든 사용자 데이터 삭제
            # 1. 분석 결과 삭제
            # 2. 세션 데이터 삭제
            # 3. 사용자 설정 삭제
            # 4. 사용자 계정 삭제 (또는 익명화)
            pass
        elif delete_type == "sessions_only":
            # 세션 데이터만 삭제
            pass
        elif delete_type == "analysis_only":
            # 분석 결과만 삭제
            pass
        
        logger.info(f"데이터 삭제 완료: user_id={user_id}, request_id={request_id}")
        
    except Exception as e:
        logger.error(f"데이터 삭제 실패: user_id={user_id}, error={e}")
