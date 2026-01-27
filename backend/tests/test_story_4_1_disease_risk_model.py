"""
Story 4.1: 질병 위험 예측 모델 헤드 구현 (TDD - Red Phase)

Acceptance Criteria:
- 각 질환별 C-Index ≥ 0.75 (공개 데이터셋)
- 위험 스코어 범위: 0-100
- 95% 신뢰 구간 계산
- 5개 질환 동시 예측 가능
- 추론 시간 < 3초

5개 질환:
- 파킨슨병 (Parkinson's Disease)
- 치매 (Dementia)
- 심근경색 (Myocardial Infarction)
- 심부전 (Heart Failure)
- 뇌졸중 (Stroke)
"""

import pytest
import numpy as np
import torch
import time
from typing import Dict, List


# ==================== Disease Risk Predictor 테스트 ====================

class TestDiseaseRiskPredictor:
    """질병 위험 예측기 테스트"""
    
    def test_predictor_creation(self):
        """예측기 생성"""
        from app.ml.models.disease_risk import DiseaseRiskPredictor
        
        predictor = DiseaseRiskPredictor(
            embedding_dim=512,
            num_diseases=5,
        )
        
        assert predictor is not None
        assert predictor.embedding_dim == 512
        assert predictor.num_diseases == 5
    
    def test_predictor_disease_names(self):
        """5개 질환 이름 확인"""
        from app.ml.models.disease_risk import DiseaseRiskPredictor, DISEASE_NAMES
        
        expected_diseases = [
            "parkinsons",
            "dementia",
            "myocardial_infarction",
            "heart_failure",
            "stroke",
        ]
        
        assert len(DISEASE_NAMES) == 5
        for disease in expected_diseases:
            assert disease in DISEASE_NAMES
    
    def test_predictor_forward_pass(self):
        """Forward pass 테스트"""
        from app.ml.models.disease_risk import DiseaseRiskPredictor
        
        predictor = DiseaseRiskPredictor(
            embedding_dim=512,
            num_diseases=5,
        )
        predictor.eval()
        
        # 임베딩 입력 (batch=4, embedding_dim=512)
        embeddings = torch.randn(4, 512)
        
        with torch.no_grad():
            output = predictor(embeddings)
        
        # 출력: (batch, num_diseases) 위험 스코어
        assert output.shape == (4, 5)
    
    def test_risk_score_range(self):
        """위험 스코어 범위 검증 (0-100)"""
        from app.ml.models.disease_risk import DiseaseRiskPredictor
        
        predictor = DiseaseRiskPredictor(
            embedding_dim=512,
            num_diseases=5,
        )
        predictor.eval()
        
        embeddings = torch.randn(10, 512)
        
        with torch.no_grad():
            scores = predictor(embeddings)
        
        # 모든 스코어가 0-100 범위
        assert torch.all(scores >= 0), "Scores should be >= 0"
        assert torch.all(scores <= 100), "Scores should be <= 100"
    
    def test_predict_with_confidence(self):
        """신뢰 구간 포함 예측"""
        from app.ml.models.disease_risk import DiseaseRiskPredictor
        
        predictor = DiseaseRiskPredictor(
            embedding_dim=512,
            num_diseases=5,
        )
        predictor.eval()
        
        embeddings = torch.randn(4, 512)
        
        with torch.no_grad():
            result = predictor.predict_with_confidence(
                embeddings, 
                confidence_level=0.95
            )
        
        # 결과 구조 검증
        assert "risk_scores" in result
        assert "confidence_lower" in result
        assert "confidence_upper" in result
        
        # Shape 검증
        assert result["risk_scores"].shape == (4, 5)
        assert result["confidence_lower"].shape == (4, 5)
        assert result["confidence_upper"].shape == (4, 5)
        
        # 신뢰 구간 관계 검증 (lower <= score <= upper)
        assert torch.all(result["confidence_lower"] <= result["risk_scores"])
        assert torch.all(result["risk_scores"] <= result["confidence_upper"])


