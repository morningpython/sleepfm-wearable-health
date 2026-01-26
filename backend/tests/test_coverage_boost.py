"""
커버리지 향상을 위한 추가 테스트

커버리지가 낮은 모듈들의 누락된 코드 경로를 테스트:
- inference.py (0%)
- model_manager.py (42%)
- resample.py (57%) - scipy_poly 메서드
- filter.py (65%) - validate_filtered_signal
- tokenize.py (68%) - validate_tokens
- normalize.py (62%)
"""

import pytest
import numpy as np
import torch
from unittest.mock import Mock, patch, MagicMock

# ==================== Resample 추가 테스트 ====================

class TestResampleExtended:
    """리샘플링 추가 테스트 - 누락 경로 커버"""
    
    def test_resample_scipy_poly_method(self):
        """scipy_poly 메서드 테스트"""
        from app.preprocessing.resample import resample_signal
        
        signal = np.random.randn(2560)  # 10초 @ 256Hz
        resampled = resample_signal(signal, 256, 128, method="scipy_poly")
        
        # 샘플 개수 대략 절반
        expected = int(np.round(2560 * 128 / 256))
        assert abs(resampled.shape[0] - expected) <= 1
    
    def test_resample_scipy_poly_2d(self):
        """scipy_poly 메서드 2D 테스트"""
        from app.preprocessing.resample import resample_signal
        
        signal = np.random.randn(2560, 3)  # 10초 @ 256Hz, 3채널
        resampled = resample_signal(signal, 256, 128, method="scipy_poly")
        
        assert resampled.shape[1] == 3
    
    def test_resample_invalid_method(self):
        """잘못된 리샘플링 메서드"""
        from app.preprocessing.resample import resample_signal
        
        signal = np.random.randn(1000)
        with pytest.raises(ValueError, match="Unknown resampling method"):
            resample_signal(signal, 256, 128, method="invalid")
    
    def test_resample_empty_signal(self):
        """빈 신호 처리"""
        from app.preprocessing.resample import resample_signal
        
        signal = np.array([])
        with pytest.raises(ValueError, match="Signal cannot be empty"):
            resample_signal(signal, 256, 128)
    
    def test_resample_invalid_sampling_rate(self):
        """잘못된 샘플링 레이트"""
        from app.preprocessing.resample import resample_signal, get_resample_ratio
        
        signal = np.random.randn(100)
        with pytest.raises(ValueError, match="positive"):
            resample_signal(signal, -256, 128)
        
        with pytest.raises(ValueError, match="positive"):
            get_resample_ratio(-256, 128)
    
    def test_resample_3d_signal_error(self):
        """3D 신호 에러"""
        from app.preprocessing.resample import resample_signal
        
        signal = np.random.randn(100, 3, 2)
        with pytest.raises(ValueError, match="1D or 2D"):
            resample_signal(signal, 256, 128)
    
    def test_resample_same_rate(self):
        """동일 샘플링 레이트 (복사 반환)"""
        from app.preprocessing.resample import resample_signal
        
        signal = np.random.randn(1000)
        resampled = resample_signal(signal, 128, 128)
        
        np.testing.assert_array_equal(signal, resampled)
    
    def test_validate_resampled_signal_mismatch(self):
        """리샘플링 검증 실패"""
        from app.preprocessing.resample import validate_resampled_signal
        
        original = np.random.randn(1000)
        # 샘플 수가 잘못된 경우
        wrong_resampled = np.random.randn(100)  # 너무 적음
        
        with pytest.raises(AssertionError):
            validate_resampled_signal(original, wrong_resampled, 256, 128, tolerance=0.05)


# ==================== Filter 추가 테스트 ====================

