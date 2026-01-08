# GitHub Strategy & Workflow
## SleepFM-Wearable-Health Project

**문서 버전:** 1.0  
**작성일:** 2026년 1월 8일  
**적용 범위:** 전체 개발팀

---

## 목차
1. [개요](#개요)
2. [브랜치 전략](#브랜치-전략)
3. [커밋 컨벤션](#커밋-컨벤션)
4. [Pull Request 프로세스](#pull-request-프로세스)
5. [코드 리뷰 가이드라인](#코드-리뷰-가이드라인)
6. [CI/CD 연동](#cicd-연동)
7. [이슈 관리](#이슈-관리)
8. [Sprint별 워크플로우](#sprint별-워크플로우)

---

## 개요

### 기본 원칙
- **스프린트 = 2주 단위**
- **1 User Story = 1 커밋** (완성 시점)
- **1 Sprint = 1 Pull Request**
- **모든 코드는 코드 리뷰 필수**
- **main 브랜치는 항상 배포 가능한 상태 유지**

### 저장소 구조
```
sleepfm-wearable-health/
├── backend/          # Python 백엔드
├── mobile/
│   ├── ios/         # Swift iOS 앱
│   └── android/     # Kotlin Android 앱
├── docs/            # 문서
└── .github/
    └── workflows/   # CI/CD
```

---

## 브랜치 전략

### 브랜치 종류

#### 1. `main` 브랜치
- **목적**: 프로덕션 배포 가능한 안정 버전
- **보호 설정**: 
  - 직접 푸시 금지
  - PR 승인 필수 (최소 1명)
  - CI 통과 필수
  - 관리자만 머지 가능
- **태그**: 릴리스 시 버전 태그 (예: `v1.0.0`)

#### 2. `develop` 브랜치
- **목적**: 다음 릴리스 준비 통합 브랜치
- **사용**: 각 Sprint PR의 타겟 브랜치
- **보호 설정**:
  - PR 승인 필수
  - CI 통과 필수

#### 3. `sprint/{sprint-number}` 브랜치
- **목적**: 각 스프린트 작업 브랜치
- **명명 규칙**: `sprint/01`, `sprint/02`, ..., `sprint/12`
- **생성 시점**: 스프린트 시작 시 `develop`에서 분기
- **예시**:
  ```bash
  git checkout develop
  git pull origin develop
  git checkout -b sprint/01
  ```

#### 4. `feature/{story-id}-{brief-description}` 브랜치 (선택적)
- **목적**: User Story 단위 개별 작업 (필요 시)
- **명명 규칙**: `feature/1.1-project-setup`, `feature/2.2-signal-preprocessing`
- **사용 케이스**: 
  - User Story가 복잡하여 여러 개발자가 협업
  - 실험적 기능 개발
- **머지 대상**: `sprint/{sprint-number}` 브랜치

### 브랜치 플로우

```
main (프로덕션)
  └── develop (스테이징)
       ├── sprint/01 (Sprint 1)
       │    ├── [Story 1.1 커밋]
       │    ├── [Story 1.2 커밋]
       │    └── [Story 1.3 커밋]
       ├── sprint/02 (Sprint 2)
       │    ├── [Story 2.1 커밋]
       │    └── [Story 2.2 커밋]
       └── sprint/03 (Sprint 3)
            └── ...
```

---

## 커밋 컨벤션

### Conventional Commits 기반

#### 커밋 메시지 구조
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type (필수)
- **feat**: 새로운 기능 추가 (User Story 완성)
- **fix**: 버그 수정
- **docs**: 문서 수정
- **style**: 코드 포맷팅, 세미콜론 누락 등 (기능 변경 없음)
- **refactor**: 코드 리팩토링 (기능 변경 없음)
- **test**: 테스트 코드 추가/수정
- **chore**: 빌드 설정, 패키지 매니저 설정 등

#### Scope (선택)
- **backend**: 백엔드 관련
- **ios**: iOS 앱 관련
- **android**: Android 앱 관련
- **watch**: watchOS/Wear OS 관련
- **infra**: 인프라/DevOps 관련
- **docs**: 문서 관련

#### Subject (필수)
- 50자 이내
- 명령형 현재 시제 ("Add" not "Added")
- 첫 글자 대문자
- 마침표 없음
- **User Story 커밋 시**: Story 번호 포함

#### Body (선택)
- 72자마다 줄바꿈
- "무엇을" 그리고 "왜" 변경했는지 설명
- User Story의 경우 Acceptance Criteria 체크 상태

#### Footer (선택)
- **Breaking Changes**: `BREAKING CHANGE: 설명`
- **이슈 참조**: `Closes #123`, `Relates to #456`
- **User Story 참조**: `Story: 1.1`, `Story: 2.3`

### 커밋 예시

#### User Story 완성 커밋
```bash
feat(backend): implement FastAPI basic server (Story 1.2)

- Set up FastAPI application with basic routing
- Configure CORS middleware for development
- Add error handling middleware
- Implement /health endpoint
- Generate Swagger documentation

Acceptance Criteria:
✅ GET /api/v1/health endpoint returns 200
✅ Swagger UI accessible at /docs
✅ CORS allows all origins in dev environment
✅ Error responses return consistent JSON format
✅ All requests/responses logged

Story: 1.2
```

#### 버그 수정 커밋
```bash
fix(ios): resolve memory leak in HealthKit service

- Release HKHealthStore observer in deinit
- Fix retain cycle in completion handler
- Add weak self reference in closure

Closes #42
```

#### 문서 업데이트 커밋
```bash
docs: update API documentation with authentication examples

- Add JWT token authentication examples
- Include error response codes
- Update Swagger annotations
```

#### 테스트 추가 커밋
```bash
test(backend): add unit tests for JWT authentication

- Test token generation and verification
- Test expired token scenarios
- Test invalid token handling

Coverage increased from 65% to 72%
```

### User Story별 커밋 타이밍

#### 원칙
- **User Story 완성 시점에 1개 커밋**
- 모든 Acceptance Criteria 충족 확인
- 테스트 통과 확인
- 코드 리뷰 준비 완료

#### 예외 상황
- **Story가 너무 큰 경우**: 
  - 서브 태스크로 분할하여 각각 커밋
  - 커밋 메시지에 `(WIP)` 또는 `(Part 1/3)` 표기
  
  ```bash
  feat(backend): implement data preprocessing pipeline (Part 1/3) (Story 2.2)
  
  - Add signal resampling to 128Hz
  - Implement Butterworth filter
  
  Story: 2.2 (In Progress)
  ```

- **급한 버그 수정**: 
  - 별도 `fix` 커밋으로 즉시 대응
  - Sprint 브랜치에 바로 커밋 가능

---

## Pull Request 프로세스

### PR 생성 규칙

#### 1 Sprint = 1 Pull Request
- **PR 생성 시점**: Sprint 종료 시
- **PR 타이틀**: `[Sprint {number}] {Sprint Goal}`
- **타겟 브랜치**: `develop`
- **소스 브랜치**: `sprint/{number}`

#### PR 타이틀 예시
```
[Sprint 01] Infrastructure and Data Pipeline Setup
[Sprint 02] Model Integration and Preprocessing
[Sprint 03] Sleep Analysis Features
```

### PR 설명 템플릿

```markdown
## Sprint {Number}: {Sprint Goal}

### 📅 Sprint 정보
- **기간**: Week {start} - Week {end}
- **총 Story Points**: {points}
- **완료된 User Stories**: {count}/{total}

### ✅ 완료된 User Stories
- [x] Story 1.1: Project Environment Setup (3 points)
- [x] Story 1.2: FastAPI Basic Server (5 points)
- [x] Story 1.3: PostgreSQL Database Setup (5 points)
- [x] Story 1.4: JWT Authentication System (5 points)
- [x] Story 1.5: Sensor Data Upload API (3 points)

### 🎯 Sprint 목표 달성 여부
- [x] 모든 User Story의 AC 충족
- [x] 코드 리뷰 완료
- [x] 단위 테스트 커버리지 ≥ 70%
- [x] Swagger 문서 업데이트
- [x] Docker Compose로 로컬 실행 가능

### 📊 테스트 결과
- **단위 테스트**: 45 passed, 0 failed
- **통합 테스트**: 12 passed, 0 failed
- **커버리지**: 72%
- **Linter**: No issues

### 🔍 주요 변경 사항
- FastAPI 서버 구조 확립
- PostgreSQL 데이터베이스 스키마 정의
- JWT 인증 시스템 구현
- 센서 데이터 업로드 API 구현

### 📝 리뷰어 확인 사항
- [ ] 코드가 프로젝트 컨벤션을 따르는가?
- [ ] 테스트가 충분한가?
- [ ] 문서가 업데이트되었는가?
- [ ] Breaking changes가 있는가?

### 🔗 관련 문서
- Sprint Plan: [SPRINT_PLAN_PHASE1.md](docs/SPRINT_PLAN_PHASE1.md)
- API Documentation: [Swagger UI](http://localhost:8000/docs)

### 📸 스크린샷 (UI 관련 Sprint)
<!-- 해당하는 경우 스크린샷 추가 -->

### 🚀 배포 영향
- [ ] 데이터베이스 마이그레이션 필요
- [ ] 환경 변수 추가 필요
- [ ] 배포 순서 고려 필요

### ⚠️ 알려진 이슈
<!-- 알려진 제한사항이나 후속 작업 -->

---
**Sprint Retrospective 완료**: [날짜]
```

### PR 라벨링

#### 필수 라벨
- **Sprint**: `sprint-01`, `sprint-02`, ..., `sprint-12`
- **Phase**: `phase-1`, `phase-2`, `phase-3`
- **Component**: `backend`, `ios`, `android`, `watch`, `infra`

#### 상태 라벨
- **Status**: `in-review`, `approved`, `changes-requested`, `ready-to-merge`
- **Priority**: `high`, `medium`, `low`

#### 특수 라벨
- **Breaking Change**: `breaking-change`
- **Dependencies**: `dependencies`
- **Documentation**: `documentation`

### PR 체크리스트

#### 작성자 체크리스트
```markdown
- [ ] 모든 User Story AC 충족
- [ ] 테스트 작성 및 통과 (커버리지 ≥ 70%)
- [ ] Linter 규칙 준수
- [ ] 문서 업데이트 (README, API docs 등)
- [ ] Breaking changes 명시
- [ ] 스크린샷 추가 (UI 변경 시)
- [ ] Self-review 완료
```

#### 리뷰어 체크리스트
```markdown
- [ ] 코드 품질 및 가독성
- [ ] 테스트 충분성
- [ ] 에러 핸들링
- [ ] 성능 고려사항
- [ ] 보안 취약점 확인
- [ ] 문서 완성도
```

---

## 코드 리뷰 가이드라인

### 리뷰 프로세스

#### 1. 리뷰어 할당
- **최소 1명 이상** (컴포넌트별 Lead)
- **Backend PR**: Backend Lead + ML Engineer
- **iOS PR**: iOS Lead + (선택) Android Lead (UI 일관성)
- **Android PR**: Android Lead + (선택) iOS Lead (UI 일관성)

#### 2. 리뷰 시간
- **목표**: PR 생성 후 **24시간 이내** 1차 리뷰
- **최종 승인**: **48시간 이내**

#### 3. 리뷰 우선순위
1. **Critical**: 보안, 데이터 손실 위험
2. **High**: 버그, 성능 이슈
3. **Medium**: 코드 품질, 가독성
4. **Low**: 네이밍, 주석

### 리뷰 코멘트 컨벤션

#### 코멘트 접두사
- **[MUST]**: 반드시 수정 필요 (머지 블로커)
- **[SHOULD]**: 권장 사항
- **[CONSIDER]**: 고려사항 제안
- **[QUESTION]**: 질문 또는 명확화 요청
- **[NITS]**: 사소한 제안 (블로커 아님)

#### 코멘트 예시
```
[MUST] 이 엔드포인트는 인증이 필요합니다. 
@auth_required 데코레이터를 추가해주세요.

[SHOULD] 이 로직을 별도 함수로 추출하면 테스트하기 
더 쉬울 것 같습니다.

[CONSIDER] Redis 캐싱을 추가하면 성능이 개선될 수 있습니다.
현재는 필수는 아니지만 향후 고려해주세요.

[QUESTION] 이 예외 처리가 모든 케이스를 커버하나요?
네트워크 타임아웃은 어떻게 처리되나요?

[NITS] 변수명을 `data`보다 `sensor_data`로 하면 
더 명확할 것 같습니다.
```

### 리뷰 승인 기준

#### Approve (승인)
- 모든 [MUST] 항목 해결
- 테스트 통과
- 문서 업데이트 확인
- 더 이상 blocking issue 없음

#### Request Changes (변경 요청)
- [MUST] 항목 미해결
- 테스트 실패
- 보안/성능 심각한 문제

#### Comment (코멘트만)
- [SHOULD], [CONSIDER] 수준의 제안
- 질문 또는 토론

---

## CI/CD 연동

### GitHub Actions 워크플로우

#### PR 생성/업데이트 시
```yaml
name: PR Validation

on:
  pull_request:
    branches: [develop, main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linters
        run: |
          # Backend: flake8, black, mypy
          # iOS: SwiftLint
          # Android: ktlint
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          # Backend: pytest
          # iOS: XCTest
          # Android: JUnit
  
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check coverage
        run: |
          # Coverage must be >= 70%
```

#### develop 브랜치 머지 시
```yaml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
      - name: Push to registry
      - name: Deploy to staging
      - name: Notify Slack
```

#### main 브랜치 머지 (릴리스) 시
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Build and deploy to production
      - name: Create GitHub Release
      - name: Upload to App Store / Play Store
```

### 머지 조건

#### develop 브랜치 머지 조건
- [ ] 1개 이상 승인 (Approve)
- [ ] 모든 CI 체크 통과
- [ ] Conflicts 해결
- [ ] Sprint Retrospective 완료

#### main 브랜치 머지 조건 (릴리스)
- [ ] 2명 이상 승인 (Lead + PM)
- [ ] 모든 CI 체크 통과
- [ ] QA 테스트 완료
- [ ] 릴리스 노트 작성

---

## 이슈 관리

### 이슈 생성 규칙

#### User Story → GitHub Issue
- **Sprint 시작 시** 모든 User Story를 Issue로 생성
- **Title**: `[Story {number}] {Story Title}`
- **Labels**: `user-story`, `sprint-{number}`, `{component}`
- **Assignees**: 담당 개발자
- **Milestone**: Sprint {number}

#### 이슈 템플릿
```markdown
## User Story {Number}

**Epic**: {Epic Name}  
**Story Points**: {points}  
**Sprint**: {number}

### User Story
**As a** {role}  
**I want to** {goal}  
**So that** {benefit}

### Description
{detailed description}

### Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}
- [ ] {criterion 3}

### Tasks
- [ ] {task 1}
- [ ] {task 2}
- [ ] {task 3}

### Testing
- [ ] Unit Tests
- [ ] Component Tests
- [ ] E2E Tests

### Definition of Done
- [ ] All ACs met
- [ ] Code review approved
- [ ] Tests written and passing
- [ ] Documentation updated

### Related
- Sprint Plan: [Link]
- Figma Design: [Link] (if applicable)
```

### 이슈 라벨 시스템

#### Type
- `user-story`: User Story 이슈
- `bug`: 버그 리포트
- `enhancement`: 개선 사항
- `documentation`: 문서 작업

#### Component
- `backend`
- `ios`
- `android`
- `watch`
- `infra`

#### Sprint
- `sprint-01` ~ `sprint-12`

#### Status
- `todo`: 시작 전
- `in-progress`: 작업 중
- `in-review`: 리뷰 중
- `done`: 완료

### 이슈 워크플로우

```
[Open] → [In Progress] → [In Review] → [Done] → [Closed]
  ↓          ↓               ↓            ↓
 todo    in-progress     in-review      done
```

---

## Sprint별 워크플로우

### Sprint 시작 (Day 1)

#### 1. Sprint 브랜치 생성
```bash
# develop 브랜치 최신화
git checkout develop
git pull origin develop

# Sprint 브랜치 생성
git checkout -b sprint/01
git push -u origin sprint/01
```

#### 2. GitHub Issue 생성
- Sprint Plan 문서 기반으로 모든 User Story를 Issue로 생성
- Milestone 설정: `Sprint 01`
- 담당자 할당

#### 3. Project Board 설정
- GitHub Projects에서 Sprint Board 생성
- 컬럼: `To Do`, `In Progress`, `In Review`, `Done`
- 모든 Issue를 `To Do`에 추가

### Sprint 진행 중 (Day 2-13)

#### User Story 작업 시작
```bash
# Sprint 브랜치에서 작업
git checkout sprint/01
git pull origin sprint/01

# Issue를 "In Progress"로 이동
# (GitHub에서 수동 또는 자동화)
```

#### User Story 완료 시
```bash
# 변경사항 스테이징
git add .

# User Story 커밋 (AC 모두 충족 확인)
git commit -m "feat(backend): implement FastAPI basic server (Story 1.2)

- Set up FastAPI application with basic routing
- Configure CORS middleware
- Add error handling middleware
- Implement /health endpoint

Acceptance Criteria:
✅ GET /api/v1/health returns 200
✅ Swagger UI accessible
✅ CORS configured
✅ Error handling works
✅ All requests logged

Story: 1.2"

# Sprint 브랜치에 푸시
git push origin sprint/01
```

#### 자가 검토
- 모든 AC 충족 확인
- 테스트 실행 및 통과 확인
- Linter 실행
- Issue를 "In Review"로 이동

### Sprint 종료 (Day 14)

#### 1. Sprint Retrospective
- 팀 회의: 완료/미완료 Story 검토
- 회고: 잘된 점, 개선점, 액션 아이템

#### 2. Pull Request 생성
```bash
# Sprint 브랜치 최종 푸시 확인
git checkout sprint/01
git push origin sprint/01

# GitHub에서 PR 생성
# Base: develop
# Compare: sprint/01
# Title: [Sprint 01] Infrastructure and Data Pipeline Setup
```

#### 3. PR 설명 작성
- 위의 PR 템플릿 사용
- 모든 완료된 User Story 나열
- 테스트 결과 첨부
- 스크린샷 추가 (UI 관련)

#### 4. 리뷰 요청
- Reviewers 할당
- Labels 추가
- Slack/Discord에 리뷰 요청 공지

#### 5. 리뷰 및 수정
```bash
# 리뷰 코멘트 반영
git checkout sprint/01

# 수정 작업
# ...

# 수정사항 커밋
git commit -m "fix(backend): address PR review comments

- Add input validation for sensor data
- Improve error messages
- Add missing docstrings"

git push origin sprint/01
```

#### 6. 승인 및 머지
- 모든 리뷰어 승인 확인
- CI 통과 확인
- Squash and Merge 또는 Create Merge Commit
- Sprint 브랜치 삭제

#### 7. 다음 Sprint 준비
```bash
# develop 브랜치 최신화
git checkout develop
git pull origin develop

# 다음 Sprint 브랜치 생성
git checkout -b sprint/02
git push -u origin sprint/02
```

---

## 특수 상황 대응

### 긴급 버그 수정 (Hotfix)

#### Hotfix 브랜치 생성
```bash
# main에서 hotfix 브랜치 생성
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-issue

# 수정 작업
# ...

# 커밋
git commit -m "fix(backend): patch SQL injection vulnerability

BREAKING CHANGE: None

Security issue fixed in user authentication.

Closes #urgent-123"

# 푸시 및 PR 생성 (main으로)
git push -u origin hotfix/critical-security-issue
```

#### Hotfix PR
- **타겟**: `main` (직접)
- **라벨**: `hotfix`, `critical`
- **승인**: 최소 2명 (긴급 시 1명)
- **머지 후**: `develop`에도 체리픽 또는 머지

### Story 미완료 시

#### Sprint 종료 시 미완료 Story 처리
1. **PR에 명시**: 미완료 Story 리스트 작성
2. **다음 Sprint로 이관**: Issue를 다음 Sprint Milestone으로 이동
3. **Retrospective**: 미완료 원인 분석

### Merge Conflict 해결

```bash
# Sprint 브랜치에서 develop 최신 변경사항 반영
git checkout sprint/01
git fetch origin
git merge origin/develop

# Conflict 해결
# ...

# 커밋
git commit -m "chore: resolve merge conflicts with develop"
git push origin sprint/01
```

---

## 릴리스 프로세스

### Phase 완료 시 (3개 Phase = 3번 릴리스)

#### 1. develop → main 머지 준비
```bash
# develop 브랜치 확인
git checkout develop
git pull origin develop

# 릴리스 브랜치 생성 (선택적)
git checkout -b release/v1.0.0
```

#### 2. 릴리스 PR 생성
- **Title**: `[Release v1.0.0] Phase 1 Completion`
- **Target**: `main`
- **Source**: `develop` 또는 `release/v1.0.0`
- **Reviewers**: 모든 Lead + PM

#### 3. QA 테스트
- 스테이징 환경에서 전체 테스트
- 체크리스트 완료 확인

#### 4. 릴리스 노트 작성
```markdown
# Release v1.0.0 - Phase 1 Completion

## 📅 릴리스 정보
- **날짜**: 2026-03-05
- **Phase**: Phase 1 - ML Backend
- **Sprints**: Sprint 1-4

## ✨ 주요 기능
- FastAPI REST API 서버
- SleepFM 모델 통합
- 수면 단계 분류 (F1 ≥ 0.70)
- 수면무호흡 탐지 (정확도 ≥ 0.85)
- 질병 위험 예측 (C-Index ≥ 0.75)

## 🔧 기술 스택
- Python 3.10+
- FastAPI 0.100+
- PyTorch 2.0+
- PostgreSQL 14+

## 📊 성능 지표
- API 응답 시간: < 2초 (95백분위)
- 테스트 커버리지: 72%

## 🐛 버그 수정
- (없음 - 첫 릴리스)

## ⚠️ Breaking Changes
- (없음 - 첫 릴리스)

## 📝 업그레이드 가이드
- 신규 설치이므로 마이그레이션 불필요

## 🔗 문서
- [API Documentation](link)
- [Deployment Guide](link)
```

#### 5. 태그 생성
```bash
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release v1.0.0 - Phase 1 Completion"
git push origin v1.0.0
```

#### 6. GitHub Release 생성
- Tag: `v1.0.0`
- Release Notes: 위의 내용 복사
- Assets: 바이너리 첨부 (해당 시)

---

## 팀 커뮤니케이션

### Slack/Discord 통합

#### 알림 채널
- `#github-prs`: PR 생성/승인/머지 알림
- `#github-issues`: Issue 생성/업데이트 알림
- `#ci-cd`: CI/CD 빌드/배포 상태

#### PR 알림 메시지 예시
```
🔔 New Pull Request
[Sprint 01] Infrastructure and Data Pipeline Setup
by @developer123
👉 Review needed: https://github.com/.../pull/1
```

### Daily Standup (비동기)
- **시간**: 매일 오전 10시
- **형식**: Slack 스레드 또는 Discord 채널
- **내용**:
  - 어제 완료한 User Story
  - 오늘 작업할 User Story
  - 블로커 또는 도움 필요 사항

### Sprint Review (동기)
- **시간**: Sprint 종료일 오후 3시
- **형식**: Zoom/Google Meet
- **내용**:
  - 완료된 User Story 데모
  - PR 리뷰 상태 확인
  - 다음 Sprint 계획

---

## 체크리스트 요약

### Sprint 시작 체크리스트
- [ ] Sprint 브랜치 생성 (`sprint/{number}`)
- [ ] GitHub Issues 생성 (모든 User Stories)
- [ ] Milestone 설정
- [ ] Project Board 설정
- [ ] 담당자 할당
- [ ] Sprint Planning 회의 완료

### User Story 완료 체크리스트
- [ ] 모든 AC 충족
- [ ] 테스트 작성 및 통과
- [ ] Linter 통과
- [ ] 문서 업데이트
- [ ] Self-review 완료
- [ ] 커밋 작성 (컨벤션 준수)
- [ ] Sprint 브랜치에 푸시
- [ ] Issue "In Review" 상태로 변경

### Sprint 종료 체크리스트
- [ ] Sprint Retrospective 회의
- [ ] PR 생성 (템플릿 사용)
- [ ] 테스트 결과 첨부
- [ ] Reviewers 할당
- [ ] Labels 추가
- [ ] 리뷰 요청 공지
- [ ] 모든 리뷰 코멘트 반영
- [ ] 승인 및 머지
- [ ] Sprint 브랜치 삭제
- [ ] 다음 Sprint 브랜치 생성

### PR 리뷰 체크리스트
- [ ] 코드 품질 및 컨벤션
- [ ] 테스트 충분성
- [ ] 에러 핸들링
- [ ] 성능 고려
- [ ] 보안 확인
- [ ] 문서 완성도
- [ ] AC 충족 확인
- [ ] Breaking changes 확인

---

## 부록

### Git 명령어 치트시트

```bash
# 브랜치 관리
git checkout -b sprint/01              # 새 Sprint 브랜치
git branch -d sprint/01                # 로컬 브랜치 삭제
git push origin --delete sprint/01     # 원격 브랜치 삭제

# 커밋
git add .                              # 모든 변경사항 스테이징
git commit -m "message"                # 커밋
git commit --amend                     # 마지막 커밋 수정

# 동기화
git fetch origin                       # 원격 변경사항 가져오기
git pull origin develop                # develop 최신화
git push origin sprint/01              # Sprint 브랜치 푸시

# Merge/Rebase
git merge origin/develop               # develop 변경사항 머지
git rebase origin/develop              # develop 기반 rebase (주의)

# 상태 확인
git status                             # 변경사항 확인
git log --oneline --graph              # 커밋 히스토리
git diff                               # 변경 내용 비교
```

### 유용한 GitHub CLI 명령어

```bash
# PR 생성
gh pr create --title "[Sprint 01] Title" --base develop

# PR 상태 확인
gh pr status

# PR 체크아웃
gh pr checkout 123

# Issue 생성
gh issue create --title "[Story 1.1] Title" --label user-story

# Issue 목록
gh issue list --milestone "Sprint 01"
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-01-08 | GitHub 전략 문서 초안 작성 | Development Team |

---

**문서 승인:**
- [ ] 프로젝트 매니저
- [ ] 기술 리드 (Backend/iOS/Android)
- [ ] DevOps Engineer

**적용 시작일:** Sprint 1 시작일
