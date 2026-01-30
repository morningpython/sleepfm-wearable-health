# SleepFM Sprint Plan - Phase 4: Android & Wear OS 개발

**문서 버전**: 1.0  
**작성일**: 2026-01-29  
**Phase 목표**: Android 모바일 앱 및 Wear OS 웨어러블 앱 개발  
**총 기간**: 4주 (Sprint 13-14)

---

## 목차
1. [Phase 4 개요](#phase-4-개요)
2. [Sprint 13: Android 앱 기반 구조](#sprint-13-android-앱-기반-구조)
3. [Sprint 14: Wear OS 및 통합](#sprint-14-wear-os-및-통합)
4. [Phase 4 완료 기준](#phase-4-완료-기준)

---

## Phase 4 개요

### 배경
Phase 1-3에서 백엔드 API, iOS/watchOS 앱 개발이 완료되었습니다.  
Phase 4에서는 Android 생태계를 지원하여 전체 사용자층을 확보합니다.

### 목표
- ✅ Android 모바일 앱 (Android Phone)
- ✅ Wear OS 앱 (Samsung Galaxy Watch, Google Pixel Watch)
- ✅ iOS와 동일한 사용자 경험 제공
- ✅ 기존 백엔드 API 100% 활용

### 팀 구성
| 역할 | 인원 | 담당 |
|------|------|------|
| Android Lead | 1명 | Android/Wear OS 개발 총괄 |
| Android Developer | 1명 | UI/비즈니스 로직 구현 |
| QA | 1명 | 테스트 및 품질 관리 |

### 기술 스택
```
Android App:
├── Kotlin 1.9+
├── Jetpack Compose (UI)
├── Hilt (DI)
├── Retrofit + OkHttp (네트워크)
├── Room (로컬 DB)
├── DataStore (설정 저장)
└── Health Connect API

Wear OS App:
├── Wear Compose
├── Health Services API
├── Data Layer API (Phone 연동)
└── Room (로컬 저장)
```

### 주요 의존성
```kotlin
// build.gradle.kts (app)
dependencies {
    // Compose
    implementation("androidx.compose.ui:ui:1.6.0")
    implementation("androidx.compose.material3:material3:1.2.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    
    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.6")
    
    // Hilt
    implementation("com.google.dagger:hilt-android:2.50")
    kapt("com.google.dagger:hilt-compiler:2.50")
    
    // Network
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    
    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")
    
    // Health Connect
    implementation("androidx.health.connect:connect-client:1.1.0-alpha06")
    
    // DataStore
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
```

---

## Sprint 13: Android 앱 기반 구조
**기간**: 2주  
**Sprint 목표**: Android 앱 프로젝트 설정 및 iOS와 동일한 인증/대시보드 구현  
**총 Story Points**: 21

---

### 🤖 User Story 13.1: Android 프로젝트 초기 설정
**Epic**: Android 앱 개발  
**Story Points**: 3  
**우선순위**: P0

**As an** Android Developer  
**I want to** Android Studio 프로젝트를 초기 설정  
**So that** 팀이 Android 앱 개발을 시작할 수 있다

**Description**:
- Android Studio 프로젝트 생성 (Kotlin, Jetpack Compose)
- Gradle 의존성 관리 (Version Catalog)
- Ktlint/Detekt 설정
- MVVM + Clean Architecture 구조

**Acceptance Criteria**:
- [ ] 프로젝트가 에뮬레이터에서 실행됨
- [ ] Jetpack Compose UI 표시
- [ ] 폴더 구조: `ui/`, `data/`, `domain/`, `di/`
- [ ] Ktlint 적용 및 CI 연동
- [ ] `.gitignore` 설정

**Tasks**:
```
- [ ] Android Studio 프로젝트 생성 (Empty Compose Activity)
- [ ] Version Catalog (libs.versions.toml) 설정
- [ ] build.gradle.kts 의존성 추가
- [ ] 폴더 구조 생성
    android/
    └── app/
        └── src/main/java/io/sleepfm/android/
            ├── ui/
            │   ├── theme/
            │   ├── components/
            │   └── screens/
            ├── data/
            │   ├── api/
            │   ├── local/
            │   └── repository/
            ├── domain/
            │   ├── model/
            │   └── usecase/
            └── di/
- [ ] Hilt 설정 (@HiltAndroidApp)
- [ ] Ktlint/Detekt 설정
```

**Testing**:
- Unit Test: N/A
- E2E Test: 앱 실행 확인

**Definition of Done**:
- [ ] 코드 리뷰 완료
- [ ] CI 빌드 성공
- [ ] 에뮬레이터/실기기 실행 확인

---

### 🤖 User Story 13.2: Android 인증 화면 구현
**Epic**: Android 앱 개발  
**Story Points**: 5  
**우선순위**: P0

**As an** App User  
**I want to** Android 앱에서 회원가입/로그인  
**So that** iOS와 동일한 방식으로 인증할 수 있다

**Description**:
- 온보딩 화면 (HorizontalPager)
- 회원가입 화면 (Composable Form)
- 로그인 화면
- Google Sign-In 통합 (선택)
- JWT 토큰 EncryptedSharedPreferences/DataStore 저장

**Acceptance Criteria**:
- [ ] 온보딩 화면 스와이프 가능 (3페이지)
- [ ] 회원가입 폼 검증 (이메일, 비밀번호 8자 이상)
- [ ] 로그인 성공 시 토큰 저장 및 대시보드 이동
- [ ] 에러 메시지 표시 (Toast/Snackbar)
- [ ] iOS와 동일한 UI/UX

**Tasks**:
```
- [ ] OnboardingScreen.kt
    - HorizontalPager
    - 3개 페이지 (앱 소개)
    - 시작하기 버튼
- [ ] SignUpScreen.kt
    - 이메일/비밀번호/이름 입력
    - 실시간 유효성 검증
    - 회원가입 API 호출
- [ ] LoginScreen.kt
    - 이메일/비밀번호 입력
    - 로그인 API 호출
    - 토큰 저장
- [ ] AuthRepository.kt
    - register(), login(), logout()
    - 토큰 관리
- [ ] AuthViewModel.kt
    - UI 상태 관리
    - 에러 핸들링
- [ ] TokenManager.kt (DataStore)
    - Access/Refresh Token 저장
    - 자동 갱신 로직
```

**API Endpoints**:
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

**Testing**:
- Unit Test: 이메일/비밀번호 검증 로직
- Unit Test: AuthRepository (Mock API)
- E2E Test: 회원가입 → 로그인 → 토큰 저장

---

### 🤖 User Story 13.3: Android 네비게이션 구조
**Epic**: Android 앱 개발  
**Story Points**: 3  
**우선순위**: P0

**As an** App User  
**I want to** Android 앱 내에서 쉽게 화면 이동  
**So that** iOS와 동일한 네비게이션 경험을 얻을 수 있다

**Description**:
- Navigation Compose 기반 라우팅
- BottomNavigation (대시보드, 히스토리, 설정)
- 인증 상태 기반 라우팅

**Acceptance Criteria**:
- [ ] 하단 네비게이션 바 3개 탭
- [ ] 탭 전환 애니메이션
- [ ] 미로그인 시 로그인 화면 리다이렉트
- [ ] 뒤로가기 네비게이션

**Tasks**:
```
- [ ] Navigation.kt (NavHost 설정)
    sealed class Screen {
        object Onboarding
        object Login
        object SignUp
        object Dashboard
        object History
        object Settings
    }
- [ ] MainNavigation.kt
    - 인증 상태 체크
    - 조건부 시작 화면
- [ ] BottomNavigationBar.kt
    - 3개 탭 아이콘
    - 선택 상태 표시
- [ ] 스켈레톤 화면들
    - DashboardScreen
    - HistoryScreen
    - SettingsScreen
```

**Testing**:
- Component Test: 네비게이션 동작 확인
- E2E Test: 로그인 → 탭 전환 → 로그아웃

---

### 🤖 User Story 13.4: Health Connect 연동
**Epic**: Android 앱 개발  
**Story Points**: 5  
**우선순위**: P1

**As an** App User  
**I want to** Health Connect 권한을 허용  
**So that** 앱이 내 건강 데이터를 읽을 수 있다

**Description**:
- Health Connect API 설정
- 권한 요청 (수면, 심박수, 산소포화도)
- 데이터 읽기
- 기존 Samsung Health 데이터도 Health Connect로 접근

**Acceptance Criteria**:
- [ ] Health Connect 앱 설치 확인 및 안내
- [ ] 권한 요청 다이얼로그 표시
- [ ] 수면, 심박수, SpO2 데이터 읽기 성공
- [ ] 권한 거부 시 안내 메시지
- [ ] 에러 핸들링

**Tasks**:
```
- [ ] AndroidManifest.xml 권한 추가
    <uses-permission android:name="android.permission.health.READ_SLEEP"/>
    <uses-permission android:name="android.permission.health.READ_HEART_RATE"/>
    <uses-permission android:name="android.permission.health.READ_OXYGEN_SATURATION"/>
- [ ] HealthConnectManager.kt
    - checkAvailability()
    - requestPermissions()
    - readSleepSessions()
    - readHeartRate()
    - readOxygenSaturation()
- [ ] HealthRepository.kt
    - 데이터 변환 (Health Connect → Domain Model)
- [ ] 권한 요청 UI
    - 설명 화면
    - 권한 요청 버튼
    - 거부 시 안내
```

**Testing**:
- Unit Test: 데이터 변환 로직
- Integration Test: Health Connect API 호출 (실기기)
- E2E Test: 권한 요청 → 데이터 읽기

---

### 🤖 User Story 13.5: Android 대시보드 UI
**Epic**: Android 앱 개발  
**Story Points**: 5  
**우선순위**: P0

**As an** App User  
**I want to** Android에서 iOS와 동일한 대시보드 확인  
**So that** 플랫폼에 관계없이 일관된 경험을 얻을 수 있다

**Description**:
- 대시보드 메인 화면 (iOS와 동일)
- 수면 요약 카드
- 수면 단계 차트 (Compose Charts)
- 질병 위험 카드

**Acceptance Criteria**:
- [ ] iOS와 동일한 레이아웃
- [ ] 수면 요약 카드 표시 (수면 시간, 효율, 품질 점수)
- [ ] 수면 단계 막대 차트
- [ ] 질병 위험 카드 (상위 3개)
- [ ] Pull-to-refresh
- [ ] 로딩/에러 상태 표시

**Tasks**:
```
- [ ] DashboardScreen.kt
    - SwipeRefresh
    - LazyColumn 레이아웃
- [ ] SleepSummaryCard.kt
    - 총 수면 시간
    - 수면 효율 %
    - 품질 점수
- [ ] SleepStageChart.kt
    - 수면 단계 시각화 (Wake, Light, Deep, REM)
    - 시간대별 막대 차트
- [ ] DiseaseRiskCard.kt
    - 위험 질병 목록
    - 위험도 색상 표시
- [ ] DashboardViewModel.kt
    - API 호출
    - 상태 관리 (Loading, Success, Error)
- [ ] DashboardRepository.kt
    - 대시보드 데이터 fetch
```

**API Endpoints**:
```
GET /api/v1/sessions/latest
GET /api/v1/analysis/{session_id}
GET /api/v1/analysis/disease-risk/{session_id}
```

**Testing**:
- Unit Test: ViewModel 로직
- Component Test: 각 Composable 렌더링
- E2E Test: API → 대시보드 표시

---

### Sprint 13 완료 기준
- [ ] Android 앱 실행 및 인증 동작
- [ ] Health Connect 데이터 읽기 성공
- [ ] 대시보드 기본 UI 표시
- [ ] iOS와 UI 일관성 확인
- [ ] 단위 테스트 커버리지 ≥ 60%

---

## Sprint 14: Wear OS 및 통합
**기간**: 2주  
**Sprint 목표**: Wear OS 앱 개발 및 전체 플랫폼 통합  
**총 Story Points**: 21

---

### ⌚ User Story 14.1: Wear OS 프로젝트 설정
**Epic**: Wear OS 앱 개발  
**Story Points**: 3  
**우선순위**: P0

**As an** Android Developer  
**I want to** Wear OS 모듈을 추가  
**So that** Galaxy Watch/Pixel Watch 앱을 개발할 수 있다

**Description**:
- Wear OS 모듈 생성
- Wear Compose 설정
- 휴대폰 앱과 데이터 공유 설정

**Acceptance Criteria**:
- [ ] Wear 모듈 빌드 성공
- [ ] Wear 에뮬레이터에서 앱 실행
- [ ] 휴대폰 앱과 연결 가능
- [ ] Wear Compose UI 표시

**Tasks**:
```
- [ ] Wear OS 모듈 추가 (New > Module > Wear OS)
- [ ] build.gradle.kts 설정
    android/
    ├── app/                 # Phone 앱
    └── wear/                # Wear OS 앱
        └── src/main/java/io/sleepfm/wear/
            ├── presentation/
            ├── data/
            └── service/
- [ ] Wear Compose 의존성
    implementation("androidx.wear.compose:compose-material:1.3.0")
    implementation("androidx.wear.compose:compose-foundation:1.3.0")
- [ ] Data Layer API 설정
- [ ] 기본 WearApp Screen
```

**Testing**:
- E2E Test: Wear 앱 실행 확인

---

### ⌚ User Story 14.2: Wear 센서 데이터 수집
**Epic**: Wear OS 앱 개발  
**Story Points**: 8  
**우선순위**: P0

**As a** Wear App  
**I want to** 수면 중 센서 데이터를 자동 수집  
**So that** watchOS와 동일한 기능을 제공할 수 있다

**Description**:
- Health Services API 사용
- 심박수, 가속도, SpO2 수집
- 1Hz 샘플링
- 로컬 Room DB 저장
- 수면 감지 자동 시작

**Acceptance Criteria**:
- [ ] 수면 감지 시 자동 수집 시작
- [ ] 센서 데이터 1초마다 기록
- [ ] Room DB에 저장
- [ ] 배터리 소모 < 15% (8시간 수면)
- [ ] watchOS 앱과 동일한 기능

**Tasks**:
```
- [ ] Health Services 설정
    implementation("androidx.health:health-services-client:1.0.0-rc01")
- [ ] SensorCollectionService.kt (Foreground Service)
    - 심박수 수집
    - 가속도계 수집
    - SpO2 수집 (가능한 경우)
- [ ] SleepDetector.kt
    - 움직임 감지 기반 수면 시작/종료
- [ ] Room Database
    @Entity
    data class SensorReading(
        @PrimaryKey val id: Long,
        val timestamp: Long,
        val heartRate: Float?,
        val accelerometerX: Float?,
        val accelerometerY: Float?,
        val accelerometerZ: Float?,
        val spO2: Float?
    )
- [ ] 배터리 최적화
    - Doze 모드 대응
    - 배치 처리
```

**Testing**:
- Unit Test: 센서 데이터 파싱
- Integration Test: Room DB 저장 확인
- E2E Test: 실제 Watch에서 수집 확인

---

### ⌚ User Story 14.3: Wear-Phone 데이터 동기화
**Epic**: Wear OS 앱 개발  
**Story Points**: 5  
**우선순위**: P0

**As a** Wear App  
**I want to** 수집한 데이터를 휴대폰으로 전송  
**So that** 서버에 업로드할 수 있다

**Description**:
- Data Layer API로 데이터 전송
- 백그라운드 전송
- 재시도 로직
- 전송 완료 후 로컬 삭제

**Acceptance Criteria**:
- [ ] 수면 종료 후 자동 전송
- [ ] 전송 진행률 표시
- [ ] 실패 시 3회 재시도
- [ ] 백그라운드 전송 지원
- [ ] 전송 완료 후 DB 삭제

**Tasks**:
```
- [ ] Data Layer API 설정
    implementation("com.google.android.gms:play-services-wearable:18.1.0")
- [ ] DataSyncManager.kt
    - DataClient로 데이터 전송
    - 청크 분할 (대용량 데이터)
- [ ] Phone 앱 WearableListenerService
    - 데이터 수신 핸들러
    - 서버 업로드 트리거
- [ ] 재시도 로직 (WorkManager)
- [ ] UI 진행률 표시
```

**Testing**:
- Unit Test: 데이터 직렬화
- Integration Test: Wear → Phone 전송 확인
- E2E Test: 전체 동기화 플로우

---

### 🔗 User Story 14.4: 전체 플랫폼 통합 테스트
**Epic**: 크로스 플랫폼 통합  
**Story Points**: 3  
**우선순위**: P1

**As a** QA Engineer  
**I want to** iOS/Android 플랫폼 모두에서 동일한 데이터 플로우 동작 확인  
**So that** 사용자 경험을 일관되게 유지할 수 있다

**Description**:
- 웨어러블 → 모바일 → 서버 데이터 플로우 검증
- 양 플랫폼에서 동일한 API 응답 처리
- 에러 핸들링 통일

**Acceptance Criteria**:
- [ ] iOS/Android 모두 동일한 API 엔드포인트 사용
- [ ] 응답 파싱 로직 동일
- [ ] 네트워크 에러 시 동일한 재시도 정책
- [ ] 오프라인 시 로컬 캐싱
- [ ] 온라인 복귀 시 자동 동기화

**Tasks**:
```
- [ ] API 호출 로직 검증
- [ ] 에러 코드 및 메시지 통일 확인
- [ ] 오프라인 모드 테스트
- [ ] 크로스 플랫폼 E2E 테스트 스크립트
```

**Testing**:
- E2E Test: 전체 플로우 (센서 수집 → 서버 업로드 → 결과 조회)

---

### 🎨 User Story 14.5: Android 히스토리 및 설정 화면
**Epic**: Android 앱 개발  
**Story Points**: 2  
**우선순위**: P1

**As an** App User  
**I want to** 수면 히스토리와 앱 설정을 확인  
**So that** 과거 수면 기록을 보고 앱을 커스터마이즈할 수 있다

**Description**:
- 히스토리 화면 (수면 기록 목록)
- 설정 화면 (알림, 계정, 데이터 관리)

**Acceptance Criteria**:
- [ ] 수면 히스토리 목록 표시
- [ ] 날짜별 필터링
- [ ] 설정 화면 구성
- [ ] 로그아웃 기능

**Tasks**:
```
- [ ] HistoryScreen.kt
    - LazyColumn 수면 기록 목록
    - 날짜 선택 필터
- [ ] HistoryViewModel.kt
- [ ] SettingsScreen.kt
    - 알림 설정
    - 계정 정보
    - 데이터 내보내기
    - 로그아웃
    - 앱 버전
- [ ] SettingsViewModel.kt
```

**Testing**:
- Unit Test: ViewModel 로직
- E2E Test: 히스토리 조회, 설정 변경

---

### Sprint 14 완료 기준
- [ ] Wear OS 앱 센서 수집 및 동기화 성공
- [ ] iOS/Android 양 플랫폼 데이터 플로우 검증
- [ ] 히스토리/설정 화면 완성
- [ ] 크로스 플랫폼 E2E 테스트 통과
- [ ] 단위 테스트 커버리지 ≥ 60%

---

## Phase 4 완료 기준

### 기능적 완료 기준
- [ ] Android 앱 (Phone) 실행 가능
- [ ] Wear OS 앱 (Galaxy Watch/Pixel Watch) 센서 수집
- [ ] 모든 플랫폼에서 인증 동작
- [ ] Health Connect 데이터 읽기
- [ ] 대시보드 UI 완성 (iOS와 동일)
- [ ] 웨어러블 → 모바일 → 서버 데이터 플로우 검증

### 비기능적 완료 기준
- [ ] 단위 테스트 커버리지 ≥ 60%
- [ ] UI 테스트 작성 (주요 화면)
- [ ] E2E 테스트 통과 (전체 플로우)
- [ ] 배터리 소모 < 15% (8시간 수면)
- [ ] UI 프레임 레이트 ≥ 60 FPS
- [ ] 앱 크래시율 < 0.1%

### 문서화 완료 기준
- [ ] Android 개발자 문서 (앱 아키텍처)
- [ ] Health Connect 연동 가이드
- [ ] Wear OS 개발 가이드

### 품질 기준
- [ ] 코드 리뷰 완료
- [ ] Ktlint/Detekt 규칙 준수
- [ ] Material Design 3 가이드라인 준수

---

## 부록

### A. 프로젝트 구조
```
android/
├── app/                              # Phone 앱
│   ├── src/main/
│   │   ├── java/io/sleepfm/android/
│   │   │   ├── SleepFMApplication.kt
│   │   │   ├── MainActivity.kt
│   │   │   ├── ui/
│   │   │   │   ├── theme/
│   │   │   │   │   ├── Color.kt
│   │   │   │   │   ├── Theme.kt
│   │   │   │   │   └── Type.kt
│   │   │   │   ├── components/
│   │   │   │   │   ├── SleepChart.kt
│   │   │   │   │   └── RiskCard.kt
│   │   │   │   ├── screens/
│   │   │   │   │   ├── onboarding/
│   │   │   │   │   ├── auth/
│   │   │   │   │   ├── dashboard/
│   │   │   │   │   ├── history/
│   │   │   │   │   └── settings/
│   │   │   │   └── navigation/
│   │   │   │       └── Navigation.kt
│   │   │   ├── data/
│   │   │   │   ├── api/
│   │   │   │   │   ├── SleepFMApi.kt
│   │   │   │   │   └── AuthInterceptor.kt
│   │   │   │   ├── local/
│   │   │   │   │   ├── TokenManager.kt
│   │   │   │   │   └── SleepDatabase.kt
│   │   │   │   └── repository/
│   │   │   │       ├── AuthRepository.kt
│   │   │   │       └── SleepRepository.kt
│   │   │   ├── domain/
│   │   │   │   ├── model/
│   │   │   │   │   ├── User.kt
│   │   │   │   │   └── SleepSession.kt
│   │   │   │   └── usecase/
│   │   │   └── di/
│   │   │       ├── AppModule.kt
│   │   │       └── NetworkModule.kt
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
│
├── wear/                             # Wear OS 앱
│   ├── src/main/
│   │   ├── java/io/sleepfm/wear/
│   │   │   ├── SleepFMWearApp.kt
│   │   │   ├── presentation/
│   │   │   │   ├── MainActivity.kt
│   │   │   │   └── WearScreens.kt
│   │   │   ├── data/
│   │   │   │   ├── SensorDatabase.kt
│   │   │   │   └── DataSyncManager.kt
│   │   │   └── service/
│   │   │       ├── SensorCollectionService.kt
│   │   │       └── SleepDetectorService.kt
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
│
├── gradle/
│   └── libs.versions.toml
├── build.gradle.kts
└── settings.gradle.kts
```

### B. API 인터페이스
```kotlin
interface SleepFMApi {
    // Auth
    @POST("api/v1/auth/register")
    suspend fun register(@Body request: RegisterRequest): AuthResponse
    
    @POST("api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse
    
    @POST("api/v1/auth/refresh")
    suspend fun refresh(@Body request: RefreshRequest): AuthResponse
    
    // Sessions
    @GET("api/v1/sessions")
    suspend fun getSessions(): List<SleepSession>
    
    @GET("api/v1/sessions/{id}")
    suspend fun getSession(@Path("id") id: Int): SleepSession
    
    @POST("api/v1/sessions")
    suspend fun createSession(@Body request: CreateSessionRequest): SleepSession
    
    // Analysis
    @GET("api/v1/analysis/{sessionId}")
    suspend fun getAnalysis(@Path("sessionId") sessionId: Int): AnalysisResponse
    
    @GET("api/v1/analysis/disease-risk/{sessionId}")
    suspend fun getDiseaseRisk(@Path("sessionId") sessionId: Int): DiseaseRiskResponse
}
```

### C. 변경 이력
| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-01-29 | Phase 4 Sprint Plan 초안 작성 | Development Team |

---

**문서 승인:**
- [ ] 프로젝트 매니저
- [ ] Android Lead

**다음 Sprint Planning 미팅:** Sprint 13 시작 전
