"""
Story 2.2: 신호 전처리 파이프라인 구현 테스트

단위 테스트 (Unit Tests):
- 리샘플링, 필터링, 토큰화, 정규화 각 단계
- 통합 파이프라인
- 데이터 품질 검증
"""

import pytest
import numpy as np
import torch
from typing import Dict

# 전처리 모듈 임포트
from app.preprocessing.resample import resample_signal, get_resample_ratio, validate_resampled_signal
from app.preprocessing.filter import apply_butterworth_filter, ButterworthFilter
from app.preprocessing.tokenize import tokenize_signal, create_windows, get_window_indices
from app.preprocessing.normalize import normalize_signal, standardize_signal, channel_wise_normalize
from app.preprocessing.pipeline import PreprocessingPipeline, create_default_pipeline


class TestResample:
    """리샘플링 테스트"""
    
    def test_resample_ratio_calculation(self):
        """리샘플링 비율 계산"""
        assert get_resample_ratio(256, 128) == 0.5
        assert get_resample_ratio(64, 128) == 2.0
        assert get_resample_ratio(128, 128) == 1.0
    
    def test_resample_downsampling(self):
        """다운샘플링 (256Hz → 128Hz)"""
        signal = np.random.randn(2560)  # 10초 @ 256Hz
        resampled = resample_signal(signal, 256, 128)
        
        # 샘플 개수는 절반 정도
        assert resampled.shape[0] == 1280 or resampled.shape[0] == 1279
    
    def test_resample_upsampling(self):
        """업샘플링 (64Hz → 128Hz)"""
        signal = np.random.randn(640)  # 10초 @ 64Hz
        resampled = resample_signal(signal, 64, 128)
        
        # 샘플 개수는 2배
        assert resampled.shape[0] == 1280 or resampled.shape[0] == 1281
    
    def test_resample_2d_signal(self):
        """2D 신호 리샘플링 (다중채널)"""
        signal = np.random.randn(2560, 3)  # 10초 @ 256Hz, 3 channels
        resampled = resample_signal(signal, 256, 128)
        
        assert resampled.shape[1] == 3
        assert resampled.shape[0] == 1280 or resampled.shape[0] == 1279
    
    def test_resample_validation(self):
        """리샘플링 검증"""
        original = np.random.randn(2560)
        resampled = resample_signal(original, 256, 128)
        
        assert validate_resampled_signal(original, resampled, 256, 128)


class TestFilter:
    """필터링 테스트"""
    
    def test_butterworth_filter_creation(self):
        """Butterworth 필터 생성"""
        filt = ButterworthFilter(0.5, 50, 128, order=4)
        assert filt.low_freq == 0.5
        assert filt.high_freq == 50
    
    def test_butterworth_filter_invalid_freq(self):
        """잘못된 주파수 범위"""
        with pytest.raises(ValueError):
            ButterworthFilter(50, 0.5, 128)  # low > high
    
    def test_filter_application(self):
        """필터 적용"""
        signal = np.random.randn(1280)  # 10초 @ 128Hz
        filtered = apply_butterworth_filter(signal, 128, 0.5, 50)
        
        assert filtered.shape == signal.shape
        # 필터링 후 에너지 감소
        assert np.sum(filtered ** 2) < np.sum(signal ** 2)
    
    def test_filter_2d_signal(self):
        """2D 신호 필터링"""
        signal = np.random.randn(1280, 3)
        filtered = apply_butterworth_filter(signal, 128, 0.5, 50)
        
        assert filtered.shape == signal.shape


class TestTokenize:
    """토큰화 테스트"""
    
    def test_create_windows(self):
        """윈도우 생성"""
        signal = np.arange(100)
        windows = create_windows(signal, 20, overlap=0)
        
        assert len(windows) == 5
        assert windows[0].shape == (20,)
        np.testing.assert_array_equal(windows[0], np.arange(20))
    
    def test_create_windows_overlap(self):
        """겹침이 있는 윈도우"""
        signal = np.arange(100)
        windows = create_windows(signal, 20, overlap=10)
        
        assert len(windows) == 9  # (100-20)/10 + 1
    
    def test_tokenize_signal(self):
        """신호 토큰화 (5초 윈도우)"""
        signal = np.random.randn(3840)  # 30초 @ 128Hz
        tokens = tokenize_signal(signal, 128, 5, 0)
        
        assert len(tokens) == 6
        assert tokens[0].shape == (640,)
    
    def test_tokenize_2d_signal(self):
        """2D 신호 토큰화"""
        signal = np.random.randn(3840, 3)
        tokens = tokenize_signal(signal, 128, 5, 0)
        
        assert len(tokens) == 6
        assert tokens[0].shape == (640, 3)
    
    def test_get_window_indices(self):
        """윈도우 인덱스"""
        indices = get_window_indices(3840, 640, overlap=0)
        
        assert len(indices) == 6
        assert indices[0] == (0, 640)
        assert indices[-1] == (3200, 3840)


