# SleepFM iOS App

SwiftUI 기반 iOS 네이티브 앱

## 요구 사항

- iOS 17.0+
- Xcode 15.0+
- Swift 5.9+

## 프로젝트 구조

```
SleepFM/
├── SleepFMApp.swift          # 앱 진입점
├── ContentView.swift         # 메인 콘텐츠 뷰
├── Info.plist               # 앱 설정
├── SleepFM.entitlements     # 권한 설정
├── Assets.xcassets/         # 앱 에셋
├── Models/                   # 데이터 모델
│   ├── User.swift
│   └── SleepSession.swift
├── ViewModels/               # 비즈니스 로직
│   ├── AuthManager.swift
│   └── HealthKitManager.swift
├── Views/                    # UI 뷰
│   ├── Onboarding/
│   │   └── OnboardingView.swift
│   ├── Auth/
│   │   ├── LoginView.swift
│   │   └── SignUpView.swift
│   └── Main/
│       ├── MainTabView.swift
│       ├── DashboardView.swift
│       ├── HistoryView.swift
│       └── SettingsView.swift
├── Services/                 # 서비스 레이어
│   ├── APIService.swift
│   └── KeychainService.swift
└── Utils/                    # 유틸리티
    └── DesignSystem.swift
```

## 주요 기능

### 1. 인증
- 이메일/비밀번호 로그인
- 회원가입
- JWT 토큰 관리 (Keychain 저장)
- 자동 토큰 갱신

### 2. HealthKit 연동
- 수면 데이터 읽기
- 심박수 데이터 읽기
- 호흡률 데이터 읽기
- 백그라운드 업데이트

### 3. 대시보드
- 수면 점수 표시
- 어젯밤 수면 요약
- 빠른 분석 액세스
- 최근 인사이트

### 4. 수면 기록
- 기간별 조회 (주간/월간/연간)
- 기간 요약 통계
- 세션 상세 보기

### 5. 설정
- 프로필 편집
- Apple Health 연동
- 알림 설정
- 앱 설정 (다크 모드, 언어, 단위)
- 계정 관리

## 디자인 시스템

### 컬러
- Primary: `#4A00E0` (Deep Indigo)
- Secondary: `#8E2DE2` (Soft Purple)
- Background: `#0F0F23` (Dark)
- Card: `#1A1A2E`
- Success: `#00D26A`
- Warning: `#FFB800`
- Danger: `#FF4757`

### 수면 단계 색상
- Wake: `#FF6B6B`
- N1: `#FFA06B`
- N2: `#FFE66B`
- N3: `#4ECDC4`
- REM: `#A06BFF`

### 타이포그래피
- Rounded 디자인 시스템
- Large Title: 34pt Bold
- Title 1: 28pt Bold
- Title 2: 22pt Bold
- Headline: 17pt Semibold
- Body: 17pt Regular

## Xcode 프로젝트 생성

1. Xcode 열기
2. File > New > Project 선택
3. iOS > App 선택
4. 설정:
   - Product Name: SleepFM
   - Team: (개발자 팀 선택)
   - Organization Identifier: com.sleepfm
   - Bundle Identifier: com.sleepfm.app
   - Interface: SwiftUI
   - Language: Swift
5. 생성 후 기존 파일 삭제하고 이 폴더의 파일들로 교체
6. Signing & Capabilities에서 HealthKit 추가

## 빌드 및 실행

```bash
# 시뮬레이터에서 실행
xcodebuild -scheme SleepFM -destination 'platform=iOS Simulator,name=iPhone 15 Pro'

# 디바이스에서 실행
xcodebuild -scheme SleepFM -destination 'platform=iOS,name=My iPhone'
```

## API 엔드포인트 설정

`Services/APIService.swift`에서 baseURL 수정:

```swift
#if DEBUG
self.baseURL = "http://localhost:8000/api/v1"
#else
self.baseURL = "https://api.sleepfm.com/api/v1"
#endif
```

## 테스트

```bash
xcodebuild test -scheme SleepFM -destination 'platform=iOS Simulator,name=iPhone 15 Pro'
```

## 라이선스

MIT License
