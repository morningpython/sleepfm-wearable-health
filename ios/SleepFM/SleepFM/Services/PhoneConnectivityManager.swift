//
//  PhoneConnectivityManager.swift
//  SleepFM
//
//  iPhone 측 WatchConnectivity 관리자
//  Apple Watch에서 전송된 센서 데이터를 수신하고 처리합니다.
//

import Foundation
import WatchConnectivity
import Combine

/// iPhone에서 Watch 데이터를 수신하는 매니저
@MainActor
final class PhoneConnectivityManager: NSObject, ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = PhoneConnectivityManager()
    
    // MARK: - Published Properties
    
    /// Watch 연결 상태
    @Published private(set) var isWatchConnected = false
    
    /// Watch 앱 설치 여부
    @Published private(set) var isWatchAppInstalled = false
    
    /// 마지막 동기화 시간
    @Published private(set) var lastSyncDate: Date?
    
    /// Watch에서 받은 수면 점수
    @Published private(set) var watchSleepScore: Int?
    
    /// Watch 배터리 레벨
    @Published private(set) var watchBatteryLevel: Double?
    
    /// Watch 모니터링 상태
    @Published private(set) var isWatchMonitoring = false
    
    /// 수신된 센서 데이터 개수
    @Published private(set) var receivedDataCount = 0
    
    // MARK: - Private Properties
    
    private var session: WCSession?
    private var pendingSensorData: [SensorDataPacket] = []
    private let maxPendingData = 1000
    
    // MARK: - Initialization
    
    private override init() {
        super.init()
        setupWatchConnectivity()
    }
    
    // MARK: - Setup
    
    private func setupWatchConnectivity() {
        guard WCSession.isSupported() else {
            print("📱 WatchConnectivity not supported on this device")
            return
        }
        
        session = WCSession.default
        session?.delegate = self
        session?.activate()
        print("📱 WatchConnectivity session activating...")
    }
    
    // MARK: - Public Methods
    
    /// Watch에 모니터링 시작 명령 전송
    func requestWatchStartMonitoring() {
        sendCommand("startMonitoring")
    }
    
    /// Watch에 모니터링 중지 명령 전송
    func requestWatchStopMonitoring() {
        sendCommand("stopMonitoring")
    }
    
    /// Watch에 센서 데이터 요청
    func requestSensorData() {
        sendCommand("requestSensorData")
    }
    
    /// Watch 상태 업데이트 요청
    func requestWatchStatus() {
        sendCommand("requestStatus")
    }
    
    /// iPhone 상태를 Watch로 전송
    func updatePhoneStatus(isLoggedIn: Bool, userName: String?) {
        guard let session = session, session.isReachable else { return }
        
        let context: [String: Any] = [
            "isLoggedIn": isLoggedIn,
            "userName": userName ?? "",
            "timestamp": Date().timeIntervalSince1970
        ]
        
        do {
            try session.updateApplicationContext(context)
            print("📱 Updated application context for Watch")
        } catch {
            print("📱 Failed to update application context: \(error)")
        }
    }
    
    /// 대기 중인 센서 데이터 가져오기 및 클리어
    func fetchPendingSensorData() -> [SensorDataPacket] {
        let data = pendingSensorData
        pendingSensorData.removeAll()
        receivedDataCount = 0
        return data
    }
    
    // MARK: - Private Methods
    
    private func sendCommand(_ command: String, data: [String: Any]? = nil) {
        guard let session = session else {
            print("📱 WCSession not available")
            return
        }
        
        guard session.activationState == .activated else {
            print("📱 WCSession not activated")
            return
        }
        
        var message: [String: Any] = ["command": command]
        if let data = data {
            message.merge(data) { _, new in new }
        }
        
        if session.isReachable {
            session.sendMessage(message, replyHandler: { reply in
                print("📱 Watch replied: \(reply)")
            }, errorHandler: { error in
                print("📱 Failed to send message: \(error)")
            })
        } else {
            // Watch가 reachable하지 않으면 userInfo로 전송
            session.transferUserInfo(message)
            print("📱 Message queued for delivery: \(command)")
        }
    }
    
    private func processSensorData(_ data: [String: Any]) {
        guard let type = data["type"] as? String,
              let timestamp = data["timestamp"] as? TimeInterval,
              let value = data["value"] as? Double else {
            return
        }
        
        let packet = SensorDataPacket(
            type: SensorType(rawValue: type) ?? .heartRate,
            timestamp: Date(timeIntervalSince1970: timestamp),
            value: value,
            metadata: data["metadata"] as? [String: Any]
        )
        
        pendingSensorData.append(packet)
        
        // 최대 개수 초과 시 오래된 데이터 삭제
        if pendingSensorData.count > maxPendingData {
            pendingSensorData.removeFirst(pendingSensorData.count - maxPendingData)
        }
        
        receivedDataCount = pendingSensorData.count
    }
    
    private func processBatchSensorData(_ samples: [[String: Any]]) {
        for sample in samples {
            processSensorData(sample)
        }
        print("📱 Processed \(samples.count) sensor samples from Watch")
    }
    
    private func updateWatchStatus(_ info: [String: Any]) {
        if let sleepScore = info["sleepScore"] as? Int {
            watchSleepScore = sleepScore
        }
        if let batteryLevel = info["batteryLevel"] as? Double {
            watchBatteryLevel = batteryLevel
        }
        if let isMonitoring = info["isMonitoring"] as? Bool {
            isWatchMonitoring = isMonitoring
        }
        if let timestamp = info["timestamp"] as? TimeInterval {
            lastSyncDate = Date(timeIntervalSince1970: timestamp)
        }
    }
}

