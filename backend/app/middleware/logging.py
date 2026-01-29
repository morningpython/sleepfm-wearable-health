"""
Sprint 9: API 요청/응답 로깅 미들웨어
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logging import get_logger


logger = get_logger("sleepfm.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """API 요청/응답 로깅 미들웨어"""
    
    def __init__(self, app: ASGIApp, exclude_paths: list[str] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 제외 경로 확인
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # 요청 ID 생성
        request_id = str(uuid.uuid4())[:8]
        
        # 시작 시간
        start_time = time.time()
        
        # 요청 로깅
        request_logger = logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        request_logger.info(f"Request started: {request.method} {request.url.path}")
        
        # 요청 처리
        try:
            response = await call_next(request)
            
            # 응답 시간 계산
            duration_ms = (time.time() - start_time) * 1000
            
            # 응답 로깅
            request_logger.info(
                f"Request completed: {request.method} {request.url.path}",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2)
            )
            
            # 응답 헤더에 요청 ID 추가
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # 에러 로깅
            duration_ms = (time.time() - start_time) * 1000
            
            request_logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=True,
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """Prometheus 메트릭 수집 미들웨어"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_count = {}  # path -> count
        self.request_latency = {}  # path -> [latencies]
        self.error_count = {}  # path -> count
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 요청 카운트
            self.request_count[path] = self.request_count.get(path, 0) + 1
            
            # 지연 시간
            latency = time.time() - start_time
            if path not in self.request_latency:
                self.request_latency[path] = []
            self.request_latency[path].append(latency)
            
            # 최근 100개만 유지
            if len(self.request_latency[path]) > 100:
                self.request_latency[path] = self.request_latency[path][-100:]
            
            # 에러 카운트 (4xx, 5xx)
            if response.status_code >= 400:
                self.error_count[path] = self.error_count.get(path, 0) + 1
            
            return response
            
        except Exception as e:
            self.error_count[path] = self.error_count.get(path, 0) + 1
            raise
    
    def get_metrics(self) -> dict:
        """메트릭 반환"""
        metrics = {
            "request_count": self.request_count.copy(),
            "error_count": self.error_count.copy(),
            "avg_latency": {}
        }
        
        for path, latencies in self.request_latency.items():
            if latencies:
                metrics["avg_latency"][path] = sum(latencies) / len(latencies)
        
        return metrics
