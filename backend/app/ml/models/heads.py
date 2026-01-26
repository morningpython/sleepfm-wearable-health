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


class ApneaDetector(nn.Module if TORCH_AVAILABLE else object):
    """
    수면무호흡 탐지 모델
    
    호흡 신호 임베딩을 입력받아 무호흡/저호흡 이벤트를 탐지합니다.
    - Normal (0): 정상 호흡
    - Apnea (1): 무호흡
    - Hypopnea (2): 저호흡
    
    AHI (Apnea-Hypopnea Index) 계산 및 심각도 분류:
    - Normal: AHI < 5
    - Mild: 5 ≤ AHI < 15
    - Moderate: 15 ≤ AHI < 30
    - Severe: AHI ≥ 30
    
    Args:
        input_dim: 입력 임베딩 차원 (기본: 512)
        num_classes: 클래스 수 (기본: 3)
        hidden_dim: 히든 레이어 차원 (기본: 256)
        num_layers: 히든 레이어 수 (기본: 1)
        dropout: 드롭아웃 비율 (기본: 0.2)
    """
    
    EVENT_TYPES = ["Normal", "Apnea", "Hypopnea"]
    
    def __init__(
        self,
        input_dim: int = 512,
        num_classes: int = 3,
        hidden_dim: int = 256,
        num_layers: int = 1,
        dropout: float = 0.2
    ):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for ApneaDetector")
        
        super().__init__()
        
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        
        # 분류 헤드 구성
        if num_layers == 1:
            # Linear 단일 레이어
            self.classifier = nn.Linear(input_dim, num_classes)
        else:
            # MLP 다층 구조
            layers = []
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            
            for _ in range(num_layers - 2):
                layers.append(nn.Linear(hidden_dim, hidden_dim))
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(dropout))
            
            layers.append(nn.Linear(hidden_dim, num_classes))
            self.classifier = nn.Sequential(*layers)
        
        self.eval()
        logger.info(f"ApneaDetector initialized: input_dim={input_dim}, num_classes={num_classes}")
    
    def forward(self, x: 'torch.Tensor') -> 'torch.Tensor':
        """
        Forward pass
        
        Args:
            x: (batch, seq_len, input_dim) 임베딩 텐서
            
        Returns:
            (batch, seq_len, num_classes) 확률값 텐서
        """
        logits = self.classifier(x)
        probabilities = F.softmax(logits, dim=-1)
        return probabilities
    
    def predict(
        self,
        x: 'torch.Tensor',
        return_probs: bool = False
    ) -> 'torch.Tensor':
        """
        클래스 예측
        
        Args:
            x: (batch, seq_len, input_dim) 임베딩 텐서
            return_probs: 확률값도 함께 반환할지 여부
            
        Returns:
            predictions: (batch, seq_len) 클래스 인덱스
            probabilities: (batch, seq_len, num_classes) 확률값 (return_probs=True인 경우)
        """
        with torch.no_grad():
            probabilities = self(x)
            predictions = torch.argmax(probabilities, dim=-1)
        
        if return_probs:
            return predictions, probabilities
        return predictions
    
    def predict_names(self, x: 'torch.Tensor') -> List[str]:
        """
        이벤트 타입 이름으로 예측
        
        Args:
            x: (1, seq_len, input_dim) 임베딩 텐서 (배치 크기 1)
            
        Returns:
            이벤트 타입 이름 리스트
        """
        predictions = self.predict(x)
        predictions = predictions.squeeze(0).cpu().numpy()  # (seq_len,)
        
        return [self.EVENT_TYPES[idx] for idx in predictions]
    
    def detect_events(
        self,
        x: 'torch.Tensor',
        threshold: float = 0.5,
        epoch_length_seconds: int = 30
    ) -> List[dict]:
        """
        무호흡/저호흡 이벤트 탐지
        
        Args:
            x: (1, seq_len, input_dim) 임베딩 텐서
            threshold: 이벤트 탐지 임계값 (기본: 0.5)
            epoch_length_seconds: 에포크 길이 (초, 기본: 30)
            
        Returns:
            이벤트 리스트, 각 이벤트는 다음 정보 포함:
            - epoch_start: 시작 에포크 번호
            - epoch_end: 종료 에포크 번호
            - event_type: 'apnea' or 'hypopnea'
            - duration_seconds: 지속 시간 (초)
            - confidence: 평균 확률값
        """
        predictions, probs = self.predict(x, return_probs=True)
        predictions = predictions.squeeze(0).cpu().numpy()  # (seq_len,)
        probs = probs.squeeze(0).cpu().numpy()  # (seq_len, num_classes)
        
        events = []
        current_event = None
        
        for epoch_idx in range(len(predictions)):
            pred_class = predictions[epoch_idx]
            confidence = probs[epoch_idx][pred_class]
            
            # Normal이 아니고 임계값 이상인 경우
            if pred_class != 0 and confidence >= threshold:
                event_type = "apnea" if pred_class == 1 else "hypopnea"
                
                if current_event is None:
                    # 새 이벤트 시작
                    current_event = {
                        'epoch_start': epoch_idx,
                        'epoch_end': epoch_idx,
                        'event_type': event_type,
                        'confidences': [confidence]
                    }
                elif current_event['event_type'] == event_type:
                    # 같은 타입의 이벤트 계속
                    current_event['epoch_end'] = epoch_idx
                    current_event['confidences'].append(confidence)
                else:
                    # 다른 타입의 이벤트 → 현재 이벤트 종료, 새 이벤트 시작
                    self._finalize_event(current_event, epoch_length_seconds, events)
                    current_event = {
                        'epoch_start': epoch_idx,
                        'epoch_end': epoch_idx,
                        'event_type': event_type,
                        'confidences': [confidence]
                    }
            else:
                # Normal → 이벤트 종료
                if current_event is not None:
                    self._finalize_event(current_event, epoch_length_seconds, events)
                    current_event = None
        
        # 마지막 이벤트 처리
        if current_event is not None:
            self._finalize_event(current_event, epoch_length_seconds, events)
        
        return events
    
    def _finalize_event(
        self,
        event: dict,
        epoch_length_seconds: int,
        events_list: List[dict]
    ):
        """이벤트 최종화 및 리스트에 추가"""
        num_epochs = event['epoch_end'] - event['epoch_start'] + 1
        event['duration_seconds'] = num_epochs * epoch_length_seconds
        event['confidence'] = sum(event['confidences']) / len(event['confidences'])
        del event['confidences']
        events_list.append(event)
    
    def calculate_ahi(
        self,
        events: List[dict],
        total_sleep_hours: float
    ) -> float:
        """
        AHI (Apnea-Hypopnea Index) 계산
        
        Args:
            events: detect_events()로 탐지된 이벤트 리스트
            total_sleep_hours: 총 수면 시간 (시간)
            
        Returns:
            AHI 값 (시간당 이벤트 수)
        """
        if total_sleep_hours <= 0:
            raise ValueError("Total sleep hours must be positive")
        
        num_events = len(events)
        ahi = num_events / total_sleep_hours
        
        return ahi
    
    def classify_severity(self, ahi: float) -> str:
        """
        AHI 기반 심각도 분류
        
        Args:
            ahi: AHI 값
            
        Returns:
            심각도: "Normal", "Mild", "Moderate", "Severe"
        """
        if ahi < 5:
            return "Normal"
        elif ahi < 15:
            return "Mild"
        elif ahi < 30:
            return "Moderate"
        else:
            return "Severe"
    
    def get_event_type_name(self, class_idx: int) -> str:
        """
        클래스 인덱스 → 이벤트 타입 이름
        
        Args:
            class_idx: 클래스 인덱스 (0, 1, 2)
            
        Returns:
            이벤트 타입 이름
        """
        if class_idx < 0 or class_idx >= self.num_classes:
            raise ValueError(f"Invalid class index: {class_idx}")
        
        return self.EVENT_TYPES[class_idx]
    
    def save(self, path: Path):
        """모델 가중치 저장"""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 모델 상태와 설정 함께 저장
        checkpoint = {
            'state_dict': self.state_dict(),
            'input_dim': self.input_dim,
            'num_classes': self.num_classes,
            'hidden_dim': self.hidden_dim,
            'num_layers': self.num_layers,
            'dropout': self.dropout
        }
        
        torch.save(checkpoint, path)
        logger.info(f"ApneaDetector saved to {path}")
    
    @classmethod
    def load(cls, path: Path) -> 'ApneaDetector':
        """모델 로딩 (클래스 메서드)"""
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        checkpoint = torch.load(path, map_location="cpu")
        
        # 설정으로 모델 생성
        model = cls(
            input_dim=checkpoint['input_dim'],
            num_classes=checkpoint['num_classes'],
            hidden_dim=checkpoint['hidden_dim'],
            num_layers=checkpoint['num_layers'],
            dropout=checkpoint['dropout']
        )
        
        # 가중치 로딩
        model.load_state_dict(checkpoint['state_dict'])
        logger.info(f"ApneaDetector loaded from {path}")
        
        return model
