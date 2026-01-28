//
//  WatchConnectivityManager.swift
//  SleepFM Watch App
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation
import WatchConnectivity

/// Watch Connectivity 매니저
///
/// iPhone과 Apple Watch 간 양방향 통신을 관리합니다.
/// 
/// 주요 기능:
/// - 실시간 메시지 송수신 (앱이 활성 상태일 때)
/// - 백그라운드 데이터 전송 (transferUserInfo)
/// - 파일 전송 (transferFile)
/// - 앱 컨텍스트 공유 (applicationContext)
@MainActor
class WatchConnectivityManager: NSObject, ObservableObject {
    // MARK: - Published Properties
    
    @Published var isReachable = false
    @Published var isSyncing = false
    @Published var lastSyncTime: Date?
    @Published var pendingTransfers = 0
    
    // MARK: - Private Properties
    
    private var session: WCSession?
    
    // MARK: - Initialization
    
    override init() {
        super.init()
        
        if WCSession.isSupported() {
            session = WCSession.default
            session?.delegate = self
            session?.activate()
        }
    }
    
    // MARK: - Send Data to iPhone
    
    /// 센서 데이터를 iPhone으로 전송
    /// 
    /// 백그라운드에서도 전송 가능한 transferUserInfo 사용
    func sendSensorData(_ data: SensorDataPackage) {
        guard let session = session, session.activationState == .activated else {
            print("WCSession not activated")
            return
        }
        
        isSyncing = true
        
        let payload: [String: Any] = [
            "type": "sensorData",
            "sessionId": data.sessionId,
            "startTime": data.startTime.timeIntervalSince1970,
            "endTime": data.endTime.timeIntervalSince1970,
            "heartRateSamples": data.heartRateSamples.map { ["timestamp": $0.timestamp.timeIntervalSince1970, "value": $0.value] },
            "respiratoryRateSamples": data.respiratoryRateSamples.map { ["timestamp": $0.timestamp.timeIntervalSince1970, "value": $0.value] },
            "accelerometerSamples": data.accelerometerSamples.map { ["timestamp": $0.timestamp.timeIntervalSince1970, "x": $0.x, "y": $0.y, "z": $0.z] }
        ]
        
        // 백그라운드 전송 (앱이 종료되어도 전송됨)
        session.transferUserInfo(payload)
        
        pendingTransfers = session.outstandingUserInfoTransfers.count
        print("Sensor data queued for transfer. Pending: \(pendingTransfers)")
    }
    
    /// 실시간 메시지 전송 (앱이 활성 상태일 때만)
    func sendMessage(_ message: [String: Any], replyHandler: (([String: Any]) -> Void)? = nil) {
        guard let session = session, session.isReachable else {
            print("iPhone not reachable")
            return
        }
        
        session.sendMessage(message, replyHandler: replyHandler) { error in
            print("Message send error: \(error.localizedDescription)")
        }
    }
    
    /// 앱 컨텍스트 업데이트 (최신 상태만 유지)
    func updateApplicationContext(_ context: [String: Any]) {
        guard let session = session else { return }
        
        do {
            try session.updateApplicationContext(context)
        } catch {
            print("Failed to update application context: \(error)")
        }
    }
    
    /// 수면 점수 동기화
    func syncSleepScore(_ score: Int, forDate date: Date) {
        let context: [String: Any] = [
            "lastSleepScore": score,
            "lastSleepDate": date.timeIntervalSince1970,
            "updateTime": Date().timeIntervalSince1970
        ]
        
        updateApplicationContext(context)
    }
    
    // MARK: - Retry Logic
    
    /// 실패한 전송 재시도
    func retryFailedTransfers() {
        guard let session = session else { return }
        
        let outstandingTransfers = session.outstandingUserInfoTransfers
        pendingTransfers = outstandingTransfers.count
        
        if outstandingTransfers.isEmpty {
            print("No outstanding transfers to retry")
        } else {
            print("Outstanding transfers: \(outstandingTransfers.count)")
        }
    }
}

// MARK: - WCSessionDelegate

