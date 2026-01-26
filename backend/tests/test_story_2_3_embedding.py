"""
Story 2.3: 멀티모달 임베딩 추출 테스트

단위 테스트 (Unit Tests):
- 임베딩 추출 기본 기능
- 배치 처리
- 메모리 최적화
- 입출력 검증
"""

import pytest
import numpy as np
import torch

# 임베딩 모듈 임포트
from app.ml.embedding_extractor import (
    EmbeddingExtractor,
    extract_embeddings,
    validate_embeddings,
    compute_embedding_statistics,
)


class SimpleModel(torch.nn.Module):
    """테스트용 간단한 모델"""
    
    def __init__(self, input_channels=3, time_steps=640, embedding_dim=512):
        super().__init__()
        self.flatten_size = input_channels * time_steps
        self.embedding_dim = embedding_dim
        
        # 간단한 MLP: flatten → fc → embedding
        self.fc1 = torch.nn.Linear(self.flatten_size, 1024)
        self.relu = torch.nn.ReLU()
        self.fc2 = torch.nn.Linear(1024, embedding_dim)
    
    def forward(self, x):
        # x: (batch, channels, time_steps)
        batch_size = x.size(0)
        x = x.view(batch_size, -1)  # Flatten
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


class TestEmbeddingExtractor:
    """임베딩 추출기 테스트"""
    
    @pytest.fixture
    def model(self):
        """테스트 모델 생성"""
        model = SimpleModel(input_channels=3, time_steps=640, embedding_dim=512)
        model.eval()
        return model
    
    @pytest.fixture
    def input_tensor(self):
        """테스트 입력 텐서"""
        return torch.randn(10, 3, 640)
    
    def test_extractor_creation(self, model):
        """추출기 생성"""
        extractor = EmbeddingExtractor(model, device="cpu")
        assert extractor.device == "cpu"
        assert extractor.max_batch_size == 32
    
    def test_extract_single_batch(self, model, input_tensor):
        """단일 배치 추출"""
        extractor = EmbeddingExtractor(model, device="cpu", max_batch_size=10)
        
        embeddings = extractor.extract(input_tensor, return_numpy=False)
        
        assert embeddings.shape == (10, 512)
        assert embeddings.dtype == torch.float32
    
    def test_extract_returns_numpy(self, model, input_tensor):
        """NumPy 배열로 반환"""
        extractor = EmbeddingExtractor(model, device="cpu", max_batch_size=10)
        
        embeddings = extractor.extract(input_tensor, return_numpy=True)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (10, 512)
    
    def test_extract_multiple_batches(self, model):
        """다중 배치 처리"""
        input_tensor = torch.randn(100, 3, 640)
        extractor = EmbeddingExtractor(model, device="cpu", max_batch_size=32)
        
        embeddings = extractor.extract(input_tensor, batch_size=32, return_numpy=False)
        
        assert embeddings.shape == (100, 512)
    
    def test_extract_small_batch(self, model):
        """작은 배치 처리"""
        input_tensor = torch.randn(5, 3, 640)
        extractor = EmbeddingExtractor(model, device="cpu", max_batch_size=32)
        
        embeddings = extractor.extract(input_tensor, return_numpy=True)
        
        assert embeddings.shape == (5, 512)
    
    def test_extract_large_batch(self, model):
        """큰 배치 처리 (자동 분할)"""
        input_tensor = torch.randn(200, 3, 640)
        extractor = EmbeddingExtractor(model, device="cpu", max_batch_size=50)
        
        embeddings = extractor.extract(input_tensor, batch_size=50, return_numpy=True)
        
        assert embeddings.shape == (200, 512)
    
    def test_empty_input_error(self, model):
        """빈 입력 에러"""
        empty_tensor = torch.randn(0, 3, 640)
        extractor = EmbeddingExtractor(model, device="cpu")
        
        with pytest.raises(ValueError):
            extractor.extract(empty_tensor)
    
    def test_batch_info(self, model, input_tensor):
        """배치 정보"""
        extractor = EmbeddingExtractor(model, device="cpu", max_batch_size=32)
        
        info = extractor.extract_batch_info(input_tensor)
        
        assert "num_samples" in info
        assert "batch_size" in info
        assert "num_batches" in info
        assert info["num_samples"] == 10


class TestEmbeddingValidation:
    """임베딩 검증 테스트"""
    
    def test_validate_valid_embeddings(self):
        """유효한 임베딩"""
        embeddings = np.random.randn(10, 512)
        assert validate_embeddings(embeddings)
    
    def test_validate_torch_tensor(self):
        """PyTorch 텐서 검증"""
        embeddings = torch.randn(10, 512)
        assert validate_embeddings(embeddings)
    
    def test_validate_wrong_shape(self):
        """잘못된 shape"""
        embeddings = np.random.randn(10, 256)  # 잘못된 embedding_dim
        with pytest.raises(AssertionError):
            validate_embeddings(embeddings)
    
    def test_validate_with_nan(self):
        """NaN 포함"""
        embeddings = np.random.randn(10, 512)
        embeddings[0, 0] = np.nan
        with pytest.raises(AssertionError):
            validate_embeddings(embeddings)
    
    def test_validate_with_inf(self):
        """Inf 포함"""
        embeddings = np.random.randn(10, 512)
        embeddings[0, 0] = np.inf
        with pytest.raises(AssertionError):
            validate_embeddings(embeddings)
    
    def test_statistics(self):
        """임베딩 통계"""
        embeddings = np.random.randn(100, 512)
        stats = compute_embedding_statistics(embeddings)
        
        assert "shape" in stats
        assert "mean" in stats
        assert "std" in stats
        assert "norm_mean" in stats
        assert stats["shape"] == (100, 512)


class TestExtractEmbeddings:
    """편의 함수 테스트"""
    
    def test_extract_embeddings_function(self):
        """extract_embeddings 함수"""
        model = SimpleModel(input_channels=3, time_steps=640, embedding_dim=512)
        model.eval()
        
        input_tensor = torch.randn(20, 3, 640)
        embeddings = extract_embeddings(
            model,
            input_tensor,
            device="cpu",
            batch_size=10,
            return_numpy=True,
        )
        
        assert embeddings.shape == (20, 512)
        assert isinstance(embeddings, np.ndarray)
    
    def test_extract_with_torch_return(self):
        """PyTorch 텐서로 반환"""
        model = SimpleModel(input_channels=3, time_steps=640, embedding_dim=512)
        model.eval()
        
        input_tensor = torch.randn(20, 3, 640)
        embeddings = extract_embeddings(
            model,
            input_tensor,
            device="cpu",
            return_numpy=False,
        )
        
        assert isinstance(embeddings, torch.Tensor)
        assert embeddings.shape == (20, 512)


class TestPerformance:
    """성능 테스트"""
    
    def test_inference_time_estimate(self):
        """추론 시간 추정"""
        model = SimpleModel(input_channels=3, time_steps=640, embedding_dim=512)
        model.eval()
        
        # 8시간 데이터 @ 128Hz: 3,686,400 샘플 → 5,760 토큰 (5초 윈도우)
        # 테스트: 100 토큰
        input_tensor = torch.randn(100, 3, 640)
        extractor = EmbeddingExtractor(model, device="cpu", max_batch_size=32)
        
        import time
        start = time.time()
        embeddings = extractor.extract(input_tensor, return_numpy=True)
        elapsed = time.time() - start
        
        # 예상: < 1초 (CPU에서 간단한 모델)
        assert elapsed < 10  # 넉넉한 상한
        assert embeddings.shape == (100, 512)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
