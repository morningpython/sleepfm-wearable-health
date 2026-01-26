"""
리샘플링 모듈

다양한 샘플링 레이트를 128Hz로 표준화
"""

import numpy as np
from scipy import signal as scipy_signal
from typing import Tuple, Union


def get_resample_ratio(
    original_fs: Union[int, float],
    target_fs: Union[int, float] = 128,
) -> float:
    """
    리샘플링 비율 계산
    
    Args:
        original_fs: 원본 샘플링 레이트 (Hz)
        target_fs: 목표 샘플링 레이트 (Hz, 기본값: 128)
    
    Returns:
        리샘플링 비율
    
    Examples:
        >>> get_resample_ratio(256, 128)
        0.5
        >>> get_resample_ratio(64, 128)
        2.0
    """
    if original_fs <= 0 or target_fs <= 0:
        raise ValueError("Sampling rates must be positive")
    
    return target_fs / original_fs


def resample_signal(
    signal_data: np.ndarray,
    original_fs: Union[int, float],
    target_fs: Union[int, float] = 128,
    method: str = "scipy",
) -> np.ndarray:
    """
    신호를 목표 샘플링 레이트로 리샘플링
    
    Args:
        signal_data: 입력 신호 (1D 또는 2D 배열)
                    - 1D: (samples,)
                    - 2D: (samples, channels)
        original_fs: 원본 샘플링 레이트 (Hz)
        target_fs: 목표 샘플링 레이트 (Hz, 기본값: 128)
        method: 리샘플링 방법
               - "scipy": scipy.signal.resample (FFT 기반)
               - "scipy_poly": scipy.signal.resample_poly (다항식)
    
    Returns:
        리샘플링된 신호
        - 1D input → 1D output: (new_samples,)
        - 2D input → 2D output: (new_samples, channels)
    
    Raises:
        ValueError: 잘못된 입력 차원 또는 샘플링 레이트
    """
    # 입력 검증
    if signal_data.size == 0:
        raise ValueError("Signal cannot be empty")
    
    if original_fs <= 0 or target_fs <= 0:
        raise ValueError("Sampling rates must be positive")
    
    if signal_data.ndim not in (1, 2):
        raise ValueError("Signal must be 1D or 2D array")
    
    # 이미 같은 샘플링 레이트면 그대로 반환
    if np.isclose(original_fs, target_fs):
        return signal_data.copy()
    
    # 새로운 샘플 개수 계산
    num_samples = signal_data.shape[0]
    num_new_samples = int(np.round(num_samples * target_fs / original_fs))
    
    # 리샘플링 방법 선택
    if method == "scipy":
        # scipy.signal.resample 사용 (FFT 기반)
        if signal_data.ndim == 1:
            resampled = scipy_signal.resample(
                signal_data,
                num_new_samples,
                axis=0,
            )
        else:
            # 2D 배열: 각 채널별로 처리
            resampled = scipy_signal.resample(
                signal_data,
                num_new_samples,
                axis=0,
            )
    
    elif method == "scipy_poly":
        # scipy.signal.resample_poly 사용 (다항식)
        # 샘플링 레이트 비율을 정수 비율로 변환
        from fractions import Fraction
        ratio = Fraction(target_fs).limit_denominator(10000) / Fraction(original_fs).limit_denominator(10000)
        up = ratio.numerator
        down = ratio.denominator
        
        if signal_data.ndim == 1:
            resampled = scipy_signal.resample_poly(
                signal_data,
                up,
                down,
                axis=0,
            )
        else:
            # 2D 배열: 각 채널별로 처리
            channels = signal_data.shape[1]
            resampled = np.zeros((num_new_samples, channels))
            for ch in range(channels):
                resampled[:, ch] = scipy_signal.resample_poly(
                    signal_data[:, ch],
                    up,
                    down,
                    axis=0,
                )
    
    else:
        raise ValueError(f"Unknown resampling method: {method}")
    
    # 정확한 샘플 개수로 조정 (반올림 오류 보정)
    if resampled.shape[0] != num_new_samples:
        if resampled.shape[0] > num_new_samples:
            resampled = resampled[:num_new_samples]
        else:
            # 부족한 샘플 추가 (마지막 값 복제)
            padding = np.tile(
                resampled[-1:],
                (num_new_samples - resampled.shape[0], 1) 
                if resampled.ndim == 2 else 
                (num_new_samples - resampled.shape[0],)
            )
            resampled = np.vstack([resampled, padding]) if resampled.ndim == 2 else np.concatenate([resampled, padding])
    
    return resampled


def validate_resampled_signal(
    original_signal: np.ndarray,
    resampled_signal: np.ndarray,
    original_fs: float,
    target_fs: float,
    tolerance: float = 0.05,
) -> bool:
    """
    리샘플링된 신호의 품질 검증
    
    Args:
        original_signal: 원본 신호
        resampled_signal: 리샘플링된 신호
        original_fs: 원본 샘플링 레이트
        target_fs: 목표 샘플링 레이트
        tolerance: 허용 오차율 (기본값: 5%)
    
    Returns:
        검증 성공 여부
    
    Raises:
        AssertionError: 검증 실패
    """
    # 기간이 대략 같은지 확인
    original_duration = len(original_signal) / original_fs
    resampled_duration = len(resampled_signal) / target_fs
    
    error_rate = abs(original_duration - resampled_duration) / original_duration
    
    assert error_rate < tolerance, (
        f"Duration mismatch: {error_rate*100:.2f}% "
        f"(tolerance: {tolerance*100:.2f}%)"
    )
    
    # 샘플 개수 확인
    expected_samples = int(np.round(len(original_signal) * target_fs / original_fs))
    actual_samples = len(resampled_signal)
    
    # 최대 1개 샘플 차이 허용
    assert abs(expected_samples - actual_samples) <= 1, (
        f"Sample count mismatch: expected {expected_samples}, "
        f"got {actual_samples}"
    )
    
    return True
