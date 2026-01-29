"""
알림 관련 Celery 태스크

분석 완료 알림, 위험 경고, 리포트 전송 등
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="app.tasks.notification_tasks.send_analysis_complete_notification",
    queue="notifications",
)
def send_analysis_complete_notification(
    user_id: int,
    session_id: int,
    analysis_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """분석 완료 알림 전송
    
    Args:
        user_id: 사용자 ID
        session_id: 세션 ID
        analysis_summary: 분석 요약 정보
    
    Returns:
        알림 전송 결과
    """
    try:
        logger.info(f"분석 완료 알림 전송: user_id={user_id}, session_id={session_id}")
        
        # 알림 내용 생성
        notification = {
            "type": "analysis_complete",
            "title": "수면 분석 완료",
            "body": _build_analysis_summary_message(analysis_summary),
            "data": {
                "session_id": session_id,
                "action": "view_analysis",
            },
        }
        
        # 푸시 알림 전송 (실제 구현에서는 FCM/APNs 사용)
        # _send_push_notification(user_id, notification)
        
        # 인앱 알림 저장
        # _save_in_app_notification(user_id, notification)
        
        return {
            "status": "success",
            "user_id": user_id,
            "notification_type": "analysis_complete",
            "sent_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"알림 전송 실패: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(
    name="app.tasks.notification_tasks.send_health_alert",
    queue="notifications",
)
def send_health_alert(
    user_id: int,
    alert_type: str,
    severity: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:
    """건강 경고 알림 전송
    
    Args:
        user_id: 사용자 ID
        alert_type: 경고 타입 (apnea_high, poor_sleep, etc.)
        severity: 심각도 (low, medium, high, critical)
        details: 상세 정보
    """
    try:
        logger.info(f"건강 경고 알림: user_id={user_id}, type={alert_type}, severity={severity}")
        
        # 심각도별 알림 우선순위 설정
        priority = _get_alert_priority(severity)
        
        notification = {
            "type": "health_alert",
            "title": _get_alert_title(alert_type),
            "body": _get_alert_body(alert_type, details),
            "priority": priority,
            "data": {
                "alert_type": alert_type,
                "severity": severity,
                "action": "view_health_details",
            },
        }
        
        # 심각도가 높으면 즉시 전송
        if severity in ["high", "critical"]:
            logger.warning(f"고위험 경고: user_id={user_id}, type={alert_type}")
            # _send_immediate_push(user_id, notification)
        
        return {
            "status": "success",
            "user_id": user_id,
            "alert_type": alert_type,
            "severity": severity,
            "sent_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"건강 경고 전송 실패: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(
    name="app.tasks.notification_tasks.send_weekly_report",
    queue="notifications",
)
def send_weekly_report(
    user_id: int,
    report_data: Dict[str, Any],
) -> Dict[str, Any]:
    """주간 리포트 알림 전송"""
    try:
        logger.info(f"주간 리포트 전송: user_id={user_id}")
        
        notification = {
            "type": "weekly_report",
            "title": "주간 수면 리포트",
            "body": _build_weekly_summary(report_data),
            "data": {
                "action": "view_weekly_report",
                "week_start": report_data.get("week_start"),
            },
        }
        
        return {
            "status": "success",
            "user_id": user_id,
            "notification_type": "weekly_report",
            "sent_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"주간 리포트 전송 실패: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(
    name="app.tasks.notification_tasks.send_batch_notifications",
    queue="notifications",
)
def send_batch_notifications(
    user_ids: List[int],
    notification_type: str,
    content: Dict[str, Any],
) -> Dict[str, Any]:
    """대량 알림 전송"""
    logger.info(f"대량 알림 전송: {len(user_ids)}명, type={notification_type}")
    
    success_count = 0
    failure_count = 0
    
    for user_id in user_ids:
        try:
            # 개별 알림 전송 (실제 구현)
            success_count += 1
        except Exception as e:
            logger.error(f"알림 실패: user_id={user_id}, error={e}")
            failure_count += 1
    
    return {
        "status": "success",
        "total": len(user_ids),
        "success": success_count,
        "failure": failure_count,
        "sent_at": datetime.utcnow().isoformat(),
    }


# ========================================
# 내부 헬퍼 함수들
# ========================================

def _build_analysis_summary_message(summary: Dict[str, Any]) -> str:
    """분석 요약 메시지 생성"""
    sleep_efficiency = summary.get("sleep_efficiency", 0)
    total_hours = summary.get("total_duration_hours", 0)
    
    if sleep_efficiency >= 85:
        quality = "좋음 😊"
    elif sleep_efficiency >= 70:
        quality = "보통 😐"
    else:
        quality = "개선 필요 😔"
    
    return f"어젯밤 {total_hours:.1f}시간 수면, 수면 효율 {sleep_efficiency:.0f}% ({quality})"


def _get_alert_priority(severity: str) -> str:
    """심각도에 따른 알림 우선순위"""
    priority_map = {
        "low": "normal",
        "medium": "normal",
        "high": "high",
        "critical": "urgent",
    }
    return priority_map.get(severity, "normal")


def _get_alert_title(alert_type: str) -> str:
    """경고 타입별 제목"""
    titles = {
        "apnea_high": "⚠️ 무호흡 지수 높음",
        "poor_sleep": "😴 수면의 질 저하 감지",
        "irregular_pattern": "🌙 불규칙한 수면 패턴",
        "cardiovascular_risk": "❤️ 심혈관 위험 주의",
        "fatigue_warning": "😵 피로 누적 경고",
    }
    return titles.get(alert_type, "건강 알림")


def _get_alert_body(alert_type: str, details: Dict[str, Any]) -> str:
    """경고 타입별 본문"""
    if alert_type == "apnea_high":
        ahi = details.get("ahi", 0)
        return f"무호흡-저호흡 지수(AHI)가 {ahi:.1f}으로 측정되었습니다. 전문가 상담을 권장합니다."
    
    elif alert_type == "poor_sleep":
        efficiency = details.get("sleep_efficiency", 0)
        return f"수면 효율이 {efficiency:.0f}%로 낮습니다. 수면 환경을 개선해보세요."
    
    elif alert_type == "irregular_pattern":
        return "최근 수면 시간이 불규칙합니다. 일정한 취침 시간을 유지해보세요."
    
    return "건강 상태를 확인해주세요."


def _build_weekly_summary(report_data: Dict[str, Any]) -> str:
    """주간 리포트 요약"""
    avg_hours = report_data.get("avg_sleep_hours", 0)
    avg_efficiency = report_data.get("avg_sleep_efficiency", 0)
    
    return f"이번 주 평균 수면: {avg_hours:.1f}시간, 평균 효율: {avg_efficiency:.0f}%"
