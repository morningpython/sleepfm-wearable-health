//
//  SleepFMApp.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// SleepFM 앱 메인 진입점
@main
struct SleepFMApp: App {
    /// 앱 전역 상태
    @StateObject private var authManager = AuthManager()
    @StateObject private var healthKitManager = HealthKitManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authManager)
                .environmentObject(healthKitManager)
        }
    }
}
