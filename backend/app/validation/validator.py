"""
통합 데이터 검증기

센서 데이터 전체 검증 프로세스를 관리합니다.
"""

import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging
from datetime import datetime

from .sensor_data import (
    validate_data_length,
    validate_missing_data,
    validate_signal_range,
    validate_sampling_rate,
    validate_channels,
)
from .exceptions import DataValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """검증 결과 데이터 클래스"""
    
    # 전체 결과
    passed: bool
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # 채널별 결과
    channel_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # 전체 메트릭
    total_duration_hours: float = 0.0
    total_channels: int = 0
    
    # 에러 및 경고
    errors: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[Dict[str, str]] = field(default_factory=list)
    
    # 추가 정보
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "passed": self.passed,
            "timestamp": self.timestamp,
            "channel_results": self.channel_results,
            "total_duration_hours": self.total_duration_hours,
            "total_channels": self.total_channels,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }
    
    def add_error(self, channel: str, error_type: str, message: str, details: Optional[Dict] = None):
        """에러 추가"""
        self.errors.append({
            "channel": channel,
            "type": error_type,
            "message": message,
            "details": details or {},
        })
        self.passed = False
    
    def add_warning(self, channel: str, warning_type: str, message: str, details: Optional[Dict] = None):
        """경고 추가"""
        self.warnings.append({
            "channel": channel,
            "type": warning_type,
            "message": message,
            "details": details or {},
        })
    
    def get_summary(self) -> str:
        """요약 문자열 생성"""
        status = "PASSED" if self.passed else "FAILED"
        summary = [
            f"Validation Result: {status}",
            f"Timestamp: {self.timestamp}",
            f"Duration: {self.total_duration_hours:.2f} hours",
            f"Channels: {self.total_channels}",
            f"Errors: {len(self.errors)}",
            f"Warnings: {len(self.warnings)}",
        ]
        
        if self.errors:
            summary.append("\nErrors:")
            for err in self.errors:
                summary.append(f"  - [{err['channel']}] {err['type']}: {err['message']}")
        
        if self.warnings:
            summary.append("\nWarnings:")
            for warn in self.warnings:
                summary.append(f"  - [{warn['channel']}] {warn['type']}: {warn['message']}")
        
        return "\n".join(summary)


