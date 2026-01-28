# Sprint 8 Summary: API 통합 및 데이터 동기화

## Sprint 정보
- **Sprint 번호**: 8
- **Sprint 목표**: iOS 앱과 Backend API 연동, Watch 데이터 서버 업로드
- **기간**: 2026년 1월 27일
- **상태**: ✅ 완료

---

## 구현된 기능

### 1. SleepSessionUploader 서비스
**파일**: `Services/SleepSessionUploader.swift`

Watch에서 수신한 센서 데이터를 서버로 업로드하는 서비스:

```swift
@MainActor
final class SleepSessionUploader: ObservableObject {
    @Published private(set) var uploadProgress: Double = 0
    @Published private(set) var uploadStatus: UploadStatus = .idle
    @Published private(set) var lastUploadDate: Date?
    @Published private(set) var pendingSessionCount: Int = 0
    
    func createAndUploadSession() async throws
    func uploadSession(_ session: PendingSleepSession) async throws
    func uploadAllPendingSessions() async
}
```

**주요 기능**:
- Watch 수면 종료 시 자동 업로드
- 청크 단위 센서 데이터 업로드 (500개씩)
- 업로드 진행률 표시
- 실패 시 대기열에 저장 후 재시도
- UserDefaults를 통한 대기 세션 영속화

### 2. AuthViewModel (인증 상태 관리)
**파일**: `ViewModels/AuthViewModel.swift`

전역 인증 상태 관리:

```swift
@MainActor
final class AuthViewModel: ObservableObject {
    static let shared = AuthViewModel()
    
    @Published private(set) var currentUser: User?
    @Published private(set) var isLoggedIn = false
    
    func signUp(email:username:password:fullName:) async -> Bool
    func login(email:password:) async -> Bool
    func logout()
    func refreshTokenIfNeeded() async -> Bool
    func checkAuthStatus() async
}
```

**주요 기능**:
- 앱 시작 시 자동 로그인 확인
- 토큰 만료 시 자동 갱신
- Watch에 로그인 상태 동기화
- Keychain 토큰 관리

### 3. SettingsViewModel
**파일**: `ViewModels/SettingsViewModel.swift`

설정 화면 데이터 관리:

```swift
@MainActor
final class SettingsViewModel: ObservableObject {
    @Published var userProfile: UserProfile?
    @Published var notificationSettings = NotificationSettings()
    @Published var watchConnectionStatus: WatchConnectionStatus = .unknown
    @Published var syncStatus: SyncStatus = .idle
    @Published var healthKitAuthorized = false
}
```

**주요 기능**:
- 사용자 프로필 표시
- 알림 설정 관리 (취침 알림, 아침 리포트)
- Watch 연결 상태 모니터링
- 수동 동기화 기능
- 캐시 삭제

### 4. DashboardViewModel API 연동
**파일**: `ViewModels/DashboardViewModel.swift`

API 연동 업데이트:

```swift
private func loadLastSession() async throws {
    // 실제 API 호출 시도
    let response = try await apiService.getSessions(userId: userId, limit: 1)
    let results = try await apiService.getSessionResults(sessionId: latestSession.id)
    updateFromSessionResults(results)
}

private func loadDiseaseRisks() async throws {
    let riskResponse = try await apiService.analyzeDiseaseRisk(sessionId: sessionId)
    diseaseRisks = riskResponse.predictions.map { ... }
}
```

**변경 사항**:
- 실제 API 호출 구현
- API 실패 시 더미 데이터 폴백
- 분석 결과에서 데이터 추출
- 수면 점수 계산 로직

### 5. RiskCategory 확장
**파일**: `Views/Components/Charts/DiseaseRiskChart.swift`

API 응답 문자열에서 초기화하는 생성자 추가:

```swift
enum RiskCategory: String, Codable {
    init(from string: String) {
        switch string.lowercased() {
        case "low", "낮음": self = .low
        case "moderate", "보통": self = .moderate
        case "high", "높음": self = .high
        case "very high", "veryhigh", "매우 높음": self = .veryHigh
        default: self = RiskCategory.fromScore(0)
        }
    }
}
```

### 6. DiseasePrediction 확장
**파일**: `Models/SleepSession.swift`

score 별칭 속성 추가:

