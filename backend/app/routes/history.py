"""
사용자 세션 및 분석 히스토리 API 라우트

Story 4.4: 분석 결과 조회 및 히스토리
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, SleepSession, SleepAnalysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["history"])


@router.get("/users/{user_id}/sessions")
def get_user_sessions(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    사용자의 수면 세션 목록 조회 (Story 4.4)
    
    Args:
        user_id: 사용자 ID
        limit: 페이지 크기 (기본 10)
        offset: 오프셋 (페이지네이션)
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        db: 데이터베이스 세션
        current_user: 현재 인증된 사용자
    
    Returns:
        세션 목록 및 메타데이터
    """
    # 권한 확인 (본인만 조회 가능)
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's sessions"
        )
    
    # 기본 쿼리
    query = db.query(SleepSession).filter(SleepSession.user_id == user_id)
    
    # 날짜 필터링
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(SleepSession.session_date >= start_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            # end_date 다음 날 00:00까지 포함
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(SleepSession.session_date <= end_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )
    
    # 전체 개수
    total = query.count()
    
    # 정렬 및 페이지네이션
    sessions = query.order_by(SleepSession.session_date.desc()) \
                    .offset(offset) \
                    .limit(limit) \
                    .all()
    
    # 각 세션의 분석 결과 존재 여부 확인
    session_list = []
    for session in sessions:
        # 해당 세션의 분석 개수
        analysis_count = db.query(func.count(SleepAnalysis.id)).filter(
            SleepAnalysis.session_id == session.id
        ).scalar()
        
        session_list.append({
            "id": session.id,
            "session_date": session.session_date.isoformat(),
            "duration_hours": session.duration_hours,
            "analysis_status": session.analysis_status,
            "has_results": analysis_count > 0
        })
    
    return {
        "sessions": session_list,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/sessions/{session_id}/results")
def get_session_results(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    세션의 모든 분석 결과 조회 (Story 4.4)
    
    Args:
        session_id: 세션 ID
        db: 데이터베이스 세션
        current_user: 현재 인증된 사용자
    
    Returns:
        세션 정보 및 모든 분석 결과
    """
    # 세션 조회 (권한 확인 포함)
    session = db.query(SleepSession).filter(
        SleepSession.id == session_id,
        SleepSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found or not authorized: {session_id}"
        )
    
    # 해당 세션의 모든 분석 결과 조회
    analyses = db.query(SleepAnalysis).filter(
        SleepAnalysis.session_id == session_id
    ).order_by(SleepAnalysis.created_at.desc()).all()
    
    # 분석 결과 포맷팅
    analyses_list = []
    for analysis in analyses:
        analyses_list.append({
            "id": analysis.id,
            "type": analysis.analysis_type,
            "result": analysis.result_data,
            "created_at": analysis.created_at.isoformat()
        })
    
    return {
        "session_id": session.id,
        "session_date": session.session_date.isoformat(),
        "duration_hours": session.duration_hours,
        "analysis_status": session.analysis_status,
        "analyses": analyses_list
    }