class TestFilterExtended:
    """필터링 추가 테스트"""
    
    def test_validate_filtered_signal(self):
        """필터링된 신호 검증"""
        from app.preprocessing.filter import apply_butterworth_filter, validate_filtered_signal
        
        original = np.random.randn(1280)
        filtered = apply_butterworth_filter(original, 128, 0.5, 50)
        
        metrics = validate_filtered_signal(original, filtered)
        
        assert "energy_retention" in metrics
        assert "rms_change" in metrics
        assert "p2p_reduction" in metrics
        assert 0 <= metrics["energy_retention"] <= 100
    
    def test_filter_frequency_response(self):
        """주파수 응답 테스트"""
        from app.preprocessing.filter import ButterworthFilter
        
        filt = ButterworthFilter(0.5, 50, 128, order=4)
        freq, mag = filt.get_frequency_response(num_points=500)
        
        assert len(freq) == 500
        assert len(mag) == 500
    
    def test_filter_negative_freq_error(self):
        """음수 주파수 에러"""
        from app.preprocessing.filter import ButterworthFilter
        
        with pytest.raises(ValueError, match="positive"):
            ButterworthFilter(-0.5, 50, 128)
    
    def test_filter_nyquist_error(self):
        """나이퀴스트 주파수 초과 에러"""
        from app.preprocessing.filter import ButterworthFilter
        
        # 128Hz 샘플링 레이트의 나이퀴스트 주파수는 64Hz
        with pytest.raises(ValueError, match="Nyquist"):
            ButterworthFilter(0.5, 65, 128)  # 65Hz > 64Hz (Nyquist)
    
    def test_filter_3d_signal_error(self):
        """3D 신호 에러"""
        from app.preprocessing.filter import ButterworthFilter
        
        filt = ButterworthFilter(0.5, 50, 128)
        signal_3d = np.random.randn(100, 3, 2)
        
        with pytest.raises(ValueError, match="1D or 2D"):
            filt.apply(signal_3d)


# ==================== Tokenize 추가 테스트 ====================

class TestTokenizeExtended:
    """토큰화 추가 테스트"""
    
    def test_validate_tokens(self):
        """토큰 검증"""
        from app.preprocessing.tokenize import tokenize_signal, validate_tokens
        
        signal = np.random.randn(3840)  # 30초 @ 128Hz
        tokens = tokenize_signal(signal, 128, 5, 0)
        
        result = validate_tokens(tokens, 640)
        
        assert result["num_tokens"] == 6
        assert len(result["sizes"]) == 6
    
    def test_validate_empty_tokens(self):
        """빈 토큰 리스트 검증"""
        from app.preprocessing.tokenize import validate_tokens
        
        with pytest.raises(ValueError, match="No tokens generated"):
            validate_tokens([], 640)
    
    def test_get_window_times(self):
        """윈도우 시간 계산"""
        from app.preprocessing.tokenize import get_window_indices, get_window_times
        
        indices = get_window_indices(1280, 640, 0)
        times = get_window_times(indices, 128)
        
        assert len(times) == 2
        assert times[0] == (0.0, 5.0)
        assert times[1] == (5.0, 10.0)
    
    def test_create_windows_empty_signal(self):
        """빈 신호 윈도우 생성"""
        from app.preprocessing.tokenize import create_windows
        
        with pytest.raises(ValueError, match="Signal cannot be empty"):
            create_windows(np.array([]), 640)
    
    def test_create_windows_invalid_size(self):
        """잘못된 윈도우 크기"""
        from app.preprocessing.tokenize import create_windows
        
        signal = np.random.randn(1000)
        
        with pytest.raises(ValueError, match="positive"):
            create_windows(signal, 0)
        
        with pytest.raises(ValueError, match="positive"):
            create_windows(signal, -640)
    
    def test_create_windows_invalid_overlap(self):
        """잘못된 오버랩"""
        from app.preprocessing.tokenize import create_windows, get_window_indices
        
        signal = np.random.randn(1000)
        
        with pytest.raises(ValueError, match="Overlap"):
            create_windows(signal, 640, overlap=640)  # overlap >= window_size
        
        with pytest.raises(ValueError, match="Overlap"):
            get_window_indices(1000, 640, overlap=-1)  # 음수 오버랩


