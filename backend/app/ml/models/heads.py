"""
수면 단계 분류 모델 헤드 구현

Story 3.1: Sleep Stage Classifier
- Linear 기반 분류 헤드
- 5개 클래스: Wake, N1, N2, N3, REM
- Softmax 확률 출력
- 모델 저장/로딩
"""

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available. SleepStageClassifier will not function.")

from typing import List, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SleepStageClassifier(nn.Module if TORCH_AVAILABLE else object):
    """
    수면 단계 분류 모델 헤드
    
    임베딩 벡터를 입력받아 5개 수면 단계로 분류합니다.
    - Wake (0)
    - N1 (1)
    - N2 (2)
    - N3 (3)
    - REM (4)
    
    Args:
        input_dim: 입력 임베딩 차원 (기본: 512)
        num_classes: 클래스 수 (기본: 5)
        hidden_dim: 히든 레이어 차원 (기본: 256)
        num_layers: 히든 레이어 수 (기본: 1)
        dropout: 드롭아웃 비율 (기본: 0.2)
    
    Examples:
        >>> classifier = SleepStageClassifier(input_dim=512, num_classes=5)
        >>> embeddings = torch.randn(32, 512)  # 배치 32개
        >>> probabilities = classifier(embeddings)
        >>> predictions = classifier.predict(embeddings)
    """
    
    def __init__(
        self,
        input_dim: int = 512,
        num_classes: int = 5,
        hidden_dim: int = 256,
        num_layers: int = 1,
        dropout: float = 0.2,
    ):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for SleepStageClassifier")
        
        super().__init__()
        
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        
        # 클래스 이름 매핑
        self.class_names = ["Wake", "N1", "N2", "N3", "REM"]
        
        # 분류 헤드 구성
        layers = []
        
        if num_layers == 1:
            # 단일 레이어: 직접 분류
            layers.append(nn.Linear(input_dim, num_classes))
        else:
            # 다층 구조
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            
            for _ in range(num_layers - 2):
                layers.append(nn.Linear(hidden_dim, hidden_dim))
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(dropout))
            
            layers.append(nn.Linear(hidden_dim, num_classes))
        
        self.classifier = nn.Sequential(*layers)
        
        logger.info(
            f"Initialized SleepStageClassifier: "
            f"input_dim={input_dim}, num_classes={num_classes}, "
            f"hidden_dim={hidden_dim}, num_layers={num_layers}"
        )
    
    def forward(self, x: "torch.Tensor") -> "torch.Tensor":
        """
        Forward pass
        
        Args:
            x: 입력 임베딩 (batch_size, input_dim)
        
        Returns:
            확률 분포 (batch_size, num_classes)
        """
        logits = self.classifier(x)
        probabilities = F.softmax(logits, dim=1)
        return probabilities
    
    def predict(
        self,
        x: "torch.Tensor",
        return_probs: bool = False
    ) -> Tuple["torch.Tensor", Optional["torch.Tensor"]]:
        """
        수면 단계 예측
        
        Args:
            x: 입력 임베딩 (batch_size, input_dim)
            return_probs: 확률도 함께 반환할지 여부
        
        Returns:
            predictions: 예측된 클래스 인덱스 (batch_size,)
            probabilities: 확률 분포 (batch_size, num_classes) - return_probs=True일 때만
        
        Examples:
            >>> predictions = classifier.predict(embeddings)
            >>> predictions, probs = classifier.predict(embeddings, return_probs=True)
        """
        probabilities = self.forward(x)
        predictions = torch.argmax(probabilities, dim=1)
        
        if return_probs:
            return predictions, probabilities
        else:
            return predictions
    
    def predict_names(self, x: "torch.Tensor") -> List[str]:
        """
        수면 단계 예측 (이름으로 반환)
        
        Args:
            x: 입력 임베딩 (batch_size, input_dim)
        
        Returns:
            stage_names: 예측된 수면 단계 이름 리스트
        
        Examples:
            >>> names = classifier.predict_names(embeddings)
            >>> print(names)
            ['N2', 'N3', 'N3', 'REM', 'Wake', ...]
        """
        predictions = self.predict(x)
        stage_names = [self.get_stage_name(pred.item()) for pred in predictions]
        return stage_names
    
    def get_stage_name(self, class_idx: int) -> str:
        """
        클래스 인덱스를 수면 단계 이름으로 변환
        
        Args:
            class_idx: 클래스 인덱스 (0-4)
        
        Returns:
            stage_name: 수면 단계 이름
        """
        if 0 <= class_idx < len(self.class_names):
            return self.class_names[class_idx]
        else:
            raise ValueError(f"Invalid class index: {class_idx}")
    
    def save(self, path: Path):
        """
        모델 가중치 저장
        
        Args:
            path: 저장 경로
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), path)
        logger.info(f"Model saved to {path}")
    
    def load(self, path: Path):
        """
        모델 가중치 로딩
        
        Args:
            path: 로딩 경로
        """
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        state_dict = torch.load(path, map_location="cpu")
        self.load_state_dict(state_dict)
        logger.info(f"Model loaded from {path}")
