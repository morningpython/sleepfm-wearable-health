"""데이터베이스 인덱스 최적화 마이그레이션

이 마이그레이션은 자주 쿼리되는 컬럼에 인덱스를 추가합니다.

Revision ID: add_performance_indexes
Revises: 
Create Date: 2026-01-28
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """인덱스 추가"""
    
    # ========================================
    # users 테이블 인덱스
    # ========================================
    
    # 이메일 검색 최적화 (로그인 시 사용)
    op.create_index(
        'ix_users_email_lower',
        'users',
        [sa.text('lower(email)')],
        unique=True,
        postgresql_using='btree'
    )
    
    # 활성 사용자 필터링
    op.create_index(
        'ix_users_is_active',
        'users',
        ['is_active'],
        postgresql_using='btree'
    )
    
    # 생성일 기준 정렬
    op.create_index(
        'ix_users_created_at',
        'users',
        ['created_at'],
        postgresql_using='btree'
    )
    
    # ========================================
    # sleep_sessions 테이블 인덱스
    # ========================================
    
    # 사용자별 세션 조회 (가장 빈번한 쿼리)
    op.create_index(
        'ix_sleep_sessions_user_id',
        'sleep_sessions',
        ['user_id'],
        postgresql_using='btree'
    )
    
    # 날짜별 세션 조회
    op.create_index(
        'ix_sleep_sessions_session_date',
        'sleep_sessions',
        ['session_date'],
        postgresql_using='btree'
    )
    
    # 사용자 + 날짜 복합 인덱스 (대부분의 세션 조회에 사용)
    op.create_index(
        'ix_sleep_sessions_user_date',
        'sleep_sessions',
        ['user_id', 'session_date'],
        postgresql_using='btree'
    )
    
    # 분석 상태별 필터링
    op.create_index(
        'ix_sleep_sessions_analysis_status',
        'sleep_sessions',
        ['analysis_status'],
        postgresql_using='btree'
    )
    
    # 최근 세션 조회 (user_id + created_at DESC)
    op.create_index(
        'ix_sleep_sessions_user_created',
        'sleep_sessions',
        ['user_id', sa.text('created_at DESC')],
        postgresql_using='btree'
    )
    
    # ========================================
    # sleep_analyses 테이블 인덱스 (존재 시)
    # ========================================
    
    try:
        # 세션별 분석 결과 조회
        op.create_index(
            'ix_sleep_analyses_session_id',
            'sleep_analyses',
            ['session_id'],
            postgresql_using='btree'
        )
        
        # 분석 타입별 조회
        op.create_index(
            'ix_sleep_analyses_analysis_type',
            'sleep_analyses',
            ['analysis_type'],
            postgresql_using='btree'
        )
        
        # 세션 + 분석 타입 복합 인덱스
        op.create_index(
            'ix_sleep_analyses_session_type',
            'sleep_analyses',
            ['session_id', 'analysis_type'],
            postgresql_using='btree'
        )
    except Exception:
        # 테이블이 없으면 무시
        pass
    
    # ========================================
    # apnea_events 테이블 인덱스 (존재 시)
    # ========================================
    
    try:
        # 세션별 무호흡 이벤트 조회
        op.create_index(
            'ix_apnea_events_session_id',
            'apnea_events',
            ['session_id'],
            postgresql_using='btree'
        )
        
        # 이벤트 타입별 조회
        op.create_index(
            'ix_apnea_events_event_type',
            'apnea_events',
            ['event_type'],
            postgresql_using='btree'
        )
        
        # 시간 범위 조회
        op.create_index(
            'ix_apnea_events_timestamp',
            'apnea_events',
            ['timestamp'],
            postgresql_using='btree'
        )
    except Exception:
        pass
    
    # ========================================
    # disease_risk_predictions 테이블 인덱스 (존재 시)
    # ========================================
    
    try:
        # 세션별 질병 위험 예측 조회
        op.create_index(
            'ix_disease_risk_session_id',
            'disease_risk_predictions',
            ['session_id'],
            postgresql_using='btree'
        )
        
        # 사용자별 예측 히스토리
        op.create_index(
            'ix_disease_risk_user_id',
            'disease_risk_predictions',
            ['user_id'],
            postgresql_using='btree'
        )
        
        # 질병 타입별 조회
        op.create_index(
            'ix_disease_risk_disease_type',
            'disease_risk_predictions',
            ['disease_type'],
            postgresql_using='btree'
        )
    except Exception:
        pass


def downgrade():
    """인덱스 제거"""
    
    # users 테이블 인덱스
    op.drop_index('ix_users_email_lower', table_name='users')
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_created_at', table_name='users')
    
    # sleep_sessions 테이블 인덱스
    op.drop_index('ix_sleep_sessions_user_id', table_name='sleep_sessions')
    op.drop_index('ix_sleep_sessions_session_date', table_name='sleep_sessions')
    op.drop_index('ix_sleep_sessions_user_date', table_name='sleep_sessions')
    op.drop_index('ix_sleep_sessions_analysis_status', table_name='sleep_sessions')
    op.drop_index('ix_sleep_sessions_user_created', table_name='sleep_sessions')
    
    # 선택적 테이블 인덱스
    try:
        op.drop_index('ix_sleep_analyses_session_id', table_name='sleep_analyses')
        op.drop_index('ix_sleep_analyses_analysis_type', table_name='sleep_analyses')
        op.drop_index('ix_sleep_analyses_session_type', table_name='sleep_analyses')
    except Exception:
        pass
    
    try:
        op.drop_index('ix_apnea_events_session_id', table_name='apnea_events')
        op.drop_index('ix_apnea_events_event_type', table_name='apnea_events')
        op.drop_index('ix_apnea_events_timestamp', table_name='apnea_events')
    except Exception:
        pass
    
    try:
        op.drop_index('ix_disease_risk_session_id', table_name='disease_risk_predictions')
        op.drop_index('ix_disease_risk_user_id', table_name='disease_risk_predictions')
        op.drop_index('ix_disease_risk_disease_type', table_name='disease_risk_predictions')
    except Exception:
        pass
