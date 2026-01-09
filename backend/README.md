# SleepFM Backend

ML 추론 기반 수면 분석 및 질병 위험 예측 API 서비스

## 🚀 빠른 시작

### 전제 조건
- Python 3.10+
- Poetry (또는 pip)
- PostgreSQL 14+
- Docker & Docker Compose (권장)

### 설치

#### 방법 1: Poetry 사용 (권장)
```bash
# 의존성 설치
poetry install

# 활성화
poetry shell
```

#### 방법 2: pip 사용
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 개발 환경 설정

#### 1. Pre-commit 설치
```bash
pre-commit install
```

#### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일 편집하여 설정값 입력
```

#### 3. 데이터베이스 실행
```bash
docker-compose up -d postgres
```

#### 4. 마이그레이션 실행
```bash
alembic upgrade head
```

#### 5. 서버 실행
```bash
uvicorn app.main:app --reload
```

### API 문서 접근
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 설정
│   ├── models/                 # SQLAlchemy 모델
│   ├── schemas/                # Pydantic 스키마
│   ├── routes/                 # API 라우트
│   ├── dependencies.py         # 의존성 주입
│   ├── middleware/             # 미들웨어
│   ├── utils/                  # 유틸리티 함수
│   ├── preprocessing/          # 데이터 전처리
│   ├── ml/                     # ML 모델 로직
│   └── database.py             # DB 설정
├── tests/                      # 테스트
├── migrations/                 # Alembic 마이그레이션
├── pyproject.toml             # Poetry 설정
├── .env.example               # 환경 변수 예시
├── docker-compose.yml         # Docker Compose 설정
└── Dockerfile                 # Docker 빌드 설정
```

## 🧪 테스트 실행

```bash
# 전체 테스트
pytest

# 커버리지 포함
pytest --cov=app

# 특정 테스트 파일
pytest tests/test_auth.py

# 특정 테스트 함수
pytest tests/test_auth.py::test_user_registration
```

## 📝 코드 스타일

이 프로젝트는 다음 도구를 사용합니다:
- **Black**: 코드 포맷팅
- **Ruff**: 린팅
- **MyPy**: 타입 체크
- **Pre-commit**: 자동 검사

모든 커밋 전에 자동으로 실행됩니다.

## 🔧 문제 해결

### 포트 이미 사용 중
```bash
# 다른 포트 사용
uvicorn app.main:app --port 8001
```

### 데이터베이스 연결 실패
```bash
# PostgreSQL 상태 확인
docker-compose ps

# PostgreSQL 로그 확인
docker-compose logs postgres
```

### 마이그레이션 문제
```bash
# 마이그레이션 현재 버전 확인
alembic current

# 마이그레이션 이력 확인
alembic history --indicate-current
```

## 📚 개발 가이드

### 새 User Story 시작
1. 브랜치 생성: `feature/{story-id}-{description}`
2. 코드 작성
3. 테스트 작성 (TDD 권장)
4. Pre-commit 검사 통과
5. PR 제출

### 커밋 메시지 규칙
```
<type>(<scope>): <subject>

<body>

<footer>
```

예시:
```
feat(backend): implement user registration endpoint

- Add POST /api/v1/auth/register endpoint
- Hash passwords using bcrypt
- Validate email format

Story: 1.1
Closes #1
```

## 🔗 참고 문서
- [SleepFM 논문](https://www.nature.com/articles/s41591-025-04133-4)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [GitHub Strategy](../docs/GITHUB_STRATEGY.md)
- [Sprint Plan Phase 1](../docs/SPRINT_PLAN_PHASE1.md)

## 📞 문의
프로젝트 관련 문의는 GitHub Issues를 통해 진행합니다.
