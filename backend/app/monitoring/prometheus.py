"""
Sprint 10: Prometheus 메트릭 Exporter

API 요청, 응답 시간, 에러율 등 메트릭 수집
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable
import psutil


# 메트릭 정의
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0)
)

REQUESTS_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)

# 시스템 메트릭
CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
MEMORY_USAGE = Gauge('system_memory_usage_percent', 'System memory usage percentage')
DISK_USAGE = Gauge('system_disk_usage_percent', 'System disk usage percentage')

# 애플리케이션 메트릭
ACTIVE_USERS = Gauge('app_active_users', 'Number of active users')
TOTAL_SESSIONS = Gauge('app_total_sessions', 'Total sleep sessions')
ANALYSIS_COUNT = Counter(
    'app_analysis_total',
    'Total analysis requests',
    ['analysis_type']
)

# 앱 정보
APP_INFO = Info('app', 'Application information')
APP_INFO.info({
    'name': 'SleepFM',
    'version': '1.0.0',
    'environment': 'development'
})


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Prometheus 메트릭 수집 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        endpoint = self._get_endpoint_label(request.url.path)
        
        # 진행 중인 요청 증가
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            
            # 요청 카운트 증가
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            # 에러 카운트
            if response.status_code >= 400:
                error_type = self._get_error_type(response.status_code)
                ERROR_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=error_type
                ).inc()
            
            return response
            
        except Exception as e:
            # 예외 발생 시
            ERROR_COUNT.labels(
                method=method,
                endpoint=endpoint,
                error_type='exception'
            ).inc()
            raise
            
        finally:
            # 응답 시간 기록
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # 진행 중인 요청 감소
            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()
    
    def _get_endpoint_label(self, path: str) -> str:
        """경로를 레이블로 변환 (파라미터 일반화)"""
        # /api/v1/users/123/sessions → /api/v1/users/{id}/sessions
        parts = path.split('/')
        normalized = []
        
        for part in parts:
            if part.isdigit():
                normalized.append('{id}')
            else:
                normalized.append(part)
        
        return '/'.join(normalized)
    
    def _get_error_type(self, status_code: int) -> str:
        """상태 코드에 따른 에러 타입"""
        if status_code == 400:
            return 'bad_request'
        elif status_code == 401:
            return 'unauthorized'
        elif status_code == 403:
            return 'forbidden'
        elif status_code == 404:
            return 'not_found'
        elif status_code == 422:
            return 'validation_error'
        elif status_code >= 500:
            return 'server_error'
        else:
            return 'client_error'


def update_system_metrics():
    """시스템 메트릭 업데이트"""
    try:
        CPU_USAGE.set(psutil.cpu_percent())
        MEMORY_USAGE.set(psutil.virtual_memory().percent)
        DISK_USAGE.set(psutil.disk_usage('/').percent)
    except Exception:
        pass


def record_analysis(analysis_type: str):
    """분석 요청 기록"""
    ANALYSIS_COUNT.labels(analysis_type=analysis_type).inc()


def set_active_users(count: int):
    """활성 사용자 수 설정"""
    ACTIVE_USERS.set(count)


def set_total_sessions(count: int):
    """총 세션 수 설정"""
    TOTAL_SESSIONS.set(count)


async def metrics_endpoint(request: Request) -> Response:
    """Prometheus 메트릭 엔드포인트"""
    # 시스템 메트릭 업데이트
    update_system_metrics()
    
    # 메트릭 생성
    metrics = generate_latest()
    
    return Response(
        content=metrics,
        media_type=CONTENT_TYPE_LATEST
    )


def setup_prometheus(app):
    """FastAPI 앱에 Prometheus 설정"""
    from fastapi import FastAPI
    
    # 미들웨어 추가
    app.add_middleware(PrometheusMiddleware)
    
    # 메트릭 엔드포인트 추가
    app.add_route('/metrics', metrics_endpoint, methods=['GET'])
    
    return app
