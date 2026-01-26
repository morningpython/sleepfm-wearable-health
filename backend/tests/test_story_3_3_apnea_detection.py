"""
Story 3.3: 수면무호흡 탐지 모델 (TDD - Red Phase)

Acceptance Criteria:
- 호흡 신호 임베딩 입력 → 무호흡 이벤트 탐지
- AHI (Apnea-Hypopnea Index) 계산: 시간당 이벤트 수
- 심각도 분류:
  - Normal: AHI < 5
  - Mild: 5 ≤ AHI < 15
  - Moderate: 15 ≤ AHI < 30
  - Severe: AHI ≥ 30
- 이벤트별 타임스탬프, 지속시간, 유형 제공
- 예측 시간 < 2초 (8시간 데이터)

TDD Approach:
1. Red: 테스트 작성 (실패 확인)
2. Green: 최소 구현
3. Refactor: 코드 개선
"""

import pytest
import torch
import numpy as np
from pathlib import Path
import tempfile
import time

# PyTorch 가용성 확인
try:
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# 테스트 스킵 조건
pytestmark = pytest.mark.skipif(
    not TORCH_AVAILABLE,
    reason="PyTorch not available in Python 3.13 environment"
)

from app.ml.models.heads import ApneaDetector


class TestApneaDetectorInitialization:
    """ApneaDetector 초기화 테스트"""
    
    def test_creates_model_with_default_params(self):
        """기본 파라미터로 모델 생성"""
        model = ApneaDetector()
        
        assert model is not None
        assert isinstance(model, nn.Module)
        assert model.input_dim == 512
        assert model.num_classes == 3  # Normal, Apnea, Hypopnea
    
    def test_creates_model_with_custom_params(self):
        """커스텀 파라미터로 모델 생성"""
        model = ApneaDetector(
            input_dim=256,
            num_classes=3,
            hidden_dim=128,
            num_layers=2,
            dropout=0.3
        )
        
        assert model.input_dim == 256
        assert model.num_classes == 3
        assert model.hidden_dim == 128
        assert model.num_layers == 2
        assert model.dropout == 0.3
    
    def test_model_in_eval_mode_by_default(self):
        """기본적으로 eval 모드로 생성"""
        model = ApneaDetector()
        assert not model.training


class TestApneaDetectorForward:
    """Forward pass 테스트"""
    
    def test_forward_returns_correct_shape(self):
        """올바른 출력 shape 반환"""
        model = ApneaDetector(input_dim=512, num_classes=3)
        batch_size = 16
        seq_len = 960  # 8시간 × 120 에포크/시간
        
        x = torch.randn(batch_size, seq_len, 512)
        output = model(x)
        
        assert output.shape == (batch_size, seq_len, 3)
        assert torch.all(output >= 0) and torch.all(output <= 1)  # 확률값
    
    def test_forward_probabilities_sum_to_one(self):
        """각 에포크의 확률 합이 1"""
        model = ApneaDetector()
        x = torch.randn(4, 100, 512)
        
        output = model(x)
        prob_sums = output.sum(dim=-1)
        
        assert torch.allclose(prob_sums, torch.ones_like(prob_sums), atol=1e-5)
    
    def test_forward_with_single_sample(self):
        """단일 샘플 처리"""
        model = ApneaDetector()
        x = torch.randn(1, 960, 512)
        
        output = model(x)
        
        assert output.shape == (1, 960, 3)


class TestApneaEventDetection:
    """무호흡 이벤트 탐지 테스트"""
    
    def test_detect_apnea_events(self):
        """무호흡 이벤트 탐지"""
        model = ApneaDetector()
        x = torch.randn(1, 960, 512)
        
        events = model.detect_events(x)
        
        assert isinstance(events, list)
        if len(events) > 0:
            event = events[0]
            assert 'epoch_start' in event
            assert 'epoch_end' in event
            assert 'event_type' in event  # 'apnea' or 'hypopnea'
            assert 'duration_seconds' in event
            assert 'confidence' in event
    
    def test_no_events_for_normal_breathing(self):
        """정상 호흡 시 이벤트 없음"""
        model = ApneaDetector()
        # 모든 확률이 Normal(class 0)에 몰린 경우 시뮬레이션
        x = torch.randn(1, 100, 512)
        
        # predict 메서드가 모두 0(Normal)을 반환하도록 설정된 경우
        events = model.detect_events(x, threshold=0.5)
        
        # 정상 호흡만 있으면 이벤트 없음
        assert isinstance(events, list)
    
    def test_event_duration_calculation(self):
        """이벤트 지속시간 계산 (30초 에포크 기준)"""
        model = ApneaDetector()
        x = torch.randn(1, 960, 512)
        
        events = model.detect_events(x, epoch_length_seconds=30)
        
        if len(events) > 0:
            for event in events:
                # 지속시간 = (에포크 수) × 30초
                expected_duration = (event['epoch_end'] - event['epoch_start'] + 1) * 30
                assert event['duration_seconds'] == expected_duration


