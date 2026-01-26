"""
데이터 검증 예외 클래스

센서 데이터 검증 실패 시 발생하는 커스텀 예외들을 정의합니다.
"""

from typing import Optional, Dict, Any


class DataValidationError(Exception):
    """
    데이터 검증 기본 예외 클래스
    
    모든 데이터 검증 관련 예외의 부모 클래스입니다.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        """
        Args:
            message: 에러 메시지
            details: 상세 정보 딕셔너리
            error_code: 에러 코드 (예: "VALIDATION_001")
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.error_code = error_code or "VALIDATION_ERROR"
    
    def to_dict(self) -> Dict[str, Any]:
        """예외를 딕셔너리로 변환 (API 응답용)"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class InsufficientDataError(DataValidationError):
    """
    데이터 길이 부족 예외
    
    최소 요구 길이(2시간)를 충족하지 못할 때 발생합니다.
    """
    
    def __init__(
        self,
        required_hours: float,
        actual_hours: float,
        message: Optional[str] = None,
    ):
        """
        Args:
            required_hours: 필요한 최소 시간 (hours)
            actual_hours: 실제 데이터 시간 (hours)
            message: 커스텀 메시지 (선택)
        """
        if message is None:
            message = (
                f"Insufficient data length: {actual_hours:.2f} hours provided, "
                f"but minimum {required_hours:.2f} hours required."
            )
        
        details = {
            "required_hours": required_hours,
            "actual_hours": actual_hours,
            "shortage_hours": required_hours - actual_hours,
        }
        
        super().__init__(
            message=message,
            details=details,
            error_code="INSUFFICIENT_DATA",
        )


class MissingDataError(DataValidationError):
    """
    결측치 과다 예외
    
    결측치 비율이 허용 범위(10%)를 초과할 때 발생합니다.
    """
    
    def __init__(
        self,
        channel: str,
        missing_ratio: float,
        threshold: float = 0.10,
        message: Optional[str] = None,
    ):
        """
        Args:
            channel: 채널 이름 (예: "ecg", "ppg")
            missing_ratio: 결측치 비율 (0-1)
            threshold: 허용 임계값 (기본: 0.10 = 10%)
            message: 커스텀 메시지 (선택)
        """
        if message is None:
            message = (
                f"Excessive missing data in {channel}: {missing_ratio*100:.2f}% "
                f"(threshold: {threshold*100:.2f}%)"
            )
        
        details = {
            "channel": channel,
            "missing_ratio": missing_ratio,
            "missing_percentage": f"{missing_ratio*100:.2f}%",
            "threshold": threshold,
            "threshold_percentage": f"{threshold*100:.2f}%",
        }
        
        super().__init__(
            message=message,
            details=details,
            error_code="EXCESSIVE_MISSING_DATA",
        )


class SignalRangeError(DataValidationError):
    """
    신호 범위 초과 예외
    
    생리학적으로 타당하지 않은 범위의 값이 검출될 때 발생합니다.
    """
    
    def __init__(
        self,
        channel: str,
        metric: str,
        value: float,
        valid_range: tuple[float, float],
        message: Optional[str] = None,
    ):
        """
        Args:
            channel: 채널 이름 (예: "ecg", "ppg")
            metric: 측정 메트릭 (예: "heart_rate", "respiration_rate")
            value: 측정값
            valid_range: 유효 범위 (min, max)
            message: 커스텀 메시지 (선택)
        """
        min_val, max_val = valid_range
        
        if message is None:
            message = (
                f"Signal {metric} out of valid range for {channel}: "
                f"{value:.2f} (valid: {min_val}-{max_val})"
            )
        
        details = {
            "channel": channel,
            "metric": metric,
            "value": value,
            "valid_range": {"min": min_val, "max": max_val},
            "deviation": value - max_val if value > max_val else min_val - value,
        }
        
        super().__init__(
            message=message,
            details=details,
            error_code="SIGNAL_RANGE_ERROR",
        )


class SamplingRateError(DataValidationError):
    """
    샘플링 레이트 불일치 예외
    
    채널 간 샘플링 레이트가 일치하지 않거나 예상 범위를 벗어날 때 발생합니다.
    """
    
    def __init__(
        self,
        channel: str,
        detected_rate: float,
        expected_rate: Optional[float] = None,
        message: Optional[str] = None,
    ):
        """
        Args:
            channel: 채널 이름
            detected_rate: 검출된 샘플링 레이트
            expected_rate: 예상 샘플링 레이트 (선택)
            message: 커스텀 메시지 (선택)
        """
        if message is None:
            if expected_rate is not None:
                message = (
                    f"Sampling rate mismatch for {channel}: "
                    f"{detected_rate:.2f} Hz (expected: {expected_rate:.2f} Hz)"
                )
            else:
                message = (
                    f"Invalid sampling rate for {channel}: {detected_rate:.2f} Hz"
                )
        
        details = {
            "channel": channel,
            "detected_rate": detected_rate,
        }
        if expected_rate is not None:
            details["expected_rate"] = expected_rate
            details["deviation"] = abs(detected_rate - expected_rate)
        
        super().__init__(
            message=message,
            details=details,
            error_code="SAMPLING_RATE_ERROR",
        )


class ChannelMismatchError(DataValidationError):
    """
    채널 불일치 예외
    
    필수 채널이 누락되었거나 채널 길이가 일치하지 않을 때 발생합니다.
    """
    
    def __init__(
        self,
        missing_channels: Optional[list[str]] = None,
        length_mismatch: Optional[Dict[str, int]] = None,
        message: Optional[str] = None,
    ):
        """
        Args:
            missing_channels: 누락된 채널 리스트
            length_mismatch: 채널별 길이 딕셔너리
            message: 커스텀 메시지 (선택)
        """
        if message is None:
            if missing_channels:
                message = f"Missing required channels: {', '.join(missing_channels)}"
            elif length_mismatch:
                message = "Channel length mismatch detected"
            else:
                message = "Channel validation error"
        
        details = {}
        if missing_channels:
            details["missing_channels"] = missing_channels
        if length_mismatch:
            details["channel_lengths"] = length_mismatch
        
        super().__init__(
            message=message,
            details=details,
            error_code="CHANNEL_MISMATCH",
        )
