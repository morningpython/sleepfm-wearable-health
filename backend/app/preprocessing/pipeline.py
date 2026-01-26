"""
통합 전처리 파이프라인

웨어러블 센서 데이터를 모델 입력 형식으로 변환
"""

import numpy as np
import torch
from typing import Dict, List, Tuple, Union, Optional
import logging

from .resample import resample_signal
from .filter import apply_butterworth_filter
from .tokenize import tokenize_signal
from .normalize import standardize_signal, channel_wise_normalize

logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """
    통합 전처리 파이프라인
    
    웨어러블 데이터 → 리샘플링 → 필터링 → 토큰화 → 정규화 → PyTorch 텐서
    
    기본 설정:
    - Target 샘플링 레이트: 128Hz
    - 필터링: 0.5-50Hz Butterworth (4차)
    - 토큰: 5초 윈도우 (640 샘플)
    - 정규화: Z-score (채널별)
    """
    
    def __init__(
        self,
        target_fs: float = 128.0,
        filter_low_freq: float = 0.5,
        filter_high_freq: float = 50.0,
        filter_order: int = 4,
        window_duration_sec: float = 5.0,
        standardize: bool = True,
        device: str = "cpu",
    ):
        """
        파이프라인 초기화
        
        Args:
            target_fs: 목표 샘플링 레이트 (Hz)
            filter_low_freq: 필터 하한 (Hz)
            filter_high_freq: 필터 상한 (Hz)
            filter_order: 필터 차수
            window_duration_sec: 토큰 윈도우 기간 (초)
            standardize: 표준화 여부
            device: PyTorch 디바이스
        """
        self.target_fs = target_fs
        self.filter_low_freq = filter_low_freq
        self.filter_high_freq = filter_high_freq
        self.filter_order = filter_order
        self.window_duration_sec = window_duration_sec
        self.standardize = standardize
        self.device = device
        
        # 토큰 크기 계산
        self.token_size = int(window_duration_sec * target_fs)
        
        logger.info(
            f"PreprocessingPipeline initialized: "
            f"target_fs={target_fs}Hz, "
            f"token_size={self.token_size}, "
            f"device={device}"
        )
    
    def process(
        self,
        sensor_data: Dict[str, np.ndarray],
        original_fs: float,
    ) -> Dict[str, Union[np.ndarray, List, torch.Tensor]]:
        """
        센서 데이터 전처리
        
        Args:
            sensor_data: 센서 데이터 딕셔너리
                        예: {"ecg": ndarray, "ppg": ndarray, "accel": ndarray}
            original_fs: 원본 샘플링 레이트
        
        Returns:
            처리 결과 딕셔너리
            - "tokens": 토큰화된 신호 (채널 마지막 축)
            - "tensor": PyTorch 텐서 (batch, channels, time)
            - "normalization_params": 정규화 파라미터
            - "metadata": 처리 메타데이터
        """
        logger.info(f"Processing sensor data: {list(sensor_data.keys())}")
        
        # 1. 채널 결합
        combined_signal = self._combine_channels(sensor_data)
        logger.info(f"Combined signal shape: {combined_signal.shape}")
        
        # 2. 리샘플링
        resampled = self._resample(combined_signal, original_fs)
        logger.info(f"Resampled signal shape: {resampled.shape}")
        
        # 3. 필터링
        filtered = self._filter(resampled)
        logger.info(f"Filtered signal shape: {filtered.shape}")
        
        # 4. 토큰화
        tokens = self._tokenize(filtered)
        logger.info(f"Generated {len(tokens)} tokens")
        
        # 5. 정규화
        tokens_normalized, norm_params = self._normalize(tokens)
        
        # 6. 텐서 변환
        tensor = self._to_tensor(tokens_normalized)
        logger.info(f"Output tensor shape: {tensor.shape}")
        
        return {
            "tokens": tokens_normalized,
            "tensor": tensor,
            "normalization_params": norm_params,
            "metadata": {
                "original_fs": original_fs,
                "target_fs": self.target_fs,
                "num_tokens": len(tokens),
                "token_size": self.token_size,
                "num_channels": combined_signal.shape[1] if combined_signal.ndim > 1 else 1,
            }
        }
    
    def _combine_channels(
        self,
        sensor_data: Dict[str, np.ndarray],
    ) -> np.ndarray:
        """
        여러 채널의 센서 데이터를 결합
        
        기본 순서: ECG, PPG, Accelerometer
        """
        channel_order = ["ecg", "ppg", "accel", "acc"]  # 별칭 포함
        channels = []
        
        for ch_name in channel_order:
            if ch_name in sensor_data:
                signal = sensor_data[ch_name]
                
                # 가속도계 데이터 (x, y, z)는 합치기
                if ch_name in ("accel", "acc"):
                    if signal.ndim == 2 and signal.shape[1] == 3:
                        # L2 norm 계산: sqrt(x^2 + y^2 + z^2)
                        signal = np.sqrt(np.sum(signal ** 2, axis=1))
                
                channels.append(signal)
        
        if not channels:
            raise ValueError("No recognized sensor channels in input")
        
        # 모든 채널이 같은 길이인지 확인
        lengths = [len(ch) for ch in channels]
        if len(set(lengths)) > 1:
            # 최소 길이로 맞추기
            min_len = min(lengths)
            channels = [ch[:min_len] for ch in channels]
            logger.warning(f"Channel length mismatch, truncated to {min_len}")
        
        # 스택: (samples, channels)
        return np.column_stack(channels)
    
    def _resample(
        self,
        signal_data: np.ndarray,
        original_fs: float,
    ) -> np.ndarray:
        """리샘플링 단계"""
        if np.isclose(original_fs, self.target_fs):
            return signal_data.copy()
        
        return resample_signal(
            signal_data,
            original_fs=original_fs,
            target_fs=self.target_fs,
            method="scipy",
        )
    
    def _filter(
        self,
        signal_data: np.ndarray,
    ) -> np.ndarray:
        """필터링 단계"""
        return apply_butterworth_filter(
            signal_data,
            sampling_rate=self.target_fs,
            low_freq=self.filter_low_freq,
            high_freq=self.filter_high_freq,
            order=self.filter_order,
        )
    
    def _tokenize(
        self,
        signal_data: np.ndarray,
    ) -> List[np.ndarray]:
        """토큰화 단계"""
        return tokenize_signal(
            signal_data,
            sampling_rate=self.target_fs,
            window_duration_sec=self.window_duration_sec,
            overlap_sec=0.0,
        )
    
    def _normalize(
        self,
        tokens: List[np.ndarray],
    ) -> Tuple[np.ndarray, dict]:
        """정규화 단계"""
        if not self.standardize:
            # 정규화하지 않음
            return np.array(tokens), {}
        
        # 모든 토큰을 스택 (batch, time, channels)
        stacked = np.array(tokens)  # (num_tokens, token_size, num_channels)
        
        # 채널별 표준화
        norm_tokens, norm_params = channel_wise_normalize(stacked, method="standardize")
        
        return norm_tokens, norm_params
    
    def _to_tensor(
        self,
        tokens: np.ndarray,
    ) -> torch.Tensor:
        """PyTorch 텐서 변환"""
        # tokens shape: (num_tokens, token_size, num_channels)
        # target shape: (num_tokens, num_channels, token_size)
        tokens_transposed = tokens.transpose(0, 2, 1)
        
        tensor = torch.from_numpy(tokens_transposed).float()
        tensor = tensor.to(self.device)
        
        return tensor


def create_default_pipeline(
    device: str = "cpu",
) -> PreprocessingPipeline:
    """기본 설정의 파이프라인 생성"""
    return PreprocessingPipeline(
        target_fs=128.0,
        filter_low_freq=0.5,
        filter_high_freq=50.0,
        filter_order=4,
        window_duration_sec=5.0,
        standardize=True,
        device=device,
    )
