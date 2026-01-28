//
//  SleepMonitor.swift
//  SleepFM Watch App
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation
import WatchKit
import Combine

/// 수면 모니터링 서비스
///
/// 자동 수면 감지 및 센서 데이터 수집을 관리합니다.
///
/// 주요 기능:
/// - 수면 상태 자동 감지
/// - 센서 데이터 수집 시작/중지
/// - 백그라운드 모니터링 유지
/// - 데이터 동기화 트리거
@MainActor
class SleepMonitor: ObservableObject {
    // MARK: - Published Properties
    
    @Published var isMonitoring = false
    @Published var monitoringStartTime = Date()
    @Published var collectedSamplesCount = 0
    @Published var currentSleepPhase: SleepPhase = .unknown
    
    // MARK: - Private Properties
    
    private var healthManager: WatchHealthManager?
    private var connectivityManager: WatchConnectivityManager?
    private var checkTimer: Timer?
    private var currentSessionId: String?
    private var cancellables = Set<AnyCancellable>()
    
    // 설정
    private let autoMonitorEnabled: Bool = true
    private let sleepCheckInterval: TimeInterval = 300 // 5분마다 수면 상태 확인
    
    // MARK: - Initialization
    
    init() {
        setupNotifications()
    }
    
    // MARK: - Setup
    
    /// HealthManager 및 ConnectivityManager 설정
    func configure(
        healthManager: WatchHealthManager,
        connectivityManager: WatchConnectivityManager
    ) {
        self.healthManager = healthManager
        self.connectivityManager = connectivityManager
    }
    
    /// 알림 수신 설정
    private func setupNotifications() {
        NotificationCenter.default.publisher(for: .startSleepMonitoring)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.startMonitoring()
            }
            .store(in: &cancellables)
        
        NotificationCenter.default.publisher(for: .stopSleepMonitoring)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.stopMonitoring()
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Auto Detection
    
    /// 자동 수면 감지 시작
    func startAutoDetection() {
        guard autoMonitorEnabled else { return }
        
        // 5분마다 수면 상태 확인
        checkTimer = Timer.scheduledTimer(withTimeInterval: sleepCheckInterval, repeats: true) { [weak self] _ in
            Task {
                await self?.checkAndStartIfSleeping()
            }
        }
        
        print("Auto sleep detection started")
    }
    
    /// 자동 수면 감지 중지
    func stopAutoDetection() {
        checkTimer?.invalidate()
        checkTimer = nil
        print("Auto sleep detection stopped")
    }
    
    /// 수면 중인지 확인하고 모니터링 시작
    private func checkAndStartIfSleeping() async {
        guard !isMonitoring, let healthManager = healthManager else { return }
        
        let isSleeping = await healthManager.checkSleepStatus()
        
        if isSleeping {
            await MainActor.run {
                startMonitoring()
            }
        }
    }
    
    // MARK: - Monitoring Control
    
    /// 수면 모니터링 시작
    func startMonitoring() {
        guard !isMonitoring else { return }
        
        isMonitoring = true
        monitoringStartTime = Date()
        collectedSamplesCount = 0
        currentSessionId = UUID().uuidString
        currentSleepPhase = .unknown
        
        // HealthKit 워크아웃 세션 시작
        Task {
            do {
                try await healthManager?.startWorkoutSession()
                print("Sleep monitoring started")
                
                // 햅틱 피드백
                WKInterfaceDevice.current().play(.start)
                
            } catch {
                print("Failed to start monitoring: \(error)")
                isMonitoring = false
            }
        }
        
        // 데이터 수집 구독 시작
        startDataCollection()
    }
    
    /// 수면 모니터링 중지
    func stopMonitoring() {
        guard isMonitoring else { return }
        
        isMonitoring = false
        
        // HealthKit 워크아웃 세션 종료
        Task {
            await healthManager?.stopWorkoutSession()
            print("Sleep monitoring stopped")
            
            // 햅틱 피드백
            WKInterfaceDevice.current().play(.stop)
            
            // 데이터 동기화
            await syncCollectedData()
        }
        
        stopDataCollection()
    }
    
