"""
Celery 설정 및 비동기 작업 큐

무거운 작업(모델 추론, 분석)을 백그라운드에서 비동기 처리
"""

from celery import Celery
from kombu import Queue
import os

# Celery 앱 설정
celery_app = Celery(
    "sleepfm_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
    include=[
        "app.tasks.analysis_tasks",
        "app.tasks.notification_tasks",
    ]
)

# Celery 설정
celery_app.conf.update(
    # 시리얼라이제이션
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 타임존
    timezone="UTC",
    enable_utc=True,
    
    # 태스크 설정
    task_track_started=True,
    task_time_limit=600,  # 10분 타임아웃
    task_soft_time_limit=540,  # 9분 소프트 타임아웃
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # 재시도 설정
    task_default_retry_delay=60,
    task_max_retries=3,
    
    # 워커 설정
    worker_prefetch_multiplier=1,  # 하나씩 처리
    worker_concurrency=4,
    
    # 결과 백엔드 설정
    result_expires=3600,  # 결과 1시간 후 만료
    result_extended=True,
    
    # 큐 설정
    task_queues=(
        Queue("default", routing_key="default"),
        Queue("analysis", routing_key="analysis.#"),
        Queue("notifications", routing_key="notifications.#"),
        Queue("high_priority", routing_key="high.#"),
    ),
    task_default_queue="default",
    task_default_exchange="tasks",
    task_default_routing_key="default",
    
    # 라우팅
    task_routes={
        "app.tasks.analysis_tasks.*": {"queue": "analysis"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
    },
    
    # 비트 스케줄 (선택적)
    beat_schedule={
        "cleanup-expired-sessions": {
            "task": "app.tasks.analysis_tasks.cleanup_expired_sessions",
            "schedule": 3600.0,  # 매시간
        },
    },
)


def get_celery_app() -> Celery:
    """Celery 앱 인스턴스 반환"""
    return celery_app
