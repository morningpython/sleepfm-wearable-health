# Sprint Plan - Phase 1
## ML 백엔드 구축 (Sprint 1-4)

**문서 버전:** 1.0  
**작성일:** 2026년 1월 8일  
**Phase 기간:** 8주 (Sprint 1-4)  
**Phase 목표:** SleepFM 모델 기반 분석 API 서비스 구축

---

## 목차
1. [Phase 1 개요](#phase-1-개요)
2. [Epic 정의](#epic-정의)
3. [Sprint 1: 인프라 및 데이터 파이프라인](#sprint-1-인프라-및-데이터-파이프라인)
4. [Sprint 2: 모델 통합 및 전처리](#sprint-2-모델-통합-및-전처리)
5. [Sprint 3: 수면 분석 기능](#sprint-3-수면-분석-기능)
6. [Sprint 4: 질병 예측 API](#sprint-4-질병-예측-api)
7. [Phase 1 완료 기준](#phase-1-완료-기준)

---

## Phase 1 개요

### 목표
웨어러블 데이터를 입력받아 수면 분석 및 질병 위험 예측을 수행하는 REST API 서비스 구축

### 주요 결과물
- ✅ FastAPI 기반 REST API 서버
- ✅ 데이터 전처리 파이프라인
- ✅ SleepFM 모델 추론 엔진
- ✅ 수면 단계 분류 기능
- ✅ 질병 위험 예측 기능
- ✅ PostgreSQL 데이터베이스
- ✅ 인증/인가 시스템

### 팀 구성
- **Backend Lead**: 1명
- **ML Engineer**: 1-2명
- **DevOps Engineer**: 0.5명 (파트타임)

---

## Epic 정의

### Epic 1: 백엔드 인프라 구축
**설명**: API 서버, 데이터베이스, 인증 시스템 등 기본 인프라 구축  
**비즈니스 가치**: 모든 기능의 기반이 되는 안정적인 서비스 인프라 확보  
**완료 조건**: 
- FastAPI 서버 실행 가능
- PostgreSQL 연결 및 마이그레이션 완료
- JWT 기반 인증 시스템 동작
- Docker 컨테이너화 완료

---

### Epic 2: 데이터 파이프라인 구축
**설명**: 웨어러블 센서 데이터를 모델 입력 형식으로 변환하는 전처리 파이프라인  
**비즈니스 가치**: 다양한 웨어러블 기기 데이터를 통일된 형식으로 처리  
**완료 조건**:
- 심박수, 호흡률, 가속도 데이터 전처리 완료
- 128Hz 리샘플링 구현
- 5초 윈도우 토큰화 완료
- 노이즈 필터링 적용

---

### Epic 3: SleepFM 모델 통합
**설명**: SleepFM 파운데이션 모델을 API 서비스에 통합  
**비즈니스 가치**: 검증된 최신 수면 분석 모델 활용  
**완료 조건**:
- SleepFM 가중치 로딩 성공
- 멀티모달 임베딩 추출 가능
- 추론 시간 < 10초 (8시간 데이터 기준)
- GPU 활용 최적화 완료

---

### Epic 4: 수면 분석 기능
**설명**: 수면 단계 분류 및 수면무호흡 탐지 기능  
**비즈니스 가치**: 사용자에게 기본적인 수면 품질 정보 제공  
**완료 조건**:
- 5단계 수면 분류 (Wake, N1, N2, N3, REM)
- F1 Score ≥ 0.70 달성
- 무호흡 이벤트 탐지
- AHI 점수 산출

---

### Epic 5: 질병 위험 예측
**설명**: 5개 주요 질환에 대한 위험 스코어 산출  
**비즈니스 가치**: 조기 질병 예측을 통한 건강관리 가치 제공  
**완료 조건**:
- 파킨슨병, 치매, 심근경색, 심부전, 뇌졸중 예측 모델 구현
- C-Index ≥ 0.75 달성
- 위험도 카테고리 분류 (Low/Medium/High)
- 신뢰 구간 계산

---

## Sprint 1: 인프라 및 데이터 파이프라인
**기간**: 2주 (Week 1-2)  
**Sprint 목표**: 기본 API 서버 및 데이터베이스 인프라 구축  
**총 Story Points**: 21

---

### 📘 User Story 1.1: 프로젝트 환경 설정
**Epic**: Epic 1 - 백엔드 인프라 구축  
**Story Points**: 3

**As a** Backend Developer  
**I want to** 프로젝트 개발 환경을 설정  
**So that** 팀원들이 동일한 환경에서 개발할 수 있다

**Description**:
- Python 3.10+ 환경 구성
- Poetry 또는 Conda를 사용한 의존성 관리
- pre-commit hooks 설정 (black, flake8, mypy)
- .gitignore 설정
- README 및 개발 가이드 작성

**Acceptance Criteria**:
- [ ] `backend/pyproject.toml` 또는 `backend/env.yml` 생성 완료
- [ ] 필수 라이브러리 설치 가능 (FastAPI, PyTorch, SQLAlchemy 등)
- [ ] pre-commit 실행 시 코드 포맷팅 자동 적용
- [ ] 새로운 개발자가 30분 내 환경 설정 가능

**Tasks**:
- [ ] Poetry 프로젝트 초기화
- [ ] 기본 의존성 추가 (fastapi, uvicorn, sqlalchemy, psycopg2, pydantic)
- [ ] ML 의존성 추가 (torch, numpy, scipy, scikit-learn)
- [ ] pre-commit 설정 파일 작성
- [ ] 개발 가이드 문서 작성

**Testing**:
- Unit Test: N/A
- Component Test: N/A
- E2E Test: N/A

---

### 📘 User Story 1.2: FastAPI 기본 서버 구축
**Epic**: Epic 1 - 백엔드 인프라 구축  
**Story Points**: 5

**As a** Backend Developer  
**I want to** FastAPI 기반 REST API 서버를 구축  
**So that** 클라이언트가 HTTP 요청을 보낼 수 있다

**Description**:
- FastAPI 앱 초기화
- 기본 라우팅 구조 설정 (auth, analysis, health)
- CORS 미들웨어 설정
- 에러 핸들링 미들웨어
- 요청/응답 로깅
- Swagger 문서 자동 생성

**Acceptance Criteria**:
- [ ] `GET /api/v1/health` 엔드포인트 정상 응답
- [ ] Swagger UI 접근 가능 (`/docs`)
- [ ] CORS 설정으로 모든 origin 허용 (개발 환경)
- [ ] 400/500 에러 시 일관된 JSON 형식 응답
- [ ] 모든 요청/응답이 구조화된 로그로 기록됨

**Tasks**:
- [ ] `backend/api/main.py` 생성 및 FastAPI 앱 초기화
- [ ] `backend/api/routes/` 디렉토리 구조 생성
- [ ] 미들웨어 설정 (CORS, 로깅, 에러 핸들링)
- [ ] `/health` 엔드포인트 구현
- [ ] Pydantic 기본 응답 모델 정의

**Testing**:
- Unit Test: 미들웨어 로직 테스트
- Component Test: `/health` 엔드포인트 응답 검증
- E2E Test: Swagger UI 접근 및 문서 생성 확인

---

### 📘 User Story 1.3: PostgreSQL 데이터베이스 설정
**Epic**: Epic 1 - 백엔드 인프라 구축  
**Story Points**: 5

**As a** Backend Developer  
**I want to** PostgreSQL 데이터베이스를 설정하고 연결  
**So that** 사용자 및 수면 데이터를 영구 저장할 수 있다

**Description**:
- Docker Compose로 PostgreSQL 컨테이너 실행
- SQLAlchemy ORM 설정
- Alembic 마이그레이션 도구 설정
- 기본 테이블 스키마 정의 (Users, SleepSessions)
- 데이터베이스 연결 풀 설정

**Acceptance Criteria**:
- [ ] `docker-compose up` 실행 시 PostgreSQL 컨테이너 시작
- [ ] SQLAlchemy를 통한 DB 연결 성공
- [ ] Alembic 마이그레이션 실행 가능
- [ ] Users, SleepSessions 테이블 생성 확인
- [ ] 연결 풀 최대 10개 유지

**Tasks**:
- [ ] `docker-compose.yml` 생성 (PostgreSQL 14)
- [ ] SQLAlchemy Base 모델 설정
- [ ] `models/user.py`, `models/sleep_session.py` 생성
- [ ] Alembic 초기화 및 첫 마이그레이션 생성
- [ ] 데이터베이스 세션 관리 유틸리티 작성

**Testing**:
- Unit Test: 모델 정의 검증 (필드, 관계)
- Component Test: CRUD 작업 테스트 (Create, Read, Update, Delete)
- E2E Test: 마이그레이션 실행 후 테이블 존재 확인

---

### 📘 User Story 1.4: JWT 인증 시스템 구현
**Epic**: Epic 1 - 백엔드 인프라 구축  
**Story Points**: 5

**As a** API User  
**I want to** JWT 토큰으로 안전하게 인증  
**So that** 내 데이터가 보호되고 권한이 관리된다

**Description**:
- JWT 토큰 생성/검증 유틸리티
- 회원가입 엔드포인트
- 로그인 엔드포인트 (토큰 발급)
- 비밀번호 해싱 (bcrypt)
- 토큰 기반 인증 미들웨어
- Access Token (15분), Refresh Token (7일) 구현

**Acceptance Criteria**:
- [ ] `POST /api/v1/auth/register` 회원가입 성공
- [ ] `POST /api/v1/auth/token` 로그인 시 JWT 발급
- [ ] 비밀번호는 bcrypt로 해싱되어 저장
- [ ] 보호된 엔드포인트는 유효한 토큰 없이 접근 불가 (401 응답)
- [ ] 만료된 토큰은 거부됨 (403 응답)

**Tasks**:
- [ ] JWT 유틸리티 함수 작성 (encode, decode, verify)
- [ ] 비밀번호 해싱 유틸리티 (bcrypt)
- [ ] `routes/auth.py` 생성
- [ ] 회원가입 엔드포인트 구현
- [ ] 로그인 엔드포인트 구현
- [ ] 인증 의존성 (Dependency) 작성
- [ ] Pydantic 스키마 정의 (UserCreate, Token)

**Testing**:
- Unit Test: JWT 토큰 생성/검증, 비밀번호 해싱
- Component Test: 회원가입/로그인 API 호출
- E2E Test: 전체 인증 플로우 (회원가입 → 로그인 → 보호된 API 접근)

---

### 📘 User Story 1.5: 센서 데이터 수집 API 엔드포인트
**Epic**: Epic 2 - 데이터 파이프라인 구축  
**Story Points**: 3

**As a** Mobile App  
**I want to** 웨어러블 센서 데이터를 서버에 업로드  
**So that** 백엔드에서 분석을 수행할 수 있다

**Description**:
- 센서 데이터 업로드 엔드포인트 생성
- JSON 형식 데이터 수신 (심박수, 호흡률, 가속도)
- 데이터 검증 (Pydantic)
- S3 또는 로컬 스토리지에 원시 데이터 저장
- SleepSessions 테이블에 메타데이터 저장

**Acceptance Criteria**:
- [ ] `POST /api/v1/sessions/upload` 엔드포인트 구현
- [ ] 필수 필드 누락 시 422 응답 (Validation Error)
- [ ] 센서 데이터가 S3/로컬에 JSON 파일로 저장됨
- [ ] SleepSessions 레코드 생성 확인
- [ ] 응답에 session_id 포함

**Tasks**:
- [ ] Pydantic 스키마 정의 (SensorDataUpload)
- [ ] `routes/sessions.py` 생성
- [ ] 업로드 엔드포인트 구현
- [ ] S3 또는 로컬 파일 저장 유틸리티
- [ ] SleepSession 생성 로직

**Testing**:
- Unit Test: Pydantic 검증 로직
- Component Test: 업로드 API 성공/실패 케이스
- E2E Test: 센서 데이터 업로드 → DB 레코드 확인 → 파일 저장 확인

---

### Sprint 1 완료 기준 (Definition of Done)
- [ ] 모든 User Story의 AC 충족
- [ ] 코드 리뷰 완료
- [ ] 단위 테스트 커버리지 ≥ 70%
- [ ] Swagger 문서 업데이트
- [ ] Docker Compose로 로컬 실행 가능
- [ ] Sprint Retrospective 회의 완료

---

## Sprint 2: 모델 통합 및 전처리
**기간**: 2주 (Week 3-4)  
**Sprint 목표**: SleepFM 모델 통합 및 데이터 전처리 파이프라인 구축  
**총 Story Points**: 21

---

### 📘 User Story 2.1: SleepFM 모델 가중치 로딩
**Epic**: Epic 3 - SleepFM 모델 통합  
**Story Points**: 5

**As a** ML Engineer  
**I want to** SleepFM 사전학습 가중치를 로드  
**So that** 파운데이션 모델을 추론에 사용할 수 있다

**Description**:
- SleepFM 공식 저장소에서 가중치 다운로드
- PyTorch 모델 클래스 정의
- 가중치 파일을 모델에 로딩
- 모델을 evaluation 모드로 설정
- GPU 사용 가능 시 자동 감지 및 활용

**Acceptance Criteria**:
- [ ] 가중치 파일 다운로드 및 경로 설정 완료
- [ ] 모델 로딩 시 에러 없음
- [ ] `model.eval()` 모드 설정
- [ ] GPU 사용 시 CUDA 메모리에 로딩
- [ ] 모델 입력/출력 shape 검증

**Tasks**:
- [ ] `models/sleepfm_encoder.py` 구현
- [ ] 가중치 다운로드 스크립트 작성
- [ ] 모델 로딩 유틸리티 함수 작성
- [ ] GPU/CPU 자동 감지 로직
- [ ] 모델 초기화 테스트

**Testing**:
- Unit Test: 모델 클래스 초기화 검증
- Component Test: 가중치 로딩 성공 여부
- E2E Test: 더미 입력으로 forward pass 실행

---

### 📘 User Story 2.2: 신호 전처리 파이프라인 구현
**Epic**: Epic 2 - 데이터 파이프라인 구축  
**Story Points**: 8

**As a** ML Engineer  
**I want to** 웨어러블 센서 데이터를 모델 입력 형식으로 전처리  
**So that** SleepFM 모델이 정확한 예측을 수행할 수 있다

**Description**:
- 다양한 샘플링 레이트를 128Hz로 리샘플링
- Butterworth 필터로 노이즈 제거
- 5초 윈도우로 토큰화
- 정규화 및 표준화
- 채널별 처리 (심박수, 호흡률, 가속도)
- NumPy 배열을 PyTorch 텐서로 변환

**Acceptance Criteria**:
- [ ] 입력 신호가 128Hz로 리샘플링됨
- [ ] 0.5-50Hz 대역 통과 필터 적용
- [ ] 5초 윈도우 (640 샘플) 토큰 생성
- [ ] 각 채널이 평균 0, 표준편차 1로 정규화
- [ ] 출력 텐서 shape: `(batch, channels, time_steps)`

**Tasks**:
- [ ] `preprocessing/resample.py` 구현
- [ ] `preprocessing/filter.py` 구현 (Butterworth)
- [ ] `preprocessing/tokenize.py` 구현 (윈도잉)
- [ ] `preprocessing/normalize.py` 구현
- [ ] 통합 전처리 파이프라인 클래스 작성
- [ ] 단위 테스트 작성 (각 전처리 단계별)

**Testing**:
- Unit Test: 리샘플링 정확도, 필터 주파수 응답, 윈도우 크기
- Component Test: 전체 파이프라인 입출력 검증
- E2E Test: 실제 웨어러블 데이터 전처리 후 모델 입력 가능 확인

---

### 📘 User Story 2.3: 멀티모달 임베딩 추출
**Epic**: Epic 3 - SleepFM 모델 통합  
**Story Points**: 5

**As a** ML Engineer  
**I want to** SleepFM 인코더로 멀티모달 임베딩을 추출  
**So that** 수면 데이터의 고수준 특징을 얻을 수 있다

**Description**:
- CNN 토크나이저로 각 5초 윈도우를 임베딩
- 채널/시간 어텐션 풀링 레이어 적용
- 최종 임베딩 벡터 생성 (예: 512차원)
- 배치 처리 지원
- 메모리 효율적 추론

**Acceptance Criteria**:
- [ ] 전처리된 텐서 입력 → 임베딩 벡터 출력
- [ ] 출력 shape: `(batch, embedding_dim)`
- [ ] 추론 시간 < 10초 (8시간 데이터, GPU 기준)
- [ ] 배치 크기 자동 조정으로 OOM 방지
- [ ] 임베딩 벡터를 NumPy 배열로 반환

**Tasks**:
- [ ] `models/pooling.py` 구현 (Attention Pooling)
- [ ] `models/transformer.py` 구현 (필요시)
- [ ] 임베딩 추출 함수 작성
- [ ] 배치 처리 로직
- [ ] 메모리 최적화 (mixed precision, gradient checkpointing)

**Testing**:
- Unit Test: 어텐션 풀링 출력 shape
- Component Test: 임베딩 추출 시간 측정
- E2E Test: 전처리 → 임베딩 추출 → 결과 검증

---

### 📘 User Story 2.4: 데이터 검증 및 품질 체크
**Epic**: Epic 2 - 데이터 파이프라인 구축  
**Story Points**: 3

**As a** Backend Developer  
**I want to** 업로드된 센서 데이터의 품질을 검증  
**So that** 불량 데이터로 인한 오류를 방지할 수 있다

**Description**:
- 센서 데이터 길이 검증 (최소 2시간 이상)
- 결측치 비율 확인 (< 10%)
- 신호 범위 검증 (생리학적으로 타당한 범위)
- 샘플링 레이트 일관성 체크
- 검증 실패 시 명확한 에러 메시지 반환

**Acceptance Criteria**:
- [ ] 2시간 미만 데이터는 거부 (400 에러)
- [ ] 결측치 > 10% 시 경고 플래그 설정
- [ ] 심박수 범위: 30-200 BPM
- [ ] 호흡률 범위: 5-40 breaths/min
- [ ] 검증 결과가 로그에 기록됨

**Tasks**:
- [ ] `validation/sensor_data.py` 구현
- [ ] 길이, 결측치, 범위 검증 함수 작성
- [ ] 검증 실패 시 커스텀 예외 정의
- [ ] 업로드 엔드포인트에 검증 로직 통합

**Testing**:
- Unit Test: 각 검증 규칙 테스트
- Component Test: 정상/비정상 데이터 업로드 시나리오
- E2E Test: 불량 데이터 업로드 → 적절한 에러 메시지 확인

---

### Sprint 2 완료 기준
- [ ] SleepFM 모델 로딩 및 임베딩 추출 가능
- [ ] 전처리 파이프라인 단위 테스트 커버리지 ≥ 80%
- [ ] 8시간 데이터 처리 시간 < 15초
- [ ] 데이터 검증 로직 모든 케이스 통과
- [ ] 기술 문서 업데이트 (전처리 파이프라인 상세 설명)

---

## Sprint 3: 수면 분석 기능
**기간**: 2주 (Week 5-6)  
**Sprint 목표**: 수면 단계 분류 및 수면무호흡 탐지 기능 구현  
**총 Story Points**: 21

---

### 📘 User Story 3.1: 수면 단계 분류 모델 헤드 구현
**Epic**: Epic 4 - 수면 분석 기능  
**Story Points**: 8

**As a** ML Engineer  
**I want to** SleepFM 임베딩을 기반으로 수면 단계를 분류  
**So that** 사용자에게 수면 패턴 정보를 제공할 수 있다

**Description**:
- Linear 또는 LSTM 기반 분류 헤드 구현
- 5개 클래스 분류 (Wake, N1, N2, N3, REM)
- 30초 에포크별 예측
- Softmax 확률 출력
- 공개 데이터셋으로 파인튜닝 (SHHS 등)

**Acceptance Criteria**:
- [ ] 임베딩 입력 → 5개 클래스 확률 출력
- [ ] F1 Score ≥ 0.70 (공개 데이터셋 기준)
- [ ] 각 에포크별 가장 높은 확률의 단계 선택
- [ ] 예측 시간 < 1초 (8시간 데이터)
- [ ] 모델 가중치 저장 및 로딩 가능

**Tasks**:
- [ ] `models/heads.py` - SleepStageClassifier 클래스 구현
- [ ] 공개 데이터셋 다운로드 및 전처리
- [ ] 파인튜닝 스크립트 작성 (`scripts/finetune_sleep_stage.py`)
- [ ] 검증 세트로 성능 평가
- [ ] 최적 가중치 저장

**Testing**:
- Unit Test: 분류 헤드 출력 shape 및 범위 (0-1)
- Component Test: 공개 데이터로 F1 Score 검증
- E2E Test: 전체 파이프라인 (전처리 → 임베딩 → 분류) 실행

---

### 📘 User Story 3.2: 수면 단계 분석 API 엔드포인트
**Epic**: Epic 4 - 수면 분석 기능  
**Story Points**: 5

**As a** Mobile App  
**I want to** 수면 단계 분석 결과를 조회  
**So that** 사용자에게 수면 패턴을 시각화할 수 있다

**Description**:
- 수면 단계 분석 실행 엔드포인트
- 에포크별 수면 단계 및 확률 반환
- SleepStages 테이블에 결과 저장
- 수면 효율성 계산 (총 수면 시간 / 총 침대 시간)
- 각 단계별 지속 시간 합산

**Acceptance Criteria**:
- [ ] `POST /api/v1/analyze/sleep-stages` 엔드포인트 구현
- [ ] session_id로 센서 데이터 조회
- [ ] 분석 결과에 에포크별 단계 배열 포함
- [ ] 수면 효율성 및 단계별 시간 요약 제공
- [ ] SleepStages 테이블에 레코드 저장 확인

**Tasks**:
- [ ] `routes/analysis.py` 생성
- [ ] 수면 단계 분석 엔드포인트 구현
- [ ] SleepStages 모델에 CRUD 로직 추가
- [ ] 수면 효율성 계산 유틸리티
- [ ] Pydantic 응답 스키마 정의

**Testing**:
- Unit Test: 수면 효율성 계산 로직
- Component Test: API 호출 후 응답 형식 검증
- E2E Test: 센서 데이터 업로드 → 분석 실행 → 결과 조회

---

### 📘 User Story 3.3: 수면무호흡 탐지 모델 구현
**Epic**: Epic 4 - 수면 분석 기능  
**Story Points**: 5

**As a** ML Engineer  
**I want to** 수면무호흡 이벤트를 탐지  
**So that** 사용자의 호흡 문제를 조기 발견할 수 있다

**Description**:
- 임베딩 기반 무호흡 탐지 모델 헤드
- 무호흡 이벤트 시점 및 지속 시간 예측
- AHI (Apnea-Hypopnea Index) 계산
- 중증도 분류 (정상, 경증, 중등도, 중증)
- 공개 데이터셋으로 파인튜닝

**Acceptance Criteria**:
- [ ] 무호흡 이벤트 탐지 정확도 ≥ 0.85
- [ ] AHI 점수 계산 (시간당 이벤트 수)
- [ ] 중증도 분류: 정상(<5), 경증(5-15), 중등도(15-30), 중증(>30)
- [ ] 이벤트별 시작 시간 및 지속 시간 반환
- [ ] 추론 시간 < 2초

**Tasks**:
- [ ] `models/heads.py` - ApneaDetector 클래스 구현
- [ ] 공개 데이터셋으로 파인튜닝
- [ ] AHI 계산 유틸리티 작성
- [ ] 중증도 분류 로직
- [ ] 성능 평가 및 가중치 저장

**Testing**:
- Unit Test: AHI 계산 로직
- Component Test: 공개 데이터로 정확도 검증
- E2E Test: 전체 파이프라인 (전처리 → 탐지 → AHI 계산)

---

### 📘 User Story 3.4: 수면무호흡 분석 API 엔드포인트
**Epic**: Epic 4 - 수면 분석 기능  
**Story Points**: 3

**As a** Mobile App  
**I want to** 수면무호흡 분석 결과를 조회  
**So that** 사용자에게 호흡 문제를 알릴 수 있다

**Description**:
- 수면무호흡 분석 엔드포인트
- 이벤트 목록 및 AHI 점수 반환
- ApneaEvents 테이블에 저장
- 중증도 및 권장사항 제공

**Acceptance Criteria**:
- [ ] `POST /api/v1/analyze/apnea` 엔드포인트 구현
- [ ] 응답에 이벤트 목록, AHI, 중증도 포함
- [ ] ApneaEvents 테이블에 레코드 저장
- [ ] 중증도에 따른 권장사항 메시지 반환
- [ ] 응답 시간 < 3초

**Tasks**:
- [ ] `routes/analysis.py`에 무호흡 엔드포인트 추가
- [ ] ApneaEvents 모델 CRUD 로직
- [ ] 권장사항 메시지 템플릿 작성
- [ ] Pydantic 응답 스키마 정의

**Testing**:
- Unit Test: 중증도별 권장사항 로직
- Component Test: API 응답 형식 검증
- E2E Test: 센서 데이터 업로드 → 무호흡 분석 → 결과 조회

---

### Sprint 3 완료 기준
- [ ] 수면 단계 분류 F1 ≥ 0.70 달성
- [ ] 무호흡 탐지 정확도 ≥ 0.85 달성
- [ ] 두 기능 모두 API로 접근 가능
- [ ] 통합 테스트 통과 (전체 분석 플로우)
- [ ] Swagger 문서 업데이트

---

## Sprint 4: 질병 예측 API
**기간**: 2주 (Week 7-8)  
**Sprint 목표**: 5개 주요 질환 위험 예측 기능 및 통합 분석 API 완성  
**총 Story Points**: 21

---

### 📘 User Story 4.1: 질병 위험 예측 모델 헤드 구현
**Epic**: Epic 5 - 질병 위험 예측  
**Story Points**: 8

**As a** ML Engineer  
**I want to** SleepFM 임베딩으로 질병 위험을 예측  
**So that** 사용자에게 건강 위험 정보를 제공할 수 있다

**Description**:
- CoxPH 기반 생존 분석 헤드 구현
- 5개 질환 예측: 파킨슨병, 치매, 심근경색, 심부전, 뇌졸중
- 위험 스코어 (0-100) 산출
- 신뢰 구간 계산
- 위험도 카테고리 분류 (Low < 30, Medium 30-60, High > 60)

**Acceptance Criteria**:
- [ ] 각 질환별 C-Index ≥ 0.75 (공개 데이터셋)
- [ ] 위험 스코어 범위: 0-100
- [ ] 95% 신뢰 구간 계산
- [ ] 5개 질환 동시 예측 가능
- [ ] 추론 시간 < 3초

**Tasks**:
- [ ] `models/heads.py` - DiseaseRiskPredictor 클래스 구현
- [ ] CoxPH 헤드 구현 (Linear 또는 LSTM)
- [ ] 공개 데이터셋으로 파인튜닝
- [ ] 신뢰 구간 계산 로직
- [ ] 성능 평가 (C-Index)
- [ ] 가중치 저장

**Testing**:
- Unit Test: 위험 스코어 범위 검증
- Component Test: 공개 데이터로 C-Index 검증
- E2E Test: 전체 파이프라인 (전처리 → 임베딩 → 위험 예측)

---

### 📘 User Story 4.2: 질병 위험 예측 API 엔드포인트
**Epic**: Epic 5 - 질병 위험 예측  
**Story Points**: 5

**As a** Mobile App  
**I want to** 질병 위험 예측 결과를 조회  
**So that** 사용자에게 건강 위험을 알릴 수 있다

**Description**:
- 질병 위험 예측 엔드포인트
- 5개 질환별 위험 스코어 및 카테고리 반환
- DiseaseRiskScores 테이블에 저장
- 고위험 질환에 대한 권장사항 제공

**Acceptance Criteria**:
- [ ] `POST /api/v1/analyze/disease-risk` 엔드포인트 구현
- [ ] 응답에 질환별 스코어, 카테고리, 신뢰 구간 포함
- [ ] DiseaseRiskScores 테이블에 레코드 저장
- [ ] 고위험(High) 질환에 대한 권장사항 반환
- [ ] 응답 시간 < 4초

**Tasks**:
- [ ] `routes/analysis.py`에 질병 위험 엔드포인트 추가
- [ ] DiseaseRiskScores 모델 CRUD 로직
- [ ] 위험도별 권장사항 템플릿
- [ ] Pydantic 응답 스키마 정의

**Testing**:
- Unit Test: 위험도 카테고리 분류 로직
- Component Test: API 응답 형식 검증
- E2E Test: 센서 데이터 업로드 → 질병 위험 예측 → 결과 조회

---

### 📘 User Story 4.3: 통합 분석 API 엔드포인트
**Epic**: Epic 5 - 질병 위험 예측  
**Story Points**: 5

**As a** Mobile App  
**I want to** 한 번의 요청으로 모든 분석 결과를 받기  
**So that** 사용자 경험을 개선하고 네트워크 비용을 줄일 수 있다

**Description**:
- 수면 단계, 무호흡, 질병 위험을 한 번에 분석
- 모든 결과를 하나의 응답으로 반환
- 비동기 작업으로 처리 시간 최적화
- 분석 상태 추적 (pending, processing, completed, failed)

**Acceptance Criteria**:
- [ ] `POST /api/v1/analyze` 엔드포인트 구현
- [ ] 응답에 수면 요약, 수면 단계, 무호흡, 질병 위험 모두 포함
- [ ] 총 분석 시간 < 15초 (8시간 데이터)
- [ ] 분석 실패 시 부분 결과라도 반환
- [ ] 분석 상태 조회 가능 (`GET /api/v1/analyze/{session_id}/status`)

**Tasks**:
- [ ] 통합 분석 엔드포인트 구현
- [ ] 비동기 작업 큐 설정 (Celery 또는 백그라운드 태스크)
- [ ] 상태 추적 로직
- [ ] 에러 핸들링 (부분 실패 처리)
- [ ] 통합 응답 스키마 정의

**Testing**:
- Unit Test: 각 분석 모듈 통합 로직
- Component Test: 통합 API 응답 검증
- E2E Test: 센서 데이터 업로드 → 통합 분석 → 모든 결과 조회

---

### 📘 User Story 4.4: 분석 결과 조회 및 히스토리
**Epic**: Epic 5 - 질병 위험 예측  
**Story Points**: 3

**As a** Mobile App User  
**I want to** 과거 분석 결과를 조회  
**So that** 건강 트렌드를 확인할 수 있다

**Description**:
- 사용자별 세션 목록 조회
- 특정 세션의 상세 분석 결과 조회
- 날짜 범위 필터링
- 페이지네이션 지원

**Acceptance Criteria**:
- [ ] `GET /api/v1/users/{user_id}/sessions` 구현
- [ ] `GET /api/v1/sessions/{session_id}/results` 구현
- [ ] 날짜 범위 쿼리 파라미터 지원
- [ ] 페이지네이션 (limit, offset)
- [ ] 응답 시간 < 500ms

**Tasks**:
- [ ] 세션 목록 조회 엔드포인트
- [ ] 세션 상세 결과 조회 엔드포인트
- [ ] 쿼리 최적화 (인덱스 추가)
- [ ] Pydantic 응답 스키마 정의

**Testing**:
- Unit Test: 쿼리 로직 (필터, 페이지네이션)
- Component Test: API 응답 검증
- E2E Test: 여러 세션 생성 → 목록 조회 → 상세 조회

---

### Sprint 4 완료 기준
- [ ] 5개 질환 예측 C-Index ≥ 0.75 달성
- [ ] 통합 분석 API 정상 동작
- [ ] 모든 API 엔드포인트 Swagger 문서화
- [ ] E2E 테스트 전체 통과
- [ ] 성능 테스트 (100 동시 요청) 통과

---

## Phase 1 완료 기준

### 기능적 완료 기준
- [x] 모든 Epic의 User Story 완료
- [x] FastAPI 서버 실행 및 접근 가능
- [x] PostgreSQL 데이터베이스 연결 및 마이그레이션
- [x] JWT 인증 시스템 동작
- [x] 센서 데이터 업로드 및 전처리
- [x] SleepFM 모델 추론 가능
- [x] 수면 단계 분류 (F1 ≥ 0.70)
- [x] 수면무호흡 탐지 (정확도 ≥ 0.85)
- [x] 질병 위험 예측 (C-Index ≥ 0.75)
- [x] 통합 분석 API 동작

### 비기능적 완료 기준
- [x] 단위 테스트 커버리지 ≥ 70%
- [x] 통합 테스트 작성 및 통과
- [x] E2E 테스트 작성 및 통과
- [x] API 응답 시간 < 2초 (95 백분위)
- [x] 추론 시간 < 10초 (8시간 데이터)
- [x] Docker Compose로 로컬 실행 가능
- [x] Swagger 문서 완성

### 문서화 완료 기준
- [x] API 문서 (OpenAPI/Swagger)
- [x] 코드 주석 (함수별 docstring)
- [x] 아키텍처 다이어그램 업데이트
- [x] 개발자 가이드 작성
- [x] 배포 가이드 작성 (로컬 환경)

### 품질 기준
- [x] 모든 코드 리뷰 완료
- [x] Linter 규칙 준수 (flake8, black, mypy)
- [x] 보안 검토 완료 (JWT, 데이터 암호화)
- [x] 성능 테스트 통과

---

## 다음 단계
Phase 1 완료 후 **Phase 2: 모바일/웨어러블 앱 개발**로 진행합니다.  
상세 계획은 `SPRINT_PLAN_PHASE2.md` 참조.

---

## 부록

### A. Story Point 가이드
- **1 Point**: 매우 간단, 1-2시간
- **3 Points**: 간단, 반나절
- **5 Points**: 중간, 1-2일
- **8 Points**: 복잡, 3-4일
- **13 Points**: 매우 복잡, 1주 이상 (분할 권장)

### B. Definition of Ready (User Story)
- [ ] 명확한 제목 및 설명
- [ ] "As a, I want to, So that" 형식
- [ ] Acceptance Criteria 정의
- [ ] Story Points 추정
- [ ] Epic 연결
- [ ] 의존성 확인

### C. Definition of Done (User Story)
- [ ] 모든 AC 충족
- [ ] 코드 리뷰 완료
- [ ] 단위 테스트 작성 및 통과
- [ ] 통합 테스트 작성 및 통과
- [ ] 문서 업데이트
- [ ] QA 검증 완료

### D. 변경 이력
| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-01-08 | Phase 1 Sprint Plan 초안 작성 | Development Team |

---

**문서 승인:**
- [ ] 프로젝트 매니저
- [ ] Backend Lead
- [ ] ML Engineer Lead

**다음 Sprint Planning 미팅:** Sprint 1 시작 전 (2026년 1월 15일 예정)
