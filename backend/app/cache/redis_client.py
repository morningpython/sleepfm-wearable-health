"""
Redis 클라이언트 모듈

비동기 Redis 클라이언트 및 연결 관리
"""

import json
import logging
from typing import Optional, Any, Union
from datetime import timedelta
import asyncio

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from app.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """비동기 Redis 클라이언트 래퍼"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
        max_connections: int = 10,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses
        self.max_connections = max_connections
        self._client: Optional[redis.Redis] = None
        self._pool: Optional[redis.ConnectionPool] = None
        self._connected = False
        
    async def connect(self) -> bool:
        """Redis에 연결"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis 패키지가 설치되지 않았습니다. 캐싱이 비활성화됩니다.")
            return False
            
        try:
            self._pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                max_connections=self.max_connections,
            )
            self._client = redis.Redis(connection_pool=self._pool)
            
            # 연결 테스트
            await self._client.ping()
            self._connected = True
            logger.info(f"Redis 연결 성공: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.warning(f"Redis 연결 실패: {e}. 캐싱이 비활성화됩니다.")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Redis 연결 해제"""
        if self._client:
            await self._client.close()
            self._connected = False
            logger.info("Redis 연결 해제")
    
    @property
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._connected and self._client is not None
    
    async def get(self, key: str) -> Optional[str]:
        """키로 값 조회"""
        if not self.is_connected:
            return None
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.error(f"Redis GET 오류: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """키-값 저장"""
        if not self.is_connected:
            return False
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            if ttl:
                await self._client.setex(key, ttl, value)
            else:
                await self._client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET 오류: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """키 삭제"""
        if not self.is_connected:
            return False
        try:
            await self._client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE 오류: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """패턴에 맞는 키 일괄 삭제"""
        if not self.is_connected:
            return 0
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self._client.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.error(f"Redis DELETE PATTERN 오류: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """키 존재 여부 확인"""
        if not self.is_connected:
            return False
        try:
            return await self._client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS 오류: {e}")
            return False
    
    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """키 만료 시간 설정"""
        if not self.is_connected:
            return False
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            await self._client.expire(key, ttl)
            return True
        except Exception as e:
            logger.error(f"Redis EXPIRE 오류: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """키 남은 TTL 조회 (-1: 만료 없음, -2: 키 없음)"""
        if not self.is_connected:
            return -2
        try:
            return await self._client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL 오류: {e}")
            return -2
    
    async def incr(self, key: str) -> Optional[int]:
        """값 증가"""
        if not self.is_connected:
            return None
        try:
            return await self._client.incr(key)
        except Exception as e:
            logger.error(f"Redis INCR 오류: {e}")
            return None
    
    async def get_json(self, key: str) -> Optional[Any]:
        """JSON 값 조회"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error(f"JSON 파싱 오류: key={key}")
                return None
        return None
    
    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """JSON 값 저장"""
        try:
            json_str = json.dumps(value, default=str)
            return await self.set(key, json_str, ttl)
        except Exception as e:
            logger.error(f"JSON 직렬화 오류: {e}")
            return False
    
    async def get_stats(self) -> dict:
        """Redis 서버 통계 조회"""
        if not self.is_connected:
            return {"connected": False}
        try:
            info = await self._client.info()
            return {
                "connected": True,
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
                    * 100
                ),
            }
        except Exception as e:
            logger.error(f"Redis INFO 오류: {e}")
            return {"connected": True, "error": str(e)}


# 전역 Redis 클라이언트 인스턴스
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> Optional[RedisClient]:
    """전역 Redis 클라이언트 반환"""
    return _redis_client


async def init_redis(
    host: Optional[str] = None,
    port: Optional[int] = None,
    password: Optional[str] = None,
) -> RedisClient:
    """Redis 클라이언트 초기화"""
    global _redis_client
    
    _redis_client = RedisClient(
        host=host or getattr(settings, 'REDIS_HOST', 'localhost'),
        port=port or getattr(settings, 'REDIS_PORT', 6379),
        password=password or getattr(settings, 'REDIS_PASSWORD', None),
    )
    await _redis_client.connect()
    return _redis_client


async def close_redis():
    """Redis 클라이언트 종료"""
    global _redis_client
    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None
