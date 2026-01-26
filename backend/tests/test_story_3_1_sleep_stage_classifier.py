"""
Tests for Story 3.1: 수면 단계 분류 모델 헤드 구현

Test Coverage:
- SleepStageClassifier 클래스 초기화
- 임베딩 → 5개 클래스 확률 출력
- Softmax 확률 범위 검증 (0-1)
- 출력 shape 검증
- 가장 높은 확률의 단계 선택
- 모델 가중치 저장/로딩
- 배치 처리
- GPU/CPU 호환성
"""

import pytest
import torch
import numpy as np
import tempfile
import os
from pathlib import Path


class TestSleepStageClassifierInitialization:
    """SleepStageClassifier 초기화 테스트"""
    
    def test_classifier_initialization(self):
        """분류기 초기화 - 기본 파라미터"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(
            input_dim=512,
            num_classes=5
        )
        
        assert classifier is not None
        assert classifier.num_classes == 5
        assert classifier.input_dim == 512
    
    def test_classifier_with_hidden_layers(self):
        """분류기 초기화 - hidden layers 지정"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(
            input_dim=512,
            num_classes=5,
            hidden_dim=256,
            num_layers=2
        )
        
        assert classifier.hidden_dim == 256
        assert classifier.num_layers == 2
    
    def test_classifier_dropout(self):
        """분류기 초기화 - dropout 지정"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(
            input_dim=512,
            num_classes=5,
            dropout=0.3
        )
        
        assert classifier.dropout == 0.3


class TestSleepStageClassifierForward:
    """SleepStageClassifier forward pass 테스트"""
    
    def test_forward_single_embedding(self):
        """단일 임베딩 입력 → 5개 클래스 확률"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        
        # 단일 임베딩 (512차원)
        embedding = torch.randn(1, 512)
        
        with torch.no_grad():
            output = classifier(embedding)
        
        assert output.shape == (1, 5)
        assert torch.all(output >= 0.0)
        assert torch.all(output <= 1.0)
        # 각 샘플의 확률 합은 1
        assert torch.allclose(output.sum(dim=1), torch.ones(1), atol=1e-5)
    
    def test_forward_batch_embeddings(self):
        """배치 임베딩 입력 → 배치 확률 출력"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        
        # 배치 임베딩 (32 샘플)
        batch_embeddings = torch.randn(32, 512)
        
        with torch.no_grad():
            output = classifier(batch_embeddings)
        
        assert output.shape == (32, 5)
        assert torch.all(output >= 0.0)
        assert torch.all(output <= 1.0)
        assert torch.allclose(output.sum(dim=1), torch.ones(32), atol=1e-5)
    
    def test_forward_large_batch(self):
        """큰 배치 처리 (960 에포크 = 8시간)"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        
        # 8시간 = 960개 30초 에포크
        large_batch = torch.randn(960, 512)
        
        with torch.no_grad():
            output = classifier(large_batch)
        
        assert output.shape == (960, 5)
        assert torch.all(output >= 0.0)
        assert torch.all(output <= 1.0)


class TestSleepStagePrediction:
    """수면 단계 예측 테스트"""
    
    def test_predict_sleep_stages(self):
        """가장 높은 확률의 단계 선택"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        
        embeddings = torch.randn(10, 512)
        
        with torch.no_grad():
            predictions = classifier.predict(embeddings)
        
        # 예측은 0-4 범위의 정수
        assert predictions.shape == (10,)
        assert torch.all(predictions >= 0)
        assert torch.all(predictions < 5)
        assert predictions.dtype == torch.long
    
    def test_predict_with_probabilities(self):
        """확률과 함께 예측 반환"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        
        embeddings = torch.randn(10, 512)
        
        with torch.no_grad():
            predictions, probabilities = classifier.predict(embeddings, return_probs=True)
        
        assert predictions.shape == (10,)
        assert probabilities.shape == (10, 5)
        
        # 예측된 클래스의 확률이 가장 높아야 함
        max_probs, max_indices = probabilities.max(dim=1)
        assert torch.all(max_indices == predictions)


class TestSleepStageClassMapping:
    """수면 단계 클래스 매핑 테스트"""
    
    def test_class_names(self):
        """클래스 이름 매핑"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        
        expected_classes = ["Wake", "N1", "N2", "N3", "REM"]
        assert classifier.class_names == expected_classes
    
    def test_get_stage_name(self):
        """클래스 인덱스 → 이름 변환"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        
        assert classifier.get_stage_name(0) == "Wake"
        assert classifier.get_stage_name(1) == "N1"
        assert classifier.get_stage_name(2) == "N2"
        assert classifier.get_stage_name(3) == "N3"
        assert classifier.get_stage_name(4) == "REM"
    
    def test_predict_with_names(self):
        """예측 결과를 이름으로 반환"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        
        embeddings = torch.randn(10, 512)
        
        with torch.no_grad():
            stage_names = classifier.predict_names(embeddings)
        
        assert len(stage_names) == 10
        assert all(name in ["Wake", "N1", "N2", "N3", "REM"] for name in stage_names)


class TestModelSaveLoad:
    """모델 저장/로딩 테스트"""
    
    def test_save_model(self):
        """모델 가중치 저장"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "classifier.pth"
            classifier.save(save_path)
            
            assert save_path.exists()
    
    def test_load_model(self):
        """모델 가중치 로딩"""
        from app.ml.models.heads import SleepStageClassifier
        
        # 원본 모델 생성 및 저장
        classifier1 = SleepStageClassifier(input_dim=512, num_classes=5)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "classifier.pth"
            classifier1.save(save_path)
            
            # 새 모델 생성 후 로딩
            classifier2 = SleepStageClassifier(input_dim=512, num_classes=5)
            classifier2.load(save_path)
            
            # 동일한 입력에 대해 동일한 출력
            test_input = torch.randn(5, 512)
            
            classifier1.eval()
            classifier2.eval()
            
            with torch.no_grad():
                output1 = classifier1(test_input)
                output2 = classifier2(test_input)
            
            assert torch.allclose(output1, output2, atol=1e-5)


class TestDeviceCompatibility:
    """GPU/CPU 호환성 테스트"""
    
    def test_cpu_inference(self):
        """CPU 추론"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        
        embeddings = torch.randn(10, 512)
        
        with torch.no_grad():
            output = classifier(embeddings)
        
        assert output.device.type == "cpu"
        assert output.shape == (10, 5)
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_gpu_inference(self):
        """GPU 추론"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        classifier.to("cuda")
        
        embeddings = torch.randn(10, 512).to("cuda")
        
        with torch.no_grad():
            output = classifier(embeddings)
        
        assert output.device.type == "cuda"
        assert output.shape == (10, 5)


class TestEdgeCases:
    """엣지 케이스 테스트"""
    
    def test_single_epoch(self):
        """단일 에포크 예측"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        
        single_embedding = torch.randn(1, 512)
        
        with torch.no_grad():
            prediction = classifier.predict(single_embedding)
        
        assert prediction.shape == (1,)
        assert 0 <= prediction.item() < 5
    
    def test_zero_embedding(self):
        """제로 임베딩 입력"""
        from app.ml.models.heads import SleepStageClassifier
        
        classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        classifier.eval()
        
        zero_embedding = torch.zeros(1, 512)
        
        with torch.no_grad():
            output = classifier(zero_embedding)
        
        # 여전히 유효한 확률 분포
        assert output.shape == (1, 5)
        assert torch.all(output >= 0.0)
        assert torch.all(output <= 1.0)
        assert torch.allclose(output.sum(), torch.tensor(1.0), atol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
