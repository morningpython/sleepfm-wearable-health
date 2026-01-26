"""
임베딩 추출 모듈

SleepFM 모델을 사용하여 전처리된 신호에서 임베딩 벡터 추출
"""

import logging
import numpy as np
import torch
from typing import Union, Tuple, Dict, Optional

logger = logging.getLogger(__name__)


class EmbeddingExtractor:
    """
    SleepFM 임베딩 추출기
    
    전처리된 토큰 → 512차원 임베딩 벡터
    
    특징:
    - 동적 배치 크기 조정 (OOM 방지)
    - 메모리 효율적 추론
    - 배치 처리 지원
    """
    
    def __init__(
        self,
        model: torch.nn.Module,
        device: str = "cpu",
        max_batch_size: int = 32,
        enable_mixed_precision: bool = False,
        enable_gradient_checkpointing: bool = False,
    ):
        """
        임베딩 추출기 초기화
        
        Args:
            model: 사전 학습된 SleepFM 모델
            device: 실행 디바이스 ("cpu" 또는 "cuda")
            max_batch_size: 최대 배치 크기 (기본값: 32)
            enable_mixed_precision: 혼합 정밀도 사용 여부
            enable_gradient_checkpointing: 그래디언트 체크포인팅 여부
        """
        self.model = model
        self.device = device
        self.max_batch_size = max_batch_size
        self.enable_mixed_precision = enable_mixed_precision
        self.enable_gradient_checkpointing = enable_gradient_checkpointing
        
        # 모델을 평가 모드로 설정
        self.model.eval()
        
        # 혼합 정밀도 설정
        if enable_mixed_precision and device == "cuda":
            self.scaler = torch.cuda.amp.GradScaler()
            logger.info("Mixed precision enabled")
        else:
            self.scaler = None
        
        logger.info(
            f"EmbeddingExtractor initialized: "
            f"device={device}, max_batch_size={max_batch_size}"
        )
    
    def extract(
        self,
        tensor_data: torch.Tensor,
        batch_size: Optional[int] = None,
        return_numpy: bool = True,
    ) -> Union[torch.Tensor, np.ndarray]:
        """
        임베딩 추출
        
        Args:
            tensor_data: 입력 텐서 (batch, channels, time_steps)
            batch_size: 배치 크기 (None이면 자동 결정)
            return_numpy: NumPy 배열로 반환 여부
        
        Returns:
            임베딩 벡터 (batch, embedding_dim)
            - torch.Tensor 또는 np.ndarray 형식
        
        Examples:
            >>> extractor = EmbeddingExtractor(model, device="cuda")
            >>> tokens = torch.randn(100, 3, 640).cuda()
            >>> embeddings = extractor.extract(tokens)
            >>> embeddings.shape
            (100, 512)
        """
        # 입력 검증
        if tensor_data.size(0) == 0:
            raise ValueError("Input tensor cannot be empty")
        
        # 배치 크기 결정
        if batch_size is None:
            batch_size = self._determine_batch_size(tensor_data)
        
        logger.info(
            f"Extracting embeddings: "
            f"input_shape={tuple(tensor_data.shape)}, "
            f"batch_size={batch_size}"
        )
        
        # 배치 처리
        embeddings = self._process_batches(tensor_data, batch_size)
        
        # 반환 형식
        if return_numpy:
            embeddings = embeddings.cpu().numpy()
            logger.info(f"Output shape: {embeddings.shape}")
            return embeddings
        else:
            logger.info(f"Output shape: {embeddings.shape}")
            return embeddings
    
    def _determine_batch_size(self, tensor_data: torch.Tensor) -> int:
        """
        사용 가능한 메모리에 따라 배치 크기 자동 결정
        
        Args:
            tensor_data: 입력 텐서
        
        Returns:
            추천 배치 크기
        """
        if self.device == "cpu":
            return self.max_batch_size
        
        try:
            # GPU 메모리 정보
            if torch.cuda.is_available():
                torch.cuda.reset_peak_memory_stats()
                free_memory = torch.cuda.mem_get_info()[0] / 1024**3  # GB
                
                # 보수적 추정: 사용 가능 메모리의 50% 사용
                available_gb = free_memory * 0.5
                
                # 샘플당 약 0.001GB (대략)
                estimated_batch_size = max(1, int(available_gb / 0.001))
                batch_size = min(self.max_batch_size, estimated_batch_size)
                
                logger.info(
                    f"GPU memory: {free_memory:.2f}GB free, "
                    f"determined batch_size={batch_size}"
                )
                return batch_size
        except Exception as e:
            logger.warning(f"Failed to determine batch size: {e}")
        
        return self.max_batch_size
    
    def _process_batches(
        self,
        tensor_data: torch.Tensor,
        batch_size: int,
    ) -> torch.Tensor:
        """
        배치 단위로 임베딩 추출
        
        Args:
            tensor_data: 전체 입력 텐서
            batch_size: 배치 크기
        
        Returns:
            전체 임베딩 (num_samples, embedding_dim)
        """
        num_samples = tensor_data.size(0)
        num_batches = (num_samples + batch_size - 1) // batch_size
        
        all_embeddings = []
        
        with torch.no_grad():
            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, num_samples)
                
                batch_data = tensor_data[start_idx:end_idx].to(self.device)
                
                # 혼합 정밀도로 추론
                if self.enable_mixed_precision and self.device == "cuda":
                    with torch.cuda.amp.autocast():
                        batch_embeddings = self.model(batch_data)
                else:
                    batch_embeddings = self.model(batch_data)
                
                all_embeddings.append(batch_embeddings.cpu())
                
                # 진행 상황 로깅
                logger.debug(
                    f"Batch {batch_idx + 1}/{num_batches}: "
                    f"processed {end_idx}/{num_samples} samples"
                )
        
        # 전체 임베딩 결합
        embeddings = torch.cat(all_embeddings, dim=0)
        
        return embeddings
    
    def extract_batch_info(
        self,
        tensor_data: torch.Tensor,
    ) -> Dict:
        """
        배치 처리 정보 반환
        
        Args:
            tensor_data: 입력 텐서
        
        Returns:
            배치 정보 딕셔너리
        """
        batch_size = self._determine_batch_size(tensor_data)
        num_samples = tensor_data.size(0)
        num_batches = (num_samples + batch_size - 1) // batch_size
        
        return {
            "num_samples": num_samples,
            "batch_size": batch_size,
            "num_batches": num_batches,
            "device": self.device,
            "mixed_precision": self.enable_mixed_precision,
        }


