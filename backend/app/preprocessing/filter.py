"""
필터링 모듈

Butterworth 필터로 노이즈 제거
"""

import numpy as np
from scipy import signal as scipy_signal
from typing import Tuple, Union, Optional


class ButterworthFilter:
    """
    Butterworth 대역 통과 필터
    
    신호의 특정 주파수 대역만 통과시키고 나머지는 감쇠
    """
    
    def __init__(
        self,
        low_freq: float,
        high_freq: float,
        sampling_rate: float,
        order: int = 4,
    ):
        """
        필터 초기화
        
        Args:
            low_freq: 통과 대역 하한 (Hz)
            high_freq: 통과 대역 상한 (Hz)
            sampling_rate: 샘플링 레이트 (Hz)
            order: 필터 차수 (기본값: 4)
        
        Raises:
            ValueError: 잘못된 주파수 범위
        """
        if low_freq <= 0 or high_freq <= 0:
            raise ValueError("Frequencies must be positive")
        
        if low_freq >= high_freq:
            raise ValueError("low_freq must be less than high_freq")
        
        nyquist = sampling_rate / 2
        if high_freq >= nyquist:
            raise ValueError(
                f"high_freq ({high_freq} Hz) must be less than "
                f"Nyquist frequency ({nyquist} Hz)"
            )
        
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.sampling_rate = sampling_rate
        self.order = order
        
        # 필터 계수 설계
        normalized_low = low_freq / nyquist
        normalized_high = high_freq / nyquist
        
        self.sos = scipy_signal.butter(
            order,
            [normalized_low, normalized_high],
            btype="band",
            output="sos",
        )
        
        # 임펄스 응답 저장 (분석용)
        self._w = None
        self._h = None
    
    def apply(self, signal_data: np.ndarray) -> np.ndarray:
        """
        필터 적용
        
        Args:
            signal_data: 입력 신호 (1D 또는 2D)
        
        Returns:
            필터링된 신호
        """
        # sosfilt 사용 (수치 안정성 향상)
        if signal_data.ndim == 1:
            filtered = scipy_signal.sosfilt(self.sos, signal_data)
        elif signal_data.ndim == 2:
            # 각 채널별로 필터 적용
            filtered = np.zeros_like(signal_data)
            for ch in range(signal_data.shape[1]):
                filtered[:, ch] = scipy_signal.sosfilt(
                    self.sos,
                    signal_data[:, ch],
                )
        else:
            raise ValueError("Signal must be 1D or 2D")
        
        return filtered
    
    def get_frequency_response(
        self,
        num_points: int = 1000,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        필터의 주파수 응답 반환
        
        Args:
            num_points: 주파수 포인트 개수
        
        Returns:
            (frequency, magnitude) - 주파수(Hz)와 크기(dB)
        """
        w, h = scipy_signal.sosfreqz(self.sos, worN=num_points)
        
        # 정규화된 주파수를 Hz로 변환
        frequency = w * self.sampling_rate / np.pi
        magnitude_db = 20 * np.log10(np.abs(h) + 1e-10)
        
        return frequency, magnitude_db


def apply_butterworth_filter(
    signal_data: np.ndarray,
    sampling_rate: float,
    low_freq: float = 0.5,
    high_freq: float = 50.0,
    order: int = 4,
) -> np.ndarray:
    """
    Butterworth 필터 적용 (편의 함수)
    
    기본값: 0.5-50 Hz (ECG/PPG에 적합)
    
    Args:
        signal_data: 입력 신호
        sampling_rate: 샘플링 레이트 (Hz)
        low_freq: 통과 대역 하한 (기본값: 0.5 Hz)
        high_freq: 통과 대역 상한 (기본값: 50 Hz)
        order: 필터 차수 (기본값: 4)
    
    Returns:
        필터링된 신호
    
    Examples:
        >>> signal = np.random.randn(1000)
        >>> filtered = apply_butterworth_filter(signal, 128, 0.5, 50)
        >>> filtered.shape
        (1000,)
    """
    butter_filter = ButterworthFilter(
        low_freq=low_freq,
        high_freq=high_freq,
        sampling_rate=sampling_rate,
        order=order,
    )
    
    return butter_filter.apply(signal_data)


def validate_filtered_signal(
    original_signal: np.ndarray,
    filtered_signal: np.ndarray,
) -> dict:
    """
    필터링된 신호의 품질 지표 계산
    
    Args:
        original_signal: 원본 신호
        filtered_signal: 필터링된 신호
    
    Returns:
        품질 지표 딕셔너리
        - snr_reduction: SNR 감소율 (%)
        - energy_retention: 에너지 보존율 (%)
        - rms_change: RMS 변화 (%)
    """
    # 에너지 계산
    original_energy = np.sum(original_signal ** 2)
    filtered_energy = np.sum(filtered_signal ** 2)
    energy_retention = (filtered_energy / original_energy) * 100 if original_energy > 0 else 0
    
    # RMS 변화
    original_rms = np.sqrt(np.mean(original_signal ** 2))
    filtered_rms = np.sqrt(np.mean(filtered_signal ** 2))
    rms_change = ((filtered_rms - original_rms) / original_rms) * 100 if original_rms > 0 else 0
    
    # 피크 대 피크 (P2P) 감소
    original_p2p = np.max(original_signal) - np.min(original_signal)
    filtered_p2p = np.max(filtered_signal) - np.min(filtered_signal)
    p2p_reduction = ((original_p2p - filtered_p2p) / original_p2p) * 100 if original_p2p > 0 else 0
    
    return {
        "energy_retention": energy_retention,
        "rms_change": rms_change,
        "p2p_reduction": p2p_reduction,
    }
