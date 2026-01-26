"""
토큰화 모듈

신호를 5초 윈도우로 분할 (640 샘플 @ 128Hz)
"""

import numpy as np
from typing import List, Tuple, Union


def create_windows(
    signal_data: np.ndarray,
    window_size: int,
    overlap: int = 0,
) -> List[np.ndarray]:
    """
    슬라이딩 윈도우를 사용해 신호를 분할
    
    Args:
        signal_data: 입력 신호 (1D 또는 2D)
        window_size: 윈도우 크기 (샘플 수)
        overlap: 윈도우 겹침 샘플 수 (기본값: 0 = 겹침 없음)
    
    Returns:
        윈도우 리스트
        - 1D input: List[ndarray] where each ndarray.shape = (window_size,)
        - 2D input: List[ndarray] where each ndarray.shape = (window_size, channels)
    
    Examples:
        >>> signal = np.arange(100)
        >>> windows = create_windows(signal, 20, overlap=0)
        >>> len(windows)
        5
        >>> windows[0].shape
        (20,)
    """
    if signal_data.size == 0:
        raise ValueError("Signal cannot be empty")
    
    if window_size <= 0:
        raise ValueError("Window size must be positive")
    
    if overlap < 0 or overlap >= window_size:
        raise ValueError("Overlap must be in [0, window_size)")
    
    num_samples = signal_data.shape[0]
    stride = window_size - overlap
    
    windows = []
    start = 0
    
    while start + window_size <= num_samples:
        if signal_data.ndim == 1:
            windows.append(signal_data[start:start + window_size])
        else:
            windows.append(signal_data[start:start + window_size, :])
        start += stride
    
    return windows


def tokenize_signal(
    signal_data: np.ndarray,
    sampling_rate: float = 128,
    window_duration_sec: float = 5.0,
    overlap_sec: float = 0.0,
) -> List[np.ndarray]:
    """
    신호를 시간 기반 윈도우로 토큰화
    
    기본: 5초 윈도우 (640 샘플 @ 128Hz)
    
    Args:
        signal_data: 입력 신호
        sampling_rate: 샘플링 레이트 (Hz, 기본값: 128)
        window_duration_sec: 윈도우 기간 (초, 기본값: 5)
        overlap_sec: 윈도우 겹침 기간 (초, 기본값: 0)
    
    Returns:
        토큰화된 윈도우 리스트
    
    Examples:
        >>> signal = np.random.randn(3840)  # 30초 @ 128Hz
        >>> tokens = tokenize_signal(signal, 128, 5, 0)
        >>> len(tokens)
        6
        >>> tokens[0].shape
        (640,)
    """
    window_size = int(window_duration_sec * sampling_rate)
    overlap_size = int(overlap_sec * sampling_rate)
    
    return create_windows(signal_data, window_size, overlap_size)


def get_window_indices(
    num_samples: int,
    window_size: int,
    overlap: int = 0,
) -> List[Tuple[int, int]]:
    """
    각 윈도우의 시작/종료 인덱스 반환
    
    Args:
        num_samples: 총 샘플 수
        window_size: 윈도우 크기
        overlap: 윈도우 겹침
    
    Returns:
        [(start, end), ...] 리스트
    """
    if window_size <= 0:
        raise ValueError("Window size must be positive")
    
    if overlap < 0 or overlap >= window_size:
        raise ValueError("Overlap must be in [0, window_size)")
    
    indices = []
    stride = window_size - overlap
    start = 0
    
    while start + window_size <= num_samples:
        indices.append((start, start + window_size))
        start += stride
    
    return indices


def get_window_times(
    indices: List[Tuple[int, int]],
    sampling_rate: float,
) -> List[Tuple[float, float]]:
    """
    윈도우 시간 범위 계산 (초)
    
    Args:
        indices: 샘플 인덱스 리스트
        sampling_rate: 샘플링 레이트 (Hz)
    
    Returns:
        [(start_time, end_time), ...] (초 단위)
    """
    times = []
    for start_idx, end_idx in indices:
        start_time = start_idx / sampling_rate
        end_time = end_idx / sampling_rate
        times.append((start_time, end_time))
    
    return times


def validate_tokens(
    tokens: List[np.ndarray],
    expected_size: int,
) -> dict:
    """
    토큰 품질 검증
    
    Args:
        tokens: 토큰 리스트
        expected_size: 예상 윈도우 크기
    
    Returns:
        검증 결과 딕셔너리
    """
    num_tokens = len(tokens)
    
    if num_tokens == 0:
        raise ValueError("No tokens generated")
    
    # 모든 토큰이 같은 크기인지 확인
    sizes = [t.shape[0] for t in tokens]
    all_same_size = len(set(sizes)) == 1
    
    # 마지막 토큰이 작을 수 있으므로 확인
    last_size_ok = sizes[-1] <= expected_size
    
    return {
        "num_tokens": num_tokens,
        "sizes": sizes,
        "all_full_size": all(s == expected_size for s in sizes[:-1]),
        "last_size_ok": last_size_ok,
        "expected_size": expected_size,
    }