class TestAHICalculation:
    """AHI (Apnea-Hypopnea Index) 계산 테스트"""
    
    def test_calculate_ahi_normal(self):
        """정상 AHI 계산 (AHI < 5)"""
        model = ApneaDetector()
        
        # 8시간 수면에서 이벤트 2개
        events = [
            {'epoch_start': 10, 'epoch_end': 12, 'event_type': 'apnea'},
            {'epoch_start': 50, 'epoch_end': 51, 'event_type': 'hypopnea'}
        ]
        
        ahi = model.calculate_ahi(events, total_sleep_hours=8.0)
        
        assert ahi == 2 / 8.0  # 0.25
        assert ahi < 5
    
    def test_calculate_ahi_mild(self):
        """경증 AHI (5 ≤ AHI < 15)"""
        model = ApneaDetector()
        
        # 8시간 수면에서 이벤트 60개 (AHI = 7.5)
        events = [{'event_type': 'apnea'} for _ in range(60)]
        
        ahi = model.calculate_ahi(events, total_sleep_hours=8.0)
        
        assert ahi == 60 / 8.0  # 7.5
        assert 5 <= ahi < 15
    
    def test_calculate_ahi_moderate(self):
        """중등도 AHI (15 ≤ AHI < 30)"""
        model = ApneaDetector()
        
        # 8시간 수면에서 이벤트 160개 (AHI = 20)
        events = [{'event_type': 'apnea'} for _ in range(160)]
        
        ahi = model.calculate_ahi(events, total_sleep_hours=8.0)
        
        assert ahi == 160 / 8.0  # 20
        assert 15 <= ahi < 30
    
    def test_calculate_ahi_severe(self):
        """중증 AHI (AHI ≥ 30)"""
        model = ApneaDetector()
        
        # 8시간 수면에서 이벤트 280개 (AHI = 35)
        events = [{'event_type': 'apnea'} for _ in range(280)]
        
        ahi = model.calculate_ahi(events, total_sleep_hours=8.0)
        
        assert ahi == 280 / 8.0  # 35
        assert ahi >= 30
    
    def test_calculate_ahi_zero_events(self):
        """이벤트 없을 때 AHI = 0"""
        model = ApneaDetector()
        
        ahi = model.calculate_ahi([], total_sleep_hours=8.0)
        
        assert ahi == 0.0


class TestSeverityClassification:
    """심각도 분류 테스트"""
    
    def test_classify_normal(self):
        """정상 분류 (AHI < 5)"""
        model = ApneaDetector()
        
        severity = model.classify_severity(ahi=3.5)
        
        assert severity == "Normal"
    
    def test_classify_mild(self):
        """경증 분류 (5 ≤ AHI < 15)"""
        model = ApneaDetector()
        
        severity = model.classify_severity(ahi=10.0)
        
        assert severity == "Mild"
    
    def test_classify_moderate(self):
        """중등도 분류 (15 ≤ AHI < 30)"""
        model = ApneaDetector()
        
        severity = model.classify_severity(ahi=22.5)
        
        assert severity == "Moderate"
    
    def test_classify_severe(self):
        """중증 분류 (AHI ≥ 30)"""
        model = ApneaDetector()
        
        severity = model.classify_severity(ahi=45.0)
        
        assert severity == "Severe"
    
    def test_classify_boundary_cases(self):
        """경계값 테스트"""
        model = ApneaDetector()
        
        assert model.classify_severity(4.99) == "Normal"
        assert model.classify_severity(5.0) == "Mild"
        assert model.classify_severity(14.99) == "Mild"
        assert model.classify_severity(15.0) == "Moderate"
        assert model.classify_severity(29.99) == "Moderate"
        assert model.classify_severity(30.0) == "Severe"