class TestDiseaseCategories:
    """질병 위험도 카테고리 테스트"""
    
    def test_categorize_risk_low(self):
        """Low 카테고리 (< 30)"""
        from app.ml.models.disease_risk import categorize_risk
        
        assert categorize_risk(0) == "Low"
        assert categorize_risk(15) == "Low"
        assert categorize_risk(29.9) == "Low"
    
    def test_categorize_risk_medium(self):
        """Medium 카테고리 (30-60)"""
        from app.ml.models.disease_risk import categorize_risk
        
        assert categorize_risk(30) == "Medium"
        assert categorize_risk(45) == "Medium"
        assert categorize_risk(60) == "Medium"
    
    def test_categorize_risk_high(self):
        """High 카테고리 (> 60)"""
        from app.ml.models.disease_risk import categorize_risk
        
        assert categorize_risk(60.1) == "High"
        assert categorize_risk(75) == "High"
        assert categorize_risk(100) == "High"
    
    def test_batch_categorization(self):
        """배치 카테고리화"""
        from app.ml.models.disease_risk import categorize_risk_batch
        
        scores = np.array([
            [10, 35, 70, 25, 55],  # Low, Medium, High, Low, Medium
            [80, 5, 45, 90, 30],   # High, Low, Medium, High, Medium
        ])
        
        categories = categorize_risk_batch(scores)
        
        assert categories.shape == (2, 5)
        assert categories[0, 0] == "Low"
        assert categories[0, 1] == "Medium"
        assert categories[0, 2] == "High"
        assert categories[1, 0] == "High"
        assert categories[1, 1] == "Low"


class TestCoxPHHead:
    """Cox Proportional Hazards 헤드 테스트"""
    
    def test_coxph_head_creation(self):
        """CoxPH 헤드 생성"""
        from app.ml.models.disease_risk import CoxPHHead
        
        head = CoxPHHead(
            input_dim=512,
            hidden_dim=256,
        )
        
        assert head is not None
        assert head.input_dim == 512
        assert head.hidden_dim == 256
    
    def test_coxph_head_forward(self):
        """CoxPH 헤드 forward pass"""
        from app.ml.models.disease_risk import CoxPHHead
        
        head = CoxPHHead(
            input_dim=512,
            hidden_dim=256,
        )
        head.eval()
        
        embeddings = torch.randn(8, 512)
        
        with torch.no_grad():
            hazard = head(embeddings)
        
        # 출력: (batch, 1) - 각 질환별 헤드
        assert hazard.shape == (8, 1)
    
    def test_coxph_hazard_positive(self):
        """CoxPH 헤저드는 양수"""
        from app.ml.models.disease_risk import CoxPHHead
        
        head = CoxPHHead(
            input_dim=512,
            hidden_dim=256,
        )
        head.eval()
        
        embeddings = torch.randn(100, 512)
        
        with torch.no_grad():
            hazard = head(embeddings)
        
        # 헤저드는 항상 양수 (exp 활성화)
        assert torch.all(hazard > 0)


class TestDiseaseRiskInference:
    """질병 위험 추론 테스트"""
    
    def test_inference_time(self):
        """추론 시간 < 3초"""
        from app.ml.models.disease_risk import DiseaseRiskPredictor
        
        predictor = DiseaseRiskPredictor(
            embedding_dim=512,
            num_diseases=5,
        )
        predictor.eval()
        
        # 8시간 수면 데이터 기준 (약 5760개 토큰)
        # 평균 임베딩 사용 시 batch=1
        embeddings = torch.randn(1, 512)
        
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(10):  # 10회 추론
                _ = predictor.predict_with_confidence(embeddings)
        
        avg_time = (time.time() - start_time) / 10
        
        assert avg_time < 3.0, f"Inference time {avg_time:.2f}s exceeds 3s limit"
    
    def test_batch_inference(self):
        """배치 추론"""
        from app.ml.models.disease_risk import DiseaseRiskPredictor
        
        predictor = DiseaseRiskPredictor(
            embedding_dim=512,
            num_diseases=5,
        )
        predictor.eval()
        
        # 다양한 배치 크기
        for batch_size in [1, 4, 16, 32]:
            embeddings = torch.randn(batch_size, 512)
            
            with torch.no_grad():
                result = predictor.predict_with_confidence(embeddings)
            
            assert result["risk_scores"].shape == (batch_size, 5)