// MARK: - WCSessionDelegate

extension PhoneConnectivityManager: WCSessionDelegate {
    
    nonisolated func session(
        _ session: WCSession,
        activationDidCompleteWith activationState: WCSessionActivationState,
        error: Error?
    ) {
        Task { @MainActor in
            if let error = error {
                print("📱 WCSession activation failed: \(error)")
                return
            }
            
            print("📱 WCSession activated: \(activationState.rawValue)")
            isWatchConnected = session.isPaired
            isWatchAppInstalled = session.isWatchAppInstalled
        }
    }
    
    nonisolated func sessionDidBecomeInactive(_ session: WCSession) {
        print("📱 WCSession became inactive")
    }
    
    nonisolated func sessionDidDeactivate(_ session: WCSession) {
        print("📱 WCSession deactivated, reactivating...")
        session.activate()
    }
    
    nonisolated func sessionReachabilityDidChange(_ session: WCSession) {
        Task { @MainActor in
            isWatchConnected = session.isReachable
            print("📱 Watch reachability changed: \(session.isReachable)")
        }
    }
    
    nonisolated func sessionWatchStateDidChange(_ session: WCSession) {
        Task { @MainActor in
            isWatchConnected = session.isPaired
            isWatchAppInstalled = session.isWatchAppInstalled
            print("📱 Watch state changed - Paired: \(session.isPaired), App installed: \(session.isWatchAppInstalled)")
        }
    }
    
    // MARK: - Message Receiving
    
    nonisolated func session(
        _ session: WCSession,
        didReceiveMessage message: [String: Any]
    ) {
        Task { @MainActor in
            handleIncomingMessage(message)
        }
    }
    
    nonisolated func session(
        _ session: WCSession,
        didReceiveMessage message: [String: Any],
        replyHandler: @escaping ([String: Any]) -> Void
    ) {
        Task { @MainActor in
            handleIncomingMessage(message)
            replyHandler(["status": "received", "timestamp": Date().timeIntervalSince1970])
        }
    }
    
    nonisolated func session(
        _ session: WCSession,
        didReceiveUserInfo userInfo: [String: Any] = [:]
    ) {
        Task { @MainActor in
            handleIncomingMessage(userInfo)
        }
    }
    
    nonisolated func session(
        _ session: WCSession,
        didReceiveApplicationContext applicationContext: [String: Any]
    ) {
        Task { @MainActor in
            updateWatchStatus(applicationContext)
        }
    }
    
    // MARK: - Message Handling
    
    @MainActor
    private func handleIncomingMessage(_ message: [String: Any]) {
        print("📱 Received message from Watch: \(message.keys)")
        
        // 센서 데이터 배치 처리
        if let sensorData = message["sensorData"] as? [[String: Any]] {
            processBatchSensorData(sensorData)
            lastSyncDate = Date()
        }
        
        // 단일 센서 데이터
        if let type = message["type"] as? String {
            processSensorData(message)
        }
        
        // 상태 업데이트
        if let status = message["status"] as? [String: Any] {
            updateWatchStatus(status)
        }
        
        // 특정 이벤트 처리
        if let event = message["event"] as? String {
            handleWatchEvent(event, data: message)
        }
    }
    
    private func handleWatchEvent(_ event: String, data: [String: Any]) {
        switch event {
        case "sleepStarted":
            print("📱 Sleep monitoring started on Watch")
            isWatchMonitoring = true
            NotificationCenter.default.post(name: .watchSleepStarted, object: nil)
            
        case "sleepEnded":
            print("📱 Sleep monitoring ended on Watch")
            isWatchMonitoring = false
            NotificationCenter.default.post(name: .watchSleepEnded, object: nil)
            
        case "syncCompleted":
            lastSyncDate = Date()
            print("📱 Sync completed at \(lastSyncDate!)")
            
        case "healthAlert":
            if let alertType = data["alertType"] as? String,
               let alertMessage = data["message"] as? String {
                NotificationCenter.default.post(
                    name: .watchHealthAlert,
                    object: nil,
                    userInfo: ["type": alertType, "message": alertMessage]
                )
            }
            
        default:
            print("📱 Unknown watch event: \(event)")
        }
    }
}

// MARK: - Supporting Types

/// 센서 데이터 타입
enum SensorType: String {
    case heartRate = "heartRate"
    case respiratoryRate = "respiratoryRate"
    case bloodOxygen = "bloodOxygen"
    case accelerometer = "accelerometer"
    case sleepPhase = "sleepPhase"
}

/// 센서 데이터 패킷
struct SensorDataPacket: Identifiable {
    let id = UUID()
    let type: SensorType
    let timestamp: Date
    let value: Double
    let metadata: [String: Any]?
}

// MARK: - Notification Names

extension Notification.Name {
    static let watchSleepStarted = Notification.Name("watchSleepStarted")
    static let watchSleepEnded = Notification.Name("watchSleepEnded")
    static let watchHealthAlert = Notification.Name("watchHealthAlert")
    static let watchDataReceived = Notification.Name("watchDataReceived")
}
