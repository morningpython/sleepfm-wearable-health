# Development Plan (SRS)
## Software Requirements Specification
### SleepFM-Wearable-Health Project

**문서 버전:** 1.0  
**작성일:** 2026년 1월 8일  
**프로젝트 코드명:** SleepFM-Wearable-Health  
**문서 상태:** Draft

---

## 목차
1. [소개](#1-소개)
2. [시스템 개요](#2-시스템-개요)
3. [기능 요구사항](#3-기능-요구사항)
4. [비기능 요구사항](#4-비기능-요구사항)
5. [시스템 아키텍처](#5-시스템-아키텍처)
6. [기술 스택](#6-기술-스택)
7. [데이터 모델](#7-데이터-모델)
8. [API 명세](#8-api-명세)
9. [보안 및 개인정보 보호](#9-보안-및-개인정보-보호)
10. [테스트 전략](#10-테스트-전략)
11. [배포 전략](#11-배포-전략)
12. [제약사항 및 가정](#12-제약사항-및-가정)

---

## 1. 소개

### 1.1 문서 목적
본 문서는 SleepFM-Wearable-Health 프로젝트의 소프트웨어 요구사항을 상세히 정의하고, 개발팀이 구현해야 할 기능적/비기능적 요구사항을 명확히 하는 것을 목표로 합니다.

### 1.2 프로젝트 범위
- **포함**: ML 백엔드 API, iOS/watchOS 앱, Android/Wear OS 앱, 데이터 파이프라인
- **제외**: 실제 임상 시험, 의료기기 인증, 상용 서비스 운영

### 1.3 대상 독자
- 개발팀 (백엔드, iOS, Android 개발자)
- ML/AI 엔지니어
- QA 엔지니어
- 프로젝트 매니저
- 연구팀

### 1.4 참조 문서
- [SleepFM 논문 (Nature Medicine, 2026)](https://www.nature.com/articles/s41591-025-04133-4)
- [SleepFM GitHub Repository](https://github.com/zou-group/sleepfm-clinical)
- Executive Summary 문서
- README.md

---

## 2. 시스템 개요

### 2.1 시스템 목표
웨어러블 기기에서 수집된 생체 신호를 기반으로 수면 분석 및 질병 위험 예측을 수행하는 연구용 프로토타입 시스템 개발

### 2.2 주요 구성 요소
1. **ML 백엔드 서비스**: 모델 추론 및 API 제공
2. **iOS 모바일 앱**: iPhone용 건강 대시보드
3. **watchOS 앱**: Apple Watch용 데이터 수집 앱
4. **Android 모바일 앱**: Android 폰용 건강 대시보드
5. **Wear OS 앱**: Samsung Galaxy Watch용 데이터 수집 앱

### 2.3 사용자 페르소나
- **연구 참여자**: 수면 데이터를 제공하고 건강 리포트를 받는 일반 사용자
- **연구자**: 데이터 수집 및 모델 성능을 모니터링하는 전문가
- **시스템 관리자**: 백엔드 서비스 운영 및 관리

---

## 3. 기능 요구사항

### 3.1 ML 백엔드 서비스

#### 3.1.1 데이터 전처리 (FR-BE-001)
- **설명**: 웨어러블 센서 데이터를 모델 입력 형식으로 변환
- **입력**: 원시 센서 데이터 (ECG, PPG, 심박수, 호흡률, 가속도 등)
- **처리**:
  - 신호 리샘플링 (128Hz)
  - 노이즈 필터링
  - 5초 윈도우 토큰화
  - 정규화 및 표준화
- **출력**: 전처리된 텐서 데이터
- **우선순위**: High

#### 3.1.2 수면 단계 분류 (FR-BE-002)
- **설명**: 수면 중 발생한 수면 단계를 분류 (Wake, N1, N2, N3, REM)
- **입력**: 전처리된 센서 데이터
- **출력**: 
  - 30초 에포크별 수면 단계 레이블
  - 각 단계별 확률 점수
  - 수면 효율성 지표
- **성능 목표**: F1 Score ≥ 0.70
- **우선순위**: High

#### 3.1.3 수면무호흡 탐지 (FR-BE-003)
- **설명**: 수면 중 무호흡 이벤트 탐지
- **입력**: 전처리된 센서 데이터
- **출력**:
  - 무호흡 이벤트 발생 시점
  - AHI (Apnea-Hypopnea Index) 점수
  - 무호흡 중증도 분류
- **성능 목표**: 정확도 ≥ 0.85
- **우선순위**: High

#### 3.1.4 질병 위험 예측 (FR-BE-004)
- **설명**: 다중 질환에 대한 위험 스코어 산출
- **입력**: 수면 임베딩, 인구통계 정보
- **출력**: 
  - 질환별 위험 스코어 (0-100)
  - 위험도 카테고리 (Low, Medium, High)
  - 신뢰 구간
- **대상 질환** (Phase 1):
  1. 파킨슨병
  2. 치매
  3. 심근경색
  4. 심부전
  5. 뇌졸중
- **성능 목표**: C-Index ≥ 0.75
- **우선순위**: High

#### 3.1.5 REST API 엔드포인트 (FR-BE-005)
- **POST /api/v1/analyze**
  - 수면 데이터 분석 요청
  - 입력: JSON (센서 데이터, 메타데이터)
  - 출력: 분석 결과 (수면 단계, 무호흡, 질병 위험)
  
- **GET /api/v1/results/{session_id}**
  - 분석 결과 조회
  - 출력: 저장된 분석 결과
  
- **GET /api/v1/health**
  - 서비스 헬스체크
  - 출력: 서비스 상태, 버전 정보

- **POST /api/v1/auth/token**
  - 인증 토큰 발급
  - 입력: 사용자 인증 정보
  - 출력: JWT 토큰

- **우선순위**: High

#### 3.1.6 모델 버전 관리 (FR-BE-006)
- **설명**: 모델 가중치 버전 관리 및 A/B 테스트
- **기능**:
  - 모델 버전별 가중치 로딩
  - 추론 결과 로깅
  - 성능 메트릭 모니터링
- **우선순위**: Medium

---

### 3.2 iOS 모바일 앱

#### 3.2.1 사용자 인증 (FR-iOS-001)
- **설명**: 안전한 사용자 로그인/회원가입
- **기능**:
  - 이메일/비밀번호 인증
  - Apple Sign-In 통합
  - 생체 인증 (Face ID, Touch ID)
- **우선순위**: High

#### 3.2.2 건강 대시보드 (FR-iOS-002)
- **설명**: 수면 분석 결과 시각화
- **화면 구성**:
  - 오늘의 수면 요약 (수면 시간, 효율성, 단계별 시간)
  - 수면 단계 타임라인 차트
  - 질병 위험 스코어 카드
  - 주간/월간 트렌드 그래프
- **우선순위**: High

#### 3.2.3 HealthKit 통합 (FR-iOS-003)
- **설명**: Apple HealthKit 데이터 읽기/쓰기
- **권한 요청**:
  - 수면 분석 읽기
  - 심박수 읽기
  - 호흡률 읽기
  - 활동 데이터 읽기
- **데이터 동기화**: 양방향 (읽기 + 쓰기)
- **우선순위**: High

#### 3.2.4 워치 데이터 동기화 (FR-iOS-004)
- **설명**: Apple Watch에서 수집된 센서 데이터 수신
- **기능**:
  - Watch Connectivity 프레임워크 사용
  - 백그라운드 데이터 전송
  - 동기화 상태 표시
- **우선순위**: High

#### 3.2.5 건강 리포트 생성 (FR-iOS-005)
- **설명**: 주간/월간 건강 리포트 PDF 생성 및 공유
- **내용**:
  - 수면 패턴 분석
  - 질병 위험 트렌드
  - 건강 권장사항
  - 데이터 차트 및 통계
- **공유**: AirDrop, 이메일, 메시지
- **우선순위**: Medium

#### 3.2.6 알림 설정 (FR-iOS-006)
- **설명**: 건강 이상 징후 알림
- **알림 유형**:
  - 고위험 질환 스코어 알림
  - 수면 품질 저하 알림
  - 수면무호흡 빈도 증가 알림
- **우선순위**: Medium

---

### 3.3 watchOS 앱

#### 3.3.1 센서 데이터 수집 (FR-Watch-001)
- **설명**: 수면 중 생체 신호 자동 수집
- **센서 종류**:
  - 심박수 (BPM)
  - 심박 변이도 (HRV)
  - 호흡률
  - 가속도계 (움직임)
  - 혈중 산소 포화도 (SpO2, 가능한 경우)
- **수집 빈도**: 1Hz (초당 1회)
- **저장**: 로컬 SQLite DB
- **우선순위**: High

#### 3.3.2 백그라운드 모니터링 (FR-Watch-002)
- **설명**: 수면 감지 시 자동 데이터 수집 시작
- **기능**:
  - 수면 상태 감지
  - 백그라운드 HealthKit 쿼리
  - 배터리 효율적 데이터 수집
- **우선순위**: High

#### 3.3.3 실시간 건강 알림 (FR-Watch-003)
- **설명**: 이상 징후 감지 시 햅틱 알림
- **알림 조건**:
  - 비정상 심박수 패턴
  - 장시간 무호흡 감지
- **우선순위**: Medium

#### 3.3.4 워치페이스 컴플리케이션 (FR-Watch-004)
- **설명**: 주요 건강 지표 워치페이스 표시
- **표시 정보**:
  - 전날 밤 수면 점수
  - 현재 주 평균 수면 시간
  - 최신 위험 스코어 요약
- **우선순위**: Low

---

### 3.4 Android 모바일 앱

#### 3.4.1 사용자 인증 (FR-Android-001)
- **설명**: 안전한 사용자 로그인/회원가입
- **기능**:
  - 이메일/비밀번호 인증
  - Google Sign-In 통합
  - 생체 인증 (지문, 얼굴 인식)
- **우선순위**: High

#### 3.4.2 건강 대시보드 (FR-Android-002)
- **설명**: 수면 분석 결과 시각화 (iOS와 동일)
- **기술**: Jetpack Compose
- **우선순위**: High

#### 3.4.3 Samsung Health SDK 통합 (FR-Android-003)
- **설명**: Samsung Health 데이터 읽기/쓰기
- **권한 요청**:
  - 수면 데이터
  - 심박수
  - 혈중 산소
  - 스트레스 레벨
- **우선순위**: High

#### 3.4.4 Wear OS 데이터 동기화 (FR-Android-004)
- **설명**: Galaxy Watch에서 수집된 센서 데이터 수신
- **기술**: Wear OS Data Layer API
- **우선순위**: High

---

### 3.5 Wear OS 앱

#### 3.5.1 센서 데이터 수집 (FR-Wear-001)
- **설명**: 수면 중 생체 신호 자동 수집 (watchOS와 유사)
- **센서 종류**:
  - 심박수
  - PPG 원시 데이터
  - 가속도계
  - SpO2
- **우선순위**: High

#### 3.5.2 백그라운드 모니터링 (FR-Wear-002)
- **설명**: 수면 감지 시 자동 데이터 수집
- **기술**: Samsung Privileged Health SDK
- **우선순위**: High

#### 3.5.3 Tile 컴플리케이션 (FR-Wear-003)
- **설명**: Wear OS Tile로 주요 건강 지표 표시
- **우선순위**: Low

---

## 4. 비기능 요구사항

### 4.1 성능 (NFR-PERF)

#### 4.1.1 API 응답 시간 (NFR-PERF-001)
- **요구사항**: 95 백분위수 응답 시간 < 2초
- **측정 지점**: API 게이트웨이에서 최종 응답까지
- **우선순위**: High

#### 4.1.2 모델 추론 시간 (NFR-PERF-002)
- **요구사항**: 8시간 수면 데이터 추론 < 10초
- **환경**: GPU 사용 시
- **우선순위**: High

#### 4.1.3 모바일 앱 반응성 (NFR-PERF-003)
- **요구사항**: UI 프레임 레이트 ≥ 60 FPS
- **측정**: 주요 화면 전환 및 스크롤
- **우선순위**: Medium

#### 4.1.4 배터리 소모 (NFR-PERF-004)
- **요구사항**: 워치 앱 실행 시 배터리 소모 < 15% (8시간 기준)
- **조건**: 백그라운드 센서 수집 중
- **우선순위**: High

---

### 4.2 확장성 (NFR-SCALE)

#### 4.2.1 동시 사용자 (NFR-SCALE-001)
- **요구사항**: 100명 동시 사용자 지원
- **Phase 1 목표**: 베타 테스트 규모
- **우선순위**: Medium

#### 4.2.2 데이터 저장 (NFR-SCALE-002)
- **요구사항**: 사용자당 최대 1년치 수면 데이터 저장 (약 365 세션)
- **추정 용량**: 사용자당 ~500MB
- **우선순위**: Medium

---

### 4.3 신뢰성 (NFR-RELIABILITY)

#### 4.3.1 시스템 가용성 (NFR-REL-001)
- **요구사항**: 99.0% 월간 가용성
- **다운타임**: 최대 7.2시간/월
- **우선순위**: Medium

#### 4.3.2 데이터 무결성 (NFR-REL-002)
- **요구사항**: 센서 데이터 손실률 < 1%
- **백업**: 일일 자동 백업
- **우선순위**: High

#### 4.3.3 앱 크래시율 (NFR-REL-003)
- **요구사항**: 크래시율 < 0.1%
- **측정**: Crashlytics/Firebase 기반
- **우선순위**: High

---

### 4.4 보안 (NFR-SECURITY)

#### 4.4.1 데이터 암호화 (NFR-SEC-001)
- **전송 중**: TLS 1.3 이상
- **저장 시**: AES-256 암호화
- **키 관리**: iOS Keychain, Android Keystore
- **우선순위**: High

#### 4.4.2 인증/인가 (NFR-SEC-002)
- **방식**: JWT 기반 토큰 인증
- **토큰 만료**: Access Token 15분, Refresh Token 7일
- **우선순위**: High

#### 4.4.3 개인정보 비식별화 (NFR-SEC-003)
- **요구사항**: 서버 전송 전 개인 식별 정보 제거 또는 해싱
- **대상**: 이름, 생년월일, 연락처 등
- **우선순위**: High

---

### 4.5 사용성 (NFR-USABILITY)

#### 4.5.1 앱 학습 곡선 (NFR-USE-001)
- **요구사항**: 신규 사용자가 5분 내 핵심 기능 사용 가능
- **온보딩**: 간단한 튜토리얼 제공
- **우선순위**: Medium

#### 4.5.2 접근성 (NFR-USE-002)
- **요구사항**: WCAG 2.1 Level AA 준수
- **기능**:
  - VoiceOver/TalkBack 지원
  - 다이나믹 타입/폰트 크기 조절
  - 고대비 모드
- **우선순위**: Medium

#### 4.5.3 다국어 지원 (NFR-USE-003)
- **Phase 1**: 한국어, 영어
- **향후**: 일본어, 중국어
- **우선순위**: Medium

---

### 4.6 유지보수성 (NFR-MAINTAIN)

#### 4.6.1 코드 품질 (NFR-MAIN-001)
- **요구사항**:
  - 테스트 커버리지 ≥ 70%
  - Linter 규칙 준수 (SwiftLint, Ktlint, Pylint)
  - 코드 리뷰 필수
- **우선순위**: High

#### 4.6.2 문서화 (NFR-MAIN-002)
- **요구사항**:
  - API 문서 (OpenAPI/Swagger)
  - 코드 주석 (함수별 docstring)
  - 아키텍처 다이어그램
- **우선순위**: Medium

#### 4.6.3 모니터링/로깅 (NFR-MAIN-003)
- **요구사항**:
  - 구조화된 로깅 (JSON 형식)
  - 에러 추적 (Sentry/Crashlytics)
  - 성능 모니터링 (APM 도구)
- **우선순위**: High

---

## 5. 시스템 아키텍처

### 5.1 전체 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
├──────────────────┬──────────────────┬───────────────────────────┤
│   iOS App        │  Android App     │   Web Dashboard (Future)  │
│   (SwiftUI)      │  (Compose)       │                           │
├──────────────────┼──────────────────┤                           │
│  watchOS App     │  Wear OS App     │                           │
│  (WatchKit)      │  (Wear Compose)  │                           │
└────────┬─────────┴──────────┬───────┴───────────────────────────┘
         │                    │
         └────────┬───────────┘
                  │ HTTPS (TLS 1.3)
                  ▼
         ┌────────────────────┐
         │   API Gateway      │
         │   (FastAPI)        │
         │   - Auth           │
         │   - Rate Limiting  │
         └────────┬───────────┘
                  │
         ┌────────┴───────────┐
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│ Analysis Service│  │  User Service   │
│ - Preprocessing │  │  - Auth         │
│ - Inference     │  │  - Profile      │
└────────┬────────┘  └─────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      ML Inference Engine             │
│  ┌────────────┐  ┌────────────────┐ │
│  │  SleepFM   │  │  Disease Risk  │ │
│  │  Encoder   │→ │  Predictor     │ │
│  └────────────┘  └────────────────┘ │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Data Storage   │
│  - PostgreSQL   │
│  - S3/Blob      │
└─────────────────┘
```

### 5.2 데이터 플로우

```
[Wearable Device] → [Sensor Data Collection]
                             ↓
                    [Local Storage (SQLite)]
                             ↓
                    [Mobile App Sync]
                             ↓
              [Data Upload (Encrypted HTTPS)]
                             ↓
                    [API Gateway (Auth)]
                             ↓
                    [Preprocessing Service]
                             ↓
                    [ML Inference Engine]
                             ↓
              [Results Storage (Database)]
                             ↓
              [Mobile App Result Fetch]
                             ↓
              [Dashboard Visualization]
```

### 5.3 컴포넌트 상세

#### 5.3.1 백엔드 컴포넌트
- **API Gateway**: FastAPI, Nginx reverse proxy
- **Analysis Service**: Python, PyTorch
- **User Service**: Python, SQLAlchemy
- **Database**: PostgreSQL 14+
- **Object Storage**: AWS S3 / Azure Blob Storage (센서 데이터 원본)
- **Cache**: Redis (세션, 임시 결과)

#### 5.3.2 모바일 컴포넌트
- **iOS App**: SwiftUI, Combine, HealthKit
- **watchOS App**: WatchKit, HealthKit
- **Android App**: Jetpack Compose, Kotlin Coroutines, Samsung Health SDK
- **Wear OS App**: Wear Compose, Sensor API

---

## 6. 기술 스택

### 6.1 백엔드

| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| 언어 | Python | 3.10+ | 주 개발 언어 |
| 프레임워크 | FastAPI | 0.100+ | REST API |
| ML 프레임워크 | PyTorch | 2.0+ | 모델 추론 |
| 데이터베이스 | PostgreSQL | 14+ | 주 데이터 저장소 |
| 캐시 | Redis | 7.0+ | 세션, 결과 캐싱 |
| Object Storage | AWS S3 / Azure Blob | - | 센서 데이터 원본 |
| 배포 | Docker + K8s | - | 컨테이너화 |
| 모니터링 | Prometheus + Grafana | - | 메트릭 수집 |

### 6.2 iOS/watchOS

| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| 언어 | Swift | 5.9+ | 주 개발 언어 |
| UI | SwiftUI | iOS 17+ | UI 프레임워크 |
| 비동기 | Combine / async-await | - | 비동기 처리 |
| 데이터 수집 | HealthKit | iOS 17+ | 건강 데이터 |
| 로컬 DB | Core Data / SQLite | - | 로컬 저장소 |
| 네트워킹 | URLSession / Alamofire | - | HTTP 통신 |
| 차트 | Swift Charts | iOS 16+ | 데이터 시각화 |

### 6.3 Android/Wear OS

| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| 언어 | Kotlin | 1.9+ | 주 개발 언어 |
| UI | Jetpack Compose | 1.5+ | UI 프레임워크 |
| 아키텍처 | MVVM + Clean Architecture | - | 앱 구조 |
| 비동기 | Kotlin Coroutines + Flow | - | 비동기 처리 |
| 데이터 수집 | Samsung Health SDK | 1.5+ | 건강 데이터 |
| 로컬 DB | Room | 2.5+ | 로컬 저장소 |
| 네트워킹 | Retrofit + OkHttp | 2.9+ | HTTP 통신 |
| 차트 | MPAndroidChart / Compose Charts | - | 데이터 시각화 |

### 6.4 개발 도구

| 구분 | 도구 |
|------|------|
| IDE | Xcode 15+, Android Studio Hedgehog+ |
| 버전 관리 | Git, GitHub |
| CI/CD | GitHub Actions |
| 이슈 관리 | GitHub Issues / Jira |
| 문서 | Markdown, Notion |
| 디자인 | Figma |

---

## 7. 데이터 모델

### 7.1 데이터베이스 스키마

#### 7.1.1 Users 테이블
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    date_of_birth DATE,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 7.1.2 SleepSessions 테이블
```sql
CREATE TABLE sleep_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    total_sleep_duration INTEGER, -- 분 단위
    sleep_efficiency FLOAT,
    raw_data_url TEXT, -- S3/Blob 저장소 경로
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, session_date)
);
```

#### 7.1.3 SleepStages 테이블
```sql
CREATE TABLE sleep_stages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sleep_sessions(id) ON DELETE CASCADE,
    epoch_index INTEGER NOT NULL, -- 30초 에포크 인덱스
    stage VARCHAR(10) NOT NULL, -- 'wake', 'n1', 'n2', 'n3', 'rem'
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 7.1.4 ApneaEvents 테이블
```sql
CREATE TABLE apnea_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sleep_sessions(id) ON DELETE CASCADE,
    event_time TIMESTAMP NOT NULL,
    event_type VARCHAR(20), -- 'obstructive', 'central', 'mixed'
    duration INTEGER, -- 초 단위
    severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 7.1.5 DiseaseRiskScores 테이블
```sql
CREATE TABLE disease_risk_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sleep_sessions(id) ON DELETE CASCADE,
    disease_name VARCHAR(100) NOT NULL,
    risk_score FLOAT NOT NULL, -- 0-100
    risk_category VARCHAR(20), -- 'low', 'medium', 'high'
    confidence_lower FLOAT,
    confidence_upper FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 7.2 API 요청/응답 모델 (JSON)

#### 7.2.1 분석 요청 (POST /api/v1/analyze)
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_date": "2026-01-07",
  "start_time": "2026-01-07T23:00:00Z",
  "end_time": "2026-01-08T07:00:00Z",
  "sensor_data": {
    "heart_rate": [65, 63, 62, ...],
    "respiratory_rate": [14, 15, 14, ...],
    "accelerometer": {
      "x": [0.01, -0.02, ...],
      "y": [0.00, 0.01, ...],
      "z": [9.81, 9.80, ...]
    },
    "spo2": [98, 97, 98, ...] // optional
  },
  "metadata": {
    "device_type": "apple_watch_series_9",
    "sampling_rate": 1.0
  }
}
```

#### 7.2.2 분석 응답
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "results": {
    "sleep_summary": {
      "total_sleep_duration_minutes": 450,
      "sleep_efficiency": 0.88,
      "wake_duration_minutes": 30,
      "n1_duration_minutes": 50,
      "n2_duration_minutes": 200,
      "n3_duration_minutes": 100,
      "rem_duration_minutes": 100
    },
    "sleep_stages": [
      {"epoch": 0, "stage": "wake", "confidence": 0.92},
      {"epoch": 1, "stage": "n1", "confidence": 0.78},
      ...
    ],
    "apnea_analysis": {
      "ahi_score": 8.5,
      "severity": "mild",
      "total_events": 34
    },
    "disease_risks": [
      {
        "disease": "parkinsons_disease",
        "risk_score": 15.3,
        "risk_category": "low",
        "confidence_interval": [12.1, 18.5]
      },
      {
        "disease": "dementia",
        "risk_score": 28.7,
        "risk_category": "low",
        "confidence_interval": [24.2, 33.1]
      },
      ...
    ]
  },
  "created_at": "2026-01-08T07:15:00Z"
}
```

---

## 8. API 명세

### 8.1 인증 API

#### 8.1.1 회원가입
- **Endpoint**: `POST /api/v1/auth/register`
- **Request**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "홍길동",
    "date_of_birth": "1990-01-01",
    "gender": "male"
  }
  ```
- **Response** (201):
  ```json
  {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "message": "User registered successfully"
  }
  ```

#### 8.1.2 로그인
- **Endpoint**: `POST /api/v1/auth/token`
- **Request**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123!"
  }
  ```
- **Response** (200):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900
  }
  ```

### 8.2 분석 API

#### 8.2.1 수면 데이터 분석
- **Endpoint**: `POST /api/v1/analyze`
- **Headers**: `Authorization: Bearer {access_token}`
- **Request**: 위의 7.2.1 참조
- **Response** (200): 위의 7.2.2 참조

#### 8.2.2 분석 결과 조회
- **Endpoint**: `GET /api/v1/results/{session_id}`
- **Headers**: `Authorization: Bearer {access_token}`
- **Response** (200): 위의 7.2.2 참조

#### 8.2.3 사용자 전체 세션 목록
- **Endpoint**: `GET /api/v1/users/{user_id}/sessions`
- **Query Parameters**: 
  - `from_date` (optional): YYYY-MM-DD
  - `to_date` (optional): YYYY-MM-DD
  - `limit` (optional): integer, default 30
- **Response** (200):
  ```json
  {
    "sessions": [
      {
        "session_id": "...",
        "session_date": "2026-01-07",
        "total_sleep_duration_minutes": 450,
        "sleep_efficiency": 0.88
      },
      ...
    ],
    "total_count": 15
  }
  ```

### 8.3 헬스체크 API

#### 8.3.1 서비스 상태
- **Endpoint**: `GET /api/v1/health`
- **Response** (200):
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2026-01-08T10:00:00Z"
  }
  ```

---

## 9. 보안 및 개인정보 보호

### 9.1 인증/인가
- **JWT 기반 토큰 인증**: Access Token (15분), Refresh Token (7일)
- **OAuth 2.0 통합**: Apple Sign-In, Google Sign-In
- **비밀번호**: bcrypt 해싱 (cost factor 12)

### 9.2 데이터 보호
- **전송 중 암호화**: TLS 1.3
- **저장 시 암호화**: AES-256 (데이터베이스 컬럼 암호화)
- **키 관리**: 
  - iOS: Keychain Services
  - Android: Android Keystore
  - Backend: AWS KMS / Azure Key Vault

### 9.3 개인정보 처리
- **최소 수집 원칙**: 분석에 필요한 최소한의 정보만 수집
- **동의 관리**: 명시적 사용자 동의 후 데이터 수집
- **데이터 보유 기간**: 최대 1년, 사용자 요청 시 즉시 삭제
- **익명화**: 연구 목적 사용 시 개인 식별 정보 제거

### 9.4 접근 제어
- **RBAC (Role-Based Access Control)**: 사용자, 연구자, 관리자 역할 분리
- **API Rate Limiting**: 사용자당 100 req/min
- **IP Whitelist**: 관리자 API는 특정 IP만 접근 허용

---

## 10. 테스트 전략

### 10.1 단위 테스트
- **커버리지 목표**: 70% 이상
- **프레임워크**:
  - Backend: pytest
  - iOS: XCTest
  - Android: JUnit + MockK
- **자동화**: CI/CD 파이프라인에서 자동 실행

### 10.2 통합 테스트
- **API 테스트**: Postman/Newman 스크립트
- **E2E 테스트**: 
  - iOS: XCUITest
  - Android: Espresso
- **주기**: 주 1회 자동 실행

### 10.3 성능 테스트
- **부하 테스트**: Locust (100 동시 사용자)
- **스트레스 테스트**: API 한계 지점 확인
- **주기**: 주요 릴리스 전

### 10.4 사용자 수용 테스트 (UAT)
- **베타 테스터**: 10-20명
- **기간**: 2주
- **피드백 수집**: Google Forms, 인터뷰

---

## 11. 배포 전략

### 11.1 백엔드 배포
- **컨테이너화**: Docker
- **오케스트레이션**: Kubernetes (GKE/EKS/AKS)
- **CI/CD**: GitHub Actions
  - PR 시: 린트, 테스트 자동 실행
  - main 브랜치 머지 시: 스테이징 환경 자동 배포
  - 태그 푸시 시: 프로덕션 환경 배포
- **무중단 배포**: Blue-Green 또는 Canary 배포

### 11.2 모바일 앱 배포
- **iOS**: TestFlight (베타) → App Store
- **Android**: Google Play Console (내부/비공개 테스트) → 공개
- **버전 관리**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **릴리스 주기**: 2주 단위 스프린트

### 11.3 환경 구성
- **Development**: 로컬 개발 환경
- **Staging**: 프로덕션 유사 환경, 베타 테스트용
- **Production**: 실제 서비스 환경

---

## 12. 제약사항 및 가정

### 12.1 제약사항
1. **연구 목적만 사용 가능**: 의료기기 인증 없음, 진단 목적 사용 금지
2. **공개 데이터셋 사용**: DUA(Data Use Agreement) 준수 필수
3. **웨어러블 센서 제약**: PSG 대비 채널 수 제한, 정확도 차이 존재
4. **배터리 제약**: 연속 센서 수집 시 배터리 소모 불가피
5. **플랫폼 제약**: Apple Health/Samsung Health SDK 정책 준수

### 12.2 가정
1. **사용자 준수**: 사용자가 매일 밤 워치 착용 및 충전
2. **네트워크 연결**: 모바일 앱이 주기적으로 인터넷 연결 가능
3. **데이터 품질**: 센서 데이터 노이즈는 일정 수준 이하
4. **모델 성능**: SleepFM 모델의 웨어러블 데이터 적용 시 성능 유지 (PSG 대비 10% 이내 성능 저하)
5. **규제 준수**: 베타 단계에서는 연구용 라벨로 운영, 상용화 시 별도 인증 진행

---

## 부록

### A. 용어 정의
- **PSG (Polysomnography)**: 수면다원검사, 수면 중 뇌파, 심전도, 호흡 등을 측정하는 종합 검사
- **C-Index**: Concordance Index, 생존 분석에서 모델 성능 평가 지표 (0.5=무작위, 1.0=완벽)
- **AHI (Apnea-Hypopnea Index)**: 시간당 무호흡/저호흡 발생 횟수
- **F1 Score**: 정밀도와 재현율의 조화 평균, 분류 모델 평가 지표
- **에포크 (Epoch)**: 수면 분석에서 30초 단위 시간 구간

### B. 참조 문서
- [SleepFM 논문](https://www.nature.com/articles/s41591-025-04133-4)
- [SleepFM GitHub](https://github.com/zou-group/sleepfm-clinical)
- [HealthKit Documentation](https://developer.apple.com/documentation/healthkit)
- [Samsung Health SDK](https://developer.samsung.com/health)

### C. 변경 이력
| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-01-08 | 초안 작성 | Development Team |

---

**문서 승인:**
- [ ] 프로젝트 매니저
- [ ] 기술 리드 (Backend)
- [ ] 기술 리드 (iOS)
- [ ] 기술 리드 (Android)
- [ ] QA 리드

**다음 단계:** Sprint Planning 및 백로그 작성
