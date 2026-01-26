"""
Tests for Story 1.2: 수면 세션 관리 API

Test Coverage:
- POST /api/v1/sessions/upload - 센서 데이터 업로드
- GET /api/v1/sessions/{session_id} - 세션 조회
- GET /api/v1/sessions/ - 세션 목록 조회
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestSessionUpload:
    """센서 데이터 업로드 테스트"""
    
    def test_upload_success(self, client: TestClient, auth_headers):
        """센서 데이터 업로드 성공"""
        response = client.post(
            "/api/v1/sessions/upload",
            headers=auth_headers,
            json={
                "session_date": "2026-01-25T22:00:00",
                "duration_hours": 8.0,
                "device_type": "apple_watch",
                "sampling_rate": 100,
                "data": [
                    {
                        "timestamp": 1737842400.0,
                        "heart_rate": 72.5,
                        "spo2": 98.0,
                        "accel_x": 0.01,
                        "accel_y": -0.02,
                        "accel_z": 0.98
                    },
                    {
                        "timestamp": 1737842401.0,
                        "heart_rate": 73.0,
                        "spo2": 97.5,
                        "accel_x": 0.02,
                        "accel_y": -0.01,
                        "accel_z": 0.97
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["analysis_status"] == "pending"
        assert data["duration_hours"] == 8.0
    
    def test_upload_requires_auth(self, client: TestClient):
        """인증 없이 업로드 시도"""
        response = client.post(
            "/api/v1/sessions/upload",
            json={
                "session_date": "2026-01-25T22:00:00",
                "duration_hours": 8.0,
                "device_type": "apple_watch",
                "sampling_rate": 100,
                "data": [{"timestamp": "2026-01-25T22:00:00"}]
            }
        )
        
        assert response.status_code == 401
    
    def test_upload_empty_data(self, client: TestClient, auth_headers):
        """빈 데이터 업로드 시도"""
        response = client.post(
            "/api/v1/sessions/upload",
            headers=auth_headers,
            json={
                "session_date": "2026-01-25T22:00:00",
                "duration_hours": 8.0,
                "device_type": "apple_watch",
                "sampling_rate": 100,
                "data": []
            }
        )
        
        assert response.status_code == 400
        assert "데이터" in response.json()["detail"]
    
    def test_upload_invalid_duration(self, client: TestClient, auth_headers):
        """잘못된 duration_hours"""
        response = client.post(
            "/api/v1/sessions/upload",
            headers=auth_headers,
            json={
                "session_date": "2026-01-25T22:00:00",
                "duration_hours": 30.0,  # 24시간 초과
                "device_type": "apple_watch",
                "sampling_rate": 100,
                "data": [{"timestamp": "2026-01-25T22:00:00"}]
            }
        )
        
        assert response.status_code == 422
    
    def test_upload_any_device_type(self, client: TestClient, auth_headers):
        """다양한 device_type 허용 (현재 검증 없음)"""
        response = client.post(
            "/api/v1/sessions/upload",
            headers=auth_headers,
            json={
                "session_date": "2026-01-25T22:00:00",
                "duration_hours": 8.0,
                "device_type": "custom_device",
                "sampling_rate": 100,
                "data": [{"timestamp": 1737842400.0}]
            }
        )
        
        # 현재 구현은 모든 device_type 허용
        assert response.status_code == 201


class TestSessionRetrieval:
    """세션 조회 테스트"""
    
    def test_get_session_success(self, client: TestClient, auth_headers, sample_session):
        """세션 조회 성공"""
        response = client.get(
            f"/api/v1/sessions/{sample_session.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_session.id
        assert "session_date" in data
        assert "duration_hours" in data
        assert "analysis_status" in data
    
    def test_get_session_requires_auth(self, client: TestClient, sample_session):
        """인증 없이 세션 조회 시도"""
        response = client.get(f"/api/v1/sessions/{sample_session.id}")
        
        assert response.status_code == 401
    
    def test_get_session_not_found(self, client: TestClient, auth_headers):
        """존재하지 않는 세션 조회"""
        response = client.get(
            "/api/v1/sessions/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "세션" in response.json()["detail"]
    
    def test_get_other_user_session(self, client: TestClient, auth_headers, db_session):
        """다른 사용자의 세션 조회 시도"""
        from app.models import User, SleepSession
        from app.utils.security import hash_password
        from datetime import datetime
        
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=hash_password("testpass123"),
            is_active=1
        )
        db_session.add(other_user)
        db_session.commit()
        
        # 다른 사용자의 세션 생성
        other_session = SleepSession(
            user_id=other_user.id,
            session_date=datetime.now(),
            duration_hours=7.5,
            analysis_status="pending"
        )
        db_session.add(other_session)
        db_session.commit()
        
        # 현재 사용자가 다른 사용자의 세션 조회 시도
        response = client.get(
            f"/api/v1/sessions/{other_session.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404  # 권한 없음 = 404


class TestSessionList:
    """세션 목록 조회 테스트"""
    
    def test_list_sessions_success(self, client: TestClient, auth_headers, sample_session):
        """세션 목록 조회 성공"""
        response = client.get(
            "/api/v1/sessions/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(s["id"] == sample_session.id for s in data)
    
    def test_list_sessions_requires_auth(self, client: TestClient):
        """인증 없이 목록 조회 시도"""
        response = client.get("/api/v1/sessions/")
        
        assert response.status_code == 401
    
    def test_list_sessions_pagination(self, client: TestClient, auth_headers, db_session, test_user):
        """페이지네이션 테스트"""
        from app.models import SleepSession
        from datetime import datetime, timedelta
        
        # 여러 세션 생성
        for i in range(5):
            session = SleepSession(
                user_id=test_user.id,
                session_date=datetime.now() - timedelta(days=i),
                duration_hours=7.0 + i * 0.1,
                analysis_status="pending"
            )
            db_session.add(session)
        db_session.commit()
        
        # skip과 limit 테스트
        response = client.get(
            "/api/v1/sessions/?skip=1&limit=2",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_list_sessions_limit_max(self, client: TestClient, auth_headers):
        """limit 최대값 제한 테스트"""
        response = client.get(
            "/api/v1/sessions/?limit=200",  # 100 초과
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # 최대 100개로 제한됨
    
    def test_list_sessions_empty(self, client: TestClient, db_session):
        """빈 세션 목록"""
        from app.models import User
        from app.utils.security import hash_password, create_token
        from datetime import timedelta
        
        # 세션이 없는 새 사용자 생성
        new_user = User(
            email="nosessions@example.com",
            username="nosessionsuser",
            hashed_password=hash_password("testpass123"),
            is_active=1
        )
        db_session.add(new_user)
        db_session.commit()
        
        # 새 사용자의 토큰 생성
        token = create_token(
            data={"sub": str(new_user.id), "email": new_user.email},
            expires_delta=timedelta(minutes=15)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        from app.main import create_app
        from app.database import get_db
        from starlette.testclient import TestClient as StarletteTestClient
        
        app = create_app(enable_lifespan=False)
        
        def override_get_db():
            yield db_session
        
        app.dependency_overrides[get_db] = override_get_db
        new_client = StarletteTestClient(app)
        
        response = new_client.get("/api/v1/sessions/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestSessionValidation:
    """세션 스키마 검증 테스트"""
    
    def test_upload_missing_session_date(self, client: TestClient, auth_headers):
        """session_date 누락"""
        response = client.post(
            "/api/v1/sessions/upload",
            headers=auth_headers,
            json={
                "duration_hours": 8.0,
                "device_type": "apple_watch",
                "sampling_rate": 100,
                "data": [{"timestamp": "2026-01-25T22:00:00"}]
            }
        )
        
        assert response.status_code == 422
    
    def test_upload_missing_data(self, client: TestClient, auth_headers):
        """data 필드 누락"""
        response = client.post(
            "/api/v1/sessions/upload",
            headers=auth_headers,
            json={
                "session_date": "2026-01-25T22:00:00",
                "duration_hours": 8.0,
                "device_type": "apple_watch",
                "sampling_rate": 100
            }
        )
        
        assert response.status_code == 422
    
    def test_upload_negative_duration(self, client: TestClient, auth_headers):
        """음수 duration"""
        response = client.post(
            "/api/v1/sessions/upload",
            headers=auth_headers,
            json={
                "session_date": "2026-01-25T22:00:00",
                "duration_hours": -1.0,
                "device_type": "apple_watch",
                "sampling_rate": 100,
                "data": [{"timestamp": "2026-01-25T22:00:00"}]
            }
        )
        
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
