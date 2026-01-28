//
//  SettingsViewModel.swift
//  SleepFM
//
//  설정 화면 ViewModel
//

import Foundation
import Combine

/// 설정 뷰모델
@MainActor
final class SettingsViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    /// 사용자 프로필
    @Published var userProfile: UserProfile?
    
    /// 알림 설정
    @Published var notificationSettings = NotificationSettings()
    
    /// Watch 연결 상태
    @Published var watchConnectionStatus: WatchConnectionStatus = .unknown
    
    /// 데이터 동기화 상태
    @Published var syncStatus: SyncStatus = .idle
    
    /// HealthKit 권한 상태
    @Published var healthKitAuthorized = false
    
    /// 앱 버전
    let appVersion: String
    
    /// 빌드 번호
    let buildNumber: String
    
    /// 로딩 상태
    @Published var isLoading = false
    
    /// 에러 메시지
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    
    private let authViewModel: AuthViewModel
    private let connectivityManager: PhoneConnectivityManager
    private let uploader: SleepSessionUploader
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(
        authViewModel: AuthViewModel = .shared,
        connectivityManager: PhoneConnectivityManager = .shared,
        uploader: SleepSessionUploader = .shared
    ) {
        self.authViewModel = authViewModel
        self.connectivityManager = connectivityManager
        self.uploader = uploader
        
        // 앱 버전 정보
        self.appVersion = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0"
        self.buildNumber = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"
        
        setupBindings()
        loadSettings()
    }
    
    // MARK: - Setup
    
    private func setupBindings() {
        // Watch 연결 상태 바인딩
        connectivityManager.$isWatchConnected
            .combineLatest(connectivityManager.$isWatchAppInstalled)
            .map { isConnected, isInstalled -> WatchConnectionStatus in
                if !isInstalled {
                    return .notInstalled
                } else if isConnected {
                    return .connected
                } else {
                    return .disconnected
                }
            }
            .assign(to: &$watchConnectionStatus)
        
        // 동기화 상태 바인딩
        uploader.$uploadStatus
            .map { status -> SyncStatus in
                switch status {
                case .idle: return .idle
                case .preparing, .uploading: return .syncing
                case .completed: return .synced
                case .failed(let error): return .failed(error)
                }
            }
            .assign(to: &$syncStatus)
        
        // 인증 상태에서 사용자 정보 가져오기
        authViewModel.$currentUser
            .compactMap { $0 }
            .map { user -> UserProfile in
                UserProfile(
                    id: user.id,
                    email: user.email,
                    username: user.username,
                    fullName: user.fullName,
                    profileImageURL: user.profileImage.flatMap { URL(string: $0) },
                    memberSince: user.createdAt
                )
            }
            .assign(to: &$userProfile)
    }
    
    // MARK: - Public Methods
    
    /// 설정 로드
    func loadSettings() {
        // UserDefaults에서 알림 설정 로드
        if let data = UserDefaults.standard.data(forKey: "notificationSettings"),
           let settings = try? JSONDecoder().decode(NotificationSettings.self, from: data) {
            notificationSettings = settings
        }
        
        // HealthKit 권한 확인
        checkHealthKitAuthorization()
    }
    
    /// 알림 설정 저장
    func saveNotificationSettings() {
        if let data = try? JSONEncoder().encode(notificationSettings) {
            UserDefaults.standard.set(data, forKey: "notificationSettings")
        }
        
        // 시스템 알림 등록/해제
        updateSystemNotifications()
    }
    
    /// Watch 앱 설정 열기
    func openWatchApp() {
        guard let url = URL(string: "itms-watchs://") else { return }
        // Note: 실제로는 WatchConnectivity를 통해 Watch 앱 열기 요청
    }
    
    /// HealthKit 권한 요청
    func requestHealthKitAuthorization() async {
        // TODO: HealthKit 권한 요청 구현
        healthKitAuthorized = true
    }
    
    /// 수동 동기화
    func syncData() async {
        isLoading = true
        
        do {
            try await uploader.createAndUploadSession()
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    /// 로그아웃
    func logout() {
        authViewModel.logout()
    }
    
    /// 캐시 삭제
    func clearCache() {
        // URL 캐시 삭제
        URLCache.shared.removeAllCachedResponses()
        
        // 임시 파일 삭제
        let tempDir = FileManager.default.temporaryDirectory
        try? FileManager.default.removeItem(at: tempDir)
        
        errorMessage = nil
    }
    
    /// 계정 삭제 요청
    func requestAccountDeletion() async -> Bool {
        isLoading = true
        
        // TODO: API를 통한 계정 삭제 요청
        // let success = try await apiService.deleteAccount()
        
        isLoading = false
        return true
    }
    
    // MARK: - Private Methods
    
    private func checkHealthKitAuthorization() {
        // TODO: HealthKit 권한 상태 확인
        healthKitAuthorized = true
    }
    
    private func updateSystemNotifications() {
        // 알림 설정에 따라 시스템 알림 업데이트
        if notificationSettings.bedtimeReminder {
            scheduleBedtimeReminder()
        } else {
            cancelBedtimeReminder()
        }
        
        if notificationSettings.morningReport {
            scheduleMorningReport()
        } else {
            cancelMorningReport()
        }
    }
    
    private func scheduleBedtimeReminder() {
        // TODO: 취침 알림 스케줄링
    }
    
    private func cancelBedtimeReminder() {
        // TODO: 취침 알림 취소
    }
    
    private func scheduleMorningReport() {
        // TODO: 아침 리포트 스케줄링
    }
    
    private func cancelMorningReport() {
        // TODO: 아침 리포트 취소
    }
}

// MARK: - Supporting Types

/// 사용자 프로필
struct UserProfile: Identifiable {
    let id: Int
    let email: String
    let username: String
    let fullName: String?
    let profileImageURL: URL?
    let memberSince: String
    
    var displayName: String {
        fullName ?? username
    }
    
    var formattedMemberSince: String {
        // ISO8601 날짜 포맷팅
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: memberSince) {
            let displayFormatter = DateFormatter()
            displayFormatter.locale = Locale(identifier: "ko_KR")
            displayFormatter.dateFormat = "yyyy년 M월 d일"
            return displayFormatter.string(from: date)
        }
        return memberSince
    }
}

