//
//  ContentView.swift
//  SleepFM Watch App
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// watchOS 메인 화면
struct ContentView: View {
    @EnvironmentObject var healthManager: WatchHealthManager
    @EnvironmentObject var connectivityManager: WatchConnectivityManager
    @EnvironmentObject var sleepMonitor: SleepMonitor
    
    var body: some View {
        NavigationStack {
            TabView {
                // 메인 대시보드
                DashboardTab()
                
                // 수면 모니터링 상태
                MonitoringTab()
                
                // 설정
                SettingsTab()
            }
            .tabViewStyle(.verticalPage)
        }
    }
}

// MARK: - Dashboard Tab

struct DashboardTab: View {
    @EnvironmentObject var healthManager: WatchHealthManager
    
    var body: some View {
        ScrollView {
            VStack(spacing: 12) {
                // 수면 점수 카드
                SleepScoreCard(score: healthManager.lastNightSleepScore)
                
                // 현재 심박수
                HeartRateCard(heartRate: healthManager.currentHeartRate)
                
                // 동기화 상태
                SyncStatusCard()
            }
            .padding(.horizontal)
        }
        .navigationTitle("SleepFM")
    }
}

// MARK: - Monitoring Tab

struct MonitoringTab: View {
    @EnvironmentObject var sleepMonitor: SleepMonitor
    
    var body: some View {
        VStack(spacing: 16) {
            // 모니터링 상태 아이콘
            ZStack {
                Circle()
                    .fill(sleepMonitor.isMonitoring ? Color.green.opacity(0.2) : Color.gray.opacity(0.2))
                    .frame(width: 80, height: 80)
                
                Image(systemName: sleepMonitor.isMonitoring ? "moon.zzz.fill" : "moon.fill")
                    .font(.system(size: 32))
                    .foregroundColor(sleepMonitor.isMonitoring ? .green : .gray)
            }
            
            // 상태 텍스트
            Text(sleepMonitor.isMonitoring ? "수면 모니터링 중" : "대기 중")
                .font(.headline)
            
            if sleepMonitor.isMonitoring {
                // 모니터링 정보
                VStack(spacing: 4) {
                    Text("시작: \(sleepMonitor.monitoringStartTime, formatter: timeFormatter)")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    
                    Text("수집된 샘플: \(sleepMonitor.collectedSamplesCount)")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            // 수동 시작/중지 버튼
            Button {
                if sleepMonitor.isMonitoring {
                    sleepMonitor.stopMonitoring()
                } else {
                    sleepMonitor.startMonitoring()
                }
            } label: {
                Text(sleepMonitor.isMonitoring ? "모니터링 중지" : "모니터링 시작")
                    .font(.caption)
            }
            .buttonStyle(.bordered)
            .tint(sleepMonitor.isMonitoring ? .red : .green)
        }
        .padding()
        .navigationTitle("모니터링")
    }
    
    private var timeFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter
    }
}

// MARK: - Settings Tab

struct SettingsTab: View {
    @EnvironmentObject var healthManager: WatchHealthManager
    @EnvironmentObject var connectivityManager: WatchConnectivityManager
    @State private var autoMonitorEnabled = true
    @State private var alertsEnabled = true
    
    var body: some View {
        List {
            Section("자동 모니터링") {
                Toggle("수면 자동 감지", isOn: $autoMonitorEnabled)
                    .toggleStyle(SwitchToggleStyle(tint: .green))
            }
            
            Section("알림") {
                Toggle("건강 알림", isOn: $alertsEnabled)
                    .toggleStyle(SwitchToggleStyle(tint: .blue))
            }
            
            Section("연결 상태") {
                HStack {
                    Text("iPhone")
                    Spacer()
                    Image(systemName: connectivityManager.isReachable ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .foregroundColor(connectivityManager.isReachable ? .green : .red)
                }
                
                HStack {
                    Text("HealthKit")
                    Spacer()
                    Image(systemName: healthManager.isAuthorized ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .foregroundColor(healthManager.isAuthorized ? .green : .red)
                }
            }
            
            Section("정보") {
                HStack {
                    Text("버전")
                    Spacer()
                    Text("1.0.0")
                        .foregroundColor(.secondary)
                }
            }
        }
        .navigationTitle("설정")
    }
}

// MARK: - Card Components

struct SleepScoreCard: View {
    let score: Int
    
    var body: some View {
        VStack(spacing: 4) {
            HStack {
                Image(systemName: "moon.zzz.fill")
                    .foregroundColor(.purple)
                Text("어젯밤 수면")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            Text("\(score)")
                .font(.system(size: 36, weight: .bold, design: .rounded))
                .foregroundColor(scoreColor)
            
            Text("점")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.gray.opacity(0.15))
        .cornerRadius(12)
    }
    
    private var scoreColor: Color {
        switch score {
        case 80...100: return .green
        case 60..<80: return .blue
        case 40..<60: return .orange
        default: return .red
        }
    }
}

struct HeartRateCard: View {
    let heartRate: Int
    
    var body: some View {
        HStack {
            Image(systemName: "heart.fill")
                .foregroundColor(.red)
                .font(.title3)
            
            VStack(alignment: .leading, spacing: 2) {
                Text("현재 심박수")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                
                HStack(alignment: .firstTextBaseline, spacing: 2) {
                    Text("\(heartRate)")
                        .font(.system(size: 24, weight: .bold, design: .rounded))
                    Text("bpm")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
        }
        .padding()
        .background(Color.gray.opacity(0.15))
        .cornerRadius(12)
    }
}

struct SyncStatusCard: View {
    @EnvironmentObject var connectivityManager: WatchConnectivityManager
    
    var body: some View {
        HStack {
            Image(systemName: "arrow.triangle.2.circlepath")
                .foregroundColor(connectivityManager.isReachable ? .green : .gray)
            
            VStack(alignment: .leading, spacing: 2) {
                Text("동기화")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                
                Text(connectivityManager.isReachable ? "연결됨" : "연결 안됨")
                    .font(.caption)
                    .foregroundColor(connectivityManager.isReachable ? .green : .red)
            }
            
            Spacer()
            
            if connectivityManager.isSyncing {
                ProgressView()
                    .scaleEffect(0.7)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.15))
        .cornerRadius(12)
    }
}

// MARK: - Preview

#Preview {
    ContentView()
        .environmentObject(WatchHealthManager())
        .environmentObject(WatchConnectivityManager())
        .environmentObject(SleepMonitor())
}
