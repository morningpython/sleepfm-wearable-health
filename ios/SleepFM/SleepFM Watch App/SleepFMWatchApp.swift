//
//  SleepFMWatchApp.swift
//  SleepFM Watch App
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI
import WatchKit
import HealthKit

/// watchOS 앱 진입점
@main
struct SleepFMWatchApp: App {
    // MARK: - State Objects
    
    @StateObject private var healthManager = WatchHealthManager()
    @StateObject private var connectivityManager = WatchConnectivityManager()
    @StateObject private var sleepMonitor = SleepMonitor()
    
    // MARK: - Scene Phase
    
    @Environment(\.scenePhase) private var scenePhase
    
    // MARK: - Body
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(healthManager)
                .environmentObject(connectivityManager)
                .environmentObject(sleepMonitor)
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            handleScenePhaseChange(from: oldPhase, to: newPhase)
        }
        
        // 백그라운드 작업
        WKNotificationScene(controller: NotificationController.self, category: "SleepFMAlert")
    }
    
    // MARK: - Scene Phase Handling
    
    private func handleScenePhaseChange(from oldPhase: ScenePhase, to newPhase: ScenePhase) {
        switch newPhase {
        case .active:
            print("Watch App is active")
            Task {
                await healthManager.requestAuthorization()
            }
        case .inactive:
            print("Watch App is inactive")
        case .background:
            print("Watch App is in background")
            // 백그라운드에서도 수면 모니터링 계속
            sleepMonitor.continueBackgroundMonitoring()
        @unknown default:
            break
        }
    }
}

/// 알림 컨트롤러
class NotificationController: WKUserNotificationHostingController<NotificationView> {
    override var body: NotificationView {
        NotificationView()
    }
}

/// 알림 뷰
struct NotificationView: View {
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: "heart.fill")
                .font(.title2)
                .foregroundColor(.red)
            
            Text("건강 알림")
                .font(.headline)
            
            Text("비정상적인 패턴이 감지되었습니다")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}
