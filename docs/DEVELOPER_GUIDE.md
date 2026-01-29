# SleepFM Developer Guide

> AI 기반 수면 분석 플랫폼 SleepFM의 개발자 가이드

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [아키텍처](#아키텍처)
3. [개발 환경 설정](#개발-환경-설정)
4. [프로젝트 구조](#프로젝트-구조)
5. [코드 스타일](#코드-스타일)
6. [테스트](#테스트)
7. [API 문서](#api-문서)
8. [기여 가이드](#기여-가이드)

---

## 프로젝트 개요

**SleepFM**은 웨어러블 디바이스(Apple Watch, Galaxy Watch 등)에서 수집된 건강 데이터를 분석하여 개인화된 수면 인사이트를 제공하는 AI 기반 플랫폼입니다.

### 핵심 기능

| 기능 | 설명 |
|------|------|
| 🔐 사용자 인증 | JWT 기반 인증 (Access/Refresh Token) |
| 📱 데이터 동기화 | Apple Health Kit, Google Fit 연동 |
| 🤖 AI 분석 | 머신러닝 기반 수면 품질 예측 |
| 📊 대시보드 | 수면 트렌드 및 통계 시각화 |
| 🔔 알림 | 수면 개선 권장사항 푸시 알림 |

### 기술 스택

```
Backend:
├── Python 3.11+
├── FastAPI
├── SQLAlchemy (ORM)
├── PostgreSQL 15
├── Redis 7 (캐싱)
├── Celery (비동기 작업)
└── Docker

ML/Data:
├── PyTorch
├── scikit-learn
├── pandas
└── numpy

Monitoring:
├── Prometheus
├── Grafana
└── Sentry
```

---

## 아키텍처

### 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                │
├─────────────────────────────────────────────────────────────────────┤
│     iOS App          │     Android App      │     Web Dashboard      │
│  (Swift/SwiftUI)     │    (Kotlin/Compose)  │     (React/Next.js)    │
└──────────┬───────────┴──────────┬───────────┴──────────┬────────────┘
           │                      │                      │
           └──────────────────────┼──────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │        Nginx (LB)         │
                    │    Rate Limiting / SSL     │
                    └─────────────┬─────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
    ┌─────────▼─────────┐ ┌───────▼───────┐ ┌────────▼────────┐
    │   FastAPI Server  │ │ Celery Worker │ │  Celery Beat    │
    │   (REST API)      │ │ (Background)  │ │  (Scheduler)    │
    └─────────┬─────────┘ └───────┬───────┘ └────────┬────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
┌────────▼────────┐    ┌──────────▼──────────┐    ┌───────▼───────┐
│   PostgreSQL    │    │       Redis         │    │  ML Models    │
│   (Primary DB)  │    │   (Cache/Broker)    │    │   (PyTorch)   │
└─────────────────┘    └─────────────────────┘    └───────────────┘
```

### 데이터 흐름

```
1. 수면 데이터 동기화
   Mobile App → HealthKit/GoogleFit → REST API → PostgreSQL

2. AI 분석 요청
   API Request → Celery Task → ML Model → Cache → Response

3. 대시보드 조회
   Request → Cache Check → DB Query → Response (+ Cache Update)
```

---

## 개발 환경 설정

### 필수 요구사항

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (또는 Docker로 실행)
- Redis 7+ (또는 Docker로 실행)

### 로컬 개발 환경 설정

#### 1. 저장소 클론

```bash
git clone https://github.com/sleepfm/sleepfm-wearable-health.git
cd sleepfm-wearable-health/backend
```

#### 2. Python 가상환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 활성화 (macOS/Linux)
source venv/bin/activate

# 활성화 (Windows)
.\venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 3. 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp .env.example .env

# .env 파일을 편집하여 필요한 값 설정
```

#### 4. Docker로 서비스 실행

```bash
# 모든 서비스 실행 (PostgreSQL, Redis, etc.)
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f backend
```

#### 5. 데이터베이스 마이그레이션

```bash
# Alembic 마이그레이션 실행
alembic upgrade head

# 새 마이그레이션 생성 (모델 변경 시)
alembic revision --autogenerate -m "Add new feature"
```

#### 6. 개발 서버 실행

```bash
# 개발 서버 시작 (핫 리로드 활성화)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 Docker로 실행
docker-compose up backend
```

### API 문서 접근

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 프로젝트 구조

```
backend/
├── app/                        # 메인 애플리케이션
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 설정 관리
│   ├── database.py             # DB 연결 설정
│   ├── dependencies.py         # FastAPI 의존성
│   │
│   ├── models/                 # SQLAlchemy 모델
│   │   ├── __init__.py
│   │   ├── user.py             # 사용자 모델
│   │   ├── session.py          # 수면 세션 모델
│   │   └── analysis.py         # 분석 결과 모델
│   │
│   ├── schemas/                # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── auth.py             # 인증 스키마
│   │   └── sessions.py         # 세션 스키마
│   │
│   ├── routes/                 # API 라우트
│   │   ├── __init__.py
│   │   ├── auth.py             # 인증 엔드포인트
│   │   ├── sessions.py         # 세션 엔드포인트
│   │   ├── analysis.py         # 분석 엔드포인트
│   │   └── history.py          # 히스토리 엔드포인트
│   │
│   ├── middleware/             # 미들웨어
│   │   └── rate_limiter.py     # Rate Limiting
│   │
│   ├── ml/                     # 머신러닝 모델
│   │   ├── models/             # 학습된 모델
│   │   ├── training/           # 학습 스크립트
│   │   └── inference/          # 추론 로직
│   │
│   ├── preprocessing/          # 데이터 전처리
│   │   └── sleep_data.py       # 수면 데이터 처리
│   │
│   ├── tasks/                  # Celery 태스크
│   │   ├── __init__.py
│   │   └── analysis.py         # 분석 태스크
│   │
│   └── utils/                  # 유틸리티
│       ├── __init__.py
│       └── security.py         # 보안 유틸리티
│
├── migrations/                 # Alembic 마이그레이션
│   ├── env.py
│   ├── script.py.mako
│   └── versions/               # 마이그레이션 버전
│
├── tests/                      # 테스트
│   ├── __init__.py
│   ├── conftest.py             # Pytest 설정
│   ├── test_auth.py            # 인증 테스트
│   ├── test_sessions.py        # 세션 테스트
│   └── integration/            # 통합 테스트
│
├── monitoring/                 # 모니터링 설정
│   ├── prometheus.yml          # Prometheus 설정
│   └── grafana/                # Grafana 대시보드
│
├── nginx/                      # Nginx 설정
│   └── nginx.conf
│
├── .env.example                # 환경 변수 예시
├── docker-compose.yml          # 개발용 Docker Compose
├── docker-compose.prod.yml     # 프로덕션 Docker Compose
├── Dockerfile                  # Docker 이미지
├── requirements.txt            # 프로덕션 의존성
├── requirements-dev.txt        # 개발 의존성
├── pyproject.toml              # Python 프로젝트 설정
└── alembic.ini                 # Alembic 설정
```

---

## 코드 스타일

### Python 코드 스타일

SleepFM은 일관된 코드 스타일을 유지하기 위해 다음 도구들을 사용합니다:

| 도구 | 용도 |
|------|------|
| **Ruff** | 린팅 (linting) |
| **Black** | 코드 포맷팅 |
| **isort** | import 정렬 |
| **mypy** | 타입 체킹 |

### 코드 검사 실행

```bash
# 린팅
ruff check app tests

# 포맷팅 (자동 수정)
black app tests
isort app tests

# 타입 체킹
mypy app

# 전체 검사 (CI에서 실행되는 것과 동일)
ruff check app tests && black --check app tests && isort --check-only app tests && mypy app
```

### 명명 규칙

```python
# 클래스: PascalCase
class SleepSession:
    pass

# 함수/메서드: snake_case
def calculate_sleep_quality():
    pass

# 변수: snake_case
sleep_duration = 480

# 상수: SCREAMING_SNAKE_CASE
MAX_RETRY_COUNT = 3

# 비공개 멤버: _prefix
def _internal_helper():
    pass
```

### Docstring 스타일

```python
def analyze_sleep_data(
    session_id: int,
    include_insights: bool = True
) -> SleepAnalysisResult:
    """
    수면 세션 데이터를 분석하여 인사이트를 생성합니다.

    Args:
        session_id: 분석할 수면 세션의 ID
        include_insights: AI 인사이트 포함 여부

    Returns:
        SleepAnalysisResult: 분석 결과 객체

    Raises:
        SessionNotFoundError: 세션을 찾을 수 없는 경우
        AnalysisFailedError: 분석 중 오류가 발생한 경우

    Example:
        >>> result = analyze_sleep_data(session_id=123)
        >>> print(result.quality_score)
        85.5
    """
    pass
```

---

## 테스트

### 테스트 구조

```
tests/
├── conftest.py             # 공통 fixture
├── test_auth.py            # 단위 테스트: 인증
├── test_sessions.py        # 단위 테스트: 세션
├── test_analysis.py        # 단위 테스트: 분석
├── integration/
│   ├── test_api_flow.py    # 통합 테스트: API 흐름
│   └── test_db.py          # 통합 테스트: DB
└── e2e/
    └── test_full_flow.py   # E2E 테스트
```

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 파일/디렉토리
pytest tests/test_auth.py
pytest tests/integration/

# 커버리지 포함
pytest --cov=app --cov-report=html

# 병렬 실행 (빠름)
pytest -n auto

# 특정 마커
pytest -m "not slow"
pytest -m integration

# 자세한 출력
pytest -v --tb=short
```

### Fixture 사용 예시

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

@pytest.fixture
def client(db_session):
    """테스트 클라이언트"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """테스트용 사용자"""
    from app.models.user import User
    user = User(email="test@example.com", hashed_password="...")
    db_session.add(user)
    db_session.commit()
    return user
```

### 테스트 작성 예시

```python
# tests/test_auth.py
import pytest
from fastapi import status

class TestAuth:
    """인증 API 테스트"""

    def test_register_success(self, client):
        """회원가입 성공 테스트"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "password": "StrongPassword123!",
                "username": "newuser"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "access_token" in response.json()

    def test_login_invalid_credentials(self, client):
        """잘못된 자격증명으로 로그인 실패 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "wrong"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    def test_token_refresh_flow(self, client, test_user):
        """토큰 갱신 통합 테스트"""
        # ... 테스트 구현
        pass
```

---

## API 문서

### 인증 (Auth)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/auth/register` | 회원가입 |
| POST | `/api/v1/auth/login` | 로그인 |
| POST | `/api/v1/auth/refresh` | 토큰 갱신 |
| POST | `/api/v1/auth/logout` | 로그아웃 |
| GET | `/api/v1/auth/me` | 현재 사용자 정보 |

### 수면 세션 (Sessions)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/sessions` | 세션 목록 조회 |
| POST | `/api/v1/sessions` | 새 세션 생성 |
| GET | `/api/v1/sessions/{id}` | 세션 상세 조회 |
| PUT | `/api/v1/sessions/{id}` | 세션 수정 |
| DELETE | `/api/v1/sessions/{id}` | 세션 삭제 |
| POST | `/api/v1/sessions/sync` | 데이터 동기화 |

### 분석 (Analysis)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/analysis/{session_id}` | 세션 분석 결과 |
| POST | `/api/v1/analysis/predict` | 수면 품질 예측 |
| GET | `/api/v1/analysis/insights` | AI 인사이트 조회 |

### 히스토리 (History)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/history` | 수면 히스토리 |
| GET | `/api/v1/history/stats` | 통계 조회 |
| GET | `/api/v1/history/trends` | 트렌드 분석 |

---

## 기여 가이드

### 브랜치 전략

```
main (production)
│
├── develop (integration)
│   │
│   ├── feature/xxx    # 새 기능
│   ├── bugfix/xxx     # 버그 수정
│   ├── hotfix/xxx     # 긴급 수정
│   └── sprint-xx-xxx  # 스프린트 작업
```

### 커밋 메시지 규칙

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 스타일 변경
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

**예시:**
```
feat(auth): Add refresh token rotation

Implement automatic rotation of refresh tokens
to improve security. Old tokens are invalidated
after successful refresh.

Closes #123
```

### Pull Request 프로세스

1. **브랜치 생성**: `feature/xxx` 또는 `bugfix/xxx`
2. **개발 진행**: 코드 작성 및 테스트
3. **코드 검사**: `ruff`, `black`, `mypy` 실행
4. **PR 생성**: 템플릿에 따라 작성
5. **코드 리뷰**: 최소 1명의 승인 필요
6. **CI 통과**: 모든 테스트 및 검사 통과
7. **머지**: Squash and Merge 사용

### PR 템플릿

```markdown
## 변경 사항
- 

## 관련 이슈
- Closes #

## 테스트
- [ ] 단위 테스트 추가/수정
- [ ] 통합 테스트 추가/수정
- [ ] 수동 테스트 완료

## 체크리스트
- [ ] 코드 스타일 검사 통과
- [ ] 문서 업데이트 (필요시)
- [ ] 마이그레이션 추가 (필요시)
```

---

## 문의 및 지원

- **GitHub Issues**: [버그 리포트 및 기능 요청](https://github.com/sleepfm/sleepfm-wearable-health/issues)
- **Email**: support@sleepfm.io
- **Slack**: #sleepfm-dev (팀 내부)

---

*마지막 업데이트: 2024년 1월*
