"""
캐시 유틸리티

캐싱 데코레이터 및 헬퍼 함수
"""

import hashlib
import json
import functools
import logging
from typing import Optional, Any, Callable, Union
from datetime import timedelta
from dataclasses import dataclass

from app.cache.redis_client import get_redis_client

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """캐시 설정"""
    ttl: Union[int, timedelta] = 300  # 기본 5분
    prefix: str = "sleepfm"
    enabled: bool = True
    
    # 캐시 키 타입별 TTL
    ANALYSIS_TTL = timedelta(hours=1)  # 분석 결과
    SESSION_TTL = timedelta(minutes=30)  # 세션 데이터
    USER_TTL = timedelta(minutes=15)  # 사용자 정보
    STATS_TTL = timedelta(minutes=5)  # 통계 데이터


def cache_key(*args, prefix: str = "sleepfm", **kwargs) -> str:
    """캐시 키 생성
    
    Args:
        *args: 키 구성 요소
        prefix: 키 프리픽스
        **kwargs: 추가 키-값 쌍
        
    Returns:
        생성된 캐시 키 문자열
        
    Example:
        >>> cache_key("analysis", user_id=1, session_id=5)
        'sleepfm:analysis:user_id=1:session_id=5'
    """
    parts = [prefix]
    
    # 위치 인자 추가
    for arg in args:
        parts.append(str(arg))
    
    # 키워드 인자 추가 (정렬하여 일관성 유지)
    for key in sorted(kwargs.keys()):
        value = kwargs[key]
        parts.append(f"{key}={value}")
    
    return ":".join(parts)


def hash_key(data: Any) -> str:
    """데이터를 해시하여 캐시 키 일부로 사용
    
    복잡한 데이터 구조를 짧은 해시로 변환
    """
    if isinstance(data, str):
        serialized = data
    else:
        serialized = json.dumps(data, sort_keys=True, default=str)
    
    return hashlib.md5(serialized.encode()).hexdigest()[:16]


async def get_cached(key: str) -> Optional[Any]:
    """캐시에서 값 조회"""
    client = get_redis_client()
    if client and client.is_connected:
        return await client.get_json(key)
    return None


async def set_cached(
    key: str,
    value: Any,
    ttl: Optional[Union[int, timedelta]] = None
) -> bool:
    """캐시에 값 저장"""
    client = get_redis_client()
    if client and client.is_connected:
        ttl = ttl or CacheConfig.ttl
        return await client.set_json(key, value, ttl)
    return False


async def delete_cached(key: str) -> bool:
    """캐시에서 값 삭제"""
    client = get_redis_client()
    if client and client.is_connected:
        return await client.delete(key)
    return False


async def invalidate_cache(pattern: str) -> int:
    """패턴에 맞는 캐시 일괄 무효화
    
    Args:
        pattern: Redis 패턴 (예: 'sleepfm:analysis:user_id=1:*')
        
    Returns:
        삭제된 키 개수
    """
    client = get_redis_client()
    if client and client.is_connected:
        count = await client.delete_pattern(pattern)
        logger.info(f"캐시 무효화: pattern={pattern}, count={count}")
        return count
    return 0


def cached(
    ttl: Optional[Union[int, timedelta]] = None,
    prefix: str = "sleepfm",
    key_builder: Optional[Callable] = None,
    skip_cache_on_error: bool = True,
):
    """비동기 함수 캐싱 데코레이터
    
    Args:
        ttl: 캐시 유효 시간 (초 또는 timedelta)
        prefix: 캐시 키 프리픽스
        key_builder: 커스텀 키 생성 함수. None이면 기본 키 생성 사용
        skip_cache_on_error: 에러 시 캐시 건너뛰기
        
    Example:
        @cached(ttl=300, prefix="analysis")
        async def get_analysis(session_id: int):
            return await compute_analysis(session_id)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            client = get_redis_client()
            
            # Redis가 없으면 원본 함수 실행
            if not client or not client.is_connected:
                return await func(*args, **kwargs)
            
            # 캐시 키 생성
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                # 기본 키: prefix:function_name:args_hash
                func_name = func.__name__
                args_hash = hash_key({"args": args, "kwargs": kwargs})
                key = f"{prefix}:{func_name}:{args_hash}"
            
            try:
                # 캐시 히트 확인
                cached_value = await client.get_json(key)
                if cached_value is not None:
                    logger.debug(f"캐시 히트: {key}")
                    return cached_value
                
                logger.debug(f"캐시 미스: {key}")
                
            except Exception as e:
                logger.warning(f"캐시 조회 오류: {e}")
                if not skip_cache_on_error:
                    raise
            
            # 원본 함수 실행
            result = await func(*args, **kwargs)
            
            # 결과 캐싱
            try:
                cache_ttl = ttl or CacheConfig.ttl
                await client.set_json(key, result, cache_ttl)
                logger.debug(f"캐시 저장: {key}, ttl={cache_ttl}")
            except Exception as e:
                logger.warning(f"캐시 저장 오류: {e}")
                if not skip_cache_on_error:
                    raise
            
            return result
        
        return wrapper
    return decorator


# 분석 결과 캐싱용 특화 데코레이터
def cached_analysis(session_id_arg: str = "session_id"):
    """분석 결과 캐싱 데코레이터
    
    Args:
        session_id_arg: session_id가 있는 인자명
        
    Example:
        @cached_analysis()
        async def analyze_sleep_stages(session_id: int):
            ...
    """
    def key_builder(*args, **kwargs):
        # 함수 이름과 session_id로 키 생성
        session_id = kwargs.get(session_id_arg)
        if session_id is None and args:
            session_id = args[0]  # 첫 번째 위치 인자로 가정
        return f"sleepfm:analysis:{session_id}"
    
    return cached(
        ttl=CacheConfig.ANALYSIS_TTL,
        prefix="sleepfm",
        key_builder=key_builder,
    )


# 사용자 세션 캐싱용 특화 데코레이터
def cached_user_data(user_id_arg: str = "user_id"):
    """사용자 데이터 캐싱 데코레이터"""
    def key_builder(*args, **kwargs):
        user_id = kwargs.get(user_id_arg)
        if user_id is None and args:
            user_id = args[0]
        return f"sleepfm:user:{user_id}"
    
    return cached(
        ttl=CacheConfig.USER_TTL,
        prefix="sleepfm",
        key_builder=key_builder,
    )


async def clear_analysis_cache(session_id: int) -> bool:
    """특정 세션의 분석 캐시 삭제"""
    key = f"sleepfm:analysis:{session_id}"
    return await delete_cached(key)


async def clear_user_cache(user_id: int) -> int:
    """특정 사용자의 모든 캐시 삭제"""
    pattern = f"sleepfm:*:user_id={user_id}:*"
    return await invalidate_cache(pattern)


async def get_cache_stats() -> dict:
    """캐시 통계 조회"""
    client = get_redis_client()
    if client:
        return await client.get_stats()
    return {"connected": False, "message": "Redis not initialized"}
