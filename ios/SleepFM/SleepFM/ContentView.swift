//
//  ContentView.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// 메인 컨텐츠 뷰 - 인증 상태에 따라 분기
struct ContentView: View {
    @EnvironmentObject var authManager: AuthManager
    
    var body: some View {
        Group {
            if authManager.isAuthenticated {
                MainTabView()
            } else if authManager.hasSeenOnboarding {
                LoginView()
            } else {
                OnboardingView()
            }
        }
        .animation(.easeInOut, value: authManager.isAuthenticated)
    }
}

#Preview {
    ContentView()
        .environmentObject(AuthManager())
        .environmentObject(HealthKitManager())
}
