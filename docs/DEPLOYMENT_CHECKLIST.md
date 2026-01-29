# SleepFM Production Deployment Checklist

> 프로덕션 배포 전 필수 확인 사항 체크리스트

## 개요

이 체크리스트는 SleepFM 백엔드를 프로덕션 환경에 배포하기 전 반드시 확인해야 할 사항들을 정리한 문서입니다.

---

## 📋 배포 전 체크리스트

### 1. 코드 품질 확인

- [ ] **모든 테스트 통과**
  ```bash
  pytest --cov=app --cov-report=term-missing
  ```
  - [ ] 단위 테스트 통과율: 100%
  - [ ] 통합 테스트 통과율: 100%
  - [ ] 코드 커버리지: 80% 이상

- [ ] **코드 스타일 검사**
  ```bash
  ruff check app tests
  black --check app tests
  isort --check-only app tests
  mypy app
  ```

- [ ] **보안 검사**
  ```bash
  safety check
  bandit -r app
  pip-audit
  ```

### 2. 환경 변수 설정

- [ ] **필수 환경 변수 설정됨**

  | 변수 | 설명 | 설정됨 |
  |------|------|--------|
  | `DATABASE_URL` | PostgreSQL 연결 문자열 | [ ] |
  | `SECRET_KEY` | JWT 서명 키 (32+ 문자) | [ ] |
  | `REDIS_HOST` | Redis 서버 호스트 | [ ] |
  | `SENTRY_DSN` | Sentry 프로젝트 DSN | [ ] |
  | `ENVIRONMENT` | `production` | [ ] |

- [ ] **시크릿 보안 확인**
  - [ ] `.env` 파일이 `.gitignore`에 포함됨
  - [ ] 민감한 정보가 코드에 하드코딩되지 않음
  - [ ] 프로덕션 시크릿이 안전하게 관리됨 (Vault, AWS Secrets Manager 등)

### 3. 데이터베이스

- [ ] **마이그레이션 확인**
  ```bash
  alembic upgrade head --sql  # 드라이런으로 먼저 확인
  alembic upgrade head
  ```
  - [ ] 모든 마이그레이션이 적용됨
  - [ ] 롤백 스크립트 준비됨

- [ ] **데이터베이스 백업**
  - [ ] 백업 스케줄 설정됨
  - [ ] 복구 테스트 완료됨
  - [ ] Point-in-time recovery 활성화됨

- [ ] **인덱스 확인**
  - [ ] 필수 인덱스 생성됨
  - [ ] 쿼리 성능 테스트 완료됨

### 4. 인프라 준비

- [ ] **Docker 이미지**
  ```bash
  docker build -t sleepfm-backend:latest --target production .
  docker push ghcr.io/sleepfm/sleepfm-backend:latest
  ```
  - [ ] 프로덕션 이미지 빌드 성공
  - [ ] 이미지 스캔 통과 (취약점 없음)

- [ ] **컨테이너 리소스 설정**
  - [ ] CPU/메모리 제한 설정됨
  - [ ] 자동 스케일링 규칙 설정됨

- [ ] **네트워크 설정**
  - [ ] SSL 인증서 설치됨
  - [ ] 도메인 DNS 설정됨
  - [ ] 방화벽 규칙 설정됨

### 5. 보안 설정

- [ ] **인증/인가**
  - [ ] JWT 토큰 만료 시간 적절히 설정됨
  - [ ] Refresh Token 로테이션 활성화됨
  - [ ] Rate Limiting 활성화됨

- [ ] **HTTPS**
  - [ ] TLS 1.2+ 강제됨
  - [ ] HSTS 헤더 설정됨
  - [ ] SSL 인증서 자동 갱신 설정됨

- [ ] **보안 헤더**
  - [ ] `X-Frame-Options`: SAMEORIGIN
  - [ ] `X-Content-Type-Options`: nosniff
  - [ ] `X-XSS-Protection`: 1; mode=block
  - [ ] `Content-Security-Policy` 설정됨

- [ ] **데이터 보호**
  - [ ] 민감 데이터 암호화됨
  - [ ] PII 데이터 마스킹됨
  - [ ] GDPR 삭제 API 동작 확인됨

### 6. 모니터링 및 로깅

- [ ] **모니터링 설정**
  - [ ] Prometheus 메트릭 수집 확인
  - [ ] Grafana 대시보드 설정됨
  - [ ] 알림 규칙 설정됨

  **주요 알림 조건:**
  | 지표 | 임계값 | 알림 설정 |
  |------|--------|----------|
  | API 응답 시간 | > 500ms | [ ] |
  | 에러율 | > 1% | [ ] |
  | CPU 사용률 | > 80% | [ ] |
  | 메모리 사용률 | > 85% | [ ] |
  | DB 연결 풀 | > 90% | [ ] |

