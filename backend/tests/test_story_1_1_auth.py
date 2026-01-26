"""
Tests for Story 1.1: 사용자 인증 API

Test Coverage:
- POST /api/v1/auth/register - 회원가입
- POST /api/v1/auth/token - 로그인
- POST /api/v1/auth/refresh - 토큰 갱신
"""

import pytest
from fastapi.testclient import TestClient


class TestUserRegistration:
    """회원가입 테스트"""
    
    def test_register_success(self, client: TestClient):
        """회원가입 성공"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepass123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data  # 비밀번호 노출 방지
    
    def test_register_duplicate_email(self, client: TestClient, test_user):
        """중복 이메일로 회원가입 실패"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",  # test_user와 동일
                "username": "anotheruser",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == 400
        assert "이메일" in response.json()["detail"]
    
    def test_register_duplicate_username(self, client: TestClient, test_user):
        """중복 사용자명으로 회원가입 실패"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "username": "testuser",  # test_user와 동일
                "password": "securepass123"
            }
        )
        
        assert response.status_code == 400
        assert "사용자명" in response.json()["detail"]
    
    def test_register_invalid_email(self, client: TestClient):
        """잘못된 이메일 형식"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "username": "validuser",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_short_password(self, client: TestClient):
        """짧은 비밀번호"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "username": "validuser",
                "password": "short"  # 8자 미만
            }
        )
        
        assert response.status_code == 422
    
    def test_register_short_username(self, client: TestClient):
        """짧은 사용자명"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "username": "ab",  # 3자 미만
                "password": "securepass123"
            }
        )
        
        assert response.status_code == 422


class TestUserLogin:
    """로그인 테스트"""
    
    def test_login_success(self, client: TestClient, test_user):
        """로그인 성공"""
        response = client.post(
            "/api/v1/auth/token",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900  # 15분 = 900초
    
    def test_login_wrong_email(self, client: TestClient, test_user):
        """존재하지 않는 이메일"""
        response = client.post(
            "/api/v1/auth/token",
            json={
                "email": "nonexistent@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 401
        assert "이메일 또는 비밀번호" in response.json()["detail"]
    
    def test_login_wrong_password(self, client: TestClient, test_user):
        """잘못된 비밀번호"""
        response = client.post(
            "/api/v1/auth/token",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "이메일 또는 비밀번호" in response.json()["detail"]
    
    def test_login_inactive_user(self, client: TestClient, db_session):
        """비활성 사용자 로그인 시도"""
        from app.models import User
        from app.utils.security import hash_password
        
        # 비활성 사용자 생성
        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=hash_password("testpass123"),
            is_active=0  # 비활성
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        response = client.post(
            "/api/v1/auth/token",
            json={
                "email": "inactive@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 403
        assert "비활성" in response.json()["detail"]


class TestTokenRefresh:
    """토큰 갱신 테스트"""
    
    def test_refresh_token_success(self, client: TestClient, test_user):
        """토큰 갱신 성공"""
        # 먼저 로그인
        login_response = client.post(
            "/api/v1/auth/token",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # 토큰 갱신
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_invalid_token(self, client: TestClient):
        """유효하지 않은 토큰으로 갱신 시도"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        
        assert response.status_code == 401
        assert "유효하지 않은" in response.json()["detail"]
    
    def test_refresh_with_access_token(self, client: TestClient, test_user):
        """access_token으로 갱신 시도 (실패해야 함)"""
        # 먼저 로그인
        login_response = client.post(
            "/api/v1/auth/token",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        access_token = login_response.json()["access_token"]
        
        # access_token으로 갱신 시도
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token}  # access_token 사용 (잘못됨)
        )
        
        assert response.status_code == 401


class TestAuthValidation:
    """인증 스키마 검증 테스트"""
    
    def test_register_missing_email(self, client: TestClient):
        """이메일 누락"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_missing_password(self, client: TestClient):
        """비밀번호 누락"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser"
            }
        )
        
        assert response.status_code == 422
    
    def test_login_missing_fields(self, client: TestClient):
        """로그인 필수 필드 누락"""
        response = client.post(
            "/api/v1/auth/token",
            json={}
        )
        
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