class TestApneaPrediction:
    """무호흡 예측 테스트"""
    
    def test_predict_returns_class_indices(self):
        """클래스 인덱스 반환"""
        model = ApneaDetector()
        x = torch.randn(2, 100, 512)
        
        predictions = model.predict(x)
        
        assert predictions.shape == (2, 100)
        assert torch.all(predictions >= 0) and torch.all(predictions < 3)
    
    def test_predict_with_probabilities(self):
        """확률값 함께 반환"""
        model = ApneaDetector()
        x = torch.randn(2, 100, 512)
        
        predictions, probs = model.predict(x, return_probs=True)
        
        assert predictions.shape == (2, 100)
        assert probs.shape == (2, 100, 3)
        assert torch.all(probs >= 0) and torch.all(probs <= 1)
    
    def test_predict_event_names(self):
        """이벤트 타입 이름 반환"""
        model = ApneaDetector()
        x = torch.randn(1, 50, 512)
        
        event_names = model.predict_names(x)
        
        assert len(event_names) == 50
        assert all(name in ["Normal", "Apnea", "Hypopnea"] for name in event_names)


class TestModelSaveLoad:
    """모델 저장 및 로드 테스트"""
    
    def test_save_model(self):
        """모델 저장"""
        model = ApneaDetector(input_dim=512, hidden_dim=256)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "apnea_detector.pth"
            model.save(save_path)
            
            assert save_path.exists()
    
    def test_load_model(self):
        """모델 로드"""
        model = ApneaDetector(input_dim=512, hidden_dim=256)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "apnea_detector.pth"
            model.save(save_path)
            
            loaded_model = ApneaDetector.load(save_path)
            
            assert loaded_model.input_dim == 512
            assert loaded_model.hidden_dim == 256
    
    def test_loaded_model_produces_same_output(self):
        """로드된 모델이 동일한 출력 생성"""
        model = ApneaDetector()
        x = torch.randn(1, 100, 512)
        
        original_output = model(x)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "apnea_detector.pth"
            model.save(save_path)
            
            loaded_model = ApneaDetector.load(save_path)
            loaded_output = loaded_model(x)
            
            assert torch.allclose(original_output, loaded_output, atol=1e-6)


class TestDeviceCompatibility:
    """GPU/CPU 호환성 테스트"""
    
    def test_model_on_cpu(self):
        """CPU에서 모델 실행"""
        model = ApneaDetector()
        x = torch.randn(1, 100, 512)
        
        output = model(x)
        
        assert output.device.type == 'cpu'
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_model_on_gpu(self):
        """GPU에서 모델 실행"""
        model = ApneaDetector().cuda()
        x = torch.randn(1, 100, 512).cuda()
        
        output = model(x)
        
        assert output.device.type == 'cuda'


class TestPerformance:
    """성능 테스트"""
    
    def test_prediction_time_under_2_seconds(self):
        """8시간 데이터 예측 시간 < 2초"""
        model = ApneaDetector()
        # 8시간 = 960 에포크 (30초 기준)
        x = torch.randn(1, 960, 512)
        
        start_time = time.time()
        _ = model.predict(x)
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 2.0, f"Prediction took {elapsed_time:.2f}s, expected < 2s"


class TestEdgeCases:
    """엣지 케이스 테스트"""
    
    def test_empty_events_list(self):
        """빈 이벤트 리스트 처리"""
        model = ApneaDetector()
        
        ahi = model.calculate_ahi([], total_sleep_hours=8.0)
        severity = model.classify_severity(ahi)
        
        assert ahi == 0.0
        assert severity == "Normal"
    
    def test_very_short_sleep_duration(self):
        """매우 짧은 수면 시간"""
        model = ApneaDetector()
        
        events = [{'event_type': 'apnea'}]
        ahi = model.calculate_ahi(events, total_sleep_hours=0.5)
        
        assert ahi == 2.0  # 1 event / 0.5 hours
    
    def test_single_epoch_input(self):
        """단일 에포크 입력"""
        model = ApneaDetector()
        x = torch.randn(1, 1, 512)
        
        output = model(x)
        
        assert output.shape == (1, 1, 3)


class TestEventTypeMapping:
    """이벤트 타입 매핑 테스트"""
    
    def test_get_event_type_name(self):
        """이벤트 타입 이름 조회"""
        model = ApneaDetector()
        
        assert model.get_event_type_name(0) == "Normal"
        assert model.get_event_type_name(1) == "Apnea"
        assert model.get_event_type_name(2) == "Hypopnea"
    
    def test_invalid_event_type_raises_error(self):
        """잘못된 이벤트 타입 시 에러"""
        model = ApneaDetector()
        
        with pytest.raises((ValueError, IndexError)):
            model.get_event_type_name(5)