/// 알림 설정
struct NotificationSettings: Codable {
    var pushEnabled = true
    var bedtimeReminder = true
    var bedtimeReminderTime = Date() // 기본: 오후 10시
    var morningReport = true
    var morningReportTime = Date() // 기본: 오전 7시
    var healthAlerts = true
    var weeklyReport = true
}

/// Watch 연결 상태
enum WatchConnectionStatus {
    case unknown
    case connected
    case disconnected
    case notInstalled
    
    var displayText: String {
        switch self {
        case .unknown: return "확인 중..."
        case .connected: return "연결됨"
        case .disconnected: return "연결 끊김"
        case .notInstalled: return "앱 미설치"
        }
    }
    
    var iconName: String {
        switch self {
        case .unknown: return "applewatch"
        case .connected: return "applewatch.radiowaves.left.and.right"
        case .disconnected: return "applewatch.slash"
        case .notInstalled: return "applewatch"
        }
    }
    
    var statusColor: String {
        switch self {
        case .unknown: return "gray"
        case .connected: return "green"
        case .disconnected: return "orange"
        case .notInstalled: return "red"
        }
    }
}

/// 동기화 상태
enum SyncStatus: Equatable {
    case idle
    case syncing
    case synced
    case failed(String)
    
    var displayText: String {
        switch self {
        case .idle: return "동기화 대기"
        case .syncing: return "동기화 중..."
        case .synced: return "동기화 완료"
        case .failed(let error): return "실패: \(error)"
        }
    }
}