- [ ] **에러 트래킹**
  - [ ] Sentry 프로젝트 설정됨
  - [ ] 에러 알림 채널 설정됨
  - [ ] Source Maps 업로드됨 (프론트엔드)

- [ ] **로깅**
  - [ ] 로그 레벨: INFO
  - [ ] 로그 로테이션 설정됨
  - [ ] 로그 보관 기간 설정됨 (30일+)

### 7. 성능 확인

- [ ] **부하 테스트**
  ```bash
  locust -f tests/load/locustfile.py --host=https://api.sleepfm.io
  ```
  - [ ] 목표 RPS 달성됨
  - [ ] P99 레이턴시 < 500ms
  - [ ] 에러율 < 0.1%

- [ ] **캐시 설정**
  - [ ] Redis 캐시 동작 확인
  - [ ] 캐시 히트율 모니터링됨
  - [ ] TTL 적절히 설정됨

### 8. 배포 프로세스

- [ ] **CI/CD 파이프라인**
  - [ ] GitHub Actions 워크플로우 동작 확인
  - [ ] 스테이징 배포 테스트 완료
  - [ ] 롤백 프로세스 테스트됨

- [ ] **배포 전략**
  - [ ] Blue-Green 또는 Rolling 배포 설정됨
  - [ ] 헬스체크 엔드포인트 동작 확인
  - [ ] 드레인 타임아웃 설정됨

### 9. 문서화

- [ ] **API 문서**
  - [ ] OpenAPI 스펙 최신화됨
  - [ ] 변경 사항 문서화됨

- [ ] **운영 문서**
  - [ ] 배포 가이드 작성됨
  - [ ] 장애 대응 절차 문서화됨
  - [ ] 연락처 목록 업데이트됨

---

## 🚀 배포 절차

### Step 1: 배포 전 확인

```bash
# 1. 최신 코드 확인
git checkout main
git pull origin main

# 2. 테스트 실행
pytest

# 3. 린트 검사
ruff check app tests

# 4. 보안 검사
safety check && bandit -r app
```

### Step 2: 데이터베이스 마이그레이션

```bash
# 1. 마이그레이션 드라이런
alembic upgrade head --sql

# 2. 백업 확인 (AWS RDS 예시)
aws rds create-db-snapshot --db-instance-identifier sleepfm-prod

# 3. 마이그레이션 실행
alembic upgrade head
```

### Step 3: 배포 실행

```bash
# GitHub Actions를 통한 자동 배포 (권장)
git tag v1.x.x
git push origin v1.x.x

# 또는 수동 배포
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Step 4: 배포 후 확인

```bash
# 1. 헬스체크
curl https://api.sleepfm.io/health

# 2. 버전 확인
curl https://api.sleepfm.io/ | jq .version

# 3. 로그 확인
docker logs sleepfm-backend-prod --tail 100

# 4. 메트릭 확인
curl https://api.sleepfm.io/metrics
```

---

## 🔄 롤백 절차

### 긴급 롤백 (< 5분)

```bash
# 1. 이전 버전으로 롤백
docker-compose -f docker-compose.prod.yml pull sleepfm-backend:previous
docker-compose -f docker-compose.prod.yml up -d

# 2. 데이터베이스 롤백 (필요시)
alembic downgrade -1
```

### 롤백 후 확인

- [ ] 서비스 정상 동작 확인
- [ ] 에러 로그 모니터링
- [ ] 사용자 영향 분석
- [ ] 포스트모텀 문서 작성

---

## 📞 비상 연락처

| 역할 | 담당자 | 연락처 |
|------|--------|--------|
| 배포 담당 | - | - |
| DB 관리자 | - | - |
| 인프라 담당 | - | - |
| PM | - | - |

---

## 📅 배포 기록

| 날짜 | 버전 | 변경 사항 | 담당자 | 상태 |
|------|------|----------|--------|------|
| - | v1.0.0 | 최초 배포 | - | 예정 |

---

## ✅ 최종 승인

- [ ] **기술 리드 승인**: _________________ (서명/날짜)
- [ ] **QA 승인**: _________________ (서명/날짜)
- [ ] **PM 승인**: _________________ (서명/날짜)

---

*마지막 업데이트: 2024년 1월*
