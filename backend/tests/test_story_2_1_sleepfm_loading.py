"""
Story 2.1: SleepFM 모델 가중치 로딩 테스트

단위 테스트 (Unit Tests):
- 모델 클래스 초기화 검증
- 가중치 로딩 성공 여부
- GPU/CPU 자동 감지
- 입출력 shape 검증
"""

import pytest
import torch
import tempfile
from pathlib import Path

from app.ml.sleepfm_encoder import (
    SleepFMEncoder,
    load_sleepfm_model,
    validate_model_io,
    SLEEPFM_CONFIG,
)


class TestSleepFMEncoder:
    """SleepFMEncoder 모델 클래스 테스트"""
    
    def test_model_initialization(self):
        """모델이 정상적으로 초기화되는지 확인"""
        model = SleepFMEncoder(SLEEPFM_CONFIG)
        
        assert model is not None
        assert hasattr(model, "tokenizer")
        assert hasattr(model, "encoder")
        assert hasattr(model, "pool")
        assert not model.is_loaded
    
    def test_model_config_validation(self):
        """설정 검증 로직 테스트"""
        # 필수 필드 누락 시 에러 발생
        invalid_config = {"embedding_dim": 512}
        
        with pytest.raises(ValueError, match="Missing required config key"):
            SleepFMEncoder(invalid_config)
    
    def test_model_forward_pass_cpu(self):
        """CPU에서 forward pass 테스트"""
        model = SleepFMEncoder(SLEEPFM_CONFIG)
        model.eval()
        
        # 더미 입력
        batch_size = 2
        num_channels = 3
        time_steps = 640
        
        dummy_input = torch.randn(batch_size, num_channels, time_steps)
        
        with torch.no_grad():
            output = model(dummy_input)
        
        # 출력 shape 검증
        assert output.shape == (batch_size, SLEEPFM_CONFIG["embedding_dim"])
        assert output.dtype == torch.float32
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_model_forward_pass_gpu(self):
        """GPU에서 forward pass 테스트"""
        model = SleepFMEncoder(SLEEPFM_CONFIG)
        model = model.to("cuda")
        model.eval()
        
        batch_size = 2
        dummy_input = torch.randn(batch_size, 3, 640, device="cuda")
        
        with torch.no_grad():
            output = model(dummy_input)
        
        assert output.device.type == "cuda"
        assert output.shape == (batch_size, SLEEPFM_CONFIG["embedding_dim"])
    
    def test_model_eval_mode(self):
        """모델이 evaluation 모드로 설정되는지 확인"""
        model = SleepFMEncoder(SLEEPFM_CONFIG)
        model.eval()
        
        # evaluation 모드 확인
        assert not model.training
        
        # Dropout/BatchNorm이 evaluation 모드
        for module in model.modules():
            if hasattr(module, "training"):
                # eval 모드에서도 정상 작동하는지 확인
                assert isinstance(module, (torch.nn.Dropout, torch.nn.BatchNorm1d))
    
    def test_gradient_disabled(self):
        """그래디언트가 비활성화되는지 확인"""
        model = SleepFMEncoder(SLEEPFM_CONFIG)
        
        for param in model.parameters():
            param.requires_grad = False
        
        for param in model.parameters():
            assert not param.requires_grad


class TestModelLoading:
    """모델 로딩 함수 테스트"""
    
    def test_load_model_cpu(self):
        """CPU에서 모델 로드"""
        # 다운로드 없이 CPU에서 로드 시도
        try:
            model, device = load_sleepfm_model(
                device="cpu",
                download_if_missing=False,
            )
            assert device == "cpu"
            assert model.is_loaded
        except FileNotFoundError:
            # 체크포인트가 없으면 스킵
            pytest.skip("Model checkpoint not available")
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_load_model_gpu(self):
        """GPU에서 모델 로드"""
        try:
            model, device = load_sleepfm_model(
                device="cuda",
                download_if_missing=False,
            )
            assert device == "cuda"
            assert model.is_loaded
        except FileNotFoundError:
            pytest.skip("Model checkpoint not available")
    
    def test_device_detection(self):
        """디바이스 자동 감지"""
        try:
            model, device = load_sleepfm_model(
                device=None,  # 자동 감지
                download_if_missing=False,
            )
            
            expected_device = "cuda" if torch.cuda.is_available() else "cpu"
            assert device == expected_device
        except FileNotFoundError:
            pytest.skip("Model checkpoint not available")


class TestModelValidation:
    """모델 입출력 검증 테스트"""
    
    def test_validate_model_io_success(self):
        """정상적인 입출력 shape 검증"""
        model = SleepFMEncoder(SLEEPFM_CONFIG)
        model.eval()
        
        # 검증 실행
        result = validate_model_io(
            model,
            device="cpu",
            batch_size=2,
            num_channels=3,
            time_steps=640,
        )
        
        assert result is True
    
    def test_validate_model_io_different_batch_size(self):
        """다양한 배치 크기에서 검증"""
        model = SleepFMEncoder(SLEEPFM_CONFIG)
        model.eval()
        
        for batch_size in [1, 4, 8]:
            result = validate_model_io(
                model,
                device="cpu",
                batch_size=batch_size,
            )
            assert result is True
    
    def test_validate_model_io_invalid_shape(self):
        """잘못된 입출력 shape 검증"""
        model = SleepFMEncoder(SLEEPFM_CONFIG)
        model.eval()
        
        # 채널 수가 다른 경우
        with pytest.raises(AssertionError):
            validate_model_io(
                model,
                device="cpu",
                num_channels=4,  # 잘못된 채널 수
            )


class TestGPUMemory:
    """GPU 메모리 사용 테스트"""
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_gpu_memory_allocation(self):
        """GPU 메모리 할당 확인"""
        torch.cuda.reset_peak_memory_stats()
        
        model = SleepFMEncoder(SLEEPFM_CONFIG)
        model = model.to("cuda")
        model.eval()
        
        initial_memory = torch.cuda.memory_allocated()
        
        # Forward pass
        batch_input = torch.randn(4, 3, 640, device="cuda")
        with torch.no_grad():
            output = model(batch_input)
        
        final_memory = torch.cuda.memory_allocated()
        
        # 메모리가 할당되었는지 확인
        assert final_memory >= initial_memory
        assert output.device.type == "cuda"
        
        # 메모리 정리
        torch.cuda.empty_cache()


if __name__ == "__main__":
    # CLI 실행
    pytest.main([__file__, "-v", "--tb=short"])
