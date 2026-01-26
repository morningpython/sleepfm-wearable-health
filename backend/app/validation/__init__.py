"""
데이터 검증 모듈

센서 데이터의 품질 검증 및 에러 처리를 담당합니다.
"""

from .exceptions import (
    DataValidationError,
    InsufficientDataError,
    MissingDataError,
    SignalRangeError,
    SamplingRateError,
    ChannelMismatchError,
)
from .sensor_data import (
    validate_data_length,
    validate_missing_data,
    validate_signal_range,
    validate_sampling_rate,
    validate_channels,
)
from .validator import SensorDataValidator, ValidationResult
from .utils import (
    estimate_heart_rate,
    estimate_respiration_rate,
    calculate_missing_ratio,
    detect_missing_segments,
    interpolate_missing_data,
    check_signal_quality,
)

__all__ = [
    # Exceptions
    "DataValidationError",
    "InsufficientDataError",
    "MissingDataError",
    "SignalRangeError",
    "SamplingRateError",
    "ChannelMismatchError",
    # Validation functions
    "validate_data_length",
    "validate_missing_data",
    "validate_signal_range",
    "validate_sampling_rate",
    "validate_channels",
    # Validator class
    "SensorDataValidator",
    "ValidationResult",
    # Utilities
    "estimate_heart_rate",
    "estimate_respiration_rate",
    "calculate_missing_ratio",
    "detect_missing_segments",
    "interpolate_missing_data",
    "check_signal_quality",
]