# ==================== Normalize 추가 테스트 ====================

class TestNormalizeExtended:
    """정규화 추가 테스트"""
    
    def test_normalize_signal_min_max(self):
        """min-max 정규화"""
        from app.preprocessing.normalize import normalize_signal
        
        signal = np.random.randn(1000) * 100 + 50
        normalized = normalize_signal(signal, method="minmax")
        
        assert np.min(normalized) >= -1e-6
        assert np.max(normalized) <= 1 + 1e-6
    
    def test_standardize_signal(self):
        """표준화 테스트"""
        from app.preprocessing.normalize import standardize_signal
        
        signal = np.random.randn(1000) * 50 + 100
        standardized, mean, std = standardize_signal(signal)
        
        # 평균 ~0, 표준편차 ~1
        assert abs(np.mean(standardized)) < 0.1
        assert abs(np.std(standardized) - 1) < 0.1
        assert mean is not None
        assert std is not None
    
    def test_normalize_robust(self):
        """robust 정규화 (상수 신호)"""
        from app.preprocessing.normalize import normalize_signal
        
        signal = np.ones(100) * 5  # 상수
        normalized = normalize_signal(signal, method="robust")
        
        # 상수 신호 -> 중앙값 기준 정규화
        assert normalized is not None
    
    def test_channel_wise_normalize_2d(self):
        """2D 채널별 정규화"""
        from app.preprocessing.normalize import channel_wise_normalize
        
        # (samples, channels)
        signal = np.random.randn(1000, 3) * np.array([10, 100, 1000])
        normalized, params = channel_wise_normalize(signal, method="standardize")
        
        assert normalized.shape == signal.shape
        # 각 채널의 평균이 0에 가까움
        for ch in range(3):
            assert abs(np.mean(normalized[:, ch])) < 0.1
    
    def test_channel_wise_normalize_3d(self):
        """3D 채널별 정규화 (배치)"""
        from app.preprocessing.normalize import channel_wise_normalize
        
        # (batch, samples, channels)
        signal = np.random.randn(4, 640, 3) * np.array([10, 100, 1000])
        normalized, params = channel_wise_normalize(signal, method="standardize")
        
        assert normalized.shape == signal.shape
        assert "ch0" in params
    
    def test_inverse_standardize(self):
        """역표준화"""
        from app.preprocessing.normalize import standardize_signal, inverse_standardize
        
        original = np.random.randn(1000) * 50 + 100
        standardized, mean, std = standardize_signal(original)
        
        reconstructed = inverse_standardize(standardized, mean, std)
        
        np.testing.assert_array_almost_equal(original, reconstructed)
    
    def test_normalize_empty_signal(self):
        """빈 신호 처리"""
        from app.preprocessing.normalize import normalize_signal, standardize_signal
        
        with pytest.raises(ValueError, match="empty"):
            normalize_signal(np.array([]))
        
        with pytest.raises(ValueError, match="empty"):
            standardize_signal(np.array([]))
    
    def test_normalize_unknown_method(self):
        """알 수 없는 메서드 에러"""
        from app.preprocessing.normalize import normalize_signal
        
        with pytest.raises(ValueError, match="Unknown"):
            normalize_signal(np.random.randn(100), method="unknown")
    
    def test_channel_wise_normalize_method(self):
        """채널별 정규화 - normalize 메서드"""
        from app.preprocessing.normalize import channel_wise_normalize
        
        signal = np.random.randn(100, 3)
        normalized, params = channel_wise_normalize(signal, method="normalize")
        
        assert normalized.shape == signal.shape
    
    def test_channel_wise_normalize_1d(self):
        """1D 채널별 정규화"""
        from app.preprocessing.normalize import channel_wise_normalize
        
        signal = np.random.randn(1000)
        normalized, params = channel_wise_normalize(signal, method="standardize")
        
        assert normalized.shape == signal.shape
        assert "mean" in params
    
    def test_channel_wise_normalize_4d_error(self):
        """4D 신호 에러"""
        from app.preprocessing.normalize import channel_wise_normalize
        
        signal = np.random.randn(2, 10, 640, 3)  # 4D
        with pytest.raises(ValueError, match="1D, 2D, or 3D"):
            channel_wise_normalize(signal)
    
    def test_channel_wise_normalize_unknown_method(self):
        """채널별 정규화 - 알 수 없는 메서드"""
        from app.preprocessing.normalize import channel_wise_normalize
        
        signal = np.random.randn(100, 3)
        with pytest.raises(ValueError, match="Unknown method"):
            channel_wise_normalize(signal, method="invalid")


