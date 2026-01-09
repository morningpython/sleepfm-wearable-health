"""
Alembic 마이그레이션 환경 설정

사용법:
    alembic init migrations  # 초기 설정 (이미 완료)
    alembic revision --autogenerate -m "Add users table"  # 마이그레이션 파일 생성
    alembic upgrade head  # 마이그레이션 실행
    alembic current  # 현재 버전 확인
    alembic history --indicate-current  # 마이그레이션 이력 확인
    alembic downgrade -1  # 한 버전 롤백
"""
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 현재 스크립트의 Config 객체 가져오기
config = context.config

# 파일 기반 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# 마이그레이션을 위한 모델의 메타데이터 가져오기
from app.models import Base  # noqa: E402

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    'offline' 모드에서 마이그레이션을 실행합니다.

    이 모드는 엔진 생성 없이 SQL을 생성하고 출력합니다.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    'online' 모드에서 마이그레이션을 실행합니다.

    이 모드는 데이터베이스 엔진을 생성하고 연결합니다.
    """

    def process_revision_directives(context, revision, directives):
        if config.cmd_opts and getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("변경사항이 없습니다")

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")
    engine = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
