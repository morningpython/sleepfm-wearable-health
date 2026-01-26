"""
Story 3.4: 수면무호흡 분석 API (TDD - Red Phase)

Acceptance Criteria:
- POST /api/v1/analyze/apnea 엔드포인트
- session_id로 센서 데이터 조회
- 무호흡/저호흡 이벤트 리스트 반환
- AHI 및 심각도 제공
- 권장사항 포함
- ApneaAnalysis 테이블에 저장

TDD Approach:
1. Red: 테스트 작성 (실패 확인)
2. Green: 최소 구현
3. Refactor: 코드 개선
"""

import pytest
from fastapi import status
from datetime import datetime
import json


class TestApneaAnalysisEndpoint:
    """무호흡 분석 API 엔드포인트 테스트"""
    
    def test_apnea_analysis_endpoint_exists(self, client):
        """POST /api/v1/analyze/apnea 엔드포인트 존재"""
        response = client.post(
            "/api/v1/analyze/apnea",
            json={"session_id": 99999}  # 존재하지 않는 ID
        )
        
        # 404 또는 401 (인증 필요)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED]
    
    def test_requires_authentication(self, client):
        """인증 필요"""
        response = client.post(
            "/api/v1/analyze/apnea",
            json={"session_id": 1}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_session_id(self, client, auth_headers):
        """존재하지 않는 session_id"""
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": 99999}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_missing_session_id(self, client, auth_headers):
        """session_id 누락"""
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestApneaAnalysisExecution:
    """무호흡 분석 실행 테스트"""
    
    def test_successful_apnea_analysis(self, client, auth_headers, sample_session):
        """무호흡 분석 성공"""
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "analysis_id" in data
        assert data["session_id"] == sample_session.id
        assert "events" in data
        assert "ahi" in data
        assert "severity" in data
        assert "recommendations" in data
    
    def test_returns_event_list(self, client, auth_headers, sample_session):
        """이벤트 리스트 반환"""
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        data = response.json()
        events = data["events"]
        
        assert isinstance(events, list)
        if len(events) > 0:
            event = events[0]
            assert "epoch_start" in event
            assert "epoch_end" in event
            assert "event_type" in event
            assert "duration_seconds" in event
            assert "confidence" in event
    
    def test_returns_ahi_and_severity(self, client, auth_headers, sample_session):
        """AHI 및 심각도 반환"""
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        data = response.json()
        
        assert isinstance(data["ahi"], (int, float))
        assert data["ahi"] >= 0
        assert data["severity"] in ["Normal", "Mild", "Moderate", "Severe"]
    
    def test_returns_recommendations(self, client, auth_headers, sample_session):
        """권장사항 반환"""
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        data = response.json()
        recommendations = data["recommendations"]
        
        assert isinstance(recommendations, list)
        assert all(isinstance(rec, str) for rec in recommendations)


class TestApneaAnalysisDatabase:
    """데이터베이스 저장 테스트"""
    
    def test_creates_apnea_analysis_record(self, client, auth_headers, sample_session, db_session):
        """ApneaAnalysis 레코드 생성"""
        from app.models import SleepAnalysis
        
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # DB에 레코드 확인
        analysis = db_session.query(SleepAnalysis).filter_by(
            session_id=sample_session.id,
            analysis_type="apnea"
        ).first()
        
        assert analysis is not None
        assert analysis.user_id == sample_session.user_id
    
    def test_stores_apnea_data(self, client, auth_headers, sample_session, db_session):
        """무호흡 데이터 저장"""
        from app.models import SleepAnalysis
        
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        analysis = db_session.query(SleepAnalysis).filter_by(
            session_id=sample_session.id,
            analysis_type="apnea"
        ).first()
        
        result_data = analysis.result_data
        assert "events" in result_data
        assert "ahi" in result_data
        assert "severity" in result_data
        assert "recommendations" in result_data


class TestRecommendationGeneration:
    """권장사항 생성 테스트"""
    
    def test_normal_severity_recommendations(self, client, auth_headers, sample_session):
        """정상 심각도 권장사항"""
        # 이 테스트는 더미 데이터로 Normal 케이스를 시뮬레이션
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        data = response.json()
        
        if data["severity"] == "Normal":
            recommendations = data["recommendations"]
            assert len(recommendations) > 0
            # 정상 심각도에서는 일반적인 수면 위생 권장사항
            assert any("수면" in rec or "건강" in rec for rec in recommendations)
    
    def test_mild_severity_recommendations(self):
        """경증 심각도 권장사항"""
        from app.routes.analysis import _generate_apnea_recommendations
        
        recommendations = _generate_apnea_recommendations(ahi=10.0, severity="Mild")
        
        assert len(recommendations) > 0
        assert any("생활습관" in rec or "의사" in rec for rec in recommendations)
    
    def test_moderate_severity_recommendations(self):
        """중등도 심각도 권장사항"""
        from app.routes.analysis import _generate_apnea_recommendations
        
        recommendations = _generate_apnea_recommendations(ahi=20.0, severity="Moderate")
        
        assert len(recommendations) > 0
        assert any("전문의" in rec or "검사" in rec for rec in recommendations)
    
    def test_severe_severity_recommendations(self):
        """중증 심각도 권장사항"""
        from app.routes.analysis import _generate_apnea_recommendations
        
        recommendations = _generate_apnea_recommendations(ahi=40.0, severity="Severe")
        
        assert len(recommendations) > 0
        assert any("즉시" in rec or "긴급" in rec or "전문의" in rec for rec in recommendations)


class TestApneaResponseSchema:
    """응답 스키마 테스트"""
    
    def test_response_schema_structure(self, client, auth_headers, sample_session):
        """응답 스키마 구조 검증"""
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        data = response.json()
        
        # 필수 필드
        required_fields = [
            "analysis_id", "session_id", "events", "ahi",
            "severity", "recommendations", "created_at"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_event_schema(self, client, auth_headers, sample_session):
        """이벤트 스키마 검증"""
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        
        data = response.json()
        events = data["events"]
        
        if len(events) > 0:
            event = events[0]
            required_event_fields = [
                "epoch_start", "epoch_end", "event_type",
                "duration_seconds", "confidence"
            ]
            
            for field in required_event_fields:
                assert field in event, f"Missing event field: {field}"
            
            assert event["event_type"] in ["apnea", "hypopnea"]
            assert event["duration_seconds"] > 0
            assert 0 <= event["confidence"] <= 1


class TestApneaAnalysisPerformance:
    """성능 테스트"""
    
    def test_analysis_response_time(self, client, auth_headers, sample_session):
        """분석 응답 시간 < 3초"""
        import time
        
        start_time = time.time()
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": sample_session.id}
        )
        elapsed_time = time.time() - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert elapsed_time < 3.0, f"Response took {elapsed_time:.2f}s, expected < 3s"


class TestApneaAnalysisAuthorization:
    """권한 검증 테스트"""
    
    def test_user_can_only_analyze_own_sessions(self, client, auth_headers, test_user, db_session):
        """사용자는 자신의 세션만 분석 가능"""
        from app.models import User, SleepSession
        from app.utils.security import hash_password
        
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            username="other",
            full_name="Other User",
            hashed_password=hash_password("password"),
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
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": other_session.id}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestApneaAnalysisEdgeCases:
    """엣지 케이스 테스트"""
    
    def test_very_short_session(self, client, auth_headers, test_user, db_session):
        """매우 짧은 세션 (< 1시간)"""
        from app.models import SleepSession
        
        short_session = SleepSession(
            user_id=test_user.id,
            session_date=datetime(2026, 1, 25, 22, 0, 0),
            duration_hours=0.5,  # 30분 -> 0.5시간
            raw_data_path="/fake/path/short.json",
            analysis_status="pending"
        )
        db_session.add(short_session)
        db_session.commit()
        
        response = client.post(
            "/api/v1/analyze/apnea",
            headers=auth_headers,
            json={"session_id": short_session.id}
        )
        
        # 짧은 세션도 분석 가능해야 함
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ahi"] >= 0
    
    def test_zero_events_case(self):
        """이벤트 0개인 경우"""
        from app.routes.analysis import _generate_apnea_recommendations
        
        recommendations = _generate_apnea_recommendations(ahi=0.0, severity="Normal")
        
        assert len(recommendations) > 0
        assert any("정상" in rec or "양호" in rec for rec in recommendations)