# ==================== Model Manager 테스트 ====================

class TestModelManager:
    """모델 매니저 테스트"""
    
    def test_model_manager_singleton(self):
        """싱글톤 패턴"""
        from app.ml.model_manager import ModelManager, get_model_manager
        
        manager1 = ModelManager()
        manager2 = ModelManager()
        
        assert manager1 is manager2
    
    def test_model_not_initialized_error(self):
        """초기화 전 접근 에러"""
        from app.ml.model_manager import ModelManager
        
        # 새 인스턴스 시뮬레이션 (리셋)
        manager = ModelManager()
        manager._is_initialized = False
        
        with pytest.raises(RuntimeError, match="not initialized"):
            _ = manager.model
        
        with pytest.raises(RuntimeError, match="not initialized"):
            _ = manager.device
    
    def test_model_manager_device_info(self):
        """디바이스 정보 조회"""
        from app.ml.model_manager import ModelManager
        
        manager = ModelManager()
        manager._is_initialized = True
        manager._device = "cpu"
        
        info = manager.get_device_info()
        
        assert info["device"] == "cpu"
        assert "cuda_available" in info
    
    def test_get_model_manager_cached(self):
        """get_model_manager 캐시"""
        from app.ml.model_manager import get_model_manager
        
        manager1 = get_model_manager()
        manager2 = get_model_manager()
        
        assert manager1 is manager2


# ==================== Inference Engine 테스트 ====================

class TestInferenceEngine:
    """추론 엔진 테스트"""
    
    def test_inference_engine_creation(self):
        """추론 엔진 생성"""
        from app.ml.inference import InferenceEngine, create_default_inference_engine
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        model = SleepFMEncoder()
        
        engine = create_default_inference_engine(
            model=model,
            device="cpu",
        )
        
        assert engine.model is model
        assert engine.device == "cpu"
    
    def test_infer_batch(self):
        """배치 추론"""
        from app.ml.inference import InferenceEngine
        from app.preprocessing.pipeline import PreprocessingPipeline
        from app.ml.embedding_extractor import EmbeddingExtractor
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        model = SleepFMEncoder()
        pipeline = PreprocessingPipeline()
        extractor = EmbeddingExtractor(model=model, device="cpu")
        
        engine = InferenceEngine(
            model=model,
            preprocessing_pipeline=pipeline,
            embedding_extractor=extractor,
            device="cpu",
        )
        
        # 전처리된 토큰
        tokens = torch.randn(2, 3, 640)  # (batch, channels, time) - 3채널
        
        embeddings = engine.infer_batch(tokens)
        
        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] == 512


# ==================== Embedding Extractor 추가 테스트 ====================

