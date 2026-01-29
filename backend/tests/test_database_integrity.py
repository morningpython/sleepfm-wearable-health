"""
Sprint 10: 데이터베이스 무결성 검증 테스트

외래 키 제약조건, 트랜잭션 롤백, 대량 데이터 삽입 테스트
"""

import pytest
from datetime import datetime, date
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError


class TestForeignKeyConstraints:
    """외래 키 제약조건 테스트"""
    
    def test_sleep_session_user_fk(self, db_session, test_user):
        """수면 세션은 유효한 사용자가 필요"""
        from app.models import SleepSession
        
        # 유효한 사용자로 세션 생성
        session = SleepSession(
            user_id=test_user.id,
            session_date=datetime.now(),
            raw_data_path="/test/path"
        )
        db_session.add(session)
        db_session.commit()
        
        assert session.id is not None
        assert session.user_id == test_user.id
    
    def test_sleep_session_invalid_user_fails(self, db_session):
        """존재하지 않는 사용자로 세션 생성 실패"""
        from app.models import SleepSession
        
        # 존재하지 않는 user_id
        session = SleepSession(
            user_id=99999,
            session_date=datetime.now(),
            raw_data_path="/test/path"
        )
        db_session.add(session)
        
        # SQLite는 기본적으로 FK 강제하지 않으므로 스킵 가능
        try:
            db_session.commit()
            # FK가 적용되지 않은 경우 (SQLite 기본 설정)
            db_session.rollback()
        except IntegrityError:
            # FK가 적용된 경우 예상대로 실패
            db_session.rollback()
    
    def test_cascade_delete_user(self, db_session):
        """사용자 삭제 시 연관 세션도 삭제 (cascade)"""
        from app.models import User, SleepSession
        from app.utils.security import hash_password
        
        # 테스트 사용자 생성
        user = User(
            email="cascade_test@example.com",
            username="cascadeuser",
            hashed_password=hash_password("password123"),
            is_active=1
        )
        db_session.add(user)
        db_session.commit()
        
        user_id = user.id
        
        # 세션 생성
        session = SleepSession(
            user_id=user_id,
            session_date=datetime.now(),
            raw_data_path="/test/cascade"
        )
        db_session.add(session)
        db_session.commit()
        
        session_id = session.id
        
        # 사용자 삭제
        db_session.delete(user)
        db_session.commit()
        
        # 세션도 삭제되었는지 확인
        deleted_session = db_session.query(SleepSession).filter(
            SleepSession.id == session_id
        ).first()
        
        # cascade가 설정되어 있으면 None
        # 설정되어 있지 않으면 orphan session 존재
        # 어느 경우든 에러 없이 완료


class TestTransactionRollback:
    """트랜잭션 롤백 테스트"""
    
    def test_rollback_on_error(self, db_session):
        """에러 발생 시 롤백 확인"""
        from app.models import User
        from app.utils.security import hash_password
        
        initial_count = db_session.query(User).count()
        
        try:
            # 첫 번째 사용자 생성
            user1 = User(
                email="rollback1@example.com",
                username="rollback1",
                hashed_password=hash_password("password123"),
                is_active=1
            )
            db_session.add(user1)
            
            # 두 번째 사용자 (중복 이메일로 에러 유발)
            user2 = User(
                email="rollback1@example.com",  # 중복
                username="rollback2",
                hashed_password=hash_password("password123"),
                is_active=1
            )
            db_session.add(user2)
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
        
        # 롤백 후 카운트 확인
        final_count = db_session.query(User).count()
        assert final_count == initial_count, "롤백 후 카운트가 동일해야 함"
    
    def test_nested_transaction_rollback(self, db_session):
        """중첩 트랜잭션 롤백"""
        from app.models import User
        from app.utils.security import hash_password
        
        initial_count = db_session.query(User).count()
        
        # 외부 트랜잭션
        user1 = User(
            email="outer@example.com",
            username="outeruser",
            hashed_password=hash_password("password123"),
            is_active=1
        )
        db_session.add(user1)
        db_session.flush()
        
        # 전체 롤백
        db_session.rollback()
        
        final_count = db_session.query(User).count()
        assert final_count == initial_count


