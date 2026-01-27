//
//  MainTabView.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// 메인 탭 네비게이션
struct MainTabView: View {
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var healthKitManager: HealthKitManager
    @State private var selectedTab: Tab = .dashboard
    
    enum Tab: Hashable {
        case dashboard
        case history
        case settings
    }
    
    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Label("대시보드", systemImage: "moon.fill")
                }
                .tag(Tab.dashboard)
            
            HistoryView()
                .tabItem {
                    Label("기록", systemImage: "clock.fill")
                }
                .tag(Tab.history)
            
            SettingsView()
                .tabItem {
                    Label("설정", systemImage: "gearshape.fill")
                }
                .tag(Tab.settings)
        }
        .tint(.sleepPrimary)
        .onAppear {
            configureTabBarAppearance()
        }
    }
    
    private func configureTabBarAppearance() {
        let appearance = UITabBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundColor = UIColor(Color.sleepCardBackground)
        
        // Normal state
        appearance.stackedLayoutAppearance.normal.iconColor = UIColor(Color.sleepTextDisabled)
        appearance.stackedLayoutAppearance.normal.titleTextAttributes = [
            .foregroundColor: UIColor(Color.sleepTextDisabled)
        ]
        
        // Selected state
        appearance.stackedLayoutAppearance.selected.iconColor = UIColor(Color.sleepPrimary)
        appearance.stackedLayoutAppearance.selected.titleTextAttributes = [
            .foregroundColor: UIColor(Color.sleepPrimary)
        ]
        
        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
    }
}

// MARK: - Preview

#Preview {
    MainTabView()
        .environmentObject(AuthManager())
        .environmentObject(HealthKitManager())
}
