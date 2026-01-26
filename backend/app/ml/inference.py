"""
추론 엔진

엔드-투-엔드 전처리 → 임베딩 추출 파이프라인
"""

import torch
import numpy as np
import logging
from typing import Dict, Union, Optional

from app.preprocessing import PreprocessingPipeline, create_default_pipeline
from app.ml.embedding_extractor import EmbeddingExtractor

logger = logging.getLogger(__name__)


class InferenceEngine:
    """
    엔드-투-엔드 추론 엔진
    
    센서 데이터 → 전처리 → 임베딩 추출
    """
    
    def __init__(
        self,
        model: torch.nn.Module,
        preprocessing_pipeline: Optional[PreprocessingPipeline] = None,
        embedding_extractor: Optional[EmbeddingExtractor] = None,
        device: str = "cpu",
    ):
        """
        추론 엔진 초기화
        
        Args:
            model: SleepFM 인코더
            preprocessing_pipeline: 전처리 파이프라인 (None이면 기본값 사용)
            embedding_extractor: 임베딩 추출기 (None이면 자동 생성)
            device: 실행 디바이스
        """
        self.model = model
        self.device = device
        
        # 전처리 파이프라인
        if preprocessing_pipeline is None:
            self.preprocessing = create_default_pipeline(device=device)
        else:
            self.preprocessing = preprocessing_pipeline
        
        # 임베딩 추출기
        if embedding_extractor is None:
            self.extractor = EmbeddingExtractor(
                model=model,
                device=device,
                max_batch_size=32 if device == "cpu" else 64,
            )
        else:
            self.extractor = embedding_extractor
        
        logger.info(
            f"InferenceEngine initialized: device={device}"
        )
    
    def process_sensor_data(
        self,
        sensor_data: Dict[str, np.ndarray],
        original_fs: float,
        return_tokens: bool = False,
    ) -> Dict:
        """
        센서 데이터 처리 (전처리 → 임베딩)
        
        Args:
            sensor_data: 센서 데이터 딕셔너리
                        {"ecg": ndarray, "ppg": ndarray, "accel": ndarray}
            original_fs: 원본 샘플링 레이트
            return_tokens: 토큰 반환 여부
        
        Returns:
            {
                "embeddings": (num_tokens, 512) ndarray,
                "tokens": 토큰 (return_tokens=True일 때),
                "metadata": 처리 메타데이터,
                "normalization_params": 정규화 파라미터,
            }
        """
        logger.info(f"Processing sensor data: {list(sensor_data.keys())}")
        
        # 1. 전처리
        preprocessing_result = self.preprocessing.process(sensor_data, original_fs)
        tokens_tensor = preprocessing_result["tensor"]
        
        logger.info(f"Preprocessing complete: {tokens_tensor.shape}")
        
        # 2. 임베딩 추출
        embeddings = self.extractor.extract(tokens_tensor, return_numpy=True)
        
        logger.info(f"Embeddings extracted: {embeddings.shape}")
        
        # 결과 구성
        result = {
            "embeddings": embeddings,
            "metadata": {
                **preprocessing_result["metadata"],
                "embedding_dim": embeddings.shape[1],
            },
            "normalization_params": preprocessing_result["normalization_params"],
        }
        
        if return_tokens:
            result["tokens"] = preprocessing_result["tokens"]
        
        return result
    
    def infer_batch(
        self,
        preprocessed_tokens: torch.Tensor,
    ) -> np.ndarray:
        """
        이미 전처리된 토큰으로부터 임베딩 추출
        
        Args:
            preprocessed_tokens: 전처리된 토큰
                                shape: (batch, channels, time) or (batch, num_tokens, channels, time)
        
        Returns:
            (batch, 512) 임베딩
        """
        return self.extractor.extract(preprocessed_tokens, return_numpy=True)


def create_default_inference_engine(
    model: torch.nn.Module,
    device: str = "cpu",
) -> InferenceEngine:
    """
    기본 설정의 추론 엔진 생성
    
    Args:
        model: SleepFM 모델
        device: 실행 디바이스
    
    Returns:
        InferenceEngine 인스턴스
    """
    return InferenceEngine(
        model=model,
        preprocessing_pipeline=None,  # 기본값 사용
        embedding_extractor=None,     # 자동 생성
        device=device,
    )
