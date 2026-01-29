"""
보안 미들웨어 및 유틸리티

OWASP Top 10 대응, Rate Limiting, 입력 검증 등
"""

import re
import html
import logging
from typing import Optional, List, Callable
from datetime import datetime, timedelta
from functools import wraps

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# ========================================
# Rate Limiting
# ========================================

class RateLimitStore:
    """Rate Limit 저장소 (메모리 기반, 프로덕션에서는 Redis 사용)"""
    
    def __init__(self):
        self._store: dict = {}
        self._cleanup_interval = timedelta(minutes=5)
        self._last_cleanup = datetime.utcnow()
    
    def _cleanup(self):
        """만료된 항목 정리"""
        now = datetime.utcnow()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        expired_keys = [
            key for key, data in self._store.items()
            if now > data["expires_at"]
        ]
        for key in expired_keys:
            del self._store[key]
        
        self._last_cleanup = now
    
    def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """Rate limit 확인
        
        Returns:
            (is_limited, remaining_requests)
        """
        self._cleanup()
        
        now = datetime.utcnow()
        
        if key not in self._store:
            self._store[key] = {
                "count": 1,
                "expires_at": now + timedelta(seconds=window_seconds),
            }
            return False, max_requests - 1
        
        data = self._store[key]
        
        # 윈도우 만료 시 리셋
        if now > data["expires_at"]:
            self._store[key] = {
                "count": 1,
                "expires_at": now + timedelta(seconds=window_seconds),
            }
            return False, max_requests - 1
        
        # 요청 카운트 증가
        data["count"] += 1
        remaining = max(0, max_requests - data["count"])
        
        return data["count"] > max_requests, remaining


# 전역 Rate Limit 저장소
_rate_limit_store = RateLimitStore()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate Limiting 미들웨어"""
    
    def __init__(
        self,
        app,
        default_limit: int = 100,
        default_window: int = 60,
        exempt_paths: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 예외 경로 확인
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # 클라이언트 식별
        client_ip = self._get_client_ip(request)
        key = f"rate_limit:{client_ip}"
        
        # Rate limit 확인
        is_limited, remaining = _rate_limit_store.is_rate_limited(
            key, self.default_limit, self.default_window
        )
        
        if is_limited:
            logger.warning(f"Rate limit 초과: IP={client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
                    "retry_after": self.default_window,
                },
                headers={"Retry-After": str(self.default_window)},
            )
        
        response = await call_next(request)
        
        # Rate limit 헤더 추가
        response.headers["X-RateLimit-Limit"] = str(self.default_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 추출"""
        # 프록시 뒤에서 실제 IP 가져오기
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


# ========================================
# 입력 검증 및 Sanitization
# ========================================

class InputSanitizer:
    """입력 데이터 정제"""
    
    # XSS 방지를 위한 위험 패턴
    XSS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'<iframe[^>]*>', re.IGNORECASE),
        re.compile(r'<object[^>]*>', re.IGNORECASE),
        re.compile(r'<embed[^>]*>', re.IGNORECASE),
    ]
    
    # SQL Injection 패턴 (경고용)
    SQL_PATTERNS = [
        re.compile(r'\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b', re.IGNORECASE),
        re.compile(r'(--|#|/\*)', re.IGNORECASE),
        re.compile(r'(\bOR\b|\bAND\b)\s+\d+\s*=\s*\d+', re.IGNORECASE),
        re.compile(r"'\s*(OR|AND)\s+'", re.IGNORECASE),
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 10000) -> str:
        """문자열 정제
        
        - HTML 이스케이프
        - 길이 제한
        - 위험 패턴 제거
        """
        if not isinstance(value, str):
            return value
        
        # 길이 제한
        value = value[:max_length]
        
        # HTML 이스케이프
        value = html.escape(value)
        
        # XSS 패턴 제거
        for pattern in cls.XSS_PATTERNS:
            value = pattern.sub('', value)
        
        return value.strip()
    
    @classmethod
    def check_sql_injection(cls, value: str) -> bool:
        """SQL Injection 패턴 감지 (경고용)"""
        if not isinstance(value, str):
            return False
        
        for pattern in cls.SQL_PATTERNS:
            if pattern.search(value):
                return True
        return False
    
    @classmethod
    def sanitize_email(cls, email: str) -> str:
        """이메일 정제 및 검증"""
        email = email.strip().lower()
        
        # 기본 이메일 형식 검증
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            raise ValueError("유효하지 않은 이메일 형식입니다.")
        
        # 길이 제한
        if len(email) > 254:
            raise ValueError("이메일이 너무 깁니다.")
        
        return email
    
    @classmethod
    def sanitize_username(cls, username: str, min_len: int = 3, max_len: int = 50) -> str:
        """사용자명 정제"""
        username = username.strip()
        
        # 허용 문자만 (알파벳, 숫자, 언더스코어)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("사용자명은 알파벳, 숫자, 언더스코어만 포함할 수 있습니다.")
        
        if len(username) < min_len:
            raise ValueError(f"사용자명은 최소 {min_len}자 이상이어야 합니다.")
        
        if len(username) > max_len:
            raise ValueError(f"사용자명은 최대 {max_len}자까지 가능합니다.")
        
        return username


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 추가 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # OWASP 권장 보안 헤더
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # 민감 정보 노출 방지
        response.headers["X-Powered-By"] = ""
        
        return response