class TestNormalize:
    """정규화 테스트"""
    
    def test_minmax_normalize(self):
        """MinMax 정규화"""
        signal = np.array([1, 2, 3, 4, 5], dtype=float)
        normalized = normalize_signal(signal, "minmax")
        
        assert normalized.min() >= 0
        assert normalized.max() <= 1
        np.testing.assert_allclose(normalized, [0, 0.25, 0.5, 0.75, 1])
    
    def test_standardize(self):
        """표준화 (Z-score)"""
        signal = np.array([1, 2, 3, 4, 5], dtype=float)
        standardized, mean, std = standardize_signal(signal)
        
        # 표준화된 신호: 평균=0, 표준편차=1
        assert np.allclose(standardized.mean(), 0, atol=1e-10)
        assert np.allclose(standardized.std(), 1)
    
    def test_standardize_with_params(self):
        """사전 계산된 파라미터로 표준화"""
        signal1 = np.array([1, 2, 3, 4, 5], dtype=float)
        signal2 = np.array([2, 3, 4, 5, 6], dtype=float)
        
        # signal1에서 파라미터 계산
        _, mean, std = standardize_signal(signal1)
        
        # signal2를 같은 파라미터로 표준화
        standardized2, _, _ = standardize_signal(signal2, mean, std)
        
        # signal2의 평균/표준편차가 signal1과 다름
        assert not np.allclose(standardized2.mean(), 0)
    
    def test_channel_wise_normalize(self):
        """채널별 정규화"""
        signal = np.random.randn(100, 3)
        normalized, params = channel_wise_normalize(signal, "standardize")
        
        assert normalized.shape == signal.shape
        assert len(params) == 3  # 3 channels


class TestPipeline:
    """통합 파이프라인 테스트"""
    
    def create_synthetic_sensor_data(
        self,
        duration_sec: float = 10,
        fs: float = 100,
    ) -> Dict[str, np.ndarray]:
        """합성 센서 데이터 생성"""
        num_samples = int(duration_sec * fs)
        
        return {
            "ecg": np.random.randn(num_samples),
            "ppg": np.random.randn(num_samples),
            "accel": np.random.randn(num_samples, 3),
        }
    
    def test_pipeline_creation(self):
        """파이프라인 생성"""
        pipeline = create_default_pipeline()
        assert pipeline.target_fs == 128
        assert pipeline.token_size == 640
    
    def test_pipeline_processing(self):
        """전체 파이프라인 처리"""
        pipeline = create_default_pipeline()
        sensor_data = self.create_synthetic_sensor_data(10, 100)
        
        result = pipeline.process(sensor_data, 100)
        
        # 출력 검증
        assert "tokens" in result
        assert "tensor" in result
        assert "metadata" in result
        
        # 토큰 크기
        assert result["tokens"].shape[1] == 640
        assert result["tokens"].shape[2] == 3  # ECG, PPG, Accel
        
        # 텐서 형태
        assert isinstance(result["tensor"], torch.Tensor)
        assert result["tensor"].shape[1] == 3
        assert result["tensor"].shape[2] == 640
    
    def test_pipeline_resampling(self):
        """파이프라인: 리샘플링 확인"""
        pipeline = create_default_pipeline()
        sensor_data = self.create_synthetic_sensor_data(10, 256)  # 256Hz input
        
        result = pipeline.process(sensor_data, 256)
        
        # 토큰 개수 = 10초 * 128Hz / 640 = 2
        assert result["metadata"]["num_tokens"] == 2
    
    def test_pipeline_normalization(self):
        """파이프라인: 정규화 확인"""
        pipeline = create_default_pipeline()
        sensor_data = self.create_synthetic_sensor_data(10, 128)
        
        result = pipeline.process(sensor_data, 128)
        
        # 정규화 파라미터 존재
        assert "normalization_params" in result
        
        # 토큰이 표준화됨 (대략적 확인)
        tokens = result["tokens"]
        # 첫 번째 토큰의 평균이 0에 가까워야 함
        for ch in range(tokens.shape[2]):
            mean = tokens[:, :, ch].mean()
            assert abs(mean) < 1.0  # 0에 가까운지 확인


class TestDataValidation:
    """데이터 검증 테스트"""
    
    def test_empty_signal_error(self):
        """빈 신호 처리"""
        with pytest.raises(ValueError):
            create_windows(np.array([]), 20)
    
    def test_invalid_window_size(self):
        """잘못된 윈도우 크기 (0 이하)"""
        signal = np.arange(100)
        with pytest.raises(ValueError):
            create_windows(signal, 0)  # 0은 유효하지 않음
        with pytest.raises(ValueError):
            create_windows(signal, -10)  # 음수도 유효하지 않음
    
    def test_window_size_larger_than_signal(self):
        """윈도우가 신호보다 큼"""
        signal = np.arange(100)
        windows = create_windows(signal, 150)
        assert len(windows) == 0  # 윈도우 생성 불가


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
