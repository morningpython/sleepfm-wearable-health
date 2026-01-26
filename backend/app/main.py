import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import setup_logging, settings
from app.database import Base, engine

# 로깅 설정
setup_logging()
logger = logging.getLogger("app")

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🚀 SleepFM Backend API 시작")
    yield
    logger.info("🛑 SleepFM Backend API 종료")


# 라우터 import를 app 생성 전에 수행
from app.routes import auth, sessions, analysis


def create_app(enable_lifespan: bool = True) -> FastAPI:
    """FastAPI 애플리케이션 팩토리"""
    app_instance = FastAPI(
        title=settings.project_name,
        version=settings.project_version,
        debug=settings.debug,
        lifespan=lifespan if enable_lifespan else None,
    )

    # 라우트 등록 (MUST be before any other decorators/handlers)
    app_instance.include_router(auth.router, prefix=settings.api_prefix)
    app_instance.include_router(sessions.router, prefix=settings.api_prefix)
    app_instance.include_router(analysis.router)

    # CORS 미들웨어
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    # 에러 처리
    @app_instance.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """요청 검증 에러 핸들러"""
        logger.warning(f"요청 검증 실패: {exc}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "message": "요청 데이터가 유효하지 않습니다",
            },
        )

    @app_instance.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """일반 에러 핸들러"""
        logger.error(f"예상치 못한 에러: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "내부 서버 에러", "message": "예상치 못한 오류가 발생했습니다"},
        )

    # 헬스 체크 엔드포인트
    @app_instance.get("/", tags=["Health"])
    async def root():
        """루트 엔드포인트"""
        return {
            "status": "ok",
            "message": "SleepFM Backend API is running",
            "version": settings.project_version,
        }

    @app_instance.get("/api/v1/health", tags=["Health"])
    async def health_check():
        """헬스 체크 엔드포인트"""
        return {
            "status": "healthy",
            "service": settings.project_name,
            "version": settings.project_version,
        }
    
    return app_instance


# Create the default app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
