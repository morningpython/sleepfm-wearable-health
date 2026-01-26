"""
SleepFM 모델 인코더 구현

SleepFM: A Foundation Model for Sleep and Health
- GitHub: https://github.com/selimslab/sleepfm
- Paper: https://arxiv.org/abs/2403.14734
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple
import urllib.request

import torch
import torch.nn as nn
import numpy as np

logger = logging.getLogger(__name__)

# SleepFM 모델 설정
SLEEPFM_CONFIG = {
    "model_name": "sleepfm-emb",
    "input_channels": 3,  # ECG, PPG, Accelerometer
    "embedding_dim": 512,
    "kernel_size": 5,
    "num_layers": 4,
}

# 모델 다운로드 URL (공식 저장소)
MODEL_DOWNLOAD_URL = "https://huggingface.co/selimslab/sleepfm/resolve/main/pytorch_model.bin"
CHECKPOINT_DIR = Path(__file__).parent.parent.parent / "checkpoints"


class SleepFMEncoder(nn.Module):
    """
    SleepFM 기반 인코더 모델
    
    입력: (batch, channels, time_steps)
    - channels: 3 (ECG, PPG, Accelerometer)
    - time_steps: 640 (5초 @ 128Hz)
    
    출력: (batch, embedding_dim)
    - 512 차원 임베딩 벡터
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Args:
            config: 모델 설정 딕셔너리
        """
        super().__init__()
        self.config = config or SLEEPFM_CONFIG
        
        # 입력 검증
        self._validate_config()
        
        # CNN 토크나이저
        self.tokenizer = self._build_tokenizer()
        
        # 트랜스포머 인코더
        self.encoder = self._build_encoder()
        
        # 어텐션 기반 풀링
        self.pool = AttentionPooling(self.config["embedding_dim"])
        
        # 추론 모드 플래그
        self.is_loaded = False
        
    def _validate_config(self):
        """설정 파라미터 검증"""
        required_keys = ["input_channels", "embedding_dim", "kernel_size", "num_layers"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
    
    def _build_tokenizer(self) -> nn.Sequential:
        """CNN 기반 토크나이저 구축"""
        return nn.Sequential(
            nn.Conv1d(
                self.config["input_channels"],
                64,
                kernel_size=self.config["kernel_size"],
                padding=self.config["kernel_size"] // 2,
            ),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(64, 128, kernel_size=self.config["kernel_size"], padding=2),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(128, self.config["embedding_dim"], kernel_size=1),
        )
    
    def _build_encoder(self) -> nn.TransformerEncoder:
        """트랜스포머 인코더 구축"""
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.config["embedding_dim"],
            nhead=8,
            dim_feedforward=1024,
            batch_first=True,
            dropout=0.1,
        )
        return nn.TransformerEncoder(
            encoder_layer,
            num_layers=self.config["num_layers"],
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, channels, time_steps)
        
        Returns:
            (batch, embedding_dim) 임베딩 벡터
        """
        # 토크나이제이션
        tokens = self.tokenizer(x)  # (batch, embedding_dim, time_steps)
        tokens = tokens.transpose(1, 2)  # (batch, time_steps, embedding_dim)
        
        # 트랜스포머 인코딩
        encoded = self.encoder(tokens)  # (batch, time_steps, embedding_dim)
        
        # 어텐션 기반 풀링
        embedding = self.pool(encoded)  # (batch, embedding_dim)
        
        return embedding


