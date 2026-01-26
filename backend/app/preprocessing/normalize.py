"""
정규화 모듈

신호 정규화 및 표준화
"""

import numpy as np
from typing import Tuple, Optional


def normalize_signal(
    signal_data: np.ndarray,
    method: str = "minmax",
    epsilon: float = 1e-8,
) -> np.ndarray:
    """
    신호 정규화
    
    Args:
        signal_data: 입력 신호
        method: 정규화 방법
               - "minmax": [0, 1] 범위로 정규화
               - "robust": 중앙값과 사분위수범위 사용 (이상치 견디기)
        epsilon: 제로 나누기 방지
    
    Returns:
        정규화된 신호
    
    Examples:
        >>> signal = np.array([1, 2, 3, 4, 5])
        >>> normalized = normalize_signal(signal, "minmax")
        >>> normalized
        array([0.  , 0.25, 0.5 , 0.75, 1.  ])
    """
    if signal_data.size == 0:
        raise ValueError("Signal cannot be empty")
    
    if method == "minmax":
        # Min-Max 정규화: (x - min) / (max - min)
        min_val = np.min(signal_data, axis=0)
        max_val = np.max(signal_data, axis=0)
        denom = max_val - min_val
        denom = np.where(denom == 0, epsilon, denom)
        normalized = (signal_data - min_val) / denom
    
    elif method == "robust":
        # Robust 정규화: (x - median) / IQR
        median = np.median(signal_data, axis=0)
        q75 = np.percentile(signal_data, 75, axis=0)
        q25 = np.percentile(signal_data, 25, axis=0)
        iqr = q75 - q25
        iqr = np.where(iqr == 0, epsilon, iqr)
        normalized = (signal_data - median) / iqr
    
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    return normalized


def standardize_signal(
    signal_data: np.ndarray,
    mean: Optional[np.ndarray] = None,
    std: Optional[np.ndarray] = None,
    epsilon: float = 1e-8,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    신호 표준화 (Z-score 정규화)
    
    (x - mean) / std → N(0, 1)
    
    Args:
        signal_data: 입력 신호
        mean: 미리 계산된 평균 (None이면 입력에서 계산)
        std: 미리 계산된 표준편차 (None이면 입력에서 계산)
        epsilon: 제로 나누기 방지
    
    Returns:
        (standardized_signal, mean, std)
        - standardized_signal: 표준화된 신호
        - mean: 사용된 평균값
        - std: 사용된 표준편차
    
    Examples:
        >>> signal = np.array([1, 2, 3, 4, 5], dtype=float)
        >>> standardized, mean, std = standardize_signal(signal)
        >>> np.allclose(standardized.mean(), 0, atol=1e-10)
        True
        >>> np.allclose(standardized.std(), 1)
        True
    """
    if signal_data.size == 0:
        raise ValueError("Signal cannot be empty")
    
    # 평균 및 표준편차 계산
    if mean is None:
        mean = np.mean(signal_data, axis=0)
    if std is None:
        std = np.std(signal_data, axis=0)
    
    # 표준편차가 0인 경우 방지
    std = np.where(std == 0, epsilon, std)
    
    # 표준화
    standardized = (signal_data - mean) / std
    
    return standardized, mean, std


def channel_wise_normalize(
    signal_data: np.ndarray,
    method: str = "standardize",
) -> Tuple[np.ndarray, dict]:
    """
    채널별 정규화 (다중채널 신호용)
    
    Args:
        signal_data: 입력 신호 (channels 마지막 차원)
                    - 1D: (samples,) → 단일 채널로 처리
                    - 2D: (samples, channels)
                    - 3D: (batch, samples, channels)
        method: 정규화 방법 ("normalize" 또는 "standardize")
    
    Returns:
        (normalized_signal, normalization_params)
        - normalized_signal: 정규화된 신호
        - normalization_params: 채널별 정규화 파라미터
    
    Examples:
        >>> signal = np.random.randn(100, 3)  # 100 samples, 3 channels
        >>> normalized, params = channel_wise_normalize(signal)
        >>> normalized.shape
        (100, 3)
    """
    if signal_data.size == 0:
        raise ValueError("Signal cannot be empty")
    
    # 신호 shape 확인
    if signal_data.ndim == 1:
        # 단일 채널
        if method == "standardize":
            normalized, mean, std = standardize_signal(signal_data)
            params = {"mean": mean, "std": std}
        elif method == "normalize":
            normalized = normalize_signal(signal_data)
            params = {}
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return normalized, params
    
    elif signal_data.ndim == 2:
        # (samples, channels)
        num_channels = signal_data.shape[1]
        normalized = np.zeros_like(signal_data)
        params = {}
        
        for ch in range(num_channels):
            if method == "standardize":
                norm_ch, mean, std = standardize_signal(signal_data[:, ch])
                normalized[:, ch] = norm_ch
                params[f"ch{ch}"] = {"mean": mean, "std": std}
            elif method == "normalize":
                normalized[:, ch] = normalize_signal(signal_data[:, ch])
            else:
                raise ValueError(f"Unknown method: {method}")
        
        return normalized, params
    
    else:
        raise ValueError("Signal must be 1D or 2D")


def inverse_standardize(
    standardized_signal: np.ndarray,
    mean: np.ndarray,
    std: np.ndarray,
) -> np.ndarray:
    """
    표준화된 신호를 원본 스케일로 복원
    
    Args:
        standardized_signal: 표준화된 신호
        mean: 표준화에 사용된 평균
        std: 표준화에 사용된 표준편차
    
    Returns:
        원본 스케일의 신호
    """
    return standardized_signal * std + mean
