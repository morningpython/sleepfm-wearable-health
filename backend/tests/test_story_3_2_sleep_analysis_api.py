"""
Tests for Story 3.2: 수면 단계 분석 API 엔드포인트

Test Coverage:
- POST /api/v1/analyze/sleep-stages 엔드포인트
- 세션 ID로 센서 데이터 조회
- 수면 단계 분석 실행
- 결과 DB 저장
- 수면 효율성 계산
- 에포크별 수면 단계 반환
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import numpy as np


class TestSleepStageAnalysisEndpoint:
    """수면 단계 분석 API 엔드포인트 테스트"""
    
    def test_analyze_sleep_stages_endpoint_exists(self, client: TestClient, auth_headers):
        """POST /api/v1/analyze/sleep-stages 엔드포인트 존재"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": 1}
        )
        
        # 404가 아니어야 함 (엔드포인트 존재)
        assert response.status_code != 404
    
    def test_analyze_sleep_stages_requires_auth(self, client: TestClient):
        """인증 없이 접근 불가"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            json={"session_id": 1}
        )
        
        assert response.status_code == 401
    
    def test_analyze_sleep_stages_invalid_session_id(self, client: TestClient, auth_headers):
        """존재하지 않는 세션 ID"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": 99999}
        )
        
        assert response.status_code == 404
        assert "session" in response.json()["detail"].lower()
    
    def test_analyze_sleep_stages_missing_session_id(self, client: TestClient, auth_headers):
        """session_id 누락"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 422


class TestSleepStageAnalysisExecution:
    """수면 단계 분석 실행 테스트"""
    
    def test_analyze_sleep_stages_success(
        self, client: TestClient, auth_headers, sample_session
    ):
        """수면 단계 분석 성공"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 기본 응답 구조
        assert "analysis_id" in data
        assert "session_id" in data
        assert "stages" in data
        assert "summary" in data
        assert "created_at" in data
    
    def test_analyze_sleep_stages_returns_epoch_stages(
        self, client: TestClient, auth_headers, sample_session
    ):
        """에포크별 수면 단계 배열 반환"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        stages = data["stages"]
        assert isinstance(stages, list)
        assert len(stages) > 0
        
        # 각 에포크는 stage와 probability 포함
        for epoch in stages:
            assert "epoch_number" in epoch
            assert "stage" in epoch
            assert "stage_name" in epoch
            assert "probability" in epoch
            
            # 유효한 수면 단계
            assert epoch["stage"] in [0, 1, 2, 3, 4]
            assert epoch["stage_name"] in ["Wake", "N1", "N2", "N3", "REM"]
            
            # 확률 범위
            assert 0.0 <= epoch["probability"] <= 1.0
    
    def test_analyze_sleep_stages_returns_summary(
        self, client: TestClient, auth_headers, sample_session
    ):
        """수면 효율성 및 단계별 시간 요약"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        summary = data["summary"]
        
        # 수면 효율성
        assert "sleep_efficiency" in summary
        assert 0.0 <= summary["sleep_efficiency"] <= 100.0
        
        # 총 시간
        assert "total_time_minutes" in summary
        assert "total_sleep_time_minutes" in summary
        
        # 단계별 시간
        assert "stage_durations" in summary
        durations = summary["stage_durations"]
        
        assert "Wake" in durations
        assert "N1" in durations
        assert "N2" in durations
        assert "N3" in durations
        assert "REM" in durations
        
        # 모든 단계 시간의 합 = 총 시간
        total_duration = sum(durations.values())
        assert abs(total_duration - summary["total_time_minutes"]) < 1.0