# ========================================
# SQL Injection 방지
# ========================================

def validate_query_params(params: dict) -> dict:
    """쿼리 파라미터 검증
    
    SQL Injection 시도 감지 및 경고
    """
    sanitized = {}
    
    for key, value in params.items():
        if isinstance(value, str):
            # SQL Injection 패턴 감지
            if InputSanitizer.check_sql_injection(value):
                logger.warning(f"SQL Injection 시도 감지: key={key}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="잘못된 입력값입니다.",
                )
            
            # 정제된 값 저장
            sanitized[key] = InputSanitizer.sanitize_string(value)
        else:
            sanitized[key] = value
    
    return sanitized


# ========================================
# 보안 데코레이터
# ========================================

def require_https(func: Callable):
    """HTTPS 강제 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request") or args[0]
        
        if not request.url.scheme == "https":
            # 개발 환경에서는 허용
            if request.url.hostname not in ["localhost", "127.0.0.1"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="HTTPS 연결이 필요합니다.",
                )
        
        return await func(*args, **kwargs)
    
    return wrapper


def sanitize_input(fields: Optional[List[str]] = None):
    """입력값 정제 데코레이터
    
    Args:
        fields: 정제할 필드 목록. None이면 모든 문자열 필드 정제
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Request body 정제
            for key, value in kwargs.items():
                if isinstance(value, str):
                    if fields is None or key in fields:
                        kwargs[key] = InputSanitizer.sanitize_string(value)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# ========================================
# 보안 유틸리티 함수
# ========================================

def mask_sensitive_data(data: dict, sensitive_keys: Optional[List[str]] = None) -> dict:
    """민감 데이터 마스킹"""
    sensitive_keys = sensitive_keys or [
        "password", "token", "secret", "api_key", "access_token", 
        "refresh_token", "authorization", "credit_card", "ssn"
    ]
    
    masked = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            masked[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_data(value, sensitive_keys)
        else:
            masked[key] = value
    
    return masked


def generate_csrf_token(session_id: str, secret: str) -> str:
    """CSRF 토큰 생성"""
    import hashlib
    import time
    
    timestamp = str(int(time.time()))
    data = f"{session_id}:{timestamp}:{secret}"
    token = hashlib.sha256(data.encode()).hexdigest()
    
    return f"{timestamp}:{token}"


def verify_csrf_token(
    token: str, 
    session_id: str, 
    secret: str,
    max_age: int = 3600,
) -> bool:
    """CSRF 토큰 검증"""
    import hashlib
    import time
    
    try:
        parts = token.split(":")
        if len(parts) != 2:
            return False
        
        timestamp, hash_value = parts
        
        # 만료 확인
        if int(time.time()) - int(timestamp) > max_age:
            return False
        
        # 해시 검증
        data = f"{session_id}:{timestamp}:{secret}"
        expected_hash = hashlib.sha256(data.encode()).hexdigest()
        
        return hash_value == expected_hash
        
    except Exception:
        return False