    /// 백그라운드 모니터링 계속
    func continueBackgroundMonitoring() {
        if isMonitoring {
            print("Continuing monitoring in background")
            // 백그라운드에서도 워크아웃 세션이 계속 실행됨
        }
    }
    
    // MARK: - Data Collection
    
    /// 데이터 수집 시작
    private func startDataCollection() {
        // 데이터 저장소 리셋
        SensorDataStore.shared.reset()
        
        // 데이터 수집 타이머 (1초마다 샘플 카운트 업데이트)
        Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                self?.collectedSamplesCount = SensorDataStore.shared.totalSampleCount
            }
            .store(in: &cancellables)
        
        print("Data collection started")
    }
    
    /// 데이터 수집 중지
    private func stopDataCollection() {
        cancellables.removeAll()
        print("Data collection stopped")
    }
    
    /// 수집된 데이터 동기화
    private func syncCollectedData() async {
        guard let sessionId = currentSessionId,
              let connectivityManager = connectivityManager else {
            return
        }
        
        let data = SensorDataStore.shared.getDataPackage(
            sessionId: sessionId,
            startTime: monitoringStartTime,
            endTime: Date()
        )
        
        connectivityManager.sendSensorData(data)
        print("Data sync initiated. Samples: \(collectedSamplesCount)")
        
        // 로컬 데이터 정리
        SensorDataStore.shared.reset()
    }
    
    // MARK: - Sleep Phase Detection
    
    /// 수면 단계 업데이트 (심박수, 움직임 기반 간단한 추정)
    func updateSleepPhase(heartRate: Double, movement: Double) {
        let previousPhase = currentSleepPhase
        
        // 간단한 수면 단계 추정 로직
        // 실제로는 더 복잡한 알고리즘 필요
        if movement > 0.5 {
            currentSleepPhase = .wake
        } else if heartRate < 55 && movement < 0.1 {
            currentSleepPhase = .deep
        } else if heartRate > 70 && movement < 0.2 {
            currentSleepPhase = .rem
        } else {
            currentSleepPhase = .light
        }
        
        // 단계 변경 시 로깅
        if currentSleepPhase != previousPhase {
            print("Sleep phase changed: \(previousPhase) -> \(currentSleepPhase)")
        }
    }
}

// MARK: - Sleep Phase

enum SleepPhase: String {
    case wake = "Wake"
    case light = "Light"
    case deep = "Deep"
    case rem = "REM"
    case unknown = "Unknown"
    
    var color: String {
        switch self {
        case .wake: return "red"
        case .light: return "yellow"
        case .deep: return "teal"
        case .rem: return "purple"
        case .unknown: return "gray"
        }
    }
}

// MARK: - Extended Runtime Session

extension SleepMonitor {
    /// 확장된 런타임 세션 시작 (백그라운드 작업용)
    func startExtendedRuntimeSession() {
        let session = WKExtendedRuntimeSession()
        session.delegate = WKExtendedRuntimeDelegate()
        session.start()
    }
}

/// 확장 런타임 델리게이트
class WKExtendedRuntimeDelegate: NSObject, WKExtendedRuntimeSessionDelegate {
    func extendedRuntimeSession(
        _ extendedRuntimeSession: WKExtendedRuntimeSession,
        didInvalidateWith reason: WKExtendedRuntimeSessionInvalidationReason,
        error: Error?
    ) {
        print("Extended runtime session invalidated: \(reason)")
    }
    
    func extendedRuntimeSessionDidStart(
        _ extendedRuntimeSession: WKExtendedRuntimeSession
    ) {
        print("Extended runtime session started")
    }
    
    func extendedRuntimeSessionWillExpire(
        _ extendedRuntimeSession: WKExtendedRuntimeSession
    ) {
        print("Extended runtime session will expire")
    }
}