class TestSleepStageAnalysisDatabase:
    """수면 단계 분석 DB 저장 테스트"""
    
    def test_analyze_creates_sleep_analysis_record(
        self, client: TestClient, auth_headers, sample_session, db_session
    ):
        """SleepAnalysis 레코드 생성"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == 200
        analysis_id = response.json()["analysis_id"]
        
        # DB에서 레코드 확인
        from app.models import SleepAnalysis
        
        analysis = db_session.query(SleepAnalysis).filter_by(id=analysis_id).first()
        assert analysis is not None
        assert analysis.session_id == sample_session.id
        assert analysis.analysis_type == "sleep_stage"
    
    def test_analyze_stores_stage_data(
        self, client: TestClient, auth_headers, sample_session, db_session
    ):
        """수면 단계 데이터 저장"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == 200
        analysis_id = response.json()["analysis_id"]
        
        from app.models import SleepAnalysis
        
        analysis = db_session.query(SleepAnalysis).filter_by(id=analysis_id).first()
        
        # 결과 데이터 저장 확인
        assert analysis.result_data is not None
        assert "stages" in analysis.result_data
        assert "summary" in analysis.result_data


class TestSleepEfficiencyCalculation:
    """수면 효율성 계산 테스트"""
    
    def test_calculate_sleep_efficiency_all_sleep(self):
        """모두 수면 상태인 경우 (Wake 제외)"""
        from app.ml.analysis.sleep_metrics import calculate_sleep_efficiency
        
        # 100개 에포크, 모두 N2 (수면)
        stages = [2] * 100
        
        efficiency = calculate_sleep_efficiency(stages)
        
        assert efficiency == 100.0
    
    def test_calculate_sleep_efficiency_half_awake(self):
        """절반이 깨어있는 경우"""
        from app.ml.analysis.sleep_metrics import calculate_sleep_efficiency
        
        # 50개 Wake, 50개 N2
        stages = [0] * 50 + [2] * 50
        
        efficiency = calculate_sleep_efficiency(stages)
        
        assert efficiency == 50.0
    
    def test_calculate_sleep_efficiency_mixed_stages(self):
        """다양한 수면 단계"""
        from app.ml.analysis.sleep_metrics import calculate_sleep_efficiency
        
        # 20 Wake, 80 수면 (N1, N2, N3, REM)
        stages = [0] * 20 + [1] * 20 + [2] * 30 + [3] * 20 + [4] * 10
        
        efficiency = calculate_sleep_efficiency(stages)
        
        assert efficiency == 80.0


class TestStageDurationCalculation:
    """단계별 지속 시간 계산 테스트"""
    
    def test_calculate_stage_durations(self):
        """각 단계별 지속 시간 계산"""
        from app.ml.analysis.sleep_metrics import calculate_stage_durations
        
        # 30초 에포크 기준
        # 10개 Wake (5분), 20개 N2 (10분), 10개 REM (5분)
        stages = [0] * 10 + [2] * 20 + [4] * 10
        
        durations = calculate_stage_durations(stages, epoch_length_seconds=30)
        
        assert durations["Wake"] == 5.0  # 분
        assert durations["N1"] == 0.0
        assert durations["N2"] == 10.0
        assert durations["N3"] == 0.0
        assert durations["REM"] == 5.0
        
        # 총 시간 = 20분
        assert sum(durations.values()) == 20.0


class TestAnalysisResponseSchema:
    """응답 스키마 테스트"""
    
    def test_response_schema_structure(
        self, client: TestClient, auth_headers, sample_session
    ):
        """응답 스키마 구조 검증"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 최상위 필드
        required_fields = [
            "analysis_id",
            "session_id",
            "stages",
            "summary",
            "created_at"
        ]
        
        for field in required_fields:
            assert field in data
    
    def test_stage_schema_structure(
        self, client: TestClient, auth_headers, sample_session
    ):
        """에포크 스키마 구조 검증"""
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == 200
        stages = response.json()["stages"]
        
        if len(stages) > 0:
            epoch = stages[0]
            
            required_fields = ["epoch_number", "stage", "stage_name", "probability"]
            
            for field in required_fields:
                assert field in epoch


class TestAnalysisPerformance:
    """분석 성능 테스트"""
    
    def test_analysis_response_time(
        self, client: TestClient, auth_headers, sample_session
    ):
        """응답 시간 < 3초"""
        import time
        
        start_time = time.time()
        
        response = client.post(
            "/api/v1/analyze/sleep-stages",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 3.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