extension WatchConnectivityManager: WCSessionDelegate {
    nonisolated func session(
        _ session: WCSession,
        activationDidCompleteWith activationState: WCSessionActivationState,
        error: Error?
    ) {
        Task { @MainActor in
            if activationState == .activated {
                self.isReachable = session.isReachable
                print("WCSession activated, reachable: \(session.isReachable)")
            } else if let error = error {
                print("WCSession activation failed: \(error.localizedDescription)")
            }
        }
    }
    
    nonisolated func sessionReachabilityDidChange(_ session: WCSession) {
        Task { @MainActor in
            self.isReachable = session.isReachable
            print("iPhone reachability changed: \(session.isReachable)")
        }
    }
    
    // iPhone으로부터 메시지 수신
    nonisolated func session(
        _ session: WCSession,
        didReceiveMessage message: [String: Any],
        replyHandler: @escaping ([String: Any]) -> Void
    ) {
        Task { @MainActor in
            handleReceivedMessage(message, replyHandler: replyHandler)
        }
    }
    
    // iPhone으로부터 앱 컨텍스트 수신
    nonisolated func session(
        _ session: WCSession,
        didReceiveApplicationContext applicationContext: [String: Any]
    ) {
        Task { @MainActor in
            handleReceivedContext(applicationContext)
        }
    }
    
    // 전송 완료 알림
    nonisolated func session(
        _ session: WCSession,
        didFinish userInfoTransfer: WCSessionUserInfoTransfer,
        error: Error?
    ) {
        Task { @MainActor in
            self.pendingTransfers = session.outstandingUserInfoTransfers.count
            
            if let error = error {
                print("UserInfo transfer failed: \(error.localizedDescription)")
            } else {
                print("UserInfo transfer completed successfully")
                self.lastSyncTime = Date()
                self.isSyncing = false
            }
        }
    }
    
    // MARK: - Message Handling
    
    @MainActor
    private func handleReceivedMessage(_ message: [String: Any], replyHandler: @escaping ([String: Any]) -> Void) {
        guard let type = message["type"] as? String else {
            replyHandler(["status": "error", "message": "Unknown message type"])
            return
        }
        
        switch type {
        case "requestSensorData":
            // iPhone이 센서 데이터 요청
            let data = SensorDataStore.shared.getAllData()
            replyHandler([
                "status": "success",
                "sampleCount": data.count
            ])
            
        case "startMonitoring":
            // iPhone이 모니터링 시작 요청
            NotificationCenter.default.post(name: .startSleepMonitoring, object: nil)
            replyHandler(["status": "success"])
            
        case "stopMonitoring":
            // iPhone이 모니터링 중지 요청
            NotificationCenter.default.post(name: .stopSleepMonitoring, object: nil)
            replyHandler(["status": "success"])
            
        default:
            replyHandler(["status": "error", "message": "Unknown command"])
        }
    }
    
    @MainActor
    private func handleReceivedContext(_ context: [String: Any]) {
        // iPhone에서 업데이트된 설정 등 처리
        if let autoMonitor = context["autoMonitorEnabled"] as? Bool {
            UserDefaults.standard.set(autoMonitor, forKey: "autoMonitorEnabled")
        }
        
        if let alertsEnabled = context["alertsEnabled"] as? Bool {
            UserDefaults.standard.set(alertsEnabled, forKey: "alertsEnabled")
        }
    }
}

// MARK: - Data Models

/// 센서 데이터 패키지
struct SensorDataPackage {
    let sessionId: String
    let startTime: Date
    let endTime: Date
    let heartRateSamples: [SensorSample]
    let respiratoryRateSamples: [SensorSample]
    let accelerometerSamples: [AccelerometerSample]
}

struct SensorSample {
    let timestamp: Date
    let value: Double
}

struct AccelerometerSample {
    let timestamp: Date
    let x: Double
    let y: Double
    let z: Double
}

// MARK: - Notification Names

extension Notification.Name {
    static let startSleepMonitoring = Notification.Name("startSleepMonitoring")
    static let stopSleepMonitoring = Notification.Name("stopSleepMonitoring")
}
