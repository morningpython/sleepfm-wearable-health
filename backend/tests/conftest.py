"""
pytest 설정 및 공통 fixtures

CRITICAL: app.* imports must be done INSIDE fixtures to avoid module pollution!
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime


@pytest.fixture(scope="function")
def db_session():
    """테스트용 데이터베이스 세션 - 각 테스트마다 새로운 engine 생성"""
    # Import inside fixture to avoid module pollution
    # Use app.models.Base to ensure all models are registered with the same Base
    from app.models import Base, User, SleepSession, SleepAnalysis
    from sqlalchemy.pool import StaticPool
    
    # Create NEW engine for each test to avoid state pollution
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # Use StaticPool for thread safety
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()  # Properly dispose engine


@pytest.fixture(scope="function")
def client(db_session):
    """테스트 클라이언트"""
    # Import inside fixture to avoid module pollution
    from app.main import create_app
    from app.database import get_db
    
    app = create_app(enable_lifespan=False)
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create TestClient directly (not using context manager)
    test_client = TestClient(app, raise_server_exceptions=True)
    
    yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """테스트용 사용자"""
    # Import inside fixture to avoid module pollution
    from app.models import User
    from app.utils.security import hash_password
    
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
def auth_headers(test_user):
    """인증 헤더 - client 의존성 제거"""
    # Directly create JWT token without using client
    from app.utils.security import create_token
    from datetime import timedelta
    
    access_token = create_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=timedelta(minutes=15)
    )
    
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def sample_session(db_session, test_user):
    """테스트용 수면 세션"""
    # Import inside fixture to avoid module pollution
    from app.models import SleepSession
    
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
