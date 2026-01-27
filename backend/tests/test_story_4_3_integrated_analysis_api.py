"""
Story 4.3: 통합 분석 API 엔드포인트 (TDD - Red Phase)

Acceptance Criteria:
- POST /api/v1/analyze 엔드포인트 구현
- 응답에 수면 요약, 수면 단계, 무호흡, 질병 위험 모두 포함
- 총 분석 시간 < 15초 (8시간 데이터)
- 분석 실패 시 부분 결과라도 반환
- 분석 상태 조회 가능 (GET /api/v1/analyze/{session_id}/status)
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime
import time


class TestIntegratedAnalysisEndpoint:
    """통합 분석 API 엔드포인트 테스트"""
    
    def test_endpoint_exists(self, client: TestClient, auth_headers, sample_session):
        """POST /api/v1/analyze 엔드포인트 존재"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code in [200, 400, 422], \
            f"Expected 200/400/422, got {response.status_code}: {response.text}"
    
    def test_requires_authentication(self, client: TestClient):
        """인증 필요"""
        response = client.post(
            "/api/v1/analyze",
            json={"session_id": 1}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_session_id(self, client: TestClient, auth_headers):
        """존재하지 않는 session_id"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": 99999}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_missing_session_id(self, client: TestClient, auth_headers):
        """session_id 누락"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestIntegratedAnalysisResponse:
    """통합 분석 응답 테스트"""
    
    def test_successful_analysis(self, client: TestClient, auth_headers, sample_session):
        """통합 분석 성공"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 기본 응답 구조
        assert "session_id" in data
        assert "analysis_status" in data
        assert "created_at" in data
        
        assert data["session_id"] == sample_session.id
        assert data["analysis_status"] == "completed"
    
    def test_contains_all_analysis_types(
        self, client: TestClient, auth_headers, sample_session
    ):
        """모든 분석 유형 포함"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 4가지 분석 결과 포함
        assert "sleep_summary" in data
        assert "sleep_stages" in data
        assert "apnea" in data
        assert "disease_risk" in data
    
    def test_sleep_summary_structure(
        self, client: TestClient, auth_headers, sample_session
    ):
        """수면 요약 구조 검증"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        summary = data["sleep_summary"]
        
        assert "total_time_minutes" in summary
        assert "total_sleep_time_minutes" in summary
        assert "sleep_efficiency" in summary
        assert "sleep_onset_latency" in summary
        assert "wake_after_sleep_onset" in summary
        
        # 수면 효율성 범위
        assert 0 <= summary["sleep_efficiency"] <= 100
    
    def test_sleep_stages_structure(
        self, client: TestClient, auth_headers, sample_session
    ):
        """수면 단계 구조 검증"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        stages = data["sleep_stages"]
        
        assert "stages" in stages
        assert "stage_durations" in stages
        
        # 단계별 시간
        durations = stages["stage_durations"]
        assert "Wake" in durations
        assert "N1" in durations
        assert "N2" in durations
        assert "N3" in durations
        assert "REM" in durations
    
    def test_apnea_structure(
        self, client: TestClient, auth_headers, sample_session
    ):
        """무호흡 분석 구조 검증"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        apnea = data["apnea"]
        
        assert "ahi" in apnea
        assert "severity" in apnea
        assert "event_count" in apnea
        
        assert apnea["ahi"] >= 0
        assert apnea["severity"] in ["Normal", "Mild", "Moderate", "Severe"]
    
    def test_disease_risk_structure(
        self, client: TestClient, auth_headers, sample_session
    ):
        """질병 위험 구조 검증"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        disease_risk = data["disease_risk"]
        
        assert "predictions" in disease_risk
        assert len(disease_risk["predictions"]) == 5


class TestIntegratedAnalysisPartialFailure:
    """부분 실패 테스트"""
    
    def test_partial_results_on_failure(
        self, client: TestClient, auth_headers, sample_session
    ):
        """일부 분석 실패 시에도 부분 결과 반환"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        # 성공하든 부분 실패하든 응답 있어야 함
        assert response.status_code in [200, 207]  # 207 = Multi-Status
        data = response.json()
        
        # 메타데이터는 항상 포함
        assert "session_id" in data
        assert "analysis_status" in data
        
        # 부분 실패 시 에러 정보 포함
        if data["analysis_status"] == "partial":
            assert "errors" in data


class TestAnalysisStatusEndpoint:
    """분석 상태 조회 엔드포인트 테스트"""
    
    def test_status_endpoint_exists(
        self, client: TestClient, auth_headers, sample_session
    ):
        """GET /api/v1/analyze/{session_id}/status 존재"""
        response = client.get(
            f"/api/v1/analyze/{sample_session.id}/status",
            headers=auth_headers,
        )
        
        assert response.status_code in [200, 404], \
            f"Expected 200/404, got {response.status_code}"
    
    def test_status_requires_auth(self, client: TestClient, sample_session):
        """상태 조회 인증 필요"""
        response = client.get(
            f"/api/v1/analyze/{sample_session.id}/status",
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_status_response_structure(
        self, client: TestClient, auth_headers, sample_session
    ):
        """상태 응답 구조"""
        # 먼저 분석 실행
        client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        # 상태 조회
        response = client.get(
            f"/api/v1/analyze/{sample_session.id}/status",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "session_id" in data
        assert "status" in data
        assert "completed_analyses" in data
        
        # 상태 값
        assert data["status"] in ["pending", "processing", "completed", "failed", "partial"]
    
    def test_status_shows_completed_analyses(
        self, client: TestClient, auth_headers, sample_session
    ):
        """완료된 분석 유형 표시"""
        # 분석 실행
        client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        # 상태 조회
        response = client.get(
            f"/api/v1/analyze/{sample_session.id}/status",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        completed = data["completed_analyses"]
        
        # 성공 시 모든 분석 유형 포함 (DB에는 sleep_stage로 저장됨)
        if data["status"] == "completed":
            assert "sleep_stage" in completed
            assert "apnea" in completed
            assert "disease_risk" in completed


class TestIntegratedAnalysisPerformance:
    """성능 테스트"""
    
    def test_analysis_time_limit(
        self, client: TestClient, auth_headers, sample_session
    ):
        """총 분석 시간 < 15초"""
        start_time = time.time()
        
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert elapsed_time < 15.0, f"Analysis time {elapsed_time:.2f}s exceeds 15s limit"


class TestIntegratedAnalysisDatabase:
    """데이터베이스 통합 테스트"""
    
    def test_creates_multiple_analysis_records(
        self, client: TestClient, auth_headers, sample_session, db_session
    ):
        """여러 분석 레코드 생성"""
        from app.models import SleepAnalysis
        
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # 여러 분석 유형 레코드 확인
        analyses = db_session.query(SleepAnalysis).filter_by(
            session_id=sample_session.id
        ).all()
        
        analysis_types = [a.analysis_type for a in analyses]
        
        assert "sleep_stage" in analysis_types
        assert "apnea" in analysis_types
        assert "disease_risk" in analysis_types
    
    def test_updates_session_status(
        self, client: TestClient, auth_headers, sample_session, db_session
    ):
        """세션 상태 업데이트"""
        from app.models import SleepSession
        
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # 세션 상태 확인
        db_session.refresh(sample_session)
        
        assert sample_session.analysis_status in ["completed", "partial"]


class TestAnalysisOptions:
    """분석 옵션 테스트"""
    
    def test_selective_analysis(
        self, client: TestClient, auth_headers, sample_session
    ):
        """선택적 분석 (특정 분석만 실행)"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={
                "session_id": sample_session.id,
                "analysis_types": ["sleep_stages", "apnea"]  # disease_risk 제외
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 요청한 분석만 포함
        assert "sleep_stages" in data
        assert "apnea" in data
        # disease_risk는 요청하지 않았으므로 없거나 null
    
    def test_full_analysis_by_default(
        self, client: TestClient, auth_headers, sample_session
    ):
        """기본값: 전체 분석"""
        response = client.post(
            "/api/v1/analyze",
            headers=auth_headers,
            json={"session_id": sample_session.id}
            # analysis_types 미지정
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 모든 분석 포함
        assert "sleep_summary" in data
        assert "sleep_stages" in data
        assert "apnea" in data
        assert "disease_risk" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
