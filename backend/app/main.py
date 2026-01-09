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


app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# 에러 처리
@app.exception_handler(RequestValidationError)
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


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 에러 핸들러"""
    logger.error(f"예상치 못한 에러: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "내부 서버 에러", "message": "예상치 못한 오류가 발생했습니다"},
    )


# 헬스 체크 엔드포인트
@app.get("/", tags=["Health"])
async def root():
    """루트 엔드포인트"""
    return {
        "status": "ok",
        "message": "SleepFM Backend API is running",
        "version": settings.project_version,
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": settings.project_name,
        "version": settings.project_version,
    }


# 라우트 임포트 (추후 추가)
# from app.routes import auth, sessions, analysis


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
