# Sprint 5: iOS App Foundation - Summary

## 개요

Sprint 5에서는 SleepFM iOS 앱의 기반 구조를 구축했습니다. SwiftUI와 MVVM 아키텍처를 사용하여 인증, HealthKit 연동, 주요 화면들을 구현했습니다.

## 완료된 User Stories

### Story 5.1: iOS 프로젝트 초기 설정 (3 SP) ✅
- SwiftUI 앱 진입점 구현 (`SleepFMApp.swift`)
- MVVM 아키텍처 폴더 구조 설정
- Info.plist 및 Entitlements 구성
- HealthKit 권한 설정

### Story 5.2: Figma 디자인 시스템 정의 (5 SP) ✅
- 컬러 팔레트 정의 (Primary, Secondary, Background, Semantic)
- 수면 단계별 색상 정의
- 타이포그래피 시스템 (Rounded font)
- 간격 및 모서리 둥글기 시스템
- 그라디언트 및 그림자 스타일
- 재사용 가능한 View Modifiers

### Story 5.3: iOS 인증 화면 구현 (5 SP) ✅
- 로그인 화면 (`LoginView.swift`)
- 회원가입 화면 (`SignUpView.swift`)
- 비밀번호 강도 검사
- 폼 유효성 검증
- Apple 로그인 버튼 (UI 준비)

### Story 5.4: iOS 네비게이션 구조 (3 SP) ✅
- 온보딩 화면 (3페이지 스와이프)
- TabView 네비게이션 (대시보드, 기록, 설정)
- 상태 기반 라우팅 (`ContentView.swift`)
- 프로필 편집 화면

### Story 5.5: HealthKit 권한 및 데이터 읽기 (5 SP) ✅
- HealthKitManager 구현
- 수면 데이터 읽기
- 심박수 데이터 읽기
- 호흡률 데이터 읽기
- 권한 요청 배너 UI

## 기술 스택

| 구분 | 기술 |
|------|------|
| 플랫폼 | iOS 17.0+ |
| 프레임워크 | SwiftUI |
| 아키텍처 | MVVM |
| 인증 | JWT + Keychain |
| 건강 데이터 | HealthKit |
| 비동기 처리 | Swift Concurrency (async/await) |
| 상태 관리 | @StateObject, @EnvironmentObject |

## 파일 구조

```
ios/SleepFM/SleepFM/
├── SleepFMApp.swift              # 앱 진입점
├── ContentView.swift             # 메인 라우터
├── Info.plist                    # 앱 설정
├── SleepFM.entitlements          # 권한 설정
├── Assets.xcassets/              # 에셋
│
├── Models/
│   ├── User.swift                # 사용자 모델
│   └── SleepSession.swift        # 수면 세션 모델
│
├── ViewModels/
│   ├── AuthManager.swift         # 인증 관리
│   └── HealthKitManager.swift    # HealthKit 관리
│
├── Views/
│   ├── Onboarding/
│   │   └── OnboardingView.swift  # 온보딩
│   ├── Auth/
│   │   ├── LoginView.swift       # 로그인
│   │   └── SignUpView.swift      # 회원가입
│   └── Main/
│       ├── MainTabView.swift     # 탭 네비게이션
│       ├── DashboardView.swift   # 대시보드
│       ├── HistoryView.swift     # 수면 기록
│       └── SettingsView.swift    # 설정
│
├── Services/
│   ├── APIService.swift          # API 클라이언트
│   └── KeychainService.swift     # 토큰 저장
│
└── Utils/
    └── DesignSystem.swift        # 디자인 시스템
```

## 주요 구현 내용

### 1. 인증 시스템
```swift
// AuthManager - 인증 상태 관리
@MainActor
class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var hasCompletedOnboarding = false
    @Published var currentUser: User?
    
    func login(email: String, password: String) async throws
    func signUp(email: String, username: String, password: String, fullName: String?) async throws
    func logout()
    func refreshAuthentication() async throws
}
```

### 2. HealthKit 연동
```swift
// HealthKitManager - 건강 데이터 관리
@MainActor
class HealthKitManager: ObservableObject {
    @Published var isAuthorized = false
    @Published var sleepData: [HKCategorySample] = []
    
    func requestAuthorization() async
    func fetchRecentSleepData() async
    func fetchHeartRateData(from startDate: Date, to endDate: Date) async -> [HKQuantitySample]
    func fetchRespiratoryRateData(from startDate: Date, to endDate: Date) async -> [HKQuantitySample]
}
```

### 3. API 서비스
```swift
// APIService - 백엔드 통신
actor APIService {
    static let shared = APIService()
    
    func signUp(email: String, username: String, password: String, fullName: String?) async throws -> AuthResponse
    func login(email: String, password: String) async throws -> AuthResponse
    func refreshToken(refreshToken: String) async throws -> TokenResponse
    func getCurrentUser() async throws -> User
    func getSessions(userId: Int, limit: Int, offset: Int) async throws -> SessionListResponse
    func requestAnalysis(sessionId: Int) async throws -> IntegratedAnalysisResponse
}
```

### 4. 디자인 시스템
```swift
// 컬러
Color.sleepPrimary      // #4A00E0
Color.sleepSecondary    // #8E2DE2
Color.sleepBackground   // #0F0F23

// 타이포그래피
SleepTypography.largeTitle  // 34pt Bold Rounded
SleepTypography.title1      // 28pt Bold Rounded
SleepTypography.headline    // 17pt Semibold Rounded

// 버튼 스타일
.buttonStyle(PrimaryButtonStyle())
.buttonStyle(SecondaryButtonStyle())

// 카드 스타일
.sleepCard()
.sleepGradientCard()
```

## UI 화면 개요

### 온보딩 (3페이지)
1. 수면 분석 소개 - AI 기반 수면 패턴 분석
2. 건강 위험 예측 - 수면 무호흡, 심장 질환 감지
3. 맞춤형 인사이트 - 개인화된 수면 개선 권장

### 대시보드
- 인사말 (시간대별)
- 수면 점수 카드 (0-100점)
- HealthKit 연결 배너
- 어젯밤 수면 요약
- 빠른 분석 (수면 단계, 무호흡, 건강 위험)
- 최근 인사이트

### 수면 기록
- 기간 선택 (주간/월간/연간)
- 기간 요약 통계
- 세션 목록 (날짜, 점수, 시간)
- 세션 상세 보기 시트

### 설정
- 프로필 섹션
- 연동 (Apple Health, Apple Watch)
- 알림 설정
- 앱 설정 (다크 모드, 언어, 단위)
- 계정 관리 (로그아웃, 삭제)
- 앱 정보

## 다음 스프린트 준비

### Sprint 6: watchOS App (예정)
- watchOS 프로젝트 설정
- 수면 모니터링 컴플리케이션
- 배경 데이터 수집
- iOS-watchOS 연동

## 참고 사항

1. **Xcode 프로젝트 생성 필요**: 소스 코드만 제공되며, Xcode 프로젝트 파일(.xcodeproj)은 Xcode에서 직접 생성해야 합니다.

2. **테스트 계정**: 백엔드 연동 시 테스트 사용자 생성 필요

3. **시뮬레이터 제한**: HealthKit은 실제 기기에서만 완전히 테스트 가능

---

**Sprint 5 완료** | 21 Story Points | iOS 앱 기반 구조 구축 완료
