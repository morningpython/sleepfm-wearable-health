//
//  NotificationService.swift
//  SleepFM Watch App
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation
import UserNotifications
import WatchKit

/// 알림 서비스
///
/// 건강 이상 징후 감지 시 사용자에게 알림을 전송합니다.
class NotificationService {
    // MARK: - Singleton
    
    static let shared = NotificationService()
    
    // MARK: - Properties
    
    private var alertHistory: [HealthAlert] = []
    private let maxHistoryCount = 50
    
    // MARK: - Initialization
    
    private init() {
        requestNotificationPermission()
    }
    
    // MARK: - Permission
    
    /// 알림 권한 요청
    func requestNotificationPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                print("Notification permission granted")
            } else if let error = error {
                print("Notification permission error: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Send Alert
    
    /// 건강 알림 전송
    func sendHealthAlert(title: String, body: String, type: AlertType) {
        // 중복 알림 방지 (같은 타입 알림이 5분 내에 있으면 무시)
        if let lastAlert = alertHistory.last(where: { $0.type == type }),
           Date().timeIntervalSince(lastAlert.timestamp) < 300 {
            return
        }
        
        // 알림 히스토리에 추가
        let alert = HealthAlert(
            id: UUID().uuidString,
            title: title,
            body: body,
            type: type,
            timestamp: Date()
        )
        alertHistory.append(alert)
        
        // 히스토리 크기 제한
        if alertHistory.count > maxHistoryCount {
            alertHistory.removeFirst()
        }
        
        // 로컬 알림 생성
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.categoryIdentifier = "SleepFMAlert"
        
        // 즉시 전송
        let request = UNNotificationRequest(
            identifier: alert.id,
            content: content,
            trigger: nil
        )
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("Failed to send notification: \(error.localizedDescription)")
            }
        }
        
        // 햅틱 피드백
        playHapticForAlert(type: type)
        
        print("Health alert sent: \(type.rawValue) - \(title)")
    }
    
    // MARK: - Haptic Feedback
    
    /// 알림 타입에 따른 햅틱 피드백
    private func playHapticForAlert(type: AlertType) {
        let device = WKInterfaceDevice.current()
        
        switch type {
        case .abnormalHeartRate:
            // 긴급한 패턴
            device.play(.notification)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                device.play(.notification)
            }
            
        case .abnormalRespiratoryRate:
            device.play(.notification)
            
        case .possibleApnea:
            // 강한 경고
            device.play(.notification)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                device.play(.notification)
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
                device.play(.notification)
            }
            
        case .sleepStarted:
            device.play(.start)
            
        case .sleepEnded:
            device.play(.stop)
            
        case .syncCompleted:
            device.play(.success)
            
        case .syncFailed:
            device.play(.failure)
        }
    }
    
    // MARK: - Alert History
    
    /// 알림 히스토리 가져오기
    func getAlertHistory() -> [HealthAlert] {
        return alertHistory
    }
    
    /// 특정 타입의 알림 히스토리 가져오기
    func getAlertHistory(ofType type: AlertType) -> [HealthAlert] {
        return alertHistory.filter { $0.type == type }
    }
    
    /// 알림 히스토리 초기화
    func clearHistory() {
        alertHistory.removeAll()
    }
    
    /// 최근 24시간 알림 수
    func getRecentAlertCount() -> Int {
        let oneDayAgo = Date().addingTimeInterval(-86400)
        return alertHistory.filter { $0.timestamp > oneDayAgo }.count
    }
}

// MARK: - Alert Types

enum AlertType: String, Codable {
    case abnormalHeartRate = "abnormal_heart_rate"
    case abnormalRespiratoryRate = "abnormal_respiratory_rate"
    case possibleApnea = "possible_apnea"
    case sleepStarted = "sleep_started"
    case sleepEnded = "sleep_ended"
    case syncCompleted = "sync_completed"
    case syncFailed = "sync_failed"
    
    var displayName: String {
        switch self {
        case .abnormalHeartRate: return "비정상 심박수"
        case .abnormalRespiratoryRate: return "비정상 호흡률"
        case .possibleApnea: return "무호흡 의심"
        case .sleepStarted: return "수면 시작"
        case .sleepEnded: return "수면 종료"
        case .syncCompleted: return "동기화 완료"
        case .syncFailed: return "동기화 실패"
        }
    }
    
    var iconName: String {
        switch self {
        case .abnormalHeartRate: return "heart.fill"
        case .abnormalRespiratoryRate: return "lungs.fill"
        case .possibleApnea: return "exclamationmark.triangle.fill"
        case .sleepStarted: return "moon.zzz.fill"
        case .sleepEnded: return "sun.max.fill"
        case .syncCompleted: return "checkmark.circle.fill"
        case .syncFailed: return "xmark.circle.fill"
        }
    }
    
    var isHealthRelated: Bool {
        switch self {
        case .abnormalHeartRate, .abnormalRespiratoryRate, .possibleApnea:
            return true
        default:
            return false
        }
    }
}

// MARK: - Health Alert Model

struct HealthAlert: Identifiable, Codable {
    let id: String
    let title: String
    let body: String
    let type: AlertType
    let timestamp: Date
    
    var formattedTime: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: timestamp)
    }
}
