import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

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
from app.routes import auth, sessions, analysis, history


def create_app(enable_lifespan: bool = True) -> FastAPI:
    """FastAPI 애플리케이션 팩토리"""
    app_instance = FastAPI(
        title=settings.project_name,
        description="""
## SleepFM Backend API

**SleepFM**은 웨어러블 디바이스 데이터를 활용한 AI 기반 수면 분석 플랫폼입니다.

### 주요 기능

* 🔐 **인증 시스템**: JWT 기반 사용자 인증 (Access/Refresh Token)
* 📊 **수면 세션 관리**: Apple Health Kit, Google Fit 데이터 동기화
* 🤖 **AI 수면 분석**: 머신러닝 기반 수면 품질 예측 및 인사이트
* 📈 **대시보드**: 수면 트렌드 및 통계 조회

### 인증

대부분의 API는 Bearer Token 인증이 필요합니다:

```
Authorization: Bearer <access_token>
```

Access Token이 만료되면 `/api/v1/auth/refresh` 엔드포인트를 사용하여 갱신하세요.

### Rate Limiting

- 일반 API: 100 requests / minute
- 인증 API: 5 requests / minute

### 문의

- GitHub: [sleepfm/sleepfm-wearable-health](https://github.com/sleepfm/sleepfm-wearable-health)
- Email: support@sleepfm.io
        """,
        version=settings.project_version,
        debug=settings.debug,
        lifespan=lifespan if enable_lifespan else None,
        contact={
            "name": "SleepFM Support",
            "email": "support@sleepfm.io",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_tags=[
            {
                "name": "Health",
                "description": "헬스 체크 및 서비스 상태 확인 엔드포인트",
            },
            {
                "name": "Auth",
                "description": "사용자 인증 관련 엔드포인트 (회원가입, 로그인, 토큰 갱신)",
            },
            {
                "name": "Sessions",
                "description": "수면 세션 CRUD 및 데이터 동기화 엔드포인트",
            },
            {
                "name": "Analysis",
                "description": "AI 기반 수면 분석 및 예측 엔드포인트",
            },
            {
                "name": "History",
                "description": "수면 히스토리 및 통계 조회 엔드포인트",
            },
        ],
    )

    # 라우트 등록 (MUST be before any other decorators/handlers)
    app_instance.include_router(auth.router, prefix=settings.api_prefix)
    app_instance.include_router(sessions.router, prefix=settings.api_prefix)
    app_instance.include_router(analysis.router)
    app_instance.include_router(history.router)  # Story 4.4

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

    @app_instance.get("/health", tags=["Health"], include_in_schema=False)
    async def health():
        """Docker/K8s 헬스체크용 엔드포인트"""
        return {"status": "ok"}
    
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