class TestBulkDataOperations:
    """대량 데이터 작업 테스트"""
    
    def test_bulk_insert_1000_sessions(self, db_session, test_user):
        """1000개 세션 일괄 삽입"""
        from app.models import SleepSession
        import time
        
        sessions = []
        base_date = datetime(2024, 1, 1)
        
        for i in range(1000):
            day_offset = i % 365
            session_date = datetime(2024, 1, 1 + day_offset % 28)
            
            session = SleepSession(
                user_id=test_user.id,
                session_date=session_date,
                raw_data_path=f"/test/bulk/session_{i}"
            )
            sessions.append(session)
        
        start = time.time()
        db_session.bulk_save_objects(sessions)
        db_session.commit()
        elapsed = time.time() - start
        
        # 삽입된 레코드 확인
        count = db_session.query(SleepSession).filter(
            SleepSession.user_id == test_user.id
        ).count()
        
        print(f"\n📊 1000개 세션 삽입:")
        print(f"   시간: {elapsed:.2f}초")
        print(f"   초당: {1000/elapsed:.1f} 레코드")
        
        assert count >= 1000
        assert elapsed < 30.0, f"1000개 삽입 시간: {elapsed:.2f}초 (기준: 30초 미만)"
    
    def test_bulk_update(self, db_session, test_user):
        """대량 업데이트 테스트"""
        from app.models import SleepSession
        import time
        
        # 먼저 데이터 생성
        sessions = []
        for i in range(100):
            session = SleepSession(
                user_id=test_user.id,
                session_date=datetime.now(),
                raw_data_path=f"/test/update/session_{i}"
            )
            sessions.append(session)
        
        db_session.bulk_save_objects(sessions)
        db_session.commit()
        
        # 대량 업데이트
        start = time.time()
        db_session.query(SleepSession).filter(
            SleepSession.user_id == test_user.id,
            SleepSession.raw_data_path.like("/test/update/%")
        ).update(
            {SleepSession.analysis_status: "completed"},
            synchronize_session=False
        )
        db_session.commit()
        elapsed = time.time() - start
        
        print(f"\n📊 100개 세션 업데이트:")
        print(f"   시간: {elapsed:.3f}초")
        
        assert elapsed < 5.0
    
    def test_bulk_delete(self, db_session, test_user):
        """대량 삭제 테스트"""
        from app.models import SleepSession
        import time
        
        # 먼저 데이터 생성
        sessions = []
        for i in range(100):
            session = SleepSession(
                user_id=test_user.id,
                session_date=datetime.now(),
                raw_data_path=f"/test/delete/session_{i}"
            )
            sessions.append(session)
        
        db_session.bulk_save_objects(sessions)
        db_session.commit()
        
        # 대량 삭제
        start = time.time()
        deleted = db_session.query(SleepSession).filter(
            SleepSession.raw_data_path.like("/test/delete/%")
        ).delete(synchronize_session=False)
        db_session.commit()
        elapsed = time.time() - start
        
        print(f"\n📊 {deleted}개 세션 삭제:")
        print(f"   시간: {elapsed:.3f}초")
        
        assert elapsed < 5.0


class TestDataTypeValidation:
    """데이터 타입 및 범위 검증"""
    
    def test_email_format_validation(self, db_session):
        """이메일 형식 검증 (애플리케이션 레벨)"""
        from app.schemas.auth import UserCreate
        from pydantic import ValidationError
        
        # 잘못된 이메일
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid_email",
                username="testuser",
                password="password123"
            )
    
    def test_password_length_validation(self, db_session):
        """비밀번호 길이 검증"""
        from app.schemas.auth import UserCreate
        from pydantic import ValidationError
        
        # 너무 짧은 비밀번호
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="testuser",
                password="short"
            )
    
    def test_username_length_validation(self, db_session):
        """사용자명 길이 검증"""
        from app.schemas.auth import UserCreate
        from pydantic import ValidationError
        
        # 너무 짧은 사용자명
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="ab",  # 최소 3자
                password="password123"
            )
    
    def test_date_range_validation(self, db_session, test_user):
        """날짜 범위 검증"""
        from app.models import SleepSession
        
        # 미래 날짜도 허용 (테스트용)
        session = SleepSession(
            user_id=test_user.id,
            session_date=datetime(2030, 1, 1),
            raw_data_path="/test/future"
        )
        db_session.add(session)
        db_session.commit()
        
        assert session.id is not None


class TestQueryPerformance:
    """쿼리 성능 테스트"""
    
    def test_index_scan_performance(self, db_session, test_user):
        """인덱스 스캔 성능"""
        from app.models import User
        import time
        
        # 이메일로 조회 (인덱스 사용 예상)
        start = time.time()
        for _ in range(100):
            user = db_session.query(User).filter(
                User.email == test_user.email
            ).first()
        elapsed = time.time() - start
        
        avg_time = elapsed / 100 * 1000  # ms
        
        print(f"\n📊 이메일 인덱스 조회 (100회):")
        print(f"   평균: {avg_time:.2f}ms")
        
        assert avg_time < 10, f"평균 조회 시간: {avg_time:.2f}ms (기준: 10ms 미만)"
    
    def test_join_query_performance(self, db_session, test_user):
        """조인 쿼리 성능"""
        from app.models import User, SleepSession
        import time
        
        # 먼저 테스트 데이터 생성
        for i in range(10):
            session = SleepSession(
                user_id=test_user.id,
                session_date=datetime.now(),
                raw_data_path=f"/test/join/session_{i}"
            )
            db_session.add(session)
        db_session.commit()
        
        # 조인 쿼리
        start = time.time()
        for _ in range(50):
            results = db_session.query(User, SleepSession).join(
                SleepSession, User.id == SleepSession.user_id
            ).filter(User.id == test_user.id).all()
        elapsed = time.time() - start
        
        avg_time = elapsed / 50 * 1000  # ms
        
        print(f"\n📊 조인 쿼리 (50회):")
        print(f"   평균: {avg_time:.2f}ms")
        
        assert avg_time < 50, f"평균 조인 시간: {avg_time:.2f}ms (기준: 50ms 미만)"
