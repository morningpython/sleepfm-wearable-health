#!/usr/bin/env python3
"""
Story 2.4 검증 스크립트: 데이터 검증 및 품질 체크

구조 검증 및 기본 동작 확인을 수행합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def verify_file_structure():
    """파일 구조 검증"""
    print("=" * 60)
    print("1. 파일 구조 검증")
    print("=" * 60)
    
    required_files = [
        "app/validation/__init__.py",
        "app/validation/exceptions.py",
        "app/validation/sensor_data.py",
        "app/validation/validator.py",
        "app/validation/utils.py",
        "tests/test_story_2_4_validation.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = backend_dir / file_path
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
        
        if not exists:
            all_exist = False
    
    print()
    return all_exist


def verify_module_imports():
    """모듈 임포트 검증"""
    print("=" * 60)
    print("2. 모듈 임포트 검증")
    print("=" * 60)
    
    try:
        # 예외 클래스
        from app.validation import (
            DataValidationError,
            InsufficientDataError,
            MissingDataError,
            SignalRangeError,
            SamplingRateError,
        )
        print("✓ 예외 클래스 임포트 성공")
        
        # 검증 함수
        from app.validation import (
            validate_data_length,
            validate_missing_data,
            validate_signal_range,
            validate_sampling_rate,
        )
        print("✓ 검증 함수 임포트 성공")
        
        # 검증기 클래스
        from app.validation import SensorDataValidator, ValidationResult
        print("✓ 검증기 클래스 임포트 성공")
        
        # 유틸리티 함수
        from app.validation import (
            calculate_missing_ratio,
            detect_missing_segments,
            estimate_heart_rate,
            estimate_respiration_rate,
        )
        print("✓ 유틸리티 함수 임포트 성공")
        
        print()
        return True
    
    except ImportError as e:
        print(f"✗ 임포트 실패: {e}")
        print()
        return False


def verify_exception_classes():
    """예외 클래스 검증"""
    print("=" * 60)
    print("3. 예외 클래스 검증")
    print("=" * 60)
    
    try:
        from app.validation.exceptions import (
            InsufficientDataError,
            MissingDataError,
            SignalRangeError,
            SamplingRateError,
            ChannelMismatchError,
        )
        
        # InsufficientDataError
        error = InsufficientDataError(required_hours=2.0, actual_hours=1.5)
        assert error.error_code == "INSUFFICIENT_DATA"
        assert error.details["shortage_hours"] == 0.5
        print("✓ InsufficientDataError 생성 및 정보 확인")
        
        # MissingDataError
        error = MissingDataError(channel="ecg", missing_ratio=0.15)
        assert error.details["channel"] == "ecg"
        print("✓ MissingDataError 생성 및 정보 확인")
        
        # SignalRangeError
        error = SignalRangeError(
            channel="ppg",
            metric="heart_rate",
            value=250.0,
            valid_range=(30.0, 200.0),
        )
        assert error.details["value"] == 250.0
        print("✓ SignalRangeError 생성 및 정보 확인")
        
        # to_dict() 메서드
        error_dict = error.to_dict()
        assert "error" in error_dict
        assert "error_code" in error_dict
        print("✓ 예외 to_dict() 메서드 확인")
        
        print()
        return True
    
    except Exception as e:
        print(f"✗ 예외 클래스 검증 실패: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def verify_validation_functions():
    """검증 함수 확인"""
    print("=" * 60)
    print("4. 검증 함수 확인")
    print("=" * 60)
    
    try:
        import numpy as np
        from app.validation.sensor_data import (
            validate_data_length,
            validate_missing_data,
            validate_channels,
        )
        
        # 데이터 길이 검증
        data = np.random.randn(100 * 3600 * 2)  # 2시간 @ 100Hz
        passed, duration = validate_data_length(data, sampling_rate=100, min_hours=2.0)
        assert passed is True
        assert duration >= 2.0
        print(f"✓ validate_data_length: {duration:.2f} hours")
        
        # 결측치 검증 (결측치 없음)
        data = np.random.randn(1000)
        passed, info = validate_missing_data(data, "ecg", sampling_rate=100)
        assert passed is True
        assert info["missing_ratio"] == 0.0
        print(f"✓ validate_missing_data: {info['missing_ratio']*100:.1f}% missing")
        
        # 채널 검증
        sensor_data = {
            "ecg": np.random.randn(1000),
            "ppg": np.random.randn(1000),
            "accel": np.random.randn(1000),
        }
        passed, channel_info = validate_channels(sensor_data)
        assert passed is True
        assert len(channel_info["present_channels"]) == 3
        print(f"✓ validate_channels: {len(channel_info['present_channels'])} channels")
        
        print()
        return True
    
    except Exception as e:
        print(f"✗ 검증 함수 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def verify_validator_class():
    """검증기 클래스 확인"""
    print("=" * 60)
    print("5. 검증기 클래스 확인")
    print("=" * 60)
    
    try:
        import numpy as np
        from app.validation import SensorDataValidator
        
        # 검증기 생성
        validator = SensorDataValidator(
            min_hours=2.0,
            max_missing_ratio=0.10,
            validate_signal_ranges=False,  # 랜덤 데이터는 범위 검증 스킵
        )
        print("✓ SensorDataValidator 인스턴스 생성")
        
        # 테스트 데이터
        num_samples = 100 * 3600 * 2  # 2시간 @ 100Hz
        sensor_data = {
            "ecg": np.random.randn(num_samples),
            "ppg": np.random.randn(num_samples),
            "accel": np.random.randn(num_samples),
        }
        sampling_rates = {"ecg": 100, "ppg": 100, "accel": 100}
        
        # 검증 실행
        result = validator.validate(sensor_data, sampling_rates)
        
        assert result.passed is True
        assert result.total_channels == 3
        assert result.total_duration_hours >= 2.0
        print(f"✓ 검증 성공: {result.total_channels} channels, {result.total_duration_hours:.2f} hours")
        
        # ValidationResult 메서드
        summary = result.get_summary()
        assert "PASSED" in summary
        print("✓ ValidationResult.get_summary() 메서드 확인")
        
        result_dict = result.to_dict()
        assert "passed" in result_dict
        assert "timestamp" in result_dict
        print("✓ ValidationResult.to_dict() 메서드 확인")
        
        print()
        return True
    
    except Exception as e:
        print(f"✗ 검증기 클래스 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def verify_utility_functions():
    """유틸리티 함수 확인"""
    print("=" * 60)
    print("6. 유틸리티 함수 확인")
    print("=" * 60)
    
    try:
        import numpy as np
        from app.validation.utils import (
            calculate_missing_ratio,
            detect_missing_segments,
            interpolate_missing_data,
            check_signal_quality,
        )
        
        # 결측치 비율 계산
        data = np.array([1, 2, np.nan, 4, 5])
        ratio = calculate_missing_ratio(data)
        assert ratio == 0.4  # 2/5
        print(f"✓ calculate_missing_ratio: {ratio*100:.0f}%")
        
        # 결측치 구간 탐지
        data = np.random.randn(1000)
        data[200:500] = np.nan  # 3초 @ 100Hz
        segments = detect_missing_segments(data, sampling_rate=100, min_duration=2.0)
        assert len(segments) >= 1
        print(f"✓ detect_missing_segments: {len(segments)} segments")
        
        # 보간
        data = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
        interpolated = interpolate_missing_data(data, method="linear")
        assert not np.any(np.isnan(interpolated))
        assert interpolated[2] == 3.0
        print(f"✓ interpolate_missing_data: {interpolated[2]:.1f}")
        
        # 신호 품질
        signal = np.sin(2 * np.pi * np.linspace(0, 10, 1000))
        metrics = check_signal_quality(signal, sampling_rate=100)
        assert "snr" in metrics
        assert "std" in metrics
        print(f"✓ check_signal_quality: SNR={metrics['snr']:.1f} dB")
        
        print()
        return True
    
    except Exception as e:
        print(f"✗ 유틸리티 함수 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def verify_test_file():
    """테스트 파일 구조 검증"""
    print("=" * 60)
    print("7. 테스트 파일 검증")
    print("=" * 60)
    
    test_file = backend_dir / "tests" / "test_story_2_4_validation.py"
    
    if not test_file.exists():
        print("✗ 테스트 파일이 존재하지 않음")
        return False
    
    content = test_file.read_text()
    
    # 테스트 클래스 확인
    test_classes = [
        "TestDataLengthValidation",
        "TestMissingDataValidation",
        "TestSignalRangeValidation",
        "TestUtilityFunctions",
        "TestSensorDataValidator",
        "TestExceptions",
    ]
    
    for test_class in test_classes:
        if f"class {test_class}" in content:
            print(f"✓ {test_class} 클래스 존재")
        else:
            print(f"✗ {test_class} 클래스 누락")
            return False
    
    # 테스트 개수 확인
    test_count = content.count("def test_")
    print(f"✓ 총 {test_count}개 테스트 함수 발견")
    
    if test_count < 20:
        print(f"  ⚠ 20개 이상 권장 (현재: {test_count}개)")
    
    print()
    return True


def print_summary(results):
    """결과 요약 출력"""
    print("=" * 60)
    print("검증 결과 요약")
    print("=" * 60)
    
    total = len(results)
    passed = sum(results.values())
    
    for step, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {step}")
    
    print()
    print(f"총 {total}개 항목 중 {passed}개 통과 ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n✅ Story 2.4 검증 완료!")
        return 0
    else:
        print(f"\n⚠️  {total - passed}개 항목 실패")
        return 1


def main():
    """메인 실행 함수"""
    print("\n📋 Story 2.4 검증: 데이터 검증 및 품질 체크\n")
    
    results = {
        "파일 구조": verify_file_structure(),
        "모듈 임포트": verify_module_imports(),
        "예외 클래스": verify_exception_classes(),
        "검증 함수": verify_validation_functions(),
        "검증기 클래스": verify_validator_class(),
        "유틸리티 함수": verify_utility_functions(),
        "테스트 파일": verify_test_file(),
    }
    
    return print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