def extract_embeddings(
    model: torch.nn.Module,
    tensor_data: torch.Tensor,
    device: str = "cpu",
    batch_size: Optional[int] = None,
    return_numpy: bool = True,
) -> Union[torch.Tensor, np.ndarray]:
    """
    편의 함수: 임베딩 추출
    
    Args:
        model: SleepFM 모델
        tensor_data: 입력 텐서 (batch, channels, time_steps)
        device: 실행 디바이스
        batch_size: 배치 크기 (None이면 자동)
        return_numpy: NumPy 반환 여부
    
    Returns:
        임베딩 벡터 (batch, 512)
    
    Examples:
        >>> model, device = load_sleepfm_model()
        >>> tensor = torch.randn(100, 3, 640).to(device)
        >>> embeddings = extract_embeddings(model, tensor, device)
        >>> embeddings.shape
        (100, 512)
    """
    extractor = EmbeddingExtractor(
        model=model,
        device=device,
        max_batch_size=batch_size or 32,
    )
    
    return extractor.extract(
        tensor_data,
        batch_size=batch_size,
        return_numpy=return_numpy,
    )


def validate_embeddings(
    embeddings: Union[torch.Tensor, np.ndarray],
    expected_shape: Tuple = (None, 512),
) -> bool:
    """
    임베딩 품질 검증
    
    Args:
        embeddings: 임베딩 벡터
        expected_shape: 예상 shape (None = 동적)
    
    Returns:
        검증 성공 여부
    
    Raises:
        AssertionError: 검증 실패
    """
    if isinstance(embeddings, torch.Tensor):
        embeddings = embeddings.cpu().numpy()
    
    # Shape 확인
    assert embeddings.ndim == 2, f"Expected 2D array, got {embeddings.ndim}D"
    assert embeddings.shape[1] == expected_shape[1], (
        f"Expected embedding_dim={expected_shape[1]}, "
        f"got {embeddings.shape[1]}"
    )
    
    # NaN/Inf 확인
    assert not np.any(np.isnan(embeddings)), "Embeddings contain NaN"
    assert not np.any(np.isinf(embeddings)), "Embeddings contain Inf"
    
    # 범위 확인 (임베딩은 보통 [-10, 10] 범위)
    assert np.max(np.abs(embeddings)) < 1e6, (
        f"Embeddings have suspiciously large values: max={np.max(np.abs(embeddings))}"
    )
    
    return True


def compute_embedding_statistics(
    embeddings: Union[torch.Tensor, np.ndarray],
) -> Dict:
    """
    임베딩 통계 계산
    
    Args:
        embeddings: 임베딩 벡터 (batch, embedding_dim)
    
    Returns:
        통계 딕셔너리
    """
    if isinstance(embeddings, torch.Tensor):
        embeddings = embeddings.cpu().numpy()
    
    return {
        "shape": embeddings.shape,
        "dtype": str(embeddings.dtype),
        "mean": float(np.mean(embeddings)),
        "std": float(np.std(embeddings)),
        "min": float(np.min(embeddings)),
        "max": float(np.max(embeddings)),
        "norm_mean": float(np.mean(np.linalg.norm(embeddings, axis=1))),
        "norm_std": float(np.std(np.linalg.norm(embeddings, axis=1))),
    }
