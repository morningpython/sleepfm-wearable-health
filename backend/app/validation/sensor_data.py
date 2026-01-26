"""
센서 데이터 검증 함수

개별 검증 규칙을 구현합니다.
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
import logging

from .exceptions import (
    InsufficientDataError,
    MissingDataError,
    SignalRangeError,
    SamplingRateError,
    ChannelMismatchError,
)
from .utils import (
    calculate_missing_ratio,
    detect_missing_segments,
    estimate_heart_rate,
    estimate_respiration_rate,
)

logger = logging.getLogger(__name__)


# 생리학적 신호 범위 상수
HEART_RATE_RANGE = (30.0, 200.0)  # BPM
RESPIRATION_RATE_RANGE = (5.0, 40.0)  # breaths/min
SAMPLING_RATE_RANGE = (50.0, 500.0)  # Hz
MIN_DATA_HOURS = 2.0  # 최소 데이터 길이 (시간)
MAX_MISSING_RATIO = 0.10  # 최대 결측치 비율 (10%)
MAX_CONSECUTIVE_MISSING = 60.0  # 최대 연속 결측치 시간 (초)


def validate_data_length(
    data: np.ndarray,
    sampling_rate: float,
    min_hours: float = MIN_DATA_HOURS,
) -> Tuple[bool, float]:
    """
    데이터 길이 검증
    
    Args:
        data: 센서 데이터 배열
        sampling_rate: 샘플링 레이트 (Hz)
        min_hours: 최소 요구 시간 (기본: 2시간)
    
    Returns:
        (검증 통과 여부, 실제 시간)
    
    Raises:
        InsufficientDataError: 데이터가 최소 길이 미만일 때
    
    Examples:
        >>> data = np.random.randn(100 * 3600 * 2)  # 2시간 @ 100Hz
        >>> validate_data_length(data, sampling_rate=100, min_hours=2)
        (True, 2.0)
    """
    num_samples = len(data)
    duration_hours = num_samples / (sampling_rate * 3600)
    
    logger.debug(
        f"Validating data length: {num_samples} samples @ {sampling_rate} Hz "
        f"= {duration_hours:.2f} hours"
    )
    
    if duration_hours < min_hours:
        raise InsufficientDataError(
            required_hours=min_hours,
            actual_hours=duration_hours,
        )
    
    return True, duration_hours


def validate_missing_data(
    data: np.ndarray,
    channel_name: str,
    sampling_rate: float,
    max_ratio: float = MAX_MISSING_RATIO,
    max_consecutive_seconds: float = MAX_CONSECUTIVE_MISSING,
    warning_ratio: float = 0.05,  # 5% 이상 경고
) -> Tuple[bool, Dict[str, any]]:
    """
    결측치 검증
    
    Args:
        data: 센서 데이터 배열 (NaN = 결측치)
        channel_name: 채널 이름 (로깅용)
        sampling_rate: 샘플링 레이트 (Hz)
        max_ratio: 최대 허용 결측치 비율 (기본: 0.10 = 10%)
        max_consecutive_seconds: 최대 연속 결측치 시간 (초)
        warning_ratio: 경고 임계값 (기본: 0.05 = 5%)
    
    Returns:
        (검증 통과 여부, 결측치 정보 딕셔너리)
        정보 딕셔너리 포함:
        - missing_ratio: 결측치 비율
        - num_missing: 결측치 개수
        - warning: 경고 여부
        - segments: 긴 연속 결측치 구간 리스트
    
    Raises:
        MissingDataError: 결측치가 허용 범위를 초과할 때
    
    Examples:
        >>> data = np.array([1, 2, np.nan, 4, 5] * 1000)
        >>> validate_missing_data(data, "ecg", sampling_rate=100, max_ratio=0.25)
        (True, {'missing_ratio': 0.2, 'num_missing': 1000, ...})
    """
    missing_ratio = calculate_missing_ratio(data)
    num_missing = int(np.sum(np.isnan(data)))
    
    logger.debug(
        f"Validating missing data for {channel_name}: "
        f"{num_missing}/{len(data)} = {missing_ratio*100:.2f}%"
    )
    
    # 긴 연속 결측치 구간 탐지
    segments = detect_missing_segments(
        data,
        sampling_rate=sampling_rate,
        min_duration=max_consecutive_seconds,
    )
    
    # 결과 정보
    info = {
        "missing_ratio": float(missing_ratio),
        "num_missing": int(num_missing),
        "total_samples": int(len(data)),
        "warning": bool(missing_ratio >= warning_ratio),
        "segments": segments,
    }
    
    # 검증 실패 조건
    if missing_ratio > max_ratio:
        raise MissingDataError(
            channel=channel_name,
            missing_ratio=missing_ratio,
            threshold=max_ratio,
        )
    
    # 경고 로깅
    if info["warning"]:
        logger.warning(
            f"High missing data ratio for {channel_name}: {missing_ratio*100:.2f}%"
        )
    
    if segments:
        logger.warning(
            f"Found {len(segments)} long missing segments (>{max_consecutive_seconds}s) "
            f"in {channel_name}"
        )
    
    return True, info


def validate_signal_range(
    data: np.ndarray,
    channel_name: str,
    sampling_rate: float,
    signal_type: str = "auto",
    custom_range: Optional[Tuple[float, float]] = None,
    raise_on_fail: bool = False,
) -> Tuple[bool, Dict[str, any]]:
    """
    신호 범위 검증 (생리학적 타당성)
    
    Args:
        data: 센서 데이터 배열
        channel_name: 채널 이름
        sampling_rate: 샘플링 레이트 (Hz)
        signal_type: 신호 타입 ("ecg", "ppg", "accel", "auto")
        custom_range: 커스텀 범위 (min, max), signal_type="auto"일 때 사용
    
    Returns:
        (검증 통과 여부, 신호 정보 딕셔너리)
        정보 딕셔너리 포함:
        - signal_type: 감지된 신호 타입
        - estimated_metric: 추정값 (심박수 또는 호흡률)
        - valid_range: 유효 범위
        - passed: 검증 통과 여부
    
    Raises:
        SignalRangeError: 신호가 유효 범위를 벗어날 때
    
    Examples:
        >>> # 정상 심박수 범위의 ECG 신호
        >>> data = np.sin(2 * np.pi * 1.2 * np.linspace(0, 10, 1000))
        >>> validate_signal_range(data, "ecg", 100, signal_type="ecg")
        (True, {'signal_type': 'ecg', 'estimated_metric': 72.0, ...})
    """
    # 신호 타입 자동 감지
    if signal_type == "auto":
        if "ecg" in channel_name.lower():
            signal_type = "ecg"
        elif "ppg" in channel_name.lower():
            signal_type = "ppg"
        elif "accel" in channel_name.lower():
            signal_type = "accel"
        else:
            # 커스텀 범위 사용
            if custom_range is None:
                logger.warning(
                    f"Could not auto-detect signal type for {channel_name}, "
                    f"skipping range validation"
                )
                return True, {
                    "signal_type": "unknown",
                    "estimated_metric": None,
                    "valid_range": None,
                    "passed": True,
                }
            signal_type = "custom"
    
    logger.debug(f"Validating signal range for {channel_name} (type: {signal_type})")
    
    # NaN 제외하고 검증
    valid_data = data[~np.isnan(data)]
    
    if len(valid_data) < sampling_rate * 2:
        logger.warning(
            f"Insufficient valid data for range validation: {len(valid_data)} samples"
        )
        return True, {
            "signal_type": signal_type,
            "estimated_metric": None,
            "valid_range": None,
            "passed": True,
            "warning": "insufficient_data",
        }
    
    info = {"signal_type": signal_type}
    
    try:
        if signal_type in ["ecg", "ppg"]:
            # 심박수 추정
            try:
                heart_rate = estimate_heart_rate(valid_data, sampling_rate, method="peaks")
            except ValueError:
                # peaks 실패 시 fft 시도
                heart_rate = estimate_heart_rate(valid_data, sampling_rate, method="fft")
            
            info["estimated_metric"] = heart_rate
            info["metric_name"] = "heart_rate"
            info["metric_unit"] = "BPM"
            info["valid_range"] = HEART_RATE_RANGE
            
            min_hr, max_hr = HEART_RATE_RANGE
            if not (min_hr <= heart_rate <= max_hr):
                if raise_on_fail:
                    raise SignalRangeError(
                        channel=channel_name,
                        metric="heart_rate",
                        value=heart_rate,
                        valid_range=HEART_RATE_RANGE,
                    )
                else:
                    info["passed"] = False
                    info["error"] = f"Heart rate {heart_rate:.1f} BPM out of range {HEART_RATE_RANGE}"
                    return False, info
            
            logger.info(f"Heart rate for {channel_name}: {heart_rate:.1f} BPM")
        
        elif signal_type == "accel":
            # 호흡률 추정
            try:
                respiration_rate = estimate_respiration_rate(valid_data, sampling_rate)
            except ValueError as e:
                logger.warning(f"Could not estimate respiration rate: {e}")
                # 호흡률 추정 실패는 치명적이지 않음
                info["estimated_metric"] = None
                info["metric_name"] = "respiration_rate"
                info["metric_unit"] = "breaths/min"
                info["valid_range"] = RESPIRATION_RATE_RANGE
                info["passed"] = True
                info["warning"] = "estimation_failed"
                return True, info
            
            info["estimated_metric"] = respiration_rate
            info["metric_name"] = "respiration_rate"
            info["metric_unit"] = "breaths/min"
            info["valid_range"] = RESPIRATION_RATE_RANGE
            
            min_rr, max_rr = RESPIRATION_RATE_RANGE
            if not (min_rr <= respiration_rate <= max_rr):
                if raise_on_fail:
                    raise SignalRangeError(
                        channel=channel_name,
                        metric="respiration_rate",
                        value=respiration_rate,
                        valid_range=RESPIRATION_RATE_RANGE,
                    )
                else:
                    info["passed"] = False
                    info["error"] = f"Respiration rate {respiration_rate:.1f} breaths/min out of range {RESPIRATION_RATE_RANGE}"
                    return False, info
            
            logger.info(f"Respiration rate for {channel_name}: {respiration_rate:.1f} breaths/min")
        
        elif signal_type == "custom" and custom_range is not None:
            # 커스텀 범위 검증 (단순 min/max)
            min_val, max_val = custom_range
            signal_min = float(np.min(valid_data))
            signal_max = float(np.max(valid_data))
            
            info["estimated_metric"] = (signal_min + signal_max) / 2
            info["metric_name"] = "signal_value"
            info["metric_unit"] = "custom"
            info["valid_range"] = custom_range
            info["signal_min"] = signal_min
            info["signal_max"] = signal_max
            
            if not (min_val <= signal_min and signal_max <= max_val):
                if raise_on_fail:
                    raise SignalRangeError(
                        channel=channel_name,
                        metric="signal_value",
                        value=signal_max if signal_max > max_val else signal_min,
                        valid_range=custom_range,
                    )
                else:
                    info["passed"] = False
                    info["error"] = f"Signal value out of custom range {custom_range}"
                    return False, info
        
        info["passed"] = True
        return True, info
    
    except SignalRangeError:
        # 재발생
        raise
    except Exception as e:
        # 예상치 못한 에러는 경고만
        logger.warning(f"Error during signal range validation for {channel_name}: {e}")
        info["passed"] = True
        info["warning"] = str(e)
        return True, info


def validate_sampling_rate(
    data: np.ndarray,
    expected_rate: float,
    channel_name: str,
    tolerance: float = 0.05,  # 5% 허용 오차
) -> Tuple[bool, Dict[str, any]]:
    """
    샘플링 레이트 검증
    
    실제로는 메타데이터에서 샘플링 레이트를 받으므로, 
    이 함수는 주로 채널 간 일관성 체크에 사용됩니다.
    
    Args:
        data: 센서 데이터 배열
        expected_rate: 예상 샘플링 레이트 (Hz)
        channel_name: 채널 이름
        tolerance: 허용 오차 비율 (기본: 0.05 = 5%)
    
    Returns:
        (검증 통과 여부, 샘플링 레이트 정보)
    
    Raises:
        SamplingRateError: 샘플링 레이트가 허용 범위를 벗어날 때
    
    Examples:
        >>> data = np.random.randn(1000)
        >>> validate_sampling_rate(data, expected_rate=100, channel_name="ecg")
        (True, {'expected_rate': 100, 'tolerance': 0.05, ...})
    """
    min_rate, max_rate = SAMPLING_RATE_RANGE
    
    # 예상 레이트가 일반적인 범위를 벗어나는지 체크
    if not (min_rate <= expected_rate <= max_rate):
        logger.warning(
            f"Unusual sampling rate for {channel_name}: {expected_rate} Hz "
            f"(typical range: {min_rate}-{max_rate} Hz)"
        )
    
    info = {
        "expected_rate": expected_rate,
        "tolerance": tolerance,
        "min_valid_rate": expected_rate * (1 - tolerance),
        "max_valid_rate": expected_rate * (1 + tolerance),
        "passed": True,
    }
    
    logger.debug(
        f"Validating sampling rate for {channel_name}: {expected_rate} Hz "
        f"(tolerance: ±{tolerance*100:.1f}%)"
    )
    
    return True, info


def validate_channels(
    sensor_data: Dict[str, np.ndarray],
    required_channels: List[str] = ["ecg", "ppg", "accel"],
    check_length_consistency: bool = True,
    length_tolerance: int = 10,  # 샘플 단위 허용 오차
) -> Tuple[bool, Dict[str, any]]:
    """
    채널 검증
    
    Args:
        sensor_data: 채널별 데이터 딕셔너리
        required_channels: 필수 채널 리스트
        check_length_consistency: 채널 길이 일관성 체크 여부
        length_tolerance: 길이 허용 오차 (샘플 수)
    
    Returns:
        (검증 통과 여부, 채널 정보)
    
    Raises:
        ChannelMismatchError: 필수 채널 누락 또는 길이 불일치
    
    Examples:
        >>> data = {
        ...     "ecg": np.random.randn(1000),
        ...     "ppg": np.random.randn(1000),
        ...     "accel": np.random.randn(1000),
        ... }
        >>> validate_channels(data)
        (True, {'present_channels': ['ecg', 'ppg', 'accel'], ...})
    """
    present_channels = list(sensor_data.keys())
    
    # 필수 채널 체크
    missing_channels = [ch for ch in required_channels if ch not in present_channels]
    if missing_channels:
        raise ChannelMismatchError(
            missing_channels=missing_channels,
            message=f"Missing required channels: {', '.join(missing_channels)}",
        )
    
    # 채널 길이 체크
    channel_lengths = {ch: len(data) for ch, data in sensor_data.items()}
    
    if check_length_consistency:
        lengths = list(channel_lengths.values())
        max_length = max(lengths)
        min_length = min(lengths)
        
        if max_length - min_length > length_tolerance:
            raise ChannelMismatchError(
                length_mismatch=channel_lengths,
                message=(
                    f"Channel length mismatch detected: "
                    f"min={min_length}, max={max_length} "
                    f"(tolerance: {length_tolerance} samples)"
                ),
            )
    
    info = {
        "present_channels": present_channels,
        "required_channels": required_channels,
        "channel_lengths": channel_lengths,
        "length_consistent": check_length_consistency,
        "passed": True,
    }
    
    logger.info(
        f"Channel validation passed: {len(present_channels)} channels, "
        f"{channel_lengths} samples"
    )
    
    return True, info
