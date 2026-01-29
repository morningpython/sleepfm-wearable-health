"""
Sprint 10: Sentry 에러 추적 통합

에러 리포팅, 성능 모니터링
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
from typing import Optional, Dict, Any
from functools import wraps


def init_sentry(
    dsn: str,
    environment: str = "development",
    release: Optional[str] = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1
):
    """
    Sentry 초기화
    
    Args:
        dsn: Sentry DSN
        environment: 환경 (development, staging, production)
        release: 릴리스 버전
        traces_sample_rate: 트레이스 샘플링 비율
        profiles_sample_rate: 프로파일링 샘플링 비율
    """
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        
        # 통합
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint"
            ),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ],
        
        # 성능 모니터링
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        
        # 민감 정보 필터링
        before_send=before_send_filter,
        
        # 트레이스 전 필터
        before_send_transaction=before_send_transaction_filter,
        
        # 추가 설정
        attach_stacktrace=True,
        send_default_pii=False,  # 개인 정보 전송 안 함
        max_breadcrumbs=50,
    )


def before_send_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Sentry 전송 전 이벤트 필터링
    민감 정보 제거, 불필요한 에러 필터링
    """
    # 민감 정보 필터링
    if 'request' in event:
        request_data = event['request']
        
        # 헤더에서 Authorization 제거
        if 'headers' in request_data:
            headers = request_data['headers']
            if isinstance(headers, dict):
                headers.pop('Authorization', None)
                headers.pop('authorization', None)
                headers.pop('Cookie', None)
                headers.pop('cookie', None)
        
        # 바디에서 비밀번호 제거
        if 'data' in request_data:
            data = request_data['data']
            if isinstance(data, dict):
                data.pop('password', None)
                data.pop('current_password', None)
                data.pop('new_password', None)
    
    # 특정 예외 무시
    if 'exception' in event:
        exc_values = event['exception'].get('values', [])
        for exc in exc_values:
            exc_type = exc.get('type', '')
            
            # 무시할 예외 타입
            ignored_exceptions = [
                'ConnectionResetError',
                'BrokenPipeError',
                'ClientDisconnect',
            ]
            
            if exc_type in ignored_exceptions:
                return None
    
    return event


def before_send_transaction_filter(
    event: Dict[str, Any], 
    hint: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    트랜잭션 전송 전 필터링
    헬스체크 등 불필요한 트랜잭션 제외
    """
    transaction_name = event.get('transaction', '')
    
    # 무시할 엔드포인트
    ignored_endpoints = [
        '/health',
        '/healthz',
        '/ready',
        '/readiness',
        '/metrics',
        '/favicon.ico',
    ]
    
    for endpoint in ignored_endpoints:
        if transaction_name.endswith(endpoint):
            return None
    
    return event


def capture_exception(error: Exception, **kwargs):
    """
    예외 캡처 헬퍼
    
    Args:
        error: 예외 객체
        **kwargs: 추가 컨텍스트
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in kwargs.items():
            scope.set_extra(key, value)
        
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", **kwargs):
    """
    메시지 캡처 헬퍼
    
    Args:
        message: 메시지
        level: 로그 레벨 (debug, info, warning, error, fatal)
        **kwargs: 추가 컨텍스트
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in kwargs.items():
            scope.set_extra(key, value)
        
        sentry_sdk.capture_message(message, level=level)


def set_user(user_id: int, email: Optional[str] = None, username: Optional[str] = None):
    """
    현재 스코프에 사용자 정보 설정
    
    Args:
        user_id: 사용자 ID
        email: 이메일 (선택)
        username: 사용자명 (선택)
    """
    sentry_sdk.set_user({
        "id": str(user_id),
        "email": email,
        "username": username,
    })


def set_tag(key: str, value: str):
    """태그 설정"""
    sentry_sdk.set_tag(key, value)


def set_context(name: str, context: Dict[str, Any]):
    """커스텀 컨텍스트 설정"""
    sentry_sdk.set_context(name, context)


def trace(operation_name: str, description: Optional[str] = None):
    """
    함수 트레이싱 데코레이터
    
    Usage:
        @trace("database.query", "Fetch user sessions")
        async def get_user_sessions(user_id: int):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with sentry_sdk.start_span(op=operation_name, description=description):
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with sentry_sdk.start_span(op=operation_name, description=description):
                return func(*args, **kwargs)
        
        # 비동기 함수 여부 확인
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class SentryMiddleware:
    """
    FastAPI용 Sentry 미들웨어
    요청별 컨텍스트 설정
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # 요청 ID 설정
        import uuid
        request_id = str(uuid.uuid4())
        
        with sentry_sdk.push_scope() as sentry_scope:
            sentry_scope.set_tag("request_id", request_id)
            sentry_scope.set_context("request", {
                "method": scope.get("method"),
                "path": scope.get("path"),
                "query_string": scope.get("query_string", b"").decode(),
            })
            
            await self.app(scope, receive, send)


def setup_sentry(app, dsn: Optional[str] = None, environment: str = "development"):
    """
    FastAPI 앱에 Sentry 설정
    
    Args:
        app: FastAPI 앱
        dsn: Sentry DSN (None이면 비활성화)
        environment: 환경
    """
    if not dsn:
        return app
    
    init_sentry(
        dsn=dsn,
        environment=environment,
        release="sleepfm@1.0.0",
    )
    
    # 미들웨어 추가
    app.add_middleware(SentryMiddleware)
    
    return app