class TestEmbeddingExtractor:
    """임베딩 추출기 테스트"""
    
    def test_extractor_creation(self):
        """추출기 생성"""
        from app.ml.embedding_extractor import EmbeddingExtractor
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        model = SleepFMEncoder()
        
        extractor = EmbeddingExtractor(
            model=model,
            device="cpu",
            max_batch_size=32,
        )
        
        assert extractor.device == "cpu"
        assert extractor.max_batch_size == 32
    
    def test_extract_embeddings(self):
        """임베딩 추출"""
        from app.ml.embedding_extractor import EmbeddingExtractor
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        model = SleepFMEncoder()
        extractor = EmbeddingExtractor(
            model=model,
            device="cpu",
        )
        
        tokens = torch.randn(4, 3, 640)
        embeddings = extractor.extract(tokens, return_numpy=True)
        
        assert embeddings.shape == (4, 512)
    
    def test_extract_return_tensor(self):
        """텐서 반환"""
        from app.ml.embedding_extractor import EmbeddingExtractor
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        model = SleepFMEncoder()
        extractor = EmbeddingExtractor(
            model=model,
            device="cpu",
        )
        
        tokens = torch.randn(2, 3, 640)
        embeddings = extractor.extract(tokens, return_numpy=False)
        
        assert isinstance(embeddings, torch.Tensor)
        assert embeddings.shape == (2, 512)


# ==================== SleepFM Encoder 추가 테스트 ====================

class TestSleepFMEncoderExtended:
    """SleepFM 인코더 추가 테스트"""
    
    def test_encoder_cpu_device(self):
        """CPU 디바이스 테스트"""
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        encoder = SleepFMEncoder()
        encoder.eval()
        
        # CPU에서 추론 - 3채널 입력
        dummy_input = torch.randn(1, 3, 640)
        
        with torch.no_grad():
            output = encoder(dummy_input)
        
        assert output.shape == (1, 512)
    
    def test_encoder_batch_processing(self):
        """배치 처리 테스트"""
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        encoder = SleepFMEncoder()
        encoder.eval()
        
        batch = torch.randn(8, 3, 640)  # 3채널 입력
        
        with torch.no_grad():
            output = encoder(batch)
        
        assert output.shape == (8, 512)
    
    def test_encoder_config_validation(self):
        """설정 검증 테스트"""
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        # 유효한 설정으로 생성
        encoder = SleepFMEncoder()
        
        assert encoder.config["input_channels"] == 3
        assert encoder.config["embedding_dim"] == 512
    
    def test_encoder_invalid_config(self):
        """잘못된 설정 에러"""
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        # 필수 키 누락
        with pytest.raises(ValueError, match="Missing required config key"):
            SleepFMEncoder(config={"input_channels": 3})  # embedding_dim 누락


# ==================== Model Manager 추가 테스트 ====================

class TestModelManagerExtended:
    """모델 매니저 추가 테스트"""
    
    def test_model_manager_already_initialized(self):
        """이미 초기화됨 로깅"""
        from app.ml.model_manager import ModelManager
        
        manager = ModelManager()
        # 첫 번째는 초기화 시도 (실패해도 됨)
        manager._is_initialized = True
        
        # 두 번째 초기화 시도 - 스킵됨
        manager.initialize()  # 로그만 출력되고 에러 없음
        
        assert manager.is_initialized
    
    def test_model_manager_initialization_failure(self):
        """초기화 실패"""
        from app.ml.model_manager import ModelManager
        
        manager = ModelManager()
        manager._is_initialized = False
        
        # 잘못된 체크포인트 경로로 초기화 실패
        with pytest.raises(RuntimeError, match="Model initialization failed"):
            manager.initialize(checkpoint_path="/invalid/path/model.bin", validate=False)


# ==================== Dependencies 추가 테스트 ====================

class TestDependencies:
    """의존성 테스트 - skip (FastAPI Depends 구조상 직접 테스트 불가)"""
    pass


# ==================== Main App 테스트 ====================

class TestMainApp:
    """메인 앱 테스트"""
    
    def test_health_check(self):
        """헬스체크 엔드포인트"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """루트 엔드포인트"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "SleepFM" in response.json().get("message", "")


# ==================== Database 테스트 ====================

class TestDatabase:
    """데이터베이스 테스트"""
    
    def test_get_db_session(self):
        """DB 세션 생성"""
        from app.database import get_db, engine
        
        # get_db는 제너레이터
        gen = get_db()
        session = next(gen)
        
        assert session is not None
        
        # 세션 종료
        try:
            next(gen)
        except StopIteration:
            pass
