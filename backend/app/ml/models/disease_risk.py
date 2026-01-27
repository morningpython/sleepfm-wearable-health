"""
질병 위험 예측 모델

CoxPH 기반 생존 분석 헤드로 5개 질환 위험 예측:
- 파킨슨병 (Parkinson's Disease)
- 치매 (Dementia)
- 심근경색 (Myocardial Infarction)
- 심부전 (Heart Failure)
- 뇌졸중 (Stroke)
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


# 질환 이름 정의
DISEASE_NAMES = [
    "parkinsons",
    "dementia",
    "myocardial_infarction",
    "heart_failure",
    "stroke",
]

# 한글 질환명 매핑
DISEASE_NAMES_KO = {
    "parkinsons": "파킨슨병",
    "dementia": "치매",
    "myocardial_infarction": "심근경색",
    "heart_failure": "심부전",
    "stroke": "뇌졸중",
}


def categorize_risk(score: float) -> str:
    """
    위험 스코어를 카테고리로 변환
    
    Args:
        score: 위험 스코어 (0-100)
    
    Returns:
        "Low" (< 30), "Medium" (30-60), "High" (> 60)
    """
    if score < 30:
        return "Low"
    elif score <= 60:
        return "Medium"
    else:
        return "High"


def categorize_risk_batch(scores: np.ndarray) -> np.ndarray:
    """
    배치 위험 스코어 카테고리화
    
    Args:
        scores: (batch, num_diseases) 위험 스코어 배열
    
    Returns:
        (batch, num_diseases) 카테고리 배열
    """
    categories = np.empty(scores.shape, dtype=object)
    
    for i in range(scores.shape[0]):
        for j in range(scores.shape[1]):
            categories[i, j] = categorize_risk(scores[i, j])
    
    return categories


class CoxPHHead(nn.Module):
    """
    Cox Proportional Hazards 헤드
    
    단일 질환에 대한 위험 예측 헤드
    """
    
    def __init__(
        self,
        input_dim: int = 512,
        hidden_dim: int = 256,
        dropout: float = 0.3,
    ):
        """
        Args:
            input_dim: 입력 임베딩 차원
            hidden_dim: 은닉층 차원
            dropout: 드롭아웃 비율
        """
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
        )
        
        # 가중치 초기화
        self._init_weights()
    
    def _init_weights(self):
        """가중치 초기화"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: (batch, input_dim) 임베딩
        
        Returns:
            (batch, 1) 헤저드 비율 (양수)
        """
        # 헤저드 비율은 항상 양수 (exp 활성화)
        return torch.exp(self.network(x))


class DiseaseRiskPredictor(nn.Module):
    """
    질병 위험 예측기
    
    5개 질환에 대한 위험 스코어 예측
    """
    
    def __init__(
        self,
        embedding_dim: int = 512,
        num_diseases: int = 5,
        hidden_dim: int = 256,
        dropout: float = 0.3,
    ):
        """
        Args:
            embedding_dim: 입력 임베딩 차원
            num_diseases: 질환 수
            hidden_dim: CoxPH 헤드 은닉층 차원
            dropout: 드롭아웃 비율
        """
        super().__init__()
        
        self.embedding_dim = embedding_dim
        self.num_diseases = num_diseases
        
        # 각 질환별 CoxPH 헤드
        self.disease_heads = nn.ModuleDict({
            disease: CoxPHHead(
                input_dim=embedding_dim,
                hidden_dim=hidden_dim,
                dropout=dropout,
            )
            for disease in DISEASE_NAMES
        })
        
        # 헤저드 → 위험 스코어 변환을 위한 스케일링 파라미터
        # 학습 가능한 파라미터로 설정
        self.scale = nn.Parameter(torch.ones(num_diseases) * 20.0)
        self.bias = nn.Parameter(torch.ones(num_diseases) * 50.0)
        
        logger.info(
            f"DiseaseRiskPredictor initialized: "
            f"embedding_dim={embedding_dim}, num_diseases={num_diseases}"
        )
    
    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        """
        Forward pass - 위험 스코어 예측
        
        Args:
            embeddings: (batch, embedding_dim) 임베딩
        
        Returns:
            (batch, num_diseases) 위험 스코어 (0-100)
        """
        batch_size = embeddings.shape[0]
        device = embeddings.device
        
        # 각 질환별 헤저드 계산
        hazards = []
        for i, disease in enumerate(DISEASE_NAMES):
            hazard = self.disease_heads[disease](embeddings)  # (batch, 1)
            hazards.append(hazard)
        
        # (batch, num_diseases)
        hazards_tensor = torch.cat(hazards, dim=1)
        
        # 헤저드 → 위험 스코어 변환
        # log(hazard)를 정규화하여 0-100 범위로
        log_hazards = torch.log(hazards_tensor + 1e-8)
        
        # 시그모이드로 0-1 범위로 변환 후 100 곱하기
        risk_scores = torch.sigmoid(log_hazards * self.scale + self.bias) * 100
        
        # 0-100 범위로 클램핑
        risk_scores = torch.clamp(risk_scores, 0, 100)
        
        return risk_scores
    
    def predict_with_confidence(
        self,
        embeddings: torch.Tensor,
        confidence_level: float = 0.95,
        num_samples: int = 100,
    ) -> Dict[str, torch.Tensor]:
        """
        신뢰 구간 포함 예측
        
        Monte Carlo Dropout으로 불확실성 추정
        
        Args:
            embeddings: (batch, embedding_dim) 임베딩
            confidence_level: 신뢰 수준 (기본 95%)
            num_samples: MC 샘플 수
        
        Returns:
            {
                "risk_scores": (batch, num_diseases) 평균 위험 스코어,
                "confidence_lower": (batch, num_diseases) 하한,
                "confidence_upper": (batch, num_diseases) 상한,
            }
        """
        # 드롭아웃 활성화를 위해 train 모드 (하지만 그래디언트는 비활성화)
        self.train()
        
        samples = []
        
        with torch.no_grad():
            for _ in range(num_samples):
                scores = self.forward(embeddings)
                samples.append(scores)
        
        # (num_samples, batch, num_diseases)
        samples_tensor = torch.stack(samples, dim=0)
        
        # 통계 계산
        mean_scores = samples_tensor.mean(dim=0)
        
        # 백분위수로 신뢰 구간 계산
        alpha = (1 - confidence_level) / 2
        
        # 정렬 후 백분위수 선택
        sorted_samples, _ = torch.sort(samples_tensor, dim=0)
        lower_idx = int(num_samples * alpha)
        upper_idx = int(num_samples * (1 - alpha)) - 1
        
        confidence_lower = sorted_samples[max(0, lower_idx)]
        confidence_upper = sorted_samples[min(num_samples - 1, upper_idx)]
        
        # 신뢰구간이 평균을 포함하도록 보정
        # lower <= mean <= upper 보장
        confidence_lower = torch.minimum(confidence_lower, mean_scores)
        confidence_upper = torch.maximum(confidence_upper, mean_scores)
        
        # 다시 eval 모드로
        self.eval()
        
        return {
            "risk_scores": mean_scores,
            "confidence_lower": confidence_lower,
            "confidence_upper": confidence_upper,
        }


# 질환별 권장사항
DISEASE_RECOMMENDATIONS = {
    "parkinsons": {
        "Low": [
            "규칙적인 운동을 유지하세요.",
            "충분한 수면을 취하세요.",
        ],
        "Medium": [
            "규칙적인 운동을 유지하세요.",
            "정기적인 신경과 검진을 고려하세요.",
            "손 떨림이나 운동 둔화가 있으면 전문의와 상담하세요.",
        ],
        "High": [
            "신경과 전문의 상담을 강력히 권장합니다.",
            "파킨슨병 조기 진단 검사를 받아보세요.",
            "규칙적인 운동과 균형 잡힌 식단을 유지하세요.",
            "가족력이 있다면 유전 상담을 고려하세요.",
        ],
    },
    "dementia": {
        "Low": [
            "두뇌 활동을 활발히 하세요 (독서, 퍼즐 등).",
            "사회적 활동을 유지하세요.",
        ],
        "Medium": [
            "인지 기능 검사를 정기적으로 받아보세요.",
            "두뇌 건강에 좋은 식단 (지중해식)을 고려하세요.",
            "규칙적인 유산소 운동을 하세요.",
        ],
        "High": [
            "신경과/정신건강의학과 전문의 상담을 권장합니다.",
            "인지 기능 정밀 검사를 받아보세요.",
            "혈관 건강 관리 (혈압, 당뇨, 콜레스테롤)에 신경 쓰세요.",
            "알코올 섭취를 줄이고 금연하세요.",
        ],
    },
    "myocardial_infarction": {
        "Low": [
            "건강한 식습관을 유지하세요.",
            "규칙적인 운동을 하세요.",
        ],
        "Medium": [
            "심혈관 건강 검진을 받아보세요.",
            "혈압과 콜레스테롤 수치를 관리하세요.",
            "스트레스 관리에 신경 쓰세요.",
        ],
        "High": [
            "심장내과 전문의 상담을 강력히 권장합니다.",
            "심장 정밀 검사 (심전도, 운동부하검사, 심장초음파)를 받아보세요.",
            "가슴 통증, 호흡 곤란 증상 시 즉시 응급실을 방문하세요.",
            "금연하고 저염식, 저지방 식단을 유지하세요.",
        ],
    },
    "heart_failure": {
        "Low": [
            "심장 건강에 좋은 운동을 규칙적으로 하세요.",
            "염분 섭취를 적절히 조절하세요.",
        ],
        "Medium": [
            "심장 기능 검사를 고려하세요.",
            "체중 관리에 신경 쓰세요.",
            "붓기나 호흡 곤란이 있으면 전문의와 상담하세요.",
        ],
        "High": [
            "심장내과 전문의 상담을 강력히 권장합니다.",
            "BNP 검사와 심장초음파를 받아보세요.",
            "염분과 수분 섭취를 철저히 관리하세요.",
            "매일 체중을 측정하고 급격한 변화 시 전문의와 상담하세요.",
        ],
    },
    "stroke": {
        "Low": [
            "혈압 관리를 꾸준히 하세요.",
            "규칙적인 운동과 건강한 식단을 유지하세요.",
        ],
        "Medium": [
            "혈관 건강 검진을 받아보세요.",
            "고혈압, 당뇨, 심방세동이 있다면 철저히 관리하세요.",
            "항응고제가 필요한지 전문의와 상담하세요.",
        ],
        "High": [
            "신경과 전문의 상담을 강력히 권장합니다.",
            "경동맥 초음파, 뇌 MRI/MRA 검사를 고려하세요.",
            "FAST 증상 (얼굴 처짐, 팔 약화, 언어 장애, 시간)을 숙지하세요.",
            "혈압, 혈당, 콜레스테롤을 철저히 관리하세요.",
        ],
    },
}


def get_disease_recommendations(disease: str, category: str) -> List[str]:
    """
    질환별 권장사항 반환
    
    Args:
        disease: 질환 이름 (영문)
        category: 위험 카테고리 ("Low", "Medium", "High")
    
    Returns:
        권장사항 목록
    """
    if disease not in DISEASE_RECOMMENDATIONS:
        return []
    
    disease_recs = DISEASE_RECOMMENDATIONS[disease]
    
    if category not in disease_recs:
        return []
    
    return disease_recs[category]
