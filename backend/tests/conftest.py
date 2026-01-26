"""
pytest 설정 및 공통 fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.database import Base, get_db
from app.models import User, SleepSession
from app.utils.security import hash_password


# 테스트용 인메모리 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """테스트용 데이터베이스 세션"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """테스트 클라이언트"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """테스트용 사용자"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("testpass123"),
        is_active=1
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client: TestClient, test_user):
    """인증 헤더"""
    # 로그인하여 토큰 획득
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    # 인증 실패 시 빈 헤더 반환 (일부 테스트용)
    return {}


@pytest.fixture
def sample_session(db_session, test_user):
    """테스트용 수면 세션"""
    session = SleepSession(
        user_id=test_user.id,
        session_date=datetime(2026, 1, 25, 22, 0, 0),
        duration_hours=8,
        raw_data_path="/tmp/sample_sleep_data.json",
        analysis_status="pending"
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session
