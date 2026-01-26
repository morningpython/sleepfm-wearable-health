"""
ML 모델 관리 유틸리티
"""

import logging
from functools import lru_cache
from typing import Optional, Tuple

import torch

from .sleepfm_encoder import (
    SleepFMEncoder,
    load_sleepfm_model,
    validate_model_io,
)

logger = logging.getLogger(__name__)


class ModelManager:
    """
    ML 모델 싱글톤 관리자
    
    모델 인스턴스를 메모리에 캐시하여 반복적인 로딩 방지
    """
    
    _instance = None
    _model: Optional[SleepFMEncoder] = None
    _device: Optional[str] = None
    _is_initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(
        self,
        checkpoint_path: Optional[str] = None,
        device: Optional[str] = None,
        validate: bool = True,
    ) -> None:
        """
        모델 초기화
        
        Args:
            checkpoint_path: 모델 체크포인트 경로
            device: 실행 디바이스 ("cuda" 또는 "cpu")
            validate: 모델 IO 검증 여부
        
        Raises:
            RuntimeError: 초기화 실패 시
        """
        if self._is_initialized:
            logger.info("Model already initialized, skipping...")
            return
        
        try:
            logger.info("Initializing ML model...")
            self._model, self._device = load_sleepfm_model(
                checkpoint_path=checkpoint_path,
                device=device,
                download_if_missing=True,
            )
            
            if validate:
                validate_model_io(self._model, self._device)
            
            self._is_initialized = True
            logger.info("✓ Model initialization completed")
        
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise RuntimeError(f"Model initialization failed: {e}")
    
    @property
    def model(self) -> SleepFMEncoder:
        """로드된 모델 반환"""
        if not self._is_initialized:
            raise RuntimeError(
                "Model not initialized. Call initialize() first."
            )
        return self._model
    
    @property
    def device(self) -> str:
        """모델이 실행되는 디바이스 반환"""
        if not self._is_initialized:
            raise RuntimeError(
                "Model not initialized. Call initialize() first."
            )
        return self._device
    
    @property
    def is_initialized(self) -> bool:
        """모델 초기화 여부"""
        return self._is_initialized
    
    def get_device_info(self) -> dict:
        """현재 디바이스 정보 반환"""
        info = {
            "device": self._device,
            "cuda_available": torch.cuda.is_available(),
        }
        
        if torch.cuda.is_available():
            info["cuda_version"] = torch.version.cuda
            info["device_name"] = torch.cuda.get_device_name(0)
            info["device_count"] = torch.cuda.device_count()
            info["gpu_memory_gb"] = (
                torch.cuda.get_device_properties(0).total_memory / 1e9
            )
        
        return info


@lru_cache(maxsize=1)
def get_model_manager() -> ModelManager:
    """
    모델 관리자 싱글톤 인스턴스 반환
    
    LRU 캐시로 동일한 인스턴스 보장
    """
    return ModelManager()