```swift
struct DiseasePrediction: Codable, Identifiable {
    let riskScore: Double
    
    /// score 별칭 (riskScore와 동일)
    var score: Double { riskScore }
}
```

---

## 데이터 흐름

### Watch → iPhone → Server 흐름

```
┌─────────────┐     WatchConnectivity     ┌──────────────────────┐
│ Apple Watch │ ─────────────────────────▶│ PhoneConnectivity    │
│ Sensors     │                           │ Manager              │
└─────────────┘                           └──────────┬───────────┘
                                                     │
                                                     ▼
                                          ┌──────────────────────┐
                                          │ SleepSessionUploader │
                                          └──────────┬───────────┘
                                                     │
                                          ┌──────────▼───────────┐
                                          │ APIService           │
                                          │ - Create Session     │
                                          │ - Upload Sensor Data │
                                          │ - Request Analysis   │
                                          └──────────┬───────────┘
                                                     │
                                          ┌──────────▼───────────┐
                                          │ Backend Server       │
                                          │ (FastAPI)            │
                                          └──────────────────────┘
```

### API 연동 흐름

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Dashboard   │ ──▶ │ Dashboard   │ ──▶ │ APIService  │
│ View        │     │ ViewModel   │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                          ┌────────────────────┼────────────────────┐
                          ▼                    ▼                    ▼
                    ┌───────────┐        ┌───────────┐        ┌───────────┐
                    │ Sessions  │        │ Results   │        │ Disease   │
                    │ API       │        │ API       │        │ Risk API  │
                    └───────────┘        └───────────┘        └───────────┘
```

---

## 지원 타입

### UploadStatus
```swift
enum UploadStatus: Equatable {
    case idle
    case preparing
    case uploading
    case completed
    case failed(String)
}
```

### WatchConnectionStatus
```swift
enum WatchConnectionStatus {
    case unknown
    case connected
    case disconnected
    case notInstalled
}
```

### SyncStatus
```swift
enum SyncStatus: Equatable {
    case idle
    case syncing
    case synced
    case failed(String)
}
```

### PendingSleepSession
```swift
struct PendingSleepSession: Codable, Identifiable {
    let id: UUID
    let startTime: Date
    let endTime: Date
    let sensorData: [SensorDataItem]
}
```

---

## 파일 구조

```
ios/SleepFM/SleepFM/
├── Services/
│   ├── APIService.swift          (기존)
│   ├── KeychainService.swift     (기존)
│   ├── PhoneConnectivityManager.swift (기존)
│   └── SleepSessionUploader.swift    ← NEW
├── ViewModels/
│   ├── AuthViewModel.swift           ← NEW
│   ├── DashboardViewModel.swift      (업데이트)
│   ├── SettingsViewModel.swift       ← NEW
│   └── ...
├── Models/
│   └── SleepSession.swift            (업데이트)
└── Views/
    └── Components/
        └── Charts/
            └── DiseaseRiskChart.swift (업데이트)
```

---

## API 연동 상태

| API 엔드포인트 | 상태 | 설명 |
|---------------|------|------|
| `/auth/login` | ✅ | 로그인 |
| `/auth/register` | ✅ | 회원가입 |
| `/auth/refresh` | ✅ | 토큰 갱신 |
| `/auth/me` | ✅ | 현재 사용자 |
| `/users/{id}/sessions` | ✅ | 세션 목록 |
| `/sessions/{id}/results` | ✅ | 세션 결과 |
| `/analyze` | ✅ | 통합 분석 |
| `/analyze/disease-risk` | ✅ | 질병 위험 분석 |

---

## 다음 단계

### Sprint 9: 통합 테스트 및 최적화
- E2E 테스트 자동화
- 에러 처리 강화
- 오프라인 모드 지원
- 배터리 최적화

### 향후 개선 사항
- Retry 정책 강화 (지수 백오프)
- 네트워크 상태 모니터링
- 백그라운드 업로드 최적화
- 캐싱 전략

---

## 관련 문서
- [SPRINT_PLAN_PHASE2.md](docs/SPRINT_PLAN_PHASE2.md)
- [SPRINT_7_SUMMARY.md](SPRINT_7_SUMMARY.md)
- [Backend API Documentation](backend/README.md)
