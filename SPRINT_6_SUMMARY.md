# Sprint 6 완료 보고서: watchOS 센서 수집

## 📋 스프린트 개요

| 항목 | 내용 |
|------|------|
| **스프린트** | Sprint 6 - watchOS 센서 수집 |
| **Phase** | Phase 2 - 데이터 수집 및 동기화 |
| **기간** | 2주 |
| **총 스토리 포인트** | 21 SP |
| **완료 스토리 포인트** | 21 SP |
| **완료율** | 100% |

---

## ✅ 완료된 User Stories

### Story 6.1: watchOS 프로젝트 설정 (3 SP) ✅

**구현 내용:**
- watchOS 앱 타겟 추가 (`SleepFM Watch App`)
- App Entry Point (`SleepFMWatchApp.swift`)
- Info.plist 및 Entitlements 설정
- Assets.xcassets 구성

**주요 파일:**
- `SleepFM Watch App/SleepFMWatchApp.swift`
- `SleepFM Watch App/Info.plist`
- `SleepFM Watch App/SleepFMWatch.entitlements`

---

### Story 6.2: Watch 센서 데이터 수집 (8 SP) ✅

**구현 내용:**
- HealthKit 통합을 통한 센서 데이터 수집
- HKWorkoutSession으로 백그라운드 수집 활성화
- HKAnchoredObjectQuery로 실시간 심박수, 호흡수 모니터링
- 센서 데이터 로컬 저장소 구현

**주요 기능:**
```swift
// 수집하는 센서 데이터
- Heart Rate (심박수)
- Respiratory Rate (호흡수)
- Blood Oxygen (혈중 산소) - 지원 기기
- Sleep Analysis (수면 분석)
- Step Count (걸음 수)
```

**주요 파일:**
- `Services/WatchHealthManager.swift` - HealthKit 통합
- `Services/SensorDataStore.swift` - Actor 기반 데이터 저장
- `Services/SleepMonitor.swift` - 수면 자동 감지

---

### Story 6.3: Watch-iPhone 동기화 (5 SP) ✅

**구현 내용:**
- WatchConnectivity 프레임워크 통합
- 양방향 메시지 통신
- 백그라운드 데이터 전송 (`transferUserInfo`)
- Application Context를 통한 상태 동기화

**Watch → iPhone 데이터:**
```swift
- 센서 데이터 배치
- 수면 시작/종료 이벤트
- 건강 알림
- Watch 상태 (배터리, 모니터링 상태)
```

**iPhone → Watch 명령:**
```swift
- startMonitoring: 모니터링 시작
- stopMonitoring: 모니터링 중지
- requestSensorData: 데이터 요청
- requestStatus: 상태 요청
```

**주요 파일:**
- Watch: `Services/WatchConnectivityManager.swift`
- iPhone: `Services/PhoneConnectivityManager.swift`

---

### Story 6.4: Watch 실시간 알림 (3 SP) ✅

**구현 내용:**
- 건강 이상 감지 알림 시스템
- 알림 타입별 햅틱 피드백
- 중복 알림 방지 (5분 쿨다운)
- 알림 히스토리 관리

**알림 타입:**
| 알림 | 조건 | 햅틱 |
|------|------|------|
| 비정상 심박수 | < 40 또는 > 120 bpm | .notification |
| 비정상 호흡수 | < 8 또는 > 25 /min | .notification |
| 무호흡 가능성 | 호흡 패턴 이상 | .directionUp |
| 수면 시작 | 자동 감지 | .start |
| 수면 종료 | 자동 감지 | .stop |
| 동기화 성공 | 데이터 전송 완료 | .success |
| 동기화 실패 | 전송 오류 | .failure |

**주요 파일:**
- `Services/NotificationService.swift`

---

### Story 6.5: Watch Complication (2 SP) ✅

**구현 내용:**
- CLKComplicationDataSource 구현
- 모든 Complication Family 지원
- 수면 점수 및 심박수 표시
- Timeline 기반 업데이트

**지원 Complication Families:**
```
- Circular Small
- Modular Small / Large
- Utilitarian Small / Small Flat / Large
- Graphic Corner / Circular / Rectangular / Extra Large
```

**주요 파일:**
- `Complications/ComplicationController.swift`

---

## 📁 생성된 파일 구조

```
ios/SleepFM/SleepFM Watch App/
├── SleepFMWatchApp.swift          # App Entry Point
├── ContentView.swift               # Main UI (TabView)
├── Info.plist                      # watchOS 설정
├── SleepFMWatch.entitlements       # Entitlements
├── Assets.xcassets/                # 앱 아이콘, 색상
│   ├── Contents.json
│   ├── AccentColor.colorset/
│   └── AppIcon.appiconset/
├── Services/
│   ├── WatchHealthManager.swift    # HealthKit 통합
│   ├── WatchConnectivityManager.swift  # Watch→iPhone
│   ├── SleepMonitor.swift          # 수면 자동 감지
│   ├── SensorDataStore.swift       # 로컬 데이터 저장
│   └── NotificationService.swift   # 건강 알림
└── Complications/
    └── ComplicationController.swift  # Watchface 위젯

ios/SleepFM/SleepFM/Services/
└── PhoneConnectivityManager.swift  # iPhone→Watch (신규)
```