class SensorDataValidator:
    """
    센서 데이터 통합 검증기
    
    전체 검증 프로세스를 관리하고 결과를 반환합니다.
    """
    
    def __init__(
        self,
        min_hours: float = 2.0,
        max_missing_ratio: float = 0.10,
        warning_missing_ratio: float = 0.05,
        max_consecutive_missing: float = 60.0,
        required_channels: Optional[List[str]] = None,
        validate_signal_ranges: bool = True,
        strict_mode: bool = False,
    ):
        """
        Args:
            min_hours: 최소 데이터 길이 (시간)
            max_missing_ratio: 최대 허용 결측치 비율
            warning_missing_ratio: 경고 임계값 결측치 비율
            max_consecutive_missing: 최대 연속 결측치 시간 (초)
            required_channels: 필수 채널 리스트 (기본: ["ecg", "ppg", "accel"])
            validate_signal_ranges: 신호 범위 검증 여부
            strict_mode: 엄격 모드 (경고를 에러로 처리)
        """
        self.min_hours = min_hours
        self.max_missing_ratio = max_missing_ratio
        self.warning_missing_ratio = warning_missing_ratio
        self.max_consecutive_missing = max_consecutive_missing
        self.required_channels = required_channels or ["ecg", "ppg", "accel"]
        self.validate_signal_ranges = validate_signal_ranges
        self.strict_mode = strict_mode
        
        logger.info(
            f"Initialized SensorDataValidator: "
            f"min_hours={min_hours}, max_missing={max_missing_ratio*100}%, "
            f"strict_mode={strict_mode}"
        )
    
    def validate(
        self,
        sensor_data: Dict[str, np.ndarray],
        sampling_rates: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        센서 데이터 전체 검증
        
        Args:
            sensor_data: 채널별 데이터 딕셔너리 {"ecg": array, "ppg": array, ...}
            sampling_rates: 채널별 샘플링 레이트 {"ecg": 100, "ppg": 100, ...}
            metadata: 추가 메타데이터 (선택)
        
        Returns:
            ValidationResult 객체
        
        Examples:
            >>> validator = SensorDataValidator(min_hours=2.0)
            >>> sensor_data = {
            ...     "ecg": np.random.randn(100 * 3600 * 2),
            ...     "ppg": np.random.randn(100 * 3600 * 2),
            ...     "accel": np.random.randn(100 * 3600 * 2),
            ... }
            >>> sampling_rates = {"ecg": 100, "ppg": 100, "accel": 100}
            >>> result = validator.validate(sensor_data, sampling_rates)
            >>> result.passed
            True
        """
        logger.info("Starting sensor data validation")
        
        result = ValidationResult(passed=True)
        result.total_channels = len(sensor_data)
        result.metadata = metadata or {}
        
        try:
            # 1. 채널 검증
            logger.debug("Step 1: Validating channels")
            self._validate_channels(sensor_data, result)
            
            # 2. 각 채널별 검증
            for channel_name, data in sensor_data.items():
                if channel_name not in sampling_rates:
                    result.add_warning(
                        channel=channel_name,
                        warning_type="missing_sampling_rate",
                        message=f"Sampling rate not provided for {channel_name}",
                    )
                    continue
                
                sampling_rate = sampling_rates[channel_name]
                
                logger.debug(f"Validating channel: {channel_name} @ {sampling_rate} Hz")
                
                channel_result = {}
                
                # 2.1 길이 검증
                try:
                    passed, duration_hours = validate_data_length(
                        data,
                        sampling_rate,
                        min_hours=self.min_hours,
                    )
                    channel_result["length_validation"] = {
                        "passed": passed,
                        "duration_hours": duration_hours,
                    }
                    result.total_duration_hours = max(result.total_duration_hours, duration_hours)
                except DataValidationError as e:
                    result.add_error(
                        channel=channel_name,
                        error_type=e.error_code,
                        message=e.message,
                        details=e.details,
                    )
                    channel_result["length_validation"] = {"passed": False, "error": str(e)}
                    continue  # 길이 부족하면 다른 검증 스킵
                
                # 2.2 결측치 검증
                try:
                    passed, missing_info = validate_missing_data(
                        data,
                        channel_name,
                        sampling_rate,
                        max_ratio=self.max_missing_ratio,
                        max_consecutive_seconds=self.max_consecutive_missing,
                        warning_ratio=self.warning_missing_ratio,
                    )
                    channel_result["missing_validation"] = missing_info
                    
                    # 경고 처리
                    if missing_info.get("warning"):
                        result.add_warning(
                            channel=channel_name,
                            warning_type="high_missing_ratio",
                            message=f"High missing ratio: {missing_info['missing_ratio']*100:.2f}%",
                            details=missing_info,
                        )
                        
                        if self.strict_mode:
                            result.add_error(
                                channel=channel_name,
                                error_type="high_missing_ratio_strict",
                                message="High missing ratio in strict mode",
                                details=missing_info,
                            )
                
                except DataValidationError as e:
                    result.add_error(
                        channel=channel_name,
                        error_type=e.error_code,
                        message=e.message,
                        details=e.details,
                    )
                    channel_result["missing_validation"] = {"passed": False, "error": str(e)}
                
                # 2.3 샘플링 레이트 검증
                try:
                    passed, rate_info = validate_sampling_rate(
                        data,
                        sampling_rate,
                        channel_name,
                    )
                    channel_result["sampling_rate_validation"] = rate_info
                except DataValidationError as e:
                    result.add_error(
                        channel=channel_name,
                        error_type=e.error_code,
                        message=e.message,
                        details=e.details,
                    )
                    channel_result["sampling_rate_validation"] = {"passed": False, "error": str(e)}
                
                # 2.4 신호 범위 검증 (선택적)
                if self.validate_signal_ranges:
                    try:
                        passed, range_info = validate_signal_range(
                            data,
                            channel_name,
                            sampling_rate,
                            signal_type="auto",
                        )
                        channel_result["signal_range_validation"] = range_info
                        
                        # 경고 처리
                        if range_info.get("warning"):
                            result.add_warning(
                                channel=channel_name,
                                warning_type="signal_range_warning",
                                message=range_info.get("warning", "Signal range validation warning"),
                                details=range_info,
                            )
                    
                    except DataValidationError as e:
                        result.add_error(
                            channel=channel_name,
                            error_type=e.error_code,
                            message=e.message,
                            details=e.details,
                        )
                        channel_result["signal_range_validation"] = {"passed": False, "error": str(e)}
                
                # 채널 결과 저장
                result.channel_results[channel_name] = channel_result
            
            # 최종 결과 결정
            if not result.errors:
                result.passed = True
                logger.info("Validation PASSED")
            else:
                result.passed = False
                logger.warning(f"Validation FAILED with {len(result.errors)} errors")
            
        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}", exc_info=True)
            result.add_error(
                channel="system",
                error_type="unexpected_error",
                message=str(e),
            )
            result.passed = False
        
        return result
    
    def _validate_channels(
        self,
        sensor_data: Dict[str, np.ndarray],
        result: ValidationResult,
    ):
        """채널 검증 내부 메서드"""
        try:
            passed, channel_info = validate_channels(
                sensor_data,
                required_channels=self.required_channels,
                check_length_consistency=True,
            )
            result.metadata["channel_validation"] = channel_info
        except DataValidationError as e:
            result.add_error(
                channel="all",
                error_type=e.error_code,
                message=e.message,
                details=e.details,
            )
    
    def validate_and_raise(
        self,
        sensor_data: Dict[str, np.ndarray],
        sampling_rates: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        검증 후 실패 시 예외 발생
        
        Args:
            sensor_data: 채널별 데이터
            sampling_rates: 채널별 샘플링 레이트
            metadata: 메타데이터
        
        Returns:
            ValidationResult (통과 시에만)
        
        Raises:
            DataValidationError: 검증 실패 시
        """
        result = self.validate(sensor_data, sampling_rates, metadata)
        
        if not result.passed:
            raise DataValidationError(
                message=f"Sensor data validation failed with {len(result.errors)} errors",
                details={
                    "errors": result.errors,
                    "warnings": result.warnings,
                },
                error_code="VALIDATION_FAILED",
            )
        
        return result


def create_default_validator(**kwargs) -> SensorDataValidator:
    """
    기본 설정 검증기 생성
    
    Args:
        **kwargs: SensorDataValidator 생성자 인자
    
    Returns:
        SensorDataValidator 인스턴스
    
    Examples:
        >>> validator = create_default_validator()
        >>> # 또는 커스텀 설정
        >>> validator = create_default_validator(min_hours=4.0, strict_mode=True)
    """
    return SensorDataValidator(**kwargs)
