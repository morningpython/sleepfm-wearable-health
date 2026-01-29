"""
Sprint 9: 구조화된 로깅 설정

JSON 형식의 구조화된 로그 출력
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Optional
import traceback


class JSONFormatter(logging.Formatter):
    """JSON 형식 로그 포매터"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 추가 컨텍스트
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        if hasattr(record, "path"):
            log_data["path"] = record.path
        
        if hasattr(record, "method"):
            log_data["method"] = record.method
        
        # 예외 정보
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if record.exc_info[0] else None
            }
        
        # 추가 데이터
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class ContextLogger:
    """컨텍스트 정보를 포함하는 로거"""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._context: dict = {}
    
    def bind(self, **kwargs) -> "ContextLogger":
        """컨텍스트 바인딩"""
        new_logger = ContextLogger(self._logger)
        new_logger._context = {**self._context, **kwargs}
        return new_logger
    
    def _log(self, level: int, message: str, **kwargs):
        """로그 출력"""
        extra = {**self._context, **kwargs}
        record = self._logger.makeRecord(
            self._logger.name,
            level,
            "(unknown)",
            0,
            message,
            (),
            None
        )
        for key, value in extra.items():
            setattr(record, key, value)
        self._logger.handle(record)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, exc_info=None, **kwargs):
        if exc_info:
            self._logger.error(message, exc_info=exc_info, extra={**self._context, **kwargs})
        else:
            self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    log_file: Optional[str] = None
) -> ContextLogger:
    """
    로깅 설정
    
    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: JSON 형식 사용 여부
        log_file: 로그 파일 경로 (선택)
    
    Returns:
        설정된 ContextLogger
    """
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # 기존 핸들러 제거
    root_logger.handlers.clear()
    
    # 포매터
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 파일 핸들러 (선택)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 앱 로거
    app_logger = logging.getLogger("sleepfm")
    app_logger.setLevel(getattr(logging, level.upper()))
    
    return ContextLogger(app_logger)


# 전역 로거 인스턴스
logger = setup_logging()


def get_logger(name: str = "sleepfm") -> ContextLogger:
    """이름이 지정된 로거 반환"""
    return ContextLogger(logging.getLogger(name))