---

## 🏗️ 아키텍처

### watchOS 앱 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    SleepFMWatchApp                          │
│                    (App Entry Point)                        │
│  ┌─────────────┐ ┌──────────────────┐ ┌─────────────────┐  │
│  │HealthManager│ │ConnectivityMgr   │ │  SleepMonitor   │  │
│  │ @StateObject│ │ @StateObject     │ │  @StateObject   │  │
│  └─────────────┘ └──────────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      ContentView                            │
│  ┌─────────────┐ ┌──────────────────┐ ┌─────────────────┐  │
│  │ DashboardTab│ │  MonitoringTab   │ │   SettingsTab   │  │
│  │  (수면점수)  │ │  (실시간 심박)   │ │   (설정)        │  │
│  └─────────────┘ └──────────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 데이터 흐름

```
┌──────────────┐    HealthKit     ┌──────────────────┐
│  Apple Watch │ ───────────────> │ WatchHealthManager│
│   Sensors    │                  │  (HKWorkoutSession│
└──────────────┘                  │   Background)     │
                                  └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │  SensorDataStore │
                                  │    (Actor)       │
                                  │  Max 30K samples │
                                  └────────┬─────────┘
                                           │
                                           ▼
┌──────────────┐  WatchConnectivity ┌──────────────────┐
│    iPhone    │ <─────────────────│  WatchConnectivity│
│              │    transferUserInfo│    Manager       │
│ PhoneConnect │                    └──────────────────┘
│  ivityManager│ 
└──────────────┘
       │
       ▼
┌──────────────┐
│   Backend    │
│   Server     │
└──────────────┘
```

---

## 🔑 핵심 기술 포인트

### 1. 백그라운드 센서 수집
```swift
// HKWorkoutSession을 통한 지속적 백그라운드 수집
let configuration = HKWorkoutConfiguration()
configuration.activityType = .sleep
configuration.locationType = .indoor

workoutSession = try HKWorkoutSession(
    healthStore: healthStore,
    configuration: configuration
)
```

### 2. 실시간 센서 쿼리
```swift
// HKAnchoredObjectQuery로 실시간 업데이트
let query = HKAnchoredObjectQuery(
    type: heartRateType,
    predicate: predicate,
    anchor: anchor,
    limit: HKObjectQueryNoLimit
) { query, samples, deletedObjects, newAnchor, error in
    // 실시간 처리
}
query.updateHandler = { ... } // 지속적 업데이트
```

### 3. Actor 기반 Thread-Safe 저장소
```swift
actor SensorDataStore {
    private var heartRateSamples: [HeartRateSample] = []
    private let maxSamples = 30_000  // 8시간 @ 1Hz
    
    func addHeartRateSample(...) async { ... }
    func getStatistics() async -> DataStatistics { ... }
}
```

### 4. Watch Connectivity 백그라운드 전송
```swift
// 백그라운드에서도 안정적인 데이터 전송
if session.activationState == .activated {
    session.transferUserInfo(sensorData)  // 큐에 저장됨
}
```

---

## 📊 테스트 계획

### 단위 테스트
- [ ] WatchHealthManager 권한 요청
- [ ] SensorDataStore 데이터 추가/조회
- [ ] NotificationService 알림 생성
- [ ] WatchConnectivityManager 메시지 처리

### 통합 테스트
- [ ] HealthKit → SensorDataStore 데이터 흐름
- [ ] Watch → iPhone 데이터 동기화
- [ ] 수면 자동 감지 정확도

### 기기 테스트
- [ ] Apple Watch Series 5+ 호환성
- [ ] watchOS 10.0 최소 버전 테스트
- [ ] 8시간 연속 모니터링 배터리 테스트

---

## 📝 다음 스프린트 준비사항

### Sprint 7: 수면 분석 UI 예고
1. 수면 대시보드 UI 구현
2. 수면 점수 계산 알고리즘
3. 일간/주간/월간 통계 화면
4. 수면 단계 시각화

---

## 🎓 watchOS 개발 학습 포인트

이번 Sprint에서 학습한 watchOS 핵심 개념:

1. **HKWorkoutSession**
   - 백그라운드 센서 접근의 핵심
   - `workout-processing` 백그라운드 모드 필요

2. **WatchConnectivity**
   - `sendMessage`: 즉시 전송 (Watch가 reachable할 때)
   - `transferUserInfo`: 큐 기반 백그라운드 전송
   - `updateApplicationContext`: 최신 상태 동기화

3. **Extended Runtime Sessions**
   - 앱이 백그라운드로 가도 작업 계속 가능
   - `WKExtendedRuntimeSession` 사용

4. **CLKComplicationDataSource**
   - Timeline 기반 데이터 제공
   - 각 Complication Family별 템플릿 생성

5. **@MainActor**
   - UI 업데이트는 반드시 Main Actor에서
   - `Task { @MainActor in ... }` 패턴

---

## ✨ Sprint 6 완료!

watchOS 앱의 기초 구조가 완성되었습니다. Apple Watch에서 수면 중 센서 데이터를 수집하고, iPhone과 동기화하며, 건강 이상 시 알림을 제공하는 기능이 구현되었습니다.
