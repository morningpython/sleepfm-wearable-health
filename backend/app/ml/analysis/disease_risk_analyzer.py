"""
질병 위험 분석기

SleepFM 임베딩을 사용하여 5개 질환 위험 예측
"""

import numpy as np
import torch
import logging
from typing import Dict, List, Optional, Union

from app.ml.models.disease_risk import (
    DiseaseRiskPredictor,
    DISEASE_NAMES,
    DISEASE_NAMES_KO,
    categorize_risk,
    get_disease_recommendations,
)

logger = logging.getLogger(__name__)


class DiseaseRiskAnalyzer:
    """
    질병 위험 분석기
    
    센서 데이터 또는 임베딩으로부터 질병 위험 예측
    """
    
    def __init__(
        self,
        encoder: torch.nn.Module,
        device: str = "cpu",
        predictor: Optional[DiseaseRiskPredictor] = None,
    ):
        """
        Args:
            encoder: SleepFM 인코더
            device: 실행 디바이스
            predictor: 질병 위험 예측기 (None이면 자동 생성)
        """
        self.encoder = encoder.to(device)
        self.encoder.eval()
        self.device = device
        
        if predictor is None:
            self.predictor = DiseaseRiskPredictor(
                embedding_dim=512,
                num_diseases=5,
            )
        else:
            self.predictor = predictor
        
        self.predictor = self.predictor.to(device)
        self.predictor.eval()
        
        logger.info(f"DiseaseRiskAnalyzer initialized: device={device}")
    
    def analyze(
        self,
        embeddings: Union[np.ndarray, torch.Tensor],
        confidence_level: float = 0.95,
    ) -> Dict:
        """
        임베딩으로부터 질병 위험 분석
        
        Args:
            embeddings: (embedding_dim,) 또는 (batch, embedding_dim) 임베딩
            confidence_level: 신뢰 수준
        
        Returns:
            {
                "predictions": [
                    {
                        "disease": "parkinsons",
                        "disease_name_ko": "파킨슨병",
                        "risk_score": 35.2,
                        "category": "Medium",
                        "confidence_interval": {"lower": 28.1, "upper": 42.3},
                        "recommendations": [...],
                    },
                    ...
                ]
            }
        """
        # numpy → tensor 변환
        if isinstance(embeddings, np.ndarray):
            embeddings = torch.from_numpy(embeddings).float()
        
        # 1D → 2D
        if embeddings.ndim == 1:
            embeddings = embeddings.unsqueeze(0)
        
        embeddings = embeddings.to(self.device)
        
        # 예측
        with torch.no_grad():
            result = self.predictor.predict_with_confidence(
                embeddings,
                confidence_level=confidence_level,
            )
        
        # 결과 파싱
        risk_scores = result["risk_scores"].cpu().numpy()
        conf_lower = result["confidence_lower"].cpu().numpy()
        conf_upper = result["confidence_upper"].cpu().numpy()
        
        # 첫 번째 배치만 사용 (단일 세션)
        predictions = []
        
        for i, disease in enumerate(DISEASE_NAMES):
            score = float(risk_scores[0, i])
            category = categorize_risk(score)
            
            prediction = {
                "disease": disease,
                "disease_name_ko": DISEASE_NAMES_KO[disease],
                "risk_score": round(score, 1),
                "category": category,
                "confidence_interval": {
                    "lower": round(float(conf_lower[0, i]), 1),
                    "upper": round(float(conf_upper[0, i]), 1),
                },
                "recommendations": get_disease_recommendations(disease, category),
            }
            
            predictions.append(prediction)
        
        return {"predictions": predictions}
    
    def analyze_from_sensor_data(
        self,
        sensor_data: Dict[str, np.ndarray],
        original_fs: float,
        confidence_level: float = 0.95,
    ) -> Dict:
        """
        센서 데이터로부터 질병 위험 분석
        
        Args:
            sensor_data: {"ecg": ..., "ppg": ..., "accel": ...}
            original_fs: 원본 샘플링 레이트
            confidence_level: 신뢰 수준
        
        Returns:
            분석 결과 딕셔너리
        """
        from app.preprocessing import create_default_pipeline
        
        # 전처리
        pipeline = create_default_pipeline(device=self.device)
        preprocessed = pipeline.process(sensor_data, original_fs)
        
        # 임베딩 추출
        tokens_tensor = preprocessed["tensor"].to(self.device)
        
        with torch.no_grad():
            # 각 토큰의 임베딩
            embeddings = self.encoder(tokens_tensor)  # (num_tokens, 512)
            
            # 평균 임베딩 사용
            mean_embedding = embeddings.mean(dim=0, keepdim=True)
        
        # 분석
        return self.analyze(
            mean_embedding,
            confidence_level=confidence_level,
        )