class TestDiseaseRecommendations:
    """질병별 권장사항 테스트"""
    
    def test_get_recommendations_high_risk(self):
        """고위험 질환 권장사항"""
        from app.ml.models.disease_risk import get_disease_recommendations
        
        # 고위험 파킨슨병
        recommendations = get_disease_recommendations(
            disease="parkinsons",
            category="High",
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(r, str) for r in recommendations)
    
    def test_get_recommendations_all_diseases(self):
        """모든 질환 권장사항 존재"""
        from app.ml.models.disease_risk import (
            get_disease_recommendations,
            DISEASE_NAMES,
        )
        
        for disease in DISEASE_NAMES:
            for category in ["Low", "Medium", "High"]:
                recommendations = get_disease_recommendations(
                    disease=disease,
                    category=category,
                )
                
                assert isinstance(recommendations, list)
                # High 카테고리는 반드시 권장사항 있어야 함
                if category == "High":
                    assert len(recommendations) > 0


class TestDiseaseRiskAnalyzer:
    """질병 위험 분석기 통합 테스트"""
    
    def test_analyzer_creation(self):
        """분석기 생성"""
        from app.ml.analysis.disease_risk_analyzer import DiseaseRiskAnalyzer
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        encoder = SleepFMEncoder()
        analyzer = DiseaseRiskAnalyzer(
            encoder=encoder,
            device="cpu",
        )
        
        assert analyzer is not None
    
    def test_analyze_from_embeddings(self):
        """임베딩으로부터 분석"""
        from app.ml.analysis.disease_risk_analyzer import DiseaseRiskAnalyzer
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        encoder = SleepFMEncoder()
        analyzer = DiseaseRiskAnalyzer(
            encoder=encoder,
            device="cpu",
        )
        
        # 평균 임베딩
        embeddings = np.random.randn(512).astype(np.float32)
        
        result = analyzer.analyze(embeddings)
        
        # 결과 구조
        assert "predictions" in result
        assert len(result["predictions"]) == 5  # 5개 질환
        
        for disease_result in result["predictions"]:
            assert "disease" in disease_result
            assert "risk_score" in disease_result
            assert "category" in disease_result
            assert "confidence_interval" in disease_result
            assert "recommendations" in disease_result
            
            # 범위 검증
            assert 0 <= disease_result["risk_score"] <= 100
            assert disease_result["category"] in ["Low", "Medium", "High"]
    
    def test_analyze_end_to_end(self):
        """엔드-투-엔드 분석 (센서 데이터 → 위험 예측)"""
        from app.ml.analysis.disease_risk_analyzer import DiseaseRiskAnalyzer
        from app.ml.sleepfm_encoder import SleepFMEncoder
        
        encoder = SleepFMEncoder()
        analyzer = DiseaseRiskAnalyzer(
            encoder=encoder,
            device="cpu",
        )
        
        # 합성 센서 데이터 (3채널, 1분)
        sensor_data = {
            "ecg": np.random.randn(6400).astype(np.float32),      # 1분 @ 100Hz → 128Hz
            "ppg": np.random.randn(6400).astype(np.float32),
            "accel": np.random.randn(6400, 3).astype(np.float32),
        }
        
        result = analyzer.analyze_from_sensor_data(
            sensor_data=sensor_data,
            original_fs=100,
        )
        
        assert "predictions" in result
        assert len(result["predictions"]) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
