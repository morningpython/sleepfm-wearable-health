"""
Story 2.3 통합 테스트: 전처리 → 임베딩 추출

실제 파이프라인:
1. 원본 신호 (ECG, PPG, Accel) 로드
2. Story 2.2 전처리 파이프라인으로 토큰 생성
3. Story 2.3 임베딩 추출
"""

import pytest
import numpy as np
import torch
from typing import Dict

# 테스트용 모의 객체
from tests.test_story_2_3_embedding import SimpleModel


class TestEndToEndEmbedding:
    """end-to-end 임베딩 추출 테스트"""
    
    @pytest.fixture
    def sample_sensor_data(self) -> Dict[str, np.ndarray]:
        """샘플 센서 데이터 (Story 2.2 입력 형식)"""
        # 10초 데이터 @ 100Hz (임의의 원본 샘플링 레이트)
        n_samples = 1000
        return {
            "ecg": np.random.randn(n_samples) * 100 + 80,      # ECG: ~80 BPM
            "ppg": np.random.randn(n_samples) * 50 + 50,        # PPG: ~50 정도
            "accel": np.random.randn(n_samples, 3) * 10 + 1,    # Accel: 3축
        }
    
    @pytest.fixture
    def preprocessed_tokens(self):
        """전처리된 토큰 (Story 2.2 출력 형식)"""
        # 10개 토큰 (10개의 5초 윈도우)
        # 각 토큰: (3, 640) = 3채널 × 640샘플 @ 128Hz
        return torch.randn(10, 3, 640)
    
    @pytest.fixture
    def model(self):
        """테스트 모델"""
        model = SimpleModel(input_channels=3, time_steps=640, embedding_dim=512)
        model.eval()
        return model
    
    def test_sensor_to_embedding_pipeline(self, sample_sensor_data, model):
        """센서 데이터 → 임베딩 파이프라인"""
        # 이 테스트는 구조만 검증
        # 실제 전처리 코드는 Story 2.2에서 구현됨
        
        # Step 1: 센서 데이터 검증
        assert "ecg" in sample_sensor_data
        assert "ppg" in sample_sensor_data
        assert "accel" in sample_sensor_data
        
        assert sample_sensor_data["ecg"].ndim == 1
        assert sample_sensor_data["ppg"].ndim == 1
        assert sample_sensor_data["accel"].ndim == 2
        assert sample_sensor_data["accel"].shape[1] == 3
    
    def test_tokens_to_embeddings(self, preprocessed_tokens, model):
        """토큰 → 임베딩"""
        from app.ml.embedding_extractor import extract_embeddings
        
        # Step 3: 임베딩 추출 (Story 2.3)
        embeddings = extract_embeddings(
            model,
            preprocessed_tokens,
            device="cpu",
            batch_size=5,
            return_numpy=True,
        )
        
        # 검증
        assert embeddings.shape == (10, 512)
        assert not np.any(np.isnan(embeddings))
        assert not np.any(np.isinf(embeddings))
    
    def test_embedding_statistics(self, preprocessed_tokens, model):
        """임베딩 통계"""
        from app.ml.embedding_extractor import (
            extract_embeddings,
            compute_embedding_statistics,
        )
        
        embeddings = extract_embeddings(
            model,
            preprocessed_tokens,
            device="cpu",
            return_numpy=True,
        )
        
        stats = compute_embedding_statistics(embeddings)
        
        assert "shape" in stats
        assert "mean" in stats
        assert "std" in stats
        assert "norm_mean" in stats
        assert stats["shape"] == (10, 512)


class TestBatchSizeOptimization:
    """배치 크기 최적화 테스트"""
    
    def test_automatic_batch_sizing(self):
        """자동 배치 크기 결정"""
        from app.ml.embedding_extractor import EmbeddingExtractor
        
        model = SimpleModel()
        extractor = EmbeddingExtractor(model, device="cpu", max_batch_size=32)
        
        # 다양한 크기의 입력
        for num_samples in [1, 5, 32, 100, 256]:
            input_tensor = torch.randn(num_samples, 3, 640)
            batch_size = extractor._determine_batch_size(input_tensor)
            assert batch_size > 0
            assert batch_size <= 32


class TestMemoryEfficiency:
    """메모리 효율성 테스트"""
    
    def test_large_batch_processing(self):
        """큰 배치 처리 (메모리 효율적)"""
        from app.ml.embedding_extractor import extract_embeddings
        
        model = SimpleModel()
        model.eval()
        
        # 1000개 토큰 처리
        large_input = torch.randn(1000, 3, 640)
        
        embeddings = extract_embeddings(
            model,
            large_input,
            device="cpu",
            batch_size=64,
            return_numpy=True,
        )
        
        assert embeddings.shape == (1000, 512)
    
    def test_batch_size_override(self):
        """배치 크기 수동 지정"""
        from app.ml.embedding_extractor import EmbeddingExtractor
        
        model = SimpleModel()
        extractor = EmbeddingExtractor(model, device="cpu", max_batch_size=32)
        
        input_tensor = torch.randn(100, 3, 640)
        
        # 명시적 배치 크기
        embeddings = extractor.extract(input_tensor, batch_size=16)
        
        assert embeddings.shape == (100, 512)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
