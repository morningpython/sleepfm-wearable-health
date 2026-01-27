"""
Story 4.4: 분석 결과 조회 및 히스토리 (TDD - Red Phase)

Acceptance Criteria:
- GET /api/v1/users/{user_id}/sessions 구현
- GET /api/v1/sessions/{session_id}/results 구현
- 날짜 범위 쿼리 파라미터 지원
- 페이지네이션 (limit, offset)
- 응답 시간 < 500ms
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime, timedelta
import time


class TestUserSessionsEndpoint:
    """사용자 세션 목록 조회 엔드포인트 테스트"""
    
    def test_endpoint_exists(self, client: TestClient, auth_headers, test_user):
        """GET /api/v1/users/{user_id}/sessions 엔드포인트 존재"""
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions",
            headers=auth_headers,
        )
        
        assert response.status_code in [200, 403, 404], \
            f"Expected 200/403/404, got {response.status_code}"
    
    def test_requires_authentication(self, client: TestClient, test_user):
        """인증 필요"""
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions",
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_can_only_access_own_sessions(
        self, client: TestClient, auth_headers, test_user, db_session
    ):
        """자신의 세션만 조회 가능"""
        from app.models import User
        from app.utils.security import hash_password
        
        # 다른 사용자
        other_user = User(
            email="other@example.com",
            username="otheruser",
            full_name="Other User",
            hashed_password=hash_password("password123"),
            is_active=1
        )
        db_session.add(other_user)
        db_session.commit()
        
        # 다른 사용자의 세션 목록 조회 시도
        response = client.get(
            f"/api/v1/users/{other_user.id}/sessions",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_returns_session_list(
        self, client: TestClient, auth_headers, test_user, sample_session
    ):
        """세션 목록 반환"""
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "sessions" in data
        assert "total" in data
        assert isinstance(data["sessions"], list)
        assert data["total"] >= 1
    
    def test_session_item_structure(
        self, client: TestClient, auth_headers, test_user, sample_session
    ):
        """세션 아이템 구조"""
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        session = data["sessions"][0]
        
        assert "id" in session
        assert "session_date" in session
        assert "duration_hours" in session
        assert "analysis_status" in session
        assert "has_results" in session  # 분석 결과 존재 여부


class TestUserSessionsPagination:
    """세션 목록 페이지네이션 테스트"""
    
    def test_pagination_default(
        self, client: TestClient, auth_headers, test_user, db_session
    ):
        """기본 페이지네이션"""
        from app.models import SleepSession
        
        # 여러 세션 생성
        for i in range(15):
            session = SleepSession(
                user_id=test_user.id,
                session_date=datetime.now() - timedelta(days=i),
                duration_hours=7.5,
                analysis_status="pending"
            )
            db_session.add(session)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 기본 limit은 10
        assert len(data["sessions"]) <= 10
    
    def test_pagination_with_limit(
        self, client: TestClient, auth_headers, test_user
    ):
        """limit 파라미터"""
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions?limit=5",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["sessions"]) <= 5
    
    def test_pagination_with_offset(
        self, client: TestClient, auth_headers, test_user, db_session
    ):
        """offset 파라미터"""
        from app.models import SleepSession
        
        # 여러 세션 생성
        for i in range(10):
            session = SleepSession(
                user_id=test_user.id,
                session_date=datetime.now() - timedelta(days=i),
                duration_hours=7.5,
                analysis_status="pending"
            )
            db_session.add(session)
        db_session.commit()
        
        # 첫 페이지
        response1 = client.get(
            f"/api/v1/users/{test_user.id}/sessions?limit=5&offset=0",
            headers=auth_headers,
        )
        
        # 두 번째 페이지
        response2 = client.get(
            f"/api/v1/users/{test_user.id}/sessions?limit=5&offset=5",
            headers=auth_headers,
        )
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        
        data1 = response1.json()
        data2 = response2.json()
        
        # 페이지가 다름
        if len(data1["sessions"]) > 0 and len(data2["sessions"]) > 0:
            assert data1["sessions"][0]["id"] != data2["sessions"][0]["id"]


class TestUserSessionsDateFilter:
    """날짜 범위 필터링 테스트"""
    
    def test_filter_by_start_date(
        self, client: TestClient, auth_headers, test_user, db_session
    ):
        """시작 날짜 필터"""
        from app.models import SleepSession
        
        # 다양한 날짜의 세션 생성
        for i in range(10):
            session = SleepSession(
                user_id=test_user.id,
                session_date=datetime.now() - timedelta(days=i),
                duration_hours=7.5,
                analysis_status="pending"
            )
            db_session.add(session)
        db_session.commit()
        
        # 3일 전부터
        start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions?start_date={start_date}",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 모든 세션이 start_date 이후
        for session in data["sessions"]:
            session_date = datetime.fromisoformat(session["session_date"].replace("Z", "+00:00"))
            assert session_date.date() >= datetime.strptime(start_date, "%Y-%m-%d").date()
    
    def test_filter_by_end_date(
        self, client: TestClient, auth_headers, test_user, db_session
    ):
        """종료 날짜 필터"""
        from app.models import SleepSession
        
        for i in range(10):
            session = SleepSession(
                user_id=test_user.id,
                session_date=datetime.now() - timedelta(days=i),
                duration_hours=7.5,
                analysis_status="pending"
            )
            db_session.add(session)
        db_session.commit()
        
        # 5일 전까지
        end_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions?end_date={end_date}",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_filter_by_date_range(
        self, client: TestClient, auth_headers, test_user
    ):
        """날짜 범위 필터"""
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions?start_date={start_date}&end_date={end_date}",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK


class TestSessionResultsEndpoint:
    """세션 상세 결과 조회 엔드포인트 테스트"""
    
    def test_endpoint_exists(
        self, client: TestClient, auth_headers, sample_session
    ):
        """GET /api/v1/sessions/{session_id}/results 존재"""
        response = client.get(
            f"/api/v1/sessions/{sample_session.id}/results",
            headers=auth_headers,
        )
        
        assert response.status_code in [200, 404], \
            f"Expected 200/404, got {response.status_code}"
    
    def test_requires_authentication(self, client: TestClient, sample_session):
        """인증 필요"""
        response = client.get(
            f"/api/v1/sessions/{sample_session.id}/results",
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_session_not_found(self, client: TestClient, auth_headers):
        """존재하지 않는 세션"""
        response = client.get(
            "/api/v1/sessions/99999/results",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_returns_all_analysis_results(
        self, client: TestClient, auth_headers, sample_session, db_session
    ):
        """모든 분석 결과 반환"""
        from app.models import SleepAnalysis
        
        # 분석 결과 생성
        analyses_data = [
            {"analysis_type": "sleep_stage", "result_data": {"stages": []}},
            {"analysis_type": "apnea", "result_data": {"ahi": 5.2}},
            {"analysis_type": "disease_risk", "result_data": {"predictions": []}},
        ]
        
        for data in analyses_data:
            analysis = SleepAnalysis(
                session_id=sample_session.id,
                user_id=sample_session.user_id,
                analysis_type=data["analysis_type"],
                result_data=data["result_data"]
            )
            db_session.add(analysis)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/sessions/{sample_session.id}/results",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "session_id" in data
        assert "session_date" in data
        assert "analyses" in data
        
        # 모든 분석 유형 포함
        analysis_types = [a["type"] for a in data["analyses"]]
        assert "sleep_stage" in analysis_types
        assert "apnea" in analysis_types
        assert "disease_risk" in analysis_types
    
    def test_analysis_result_structure(
        self, client: TestClient, auth_headers, sample_session, db_session
    ):
        """분석 결과 구조"""
        from app.models import SleepAnalysis
        
        analysis = SleepAnalysis(
            session_id=sample_session.id,
            user_id=sample_session.user_id,
            analysis_type="sleep_stage",
            result_data={"stages": [], "summary": {}}
        )
        db_session.add(analysis)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/sessions/{sample_session.id}/results",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for analysis in data["analyses"]:
            assert "id" in analysis
            assert "type" in analysis
            assert "result" in analysis
            assert "created_at" in analysis


class TestSessionResultsAuthorization:
    """세션 결과 권한 테스트"""
    
    def test_cannot_access_other_user_results(
        self, client: TestClient, auth_headers, test_user, db_session
    ):
        """다른 사용자의 결과 접근 불가"""
        from app.models import User, SleepSession
        from app.utils.security import hash_password
        
        # 다른 사용자
        other_user = User(
            email="other@example.com",
            username="otheruser",
            full_name="Other User",
            hashed_password=hash_password("password123"),
            is_active=1
        )
        db_session.add(other_user)
        db_session.commit()
        
        # 다른 사용자의 세션
        other_session = SleepSession(
            user_id=other_user.id,
            session_date=datetime.now(),
            duration_hours=8,
            analysis_status="completed"
        )
        db_session.add(other_session)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/sessions/{other_session.id}/results",
            headers=auth_headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestHistoryPerformance:
    """히스토리 조회 성능 테스트"""
    
    def test_sessions_response_time(
        self, client: TestClient, auth_headers, test_user
    ):
        """세션 목록 조회 응답 시간 < 500ms"""
        start_time = time.time()
        
        response = client.get(
            f"/api/v1/users/{test_user.id}/sessions",
            headers=auth_headers,
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert elapsed_time < 0.5, f"Response time {elapsed_time:.3f}s exceeds 500ms limit"
    
    def test_results_response_time(
        self, client: TestClient, auth_headers, sample_session
    ):
        """세션 결과 조회 응답 시간 < 500ms"""
        start_time = time.time()
        
        response = client.get(
            f"/api/v1/sessions/{sample_session.id}/results",
            headers=auth_headers,
        )
        
        elapsed_time = time.time() - start_time
        
        # 결과가 없어도 응답 시간은 빨라야 함
        assert elapsed_time < 0.5, f"Response time {elapsed_time:.3f}s exceeds 500ms limit"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