class AttentionPooling(nn.Module):
    """
    어텐션 기반 풀링 레이어
    
    시간 차원의 가중치 평균을 계산
    """
    
    def __init__(self, embedding_dim: int):
        super().__init__()
        self.attention = nn.Linear(embedding_dim, 1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, time_steps, embedding_dim)
        
        Returns:
            (batch, embedding_dim)
        """
        # 어텐션 가중치 계산
        weights = self.attention(x)  # (batch, time_steps, 1)
        weights = torch.softmax(weights, dim=1)  # (batch, time_steps, 1)
        
        # 가중치 평균
        pooled = torch.sum(x * weights, dim=1)  # (batch, embedding_dim)
        
        return pooled


def download_model_weights(
    url: str = MODEL_DOWNLOAD_URL,
    output_dir: Optional[Path] = None,
) -> Path:
    """
    SleepFM 모델 가중치 다운로드
    
    Args:
        url: 다운로드 URL
        output_dir: 저장 경로 (기본값: checkpoints/)
    
    Returns:
        저장된 파일 경로
    
    Raises:
        RuntimeError: 다운로드 실패 시
    """
    output_dir = output_dir or CHECKPOINT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "sleepfm_model.bin"
    
    # 이미 존재하면 스킵
    if output_path.exists():
        logger.info(f"Model weights already exist at {output_path}")
        return output_path
    
    try:
        logger.info(f"Downloading SleepFM model from {url}")
        urllib.request.urlretrieve(url, output_path)
        logger.info(f"Model downloaded successfully to {output_path}")
        return output_path
    
    except Exception as e:
        raise RuntimeError(f"Failed to download model weights: {e}")


def load_sleepfm_model(
    checkpoint_path: Optional[str] = None,
    device: Optional[str] = None,
    download_if_missing: bool = True,
) -> Tuple[SleepFMEncoder, str]:
    """
    SleepFM 모델 로드
    
    Args:
        checkpoint_path: 모델 체크포인트 경로 (None이면 기본 경로 사용)
        device: 실행 디바이스 ("cuda" 또는 "cpu")
        download_if_missing: 모델이 없으면 다운로드 여부
    
    Returns:
        (model, device) - 로드된 모델과 사용된 디바이스
    
    Raises:
        FileNotFoundError: 체크포인트 파일이 없을 때
        RuntimeError: 모델 로딩 실패 시
    """
    # 디바이스 결정
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    logger.info(f"Loading SleepFM model on {device}")
    
    # 체크포인트 경로 결정
    if checkpoint_path is None:
        checkpoint_path = CHECKPOINT_DIR / "sleepfm_model.bin"
    else:
        checkpoint_path = Path(checkpoint_path)
    
    # 파일이 없으면 다운로드
    if not checkpoint_path.exists():
        if download_if_missing:
            logger.info(f"Checkpoint not found at {checkpoint_path}, downloading...")
            checkpoint_path = download_model_weights()
        else:
            raise FileNotFoundError(
                f"Model checkpoint not found at {checkpoint_path}. "
                f"Set download_if_missing=True to download automatically."
            )
    
    # 모델 인스턴스 생성
    model = SleepFMEncoder(SLEEPFM_CONFIG)
    
    try:
        # 가중치 로드
        state_dict = torch.load(checkpoint_path, map_location=device)
        
        # 상태 딕셔너리 호환성 처리
        # (경우에 따라 'module.' 접두사가 있을 수 있음)
        if any(k.startswith("module.") for k in state_dict.keys()):
            state_dict = {
                k.replace("module.", ""): v for k, v in state_dict.items()
            }
        
        model.load_state_dict(state_dict, strict=False)
        logger.info("Model weights loaded successfully")
    
    except Exception as e:
        raise RuntimeError(f"Failed to load model weights: {e}")
    
    # 모델을 디바이스로 이동
    model = model.to(device)
    
    # Evaluation 모드 설정
    model.eval()
    logger.info("Model set to evaluation mode")
    
    # 그래디언트 계산 비활성화
    for param in model.parameters():
        param.requires_grad = False
    
    model.is_loaded = True
    
    # GPU 메모리 정보 로깅
    if device == "cuda":
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        allocated = torch.cuda.memory_allocated(0) / 1e9
        logger.info(
            f"GPU Memory: Total={gpu_memory:.2f}GB, "
            f"Allocated={allocated:.2f}GB"
        )
    
    return model, device


def validate_model_io(
    model: SleepFMEncoder,
    device: str,
    batch_size: int = 2,
    num_channels: int = 3,
    time_steps: int = 640,
) -> bool:
    """
    모델의 입출력 shape 검증
    
    Args:
        model: 검증할 모델
        device: 실행 디바이스
        batch_size: 배치 크기
        num_channels: 입력 채널 수 (ECG, PPG, Accelerometer = 3)
        time_steps: 시계열 길이 (5초 @ 128Hz = 640)
    
    Returns:
        검증 성공 여부
    
    Raises:
        AssertionError: 입출력 shape가 예상과 다를 때
    """
    logger.info("Validating model input/output shapes...")
    
    try:
        # 더미 입력 생성
        dummy_input = torch.randn(
            batch_size, num_channels, time_steps, device=device
        )
        
        # Forward pass
        with torch.no_grad():
            output = model(dummy_input)
        
        # 출력 shape 검증
        expected_shape = (batch_size, SLEEPFM_CONFIG["embedding_dim"])
        assert output.shape == expected_shape, (
            f"Output shape mismatch. "
            f"Expected {expected_shape}, got {output.shape}"
        )
        
        logger.info(f"✓ Input shape: {dummy_input.shape}")
        logger.info(f"✓ Output shape: {output.shape}")
        logger.info("✓ Model IO validation passed")
        
        return True
    
    except Exception as e:
        logger.error(f"Model IO validation failed: {e}")
        raise AssertionError(f"Model validation failed: {e}")
