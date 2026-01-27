"""
Story 4.2: 질병 위험 예측 API 엔드포인트 (TDD - Red Phase)

Acceptance Criteria:
- POST /api/v1/analyze/disease-risk 엔드포인트 구현
- 응답에 질환별 스코어, 카테고리, 신뢰 구간 포함
- DiseaseRiskScores 테이블에 레코드 저장
- 고위험(High) 질환에 대한 권장사항 반환
- 응답 시간 < 4초
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime


class TestDiseaseRiskEndpoint:
    """질병 위험 예측 API 엔드포인트 테스트"""
    
    def test_endpoint_exists(self, client: TestClient, auth_headers, sample_session):
        """POST /api/v1/analyze/disease-risk 엔드포인트 존재"""
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        # 엔드포인트 존재 확인 (404 Not Found가 아닌 응답)
        assert response.status_code in [200, 400, 422], \
            f"Expected 200/400/422, got {response.status_code}: {response.text}"
    
    def test_requires_authentication(self, client: TestClient):
        """인증 필요"""
        response = client.post(
            "/api/v1/analyze/disease-risk",
            json={"session_id": 1}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_session_id(self, client: TestClient, auth_headers):
        """존재하지 않는 session_id"""
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": 99999}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_missing_session_id(self, client: TestClient, auth_headers):
        """session_id 누락"""
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDiseaseRiskResponse:
    """질병 위험 예측 응답 테스트"""
    
    def test_successful_analysis(self, client: TestClient, auth_headers, sample_session):
        """질병 위험 분석 성공"""
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 기본 응답 구조
        assert "analysis_id" in data
        assert "session_id" in data
        assert "predictions" in data
        assert "created_at" in data
        
        assert data["session_id"] == sample_session.id
    
    def test_response_contains_all_diseases(
        self, client: TestClient, auth_headers, sample_session
    ):
        """응답에 5개 질환 모두 포함"""
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        predictions = data["predictions"]
        assert len(predictions) == 5
        
        expected_diseases = [
            "parkinsons",
            "dementia",
            "myocardial_infarction",
            "heart_failure",
            "stroke",
        ]
        
        disease_names = [p["disease"] for p in predictions]
        for disease in expected_diseases:
            assert disease in disease_names
    
    def test_prediction_structure(
        self, client: TestClient, auth_headers, sample_session
    ):
        """각 질환 예측 구조 검증"""
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for prediction in data["predictions"]:
            # 필수 필드
            assert "disease" in prediction
            assert "disease_name_ko" in prediction  # 한글 질환명
            assert "risk_score" in prediction
            assert "category" in prediction
            assert "confidence_interval" in prediction
            
            # 위험 스코어 범위
            assert 0 <= prediction["risk_score"] <= 100
            
            # 카테고리
            assert prediction["category"] in ["Low", "Medium", "High"]
            
            # 신뢰 구간
            ci = prediction["confidence_interval"]
            assert "lower" in ci
            assert "upper" in ci
            assert ci["lower"] <= prediction["risk_score"] <= ci["upper"]
    
    def test_high_risk_has_recommendations(
        self, client: TestClient, auth_headers, sample_session
    ):
        """고위험 질환에 권장사항 포함"""
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for prediction in data["predictions"]:
            if prediction["category"] == "High":
                assert "recommendations" in prediction
                assert isinstance(prediction["recommendations"], list)
                assert len(prediction["recommendations"]) > 0


class TestDiseaseRiskDatabase:
    """데이터베이스 저장 테스트"""
    
    def test_creates_analysis_record(
        self, client: TestClient, auth_headers, sample_session, db_session
    ):
        """SleepAnalysis 레코드 생성 (analysis_type='disease_risk')"""
        from app.models import SleepAnalysis
        
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # DB에서 레코드 확인
        analysis = db_session.query(SleepAnalysis).filter_by(
            session_id=sample_session.id,
            analysis_type="disease_risk"
        ).first()
        
        assert analysis is not None
        assert analysis.result_data is not None
    
    def test_stores_all_predictions(
        self, client: TestClient, auth_headers, sample_session, db_session
    ):
        """모든 예측 결과 저장"""
        from app.models import SleepAnalysis
        
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        analysis = db_session.query(SleepAnalysis).filter_by(
            session_id=sample_session.id,
            analysis_type="disease_risk"
        ).first()
        
        # result_data에 5개 질환 예측 포함
        assert "predictions" in analysis.result_data
        assert len(analysis.result_data["predictions"]) == 5


class TestDiseaseRiskAuthorization:
    """권한 검증 테스트"""
    
    def test_user_can_only_analyze_own_sessions(
        self, client: TestClient, auth_headers, test_user, db_session
    ):
        """사용자는 자신의 세션만 분석 가능"""
        from app.models import User, SleepSession
        from app.utils.security import hash_password
        
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            username="otheruser",
            full_name="Other User",
            hashed_password=hash_password("password123"),
            is_active=1
        )
        db_session.add(other_user)
        db_session.commit()
        
        # 다른 사용자의 세션 생성
        other_session = SleepSession(
            user_id=other_user.id,
            session_date=datetime(2026, 1, 25, 22, 0, 0),
            duration_hours=8,
            raw_data_path="/fake/path/other.json",
            analysis_status="pending"
        )
        db_session.add(other_session)
        db_session.commit()
        
        # 현재 사용자가 다른 사용자의 세션 분석 시도
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": other_session.id}
        )
        
        # 404 또는 403
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ]


class TestDiseaseRiskPerformance:
    """성능 테스트"""
    
    def test_response_time(self, client: TestClient, auth_headers, sample_session):
        """응답 시간 < 4초"""
        import time
        
        start_time = time.time()
        
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert elapsed_time < 4.0, f"Response time {elapsed_time:.2f}s exceeds 4s limit"


class TestDiseaseNameTranslation:
    """질환명 번역 테스트"""
    
    def test_korean_disease_names(
        self, client: TestClient, auth_headers, sample_session
    ):
        """한글 질환명 포함"""
        response = client.post(
            "/api/v1/analyze/disease-risk",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        expected_korean = {
            "parkinsons": "파킨슨병",
            "dementia": "치매",
            "myocardial_infarction": "심근경색",
            "heart_failure": "심부전",
            "stroke": "뇌졸중",
        }
        
        for prediction in data["predictions"]:
            disease = prediction["disease"]
            assert prediction["disease_name_ko"] == expected_korean[disease]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
